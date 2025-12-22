from django.views.generic import ListView, CreateView, UpdateView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db import transaction
from django.shortcuts import redirect
from . import forms
from products.models import Product, ProductBasket, Category, Merchandise, Recipe
from checkout.models import Order, DeliveryZone
from core.models import GalleryCategory, GalleryItem, PromotionalPopup
from cart.models import Cart

# --- 1. SECURITY MIXIN ---
class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class DashboardHomeView(StaffRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

# --- 2. PRODUCT VIEWS ---
class ProductListView(StaffRequiredMixin, ListView):
    model = Product
    template_name = 'dashboard/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

class ProductCreateView(StaffRequiredMixin, CreateView):
    model = Product
    form_class = forms.ProductForm
    template_name = 'dashboard/generic_form.html'
    success_url = reverse_lazy('dashboard:product_list')
    extra_context = {'title': 'Add Product'}

class ProductUpdateView(StaffRequiredMixin, UpdateView):
    model = Product
    form_class = forms.ProductForm
    template_name = 'dashboard/generic_form.html'
    success_url = reverse_lazy('dashboard:product_list')
    extra_context = {'title': 'Edit Product'}

class ProductDeleteView(StaffRequiredMixin, DeleteView):
    model = Product
    template_name = 'dashboard/delete_confirm.html'
    success_url = reverse_lazy('dashboard:product_list')

# --- 3. BASKET VIEWS ---
class BasketCreateView(StaffRequiredMixin, CreateView):
    model = ProductBasket
    form_class = forms.BasketForm
    template_name = 'dashboard/basket_form.html'
    success_url = reverse_lazy('dashboard:home')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['items'] = forms.BasketItemFormSet(self.request.POST)
        else:
            data['items'] = forms.BasketItemFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']
        with transaction.atomic():
            self.object = form.save()
            if items.is_valid():
                items.instance = self.object
                items.save()
        return super().form_valid(form)

# --- 4. VIEW FACTORY (Handles List, Create, Update, Delete) ---
def create_simple_views(model_class, form_cls, list_template='dashboard/core_list.html', success_url_name='dashboard:home'):
    """
    Creates standard List, Create, Update, and Delete views dynamically.
    Renamed 'form_class' arg to 'form_cls' to fix NameError.
    """
    class List(StaffRequiredMixin, ListView):
        model = model_class
        template_name = list_template
        context_object_name = 'items'
        
    class Create(StaffRequiredMixin, CreateView):
        model = model_class
        form_class = form_cls
        template_name = 'dashboard/generic_form.html'
        success_url = reverse_lazy(success_url_name)
        extra_context = {'title': f'Add {model_class._meta.verbose_name}'}
        
    class Update(StaffRequiredMixin, UpdateView):
        model = model_class
        form_class = form_cls
        template_name = 'dashboard/generic_form.html'
        success_url = reverse_lazy(success_url_name)
        extra_context = {'title': f'Edit {model_class._meta.verbose_name}'}

    class Delete(StaffRequiredMixin, DeleteView):
        model = model_class
        template_name = 'dashboard/delete_confirm.html'
        success_url = reverse_lazy(success_url_name)
        
    return List, Create, Update, Delete

# --- 5. GENERATE VIEWS ---

# Merchandise
MerchList, MerchCreate, MerchUpdate, MerchDelete = create_simple_views(Merchandise, forms.MerchandiseForm, success_url_name='dashboard:merch_list')

# Recipes
RecipeList, RecipeCreate, RecipeUpdate, RecipeDelete = create_simple_views(Recipe, forms.RecipeForm, success_url_name='dashboard:recipe_list')

# Delivery Zones
ZoneList, ZoneCreate, ZoneUpdate, ZoneDelete = create_simple_views(DeliveryZone, forms.DeliveryZoneForm, success_url_name='dashboard:zone_list')

# Gallery Categories
GalCatList, GalCatCreate, GalCatUpdate, GalCatDelete = create_simple_views(GalleryCategory, forms.GalleryCategoryForm, success_url_name='dashboard:gallery_cat_list')

# Gallery Items
GalItemList, GalItemCreate, GalItemUpdate, GalItemDelete = create_simple_views(GalleryItem, forms.GalleryItemForm, success_url_name='dashboard:gallery_item_list')

# Popups
PopupList, PopupCreateView, PopupUpdateView, PopupDeleteView = create_simple_views(PromotionalPopup, forms.PromotionalPopupForm, success_url_name='dashboard:popup_list')


# --- 6. ORDER & CART MANAGEMENT ---
class OrderListView(StaffRequiredMixin, ListView):
    model = Order
    template_name = 'dashboard/order_list.html'
    context_object_name = 'orders'
    ordering = ['-created_at']

class OrderDetailView(StaffRequiredMixin, UpdateView):
    model = Order
    form_class = forms.OrderStatusForm
    template_name = 'dashboard/order_detail.html'
    context_object_name = 'order'
    
    def get_success_url(self):
        return reverse_lazy('dashboard:order_detail', kwargs={'pk': self.object.pk})

class OrderDeleteView(StaffRequiredMixin, DeleteView):
    model = Order
    template_name = 'dashboard/delete_confirm.html'
    success_url = reverse_lazy('dashboard:order_list')

class CartListView(StaffRequiredMixin, ListView):
    model = Cart
    template_name = 'dashboard/cart_list.html'
    context_object_name = 'carts'
    def get_queryset(self):
        # Only show carts that have items
        return Cart.objects.filter(items__isnull=False).distinct()

class CartDeleteView(StaffRequiredMixin, DeleteView):
    model = Cart
    template_name = 'dashboard/delete_confirm.html'
    success_url = reverse_lazy('dashboard:cart_list')