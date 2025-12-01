# products/urls.py - ADD THESE URL PATTERNS

from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Public URLs (keep your existing ones)
    path('', views.HomeView.as_view(), name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/category/<slug:category_slug>/', views.ProductListView.as_view(), name='category_products'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('baskets/', views.BasketListView.as_view(), name='basket_list'),
    path('baskets/<slug:slug>/', views.BasketDetailView.as_view(), name='basket_detail'),
    path('recipes/', views.RecipeListView.as_view(), name='recipe_list'),
    path('recipes/<slug:slug>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    path('merchandise/', views.MerchandiseListView.as_view(), name='merchandise_list'),
    path('merchandise/<int:pk>/', views.MerchandiseDetailView.as_view(), name='merchandise_detail'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('search/', views.search_view, name='search'),
    
    # Admin URLs (ADD THESE)
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Product Admin
    path('admin/products/create/', views.admin_product_create, name='admin_product_create'),
    path('admin/products/<int:product_id>/edit/', views.admin_product_edit, name='admin_product_edit'),
    path('admin/products/<int:product_id>/delete/', views.admin_product_delete, name='admin_product_delete'),
    
    # Basket Admin
    path('admin/baskets/create/', views.admin_basket_create, name='admin_basket_create'),
    path('admin/baskets/<int:basket_id>/edit/', views.admin_basket_edit, name='admin_basket_edit'),
    
    # Recipe Admin
    path('admin/recipes/create/', views.admin_recipe_create, name='admin_recipe_create'),
    path('admin/recipes/<int:recipe_id>/edit/', views.admin_recipe_edit, name='admin_recipe_edit'),
    
    # Category Admin
    path('admin/categories/create/', views.admin_category_create, name='admin_category_create'),
    
    # Merchandise Admin
    path('admin/merchandise/create/', views.admin_merchandise_create, name='admin_merchandise_create'),
    path('admin/merchandise/<int:merchandise_id>/edit/', views.admin_merchandise_edit, name='admin_merchandise_edit'),
    
    # Bulk Operations
    path('admin/bulk/', views.admin_bulk_operations, name='admin_bulk_operations'),
]