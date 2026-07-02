import json
import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from accounts.models import Booking


logger = logging.getLogger(__name__)

stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)


@csrf_exempt
@require_http_methods(["POST"])
def create_checkout_session(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Please log in first."}, status=401)

    try:
        data = json.loads(request.body.decode("utf-8"))
        service = data.get("service", "boarding")
        booking_id = data.get("booking_id")

        if not booking_id:
            return JsonResponse({"error": "Missing booking_id."}, status=400)

        booking = get_object_or_404(
            Booking,
            id=booking_id,
            user=request.user,
            paid=False,
        )

        prices = {
            "dog_walking": 3000,
            "grooming": 2500,
            "boarding": 3500,
        }
        price = prices.get(service, 3000)

        success_url = request.build_absolute_uri(
            reverse("payment-success", args=[booking.id])
        )
        cancel_url = request.build_absolute_uri(
            reverse("payment-cancelled", args=[booking.id])
        )

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "gbp",
                        "product_data": {
                            "name": f"{service.replace('_', ' ').title()} - {booking.pet_name}"
                        },
                        "unit_amount": price,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "booking_id": str(booking.id),
                "user_id": str(request.user.id),
                "service": service,
            },
        )

        booking.stripe_payment_intent = session.id
        booking.amount_paid = price / 100
        booking.save(update_fields=["stripe_payment_intent", "amount_paid"])

        logger.info(f"Checkout session created for booking {booking.id}, session {session.id}")

        return JsonResponse({"url": session.url})

    except Exception as e:
        logger.exception("Error creating checkout session")
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.paid:
        messages.success(request, f"Payment complete for {booking.pet_name}.")
    else:
        messages.info(
            request,
            f"Payment submitted for {booking.pet_name}. Your booking will update after Stripe confirms it."
        )

    return redirect("bookings")


@login_required
def payment_cancelled(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    messages.warning(
        request,
        f"Payment was cancelled for {booking.pet_name}. Your booking has not been marked as paid."
    )
    return redirect(f"{reverse('book')}?booking_id={booking.id}")


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", None)

    if not endpoint_secret:
        logger.error("Stripe webhook secret not configured")
        return HttpResponse("Webhook secret not configured.", status=500)

    if not sig_header:
        logger.error("Missing Stripe-Signature header")
        return HttpResponse("Missing signature header.", status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=endpoint_secret,
        )
    except ValueError:
        logger.exception("Invalid Stripe webhook payload")
        return HttpResponse("Invalid payload.", status=400)
    except stripe.error.SignatureVerificationError:
        logger.exception("Invalid Stripe webhook signature")
        return HttpResponse("Invalid signature.", status=400)

    logger.info(f"Stripe webhook received: {event['type']}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {}) or {}
        booking_id = metadata.get("booking_id")

        logger.info(f"Webhook session id: {session.get('id')}")
        logger.info(f"Webhook metadata: {metadata}")
        logger.info(f"Webhook booking_id: {booking_id}")

        if not booking_id:
            logger.warning("No booking_id found in Stripe session metadata")
            return HttpResponse(status=200)

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            logger.warning(f"Booking {booking_id} not found")
            return HttpResponse(status=200)

        if booking.paid:
            logger.info(f"Booking {booking_id} already marked as paid")
            return HttpResponse(status=200)

        booking.paid = True
        booking.stripe_payment_intent = session.get("id")

        amount_total = session.get("amount_total")
        if amount_total is not None:
            booking.amount_paid = amount_total / 100

        booking.save(update_fields=["paid", "stripe_payment_intent", "amount_paid"])
        logger.info(f"Booking {booking_id} marked as paid successfully")

    return HttpResponse(status=200)
