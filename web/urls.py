from django.urls import path
from django.views.generic import TemplateView

from . import views


urlpatterns = [
    path('', views.generate_graph, name="web"),
    path('search', views.search),
    path('graph', views.graph),
    path('node', views.node),
]
