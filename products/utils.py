# products/utils.py
from django.db.models import Q
from .models import Product, ProductBasket, Recipe, Category

def get_featured_items():
    """Get featured items for homepage"""
    return {
        'featured_products': Product.objects.filter(is_active=True, is_new=True)[:8],
        'featured_baskets': ProductBasket.objects.filter(is_active=True)[:4],
        'featured_recipes': Recipe.objects.filter(is_active=True, is_featured=True)[:4],
        'categories': Category.objects.filter(is_active=True)[:8],
    }

def calculate_basket_stock(basket):
    """Calculate available stock for a basket"""
    if not basket.included_products.exists():
        return 0
    
    min_stock = None
    for item in basket.included_products.all():
        product_stock = item.product.stock // item.quantity
        if min_stock is None or product_stock < min_stock:
            min_stock = product_stock
    
    return min_stock or 0

def search_all(query):
    """Search across all product types"""
    results = {
        'products': Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        ),
        'baskets': ProductBasket.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        ),
        'recipes': Recipe.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        ),
        'categories': Category.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        ),
    }
    return results