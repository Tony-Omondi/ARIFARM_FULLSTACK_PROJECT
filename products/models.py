# products/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
import os
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.utils import timezone

# Create your models here.

def product_image_path(instance, filename):
    """Generate path for product images"""
    ext = filename.split('.')[-1]
    if instance.id:
        filename = f"{slugify(instance.name)}_{instance.id}.{ext}"
    else:
        filename = f"{slugify(instance.name)}_{int(timezone.now().timestamp())}.{ext}"
    return os.path.join('products', filename)

def basket_image_path(instance, filename):
    """Generate path for basket images"""
    ext = filename.split('.')[-1]
    if instance.id:
        filename = f"basket_{slugify(instance.name)}_{instance.id}.{ext}"
    else:
        filename = f"basket_{slugify(instance.name)}_{int(timezone.now().timestamp())}.{ext}"
    return os.path.join('baskets', filename)

def recipe_image_path(instance, filename):
    """Generate path for recipe images"""
    ext = filename.split('.')[-1]
    if instance.id:
        filename = f"recipe_{slugify(instance.title)}_{instance.id}.{ext}"
    else:
        filename = f"recipe_{slugify(instance.title)}_{int(timezone.now().timestamp())}.{ext}"
    return os.path.join('recipes', filename)

def merchandise_image_path(instance, filename):
    """Generate path for merchandise images"""
    ext = filename.split('.')[-1]
    if instance.id:
        filename = f"merch_{slugify(instance.name)}_{instance.id}.{ext}"
    else:
        filename = f"merch_{slugify(instance.name)}_{int(timezone.now().timestamp())}.{ext}"
    return os.path.join('merchandise', filename)

class Category(models.Model):
    """Product categories - Admin can add dynamically"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:category_products', args=[self.slug])
    
    def get_products_count(self):
        """Get count of active products in this category"""
        return self.products.filter(is_active=True).count()

class Product(models.Model):
    """Normal Products"""
    product_id = models.CharField(max_length=50, unique=True, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    stock = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField()
    image = models.ImageField(upload_to=product_image_path)
    is_new = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Track if this product is part of any baskets
    is_in_basket = models.BooleanField(default=False, editable=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_new']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.product_id}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Generate product ID if not exists
        if not self.product_id:
            last_product = Product.objects.order_by('-id').first()
            last_id = last_product.id if last_product else 0
            self.product_id = f"PRD-{str(last_id + 1).zfill(4)}"
        
        super().save(*args, **kwargs)
        
        # Update is_in_basket flag
        is_used_in_baskets = self.basket_items.exists()
        if self.is_in_basket != is_used_in_baskets:
            self.is_in_basket = is_used_in_baskets
            # Save again without triggering save() recursion
            Product.objects.filter(id=self.id).update(is_in_basket=is_used_in_baskets)
    
    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.slug])
    
    @property
    def available_stock(self):
        """Get available stock considering baskets"""
        return self.stock
    
    def reduce_stock(self, quantity):
        """Reduce stock by given quantity"""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save(update_fields=['stock'])
            return True
        return False
    
    @property
    def baskets_included_in(self):
        """Get all baskets that include this product"""
        return ProductBasket.objects.filter(
            included_products__product=self,
            is_active=True
        ).distinct()
    
    @property
    def total_quantity_in_baskets(self):
        """Get total quantity of this product used in all baskets"""
        total = 0
        for basket_item in self.basket_items.all():
            total += basket_item.quantity
        return total

class ProductBasket(models.Model):
    """Product Baskets/Combo Offers - Made from existing products"""
    basket_id = models.CharField(max_length=50, unique=True, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to=basket_image_path)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Products included in this basket (through BasketItem model)
    products = models.ManyToManyField(
        Product, 
        through='BasketItem',
        through_fields=('basket', 'product'),
        related_name='baskets'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product Basket"
        verbose_name_plural = "Product Baskets"
    
    def __str__(self):
        return f"{self.name} - {self.basket_id}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        if not self.basket_id:
            last_basket = ProductBasket.objects.order_by('-id').first()
            last_id = last_basket.id if last_basket else 0
            self.basket_id = f"BSK-{str(last_id + 1).zfill(4)}"
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:basket_detail', args=[self.slug])
    
    @property
    def stock(self):
        """Calculate stock based on included products' availability"""
        if not self.included_products.exists():
            return 0
        
        min_stock = None
        for basket_item in self.included_products.select_related('product').all():
            product = basket_item.product
            
            # Check if product is active and has stock
            if not product.is_active:
                return 0
            
            # Calculate how many baskets can be made with this product
            baskets_possible = product.stock // basket_item.quantity
            
            if min_stock is None or baskets_possible < min_stock:
                min_stock = baskets_possible
        
        return min_stock or 0
    
    @property
    def is_in_stock(self):
        """Check if basket is in stock"""
        return self.stock > 0
    
    @property
    def total_original_price(self):
        """Calculate total price if buying products individually"""
        total = Decimal('0.00')
        for basket_item in self.included_products.select_related('product').all():
            total += basket_item.product.price * basket_item.quantity
        return total
    
    @property
    def discount_amount(self):
        """Calculate discount amount"""
        return self.total_original_price - self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.total_original_price > 0:
            discount = ((self.total_original_price - self.price) / self.total_original_price) * 100
            return round(discount, 1)
        return 0
    
    @property
    def savings_per_basket(self):
        """Calculate savings per basket"""
        return self.discount_amount
    
    def get_products_list(self):
        """Get list of products in this basket with quantities"""
        return [
            {
                'product': item.product,
                'quantity': item.quantity,
                'item_total': item.product.price * item.quantity
            }
            for item in self.included_products.select_related('product').all()
        ]
    
    def can_add_to_cart(self, quantity=1):
        """Check if basket can be added to cart in given quantity"""
        return self.stock >= quantity
    
    def update_product_stock(self, quantity_sold=1):
        """Update stock of all included products when basket is sold"""
        if not self.can_add_to_cart(quantity_sold):
            return False
        
        # Update stock for each product in basket
        for basket_item in self.included_products.select_related('product').all():
            product = basket_item.product
            quantity_needed = basket_item.quantity * quantity_sold
            if product.stock >= quantity_needed:
                product.stock -= quantity_needed
                product.save(update_fields=['stock'])
            else:
                return False
        
        return True

