# Commit 2: Auth URLs
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.login, name='login'),  # Built-in Django login
    path('logout/', views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('services/', views.services, name='services'),
]