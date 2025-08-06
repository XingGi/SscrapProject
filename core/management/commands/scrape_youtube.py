# core/management/commands/scrape_youtube.py

import time
import random
from django.core.management.base import BaseCommand
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

from core.models import Platform, TargetProfile, ScrapedPost, ScrapedComment

class Command(BaseCommand):
    help = 'Scraper YouTube dengan dua langkah: 1. search, 2. detail'

    def add_arguments(self, parser):
        parser.add_argument('--step', type=str, required=True, choices=['search', 'detail'], help='Langkah yang ingin dijalankan: "search" atau "detail".')
        parser.add_argument('--query', type=str, help='(Hanya untuk step "search") Kalimat yang ingin dicari.')
        parser.add_argument('--type', type=str, choices=['video', 'short'], default='video', help='(Hanya untuk step "search") Tipe konten.')

    def handle(self, *args, **options):
        step = options['step']
        
        # --- Setup Driver ---
        chrome_options = Options()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(service=Service('./chromedriver.exe'), options=chrome_options)
        
        platform, _ = Platform.objects.get_or_create(name='YouTube', defaults={'url': 'https://www.youtube.com'})

        try:
            if step == 'search':
                query = options['query']
                video_type = options['type']
                if not query:
                    self.stdout.write(self.style.ERROR('Untuk --step=search, Anda harus menyediakan --query.'))
                    return
                self._perform_search(driver, platform, query, video_type)
            elif step == 'detail':
                self._scrape_video_details(driver, platform)
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Terjadi error: {e}'))
        finally:
            driver.quit()
            self.stdout.write('Browser telah ditutup.')

    def _perform_search(self, driver, platform, query, video_type):
        """Langkah 1: Mencari video dan menyimpan link-nya."""
        # ... (Kode ini sama seperti sebelumnya, tidak perlu diubah)
        self.stdout.write(self.style.SUCCESS(f'🚀 STEP 1: SEARCH | Query: "{query}" [Tipe: {video_type}]'))
        if video_type == 'short':
            search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}&sp=EgIQAw%3D%3D"
        else:
            search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        
        driver.get(search_url)
        time.sleep(3)
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(random.uniform(2, 4))

        if video_type == 'short':
            containers = driver.find_elements(By.TAG_NAME, 'ytd-reel-item-renderer')
        else:
            containers = driver.find_elements(By.TAG_NAME, 'ytd-video-renderer')
        
        self.stdout.write(f'Menemukan {len(containers)} container.')
        # ... (Sisa logika scraping dan saving video sama seperti sebelumnya) ...
        # (Untuk keringkasan, logika looping dan saving tidak ditampilkan lagi di sini,
        # tapi di kodemu, itu adalah bagian dari fungsi ini)

    def _scrape_video_details(self, driver, platform):
        """Langkah 2: Mengunjungi video yang ada di DB dan mengambil detailnya."""
        self.stdout.write(self.style.SUCCESS('🚀 STEP 2: DETAIL | Mengambil detail video...'))
        
        # Ambil semua post dari YouTube yang deskripsinya masih kosong
        posts_to_process = ScrapedPost.objects.filter(profile__platform=platform, description__isnull=True)
        self.stdout.write(f'Menemukan {posts_to_process.count()} video untuk diproses.')

        for post in posts_to_process:
            self.stdout.write(f'  -> Memproses: {post.caption[:50]}...')
            driver.get(post.post_url)
            time.sleep(random.uniform(3, 5))

            # --- Scrape Deskripsi ---
            try:
                # Klik tombol "...more" untuk membuka deskripsi lengkap
                more_button = driver.find_element(By.ID, 'expand')
                more_button.click()
                time.sleep(1)
                
                description_element = driver.find_element(By.ID, 'description-inline-expander')
                post.description = description_element.text
                post.save() # Simpan deskripsi ke database
                self.stdout.write(self.style.SUCCESS('     -- Deskripsi berhasil disimpan.'))
            except NoSuchElementException:
                self.stdout.write(self.style.WARNING('     -- Deskripsi tidak ditemukan atau tidak ada tombol "more".'))

            # --- Scrape Komentar ---
            try:
                # Scroll ke bawah untuk memuat komentar
                driver.execute_script("window.scrollTo(0, 700);")
                time.sleep(3)
                
                comment_threads = driver.find_elements(By.TAG_NAME, 'ytd-comment-thread-renderer')
                self.stdout.write(f'     -- Menemukan {len(comment_threads)} komentar, mengambil max 5.')
                
                comment_saved_count = 0
                for comment in comment_threads[:5]: # Batasi hanya 5 komentar pertama
                    author_name = comment.find_element(By.ID, 'author-text').text
                    comment_text = comment.find_element(By.ID, 'content-text').text
                    
                    # Simpan komentar ke database
                    ScrapedComment.objects.get_or_create(
                        post=post,
                        commenter_name=author_name,
                        defaults={'comment_text': comment_text}
                    )
                    comment_saved_count +=1
                self.stdout.write(self.style.SUCCESS(f'     -- {comment_saved_count} komentar berhasil disimpan.'))

            except NoSuchElementException:
                self.stdout.write(self.style.WARNING('     -- Gagal mengambil komentar.'))
    
    # Fungsi _save_video_data dari kode sebelumnya tetap ada di sini
    def _save_video_data(self, platform, channel_name, channel_url, video_title, video_url):
        # ... (fungsi ini tidak berubah)
        pass