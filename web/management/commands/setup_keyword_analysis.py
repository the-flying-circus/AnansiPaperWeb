import nltk

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'download the files needed to make the keyword extractor work'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        nltk.download('stopwords')
        nltk.download('punkt')
