from django.urls import path
from . import views

urlpatterns = [
    # Halaman Utama (Dashboard Menu)
    path('', views.dashboard_view, name='dashboard'),

    # Halaman-halaman Scraper
    path('youtube/video/', views.youtube_video_dashboard_view, name='youtube_video_dashboard'),
    # path('youtube/short/', views.youtube_short_dashboard_view, name='youtube_short_dashboard'), # Kita siapkan tapi belum dibuat

    # Halaman untuk melihat detail hasil
    path('post/<int:post_id>/comments/', views.post_comments_view, name='post_comments_detail'),

    # URL Aksi (dijalankan dari form)
    path('trigger/youtube/', views.trigger_youtube_scrape_view, name='trigger_youtube_scrape'),
    
    path('comment/toggle-follow-up/<int:comment_id>/', views.toggle_follow_up_view, name='toggle_follow_up'),
    
    path('trigger/youtube-detail/<int:post_id>/', views.trigger_youtube_detail_scrape_view, name='trigger_youtube_detail_scrape'),
]