# products/views.py - UPDATED TO WORK WITH NEW MODELS
# products/views.py - UPDATED TO WORK WITH NEW MODELS

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Avg
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

# Import models
from .models import (
    Product, ProductBasket, Recipe, Merchandise, 
    Category, BasketItem, ProductReview
)

# Import forms
from .forms import (
    SearchForm, FilterForm, ProductForm, ProductBasketForm, 
    RecipeForm, MerchandiseForm, CategoryForm, RecipeIngredientForm, 
    BasketItemForm, ProductReviewForm
)
from django.db.models import Avg, Count, Q
from django.views.generic import ListView
from django.db.models import Avg, Count, Q, Value
from django.db.models.functions import Coalesce
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from .models import Product, Category


# Create your views here.

class HomeView(TemplateView):
    template_name = 'products/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(
            is_active=True, 
            is_new=True
        )[:8]
        context['product_baskets'] = ProductBasket.objects.filter(
            is_active=True
        ).prefetch_related('included_products__product')[:4]
        context['featured_recipes'] = Recipe.objects.filter(
            is_active=True, 
            is_featured=True
        ).prefetch_related('ingredients__product')[:4]
        context['categories'] = Category.objects.filter(is_active=True)[:8]
        context['merchandise'] = Merchandise.objects.filter(is_active=True)[:4]
        return context

# products/views.py


# products/views.py




class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related('category')

        # This line now works perfectly
        qs = qs.annotate(
            average_rating=Coalesce(Avg('reviews__rating'), Value(0.0)),
            reviews_count=Count('reviews', filter=Q(reviews__is_approved=True))
        )

        # Category filter
        if category_slug := self.kwargs.get('category_slug'):
            category = get_object_or_404(Category, slug=category_slug, is_active=True)
            qs = qs.filter(category=category)
            self.category = category

        # Search
        if q := self.request.GET.get('q'):
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q) |
                Q(category__name__icontains=q)
            )

        # Price filter
        if min_price := self.request.GET.get('min_price'):
            qs = qs.filter(price__gte=min_price)
        if max_price := self.request.GET.get('max_price'):
            qs = qs.filter(price__lte=max_price)

        # Only new products
        if self.request.GET.get('is_new'):
            qs = qs.filter(is_new=True)

        # Sorting
        ordering = self.request.GET.get('ordering', '-created_at')
        allowed = ['name', '-name', 'price', '-price', '-created_at', '-reviews_count']
        if ordering in allowed:
            qs = qs.order_by(ordering)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['total_products'] = Product.objects.filter(is_active=True).count()
        if hasattr(self, 'category'):
            context['category'] = self.category
        return context



class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Related products (same category)
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(id=self.object.id)[:4]

        # Baskets that include this product
        context['baskets_with_product'] = self.object.baskets.filter(is_active=True)[:3]

        # Upsell merchandise
        context['merchandise'] = Merchandise.objects.filter(is_active=True)[:3]

        # === REVIEWS SYSTEM ===
        reviews = self.object.reviews.filter(is_approved=True).select_related('user')
        context['reviews'] = reviews

        # Average rating
        avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        context['average_rating'] = round(avg_rating, 1) if avg_rating else 0
        context['total_reviews'] = reviews.count()

        # Review form for authenticated users
        if self.request.user.is_authenticated:
            has_reviewed = self.object.reviews.filter(user=self.request.user).exists()
            if not has_reviewed:
                context['review_form'] = ProductReviewForm()
            else:
                context['has_reviewed'] = True
        else:
            context['review_form'] = None

        return context

    def post(self, *args, **kwargs):
        self.object = self.get_object()

        if not self.request.user.is_authenticated:
            messages.error(self.request, "You must be logged in to leave a review.")
            return redirect('products:product_detail', slug=self.object.slug)

        # Prevent multiple reviews
        if self.object.reviews.filter(user=self.request.user).exists():
            messages.error(self.request, "You have already reviewed this product.")
            return redirect('products:product_detail', slug=self.object.slug)

        form = ProductReviewForm(self.request.POST, user=self.request.user, product=self.object)
        if form.is_valid():
            form.save()
            messages.success(self.request, "Thank you! Your review has been submitted and will appear shortly.")
            return redirect('products:product_detail', slug=self.object.slug)
        else:
            # If form invalid, re-render page with errors
            context = self.get_context_data()
            context['review_form'] = form
            messages.error(self.request, "Please correct the errors below.")
            return self.render_to_response(context)

