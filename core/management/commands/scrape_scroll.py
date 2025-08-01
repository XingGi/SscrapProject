# core/management/commands/scrape_scroll.py

import time
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from core.models import Platform, TargetProfile, ScrapedPost

class Command(BaseCommand):
    help = 'Menjalankan scraper dengan kemampuan infinite scroll.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Memulai scraper infinite scroll...'))

        platform, _ = Platform.objects.get_or_create(
            name='quotes.toscrape.com/scroll', defaults={'url': 'http://quotes.toscrape.com/scroll'}
        )
        target_profile, _ = TargetProfile.objects.get_or_create(
            platform=platform, username='quotes.toscrape.com', defaults={'display_name': 'Quotes To Scrape (Scroll)'}
        )
        
        driver = webdriver.Chrome(
            service=Service(executable_path='./chromedriver.exe'),
            options=Options()
        )

        url = 'http://quotes.toscrape.com/scroll'
        driver.get(url)
        self.stdout.write(f'Mengunjungi: {url}')
        time.sleep(2)

        # --- LOGIKA INFINITE SCROLL DIMULAI DI SINI ---
        last_height = driver.execute_script("return document.body.scrollHeight")
        self.stdout.write(self.style.HTTP_INFO('Memulai proses scrolling...'))

        while True:
            # Scroll ke bawah
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Tunggu konten baru dimuat
            time.sleep(2)

            # Hitung tinggi halaman yang baru dan bandingkan dengan yang lama
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # Jika tinggi halaman tidak berubah, kita sudah di dasar.
                self.stdout.write(self.style.WARNING('Sudah mencapai dasar halaman.'))
                break
            last_height = new_height
            self.stdout.write('   -> Scroll ke bawah...')

        # --- Setelah semua konten termuat, baru kita scrape ---
        self.stdout.write(self.style.SUCCESS('✅ Proses scrolling selesai. Memulai panen data...'))
        
        quotes = driver.find_elements(By.CLASS_NAME, 'quote')
        self.stdout.write(f'Menemukan total {len(quotes)} kutipan.')
        
        saved_count = 0
        for quote in quotes:
            text = quote.find_element(By.CLASS_NAME, 'text').text
            author = quote.find_element(By.CLASS_NAME, 'author').text
            post_unique_url = f"http://quotes.toscrape.com/scroll/author/{author.replace(' ', '-')}/{text[:30]}"

            _, created = ScrapedPost.objects.get_or_create(
                post_url=post_unique_url,
                defaults={'profile': target_profile, 'caption': f'"{text}" - {author}'}
            )
            if created:
                saved_count += 1
        
        driver.quit()
        self.stdout.write(self.style.SUCCESS(f'🎉 Scraping selesai! {saved_count} kutipan baru disimpan.'))