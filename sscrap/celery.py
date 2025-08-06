# sscrap/celery.py

import os
from celery import Celery

# Atur 'DJANGO_SETTINGS_MODULE' agar Celery tahu cara menemukan proyek Django-mu.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sscrap.settings')

# Buat instance aplikasi Celery
app = Celery('sscrap')

# Celery akan mengambil konfigurasinya dari settings.py Django-mu.
# namespace='CELERY' berarti semua variabel konfigurasi Celery di settings.py
# harus diawali dengan 'CELERY_' (contoh: CELERY_BROKER_URL).
app.config_from_object('django.conf:settings', namespace='CELERY')

# Secara otomatis mencari file tasks.py di semua aplikasi Django yang terdaftar.
app.autodiscover_tasks()