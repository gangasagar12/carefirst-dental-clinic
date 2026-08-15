
from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['full_name', 'phone', 'email', 'preferred_date', 'preferred_time', 'treatment', 'doctor', 'branch', 'message']
