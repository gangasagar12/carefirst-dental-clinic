from django import forms
from .models import ContactMessage

class ContactMessageForm(forms.ModelForm):
    # 1. Honeypot Field (Invisible to human users, traps automated bots)
    website_url_check = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'style': 'display:none !important;',
            'tabindex': '-1',
            'autocomplete': 'off',
            'aria-hidden': 'true',
        })
    )

    # 2. Form Field Renaming (Anti-Bot Pattern)
    patient_message_content = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Tell us how we can help you...',
        })
    )

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject']

    def clean(self):
        cleaned_data = super().clean()
        
        # Honeypot validation: Any content in this field indicates an automated scraper/bot
        honeypot = cleaned_data.get('website_url_check', '').strip()
        if honeypot:
            raise forms.ValidationError("Automated submission detected. Your request was rejected.")

        # Anti-bot field mapping: Resolve patient_message_content into message
        message_body = (
            cleaned_data.get('patient_message_content', '').strip() or
            self.data.get('patient_message_content', '').strip() or
            self.data.get('message', '').strip()
        )
        if not message_body:
            self.add_error('patient_message_content', 'Please enter your message.')
        else:
            cleaned_data['message'] = message_body

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.message = self.cleaned_data.get('message', '')
        if commit:
            instance.save()
        return instance

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
