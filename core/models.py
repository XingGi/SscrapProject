from django.db import models

class Platform(models.Model):
    """Mewakili platform media sosial yang bisa di-scrape."""
    name = models.CharField(max_length=100, unique=True, help_text="Nama platform, cth: Instagram")
    url = models.URLField(max_length=200, help_text="URL utama platform")
    last_scraped = models.DateTimeField(null=True, blank=True, help_text="Kapan terakhir kali platform ini di-scrape")

    def __str__(self):
        return self.name

class TargetProfile(models.Model):
    """Menyimpan informasi tentang satu profil/akun yang menjadi target scraping."""
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, help_text="Platform asal profil ini")
    username = models.CharField(max_length=255, help_text="Username atau nama unik akun")
    display_name = models.CharField(max_length=255, null=True, blank=True, help_text="Nama tampilan akun")
    email = models.EmailField(null=True, blank=True, help_text="Email yang ditemukan (jika ada)")
    domisili = models.CharField(max_length=255, null=True, blank=True, help_text="Domisili yang ditemukan (jika ada)")
    bio = models.TextField(null=True, blank=True, help_text="Teks bio atau deskripsi profil")
    website_url = models.URLField(null=True, blank=True, help_text="URL website yang ada di bio")
    scraped_at = models.DateTimeField(auto_now_add=True, help_text="Waktu data profil ini disimpan")

    def __str__(self):
        return f"{self.username} di {self.platform.name}"

class ScrapedPost(models.Model):
    """Menyimpan satu data postingan dari sebuah TargetProfile."""
    profile = models.ForeignKey(TargetProfile, on_delete=models.CASCADE, related_name="posts")
    post_url = models.URLField(unique=True, help_text="URL unik dari postingan")
    caption = models.TextField(null=True, blank=True, help_text="Teks atau caption dari postingan")
    media_url = models.URLField(null=True, blank=True, help_text="URL ke gambar atau video utama")
    posted_at = models.DateTimeField(null=True, blank=True, help_text="Waktu postingan ini diunggah")

    def __str__(self):
        return f"Postingan dari {self.profile.username} di {self.post_url}"

class ScrapedComment(models.Model):
    """Menyimpan satu komentar dari sebuah ScrapedPost."""
    post = models.ForeignKey(ScrapedPost, on_delete=models.CASCADE, related_name="comments")
    commenter_name = models.CharField(max_length=255)
    comment_text = models.TextField()
    commented_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Komentar oleh {self.commenter_name} pada postingan {self.post.id}"