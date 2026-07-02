from django.urls import path
from . import views

urlpatterns = [
    path("create-checkout-session/", views.create_checkout_session, name="create-checkout-session"),
    path("payment/success/<int:booking_id>/", views.payment_success, name="payment-success"),
    path("payment/cancelled/<int:booking_id>/", views.payment_cancelled, name="payment-cancelled"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe-webhook"),
]