class BasketListView(ListView):
    model = ProductBasket
    template_name = 'products/basket_list.html'
    context_object_name = 'baskets'
    paginate_by = 9
    
    def get_queryset(self):
        return ProductBasket.objects.filter(is_active=True).prefetch_related(
            'included_products__product'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Combo Offers'
        return context

class BasketDetailView(DetailView):
    model = ProductBasket
    template_name = 'products/basket_detail.html'
    context_object_name = 'basket'
    
    def get_queryset(self):
        return ProductBasket.objects.filter(is_active=True).prefetch_related(
            'included_products__product'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get products in this basket with quantities
        basket_items = self.object.included_products.select_related('product').all()
        context['basket_items'] = basket_items
        
        # Calculate basket details
        context['original_price'] = self.object.total_original_price
        context['discount_percentage'] = self.object.discount_percentage
        context['savings'] = self.object.savings_per_basket
        
        # Get related baskets
        context['related_baskets'] = ProductBasket.objects.filter(
            is_active=True
        ).exclude(id=self.object.id).prefetch_related('included_products__product')[:3]
        
        return context

class RecipeListView(ListView):
    model = Recipe
    template_name = 'products/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Recipe.objects.filter(is_active=True).prefetch_related('ingredients__product')
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(instructions__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Recipes'
        return context

class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'products/recipe_detail.html'
    context_object_name = 'recipe'
    
    def get_queryset(self):
        return Recipe.objects.filter(is_active=True).prefetch_related('ingredients__product')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get ingredients with products
        ingredients = self.object.ingredients.select_related('product').all()
        context['ingredients'] = ingredients
        
        # Get only ingredients that have associated products
        ingredient_products = []
        for ingredient in ingredients:
            if ingredient.product:
                ingredient_products.append({
                    'product': ingredient.product,
                    'quantity': ingredient.quantity
                })
        
        context['ingredient_products'] = ingredient_products
        context['related_recipes'] = Recipe.objects.filter(
            is_active=True
        ).exclude(id=self.object.id).prefetch_related('ingredients__product')[:3]
        
        # Calculate total cost to buy all ingredient products
        total_cost = sum(item['product'].price for item in ingredient_products)
        context['ingredients_total_cost'] = total_cost
        
        return context

class MerchandiseListView(ListView):
    model = Merchandise
    template_name = 'products/merchandise_list.html'
    context_object_name = 'merchandise_items'
    paginate_by = 12
    
    def get_queryset(self):
        return Merchandise.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Merchandise'
        return context

class MerchandiseDetailView(DetailView):
    model = Merchandise
    template_name = 'products/merchandise_detail.html'
    context_object_name = 'merchandise'
    
    def get_queryset(self):
        return Merchandise.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related merchandise
        context['related_merchandise'] = Merchandise.objects.filter(
            is_active=True
        ).exclude(id=self.object.id)[:3]
        return context

class CategoryListView(ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get product count for each category
        categories_with_count = []
        for category in context['categories']:
            product_count = Product.objects.filter(
                category=category, 
                is_active=True
            ).count()
            categories_with_count.append({
                'category': category,
                'product_count': product_count
            })
        context['categories_with_count'] = categories_with_count
        return context

def search_view(request):
    query = request.GET.get('q', '')
    results = {
        'products': [],
        'recipes': [],
        'baskets': [],
        'categories': []
    }
    
    if query:
        results['products'] = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        )[:5]
        
        results['recipes'] = Recipe.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        ).prefetch_related('ingredients__product')[:5]
        
        results['baskets'] = ProductBasket.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        ).prefetch_related('included_products__product')[:5]
        
        results['categories'] = Category.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        )[:5]
    
    return render(request, 'products/search_results.html', {
        'query': query,
        'results': results
    })

# New view to see all baskets containing a specific product
def product_baskets_view(request, product_slug):
    """View all baskets that contain a specific product"""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    baskets = product.baskets.filter(is_active=True).prefetch_related(
        'included_products__product'
    )
    
    return render(request, 'products/product_baskets.html', {
        'product': product,
        'baskets': baskets,
        'title': f'Baskets containing {product.name}'
    })

# New view to see all recipes using a specific product
def product_recipes_view(request, product_slug):
    """View all recipes that use a specific product as ingredient"""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    recipes = Recipe.objects.filter(
        ingredients__product=product,
        is_active=True
    ).prefetch_related('ingredients__product').distinct()
    
    return render(request, 'products/product_recipes.html', {
        'product': product,
        'recipes': recipes,
        'title': f'Recipes using {product.name}'
    })





