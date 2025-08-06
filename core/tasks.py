# core/tasks.py (Solusi Definitif untuk Bug "Hanya 1 Video")

import time
import random
from urllib.parse import quote_plus
from celery import shared_task
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from .models import Platform, TargetProfile, ScrapedPost

def _save_video_data(platform, channel_name, channel_url, video_title, video_url):
    """Fungsi bantuan untuk menyimpan data ke database."""
    if not all([video_title, video_url, channel_name]):
        return False
    
    profile, _ = TargetProfile.objects.get_or_create(
        username=channel_name.strip(), 
        platform=platform,
        defaults={'display_name': channel_name.strip(), 'website_url': channel_url}
    )
    
    _, created = ScrapedPost.objects.get_or_create(
        post_url=video_url,
        defaults={'profile': profile, 'caption': video_title}
    )
    return created

@shared_task(bind=True)
def run_Youtube_task(self, query, video_type):
    # Nama fungsi disesuaikan dengan yang dipanggil di views.py
    print(f'Memulai tugas YouTube untuk query: "{query}"')
    platform, _ = Platform.objects.get_or_create(name='YouTube', defaults={'url': 'https://www.youtube.com'})
    
    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # chrome_options.add_argument("--headless")
    
    driver = webdriver.Chrome(service=Service('./chromedriver.exe'), options=chrome_options)
    wait = WebDriverWait(driver, 10)
    saved_count = 0

    try:
        search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        driver.get(search_url)
        print(f"Halaman dibuka: {search_url}")

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "ytd-video-renderer")))
        print("Container video ditemukan. Melakukan scroll...")

        for i in range(2):
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)

        containers = driver.find_elements(By.TAG_NAME, 'ytd-video-renderer')
        print(f'Menemukan total {len(containers)} container video.')

        for i, video_container in enumerate(containers):
            print(f"\n--- Memproses container ke-{i+1} ---")
            try:
                # --- PERBAIKAN UTAMA: MENCARI JUDUL DI DALAM CONTAINER YANG BENAR ---
                # Kita tidak lagi menggunakan wait.until di sini, tapi find_element dari container-nya
                title_element = video_container.find_element(By.CSS_SELECTOR, "a#video-title")
                # ---------------------------------------------------------------
                
                video_title = title_element.text
                video_url = title_element.get_attribute('href')
                print(f"  -> Judul Ditemukan: {video_title[:30]}...")

                channel_element = video_container.find_element(By.CSS_SELECTOR, "ytd-channel-name a")
                channel_name = channel_element.get_attribute("textContent").strip()
                channel_url = channel_element.get_attribute('href')
                print(f"  -> Channel Ditemukan: '{channel_name}'")

                if _save_video_data(platform, channel_name, channel_url, video_title, video_url):
                    saved_count += 1
                    print(f"  ==> SUKSES DISIMPAN!")

            except NoSuchElementException:
                print("  -> GAGAL: Struktur tidak cocok (kemungkinan iklan). Melewati.")
                continue
        
        print(f'\n{saved_count} video baru berhasil disimpan.')

    except Exception as e:
        print(f"\nGAGAL TOTAL: Terjadi error yang tidak bisa ditangani: {e}")
    finally:
        driver.quit()
    
    return f'Tugas selesai. {saved_count} video baru diproses.'