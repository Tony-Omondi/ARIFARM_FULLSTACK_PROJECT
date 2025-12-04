# core/urls.py
from django.urls import path
from .views import (
    # Main
    HomeView, AboutView, ContactView, ServicesView, TeamView, TeamCarouselView,
    PortfolioView, PortfolioCarouselView, PortfolioDetailsView,
    TestimonialsView, TestimonialsCarouselView, PricingView, PricingCarouselView,
    FAQView, Error404View,

    # Shop
    ShopView, ProductListView, ProductDetailsView, CartView, CheckoutView,
    WishlistView, MyAccountView,

    # News
    NewsView, NewsCarouselView, NewsSidebarView, NewsDetailsView,

    # Services
    AgricultureServicesView, OrganicServicesView, DeliveryServicesView, FarmingProductsView, search_view
)

urlpatterns = [
    # Main Pages
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),

    # Services
    path('services/', ServicesView.as_view(), name='services'),
    path('services-carousel/', ServicesView.as_view(), name='services_carousel'),  # same template for now
    path('agriculture-services/', AgricultureServicesView.as_view(), name='agriculture'),
    path('organic-services/', OrganicServicesView.as_view(), name='organic'),
    path('delivery-services/', DeliveryServicesView.as_view(), name='delivery'),
    path('farming-products/', FarmingProductsView.as_view(), name='farming'),

    # Pages
    path('team/', TeamView.as_view(), name='team'),
    path('team-carousel/', TeamCarouselView.as_view(), name='team_carousel'),
    path('portfolio/', PortfolioView.as_view(), name='portfolio'),
    path('portfolio-carousel/', PortfolioCarouselView.as_view(), name='portfolio_carousel'),
    path('portfolio-details/', PortfolioDetailsView.as_view(), name='portfolio_details'),
    path('testimonials/', TestimonialsView.as_view(), name='testimonials'),
    path('testimonials-carousel/', TestimonialsCarouselView.as_view(), name='testimonials_carousel'),
    path('pricing/', PricingView.as_view(), name='pricing'),
    path('pricing-carousel/', PricingCarouselView.as_view(), name='pricing_carousel'),
    path('faq/', FAQView.as_view(), name='faq'),
    path('404/', Error404View.as_view(), name='error_404'),

    # Shop
    path('shop/', ShopView.as_view(), name='shop'),
    path('products/', ShopView.as_view(), name='products'),  # same as shop for now
    path('product-list/', ProductListView.as_view(), name='product_list'),
    path('product-details/', ProductDetailsView.as_view(), name='product_details'),
    path('cart/', CartView.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('my-account/', MyAccountView.as_view(), name='account'),

    # News / Blog
    path('news/', NewsView.as_view(), name='news'),
    path('news-carousel/', NewsCarouselView.as_view(), name='news_carousel'),
    path('news-sidebar/', NewsSidebarView.as_view(), name='news_sidebar'),
    path('news-details/', NewsDetailsView.as_view(), name='news_details'),
    path('search/', search_view, name='search'),
]