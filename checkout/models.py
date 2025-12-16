# checkout/models.py
from django.db import models
from django.conf import settings  # ← Use this instead of importing User directly
from cart.models import Cart
from products.models import Product, ProductBasket

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← Correct way when using custom User model
        on_delete=models.CASCADE,
        related_name='orders'
    )
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    zone = models.CharField(max_length=100)  # e.g., Westlands, Kilimani, etc.
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Payment'),
            ('paid', 'Paid'),
            ('failed', 'Payment Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.get_full_name() or self.user.username} - {self.status}"

    @property
    def items(self):
        return self.order_items.all()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    basket = models.ForeignKey(ProductBasket, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        if self.product:
            return f"{self.quantity} × {self.product.name}"
        return f"{self.quantity} × {self.basket.name} (Combo)"