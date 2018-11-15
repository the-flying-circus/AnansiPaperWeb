from django.core.management.base import BaseCommand, CommandError
from django.models import Q

from .scholar import SearchScholarQuery, ScholarQuerier
from web.models import Article


class Command(BaseCommand):
    help = 'Import data from Google scholar'

    def add_arguments(self, parser):
        parser.add_argument("query", type=str)

    def handle(self, *args, **kwargs):
        query = SearchScholarQuery()
        query.set_words_some(kwargs["query"])
        querier = ScholarQuerier()
        querier.send_query(query)

        for article in querier.articles:
            year = int(article['year'])
            art, _ = Article.objects.get_or_create(title__iexact=article['title'].strip(), Q(year=year) | Q(year__isnull=True), defaults={
                "url": article['url_pdf'],
                "title": article['title'].strip(),
                "year": year
            })

            if not art.year:
                art.year = year
                art.save()

            self.stdout.write("Imported '{}'".format(article['title']))

        self.stdout.write(self.style.SUCCESS('Import completed!'))
