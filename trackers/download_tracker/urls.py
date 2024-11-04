from django.urls import path
from . import views

urlpatterns = [
    path('announce/', views.announce, name='announce'),
    # path('scrape/', views.scrape, name='scrape'),
    path('getfile/', views.getFile, name='getfile'),
]
