from django.contrib import admin
from .models import Booking, UserProfile
# Register your models here.


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['pet_name', 'service', 'date', 'paid', 'created']
    list_filter = ['service', 'paid', 'date']
    list_editable = ['paid']  # tick/untick paid directly in admin

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass
