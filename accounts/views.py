import json
import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, FormView, TemplateView, ListView
from django.views.generic.edit import UpdateView, DeleteView

from .forms import SignUpForm, BookingForm
from .models import Booking

stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = "/login/"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

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
        context["STRIPE_PUBLIC_KEY"] = getattr(settings, "STRIPE_PUBLISHABLE_KEY", "")
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

    def get_booking_from_query(self):
        booking_id = self.request.GET.get("booking_id")
        if not booking_id:
            return None
        return Booking.objects.filter(
            id=booking_id,
            user=self.request.user,
        ).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["STRIPE_PUBLIC_KEY"] = getattr(settings, "STRIPE_PUBLISHABLE_KEY", "")
        context["booking"] = self.get_booking_from_query()
        return context

    def form_valid(self, form):
        booking = form.save(commit=False)
        booking.user = self.request.user
        booking.save()
        messages.success(self.request, f"Booking created for {booking.pet_name}!")
        book_url = reverse("book")
        return redirect(f"{book_url}?booking_id={booking.id}")


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
        messages.success(self.request, "Booking updated successfully.")
        return reverse_lazy("bookings")


class BookingDeleteView(LoginRequiredMixin, DeleteView):
    model = Booking
    template_name = "accounts/booking_confirm_delete.html"
    login_url = "login"
    redirect_field_name = "next"

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Booking deleted successfully.")
        return reverse_lazy("bookings")


@csrf_exempt
@require_http_methods(["POST"])
def create_checkout_session(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Please log in first."}, status=401)

    try:
        data = json.loads(request.body.decode("utf-8"))
        service = data.get("service", "boarding")
        booking_id = data.get("booking_id")

        if not booking_id:
            return JsonResponse({"error": "Missing booking_id."}, status=400)

        booking = get_object_or_404(
            Booking,
            id=booking_id,
            user=request.user,
            paid=False
        )

        prices = {
            "dog_walking": 3000,
            "grooming": 2500,
            "boarding": 3500,
        }
        price = prices.get(service, 3000)

        success_url = request.build_absolute_uri(
            reverse("payment-success", args=[booking.id])
        )
        cancel_url = request.build_absolute_uri(
            reverse("payment-cancelled", args=[booking.id])
        )

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "gbp",
                        "product_data": {
                            "name": f"{service.replace('_', ' ').title()} - {booking.pet_name}"
                        },
                        "unit_amount": price,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "booking_id": str(booking.id),
                "user_id": str(request.user.id),
                "service": service,
            },
        )

        booking.stripe_payment_intent = session.id
        booking.amount_paid = price / 100
        booking.save(update_fields=["stripe_payment_intent", "amount_paid"])

        return JsonResponse({"url": session.url})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.paid:
        messages.success(request, f"Payment complete for {booking.pet_name}.")
    else:
        messages.info(
            request,
            f"Payment submitted for {booking.pet_name}. Your booking will update after Stripe confirms it."
        )

    return redirect("bookings")


@login_required
def payment_cancelled(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    messages.warning(
        request,
        f"Payment was cancelled for {booking.pet_name}. Your booking has not been marked as paid."
    )
    return redirect(f"{reverse('book')}?booking_id={booking.id}")


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", None)

    if not endpoint_secret:
        return HttpResponse("Webhook secret not configured.", status=500)

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=endpoint_secret,
        )
    except ValueError:
        return HttpResponse("Invalid payload.", status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse("Invalid signature.", status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        booking_id = session.get("metadata", {}).get("booking_id")

        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)

                if not booking.paid:
                    booking.paid = True
                    booking.stripe_payment_intent = session.get("id")

                    amount_total = session.get("amount_total")
                    if amount_total is not None:
                        booking.amount_paid = amount_total / 100

                    booking.save()
            except Booking.DoesNotExist:
                pass

    return HttpResponse(status=200)