# core/views.py
from django.views.generic import TemplateView

# Main Pages
class HomeView(TemplateView):
    template_name = 'core/home.html'

class AboutView(TemplateView):
    template_name = 'about.html'

class ContactView(TemplateView):
    template_name = 'contact.html'

# Shop Pages
class ShopView(TemplateView):
    template_name = 'shop/shop.html'

# class CartView(TemplateView):
#     template_name = 'shop/cart.html'

class CheckoutView(TemplateView):
    template_name = 'shop/checkout.html'

# Note: Profile and Login views are handled by the accounts app