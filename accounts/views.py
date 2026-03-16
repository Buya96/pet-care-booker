import stripe

from django.conf import settings
from django.http import JsonResponse
# from django.contrib.auth import login 
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.views.generic import CreateView, FormView, TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SignUpForm, BookingForm
from .models import Booking


# ---------- Auth / Signup ----------

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = "/accounts/login/"

    def form_valid(self, form):
        response = super().form_valid(form)
        auth.login(self.request, self.object)
        return response


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return "/"  # go to home page after login


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("home")  # make sure you have a 'home' URL name


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
        kwargs["user"] = self.request.user  # pass logged-in user to form
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user  # ensure user is set
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
        # Fix: only query for logged-in user; LoginRequiredMixin prevents AnonymousUser
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


# ---------- Stripe ----------

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    service = request.POST.get("service", "boarding")
    prices = {"dog_walking": 3000, "grooming": 2500, "boarding": 3500}
    price = prices.get(service, 3000)

    try:
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
            success_url=request.build_absolute_uri("/success/"),
            cancel_url=request.build_absolute_uri("/cancel/"),
        )
        return JsonResponse({"id": session.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
