# core/tasks.py (Versi Lengkap dan Benar)

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

def _save_video_data(platform, channel_name, channel_url, video_title, video_url):
    """Fungsi bantuan untuk menyimpan data ke database agar tidak duplikat kode."""
    if not all([video_title, video_url, channel_name]):
        return False
    
    profile, _ = TargetProfile.objects.get_or_create(
        username=channel_name, 
        platform=platform,
        defaults={'display_name': channel_name, 'website_url': channel_url}
    )
    
    _, created = ScrapedPost.objects.get_or_create(
        post_url=video_url,
        defaults={'profile': profile, 'caption': video_title}
    )
    return created

@shared_task(bind=True)
def run_Youtube_task(self, query, video_type):
    """Tugas Celery untuk menjalankan pencarian YouTube."""
    print(f'Memulai tugas YouTube untuk query: "{query}" [Tipe: {video_type}]')

    platform, _ = Platform.objects.get_or_create(name='YouTube', defaults={'url': 'https://www.youtube.com'})
    
    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # chrome_options.add_argument("--headless") # Aktifkan ini jika tidak ingin melihat jendela browser
    
    driver = webdriver.Chrome(service=Service('./chromedriver.exe'), options=chrome_options)
    saved_count = 0

    try:
        if video_type == 'short':
            search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}&sp=EgIQAw%3D%3D"
        else:
            search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        
        driver.get(search_url)
        time.sleep(3)

        scroll_count = 5 if video_type == 'short' else 3
        print(f"Melakukan scroll sebanyak {scroll_count} kali...")
        for i in range(scroll_count):
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(random.uniform(2, 4))

        if video_type == 'short':
            containers = driver.find_elements(By.TAG_NAME, 'ytd-reel-item-renderer')
        else:
            containers = driver.find_elements(By.TAG_NAME, 'ytd-video-renderer')

        print(f'Menemukan {len(containers)} container untuk tipe {video_type}.')
        
        for video in containers:
            try:
                if video_type == 'short':
                    title_element = video.find_element(By.ID, 'video-title')
                    channel_element = video.find_element(By.TAG_NAME, 'ytd-channel-name').find_element(By.ID, 'text-container')
                    channel_url = "N/A" # URL channel sulit didapat di halaman search Shorts
                else: # video biasa
                    title_element = video.find_element(By.ID, 'video-title')
                    channel_element = video.find_element(By.ID, 'channel-name').find_element(By.TAG_NAME, 'a')
                    channel_url = channel_element.get_attribute('href')
                
                video_title = title_element.text
                video_url = title_element.get_attribute('href')
                channel_name = channel_element.text

                if _save_video_data(platform, channel_name, channel_url, video_title, video_url):
                    saved_count += 1
            except NoSuchElementException:
                continue
        
        print(f'{saved_count} video baru berhasil disimpan.')

    finally:
        driver.quit()
    
    return f'Tugas selesai. {saved_count} video baru diproses.'