"""
URL configuration for pet_care_booker project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Accounts app
    path("accounts/", include("accounts.urls")),

    # Root-level pages from accounts
    path("", include("accounts.urls")),

    # Booking routes stay at the same public URLs as before
    path("", include("bookings.urls")),
]