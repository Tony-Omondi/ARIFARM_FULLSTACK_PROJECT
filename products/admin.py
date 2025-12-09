# products/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Category, Product, ProductBasket, BasketItem, 
    Recipe, RecipeIngredient, Merchandise, ProductReview
)

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'get_products_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'product_id', 'name', 'category', 'price', 'stock', 
        'is_new', 'is_in_basket', 'is_active', 'created_at'
    ]
    list_filter = ['category', 'is_new', 'is_in_basket', 'is_active', 'created_at']
    search_fields = ['name', 'product_id', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_new', 'is_active']
    readonly_fields = ['product_id', 'is_in_basket', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_id', 'name', 'slug', 'description')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock')
        }),
        ('Media & Display', {
            'fields': ('image', 'is_new', 'is_active')
        }),
        ('Categorization', {
            'fields': ('category',)
        }),
        ('Additional Info', {
            'fields': ('is_in_basket',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('baskets')

class BasketItemInline(admin.TabularInline):
    model = BasketItem
    extra = 1
    raw_id_fields = ['product']
    autocomplete_fields = ['product']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(ProductBasket)
class ProductBasketAdmin(admin.ModelAdmin):
    list_display = [
        'basket_id', 'name', 'price', 'stock', 'discount_display', 
        'savings_display', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'basket_id', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'is_active']
    readonly_fields = [
        'basket_id', 'created_at', 'updated_at', 'stock', 
        'total_original_price', 'discount_percentage', 'discount_amount',
        'savings_per_basket'
    ]
    inlines = [BasketItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('basket_id', 'name', 'slug', 'description')
        }),
        ('Pricing', {
            'fields': ('price',)
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Calculated Fields', {
            'fields': ('stock', 'total_original_price', 'discount_percentage', 
                      'discount_amount', 'savings_per_basket'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def discount_display(self, obj):
        if obj.discount_percentage > 0:
            return f"{obj.discount_percentage}% OFF"
        return "-"
    discount_display.short_description = 'Discount'
    
    def savings_display(self, obj):
        return f"₵{obj.savings_per_basket:.2f}"
    savings_display.short_description = 'Savings'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('included_products')

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    raw_id_fields = ['product']
    autocomplete_fields = ['product']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'recipe_id', 'title', 'difficulty', 'total_time_display', 
        'servings', 'is_featured', 'is_active', 'created_at'
    ]
    list_filter = ['difficulty', 'is_featured', 'is_active', 'created_at']
    search_fields = ['title', 'recipe_id', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_featured', 'is_active']
    readonly_fields = ['recipe_id', 'created_at', 'updated_at']
    inlines = [RecipeIngredientInline]
    
    def total_time_display(self, obj):
        return f"{obj.total_time} min"
    total_time_display.short_description = 'Total Time'

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'display_name', 'quantity', 'order']
    list_filter = ['recipe']
    search_fields = ['name', 'recipe__title', 'product__name']
    autocomplete_fields = ['product']

@admin.register(Merchandise)
class MerchandiseAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name', 'price', 'stock', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'product_id', 'description']
    list_editable = ['price', 'stock', 'is_active']
    readonly_fields = ['product_id', 'created_at', 'updated_at']



# products/admin.py



@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'get_reviewer_name', 'rating', 'rating_stars', 'created_at', 'is_approved']
    list_filter = ['rating', 'is_approved', 'created_at', 'product__category']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'review_text', 'product__name']
    readonly_fields = ['created_at']  # only keep created_at read-only
    list_editable = ['is_approved']
