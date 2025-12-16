# checkout/urls.py
from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('', views.checkout_view, name='checkout'),
    path('success/<int:order_id>/', views.order_success_view, name='order_success'),
    path('stk-status/', views.stk_status_view, name='stk_status'),
    path('callback/', views.payment_callback, name='payment_callback'),
]