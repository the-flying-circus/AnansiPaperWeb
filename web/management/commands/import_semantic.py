import requests
import threading

from concurrent.futures import ThreadPoolExecutor, wait
from django.core.management.base import BaseCommand, CommandError

from web.models import Article, Author

SEARCH_ENDPOINT = "https://www.semanticscholar.org/api/1/search"
LIMIT = 100
DEPTH = 3


class Command(BaseCommand):
    help = 'Import data from Semantic Scholar'

    def add_arguments(self, parser):
        parser.add_argument("query", type=str)

    def add_paper(self, result_id, depth=0):
        resp = requests.get('https://www.semanticscholar.org/api/1/paper/{}?citedPapersLimit={}&citingPapersLimit={}'.format(result_id, LIMIT, LIMIT))
        resp.raise_for_status()

        with self.lock:
            raw_resp = resp.json()
            result = raw_resp['paper']

            title = result['title']['text'].strip()
            if 'paperAbstract' in result:
                abstract = result['paperAbstract']['text'].strip()
            else:
                abstract = None
            url = result.get('presentationUrl')
            if not url and 'links' in result:
                url = result['links'][0]['url']
            year = result.get('year')
            if year is not None:
                if not isinstance(year, int):
                    year = year['text']
                if year:
                    year = int(year)
                else:
                    year = None

            obj, _ = Article.objects.get_or_create(title__iexact=title, year__in=[year, None], defaults={
                'title': title,
                'abstract': abstract,
                'url': url,
                'year': year
            })

            if not url:
                self.missing_link += 1

            if not abstract:
                self.missing_abstract += 1

            if not obj.url:
                obj.url = url
                obj.save(update_fields=["url"])

            if not obj.abstract:
                obj.abstract = abstract
                obj.save(update_fields=["abstract"])

            # add authors
            authors = [x[0]['name'].strip() for x in result['authors']]
            for author in authors:
                try:
                    first, last = author.rsplit(' ', 1)
                except ValueError:
                    first = ''
                    last = author
                ath, _ = Author.objects.get_or_create(first_name__iexact=first, last_name__iexact=last, defaults={
                    "first_name": first,
                    "last_name": last
                })
                obj.authors.add(ath)

            self.total += 1
            self.stdout.write("Imported '{}'".format(title))

        if depth > 0:
            for paper in raw_resp['citedPapers']['citations']:
                child = self.add_paper(paper['id'], depth=depth - 1)
                obj.cites.add(child)

            for paper in raw_resp['citingPapers']['citations']:
                child = self.add_paper(paper['id'], depth=depth - 1)
                obj.cited.add(child)

        return obj

    def handle(self, *args, **kwargs):
        self.missing_abstract = 0
        self.missing_link = 0
        self.total = 0

        resp = requests.post(SEARCH_ENDPOINT, json={
            "queryString": kwargs['query'],
            "authors": [],
            "coAuthors": [],
            "facets": {},
            "page": 1,
            "pageSize": LIMIT,
            "publicationTypes": [],
            "requireViewablePdf": False,
            "sort": "relevance",
            "venues": [],
            "yearFilter": None
        })
        resp.raise_for_status()

        self.lock = threading.Lock()
        with ThreadPoolExecutor(max_workers=4) as executor:
            wait([executor.submit(self.add_paper, result["id"], depth=DEPTH) for result in resp.json()["results"]])

        self.stdout.write(self.style.SUCCESS('Import completed!'))
        self.stdout.write("{} imported, {} missing link, {} missing abstract.".format(self.total, self.missing_link, self.missing_abstract))
