from django.db import models


class Author(models.Model):
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.EmailField(null=True)

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    def __str__(self):
        return self.name


class Journal(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.TextField()
    url = models.TextField(null=True)
    year = models.PositiveSmallIntegerField(null=True)
    abstract = models.TextField(null=True)
    doi = models.TextField(null=True)
    authors = models.ManyToManyField(Author)
    first_author = models.ForeignKey(Author, null=True, on_delete=models.SET_NULL, related_name="primary_articles")
    last_author = models.ForeignKey(Author, null=True, on_delete=models.SET_NULL, related_name="pi_articles")
    journal = models.ForeignKey(Journal, null=True, on_delete=models.SET_NULL)
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

    def __str__(self):
        return str(self.keyword) + ' in ' + str(self.article) + ' (' + str(self.rank) + ')'
