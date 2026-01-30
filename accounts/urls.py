# Commit 2: Auth URLs
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.login, name='login'),  # Built-in Django login
    path('logout/', views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('services/', views.services, name='services'),
    path('book/', views.BookingView.as_view(), name='book'),
    path('booking/<int:pk>/update/', views.BookingUpdateView.as_view(), name='booking_update'),
    path('booking/<int:pk>/delete/', views.BookingDeleteView.as_view(), name='booking_delete'),
    path('bookings/', views.UserBookingsView.as_view(), name='bookings'),
    
]