# core/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

# --- UNFOLD IMPORTS ---
from unfold.admin import ModelAdmin
from unfold.decorators import display
# ----------------------

from .models import GalleryCategory, GalleryItem, PromotionalPopup

@admin.register(GalleryCategory)
class GalleryCategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'order', 'item_count')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)
    search_fields = ('name',)

    @display(description="Items")
    def item_count(self, obj):
        return obj.items.count()


@admin.register(GalleryItem)
class GalleryItemAdmin(ModelAdmin):
    list_display = (
        'media_preview', 'title', 'media_type_badge', 
        'category', 'is_active', 'order', 'created_at'
    )
    list_filter = ('media_type', 'category', 'is_active')
    search_fields = ('title', 'description')
    list_editable = ('order', 'is_active')
    readonly_fields = ('created_at',)
    list_per_page = 20

    @display(description="Preview")
    def media_preview(self, obj):
        thumb = obj.get_thumbnail_url()
        if thumb:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);" />',
                thumb
            )
        return format_html('<span class="text-gray-400 text-xs">No preview</span>')

    @display(
        description="Type",
        label={
            'image': 'success',      # Green
            'youtube': 'danger',     # Red
            'instagram': 'warning',  # Orange/Yellow
            'tiktok': 'info',        # Blue
        }
    )
    def media_type_badge(self, obj):
        return obj.media_type


@admin.register(PromotionalPopup)
class PromotionalPopupAdmin(ModelAdmin):
    list_display = (
        'image_preview', 'title', 'is_active', 
        'behavior_info', 'link_status', 'created_at'
    )
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at', 'image_preview_full')

    # Use Unfold's Tab layout for a cleaner interface
    fieldsets = (
        ('Content', {
            'fields': (('title', 'is_active'), 'flyer_image', 'image_preview_full')
        }),
        ('Configuration', {
            'classes': ('tab',),
            'fields': ('show_once_per_session', 'delay_seconds', 'link_url'),
            'description': 'Control how and when the popup appears to visitors.'
        }),
        ('Timestamps', {
            'classes': ('tab',),
            'fields': ('created_at', 'updated_at'),
        }),
    )

    @display(description="Flyer")
    def image_preview(self, obj):
        if obj.flyer_image:
            return format_html(
                '<img src="{}" style="width: 80px; height: 50px; object-fit: cover; border-radius: 4px; border: 1px solid #e5e7eb;" />',
                obj.flyer_image.url
            )
        return "No Image"

    @display(description="Current Flyer", label=False)
    def image_preview_full(self, obj):
        if obj.flyer_image:
            return format_html(
                '<div style="background: #f3f4f6; padding: 10px; border-radius: 8px; display: inline-block;">'
                '<img src="{}" style="max-width: 100%; max-height: 400px; object-fit: contain; border-radius: 6px;" />'
                '</div>',
                obj.flyer_image.url
            )
        return "No image uploaded yet."

    @display(description="Behavior")
    def behavior_info(self, obj):
        frequency = "Once/Session" if obj.show_once_per_session else "Always"
        return f"{frequency} after {obj.delay_seconds}s"

    @display(description="Link", boolean=True)
    def link_status(self, obj):
        return bool(obj.link_url)