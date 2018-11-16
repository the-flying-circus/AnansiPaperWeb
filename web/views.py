from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q

from .models import Article


def node(request):
    query = Q(pk=None)
    if "q" in request.GET:
        query |= Q(title__icontains=request.GET.get("q"))
    if "id" in request.GET:
        query |= Q(id=request.GET.get("id"))
    article = Article.objects.filter(query).first()
    if not article:
        return JsonResponse({
            "success": False
        })
    return JsonResponse({
        "success": True,
        "id": article.id,
        "title": article.title,
        "abstract": article.abstract,
        "authors": [{"name": "{} {}".format(author.first_name, author.last_name).strip(), "id": author.id} for author in article.authors.order_by("last_name")],
        "url": article.url,
        "outward": list(article.cites.values("id", "title")),
        "inward": list(article.cited.values("id", "title"))
    })


def search(request):
    query = request.GET.get("q")
    return JsonResponse({
        "articles": list(Article.objects.filter(title__icontains=query).values("id", "title"))
    })

