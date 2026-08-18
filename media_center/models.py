from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image
import os
from io import BytesIO
from django.core.files.base import ContentFile

def optimize_image(image_field, max_width=1920):
    if not image_field:
        return
    # Check if already webp
    if image_field.name.endswith('.webp'):
        return

    try:
        img = Image.open(image_field)
        # Convert to RGB if necessary
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # Resize if too large
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int((float(img.height) * float(ratio)))
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Save as WebP
        buffer = BytesIO()
        img.save(buffer, format='WEBP', quality=85)
        
        # Replace original field with new WebP content
        name_without_ext = os.path.splitext(image_field.name)[0]
        new_name = f"{name_without_ext}.webp"
        
        image_field.save(new_name, ContentFile(buffer.getvalue()), save=False)
    except Exception as e:
        print(f"Error optimizing image: {e}")

# ── Gallery Management (Removed) ────────────────────────────────

# ── Video Library ───────────────────────────────────────────────

class VideoCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Video Categories"
        
    def __str__(self):
        return self.name

class VideoPlaylist(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'title']
        
    def __str__(self):
        return self.title

class Video(models.Model):
    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('facebook', 'Facebook'),
    ]
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='youtube')
    video_id = models.CharField(max_length=100, blank=True, help_text="Can be left blank if you provide the full Video URL below")
    video_url = models.URLField(blank=True, help_text="Paste the full video URL here to auto-extract the ID")
    embed_code = models.TextField(blank=True, help_text="Optional: Paste the raw iframe embed code directly from YouTube/Facebook")
    thumbnail_url = models.URLField(blank=True, help_text="External URL to the thumbnail (auto-fetched)")
    thumbnail = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True, help_text="Upload a local image for the thumbnail (overrides the auto-fetched URL)")
    
    category = models.ForeignKey(VideoCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='videos')
    playlist = models.ForeignKey(VideoPlaylist, on_delete=models.SET_NULL, null=True, blank=True, related_name='videos')
    related_service = models.ForeignKey('main.Service', on_delete=models.SET_NULL, null=True, blank=True)
    related_branch = models.ForeignKey('main.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    
    short_description = models.TextField(blank=True)
    published_date = models.DateTimeField(default=timezone.now)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    
    # SEO
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:48].rstrip('-')
            
        # Auto-extract video ID from URL if provided
        if self.video_url:
            import re
            if self.platform == 'youtube':
                match = re.search(r'(?:v=|youtu\.be/|embed/|shorts/|live/|watch\?.*?v=)([0-9A-Za-z_-]{11})', self.video_url)
                if match:
                    self.video_id = match.group(1)
            elif self.platform == 'facebook':
                match = re.search(r'facebook\.com/(?:watch/\?v=|reel/|.*/videos/|video\.php\?v=)(\d+)', self.video_url)
                if match:
                    self.video_id = match.group(1)
            elif self.platform == 'tiktok':
                match = re.search(r'tiktok\.com/.*?/video/(\d+)', self.video_url)
                if match:
                    self.video_id = match.group(1)
            elif self.platform == 'instagram':
                match = re.search(r'instagram\.com/(?:p|reel|reels|tv|share/reel)/([A-Za-z0-9_-]+)', self.video_url)
                if match:
                    self.video_id = match.group(1)
                    
        super().save(*args, **kwargs)
        
    class Meta:
        ordering = ['-published_date']
        
    def get_embed_url(self):
        """
        Generate mobile-optimized, cross-browser embed URL (Android, iOS Safari, desktop).
        Includes playsinline=1, modestbranding, rel=0 for YouTube.
        """
        if self.platform == 'youtube':
            if self.video_id:
                return f"https://www.youtube.com/embed/{self.video_id}?enablejsapi=1&playsinline=1&rel=0&modestbranding=1"
            return ""
        elif self.platform == 'tiktok':
            if self.video_id:
                return f"https://www.tiktok.com/embed/v2/{self.video_id}"
            return ""
        elif self.platform == 'facebook':
            if self.video_url:
                import urllib.parse
                encoded_url = urllib.parse.quote(self.video_url)
                return f"https://www.facebook.com/plugins/video.php?href={encoded_url}&show_text=false&allowfullscreen=true"
            return ""
        elif self.platform == 'instagram':
            if self.video_id:
                return f"https://www.instagram.com/reel/{self.video_id}/embed/captioned/"
            elif self.video_url:
                clean_url = self.video_url.split('?')[0].rstrip('/')
                return f"{clean_url}/embed/captioned/"
        return ""

    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail.url
        if self.thumbnail_url:
            return self.thumbnail_url
        if self.platform == 'youtube' and self.video_id:
            return f"https://img.youtube.com/vi/{self.video_id}/hqdefault.jpg"
        return ""

    def __str__(self):
        return self.title

# ── Social Media Integration ────────────────────────────────────

class ConnectedSocialAccount(models.Model):
    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
    ]
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    account_name = models.CharField(max_length=100)
    access_token = models.TextField(blank=True)
    is_connected = models.BooleanField(default=False)
    last_sync_time = models.DateTimeField(null=True, blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_platform_display()} - {self.account_name}"

class SocialSyncSetting(models.Model):
    platform = models.CharField(max_length=20, choices=ConnectedSocialAccount.PLATFORM_CHOICES, unique=True)
    enable_auto_sync = models.BooleanField(default=False)
    SYNC_FREQ_CHOICES = [
        ('30m', 'Every 30 Minutes'),
        ('1h', 'Every Hour'),
        ('6h', 'Every 6 Hours'),
        ('24h', 'Daily'),
    ]
    sync_frequency = models.CharField(max_length=10, choices=SYNC_FREQ_CHOICES, default='24h')
    max_videos_to_import = models.PositiveSmallIntegerField(default=10)
    auto_publish = models.BooleanField(default=True)
    auto_generate_thumbnail = models.BooleanField(default=True)
    
    default_category = models.ForeignKey(VideoCategory, on_delete=models.SET_NULL, null=True, blank=True)
    default_playlist = models.ForeignKey(VideoPlaylist, on_delete=models.SET_NULL, null=True, blank=True)
    default_related_service = models.ForeignKey('main.Service', on_delete=models.SET_NULL, null=True, blank=True)
    default_branch = models.ForeignKey('main.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Settings for {self.get_platform_display()}"

class SocialSyncLog(models.Model):
    platform = models.CharField(max_length=20, choices=ConnectedSocialAccount.PLATFORM_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('success', 'Success'), ('error', 'Error')])
    imported_videos = models.PositiveIntegerField(default=0)
    failed_videos = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.platform} Sync on {self.date.strftime('%Y-%m-%d %H:%M')}"



# ── Documents (Removed) ─────────────────────────────────────────
