import math

from .models import Article, Author, Keyword
from django.db.models import Count, Case, When

CENTRAL_AUTHOR_TO_TITLE_THRESH = 0.3
CENTRAL_AUTHOR_TO_KEYWORD_THRESH = 0.3
CENTRAL_KEYWORD_ONLY_THRESH = 0.8

NODE_KILL_SCORE_THRESH = 0.3
NODE_KILL_DEPTH_THRESH = 5


def findCentral(titles, authors, keywords):
    """
    :param titles: plaintext article title (must match exactly)
    :param authors: tuples of plaintext (firstname, lastname)
    :param keywords: plaintext keywords that are in the db
    :return: queryset of article objects that are central
    """

    # first, all titles are automatically centrals
    centrals = []
    if titles:
        centrals = Article.objects.filter(title__in=titles)
        # print('found matching articles: ')
        # print(centrals)

    if authors:
        # if there's only authors
        authorPapers = Article.objects.filter(authors__first_name__in=map(lambda x: x[0], authors), authors__last_name__in=map(lambda x: x[1], authors))
        # print('found author papers: ')
        # print(authorPapers)
        if not titles and not keywords:
            centrals = authorPapers

        if titles:
            # if there's titles, get the relevant keywords
            keywordsTitleObjs = Keyword.objects.filter(articles__in=centrals).distinct()
            # print('found keywords from title-papers: ')
            # print(keywords)

            # get the papers from the authors with enough keywords
            found = authorPapers.annotate(match_count=Count(Case(When(keywords__in=keywordsTitleObjs, then=1)))).filter(match_count__gte=CENTRAL_AUTHOR_TO_TITLE_THRESH)
            # print('found relevant papers from authors')
            # print(found)

            centrals = centrals | found

        if keywords:
            # choose articles from the author that also nicely correspond with keywords
            keywordObjs = Keyword.objects.filter(keyword__in=keywords).distinct()
            found = authorPapers.annotate(match_count=Count(Case(When(keywords__in=keywordObjs, then=1)))).filter(match_count__gte=CENTRAL_AUTHOR_TO_KEYWORD_THRESH)
            centrals = centrals | found

    if keywords and not titles and not authors:
        # if keywords are all we have to go off of
        keywordObjs = Keyword.objects.filter(keyword__in=keywords).distinct()
        centrals = Article.objects.annotate(match_count=Count(Case(When(keywords__in=keywordObjs, then=1)))).filter(match_count__gte=CENTRAL_KEYWORD_ONLY_THRESH)

    return centrals.distinct().all()


def calcScore(node, foundNodes, keywords):
    found = Article.objects.filter(id__in=foundNodes)

    connectionPoints = 5 * found.filter(cites=node).count() + 1 * found.filter(cited=node).count()

    keywordPoints = node.keywords.filter(id__in=keywords).count()

    return connectionPoints, keywordPoints


def useScore(scoreTuple):
    return scoreTuple[0] * scoreTuple[1]


def traverse(centralNodes, keywords):
    # traverse in the way that is good
    # we're just gonna look for the largest element each time because priority queues are not meant for changing an arbitrary number of elements arbitrarily

    # nodes is a dict: article.id -> (score, depth)
    # foundNodes is just a set of article ids
    foundNodes = set(centralNodes.values_list('id', flat=True))

    # populate the dict
    nodes = {}
    firstLayer = (Article.objects.filter(cited__in=centralNodes) | Article.objects.filter(cites__in=centralNodes)).distinct()
    maxVal = 0  # max val ever seen
    for node in firstLayer:
        nodes[node.id] = (calcScore(node, foundNodes, keywords), 1)
        if maxVal < useScore(nodes[node.id][0]):
            maxVal = useScore(nodes[node.id][0])

    while nodes:
        print('found node count:', len(foundNodes))
        print('in-process nodes: ', len(nodes))
        # find the largest node
        thisMax = next(iter(nodes.keys()))
        thisMaxVal = useScore(nodes[thisMax][0])
        toKill = set()
        for node in nodes:
            thisVal = useScore(nodes[node][0])

            # they are too weak, they will be deleted
            if thisVal < maxVal * NODE_KILL_SCORE_THRESH:
                toKill.add(node)
                continue

            if thisVal > thisMaxVal:
                thisMax = node
                thisMaxVal = thisVal

            if thisMaxVal > maxVal:
                maxVal = thisMaxVal

        for dead in toKill:
            del nodes[dead]

        # if it's a found max then keep it
        foundNodes.add(thisMax)

        # if it's too far away to continue
        try:
            if nodes[thisMax][1] >= NODE_KILL_DEPTH_THRESH:
                continue
        except KeyError:
            continue

        maxObj = Article.objects.filter(id=thisMax).first()
        for child in maxObj.cites.all():
            if child.id in foundNodes:
                continue

            if child.id in nodes:
                oldVal = nodes[child.id]
                nodes[child.id] = ((oldVal[0][0] + 5, oldVal[0][1]), min(oldVal[1], nodes[thisMax][1] + 1))
            else:
                nodes[child.id] = (calcScore(child, foundNodes, keywords), nodes[thisMax][1] + 1)

            # then update the scores of all the attached nodes to that node
            for superChild in child.cites.all():
                if superChild.id in foundNodes:
                    continue

                if superChild.id in nodes:
                    oldVal = nodes[superChild.id]
                    nodes[superChild.id] = ((oldVal[0][0] + 5, oldVal[0][1]), min(oldVal[1], nodes[thisMax][1] + 2))
            for superChild in child.cited.all():
                if superChild.id in foundNodes:
                    continue

                if superChild.id in nodes:
                    oldVal = nodes[superChild.id]
                    nodes[superChild.id] = ((oldVal[0][0] + 1, oldVal[0][1]), min(oldVal[1], nodes[thisMax][1] + 2))

        for child in maxObj.cited.all():
            if child.id in foundNodes:
                continue

            if child.id in nodes:
                oldVal = nodes[child.id]
                nodes[child.id] = ((oldVal[0][0] + 1, oldVal[0][1]), min(oldVal[1], nodes[thisMax][1] + 1))
            else:
                nodes[child.id] = (calcScore(child, foundNodes, keywords), nodes[thisMax][1] + 1)

            # then update the scores of all the attached nodes to that node
            for superChild in child.cites.all():
                if superChild.id in foundNodes:
                    continue

                if superChild.id in nodes:
                    oldVal = nodes[superChild.id]
                    nodes[superChild.id] = ((oldVal[0][0] + 5, oldVal[0][1]), min(oldVal[1], nodes[thisMax][1] + 2))
            for superChild in child.cited.all():
                if superChild.id in foundNodes:
                    continue

                if superChild.id in nodes:
                    oldVal = nodes[superChild.id]
                    nodes[superChild.id] = ((oldVal[0][0] + 1, oldVal[0][1]), min(oldVal[1], nodes[thisMax][1] + 2))

        # remove the found max from the pool
        del nodes[thisMax]

    return Article.objects.filter(id__in=foundNodes).distinct().all()


def search(titles, authors, keywords):
    centrals = findCentral(titles, authors, keywords)
    print(centrals)
    print(centrals.count())
    centralKeys = Keyword.objects.filter(articles__in=centrals)
    searchKeys = Keyword.objects.filter(keyword__in=keywords)
    keywords = (centralKeys | searchKeys).distinct()
    print(keywords)
    print(keywords.count())
    allNodes = traverse(centrals, keywords)

    return centrals, allNodes

