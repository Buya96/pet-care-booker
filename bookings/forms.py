from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from accounts.models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["service", "pet_name", "date", "time", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.user = user
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "service", "pet_name", "date", "time", "notes",
            Submit("submit", "Book Now", css_class="btn btn-success w-100 mt-3")
        )

    def save(self, commit=True):
        booking = super().save(commit=False)
        booking.user = self.user
        if commit:
            booking.save()
        return booking