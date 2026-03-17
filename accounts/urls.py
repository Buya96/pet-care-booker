from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('services/', views.services, name='services'),
    path('book/', views.BookingView.as_view(), name='book'),
    path('bookings/', views.UserBookingsView.as_view(), name='bookings'),
    path('bookings/<int:pk>/edit/', views.BookingUpdateView.as_view(), name='booking_update'),
    path('bookings/<int:pk>/delete/', views.BookingDeleteView.as_view(), name='booking_delete'),
    path('pay/', views.create_checkout_session, name='pay'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]
