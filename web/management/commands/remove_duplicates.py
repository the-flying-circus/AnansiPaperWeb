from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from web.models import Article, Author


class Command(BaseCommand):
    help = 'Remove duplicate entries from the database'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        self.removed = 0
        duplicates = Article.objects.values("title").annotate(Count("id")).order_by().filter(id__count__gt=1)
        for item in duplicates:
            for article in Article.objects.filter(title=item["title"])[1:]:
                article.delete()
            self.stdout.write("Removed '{}'".format(item["title"]))
            self.removed += 1
        self.stdout.write(self.style.SUCCESS('Cleanup completed! Removed {} object(s).'.format(self.removed)))
