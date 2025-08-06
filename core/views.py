# core/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .tasks import run_Youtube_task # Impor tugas Celery kita

def dashboard_view(request):
    # Nanti kita bisa tampilkan data di sini
    return render(request, 'core/dashboard.html')

def trigger_youtube_scrape_view(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        video_type = request.POST.get('video_type')

        if not query:
            messages.error(request, 'Query pencarian tidak boleh kosong.')
            return redirect('dashboard')
        
        # Ini bagian pentingnya! Memanggil tugas untuk berjalan di background.
        run_Youtube_task.delay(query, video_type)

        messages.success(request, f'Tugas scraping YouTube untuk query "{query}" telah dimulai di latar belakang!')
        return redirect('dashboard')
    
    # Jika bukan POST, kembalikan ke dashboard
    return redirect('dashboard')