"""
URL configuration for pet_care_booker project.
"""
from django.contrib import admin
from django.urls import path, include
from . import views  # For home view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'), 
    path('accounts/', include('accounts.urls')),  # ONLY THIS LINE
    # DELETE: path('', include('accounts.urls')),  # Duplicate!
]
