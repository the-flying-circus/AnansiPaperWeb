from django.db import models


class Author(models.Model):
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.EmailField(null=True)

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    def __str__(self):
        return self.full_name


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

    @property
    def label(self):
        suffix = " et al." if self.authors.count() > 1 else ""
        if self.last_author:
            prefix = self.last_author.last_name
        elif self.authors.first():
            prefix = self.authors.first().last_name
        else:
            prefix = "(no author)"
        return prefix + suffix

    @property
    def group(self):
        if self.last_author:
            return self.last_author.id
        elif self.authors.first():
            return self.authors.first().id
        else:
            return 0

    @property
    def author_string(self):
        return ", ".join([ath.full_name for ath in self.authors.all()])

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
