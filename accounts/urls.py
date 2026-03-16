from django.urls import path
from .views import (
    SignUpView,
    CustomLoginView,
    CustomLogoutView,
    ProfileView,
    BookingView,
    UserBookingsView,
    BookingUpdateView,
    BookingDeleteView,
    home,
    services,
)

urlpatterns = [
    path("", home, name="home"),
    path("services/", services, name="services"),

    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),

    path("profile/", ProfileView.as_view(), name="profile"),
    path("book/", BookingView.as_view(), name="book"),
    path("bookings/", UserBookingsView.as_view(), name="bookings"),
    path("bookings/<int:pk>/edit/", BookingUpdateView.as_view(), name="booking_edit"),
    path("bookings/<int:pk>/delete/", BookingDeleteView.as_view(), name="booking_delete"),
]
