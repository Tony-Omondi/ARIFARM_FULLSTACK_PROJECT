# products/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Product, ProductBasket, Recipe, Merchandise, 
    BasketItem, RecipeIngredient, Category, ProductReview
)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image', 
                  'category', 'is_new', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ProductBasketForm(forms.ModelForm):
    class Meta:
        model = ProductBasket
        fields = ['name', 'description', 'price', 'image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise ValidationError("Price must be greater than zero.")
        return price

class BasketItemForm(forms.ModelForm):
    class Meta:
        model = BasketItem
        fields = ['product', 'quantity']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active products
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity < 1:
            raise ValidationError("Quantity must be at least 1.")
        return quantity

class AddToBasketForm(forms.Form):
    """Form for adding products to a basket in admin"""
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.filter(is_active=True),
        widget=forms.SelectMultiple(),
        help_text="Select products to include in the basket"
    )
    quantities = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter quantities separated by commas (e.g., 2,1,3)'
        }),
        help_text="Enter quantities for each selected product in order"
    )

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'image', 'description', 'instructions', 
                  'prep_time', 'cook_time', 'servings', 'difficulty', 
                  'is_featured', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'instructions': forms.Textarea(attrs={'rows': 10}),
        }

class BuyIngredientsForm(forms.Form):
    """Form for buying all ingredients from a recipe"""
    recipe = forms.ModelChoiceField(queryset=Recipe.objects.filter(is_active=True))
    
    def buy_ingredients(self):
        recipe = self.cleaned_data['recipe']
        # Logic to add all ingredient products to cart
        # This would integrate with your cart system
        pass

# ADDED: SearchForm that was missing
class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={
            'placeholder': 'Search products, recipes...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories"
    )

# ADDED: FilterForm that was missing
class FilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories"
    )
    min_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    is_new = forms.BooleanField(required=False)

# ADDED: Category Form
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

# ADDED: Recipe Ingredient Form
class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['product', 'name', 'quantity', 'notes', 'order']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active products
        self.fields['product'].queryset = Product.objects.filter(is_active=True)

# ADDED: Merchandise Form
class MerchandiseForm(forms.ModelForm):
    class Meta:
        model = Merchandise
        fields = ['name', 'description', 'price', 'image', 'stock', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise ValidationError("Price must be greater than zero.")
        return price

# ADDED: Quick Add Form (for admin dashboard)
class QuickAddProductForm(forms.Form):
    name = forms.CharField(max_length=200)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    stock = forms.IntegerField(min_value=0)
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False
    )

# ADDED: Bulk Upload Form (for CSV upload)
class BulkUploadForm(forms.Form):
    file = forms.FileField(label='CSV File')
    product_type = forms.ChoiceField(
        choices=[
            ('products', 'Products'),
            ('categories', 'Categories'),
            ('merchandise', 'Merchandise'),
        ]
    )

# ADDED: Price Update Form
class PriceUpdateForm(forms.Form):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.filter(is_active=True)
    )
    percentage = forms.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Percentage to increase/decrease (e.g., 10 for 10% increase, -10 for 10% decrease)"
    )

# ADDED: Stock Update Form
class StockUpdateForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    quantity = forms.IntegerField(help_text="Positive to add, negative to remove")
    reason = forms.ChoiceField(
        choices=[
            ('restock', 'Restock'),
            ('damaged', 'Damaged Goods'),
            ('return', 'Customer Return'),
            ('other', 'Other'),
        ]
    )
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))

# ADDED: Export Form
class ExportForm(forms.Form):
    format = forms.ChoiceField(
        choices=[
            ('csv', 'CSV'),
            ('json', 'JSON'),
            ('excel', 'Excel'),
        ]
    )
    model = forms.ChoiceField(
        choices=[
            ('products', 'Products'),
            ('categories', 'Categories'),
            ('baskets', 'Baskets'),
            ('recipes', 'Recipes'),
            ('merchandise', 'Merchandise'),
        ]
    )
    include_inactive = forms.BooleanField(required=False, initial=False)


# products/forms.py

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.RadioSelect(choices=ProductReview.RATING_CHOICES),
            'review_text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Share your experience with this product...'
            }),
        }
        labels = {
            'rating': 'Your Rating',
            'review_text': 'Your Review (optional)',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        review = super().save(commit=False)
        review.user = self.user
        review.product = self.product
        if commit:
            review.save()
        return review