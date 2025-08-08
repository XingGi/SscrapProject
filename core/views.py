# core/views.py (Versi Baru)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .tasks import run_Youtube_task, scrape_youtube_detail_task
from .models import ScrapedPost, ScrapedComment, Platform

def dashboard_view(request):
    """Menampilkan menu utama aplikasi."""
    return render(request, 'core/dashboard.html')

def youtube_video_dashboard_view(request):
    """Menampilkan halaman untuk scrape YouTube Video (Engine & Hasil)."""
    # Ambil platform YouTube
    youtube_platform = Platform.objects.get(name='YouTube')
    
    # Ambil semua postingan yang berasal dari platform YouTube
    # Kita filter agar Shorts tidak ikut tampil di sini
    video_posts = ScrapedPost.objects.filter(
        profile__platform=youtube_platform, 
        post_url__icontains='watch?v=' # Trik untuk memfilter video biasa
    ).order_by('-created_at')

    context = {
        'posts': video_posts,
    }
    return render(request, 'core/youtube_video_dashboard.html', context)

def post_comments_view(request, post_id):
    """Menampilkan detail komentar dari satu postingan spesifik."""
    # Ambil objek post yang spesifik, atau tampilkan halaman 404 jika tidak ditemukan
    post = get_object_or_404(ScrapedPost, id=post_id)
    
    # Ambil semua komentar yang terhubung dengan post ini
    comments = ScrapedComment.objects.filter(post=post).order_by('-commented_at')

    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'core/post_comments_detail.html', context)

def trigger_youtube_scrape_view(request):
    """Memicu tugas scraping dari form."""
    if request.method == 'POST':
        query = request.POST.get('query')
        video_type = request.POST.get('video_type', 'video') # default ke 'video'

        if not query:
            messages.error(request, 'Query pencarian tidak boleh kosong.')
        else:
            run_Youtube_task.delay(query, video_type)
            messages.success(request, f'Tugas scraping YouTube untuk query "{query}" telah dimulai!')
        
        # Arahkan kembali ke halaman sebelumnya
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
    
    return redirect('dashboard')

def toggle_follow_up_view(request, comment_id):
    # Hanya izinkan request dengan metode POST untuk keamanan
    if request.method == 'POST':
        try:
            # Ambil objek komentar berdasarkan ID
            comment = ScrapedComment.objects.get(id=comment_id)
            # Balik nilainya (jika True jadi False, jika False jadi True)
            comment.follow_up = not comment.follow_up
            comment.save()
            # Kirim kembali response dalam format JSON sebagai konfirmasi
            return JsonResponse({'status': 'ok', 'new_value': comment.follow_up})
        except ScrapedComment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Comment not found'}, status=404)

    # Jika metodenya bukan POST, tolak request
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def trigger_youtube_detail_scrape_view(request, post_id):
    scrape_youtube_detail_task.delay(post_id)
    messages.success(request, f"Tugas pengambilan komentar untuk video ini telah dimulai di latar belakang.")
    return redirect('post_comments_detail', post_id=post_id)