from django.views.generic import TemplateView
from django.shortcuts import render
# IMPORT MODELS to fix the missing products issue
from products.models import Product, ProductBasket, Recipe, Category, Merchandise

from django.views.generic import ListView
from .models import GalleryItem, GalleryCategory

# core/views.py (only GalleryView part shown)
from django.views.generic import ListView
from .models import GalleryItem, GalleryCategory

class GalleryView(ListView):
    model = GalleryItem
    template_name = 'core/gallery.html'
    context_object_name = 'gallery_items'
    paginate_by = 12  # Increased for better display

    def get_queryset(self):
        return GalleryItem.objects.filter(is_active=True).select_related('category').order_by('order', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = GalleryCategory.objects.all().order_by('order', 'name')
        return context

# ============================
# MAIN PAGES
# ============================

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Fetch Latest Products (Ordered by creation date so new ones show up)
        context['featured_products'] = Product.objects.filter(
            is_active=True
        ).order_by('-created_at')[:8]

        # 2. Fetch Combo Offers (Baskets)
        context['product_baskets'] = ProductBasket.objects.filter(
            is_active=True
        ).prefetch_related('included_products__product')[:4]

        # 3. Fetch Featured Recipes
        context['featured_recipes'] = Recipe.objects.filter(
            is_active=True, 
            is_featured=True
        ).prefetch_related('ingredients__product')[:4]

        # 4. Fetch Categories
        context['categories'] = Category.objects.filter(is_active=True)[:8]
        
        # 5. Fetch Merchandise
        context['merchandise'] = Merchandise.objects.filter(is_active=True)[:4]
        
        return context

class AboutView(TemplateView):
    template_name = 'core/about.html'

class ContactView(TemplateView):
    template_name = 'core/contact.html'

# ============================
# ADMIN PAGES
# ============================

class AdminDashboardView(TemplateView):
    template_name = 'admin/admin_dashboard.html'

class AdminAddProductView(TemplateView):
    template_name = 'admin/products/add_product.html'

class AdminProductListView(TemplateView):
    template_name = 'admin/products/product_list.html'

class AdminProductDetailView(TemplateView):
    template_name = 'admin/products/product_detail.html'

class AdminCategoryListView(TemplateView):
    template_name = 'admin/categories/category_list.html'

class AdminAddCategoryView(TemplateView):
    template_name = 'admin/categories/add_category.html'

class AdminOrderListView(TemplateView):
    template_name = 'admin/orders/order_list.html'

class AdminOrderDetailView(TemplateView):
    template_name = 'admin/orders/order_detail.html'

class AdminOrderTrackingView(TemplateView):
    template_name = 'admin/orders/order_tracking.html'

class AdminUserListView(TemplateView):
    template_name = 'admin/users/user_list.html'

class AdminLoginView(TemplateView):
    template_name = 'admin/users/login.html'

class AdminGalleryView(TemplateView):
    template_name = 'admin/gallery.html'

class AdminReportView(TemplateView):
    template_name = 'admin/report.html'