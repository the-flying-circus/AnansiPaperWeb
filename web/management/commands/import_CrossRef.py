from django.core.management.base import BaseCommand, CommandError

from web.models import Article
from requests import get


class Command(BaseCommand):
    help = 'Import data from CrossRef'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        pass