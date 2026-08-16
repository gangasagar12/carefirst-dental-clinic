import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Conversation(models.Model):
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('closed', _('Closed')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=255, db_index=True, help_text="Browser session or unique client token")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_conversations')
    title = models.CharField(max_length=255, blank=True, default="New Consultation")
    current_page = models.CharField(max_length=500, blank=True, default="/")
    current_treatment = models.CharField(max_length=150, blank=True, help_text="Slug or title of treatment being viewed")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index=True)
    
    # Marketing UTM & Analytics tracking
    landing_page = models.CharField(max_length=500, blank=True)
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    utm_content = models.CharField(max_length=100, blank=True)
    utm_term = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = _("Conversation")
        verbose_name_plural = _("Conversations")

    def __str__(self):
        return f"Chat {str(self.id)[:8]} ({self.current_treatment or 'General'})"


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', _('Patient / Visitor')),
        ('assistant', _('CareFirst Assistant')),
        ('system', _('System Safety / Notification')),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    content = models.TextField(help_text="Message body (safe sanitized markdown or text)")
    intent = models.CharField(max_length=100, blank=True, db_index=True, help_text="Detected intent category")
    
    # Structured response components
    quick_actions = models.JSONField(blank=True, default=list, help_text="List of quick suggestion action buttons")
    cards = models.JSONField(blank=True, default=list, help_text="Structured cards (Treatment, Pricing Estimate, WhatsApp, Appointment)")
    metadata = models.JSONField(blank=True, default=dict, help_text="Execution metadata (provider used, tokens, safety status)")
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = _("Chat Message")
        verbose_name_plural = _("Chat Messages")

    def __str__(self):
        return f"[{self.role.upper()}] {self.content[:40]}..."


class ChatInteraction(models.Model):
    ACTION_CHOICES = [
        ('answer', _('Answer Provided')),
        ('pricing', _('Pricing Estimated')),
        ('treatment_view', _('Treatment Viewed')),
        ('appointment_started', _('Appointment Booking Started')),
        ('appointment_completed', _('Appointment Successfully Submitted')),
        ('whatsapp_clicked', _('WhatsApp Consultation Clicked')),
        ('call_clicked', _('Direct Phone Call Clicked')),
        ('emergency_alerted', _('Emergency Safety Alerted')),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='interactions')
    intent = models.CharField(max_length=100, blank=True, db_index=True)
    treatment = models.CharField(max_length=150, blank=True, db_index=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    extra_data = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Chat Interaction")
        verbose_name_plural = _("Chat Interactions")

    def __str__(self):
        return f"{self.action} - {self.treatment or 'General'} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class ChatbotFeedback(models.Model):
    RATING_CHOICES = [
        ('positive', _('Helpful 👍')),
        ('negative', _('Not Helpful 👎')),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='feedback_entries')
    message = models.ForeignKey(ChatMessage, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks')
    rating = models.CharField(max_length=20, choices=RATING_CHOICES)
    comment = models.TextField(blank=True, help_text="Optional patient review / what they were looking for")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Chatbot Feedback")
        verbose_name_plural = _("Chatbot Feedback Entries")

    def __str__(self):
        return f"{self.rating.capitalize()} Feedback on Chat {str(self.conversation.id)[:8]}"


class UnansweredQuestion(models.Model):
    STATUS_CHOICES = [
        ('new', _('New / Pending Review')),
        ('reviewed', _('Reviewed')),
        ('added_to_faq', _('Added to Official FAQ')),
        ('ignored', _('Ignored / Invalid')),
    ]

    question = models.TextField()
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=100, blank=True, default='general')
    frequency = models.PositiveIntegerField(default=1, help_text="Occurrences of this or similar unanswered inquiry")
    notes = models.TextField(blank=True, help_text="Staff notes or draft answer")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='new', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-frequency', '-created_at']
        verbose_name = _("Unanswered Question")
        verbose_name_plural = _("Unanswered Questions")

    def __str__(self):
        return f"{self.question[:60]} (Count: {self.frequency})"
