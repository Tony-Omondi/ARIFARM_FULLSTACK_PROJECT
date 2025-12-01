from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid

class Cart(models.Model):
    CART_STATUS = (
        ('active', 'Active'),
        ('abandoned', 'Abandoned'),
        ('converted', 'Converted to Order'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='carts'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    status = models.CharField(max_length=20, choices=CART_STATUS, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Delivery info (pre-filled from user profile or entered at checkout)
    delivery_name = models.CharField(max_length=255, null=True, blank=True)
    delivery_phone = models.CharField(max_length=20, null=True, blank=True)
    delivery_county = models.CharField(max_length=100, null=True, blank=True)
    delivery_zone = models.CharField(max_length=100, null=True, blank=True)
    delivery_address = models.TextField(null=True, blank=True)
    
    # Payment info
    payment_method = models.CharField(
        max_length=20, 
        choices=[('mpesa', 'M-Pesa'), ('paystack', 'Paystack'), ('cod', 'Cash on Delivery')],
        null=True,
        blank=True
    )
    
    # Checkout calculated fields
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Checkout flags
    is_checkout_started = models.BooleanField(default=False)
    checkout_started_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Guest Cart - {self.id}"
    
    def calculate_totals(self):
        """Calculate cart totals"""
        items = self.items.all()
        subtotal = sum(item.total_price for item in items)
        
        # Apply any discounts here (you can add discount logic later)
        discount = self.discount
        
        # Calculate delivery fee based on county
        delivery_fee = self.calculate_delivery_fee()
        
        total = subtotal + delivery_fee - discount
        
        self.subtotal = subtotal
        self.delivery_fee = delivery_fee
        self.discount = discount
        self.total = total
        self.save()
        return total
    
    def calculate_delivery_fee(self):
        """Calculate delivery fee based on county"""
        # Default delivery fee - you can expand this with a County model
        county_fees = {
            'Nairobi': 200,
            'Kiambu': 250,
            'Mombasa': 500,
            'Kisumu': 450,
            # Add more counties
        }
        
        if self.delivery_county and self.delivery_county in county_fees:
            return county_fees[self.delivery_county]
        
        return 300  # Default fee
    
    def get_item_count(self):
        return self.items.count()
    
    def is_empty(self):
        return self.items.count() == 0


class CartItem(models.Model):
    ITEM_TYPES = (
        ('product', 'Normal Product'),
        ('basket', 'Product Basket'),
        ('merchandise', 'Merchandise'),
    )
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, null=True, blank=True)
    basket = models.ForeignKey('products.ProductBasket', on_delete=models.CASCADE, null=True, blank=True)
    merchandise = models.ForeignKey('products.Merchandise', on_delete=models.CASCADE, null=True, blank=True)
    
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of adding
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-added_at']
        unique_together = [('cart', 'item_type', 'product'), 
                          ('cart', 'item_type', 'basket'),
                          ('cart', 'item_type', 'merchandise')]
    
    def __str__(self):
        if self.item_type == 'product' and self.product:
            return f"{self.quantity} x {self.product.name}"
        elif self.item_type == 'basket' and self.basket:
            return f"{self.quantity} x {self.basket.name}"
        elif self.item_type == 'merchandise' and self.merchandise:
            return f"{self.quantity} x {self.merchandise.name}"
        return "Cart Item"
    
    @property
    def name(self):
        if self.item_type == 'product' and self.product:
            return self.product.name
        elif self.item_type == 'basket' and self.basket:
            return self.basket.name
        elif self.item_type == 'merchandise' and self.merchandise:
            return self.merchandise.name
        return "Item"
    
    @property
    def image(self):
        if self.item_type == 'product' and self.product and self.product.image:
            return self.product.image.url
        elif self.item_type == 'basket' and self.basket and self.basket.image:
            return self.basket.image.url
        elif self.item_type == 'merchandise' and self.merchandise and self.merchandise.image:
            return self.merchandise.image.url
        return None
    
    @property
    def total_price(self):
        return self.price * self.quantity
    
    def get_item_object(self):
        """Return the actual object based on item_type"""
        if self.item_type == 'product':
            return self.product
        elif self.item_type == 'basket':
            return self.basket
        elif self.item_type == 'merchandise':
            return self.merchandise
        return None