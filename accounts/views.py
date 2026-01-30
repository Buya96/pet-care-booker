# Signup view
# User story: Visitors can create an account with additional profile information.

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, FormView, TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import SignUpForm, BookingForm  # Add BookingForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Booking  # Assuming Booking model exists   




# Create your views here.

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = '/accounts/login/'
    template_name = 'accounts/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        # Auto-login after signup
        user = form.save()
        login(self.request, user)
        return response

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    success_url = '/'

login = LoginView.as_view()

class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['bookings'] = Booking.objects.filter(user=self.request.user).order_by('-created')[:5]
        return context



def home(request):
    return render(request, 'accounts/home.html')

def services(request):
    return render(request, 'accounts/services.html')

class BookingView(LoginRequiredMixin, FormView):
    template_name = 'accounts/booking.html'
    form_class = BookingForm
    success_url = reverse_lazy('profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass logged-in user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user  # Ensure user is set
        form.save()
        return super().form_valid(form)

class UserBookingsView(ListView):
    model = Booking
    template_name = 'accounts/bookings.html'
    context_object_name = 'bookings'
    paginate_by = 10
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    
class BookingUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    fields = ['service', 'pet_name', 'date', 'time', 'notes']
    template_name = 'accounts/booking_form.html'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('bookings')

class BookingDeleteView(LoginRequiredMixin, DeleteView):
    model = Booking
    template_name = 'accounts/booking_confirm_delete.html'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('bookings')
