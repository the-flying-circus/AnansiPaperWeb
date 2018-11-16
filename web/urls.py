from django.urls import path
from django.views.generic import TemplateView

from . import views


urlpatterns = [
    path('', TemplateView.as_view(template_name="web.html")),
    path('search', views.search),
    path('node', views.node)
]
