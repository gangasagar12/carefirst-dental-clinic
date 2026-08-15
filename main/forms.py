from django import forms
from .models import ContactMessage

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']

from django.contrib.auth import get_user_model

class OTPRequestForm(forms.Form):
    email = forms.EmailField(label='Email address', max_length=254)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()
        if not User.objects.filter(email=email, is_active=True).exists():
            # We don\'t raise an error to prevent email enumeration, 
            # we just handle it silently in the view.
            pass
        return email

class OTPVerifyForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput())
    otp = forms.CharField(label='6-Digit OTP', max_length=6, min_length=6)
