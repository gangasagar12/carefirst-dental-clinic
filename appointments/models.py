import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from .utils import generate_booking_id, generate_secure_access_token

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending Confirmation')),
        ('confirmed', _('Confirmed')),
        ('checked_in', _('Patient Checked In / Arrived')),
        ('completed', _('Completed Visit')),
        ('rescheduled', _('Rescheduled')),
        ('cancelled', _('Cancelled')),
        ('no_show', _('No Show')),
        ('new', _('New Request')),
    ]

    LOYALTY_STATUS_CHOICES = [
        ('none', _('Not Applicable')),
        ('awaiting_verification', _('Awaiting Loyalty Verification')),
        ('verified', _('Loyalty Progress Granted (+1)')),
        ('not_eligible', _('Marked Not Eligible')),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Payment Pending')),
        ('paid', _('Payment Completed')),
        ('waived', _('Payment Waived / Free Checkup')),
    ]
    
    TIME_CHOICES = [
        ('', _('Flexible / Any Time')),
        ('morning', _('Morning (7:30 AM - 12:00 PM)')),
        ('afternoon', _('Afternoon (12:00 PM - 4:00 PM)')),
        ('evening', _('Evening (4:00 PM - 7:30 PM)')),
    ]

    TYPE_CHOICES = [
        ('consultation', _('Book a Consultation')),
        ('treatment', _('Direct Treatment Visit')),
        ('follow_up', _('Follow-up / Routine Check')),
        ('checkup', _('General Dental Check-up')),
    ]

    TREATMENT_CHOICES = [
        ('', _('General Dental Consultation')),
        ('scaling-and-polishing', _('Scaling & Polishing')),
        ('dental-filling', _('Dental Filling')),
        ('root-canal-treatment', _('Root Canal Treatment (RCT)')),
        ('tooth-extraction', _('Tooth Extraction & Wisdom Teeth')),
        ('dental-implants', _('Dental Implants')),
        ('orthodontic-treatment-braces', _('Braces & Clear Aligners')),
        ('teeth-whitening', _('Professional Teeth Whitening')),
        ('crowns-and-bridges', _('Crowns & Bridges / Veneers')),
        ('periodontal-treatment-gum', _('Gum Care & Periodontal Therapy')),
        ('dentures', _('Complete & Partial Dentures')),
        ('digital-dental-x-ray', _('Digital RVG Dental X-Ray')),
        ('other', _('Other / Unsure')),
    ]

    # Human-readable Unique Booking Reference ID
    booking_id = models.CharField(
        max_length=60, 
        unique=True, 
        null=True,
        blank=True, 
        db_index=True, 
        verbose_name=_("Booking Reference ID"),
        help_text=_("Human-readable unique reference e.g. CF-APT-20260902-A7X92")
    )

    # Cryptographically Secure Access Token (No predictable sequential IDs)
    access_token = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("Secure Access Token"),
        help_text=_("Cryptographically secure random token for patient access without login")
    )

    # Legacy reference compatibility field
    appointment_number = models.CharField(
        max_length=60, 
        unique=True, 
        null=True,
        blank=True, 
        db_index=True, 
        verbose_name=_("Appointment Request ID"),
        help_text=_("Legacy reference ID compatible with booking_id")
    )

    full_name = models.CharField(max_length=200, verbose_name=_("Full Name"))
    phone = models.CharField(max_length=30, verbose_name=_("Phone Number"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("Email Address"))
    
    appointment_type = models.CharField(
        max_length=40, 
        choices=TYPE_CHOICES, 
        default='consultation', 
        verbose_name=_("Appointment Type")
    )
    
    # Treatment association
    service = models.ForeignKey(
        'main.Service', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='appointments',
        verbose_name=_("Selected Service")
    )
    treatment = models.CharField(max_length=100, choices=TREATMENT_CHOICES, blank=True, verbose_name=_("Treatment Category"))
    pricing_option = models.CharField(max_length=150, blank=True, verbose_name=_("Pricing Option / Material"))
    quantity = models.PositiveSmallIntegerField(default=1, verbose_name=_("Tooth / Unit Quantity"))
    estimated_amount = models.CharField(max_length=100, blank=True, verbose_name=_("Informational Price Estimate"))

    # Preferred Date and Time
    preferred_date = models.DateField(verbose_name=_("Preferred Date"))
    preferred_time = models.CharField(max_length=50, choices=TIME_CHOICES, blank=True, verbose_name=_("Preferred Time Slot"))
    
    doctor = models.ForeignKey('main.Doctor', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Preferred Doctor"))
    branch = models.ForeignKey('main.Branch', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Preferred Branch"))
    
    message = models.TextField(blank=True, verbose_name=_("Patient Notes / Special Requirements"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True, verbose_name=_("Status"))

    # Marketing Attribution & Tracking
    utm_source = models.CharField(max_length=100, blank=True, verbose_name=_("UTM Source"))
    utm_medium = models.CharField(max_length=100, blank=True, verbose_name=_("UTM Medium"))
    utm_campaign = models.CharField(max_length=100, blank=True, verbose_name=_("UTM Campaign"))
    utm_content = models.CharField(max_length=100, blank=True, verbose_name=_("UTM Content"))
    utm_term = models.CharField(max_length=100, blank=True, verbose_name=_("UTM Term"))
    landing_page = models.CharField(max_length=500, blank=True, verbose_name=_("Landing Page URL"))
    referrer = models.CharField(max_length=500, blank=True, verbose_name=_("Referrer URL"))
    chat_used = models.BooleanField(default=False, verbose_name=_("Booked via AI Chatbot"))
    estimator_used = models.BooleanField(default=False, verbose_name=_("Booked via Cost Estimator"))

    # Staff Rescheduling & Internal Management
    original_date = models.DateField(null=True, blank=True, verbose_name=_("Original Requested Date"))
    original_time = models.CharField(max_length=50, blank=True, verbose_name=_("Original Requested Time"))
    reschedule_reason = models.CharField(max_length=255, blank=True, verbose_name=_("Reschedule Reason"))
    internal_note = models.TextField(blank=True, verbose_name=_("Staff Internal Notes (Hidden from Patient)"))
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Confirmed At"))
    checked_in_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Checked In At"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed At"))

    # Human-Verified Loyalty & Payment Workflow
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending', 
        db_index=True, 
        verbose_name=_("Payment Status")
    )
    loyalty_status = models.CharField(
        max_length=30, 
        choices=LOYALTY_STATUS_CHOICES, 
        default='none', 
        db_index=True, 
        verbose_name=_("Loyalty Verification Status")
    )
    loyalty_verified_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Loyalty Verified At"))
    loyalty_verified_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_appointments', 
        verbose_name=_("Loyalty Verified By")
    )
    loyalty_rejection_reason = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name=_("Loyalty Ineligibility Reason")
    )

    # Automated 24-Hour & Communication Reminder Tracking
    reminder_sent = models.BooleanField(default=False, db_index=True, verbose_name=_("24h Reminder Sent"))
    reminder_sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Reminder Sent At"))
    reminder_channel = models.CharField(max_length=50, blank=True, default='email', verbose_name=_("Reminder Channel"))
    reminder_count = models.PositiveIntegerField(default=0, verbose_name=_("Total Reminders Sent"))

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated Update At"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Appointment")
        verbose_name_plural = _("All Appointments")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not self.booking_id:
            self.booking_id = generate_booking_id()
        if not self.access_token:
            self.access_token = generate_secure_access_token()
        if not self.appointment_number:
            self.appointment_number = self.booking_id

        super().save(*args, **kwargs)

    @property
    def display_booking_id(self) -> str:
        return self.booking_id or self.appointment_number or f"CF-APT-{self.id:06d}"

    def get_manage_url(self) -> str:
        token = self.access_token or self.booking_id or str(self.id)
        try:
            return reverse('appointments:manage', kwargs={'access_token': token})
        except Exception:
            return f"/appointment/manage/{token}/"

    def get_confirmation_url(self) -> str:
        token = self.access_token or self.booking_id or str(self.id)
        try:
            return reverse('appointments:confirmation', kwargs={'access_token': token})
        except Exception:
            return f"/appointment/confirmation/{token}/"

    def get_pdf_url(self) -> str:
        token = self.access_token or self.booking_id or str(self.id)
        try:
            return reverse('appointments:download_pdf', kwargs={'access_token': token})
        except Exception:
            return f"/appointment/manage/{token}/pdf/"

    def get_calendar_ics_url(self) -> str:
        token = self.access_token or self.booking_id or str(self.id)
        try:
            return reverse('appointments:calendar_ics', kwargs={'access_token': token})
        except Exception:
            return f"/appointment/manage/{token}/calendar.ics"

    def get_status_badge_class(self) -> str:
        mapping = {
            'pending': 'bg-warning text-dark border border-warning',
            'confirmed': 'bg-success text-white',
            'checked_in': 'bg-info text-white',
            'completed': 'bg-primary text-white',
            'rescheduled': 'bg-primary-subtle text-primary border border-primary',
            'cancelled': 'bg-danger text-white',
            'no_show': 'bg-secondary text-white',
            'new': 'bg-warning text-dark',
        }
        return mapping.get(self.status, 'bg-secondary text-white')

    def get_status_explanation(self) -> str:
        if self.status in ['pending', 'new']:
            return _("Your appointment request has been received. Our team will review and confirm your appointment shortly.")
        elif self.status == 'confirmed':
            return _("Your appointment has been confirmed! Please arrive approximately 10 minutes before your scheduled slot.")
        elif self.status == 'checked_in':
            return _("Patient is checked in at the clinic reception.")
        elif self.status == 'completed':
            return _("This clinical treatment visit has been completed.")
        elif self.status == 'rescheduled':
            return _("Your appointment has been rescheduled. Please note your updated time slot.")
        elif self.status == 'cancelled':
            return _("This appointment request has been cancelled.")
        return _("Appointment logged in clinical registry.")

    def __str__(self):
        ref = self.display_booking_id
        return f"[{ref}] {self.full_name} - {self.preferred_date} ({self.get_status_display()})"


