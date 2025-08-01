# core/management/commands/scrape_quotes.py

import time
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# --- Import Exception jika elemen tidak ditemukan ---
from selenium.common.exceptions import NoSuchElementException

from core.models import Platform, TargetProfile, ScrapedPost

class Command(BaseCommand):
    help = 'Menjalankan scraper dengan kemampuan pagination untuk mengambil semua kutipan.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Memulai proses scraping dengan pagination...'))

        platform, _ = Platform.objects.get_or_create(
            name='quotes.toscrape.com', defaults={'url': 'http://quotes.toscrape.com/'}
        )
        target_profile, _ = TargetProfile.objects.get_or_create(
            platform=platform, username='quotes.toscrape.com', defaults={'display_name': 'Quotes To Scrape'}
        )
        
        chrome_options = Options()
        chrome_service = Service(executable_path='./chromedriver.exe')
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        url = 'http://quotes.toscrape.com/'
        driver.get(url)
        time.sleep(2)

        # --- LOGIKA PAGINATION DIMULAI DI SINI ---
        page_count = 1
        while True: # Loop akan berjalan selamanya sampai kita perintahkan berhenti
            self.stdout.write(self.style.HTTP_INFO(f'--- Memproses halaman {page_count} ---'))
            
            quotes = driver.find_elements(By.CLASS_NAME, 'quote')
            self.stdout.write(f'✅ Menemukan {len(quotes)} kutipan di halaman ini.')
            
            saved_count = 0
            for quote in quotes:
                text = quote.find_element(By.CLASS_NAME, 'text').text
                author = quote.find_element(By.CLASS_NAME, 'author').text
                post_unique_url = f"{url}author/{author.replace(' ', '-')}/{text[:30]}"

                _, created = ScrapedPost.objects.get_or_create(
                    post_url=post_unique_url,
                    defaults={'profile': target_profile, 'caption': f'"{text}" - {author}'}
                )
                if created:
                    saved_count += 1
            
            self.stdout.write(f'  -> {saved_count} kutipan baru disimpan.')

            # --- Cari dan Klik Tombol "Next" ---
            try:
                # Cari link di dalam elemen <li> dengan class 'next'
                next_button = driver.find_element(By.CSS_SELECTOR, 'li.next a')
                next_button.click()
                self.stdout.write('Navigasi ke halaman berikutnya...')
                time.sleep(2) # Tunggu halaman baru termuat
                page_count += 1
            except NoSuchElementException:
                # Jika tombol "Next" tidak ditemukan, berarti ini halaman terakhir.
                self.stdout.write(self.style.WARNING('Tombol "Next" tidak ditemukan. Ini halaman terakhir.'))
                break # Hentikan loop while

        driver.quit()
        self.stdout.write(self.style.SUCCESS('🎉 Scraping semua halaman selesai!'))