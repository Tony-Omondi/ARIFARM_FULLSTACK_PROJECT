from django import forms
from django.forms import inlineformset_factory
from products.models import Product, ProductBasket, BasketItem, Category, Recipe, Merchandise
from checkout.models import Order, DeliveryZone
from core.models import GalleryCategory, GalleryItem, PromotionalPopup

# --- MIXIN FOR BOOTSTRAP STYLING ---
class BootstrapMixin:
    """Adds 'form-control' class to all fields automatically"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

# --- PRODUCT FORMS ---
class ProductForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'stock', 'description', 'image', 'is_new', 'is_active']

class BasketForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = ProductBasket
        fields = ['name', 'price', 'description', 'image', 'is_active']

# The "Magic" Formset for Basket Items
BasketItemFormSet = inlineformset_factory(
    ProductBasket, BasketItem,
    fields=['product', 'quantity'],
    extra=1, can_delete=True,
    widgets={
        'product': forms.Select(attrs={'class': 'form-select'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 100px;'}),
    }
)

class CategoryForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']

class MerchandiseForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Merchandise
        fields = ['name', 'price', 'stock', 'description', 'image', 'is_active']

class RecipeForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'instructions', 'prep_time', 'cook_time', 'servings', 'difficulty', 'image', 'is_featured', 'is_active']

# --- CHECKOUT & ORDER FORMS ---
class DeliveryZoneForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = DeliveryZone
        fields = ['name', 'delivery_fee', 'is_active']

class OrderStatusForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {'status': forms.Select(attrs={'class': 'form-select form-select-lg'})}

# --- CORE FORMS ---
class GalleryCategoryForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = GalleryCategory
        fields = ['name', 'order']

class GalleryItemForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = GalleryItem
        fields = ['title', 'category', 'media_type', 'image', 'social_url', 'description', 'is_active', 'order']

class PromotionalPopupForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = PromotionalPopup
        fields = ['title', 'flyer_image', 'link_url', 'delay_seconds', 'is_active', 'show_once_per_session']