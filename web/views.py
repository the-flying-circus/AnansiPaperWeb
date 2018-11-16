from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q

from web.search import getGraph
from .models import Article, Author


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
        "keywords": list(article.keywords.order_by("-keywordrank__rank").values_list("keyword", flat=True)),
        "url": article.url,
        "outward": list(article.cites.values("id", "title")),
        "inward": list(article.cited.values("id", "title"))
    })


def search(request):
    query = request.GET.get("q")
    articles = Article.objects.filter(Q(title__icontains=query) | Q(authors__first_name__icontains=query) | Q(authors__last_name__icontains=query) | Q(doi__icontains=query)).order_by("-year")[:1000]
    return JsonResponse({
        "articles": list({"type": "article", "id": art.id, "title": art.title, "year": art.year, "authors": art.author_string, "doi": art.doi} for art in articles.prefetch_related("authors")),
        "authors": list({"type": "author", "id": aut.id, "title": aut.full_name} for aut in Author.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query)))
    })


def graph(request):
    nodes = Article.objects.all()[:100]

    node_list = []
    edge_list = []
    for node in nodes.prefetch_related("authors"):
        node_list.append({
            "id": node.id,
            "label": node.label,
            "title": node.title,
            "isQuery": True,
            "authors": node.author_string,
            "group": node.group,
            "indegree": node.cited.count()
        })

        for other in node.cites.filter(id__in=nodes.values_list("id", flat=True)):
            edge_list.append({
                "source": node.id,
                "target": other.id
            })

    return JsonResponse({
        "nodes": node_list,
        "edges": edge_list
    })


def generate_graph(request):
    articles = [x for x in request.POST.get("articles").strip().split(',') if x]
    authors = [x for x in request.POST.get("authors").strip().split(',') if x]
    keywords = [x for x in request.POST.get("keywords").strip().split(',') if x]
    nodes = getGraph(articles, authors, keywords)
