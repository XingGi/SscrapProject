# core/management/commands/login_test.py

import time
from django.core.management.base import BaseCommand
from decouple import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

class Command(BaseCommand):
    help = 'Melakukan tes login otomatis menggunakan Selenium.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Memulai tes login...'))

        # --- Ambil Kredensial dari file .env ---
        # config() akan secara otomatis membaca dari file .env kita
        username = config('DUMMY_USER')
        password = config('DUMMY_PASSWORD')

        # --- Setup Selenium ---
        driver = webdriver.Chrome(service=Service('./chromedriver.exe'), options=Options())

        # --- Proses Login ---
        url = 'http://quotes.toscrape.com/login'
        driver.get(url)
        self.stdout.write(f'Mengunjungi halaman login: {url}')
        time.sleep(2)

        # 1. Cari elemen form, lalu ketik username & password
        #    Gunakan "Inspect Element" di browser untuk menemukan 'id' atau 'name' dari input field
        username_field = driver.find_element(By.ID, 'username')
        password_field = driver.find_element(By.ID, 'password')

        username_field.send_keys(username)
        self.stdout.write('   -> Mengetik username.')
        password_field.send_keys(password)
        self.stdout.write('   -> Mengetik password.')
        time.sleep(1)

        # 2. Cari tombol login dan klik
        #    Tombol ini tidak punya ID, tapi kita bisa cari berdasarkan tipenya dan valuenya
        login_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="Login"]')
        login_button.click()
        self.stdout.write('   -> Mengklik tombol login.')
        time.sleep(3) # Tunggu hasil login

        # 3. Verifikasi apakah login berhasil
        #    Cara verifikasi paling umum adalah mencari elemen yang hanya ada setelah login berhasil.
        #    Dalam kasus ini, kita cari link "Logout".
        try:
            logout_link = driver.find_element(By.PARTIAL_LINK_TEXT, 'Logout')
            self.stdout.write(self.style.SUCCESS('✅ Login BERHASIL! Link "Logout" ditemukan.'))
        except NoSuchElementException:
            self.stdout.write(self.style.ERROR('❌ Login GAGAL. Link "Logout" tidak ditemukan.'))

        driver.quit()