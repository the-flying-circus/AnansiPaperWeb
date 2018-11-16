import requests

from django.core.management.base import BaseCommand, CommandError

from web.models import Article, Author

SEARCH_ENDPOINT = "https://www.semanticscholar.org/api/1/search"


class Command(BaseCommand):
    help = 'Import data from Semantic Scholar'

    def add_arguments(self, parser):
        parser.add_argument("query", type=str)

    def add_paper(self, result, depth=0):
        title = result['title']['text'].strip()
        if 'abstract' in result:
            abstract = result['abstract']['text'].strip()
        else:
            abstract = None
        url = result.get('presentationUrl')
        year = result['year']['text']
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

        if not obj.url:
            obj.url = url
            obj.save()

        if not obj.abstract:
            obj.abstract = abstract
            obj.save()

        # add authors
        authors = [x[0]['name'].strip() for x in result['authors']]
        for author in authors:
            ath, _ = Author.objects.get_or_create(name=author)
            obj.authors.add(ath)

        self.stdout.write("Imported '{}'".format(title))

        if depth > 0:
            resp = requests.get('https://www.semanticscholar.org/api/1/paper/{}?citedPapersLimit=100'.format(result['id']))
            resp.raise_for_status()

            for paper in resp.json()['citedPapers']['citations']:
                child = self.add_paper(paper, depth=depth - 1)
                obj.cites.add(child)

            for paper in resp.json()['citingPapers']['citations']:
                child = self.add_paper(paper, depth=depth - 1)
                obj.cited.add(child)

        return obj

    def handle(self, *args, **kwargs):
        resp = requests.post(SEARCH_ENDPOINT, json={
            "queryString": kwargs['query'],
            "authors": [],
            "coAuthors": [],
            "facets": {},
            "page": 1,
            "pageSize": 100,
            "publicationTypes": [],
            "requireViewablePdf": False,
            "sort": "relevance",
            "venues": [],
            "yearFilter": None
        })
        resp.raise_for_status()

        for result in resp.json()["results"]:
            self.add_paper(result, depth=1)

        self.stdout.write(self.style.SUCCESS('Import completed!'))
