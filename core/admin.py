# core/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import GalleryCategory, GalleryItem


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