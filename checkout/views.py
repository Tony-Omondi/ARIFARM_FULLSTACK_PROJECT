# checkout/views.py
import json
import logging
from datetime import time
from decimal import Decimal, ROUND_HALF_UP

import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction

from cart.models import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm
from .mpesa import initiate_stk_push, query_stk_push

logger = logging.getLogger(__name__)


@login_required
def checkout_view(request):
    """Main checkout page: form + order summary with delivery fee"""
    cart = request.user.cart

    if not cart.items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect('cart:cart_detail')

    subtotal = cart.total_price

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            selected_zone = form.cleaned_data['zone']
            delivery_fee = selected_zone.delivery_fee
            total = subtotal + delivery_fee

            try:
                with transaction.atomic():
                    order = Order.objects.create(
                        user=request.user,
                        cart=cart,
                        email=form.cleaned_data['email'],
                        phone_number=form.cleaned_data['phone_number'],
                        zone=selected_zone,
                        preferred_delivery_date=form.cleaned_data['preferred_delivery_date'],
                        subtotal_amount=subtotal,
                        delivery_fee=delivery_fee,
                        total_amount=total,
                        status='pending'
                    )

                    # Set delivery time window
                    time_slot = form.cleaned_data['preferred_delivery_time']
                    time_mapping = {
                        '09:00-12:00': (time(9, 0), time(12, 0)),
                        '12:00-15:00': (time(12, 0), time(15, 0)),
                        '15:00-18:00': (time(15, 0), time(18, 0)),
                        '18:00-21:00': (time(18, 0), time(21, 0)),
                    }
                    start_time, end_time = time_mapping.get(time_slot, (None, None))
                    order.preferred_delivery_time_start = start_time
                    order.preferred_delivery_time_end = end_time
                    order.save(update_fields=['preferred_delivery_time_start', 'preferred_delivery_time_end'])

                    # Snapshot cart items
                    for item in cart.items.all():
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            basket=item.basket,
                            quantity=item.quantity,
                            unit_price=item.unit_price,
                            total_price=item.total_price
                        )

                # M-Pesa: Charge total including delivery fee
                phone = form.cleaned_data['phone_number']
                amount = int(total.quantize(Decimal('1'), rounding=ROUND_HALF_UP))

                logger.info(f"STK Push → Phone: {phone}, Amount: {amount} KES (Subtotal: {subtotal} + Delivery: {delivery_fee})")
                response = initiate_stk_push(phone, amount)

                if response.get("ResponseCode") == "0":
                    order.checkout_request_id = response["CheckoutRequestID"]
                    order.save(update_fields=['checkout_request_id'])

                    messages.success(request, "STK Push sent! Please complete payment on your phone.")
                    return render(request, 'checkout/pending.html', {
                        'order': order,
                        'checkout_request_id': response["CheckoutRequestID"],
                    })
                else:
                    error_msg = response.get("CustomerMessage") or response.get("errorMessage") or "Unknown error"
                    logger.error(f"STK Push failed: {error_msg}")
                    order.status = 'failed'
                    order.save(update_fields=['status'])
                    messages.error(request, f"Payment failed: {error_msg}. Please try again.")

            except Exception as e:
                logger.exception("Unexpected error during checkout")
                messages.error(request, "An error occurred. Please try again later.")

            # If failed, show form again with calculated totals
            return render(request, 'checkout/checkout_form.html', {
                'form': form,
                'cart': cart,
                'subtotal': subtotal,
                'delivery_fee': delivery_fee,
                'total': total,
            })

    else:
        # GET request
        initial = {'email': request.user.email or ''}
        form = CheckoutForm(initial=initial)

    return render(request, 'checkout/checkout_form.html', {
        'form': form,
        'cart': cart,
        'subtotal': subtotal,
        'delivery_fee': None,  # Will be shown after zone selection (or via JS)
        'total': subtotal,
    })


@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='paid')
    return render(request, 'checkout/order_success.html', {'order': order})


@require_POST
@login_required
def stk_status_view(request):
    try:
        data = json.loads(request.body)
        checkout_request_id = data.get('checkout_request_id')
        if not checkout_request_id:
            return JsonResponse({"error": "Missing checkout_request_id"}, status=400)

        status_response = query_stk_push(checkout_request_id)
        return JsonResponse({"status": status_response})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"STK status error: {e}")
        return JsonResponse({"error": "Server error"}, status=500)


@csrf_exempt
def payment_callback(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        callback_data = json.loads(request.body)
        logger.info(f"M-Pesa Callback received: {callback_data}")

        stk_callback = callback_data["Body"]["stkCallback"]
        result_code = int(stk_callback["ResultCode"])
        checkout_request_id = stk_callback["CheckoutRequestID"]

        order = get_object_or_404(Order, checkout_request_id=checkout_request_id, status='pending')

        if result_code == 0:
            metadata = stk_callback["CallbackMetadata"]["Item"]
            receipt = next((item["Value"] for item in metadata if item["Name"] == "MpesaReceiptNumber"), None)

            order.status = 'paid'
            order.mpesa_receipt_number = receipt
            order.save(update_fields=['status', 'mpesa_receipt_number'])

            # Clear user's cart
            if order.cart:
                order.cart.items.all().delete()

            logger.info(f"Payment SUCCESS → Order #{order.id} | Receipt: {receipt}")
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

        else:
            result_desc = stk_callback.get("ResultDesc", "Payment failed")
            order.status = 'failed'
            order.save(update_fields=['status'])
            logger.warning(f"Payment FAILED → Order #{order.id} | {result_desc}")
            return JsonResponse({"ResultCode": result_code, "ResultDesc": result_desc})

    except Exception as e:
        logger.error(f"Callback processing error: {e}")
        return JsonResponse({"error": "Processing failed"}, status=500)


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'checkout/order_detail.html', {'order': order})