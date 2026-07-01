from django.urls import path
from . import views

urlpatterns = [
    path("book/", views.BookingView.as_view(), name="book"),
    path("bookings/", views.UserBookingsView.as_view(), name="bookings"),
    path("booking/<int:pk>/update/", views.BookingUpdateView.as_view(), name="booking-update"),
    path("booking/<int:pk>/delete/", views.BookingDeleteView.as_view(), name="booking-delete"),
]