# Helper function to check if user is admin
def is_admin(user):
    return user.is_staff

# Admin Dashboard
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with quick stats"""
    stats = {
        'total_products': Product.objects.count(),
        'active_products': Product.objects.filter(is_active=True).count(),
        'total_baskets': ProductBasket.objects.count(),
        'active_baskets': ProductBasket.objects.filter(is_active=True).count(),
        'total_recipes': Recipe.objects.count(),
        'total_categories': Category.objects.count(),
        'total_merchandise': Merchandise.objects.count(),
        'low_stock_products': Product.objects.filter(stock__lt=10, stock__gt=0).count(),
        'out_of_stock': Product.objects.filter(stock=0).count(),
    }
    
    return render(request, 'products/admin_dashboard.html', {
        'stats': stats,
        'title': 'Admin Dashboard'
    })

# Product Admin Views
@login_required
@user_passes_test(is_admin)
def admin_product_create(request):
    """Create new product (admin)"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('products:admin_product_edit', product_id=product.id)
    else:
        form = ProductForm()
    
    return render(request, 'products/admin_form.html', {
        'form': form,
        'title': 'Add New Product',
        'categories': Category.objects.filter(is_active=True),
    })

@login_required
@user_passes_test(is_admin)
def admin_product_edit(request, product_id):
    """Edit existing product (admin)"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('products:admin_product_edit', product_id=product.id)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/admin_form.html', {
        'form': form,
        'product': product,
        'title': f'Edit Product: {product.name}',
        'categories': Category.objects.filter(is_active=True),
    })

@login_required
@user_passes_test(is_admin)
def admin_product_delete(request, product_id):
    """Delete product (admin)"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('products:admin_dashboard')
    
    return render(request, 'products/admin_confirm_delete.html', {
        'object': product,
        'title': f'Delete Product: {product.name}',
    })

# Basket Admin Views
@login_required
@user_passes_test(is_admin)
def admin_basket_create(request):
    """Create new basket (admin)"""
    if request.method == 'POST':
        form = ProductBasketForm(request.POST, request.FILES)
        if form.is_valid():
            basket = form.save()
            
            # Handle basket items
            products = request.POST.getlist('products[]')
            quantities = request.POST.getlist('quantities[]')
            
            for product_id, quantity in zip(products, quantities):
                if product_id and quantity:
                    product = Product.objects.get(id=product_id)
                    BasketItem.objects.create(
                        basket=basket,
                        product=product,
                        quantity=quantity
                    )
            
            messages.success(request, f'Basket "{basket.name}" created successfully!')
            return redirect('products:admin_basket_edit', basket_id=basket.id)
    else:
        form = ProductBasketForm()
    
    return render(request, 'products/admin_basket_form.html', {
        'form': form,
        'title': 'Create New Basket',
        'all_products': Product.objects.filter(is_active=True),
    })

@login_required
@user_passes_test(is_admin)
def admin_basket_edit(request, basket_id):
    """Edit existing basket (admin)"""
    basket = get_object_or_404(ProductBasket, id=basket_id)
    basket_items = basket.included_products.all()
    
    if request.method == 'POST':
        form = ProductBasketForm(request.POST, request.FILES, instance=basket)
        if form.is_valid():
            basket = form.save()
            
            # Clear existing items
            basket.included_products.all().delete()
            
            # Add new items
            products = request.POST.getlist('products[]')
            quantities = request.POST.getlist('quantities[]')
            
            for product_id, quantity in zip(products, quantities):
                if product_id and quantity:
                    product = Product.objects.get(id=product_id)
                    BasketItem.objects.create(
                        basket=basket,
                        product=product,
                        quantity=quantity
                    )
            
            messages.success(request, f'Basket "{basket.name}" updated successfully!')
            return redirect('products:admin_basket_edit', basket_id=basket.id)
    else:
        form = ProductBasketForm(instance=basket)
    
    return render(request, 'products/admin_basket_form.html', {
        'form': form,
        'basket': basket,
        'basket_items': basket_items,
        'title': f'Edit Basket: {basket.name}',
        'all_products': Product.objects.filter(is_active=True),
    })

