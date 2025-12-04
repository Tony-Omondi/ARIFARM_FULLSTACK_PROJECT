# core/views.py
from django.views.generic import TemplateView
from django.shortcuts import render


# ============================
# MAIN PAGES
# ============================
class HomeView(TemplateView):
    template_name = 'core/home.html'


class AboutView(TemplateView):
    template_name = 'core/about.html'


class ContactView(TemplateView):
    template_name = 'core/contact.html'


class ServicesView(TemplateView):
    template_name = 'core/services.html'


class TeamView(TemplateView):
    template_name = 'core/team.html'


class TeamCarouselView(TemplateView):
    template_name = 'core/team_carousel.html'


class PortfolioView(TemplateView):
    template_name = 'core/portfolio.html'


class PortfolioCarouselView(TemplateView):
    template_name = 'core/portfolio_carousel.html'


class PortfolioDetailsView(TemplateView):
    template_name = 'core/portfolio_details.html'


class TestimonialsView(TemplateView):
    template_name = 'core/testimonials.html'


class TestimonialsCarouselView(TemplateView):
    template_name = 'core/testimonials_carousel.html'


class PricingView(TemplateView):
    template_name = 'core/pricing.html'


class PricingCarouselView(TemplateView):
    template_name = 'core/pricing_carousel.html'


class FAQView(TemplateView):
    template_name = 'core/faq.html'


class Error404View(TemplateView):
    template_name = 'core/404.html'


# ============================
# SHOP PAGES
# ============================
class ShopView(TemplateView):
    template_name = 'shop/shop.html'


class ProductListView(TemplateView):
    template_name = 'shop/product_list.html'


class ProductDetailsView(TemplateView):
    template_name = 'shop/product_details.html'


class CartView(TemplateView):
    template_name = 'shop/cart.html'


class CheckoutView(TemplateView):
    template_name = 'shop/checkout.html'


class WishlistView(TemplateView):
    template_name = 'shop/wishlist.html'


class MyAccountView(TemplateView):
    template_name = 'shop/my_account.html'


# ============================
# NEWS / BLOG PAGES
# ============================
class NewsView(TemplateView):
    template_name = 'news/news.html'


class NewsCarouselView(TemplateView):
    template_name = 'news/news_carousel.html'


class NewsSidebarView(TemplateView):
    template_name = 'news/news_sidebar.html'


class NewsDetailsView(TemplateView):
    template_name = 'news/news_details.html'


# ============================
# SERVICE PAGES
# ============================
class AgricultureServicesView(TemplateView):
    template_name = 'services/agriculture_services.html'


class OrganicServicesView(TemplateView):
    template_name = 'services/organic_services.html'


class DeliveryServicesView(TemplateView):
    template_name = 'services/delivery_services.html'


class FarmingProductsView(TemplateView):
    template_name = 'services/farming_products.html'



def search_view(request):
    query = request.GET.get('q', '').strip()
    # Later you can search products here
    context = {'query': query}
    return render(request, 'core/search_results.html', context)