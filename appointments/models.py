from django.db import models
from django.utils.translation import gettext_lazy as _

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('cancelled', _('Cancelled')),
        ('completed', _('Completed')),
    ]
    
    TIME_CHOICES = [
        ('', _('Any Time')),
        ('morning', _('Morning (9AM - 12PM)')),
        ('afternoon', _('Afternoon (12PM - 4PM)')),
        ('evening', _('Evening (4PM - 7PM)')),
    ]

    TREATMENT_CHOICES = [
        ('', _('General Check-up & Consultation')),
        ('cleaning', _('Scaling & Polishing')),
        ('filling', _('Dental Filling')),
        ('rct', _('Root Canal Treatment')),
        ('extraction', _('Tooth Extraction')),
        ('implants', _('Dental Implants')),
        ('braces', _('Braces / Orthodontics')),
        ('other', _('Other / Not Sure')),
    ]

    full_name = models.CharField(max_length=200, verbose_name=_("Full Name"))
    phone = models.CharField(max_length=20, verbose_name=_("Phone Number"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("Email Address"))
    preferred_date = models.DateField(verbose_name=_("Preferred Date"))
    preferred_time = models.CharField(max_length=50, choices=TIME_CHOICES, blank=True, verbose_name=_("Preferred Time"))
    treatment = models.CharField(max_length=50, choices=TREATMENT_CHOICES, blank=True, verbose_name=_("Treatment"))
    
    doctor = models.ForeignKey('main.Doctor', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Preferred Doctor"))
    branch = models.ForeignKey('main.Branch', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Preferred Branch"))
    
    message = models.TextField(blank=True, verbose_name=_("Message / Special Requirements"))
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Status"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Appointment")
        verbose_name_plural = _("All Appointments")

    def __str__(self):
        return f"{self.full_name} - {self.preferred_date}"

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