class AppointmentFunnelEvent(models.Model):
    EVENT_CHOICES = [
        ('STARTED', _('Funnel Started')),
        ('TREATMENT_SELECTED', _('Treatment Selected')),
        ('TYPE_SELECTED', _('Appointment Type Selected')),
        ('DATE_SELECTED', _('Date Selected')),
        ('TIME_SELECTED', _('Time Selected')),
        ('DETAILS_STARTED', _('Patient Details Form Started')),
        ('REVIEW_VIEWED', _('Summary Review Viewed')),
        ('SUBMITTED', _('Successfully Submitted')),
        ('ABANDONED', _('Funnel Abandoned')),
        ('CONFIRMED', _('Confirmed by Staff')),
        ('CANCELLED', _('Cancelled')),
        ('COMPLETED', _('Completed Visit')),
    ]

    session_id = models.CharField(max_length=255, db_index=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='funnel_events')
    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES, db_index=True)
    treatment_slug = models.CharField(max_length=150, blank=True)
    source = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Funnel Event")
        verbose_name_plural = _("Funnel Events")

    def __str__(self):
        return f"{self.event_type} ({self.session_id[:8]}) at {self.created_at.strftime('%H:%M')}"


class InquiriesDashboard(Appointment):
    class Meta:
        proxy = True
        verbose_name = _("Inquiries Dashboard")
        verbose_name_plural = _("Inquiries Dashboard")


