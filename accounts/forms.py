# Custom sign up form and bootstrap integration
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class SignUpForm(UserCreationForm):
    phone = forms.CharField(max_length=20, required=False, label="Phone (optional)")
    address = forms.CharField(widget=forms.Textarea, required=False, label="Address")

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'address', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('username', css_class='form-control mb-3'),
            Field('email', css_class='form-control mb-3'),
            Field('phone', css_class='form-control mb-3'),
            Field('address', css_class='form-control mb-3'),
            Field('password1', css_class='form-control mb-3'),
            Field('password2', css_class='form-control mb-3'),
            Submit('submit', 'Create Account', css_class='btn btn-primary w-100'),
        )

def save(self, commit=True):
    user = super().save(commit=False)
    user.email = self.cleaned_data['email']
    if commit:
        user.save()
        # Check if profile exists first
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone': self.cleaned_data['phone'],
                'address': self.cleaned_data['address']
            }
        )
    return user
