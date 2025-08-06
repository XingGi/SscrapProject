from django.contrib import admin
from .models import Platform, TargetProfile, ScrapedPost, ScrapedComment

@admin.register(ScrapedComment)
class ScrapedCommentAdmin(admin.ModelAdmin):
    list_display = ('commenter_name', 'comment_text', 'post', 'commented_at', 'follow_up')
    list_editable = ('follow_up',) # Membuat flag bisa diubah langsung dari daftar
    list_filter = ('follow_up', 'post__profile__platform')
    
@admin.register(TargetProfile)
class TargetProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'platform', 'domisili', 'website_url', 'scraped_at')
    list_filter = ('platform', 'domisili')
    search_fields = ('username', 'display_name', 'bio')

@admin.register(ScrapedPost)
class ScrapedPostAdmin(admin.ModelAdmin):
    list_display = ('caption', 'profile', 'posted_at')
    list_filter = ('profile__platform', 'profile')
    search_fields = ('caption',)
    date_hierarchy = 'posted_at' # Filter cepat berdasarkan tanggal

# Daftarkan model lain yang tidak butuh kustomisasi khusus
admin.site.register(Platform)