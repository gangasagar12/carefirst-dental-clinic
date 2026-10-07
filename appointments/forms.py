
from django import forms
from .models import Appointment
from main.services.spam_filter import is_spam_submission

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['full_name', 'phone', 'email', 'preferred_date', 'preferred_time', 'treatment', 'doctor', 'branch', 'message']

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        is_spam, reason = is_spam_submission(name=full_name)
        if is_spam:
            raise forms.ValidationError("Invalid name format.")
        return full_name

    def clean_message(self):
        msg = self.cleaned_data.get('message', '').strip()
        if msg:
            is_spam, reason = is_spam_submission(message=msg)
            if is_spam:
                raise forms.ValidationError("Invalid message content.")
        return msg
