# cart/models.py
from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product, ProductBasket

User = get_user_model()

class Cart(models.Model):
    """One cart per registered user"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f"Cart of {self.user.get_full_name() or self.user.username}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def item_count(self):
        return self.items.count()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')

    product = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    basket = models.ForeignKey(
        ProductBasket,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(product__isnull=False, basket__isnull=True) |
                    models.Q(product__isnull=True, basket__isnull=False)
                ),
                name='cartitem_either_product_or_basket'
            )
        ]
        unique_together = ('cart', 'product', 'basket')

    def __str__(self):
        if self.product:
            return f"{self.quantity} × {self.product.name}"
        return f"{self.quantity} × {self.basket.name} (Basket)"

    @property
    def total_price(self):
        if self.product:
            return self.product.price * self.quantity
        if self.basket:
            return self.basket.price * self.quantity
        return 0