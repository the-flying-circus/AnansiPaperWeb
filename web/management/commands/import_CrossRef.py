from django.core.management.base import BaseCommand, CommandError
from pprint import pformat

from web.models import Article
import requests


class Command(BaseCommand):
    help = 'Import data from CrossRef'

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        # hopefully make crossref like us better by adding a mailto
        self.session.headers.update({'User-Agent': 'AnansiPaperWeb 0.001 (no-url-yet; mailto:bobobalink+anasi@gmail.com) based on python-requests/2.20.1'})

    def add_arguments(self, parser):
        parser.add_argument('query', type=str)

    def handle(self, *args, **kwargs):
        r = self.session.get('https://api.crossref.org/works', params={'query': kwargs['query']})
        self.stdout.write(pformat(r.json()))
