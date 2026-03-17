import stripe
import json  # for JSON body parsing

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth import login  # needed for SignUpView
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
        # Create & save Booking first
        booking = form.save(commit=False)
        booking.user = self.request.user
        booking.save()
        
        # Store booking.pk in session for checkout (webhook will use metadata)
        self.request.session['pending_booking_id'] = booking.pk
        
        # Redirect to same page but trigger Stripe checkout
        return redirect('pay')  # Assumes /pay/ URL exists

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

# ---------- STRIPE ----------
@csrf_exempt
@require_http_methods(["POST"])
def create_checkout_session(request):
    try:
        # Parse JSON body from JS fetch()
        data = json.loads(request.body.decode("utf-8"))
        service = data.get("service", "boarding")
        
        prices = {"dog_walking": 3000, "grooming": 2500, "boarding": 3500}
        price = prices.get(service, 3000)

        # Get pending booking ID from session
        booking_id = request.session.get('pending_booking_id')
        if not booking_id:
            return JsonResponse({"error": "No booking found"}, status=400)

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
            success_url=request.build_absolute_uri("/profile/"),
            cancel_url=request.build_absolute_uri("/book/"),
            metadata={'booking_id': str(booking_id)},  # Key: pass booking ID to webhook
        )
        return JsonResponse({"id": session.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)  # Fixed syntax

# ---------- STRIPE WEBHOOK ----------
@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        booking_id = session.metadata.get('booking_id')
        if booking_id:
            booking = Booking.objects.get(id=int(booking_id), user=request.user)  # Secure: filter by user if possible
            booking.paid = True
            booking.save()
            print(f"Booking {booking_id} marked as paid!")  # For logs

    return HttpResponse(status=200)
