# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('scrape/youtube/', views.trigger_youtube_scrape_view, name='trigger_youtube_scrape'),
]