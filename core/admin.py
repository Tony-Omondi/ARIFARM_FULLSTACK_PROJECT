# core/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import GalleryCategory, GalleryItem, PromotionalPopup  # Add PromotionalPopup here


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_preview', 'media_type', 'category', 'is_active', 'order', 'created_at')
    list_filter = ('media_type', 'category', 'is_active')
    search_fields = ('title', 'description')
    list_editable = ('order', 'is_active')
    readonly_fields = ('created_at',)

    def media_preview(self, obj):
        thumb = obj.get_thumbnail_url()
        if thumb:
            return format_html(
                '<img src="{}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 6px;" />',
                thumb
            )
        return format_html('<span style="color:#999;">No preview</span>')
    media_preview.short_description = "Preview"


# === NEW: Promotional Popup Admin ===
@admin.register(PromotionalPopup)
class PromotionalPopupAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'is_active', 'show_once_per_session', 'delay_seconds', 'link_url', 'created_at')
    list_editable = ('is_active', 'delay_seconds', 'show_once_per_session')
    readonly_fields = ('created_at', 'updated_at', 'image_preview_full')

    fieldsets = (
        (None, {
            'fields': ('title', 'flyer_image', 'image_preview_full')
        }),
        ('Behavior', {
            'fields': ('is_active', 'show_once_per_session', 'delay_seconds')
        }),
        ('Optional Link', {
            'fields': ('link_url',),
            'description': '<small class="text-muted">If provided, the entire flyer becomes clickable. Leave blank for static announcement.</small>'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.flyer_image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: contain; border-radius: 6px; background:#f9f9f9;" />',
                obj.flyer_image.url
            )
        return "(No image)"
    image_preview.short_description = "Preview"

    def image_preview_full(self, obj):
        if obj.flyer_image:
            return format_html(
                '<img src="{}" style="max-width: 500px; max-height: 600px; object-fit: contain; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" />',
                obj.flyer_image.url
            )
        return "No image uploaded yet."
    image_preview_full.short_description = "Full Preview"