from django.urls import path
from .views import (
    # Main
    HomeView, AboutView, ContactView,
    # Admin Products
    AdminDashboardView, AdminAddProductView, AdminProductListView, 
    AdminProductDetailView, 
    # Admin Categories
    AdminCategoryListView, AdminAddCategoryView, 
    # Admin Orders
    AdminOrderListView, AdminOrderDetailView, AdminOrderTrackingView, 
    # Admin Users & Misc
    AdminUserListView, AdminLoginView, AdminGalleryView, AdminReportView, GalleryView
    
)

urlpatterns = [
    # Main Pages
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),

    # Admin Pages - Dashboard
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # Admin Pages - Products
    path('admin-dashboard/add-product/', AdminAddProductView.as_view(), name='admin_add_product'),
    path('admin-dashboard/products/', AdminProductListView.as_view(), name='admin_product_list'),
    path('admin-dashboard/product-detail/', AdminProductDetailView.as_view(), name='admin_product_detail'),
    
    # Admin Pages - Categories
    path('admin-dashboard/categories/', AdminCategoryListView.as_view(), name='admin_category_list'),
    path('admin-dashboard/categories/add/', AdminAddCategoryView.as_view(), name='admin_add_category'),
    
    # Admin Pages - Orders
    path('admin-dashboard/orders/', AdminOrderListView.as_view(), name='admin_order_list'),
    path('admin-dashboard/orders/detail/', AdminOrderDetailView.as_view(), name='admin_order_detail'),
    path('admin-dashboard/orders/track/', AdminOrderTrackingView.as_view(), name='admin_order_tracking'),
    
    # Admin Pages - Users & Misc
    path('admin-dashboard/users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('admin-dashboard/login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin-dashboard/gallery/', AdminGalleryView.as_view(), name='admin_gallery'),
    path('admin-dashboard/report/', AdminReportView.as_view(), name='admin_report'),
    path('gallery/', GalleryView.as_view(), name='gallery'),
]