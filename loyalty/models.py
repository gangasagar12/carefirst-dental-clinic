import secrets
import string
import re
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def normalize_phone(phone_str):
    """
    Strips non-digit characters and normalizes phone numbers.
    e.g., '+977 980-7464136' -> '9807464136' or '9779807464136'
    """
    if not phone_str:
        return ""
    digits = re.sub(r'\D', '', str(phone_str))
    if len(digits) == 13 and digits.startswith('977'):
        digits = digits[3:]
    elif len(digits) == 12 and digits.startswith('977'):
        digits = digits[3:]
    return digits


def generate_reward_reference():
    """Generates an alphanumeric reward reference code e.g. CF-RWD-7A92"""
    chars = string.ascii_uppercase + string.digits
    random_str = ''.join(secrets.choice(chars) for _ in range(5))
    return f"CF-RWD-{random_str}"


class LoyaltyProgram(models.Model):
    """
    Configurable Loyalty & Rewards Program rules.
    Default: CareFirst Smile Rewards (3 completed treatments -> 10% OFF reward valid for 60 days).
    """
    REWARD_TYPE_CHOICES = [
        ('percentage', _('Percentage Discount (e.g. 10% OFF)')),
        ('fixed_amount', _('Fixed Amount Discount (e.g. NPR 1,000 OFF)')),
        ('free_service', _('Free Preventive Service / Checkup')),
    ]

    name = models.CharField(max_length=150, default="CareFirst Smile Rewards", verbose_name=_("Program Name"))
    tagline = models.CharField(max_length=255, default="Your care deserves a little extra.", verbose_name=_("Program Tagline"))
    description = models.TextField(
        blank=True,
        default="Complete eligible dental visits and unlock exclusive savings on your care without any app or membership cards required.",
        verbose_name=_("Description")
    )

    # Threshold & Reward Configuration
    required_completed_treatments = models.PositiveIntegerField(
        default=3,
        verbose_name=_("Required Completed Visits"),
        help_text=_("Number of eligible completed treatments needed to unlock a reward (e.g. 3)")
    )
    reward_type = models.CharField(
        max_length=30,
        choices=REWARD_TYPE_CHOICES,
        default='percentage',
        verbose_name=_("Reward Type")
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        verbose_name=_("Discount Percentage (%)"),
        help_text=_("Percentage discount given when reward is unlocked (e.g. 10.00)")
    )
    fixed_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Fixed Discount Amount (NPR)"),
        help_text=_("Used if reward type is fixed amount")
    )
    maximum_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Maximum Discount Cap (NPR)"),
        help_text=_("Set to 0 for unlimited discount")
    )
    expiry_days = models.PositiveIntegerField(
        default=60,
        verbose_name=_("Reward Validity Period (Days)"),
        help_text=_("Number of days unlocked rewards remain valid before expiring")
    )

    # Service Eligibility Controls
    allow_all_services_by_default = models.BooleanField(
        default=True,
        verbose_name=_("All Services Eligible by Default"),
        help_text=_("If checked, all clinic services count towards rewards unless explicitly excluded.")
    )
    eligible_services = models.ManyToManyField(
        'main.Service',
        blank=True,
        related_name='eligible_loyalty_programs',
        verbose_name=_("Explicitly Eligible Services")
    )
    excluded_services = models.ManyToManyField(
        'main.Service',
        blank=True,
        related_name='excluded_loyalty_programs',
        verbose_name=_("Excluded Services / Materials")
    )
    allow_consultations_eligible = models.BooleanField(
        default=False,
        verbose_name=_("Count Free/Basic Consultations as Eligible Visits"),
        help_text=_("Usually set to False to count only clinical treatment visits.")
    )

    # Status
    is_active = models.BooleanField(default=True, verbose_name=_("Program Active Status"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Loyalty Program")
        verbose_name_plural = _("Loyalty Programs")

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.name} ({self.required_completed_treatments} Visits → {self.get_reward_label()}) [{status}]"

    def get_reward_label(self):
        if self.reward_type == 'percentage':
            return f"{self.discount_percentage:.0f}% OFF"
        elif self.reward_type == 'fixed_amount':
            return f"NPR {self.fixed_discount_amount:.0f} OFF"
        return _("Complimentary Service")

    @classmethod
    def get_active_program(cls):
        """Returns the primary active loyalty program or creates default."""
        program = cls.objects.filter(is_active=True).first()
        if not program:
            program = cls.objects.create(
                name="CareFirst Smile Rewards",
                tagline="Your care deserves a little extra.",
                required_completed_treatments=3,
                reward_type='percentage',
                discount_percentage=10.00,
                expiry_days=60,
                is_active=True
            )
        return program


class PatientLoyaltyProfile(models.Model):
    """
    Central Patient Loyalty Profile linked by verified Phone Number.
    Requires NO patient account/login. Staff searches phone number at reception.
    """
    patient_id = models.CharField(max_length=50, blank=True, null=True, db_index=True, verbose_name=_("Patient ID"))
    phone = models.CharField(max_length=30, db_index=True, verbose_name=_("Registered Phone Number"))
    normalized_phone = models.CharField(max_length=30, db_index=True, verbose_name=_("Normalized Phone"))
    full_name = models.CharField(max_length=200, verbose_name=_("Patient Full Name"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("Email Address"))

    program = models.ForeignKey(
        LoyaltyProgram,
        on_delete=models.CASCADE,
        related_name='patient_profiles',
        verbose_name=_("Enrolled Program")
    )

    # Realtime Progress Tracking
    current_progress = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Current Cycle Progress"),
        help_text=_("Current count of completed eligible treatments in active cycle (e.g. 1 of 3)")
    )
    current_cycle = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Current Reward Cycle"),
        help_text=_("Increments every time a reward is unlocked (e.g. Cycle 1, Cycle 2)")
    )
    total_completed_eligible_treatments = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Lifetime Completed Treatments")
    )
    total_rewards_earned = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Rewards Earned")
    )
    total_rewards_redeemed = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Rewards Redeemed")
    )

    notes = models.TextField(blank=True, verbose_name=_("Reception / Internal Notes"))
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['normalized_phone', 'program'], name='unique_patient_per_loyalty_program')
        ]
        ordering = ['-updated_at']
        verbose_name = _("Patient Loyalty Profile")
        verbose_name_plural = _("Patient Loyalty Profiles")

    def save(self, *args, **kwargs):
        self.normalized_phone = normalize_phone(self.phone)
        if not self.patient_id:
            # Auto-assign patient ID if empty
            count = PatientLoyaltyProfile.objects.count() + 1
            self.patient_id = f"CF-PAT-{count:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.phone}) - {self.current_progress}/{self.program.required_completed_treatments}"

    @property
    def progress_dots(self):
        """Returns visual list of progress states e.g. [True, True, False] for 2/3"""
        required = self.program.required_completed_treatments
        return [i < self.current_progress for i in range(required)]

    @property
    def progress_fraction(self):
        return f"{self.current_progress} / {self.program.required_completed_treatments}"

    @property
    def progress_percentage(self):
        if self.program.required_completed_treatments > 0:
            pct = (self.current_progress / self.program.required_completed_treatments) * 100
            return min(int(pct), 100)
        return 0

    def active_rewards(self):
        """Returns valid, unexpired available rewards."""
        now = timezone.now()
        return self.rewards.filter(status='available', expires_at__gt=now).order_by('expires_at')

    def has_available_reward(self):
        return self.active_rewards().exists()


