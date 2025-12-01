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
            defaults={'session_key': request.session.session_key}
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
    """Add item to cart"""
    try:
        data = json.loads(request.body)
        item_type = data.get('item_type')
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        
        cart = get_or_create_cart(request)
        
        if item_type == 'product':
            product = get_object_or_404(Product, id=item_id, is_active=True)
            
            # Check stock
            if product.stock < quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Only {product.stock} items available in stock'
                })
            
            # Check if item already in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                item_type='product',
                product=product,
                defaults={'quantity': quantity, 'price': product.price}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
                
        elif item_type == 'basket':
            basket = get_object_or_404(ProductBasket, id=item_id, is_active=True)
            
            # Check basket stock (based on included products)
            if not basket.is_available():
                return JsonResponse({
                    'success': False,
                    'message': 'Basket is currently unavailable'
                })
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                item_type='basket',
                basket=basket,
                defaults={'quantity': quantity, 'price': basket.price}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
                
        elif item_type == 'merchandise':
            merchandise = get_object_or_404(Merchandise, id=item_id, is_active=True)
            
            if merchandise.stock < quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Only {merchandise.stock} items available in stock'
                })
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                item_type='merchandise',
                merchandise=merchandise,
                defaults={'quantity': quantity, 'price': merchandise.price}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
        
        else:
            return JsonResponse({'success': False, 'message': 'Invalid item type'})
        
        # Recalculate cart totals
        cart.calculate_totals()
        
        return JsonResponse({
            'success': True,
            'message': 'Item added to cart',
            'cart_item_count': cart.get_item_count(),
            'subtotal': float(cart.subtotal),
            'total': float(cart.total)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        # Check stock based on item type
        item_obj = cart_item.get_item_object()
        if hasattr(item_obj, 'stock') and item_obj.stock < quantity:
            return JsonResponse({
                'success': False,
                'message': f'Only {item_obj.stock} items available in stock'
            })
        
        cart_item.quantity = quantity
        cart_item.save()
        
        # Recalculate cart totals
        cart.calculate_totals()
        
        return JsonResponse({
            'success': True,
            'message': 'Cart updated',
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
    """Remove item from cart"""
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        
        # Recalculate cart totals
        cart.calculate_totals()
        
        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart',
            'cart_item_count': cart.get_item_count(),
            'subtotal': float(cart.subtotal),
            'total': float(cart.total)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def view_cart(request):
    """View cart page"""
    cart = get_or_create_cart(request)
    cart.calculate_totals()  # Ensure totals are up to date
    
    context = {
        'cart': cart,
        'cart_items': cart.items.all().select_related('product', 'basket', 'merchandise')
    }
    return render(request, 'cart/cart.html', context)


@require_POST
def update_delivery_info(request):
    """Update delivery information in cart (first step of checkout)"""
    try:
        cart = get_or_create_cart(request)
        
        cart.delivery_name = request.POST.get('delivery_name')
        cart.delivery_phone = request.POST.get('delivery_phone')
        cart.delivery_county = request.POST.get('delivery_county')
        cart.delivery_zone = request.POST.get('delivery_zone')
        cart.delivery_address = request.POST.get('delivery_address')
        
        # Mark checkout as started
        cart.is_checkout_started = True
        
        cart.save()
        cart.calculate_totals()  # Recalculate with new delivery fee
        
        messages.success(request, 'Delivery information updated')
        return redirect('cart:checkout_payment')
        
    except Exception as e:
        messages.error(request, f'Error updating delivery info: {str(e)}')
        return redirect('cart:view_cart')


def checkout_delivery(request):
    """Checkout - Delivery Information step"""
    cart = get_or_create_cart(request)
    
    if cart.is_empty():
        messages.warning(request, 'Your cart is empty')
        return redirect('products:product_list')
    
    # Pre-fill with user info if logged in
    if request.user.is_authenticated and request.user.profile:
        profile = request.user.profile
        initial_data = {
            'delivery_name': profile.name or '',
            'delivery_phone': profile.phone_number or '',
            'delivery_county': profile.county or '',
            'delivery_zone': profile.zone or '',
            'delivery_address': profile.address or '',
        }
    else:
        initial_data = {}
    
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
    """Checkout - Payment Method step"""
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
    """Final step - Place order"""
    try:
        cart = get_or_create_cart(request)
        
        if cart.is_empty():
            messages.error(request, 'Your cart is empty')
            return redirect('products:product_list')
        
        # Get payment method
        payment_method = request.POST.get('payment_method')
        if not payment_method:
            messages.error(request, 'Please select a payment method')
            return redirect('cart:checkout_payment')
        
        # Validate all items are in stock
        for item in cart.items.all():
            item_obj = item.get_item_object()
            if hasattr(item_obj, 'stock') and item_obj.stock < item.quantity:
                messages.error(request, f'{item.name} is out of stock')
                return redirect('cart:view_cart')
        
        # Here you would:
        # 1. Create Order from Cart
        # 2. Process payment based on payment_method
        # 3. Reduce stock
        # 4. Clear cart
        # 5. Send confirmation
        
        # For now, just show a success message
        messages.success(request, 'Order placed successfully! Payment processing would happen here.')
        
        # Clear the cart after order
        cart.items.all().delete()
        cart.status = 'converted'
        cart.save()
        
        return redirect('cart:order_confirmation')
        
    except Exception as e:
        messages.error(request, f'Error placing order: {str(e)}')
        return redirect('cart:checkout_payment')


def order_confirmation(request):
    """Order confirmation page"""
    return render(request, 'cart/order_confirmation.html')


@login_required
def merge_carts(request):
    """Merge guest cart with user cart after login"""
    if not request.session.session_key:
        return
    
    try:
        # Get guest cart
        guest_cart = Cart.objects.filter(
            session_key=request.session.session_key,
            status='active'
        ).first()
        
        if guest_cart and guest_cart.items.exists():
            # Get or create user cart
            user_cart, created = Cart.objects.get_or_create(
                user=request.user,
                status='active',
                defaults={'session_key': request.session.session_key}
            )
            
            # Merge items
            for guest_item in guest_cart.items.all():
                # Check if similar item exists in user cart
                existing_item = None
                
                if guest_item.item_type == 'product' and guest_item.product:
                    existing_item = user_cart.items.filter(
                        item_type='product',
                        product=guest_item.product
                    ).first()
                elif guest_item.item_type == 'basket' and guest_item.basket:
                    existing_item = user_cart.items.filter(
                        item_type='basket',
                        basket=guest_item.basket
                    ).first()
                elif guest_item.item_type == 'merchandise' and guest_item.merchandise:
                    existing_item = user_cart.items.filter(
                        item_type='merchandise',
                        merchandise=guest_item.merchandise
                    ).first()
                
                if existing_item:
                    existing_item.quantity += guest_item.quantity
                    existing_item.save()
                else:
                    # Create new item in user cart
                    CartItem.objects.create(
                        cart=user_cart,
                        item_type=guest_item.item_type,
                        product=guest_item.product,
                        basket=guest_item.basket,
                        merchandise=guest_item.merchandise,
                        quantity=guest_item.quantity,
                        price=guest_item.price
                    )
            
            # Delete guest cart
            guest_cart.delete()
            
            # Recalculate user cart totals
            user_cart.calculate_totals()
            
    except Exception as e:
        print(f"Error merging carts: {e}")