class WhatsAppNotification(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('failed', _('Failed')),
    ]
    inquiry_type = models.CharField(max_length=50, verbose_name=_("Inquiry Type"))
    inquiry_id = models.IntegerField(verbose_name=_("Inquiry ID"))
    patient_name = models.CharField(max_length=200, verbose_name=_("Patient Name"))
    phone_number = models.CharField(max_length=50, verbose_name=_("Phone Number"))
    message_text = models.TextField(verbose_name=_("Message Text"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Status"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("WhatsApp Notification")
        verbose_name_plural = _("WhatsApp Notifications")

    def __str__(self):
        return f"{self.patient_name} - {self.status}"


class EmailNotification(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('failed', _('Failed')),
    ]
    inquiry_type = models.CharField(max_length=50, verbose_name=_("Inquiry Type"))
    inquiry_id = models.IntegerField(verbose_name=_("Inquiry ID"))
    patient_name = models.CharField(max_length=200, verbose_name=_("Patient Name"))
    email_address = models.EmailField(verbose_name=_("Email Address"))
    subject = models.CharField(max_length=255, verbose_name=_("Subject"))
    message_text = models.TextField(verbose_name=_("Message Text"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Status"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Email Notification")
        verbose_name_plural = _("Email Notifications")

    def __str__(self):
        return f"{self.patient_name} - {self.status}"