import stripe
import json  # <-- ADDED for JSON body parsing

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login  # <-- UNCOMMENTED (needed for SignUpView)
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.views.generic import CreateView, FormView, TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SignUpForm, BookingForm
from .models import Booking

# ---------- Stripe Config ----------
stripe.api_key = settings.STRIPE_SECRET_KEY

# ---------- Auth / Signup ----------
class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = "/accounts/login/"

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return "/"

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("home")

# ---------- Profile / Static pages ----------
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"
    login_url = "login"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["bookings"] = (
            Booking.objects.filter(user=self.request.user)
            .order_by("-created")[:5]
        )
        return context

def home(request):
    return render(request, "accounts/home.html")

def services(request):
    return render(request, "accounts/services.html")

# ---------- Bookings ----------
class BookingView(LoginRequiredMixin, FormView):
    template_name = "accounts/booking.html"
    form_class = BookingForm
    success_url = reverse_lazy("profile")
    login_url = "login"
    redirect_field_name = "next"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)

class UserBookingsView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "accounts/bookings.html"
    context_object_name = "bookings"
    paginate_by = 10
    login_url = "login"
    redirect_field_name = "next"

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by("-created")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context

class BookingUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    fields = ["service", "pet_name", "date", "time", "notes"]
    template_name = "accounts/booking_form.html"
    login_url = "login"
    redirect_field_name = "next"

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("bookings")

class BookingDeleteView(LoginRequiredMixin, DeleteView):
    model = Booking
    template_name = "accounts/booking_confirm_delete.html"
    login_url = "login"
    redirect_field_name = "next"

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("bookings")

# ---------- STRIPE (FULLY FIXED) ----------
@csrf_exempt  # <-- ADDED: allows JS POST without CSRF cookie
@require_http_methods(["POST"])  # <-- ADDED: enforces POST only
def create_checkout_session(request):
    try:
        # Parse JSON body from JS fetch()  <-- FIXED: was request.POST (empty for JSON)
        data = json.loads(request.body.decode("utf-8"))
        service = data.get("service", "boarding")
        
        prices = {"dog_walking": 3000, "grooming": 2500, "boarding": 3500}
        price = prices.get(service, 3000)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "gbp",
                        "product_data": {
                            "name": service.replace("_", " ").title()
                        },
                        "unit_amount": price,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=request.build_absolute_uri("/profile/"),  # <-- FIXED: use existing URL
            cancel_url=request.build_absolute_uri("/book/"),     # <-- FIXED: use existing URL
        )
        return JsonResponse({"id": session.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