class LoyaltyTransaction(models.Model):
    """
    Immutable audit ledger for every loyalty action.
    Strict database constraint guarantees the same appointment NEVER generates duplicate progress.
    """
    TRANSACTION_TYPES = [
        ('treatment_completed', _('Eligible Treatment Completed (+1 Progress)')),
        ('reward_unlocked', _('Reward Unlocked (Cycle Reset)')),
        ('reward_applied', _('Reward Applied to Invoice')),
        ('reward_expired', _('Reward Expired')),
        ('reward_cancelled', _('Reward Cancelled / Overridden')),
        ('admin_adjustment', _('Staff Manual Adjustment')),
    ]

    patient = models.ForeignKey(
        PatientLoyaltyProfile,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_("Patient Profile")
    )
    program = models.ForeignKey(
        LoyaltyProgram,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_("Program")
    )
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='loyalty_transactions',
        verbose_name=_("Related Appointment")
    )
    service = models.ForeignKey(
        'main.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Clinical Service")
    )
    treatment_name = models.CharField(max_length=200, blank=True, verbose_name=_("Treatment Description"))
    invoice_reference = models.CharField(max_length=100, blank=True, verbose_name=_("Invoice / Receipt Ref"))
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Amount Paid (NPR)"))

    transaction_type = models.CharField(max_length=40, choices=TRANSACTION_TYPES, verbose_name=_("Action Type"))
    progress_added = models.IntegerField(default=0, verbose_name=_("Progress Added (+/-)"))
    notes = models.TextField(blank=True, verbose_name=_("Audit Notes"))

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Staff User")
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Loyalty Transaction")
        verbose_name_plural = _("Loyalty Transactions")

    def __str__(self):
        return f"[{self.get_transaction_type_display()}] {self.patient.full_name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class LoyaltyReward(models.Model):
    """
    Unlocked reward record securely linked to patient's verified phone number.
    Redeemed directly at reception without coupon memorization.
    """
    STATUS_CHOICES = [
        ('available', _('Available (Ready for Use)')),
        ('applied', _('Applied to Invoice')),
        ('expired', _('Expired')),
        ('cancelled', _('Cancelled by Staff')),
    ]

    patient = models.ForeignKey(
        PatientLoyaltyProfile,
        on_delete=models.CASCADE,
        related_name='rewards',
        verbose_name=_("Patient Profile")
    )
    program = models.ForeignKey(
        LoyaltyProgram,
        on_delete=models.CASCADE,
        related_name='rewards',
        verbose_name=_("Program")
    )
    reward_reference = models.CharField(
        max_length=50,
        unique=True,
        default=generate_reward_reference,
        db_index=True,
        verbose_name=_("Reward Reference ID")
    )

    reward_type = models.CharField(max_length=30, choices=LoyaltyProgram.REWARD_TYPE_CHOICES, default='percentage')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, verbose_name=_("Discount %"))
    fixed_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Fixed Discount (NPR)"))
    maximum_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Max Discount Cap (NPR)"))

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', db_index=True, verbose_name=_("Status"))
    unlocked_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Unlocked At"))
    expires_at = models.DateTimeField(db_index=True, verbose_name=_("Expires At"))

    # Redemption Tracking
    used_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Redeemed At"))
    applied_invoice_ref = models.CharField(max_length=100, blank=True, verbose_name=_("Applied Invoice / Bill Ref"))
    discount_amount_applied = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Calculated Discount (NPR)"))
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='redeemed_loyalty_rewards',
        verbose_name=_("Staff Who Applied Reward")
    )
    cancellation_reason = models.TextField(blank=True, verbose_name=_("Cancellation / Override Reason"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-unlocked_at']
        verbose_name = _("Loyalty Reward")
        verbose_name_plural = _("Loyalty Rewards")

    def __str__(self):
        return f"{self.reward_reference} - {self.patient.full_name} ({self.get_reward_display()}) [{self.get_status_display()}]"

    def get_reward_display(self):
        if self.reward_type == 'percentage':
            return f"{self.discount_percentage:.0f}% OFF"
        elif self.reward_type == 'fixed_amount':
            return f"NPR {self.fixed_discount_amount:.0f} OFF"
        return _("Free Preventive Treatment")

    @property
    def is_valid(self):
        return self.status == 'available' and self.expires_at > timezone.now()

    @property
    def days_remaining(self):
        if not self.is_valid:
            return 0
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)


class LoyaltyNotificationLog(models.Model):
    """
    Audit log for proactive multi-channel communications (Email, WhatsApp, SMS).
    """
    CHANNEL_CHOICES = [
        ('email', _('Email Notification')),
        ('whatsapp', _('WhatsApp Message')),
        ('sms', _('SMS Text')),
    ]
    EVENT_CHOICES = [
        ('progress_update', _('Progress Update (1/3, 2/3)')),
        ('reward_unlocked', _('Reward Unlocked (3/3)')),
        ('reward_applied', _('Reward Redeemed Confirmation')),
        ('reward_reminder', _('Reward Expiry Reminder')),
    ]
    STATUS_CHOICES = [
        ('sent', _('Sent Successfully')),
        ('pending', _('Pending / Queued')),
        ('failed', _('Failed')),
    ]

    patient = models.ForeignKey(
        PatientLoyaltyProfile,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_("Patient Profile")
    )
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, db_index=True)
    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES, db_index=True)
    recipient = models.CharField(max_length=150, verbose_name=_("Recipient (Phone / Email)"))
    subject = models.CharField(max_length=255, blank=True, verbose_name=_("Subject"))
    message_body = models.TextField(verbose_name=_("Message Content"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, verbose_name=_("Error Details (if failed)"))
    sent_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = _("Loyalty Notification Log")
        verbose_name_plural = _("Loyalty Notification Logs")

    def __str__(self):
        return f"[{self.get_channel_display()}] {self.patient.full_name} - {self.get_event_type_display()} ({self.status})"
