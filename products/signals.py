# products/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Product, ProductBasket, Recipe, Category

@receiver(pre_save, sender=Category)
def category_pre_save(sender, instance, **kwargs):
    """Auto-generate slug for category if not provided"""
    if not instance.slug:
        instance.slug = slugify(instance.name)

@receiver(pre_save, sender=Product)
def product_pre_save(sender, instance, **kwargs):
    """Auto-generate slug for product if not provided"""
    if not instance.slug:
        instance.slug = slugify(instance.name)

@receiver(pre_save, sender=ProductBasket)
def basket_pre_save(sender, instance, **kwargs):
    """Auto-generate slug for basket if not provided"""
    if not instance.slug:
        instance.slug = slugify(instance.name)

@receiver(pre_save, sender=Recipe)
def recipe_pre_save(sender, instance, **kwargs):
    """Auto-generate slug for recipe if not provided"""
    if not instance.slug:
        instance.slug = slugify(instance.title)