from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from django.core.cache import cache

from web.models import Article, Author


class Command(BaseCommand):
    help = 'Remove duplicate entries from the database'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        self.removed = 0
        duplicates = Article.objects.values("title").annotate(Count("id")).order_by().filter(id__count__gt=1)
        all_ids = []
        for item in duplicates:
            ids = list(Article.objects.filter(title=item["title"])[1:].values_list("id", flat=True))
            all_ids += ids
            self.stdout.write("Removed '{}' ({} times)".format(item["title"], len(ids)))
            self.removed += len(ids)
        Article.objects.filter(id__in=all_ids).delete()
        cache.clear()
        self.stdout.write(self.style.SUCCESS('Cleanup completed! Removed {} object(s) with {} object(s) remaining.'.format(self.removed, Article.objects.count())))
