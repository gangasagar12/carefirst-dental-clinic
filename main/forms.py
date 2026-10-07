from django import forms
from .models import ContactMessage
from main.services.spam_filter import is_spam_submission

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

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        is_spam, reason = is_spam_submission(name=name)
        if is_spam:
            raise forms.ValidationError("Invalid name format. Please enter a valid name.")
        return name

    def clean(self):
        cleaned_data = super().clean()
        
        # 1. Honeypot check: Any content traps bots
        honeypot = cleaned_data.get('website_url_check', '').strip()
        if honeypot:
            raise forms.ValidationError("Automated submission detected.")

        # 2. Resolve message content
        message_body = (
            cleaned_data.get('patient_message_content', '').strip() or
            self.data.get('patient_message_content', '').strip()
        )
        # If renamed field is empty but bot submitted legacy 'message' field
        if not message_body and self.data.get('message', '').strip():
            # Bot bypass attempt targeting raw 'message'
            legacy_msg = self.data.get('message', '').strip()
            is_spam, _ = is_spam_submission(message=legacy_msg)
            if is_spam:
                raise forms.ValidationError("Invalid message content.")
            message_body = legacy_msg

        if not message_body:
            self.add_error('patient_message_content', 'Please enter your message.')
            return cleaned_data

        # 3. Comprehensive content spam validation
        name = cleaned_data.get('name', '')
        email = cleaned_data.get('email', '')
        subject = cleaned_data.get('subject', '')
        is_spam, reason = is_spam_submission(name=name, email=email, message=message_body, subject=subject)
        if is_spam:
            raise forms.ValidationError(f"Your message could not be processed: {reason}")

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
