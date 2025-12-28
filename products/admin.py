from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import (
    Category, Product, ProductBasket, BasketItem,
    Recipe, RecipeIngredient, Merchandise, ProductReview
)


def display_image(image_field):
    if image_field:
        return format_html(
            '<img src="{}" style="width:40px;height:40px;object-fit:cover;border-radius:6px;" />',
            image_field.url
        )
    return "-"


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['image_preview', 'name', 'product_count', 'is_active', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']

    @display(description="Image")
    def image_preview(self, obj):
        return display_image(obj.image)

    @display(description="Products")
    def product_count(self, obj):
        return obj.products.filter(is_active=True).count()


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['image_preview', 'product_id', 'name', 'category', 'price', 'stock', 'is_active']
    search_fields = ['name', 'product_id']
    list_filter = ['category', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['product_id', 'created_at', 'updated_at']

    @display(description="Image")
    def image_preview(self, obj):
        return display_image(obj.image)


class BasketItemInline(TabularInline):
    model = BasketItem
    extra = 1
    autocomplete_fields = ['product']


@admin.register(ProductBasket)
class ProductBasketAdmin(ModelAdmin):
    list_display = ['image_preview', 'basket_id', 'name', 'price', 'stock', 'is_active']
    search_fields = ['name', 'basket_id']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [BasketItemInline]
    readonly_fields = ['basket_id', 'stock', 'created_at', 'updated_at']

    @display(description="Image")
    def image_preview(self, obj):
        return display_image(obj.image)


class RecipeIngredientInline(TabularInline):
    model = RecipeIngredient
    extra = 2
    autocomplete_fields = ['product']
    fields = ['order', 'product', 'custom_name', 'quantity', 'notes']
    readonly_fields = ['ingredient_type']

    @display(description="Type")
    def ingredient_type(self, obj):
        if obj.product:
            return format_html('<span style="color:#27ae60;">✓ Product</span>')
        if obj.custom_name:
            return format_html('<span style="color:#e67e22;">Custom</span>')
        return "—"

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['custom_name'].widget.attrs.update({
            'placeholder': 'e.g. Salt, 2 cloves garlic, Olive oil... (if not in products)'
        })
        return formset


@admin.register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ['image_preview', 'title', 'difficulty', 'total_time', 'servings', 'is_featured']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ['difficulty', 'is_featured']
    inlines = [RecipeIngredientInline]

    @display(description="Image")
    def image_preview(self, obj):
        return display_image(obj.image)

    @display(description="Total Time")
    def total_time(self, obj):
        return f"{obj.total_time} min"


@admin.register(Merchandise)
class MerchandiseAdmin(ModelAdmin):
    list_display = ['image_preview', 'product_id', 'name', 'price', 'stock', 'is_active']
    search_fields = ['name']
    list_editable = ['stock', 'is_active']

    @display(description="Image")
    def image_preview(self, obj):
        return display_image(obj.image)


@admin.register(ProductReview)
class ProductReviewAdmin(ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved']
    search_fields = ['product__name', 'user__email']
    list_editable = ['is_approved']