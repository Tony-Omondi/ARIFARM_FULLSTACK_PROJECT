# core/urls.py
from django.urls import path
from .views import (
    HomeView,
    AboutView,
    ContactView,
    ShopView,
    
    CheckoutView
)

urlpatterns = [
    # Main Pages
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    
    # Shop Pages
    path('shop/', ShopView.as_view(), name='shop'),
    # path('cart/', CartView.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
]