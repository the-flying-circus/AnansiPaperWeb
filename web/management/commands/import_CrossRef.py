from django.core.management.base import BaseCommand, CommandError

from web.models import Article
from requests import get