class BasketItem(models.Model):
    """Individual products included in a basket with quantities"""
    basket = models.ForeignKey(
        ProductBasket, 
        on_delete=models.CASCADE, 
        related_name='included_products'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='basket_items'
    )
    quantity = models.PositiveIntegerField(
        default=1, 
        validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['basket', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.basket.name}"
    
    @property
    def item_total_price(self):
        """Total price for this item (product price * quantity)"""
        return self.product.price * self.quantity
    
    @property
    def is_product_available(self):
        """Check if product has enough stock for this basket"""
        return self.product.stock >= self.quantity

class Recipe(models.Model):
    """Recipes - Free content to promote products"""
    recipe_id = models.CharField(max_length=50, unique=True, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(upload_to=recipe_image_path)
    description = models.TextField(blank=True)
    instructions = models.TextField(help_text="Step-by-step cooking instructions")
    prep_time = models.PositiveIntegerField(help_text="Preparation time in minutes", default=15)
    cook_time = models.PositiveIntegerField(help_text="Cooking time in minutes", default=30)
    servings = models.PositiveIntegerField(default=4)
    difficulty = models.CharField(max_length=50, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ], default='medium')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipe_id}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        if not self.recipe_id:
            last_recipe = Recipe.objects.order_by('-id').first()
            last_id = last_recipe.id if last_recipe else 0
            self.recipe_id = f"RCP-{str(last_id + 1).zfill(4)}"
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:recipe_detail', args=[self.slug])
    
    @property
    def total_time(self):
        return self.prep_time + self.cook_time
    
    @property
    def get_ingredient_products(self):
        """Get all products used in this recipe"""
        products = []
        for ingredient in self.ingredients.all():
            if ingredient.product:
                products.append(ingredient.product)
        return products
    
    def get_buy_ingredients_total(self):
        """Calculate total price to buy all ingredient products"""
        total = Decimal('0.00')
        for ingredient in self.ingredients.all():
            if ingredient.product:
                # Assuming 1 quantity of each product for recipe
                total += ingredient.product.price
        return total

class RecipeIngredient(models.Model):
    """Ingredients for recipes - can reference products"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='used_in_recipes'
    )
    name = models.CharField(max_length=200, help_text="Ingredient name if not a product")
    quantity = models.CharField(max_length=100, help_text="e.g., 2 cups, 500g, 3 pieces")
    notes = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Recipe Ingredient"
        verbose_name_plural = "Recipe Ingredients"
    
    def __str__(self):
        product_name = self.product.name if self.product else self.name
        return f"{self.quantity} {product_name} for {self.recipe.title}"
    
    @property
    def display_name(self):
        """Display either product name or custom name"""
        return self.product.name if self.product else self.name
    
    @property
    def ingredient_price(self):
        """Get price if ingredient is a product"""
        return self.product.price if self.product else None

class Merchandise(models.Model):
    """Merchandise items - Separate from regular products"""
    product_id = models.CharField(max_length=50, unique=True, editable=False)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to=merchandise_image_path)
    description = models.TextField()
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Merchandise"
    
    def __str__(self):
        return f"{self.name} - {self.product_id}"
    
    def save(self, *args, **kwargs):
        if not self.product_id:
            last_merch = Merchandise.objects.order_by('-id').first()
            last_id = last_merch.id if last_merch else 0
            self.product_id = f"MRCH-{str(last_id + 1).zfill(4)}"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:merchandise_detail', args=[self.id])
    
    def reduce_stock(self, quantity):
        """Reduce merchandise stock"""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save(update_fields=['stock'])
            return True
        return False