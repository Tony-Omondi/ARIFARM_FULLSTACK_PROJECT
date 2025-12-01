from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.view_cart, name='view_cart'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('update/<uuid:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove/<uuid:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout URLs
    path('checkout/delivery/', views.checkout_delivery, name='checkout_delivery'),
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('checkout/place-order/', views.place_order, name='place_order'),
    path('checkout/confirmation/', views.order_confirmation, name='order_confirmation'),
    
    # Utility
    path('merge/', views.merge_carts, name='merge_carts'),
    path('update-delivery/', views.update_delivery_info, name='update_delivery_info'),
]