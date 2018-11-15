from django.db import models


class Author(models.Model):
    name = models.TextField()
    email = models.EmailField()


class Article(models.Model):
    title = models.TextField()
    abstract = models.TextField()
    authors = models.ManyToManyField(Author)
