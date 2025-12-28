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


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['product', 'custom_name', 'quantity', 'notes', 'order']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'custom_name': forms.TextInput(attrs={
                'placeholder': 'Use this for non-shop ingredients (e.g. Salt, Water, 2 cloves garlic...)',
                'class': 'form-control'
            }),
            'quantity': forms.TextInput(attrs={
                'placeholder': 'e.g. 2 cups, 500g, to taste',
                'class': 'form-control'
            }),
            'notes': forms.TextInput(attrs={
                'placeholder': 'Optional notes (e.g. freshly ground)',
                'class': 'form-control'
            }),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        self.fields['custom_name'].required = False  # Optional when product is selected

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        custom_name = cleaned_data.get('custom_name')

        # Validation: require either product OR custom_name
        if not product and not custom_name.strip():
            raise ValidationError(
                "You must either select a product from the shop OR enter a custom ingredient name."
            )

        return cleaned_data


class BuyIngredientsForm(forms.Form):
    recipe = forms.ModelChoiceField(queryset=Recipe.objects.filter(is_active=True))

    def buy_ingredients(self):
        # Placeholder: integrate with cart system
        recipe = self.cleaned_data['recipe']
        pass


class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search products, recipes, baskets...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories"
    )


class FilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories"
    )
    min_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    is_new = forms.BooleanField(required=False)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


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


class QuickAddProductForm(forms.Form):
    name = forms.CharField(max_length=200)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    stock = forms.IntegerField(min_value=0)
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False
    )


class BulkUploadForm(forms.Form):
    file = forms.FileField(label='CSV File')
    product_type = forms.ChoiceField(
        choices=[
            ('products', 'Products'),
            ('categories', 'Categories'),
            ('merchandise', 'Merchandise'),
        ]
    )


class PriceUpdateForm(forms.Form):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.filter(is_active=True)
    )
    percentage = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Percentage to increase/decrease (e.g., 10 for +10%, -10 for -10%)"
    )


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