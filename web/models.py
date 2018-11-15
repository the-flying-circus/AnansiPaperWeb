from django.db import models


class Author(models.Model):
    name = models.TextField()


class Article(models.Model):
    title = models.TextField()
    abstract = models.TextField()
    authors = models.ManyToManyField(Author)
