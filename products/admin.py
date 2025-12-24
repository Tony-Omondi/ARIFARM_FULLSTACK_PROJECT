from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count

# --- UNFOLD IMPORTS ---
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from unfold.contrib.forms.widgets import WysiwygWidget
# ----------------------

from .models import (
    Category, Product, ProductBasket, BasketItem, 
    Recipe, RecipeIngredient, Merchandise, ProductReview
)

# ================= HELPER FUNCTIONS =================
def display_image(image_field):
    """Helper to display small thumbnails in admin list"""
    if image_field:
        return format_html(
            '<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 6px;" />',
            image_field.url
        )
    return format_html('<span style="color: #ccc;">-</span>')

# ================= ADMIN CLASSES =================

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['image_preview', 'name', 'product_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']

    @display(description="Image")
    def image_preview(self, obj):
        return display_image(obj.image)

    @display(description="Products", ordering="_product_count")
    def product_count(self, obj):
        return obj._product_count

    def get_queryset(self, request):
        # Annotate count so we can sort by it
        return super().get_queryset(request).prefetch_related('products').annotate(
            _product_count=Count('products')
        )


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = [
        'image_preview', 'product_id', 'name', 'category', 
        'price_display', 'stock_status', 'is_new', 'is_active'
    ]
    list_filter = ['category', 'is_new', 'is_in_basket', 'is_active', 'created_at']
    search_fields = ['name', 'product_id', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_new', 'is_active']
    readonly_fields = ['product_id', 'is_in_basket', 'created_at', 'updated_at']
    list_per_page = 20

    fieldsets = (
        ('Basic Information', {
            'fields': (('product_id', 'is_active'), 'name', 'slug', 'description')
        }),
        ('Media', {
            'fields': ('image', 'is_new')
        }),
        ('Pricing & Inventory', {
            'classes': ('tab',),
            'fields': ('price', 'stock', 'category')
        }),
        ('System Info', {
            'classes': ('collapse',),
            'fields': ('is_in_basket', 'created_at', 'updated_at')
        }),
    )

    @display(description="Image")
    def image_preview(self, obj):
        return display_image(obj.image)

    @display(description="Price")
    def price_display(self, obj):
        if obj.price is None:
            return "-"
        return f"KSh {obj.price:,.2f}"

    @display(
        description="Stock",
        label={
            "Out of Stock": "danger",  # Red
            "Low Stock": "warning",    # Yellow
            "In Stock": "success",     # Green
        }
    )
    def stock_status(self, obj):
        if obj.stock is None:
            return "Out of Stock"
        if obj.stock == 0:
            return "Out of Stock"
        if obj.stock < 10:
            return "Low Stock"
        return "In Stock"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


class BasketItemInline(TabularInline):
    model = BasketItem
    extra = 1
    autocomplete_fields = ['product']
    tab = True


@admin.register(ProductBasket)
class ProductBasketAdmin(ModelAdmin):
    list_display = [
        'image_preview', 'basket_id', 'name', 'price_display', 
        'savings_badge', 'stock_display', 'is_active'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'basket_id']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    readonly_fields = [
        'basket_id', 'created_at', 'updated_at', 'stock', 
        'total_original_price', 'discount_percentage', 'discount_amount',
        'savings_per_basket'
    ]
    inlines = [BasketItemInline]
    
    fieldsets = (
        ('Overview', {
            'fields': (('basket_id', 'is_active'), 'name', 'slug', 'description', 'image')
        }),
        ('Pricing Strategy', {
            'fields': ('price', 'total_original_price', 'discount_percentage', 'savings_per_basket'),
            'classes': ('bg-gray-50', 'border', 'border-gray-200', 'rounded-md', 'p-4')
        }),
    )

    @display(description="Image")
    def image_preview(self, obj):
        return display_image(obj.image)

    @display(description="Price")
    def price_display(self, obj):
        if obj.price is None: return "-"
        return f"KSh {obj.price:,.2f}"
    
    @display(description="Stock")
    def stock_display(self, obj):
        return obj.stock

    @display(description="Savings", label=True)
    def savings_badge(self, obj):
        try:
            # Check for None to avoid errors if defaults aren't set
            if obj.discount_amount and obj.discount_amount > 0:
                return f"Save KSh {obj.discount_amount:,.0f}"
        except:
            pass
        return "No Discount"


class RecipeIngredientInline(TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ['product']
    tab = True


@admin.register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = [
        'image_preview', 'title', 'difficulty_badge', 'total_time_display', 
        'servings', 'is_featured', 'is_active'
    ]
    list_filter = ['difficulty', 'is_featured', 'is_active']
    search_fields = ['title', 'recipe_id']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_featured', 'is_active']
    inlines = [RecipeIngredientInline]

    @display(description="Image")
    def image_preview(self, obj):
        return display_image(obj.image)

    @display(
        description="Difficulty",
        label={
            "easy": "success", 
            "medium": "warning",
            "hard": "danger",
        }
    )
    def difficulty_badge(self, obj):
        return obj.difficulty

    @display(description="Time")
    def total_time_display(self, obj):
        return f"{obj.total_time} min"


@admin.register(Merchandise)
class MerchandiseAdmin(ModelAdmin):
    list_display = ['image_preview', 'product_id', 'name', 'price_display', 'stock', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'product_id']
    list_editable = ['stock', 'is_active']

    @display(description="Image")
    def image_preview(self, obj):
        return display_image(obj.image)

    @display(description="Price")
    def price_display(self, obj):
        if obj.price is None: return "-"
        return f"KSh {obj.price:,.2f}"


@admin.register(ProductReview)
class ProductReviewAdmin(ModelAdmin):
    list_display = ['product', 'user_info', 'rating_badge', 'created_at', 'is_approved']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['user__email', 'product__name', 'review_text']
    list_editable = ['is_approved']
    readonly_fields = ['created_at']

    @display(description="User")
    def user_info(self, obj):
        if not obj.user: return "Anonymous"
        return obj.user.get_full_name() or obj.user.email

    @display(
        description="Rating",
        label={
            1: "danger",
            2: "warning",
            3: "warning",
            4: "success",
            5: "success",
        }
    )
    def rating_badge(self, obj):
        return f"{obj.rating} ★"