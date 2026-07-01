from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),


    path("", views.home, name="home"),
    path("services/", views.services, name="services"),

    path("create-checkout-session/", views.create_checkout_session, name="create-checkout-session"),
    path("payment/success/<int:booking_id>/", views.payment_success, name="payment-success"),
    path("payment/cancelled/<int:booking_id>/", views.payment_cancelled, name="payment-cancelled"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe-webhook"),
]