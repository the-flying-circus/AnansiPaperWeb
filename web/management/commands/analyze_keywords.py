from django.core.management.base import BaseCommand, CommandError
from rake_nltk import Rake

from web.models import Article, Keyword, KeywordRank


class Command(BaseCommand):
    help = 'scrape abstract for keywords'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for article in Article.objects.filter(keywords=None):
            self.stdout.write("analyzing keywords for {}".format(article.title))

            abstract = article.abstract
            if abstract is not None:
                r = Rake(max_length=3)
                r.extract_keywords_from_text(abstract)
                keywords = r.get_ranked_phrases_with_scores()
                for rank, keyword in keywords:
                    keywordObj, _ = Keyword.objects.get_or_create(keyword=keyword, defaults={'keyword': keyword})
                    KeywordRank.objects.create(rank=rank, keyword=keywordObj, article=article)
                    self.stdout.write("    wrote keyword '{}' (rank {})".format(keyword, rank))
