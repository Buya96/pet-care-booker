import stripe
import json

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, FormView, TemplateView, ListView
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .forms import SignUpForm, BookingForm
from .models import Booking


stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)


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


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"
    login_url = "login"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["bookings"] = Booking.objects.filter(user=self.request.user).order_by("-created")[:5]
        context['STRIPE_PUBLIC_KEY'] = getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')
        return context


def home(request):
    return render(request, "accounts/home.html")


def services(request):
    return render(request, "accounts/services.html")


class BookingView(LoginRequiredMixin, FormView):
    template_name = "accounts/booking.html"
    form_class = BookingForm
    login_url = "login"
    redirect_field_name = "next"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['STRIPE_PUBLIC_KEY'] = getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')
        
        # Pass latest unpaid booking for Pay button
        if self.request.user.is_authenticated:
            context['booking'] = Booking.objects.filter(
                user=self.request.user, 
                paid=False
            ).order_by('-created').first()
        return context

    def form_valid(self, form):
        booking = form.save(commit=False)
        booking.user = self.request.user
        booking.save()
        messages.success(self.request, f"Booking created for {booking.pet_name}!")
        return redirect('book')  # Stay on page with booking context


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


# STRIPE PAYMENT - PERFECTLY MATCHES FRONTEND
@csrf_exempt
@require_http_methods(["POST"])
def create_checkout_session(request):
    print("=== PAY HIT ===")
    
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Please log in first."}, status=401)

    try:
        data = json.loads(request.body.decode("utf-8"))
        service = data.get("service", "boarding")
        booking_id = data.get("booking_id")

        if not booking_id:
            return JsonResponse({"error": "Missing booking_id."}, status=400)

        # Get exact booking
        booking = get_object_or_404(
            Booking, 
            id=booking_id, 
            user=request.user, 
            paid=False
        )

        prices = {"dog_walking": 3000, "grooming": 2500, "boarding": 3500}
        price = prices.get(service, 3000)

        success_url = f"{request.build_absolute_uri('/accounts/payment-success/')}{booking.id}/"

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": f"{service.replace('_', ' ').title()} - {booking.pet_name}"
                    },
                    "unit_amount": price,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=request.build_absolute_uri("/accounts/book/"),
        )
        
        print(f"Pay session for booking {booking.id}: {session.id}")
        return JsonResponse({"url": session.url})  # ← Frontend uses this!
        
    except Exception as e:
        print(f"Pay error: {e}")
        return JsonResponse({"error": str(e)}, status=400)


# PAYMENT SUCCESS - MARK SPECIFIC BOOKING PAID
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if not booking.paid:
        booking.paid = True
        booking.save()
        messages.success(
            request,
            f"✅ Payment complete! '{booking.pet_name} - {booking.get_service_display()}' is now PAID."
        )
    else:
        messages.info(request, f"'{booking.pet_name}' already paid.")
    
    return redirect("bookings")
