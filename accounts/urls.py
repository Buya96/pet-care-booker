from django.urls import path
from . import views



urlpatterns = [
    # Auth
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Bookings
    path('book/', views.BookingView.as_view(), name='book'),
    path('bookings/', views.UserBookingsView.as_view(), name='bookings'),
    path('booking/<int:pk>/update/', views.BookingUpdateView.as_view(), name='booking-update'),
    path('booking/<int:pk>/delete/', views.BookingDeleteView.as_view(), name='booking-delete'),
    
    # Static pages
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    
    # Stripe
    path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
    path('payment-success/<int:booking_id>/', views.payment_success, name='payment-success'),
]

