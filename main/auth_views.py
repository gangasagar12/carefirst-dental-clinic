import random
import string
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.views.generic.edit import FormView
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.views.generic import TemplateView

from .models import PasswordResetOTP
from .forms import OTPRequestForm, OTPVerifyForm

User = get_user_model()

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

class OTPRequestView(FormView):
    template_name = 'registration/password_reset_form.html'
    form_class = OTPRequestForm
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        users = User.objects.filter(email=email, is_active=True)
        
        if users.exists():
            user = users.first()
            otp_code = generate_otp()
            
            # Save OTP to database
            PasswordResetOTP.objects.create(user=user, otp=otp_code)
            
            # Send Email
            subject = "Your Password Reset OTP"
            message = f"Hello {user.username},\n\nYour 6-digit OTP for password reset is: {otp_code}\n\nThis OTP is valid for 10 minutes.\nIf you did not request this, please ignore this email."
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,
            )
            
        # Store email in session to pre-fill the verify form
        self.request.session['reset_email'] = email
        return super().form_valid(form)

class OTPVerifyView(FormView):
    template_name = 'registration/password_reset_done.html'
    form_class = OTPVerifyForm
    success_url = reverse_lazy('password_reset_confirm')

    def get_initial(self):
        initial = super().get_initial()
        initial['email'] = self.request.session.get('reset_email', '')
        return initial

    def form_valid(self, form):
        email = form.cleaned_data['email']
        otp_code = form.cleaned_data['otp']
        
        users = User.objects.filter(email=email, is_active=True)
        if users.exists():
            user = users.first()
            otp_record = PasswordResetOTP.objects.filter(user=user, otp=otp_code).order_by('-created_at').first()
            
            if otp_record and otp_record.is_valid():
                otp_record.is_used = True
                otp_record.save()
                
                # Mark session as verified
                self.request.session['otp_verified_email'] = email
                return super().form_valid(form)
                
        # If we reach here, OTP was invalid
        form.add_error('otp', 'Invalid or expired OTP.')
        return self.form_invalid(form)

class OTPPasswordResetConfirmView(FormView):
    template_name = 'registration/password_reset_confirm.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('password_reset_complete')

    def dispatch(self, request, *args, **kwargs):
        self.reset_email = request.session.get('otp_verified_email')
        if not self.reset_email:
            # If not verified, redirect to request
            return redirect('admin_password_reset')
            
        self.reset_user = User.objects.filter(email=self.reset_email, is_active=True).first()
        if not self.reset_user:
            return redirect('admin_password_reset')
            
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.reset_user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['validlink'] = True
        return context

    def form_valid(self, form):
        form.save()
        # Clear session
        if 'reset_email' in self.request.session:
            del self.request.session['reset_email']
        if 'otp_verified_email' in self.request.session:
            del self.request.session['otp_verified_email']
        return super().form_valid(form)

class OTPPasswordResetCompleteView(TemplateView):
    template_name = 'registration/password_reset_complete.html'
