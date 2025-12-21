# core/models.py
from django.db import models

class GalleryCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Gallery Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class GalleryItem(models.Model):
    MEDIA_TYPES = [
        ('image', 'Farm Image (Upload)'),
        ('youtube', 'YouTube Video'),
        ('instagram', 'Instagram (Reel/Post)'),
        ('tiktok', 'TikTok Video'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Short description appearing under the media")
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='items')
    
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, default='image')

    # Content Fields
    image = models.ImageField(upload_to='gallery/', blank=True, null=True, help_text="Upload image for Farm Image type")
    social_url = models.URLField(blank=True, null=True, help_text="Paste full YouTube, Instagram, or TikTok URL")

    # Meta
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_media_type_display()})"

    # --- Thumbnail & Embed Helpers ---

    def get_thumbnail_url(self):
        """Returns a preview image URL for all media types"""
        if self.media_type == 'image' and self.image:
            return self.image.url

        elif self.media_type == 'youtube':
            embed_url = self.get_youtube_embed_url()
            if embed_url:
                video_id = embed_url.split('/embed/')[-1]
                return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

        elif self.media_type == 'instagram':
            if self.social_url:
                # Instagram oembed thumbnail (works reliably)
                post_id = self.social_url.strip('/').split('/')[-1]
                return f"https://www.instagram.com/p/{post_id}/media/?size=m"

        elif self.media_type == 'tiktok':
            video_id = self.get_tiktok_id()
            if video_id:
                return f"https://www.tiktok.com/oembed/thumbnail/{video_id}"

        return None  # fallback placeholder if needed

    def get_youtube_embed_url(self):
        if not self.social_url:
            return None
        video_id = None
        if 'youtu.be' in self.social_url:
            video_id = self.social_url.split('/')[-1].split('?')[0]
        elif 'youtube.com/shorts/' in self.social_url:
            video_id = self.social_url.split('/shorts/')[-1].split('?')[0]
        elif 'youtube.com/watch' in self.social_url:
            video_id = self.social_url.split('v=')[-1].split('&')[0]
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        return None

    def get_instagram_embed_url(self):
        if not self.social_url:
            return None
        url = self.social_url.rstrip('/') + '/'
        return f"{url}embed"

    def get_tiktok_embed_code(self):
        video_id = self.get_tiktok_id()
        if not video_id:
            return None
        return f'''
        <blockquote class="tiktok-embed" cite="{self.social_url}" data-video-id="{video_id}" style="max-width: 605px; min-width: 325px;"> 
            <section> </section> 
        </blockquote>
        <script async src="https://www.tiktok.com/embed.js"></script>
        '''

    def get_tiktok_id(self):
        if not self.social_url:
            return None
        try:
            return self.social_url.split('/video/')[-1].split('?')[0]
        except:
            return None




class PromotionalPopup(models.Model):
    title = models.CharField(max_length=200, help_text="Internal name (for admin only)")
    flyer_image = models.ImageField(upload_to='promotions/', help_text="The promotional flyer/banner image")
    link_url = models.URLField(blank=True, null=True, help_text="Optional: Where to go when flyer is clicked (e.g., referral page or WhatsApp)")
    is_active = models.BooleanField(default=False, help_text="Check to show popup site-wide")
    show_once_per_session = models.BooleanField(default=True, help_text="If checked, popup shows only once per browser session")
    delay_seconds = models.PositiveIntegerField(default=3, help_text="Seconds to wait before showing popup")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Promotional Popup"
        verbose_name_plural = "Promotional Popups"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @staticmethod
    def get_active_popup():
        """Return the first active popup (supports only one active at a time)"""
        return PromotionalPopup.objects.filter(is_active=True).first()