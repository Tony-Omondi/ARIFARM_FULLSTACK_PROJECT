# checkout/views.py
import json
import logging
import requests  # <-- Added explicit import for clarity
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from cart.models import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm
from .mpesa import initiate_stk_push, query_stk_push

# Set up logger for detailed debugging
logger = logging.getLogger(__name__)


@login_required
def checkout_view(request):
    """Main checkout page: form + order summary"""
    cart = request.user.cart

    if not cart.items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect('cart:cart_detail')

    total = cart.total_price

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create pending order first
            order = Order.objects.create(
                user=request.user,
                cart=cart,
                email=form.cleaned_data['email'],
                phone_number=form.cleaned_data['phone_number'],
                zone=form.cleaned_data['zone'],
                total_amount=total,
                status='pending'
            )

            # Snapshot cart items into order items
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    basket=item.basket,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price
                )

            # Initiate M-Pesa STK Push
            try:
                phone = form.cleaned_data['phone_number']
                amount = int(total)  # M-Pesa expects integer (in shillings)

                logger.info(f"Initiating STK Push: Phone={phone}, Amount={amount}")
                response = initiate_stk_push(phone, amount)

                logger.info(f"M-Pesa STK Push Response: {response}")

                if response.get("ResponseCode") == "0":
                    order.checkout_request_id = response["CheckoutRequestID"]
                    order.save(update_fields=['checkout_request_id'])

                    messages.success(request, "STK Push sent to your phone! Please complete payment.")
                    return render(request, 'checkout/pending.html', {
                        'order': order,
                        'checkout_request_id': response["CheckoutRequestID"],
                    })

                else:
                    # Handle M-Pesa error response
                    customer_msg = response.get("CustomerMessage")
                    error_msg = response.get("errorMessage")
                    request_desc = response.get("RequestDescription", "Unknown error")

                    full_error = customer_msg or error_msg or request_desc
                    logger.error(f"STK Push failed: {full_error} | Full response: {response}")

                    order.status = 'failed'
                    order.save(update_fields=['status'])

                    messages.error(request, f"Payment initiation failed: {full_error}. Please try again.")

            except ValueError as ve:
                logger.warning(f"Invalid amount or phone number format: {ve}")
                messages.error(request, "Invalid phone number or amount. Please check your input.")
            except requests.exceptions.RequestException as re:  # <-- Fixed: was 'request.exceptions'
                logger.error(f"Network error calling M-Pesa API: {re}")
                messages.error(request, "Network error. Please check your internet connection and try again.")
            except Exception as e:
                logger.exception("Unexpected error during STK Push initiation")
                messages.error(request, "An unexpected error occurred. Please try again later.")

            # If we reach here, something went wrong — re-render the form
            return render(request, 'checkout/checkout_form.html', {
                'form': form,
                'cart': cart,
                'total': total
            })

    else:
        # GET request — show empty form with user data pre-filled if available
        initial = {
            'email': request.user.email or '',
            'phone_number': getattr(request.user, 'phone_number', '') or '',
        }
        form = CheckoutForm(initial=initial)

    return render(request, 'checkout/checkout_form.html', {
        'form': form,
        'cart': cart,
        'total': total
    })


@login_required
def order_success_view(request, order_id):
    """Final success page after confirmed payment"""
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        status='paid'
    )
    return render(request, 'checkout/order_success.html', {'order': order})


@require_POST
@login_required
def stk_status_view(request):
    """Frontend polls this endpoint to check payment status"""
    try:
        data = json.loads(request.body)
        checkout_request_id = data.get('checkout_request_id')

        if not checkout_request_id:
            return JsonResponse({"error": "Missing checkout_request_id"}, status=400)

        logger.info(f"Querying STK status for: {checkout_request_id}")
        status_response = query_stk_push(checkout_request_id)
        logger.info(f"STK Query Response: {status_response}")

        return JsonResponse({"status": status_response})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error in stk_status_view: {e}")
        return JsonResponse({"error": "Server error"}, status=500)


@csrf_exempt
def payment_callback(request):
    """M-Pesa posts callback result here"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        callback_data = json.loads(request.body)
        logger.info(f"M-Pesa Callback received: {callback_data}")

        stk_callback = callback_data["Body"]["stkCallback"]
        result_code = int(stk_callback["ResultCode"])
        checkout_request_id = stk_callback["CheckoutRequestID"]

        order = get_object_or_404(Order, checkout_request_id=checkout_request_id)

        if result_code == 0:
            # Payment SUCCESS
            metadata = stk_callback["CallbackMetadata"]["Item"]
            mpesa_receipt = next(
                (item["Value"] for item in metadata if item["Name"] == "MpesaReceiptNumber"),
                None
            )

            order.status = 'paid'
            order.mpesa_receipt_number = mpesa_receipt
            order.save(update_fields=['status', 'mpesa_receipt_number'])

            # Clear the user's cart
            order.cart.items.all().delete()

            logger.info(f"Payment SUCCESS for Order #{order.id} - Receipt: {mpesa_receipt}")
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

        else:
            # Payment FAILED or CANCELLED
            result_desc = stk_callback.get("ResultDesc", "Payment failed")
            order.status = 'failed'
            order.save(update_fields=['status'])
            logger.warning(f"Payment FAILED for Order #{order.id}: {result_desc}")
            return JsonResponse({"ResultCode": result_code, "ResultDesc": result_desc})

    except Exception as e:
        logger.error(f"Callback processing error: {e}")
        return JsonResponse({"error": "Processing failed"}, status=500)