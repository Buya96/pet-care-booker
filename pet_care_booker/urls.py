"""
URL configuration for pet_care_booker project.
"""
from django.contrib import admin
from django.urls import path, include
from . import views  # For home view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # All accounts URLs
    path('', include('accounts.urls')),  # Home + services accessible from root
]
