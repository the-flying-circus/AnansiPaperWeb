from django.db import models


class Author(models.Model):
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.EmailField(null=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.TextField()
    url = models.TextField(null=True)
    year = models.PositiveSmallIntegerField(null=True)
    abstract = models.TextField(null=True)
    authors = models.ManyToManyField(Author)
    # cites is the papers that this paper cites
    # cited is all the other papers that cite this paper
    cites = models.ManyToManyField("Article", related_name="cited")

    def __str__(self):
        return self.title


class Keyword(models.Model):
    keyword = models.TextField()
    articles = models.ManyToManyField(Article, related_name="keywords", through="KeywordRank")

    def __str__(self):
        return self.keyword


class KeywordRank(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    rank = models.FloatField()
