from django.core.management.base import BaseCommand, CommandError

from .scholar import SearchScholarQuery, ScholarQuerier
from web.models import Article


class Command(BaseCommand):
    help = 'Import data from Google scholar'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        query = SearchScholarQuery()
        query.set_words_some("car security")
        querier = ScholarQuerier()
        querier.send_query(query)

        for article in querier.articles:
            Article.objects.get_or_create(title=article['title'], year=int(article['year']))
            self.stdout.write("Imported '{}'".format(article['title']))

        self.stdout.write(self.style.SUCCESS('Import completed!'))
