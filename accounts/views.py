# Signup view
# User story: Visitors can create an account with additional profile information.

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import SignUpForm

# Create your views here.

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = '/accounts/profile/'
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



