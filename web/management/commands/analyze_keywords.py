from django.core.management.base import BaseCommand, CommandError
from rake_nltk import Rake

from web.models import Article, Keywords

class Command(BaseCommand):
    help = 'scrape abstract for keywords'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for article in Article.objects.filter(keywords=None):
            abstract = article.abstract
            if abstract is not None:
                r = Rake()
                r.extract_keywords_from_text(abstract)
                keywords = r.get_ranked_phrases()
                for keyword in keywords:
