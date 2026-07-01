from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, ListView
from django.views.generic.edit import UpdateView, DeleteView
from django.conf import settings

from accounts.models import Booking
from .forms import BookingForm


class BookingView(LoginRequiredMixin, FormView):
    template_name = "bookings/booking.html"
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
    template_name = "bookings/bookings.html"
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
    template_name = "bookings/booking_form.html"
    login_url = "login"
    redirect_field_name = "next"

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Booking updated successfully.")
        return reverse_lazy("bookings")


class BookingDeleteView(LoginRequiredMixin, DeleteView):
    model = Booking
    template_name = "bookings/booking_confirm_delete.html"
    login_url = "login"
    redirect_field_name = "next"

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Booking deleted successfully.")
        return reverse_lazy("bookings")
