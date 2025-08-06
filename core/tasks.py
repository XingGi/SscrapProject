# core/tasks.py

import time
import random
from urllib.parse import quote_plus
from celery import shared_task
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

from .models import Platform, TargetProfile, ScrapedPost

@shared_task(bind=True)
def run_Youtube_task(self, query, video_type):
    """Tugas Celery untuk menjalankan pencarian YouTube."""
    print(f'Memulai tugas YouTube untuk query: "{query}" [Tipe: {video_type}]')

    platform, _ = Platform.objects.get_or_create(name='YouTube', defaults={'url': 'https://www.youtube.com'})

    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # PENTING: Jalankan dalam mode headless agar tidak membuka jendela browser di server
    # chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service('./chromedriver.exe'), options=chrome_options)

    try:
        if video_type == 'short':
            search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}&sp=EgIQAw%3D%3D"
        else:
            search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"

        driver.get(search_url)
        time.sleep(3)

        # Scroll
        scroll_count = 3 if video_type == 'video' else 5
        for i in range(scroll_count):
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(random.uniform(2, 4))

        # Panen Data
        if video_type == 'short':
            containers = driver.find_elements(By.TAG_NAME, 'ytd-reel-item-renderer')
        else:
            containers = driver.find_elements(By.TAG_NAME, 'ytd-video-renderer')

        print(f'Menemukan {len(containers)} container untuk tipe {video_type}.')

        # Looping dan simpan data (logika ini sama seperti sebelumnya)
        # ... (logika untuk `for video in containers` dan `_save_video_data` ada di sini) ...

    finally:
        driver.quit()

    return f'Tugas selesai. {len(containers)} container diproses.'