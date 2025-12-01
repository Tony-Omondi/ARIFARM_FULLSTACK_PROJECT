from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from .models import Cart, CartItem
from products.models import Product, ProductBasket, Merchandise
from decimal import Decimal
import json


def get_or_create_cart(request):
    """Helper function to get or create cart"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            status='active',
            defaults={'session_key': request.session.session_key or ''}
        )
    else:
        if not request.session.session_key:
            request.session.create()
        
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(
            session_key=session_key,
            status='active',
            defaults={}
        )
    
    return cart


@require_POST
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        item_type = data.get('item_type')
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        
        cart = get_or_create_cart(request)
        
        if item_type == 'product':
            product = get_object_or_404(Product, id=item_id, is_active=True)
            if product.stock < quantity:
                return JsonResponse({'success': False, 'message': f'Only {product.stock} in stock'})
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, item_type='product', product=product,
                defaults={'quantity': quantity, 'price': product.price}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

        elif item_type == 'basket':
            basket = get_object_or_404(ProductBasket, id=item_id, is_active=True)
            if not basket.is_available():
                return JsonResponse({'success': False, 'message': 'Basket unavailable'})
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, item_type='basket', basket=basket,
                defaults={'quantity': quantity, 'price': basket.price}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

        elif item_type == 'merchandise':
            merchandise = get_object_or_404(Merchandise, id=item_id, is_active=True)
            if merchandise.stock < quantity:
                return JsonResponse({'success': False, 'message': f'Only {merchandise.stock} in stock'})
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, item_type='merchandise', merchandise=merchandise,
                defaults={'quantity': quantity, 'price': merchandise.price}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
        else:
            return JsonResponse({'success': False, 'message': 'Invalid item type'})

        cart.calculate_totals()

        return JsonResponse({
            'success': True,
            'message': 'Added to cart',
            'cart_item_count': cart.get_item_count(),
            'subtotal': float(cart.subtotal),
            'total': float(cart.total)
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
def update_cart_item(request, item_id):
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        item_obj = cart_item.get_item_object()
        if hasattr(item_obj, 'stock') and item_obj.stock < quantity:
            return JsonResponse({'success': False, 'message': f'Only {item_obj.stock} available'})

        cart_item.quantity = quantity
        cart_item.save()
        cart.calculate_totals()

        return JsonResponse({
            'success': True,
            'item_total': float(cart_item.total_price),
            'subtotal': float(cart.subtotal),
            'delivery_fee': float(cart.delivery_fee),
            'discount': float(cart.discount),
            'total': float(cart.total)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
def remove_from_cart(request, item_id):
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        cart.calculate_totals()

        return JsonResponse({
            'success': True,
            'message': 'Item removed',
            'cart_item_count': cart.get_item_count(),
            'subtotal': float(cart.subtotal),
            'total': float(cart.total)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def view_cart(request):
    cart = get_or_create_cart(request)
    cart.calculate_totals()

    context = {
        'cart': cart,
        'cart_items': cart.items.all().select_related('product', 'basket', 'merchandise')
    }
    return render(request, 'cart/cart.html', context)


@require_POST
def update_delivery_info(request):
    try:
        cart = get_or_create_cart(request)
        
        cart.delivery_name = request.POST.get('delivery_name')
        cart.delivery_phone = request.POST.get('delivery_phone')
        cart.delivery_county = request.POST.get('delivery_county')
        cart.delivery_zone = request.POST.get('delivery_zone')
        cart.delivery_address = request.POST.get('delivery_address')
        
        cart.is_checkout_started = True
        cart.save()
        cart.calculate_totals()

        messages.success(request, 'Delivery information saved!')
        return redirect('cart:checkout_payment')
    except Exception as e:
        messages.error(request, f'Error: {e}')
        return redirect('cart:view_cart')


def checkout_delivery(request):
    cart = get_or_create_cart(request)
    
    if cart.is_empty():
        messages.warning(request, 'Your cart is empty')
        return redirect('products:product_list')

    initial_data = {
        'delivery_name': cart.delivery_name or '',
        'delivery_phone': cart.delivery_phone or '',
        'delivery_county': cart.delivery_county or '',
        'delivery_zone': cart.delivery_zone or '',
        'delivery_address': cart.delivery_address or '',
    }

    if request.user.is_authenticated:
        user = request.user

        if not initial_data['delivery_name']:
            full_name = ' '.join(filter(None, [user.first_name, user.last_name])).strip()
            if full_name:
                initial_data['delivery_name'] = full_name
            elif user.email:
                initial_data['delivery_name'] = user.email.split('@')[0].replace('.', ' ').title()

        if not initial_data['delivery_phone']:
            initial_data['delivery_phone'] = getattr(user, 'phone_number', '') or ''

        if not initial_data['delivery_county']:
            initial_data['delivery_county'] = getattr(user, 'county', '') or ''

        if not initial_data['delivery_zone']:
            initial_data['delivery_zone'] = getattr(user, 'zone', '') or ''

        if not initial_data['delivery_address']:
            initial_data['delivery_address'] = getattr(user, 'address', '') or ''

    context = {
        'cart': cart,
        'initial_data': initial_data,
        'counties': [
            'Nairobi', 'Kiambu', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret',
            'Thika', 'Machakos', 'Kakamega', 'Kisii', 'Meru', 'Nyeri'
        ]
    }
    return render(request, 'cart/checkout_delivery.html', context)


def checkout_payment(request):
    cart = get_or_create_cart(request)
    
    if cart.is_empty():
        messages.warning(request, 'Your cart is empty')
        return redirect('products:product_list')
    
    if not cart.is_checkout_started:
        return redirect('cart:checkout_delivery')

    context = {
        'cart': cart,
        'payment_methods': [
            {'value': 'mpesa', 'name': 'M-Pesa', 'icon': 'mobile-alt'},
            {'value': 'paystack', 'name': 'Paystack (Card)', 'icon': 'credit-card'},
            {'value': 'cod', 'name': 'Cash on Delivery', 'icon': 'money-bill'},
        ]
    }
    return render(request, 'cart/checkout_payment.html', context)


@require_POST
def place_order(request):
    try:
        cart = get_or_create_cart(request)
        if cart.is_empty():
            messages.error(request, 'Cart is empty')
            return redirect('products:product_list')

        payment_method = request.POST.get('payment_method')
        if not payment_method:
            messages.error(request, 'Please select a payment method')
            return redirect('cart:checkout_payment')

        # Stock check
        for item in cart.items.all():
            obj = item.get_item_object()
            if hasattr(obj, 'stock') and obj.stock < item.quantity:
                messages.error(request, f'{item.name} is out of stock')
                return redirect('cart:view_cart')

        messages.success(request, 'Order placed successfully! (Payment integration coming soon)')

        cart.items.all().delete()
        cart.status = 'converted'
        cart.save()

        return redirect('cart:order_confirmation')

    except Exception as e:
        messages.error(request, f'Error: {e}')
        return redirect('cart:checkout_payment')


def order_confirmation(request):
    return render(request, 'cart/order_confirmation.html')


@login_required
def merge_carts(request):
    if not request.session.session_key:
        return

    try:
        guest_cart = Cart.objects.filter(session_key=request.session.session_key, status='active').first()
        if not guest_cart or not guest_cart.items.exists():
            return

        user_cart, _ = Cart.objects.get_or_create(user=request.user, status='active')
        
        for item in guest_cart.items.all():
            existing = None
            if item.item_type == 'product' and item.product:
                existing = user_cart.items.filter(item_type='product', product=item.product).first()
            elif item.item_type == 'basket' and item.basket:
                existing = user_cart.items.filter(item_type='basket', basket=item.basket).first()
            elif item.item_type == 'merchandise' and item.merchandise:
                existing = user_cart.items.filter(item_type='merchandise', merchandise=item.merchandise).first()

            if existing:
                existing.quantity += item.quantity
                existing.save()
            else:
                CartItem.objects.create(
                    cart=user_cart,
                    item_type=item.item_type,
                    product=item.product,
                    basket=item.basket,
                    merchandise=item.merchandise,
                    quantity=item.quantity,
                    price=item.price
                )

        guest_cart.delete()
        user_cart.calculate_totals()

    except Exception as e:
        print("Cart merge error:", e)