# Recipe Admin Views
@login_required
@user_passes_test(is_admin)
def admin_recipe_create(request):
    """Create new recipe (admin)"""
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save()
            
            # Handle ingredients
            ingredient_products = request.POST.getlist('ingredient_products[]')
            ingredient_names = request.POST.getlist('ingredient_names[]')
            ingredient_quantities = request.POST.getlist('ingredient_quantities[]')
            ingredient_notes = request.POST.getlist('ingredient_notes[]')
            
            for i in range(len(ingredient_names)):
                if ingredient_names[i] or ingredient_products[i]:
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        product_id=ingredient_products[i] if ingredient_products[i] else None,
                        name=ingredient_names[i],
                        quantity=ingredient_quantities[i],
                        notes=ingredient_notes[i],
                        order=i
                    )
            
            messages.success(request, f'Recipe "{recipe.title}" created successfully!')
            return redirect('products:admin_recipe_edit', recipe_id=recipe.id)
    else:
        form = RecipeForm()
    
    return render(request, 'products/admin_recipe_form.html', {
        'form': form,
        'title': 'Create New Recipe',
        'products': Product.objects.filter(is_active=True),
    })

@login_required
@user_passes_test(is_admin)
def admin_recipe_edit(request, recipe_id):
    """Edit existing recipe (admin)"""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    ingredients = recipe.ingredients.all()
    
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            recipe = form.save()
            
            # Clear existing ingredients
            recipe.ingredients.all().delete()
            
            # Add new ingredients
            ingredient_products = request.POST.getlist('ingredient_products[]')
            ingredient_names = request.POST.getlist('ingredient_names[]')
            ingredient_quantities = request.POST.getlist('ingredient_quantities[]')
            ingredient_notes = request.POST.getlist('ingredient_notes[]')
            
            for i in range(len(ingredient_names)):
                if ingredient_names[i] or ingredient_products[i]:
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        product_id=ingredient_products[i] if ingredient_products[i] else None,
                        name=ingredient_names[i],
                        quantity=ingredient_quantities[i],
                        notes=ingredient_notes[i],
                        order=i
                    )
            
            messages.success(request, f'Recipe "{recipe.title}" updated successfully!')
            return redirect('products:admin_recipe_edit', recipe_id=recipe.id)
    else:
        form = RecipeForm(instance=recipe)
    
    return render(request, 'products/admin_recipe_form.html', {
        'form': form,
        'recipe': recipe,
        'ingredients': ingredients,
        'title': f'Edit Recipe: {recipe.title}',
        'products': Product.objects.filter(is_active=True),
    })

# Category Admin Views
@login_required
@user_passes_test(is_admin)
def admin_category_create(request):
    """Create new category (admin)"""
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('products:admin_dashboard')
    else:
        form = CategoryForm()
    
    return render(request, 'products/admin_category_form.html', {
        'form': form,
        'title': 'Create New Category',
    })

# Merchandise Admin Views
@login_required
@user_passes_test(is_admin)
def admin_merchandise_create(request):
    """Create new merchandise (admin)"""
    if request.method == 'POST':
        form = MerchandiseForm(request.POST, request.FILES)
        if form.is_valid():
            merchandise = form.save()
            messages.success(request, f'Merchandise "{merchandise.name}" created successfully!')
            return redirect('products:merchandise_detail', pk=merchandise.id)
    else:
        form = MerchandiseForm()
    
    return render(request, 'products/admin_merchandise_form.html', {
        'form': form,
        'title': 'Add New Merchandise',
    })

@login_required
@user_passes_test(is_admin)
def admin_merchandise_edit(request, merchandise_id):
    """Edit merchandise (admin)"""
    merchandise = get_object_or_404(Merchandise, id=merchandise_id)
    
    if request.method == 'POST':
        form = MerchandiseForm(request.POST, request.FILES, instance=merchandise)
        if form.is_valid():
            merchandise = form.save()
            messages.success(request, f'Merchandise "{merchandise.name}" updated successfully!')
            return redirect('products:merchandise_detail', pk=merchandise.id)
    else:
        form = MerchandiseForm(instance=merchandise)
    
    return render(request, 'products/admin_merchandise_form.html', {
        'form': form,
        'merchandise': merchandise,
        'title': f'Edit Merchandise: {merchandise.name}',
    })

# Bulk Operations
@login_required
@user_passes_test(is_admin)
def admin_bulk_operations(request):
    """Bulk operations page"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_prices':
            # Handle price updates
            pass
        elif action == 'update_stock':
            # Handle stock updates
            pass
        elif action == 'export_data':
            # Handle data export
            pass
    
    return render(request, 'products/admin_bulk_operations.html', {
        'title': 'Bulk Operations',
    })