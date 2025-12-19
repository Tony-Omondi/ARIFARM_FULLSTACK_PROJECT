# core/urls.py
from django.urls import path
from .views import (
    # Main
    HomeView, AboutView, ContactView,
    # Admin
    AdminDashboardView, AdminAddProductView , AdminProductListView,AdminProductDetailView,AdminCategoryListView,
    AdminAddCategoryView, AdminOrderListView, AdminOrderDetailView, AdminOrderTrackingView, AdminUserListView,AdminLoginView, AdminGalleryView,AdminReportView
)

urlpatterns = [
    # Main Pages
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),

    # Admin Pages
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-dashboard/add-product/', AdminAddProductView.as_view(), name='admin_add_product'),
    path('admin-dashboard/products/', AdminProductListView.as_view(), name='admin_product_list'),
    path('admin-dashboard/product-detail/', AdminProductDetailView.as_view(), name='admin_product_detail'),
    path('admin-dashboard/categories/', AdminCategoryListView.as_view(), name='admin_category_list'),
    path('admin-dashboard/categories/add/', AdminAddCategoryView.as_view(), name='admin_add_category'),
    path('admin-dashboard/orders/', AdminOrderListView.as_view(), name='admin_order_list'),
    path('admin-dashboard/orders/detail/', AdminOrderDetailView.as_view(), name='admin_order_detail'),
    path('admin-dashboard/orders/track/', AdminOrderTrackingView.as_view(), name='admin_order_tracking'),
    path('admin-dashboard/users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('admin-dashboard/login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin-dashboard/gallery/', AdminGalleryView.as_view(), name='admin_gallery'),
    path('admin-dashboard/report/', AdminReportView.as_view(), name='admin_report'),
    
]


    # Services
    # path('services/', ServicesView.as_view(), name='services'),
    # path('services-carousel/', ServicesView.as_view(), name='services_carousel'),  # same template for now
    # path('agriculture-services/', AgricultureServicesView.as_view(), name='agriculture'),
    # path('organic-services/', OrganicServicesView.as_view(), name='organic'),
    # path('delivery-services/', DeliveryServicesView.as_view(), name='delivery'),
    # path('farming-products/', FarmingProductsView.as_view(), name='farming'),

    # # Pages
    # path('team/', TeamView.as_view(), name='team'),
    # path('team-carousel/', TeamCarouselView.as_view(), name='team_carousel'),
    # path('portfolio/', PortfolioView.as_view(), name='portfolio'),
    # path('portfolio-carousel/', PortfolioCarouselView.as_view(), name='portfolio_carousel'),
    # path('portfolio-details/', PortfolioDetailsView.as_view(), name='portfolio_details'),
    # path('testimonials/', TestimonialsView.as_view(), name='testimonials'),
    # path('testimonials-carousel/', TestimonialsCarouselView.as_view(), name='testimonials_carousel'),
    # path('pricing/', PricingView.as_view(), name='pricing'),
    # path('pricing-carousel/', PricingCarouselView.as_view(), name='pricing_carousel'),
    # path('faq/', FAQView.as_view(), name='faq'),
    # path('404/', Error404View.as_view(), name='error_404'),

    # # Shop

    # path('products/', ShopView.as_view(), name='products'),  # same as shop for now
    # path('product-list/', ProductListView.as_view(), name='product_list'),
    # path('product-details/', ProductDetailsView.as_view(), name='product_details'),
    # path('cart/', CartView.as_view(), name='cart'),
    # path('checkout/', CheckoutView.as_view(), name='checkout'),
    # path('wishlist/', WishlistView.as_view(), name='wishlist'),
    # path('my-account/', MyAccountView.as_view(), name='account'),

    # # News / Blog
    # path('news/', NewsView.as_view(), name='news'),
    # path('news-carousel/', NewsCarouselView.as_view(), name='news_carousel'),
    # path('news-sidebar/', NewsSidebarView.as_view(), name='news_sidebar'),
    # path('news-details/', NewsDetailsView.as_view(), name='news_details'),
    # path('search/', search_view, name='search'),
