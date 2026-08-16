from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
from django.utils import timezone
from unfold.admin import ModelAdmin
from unfold.decorators import action
from .models import Appointment, AppointmentFunnelEvent, InquiriesDashboard, WhatsAppNotification, EmailNotification
from .admin_views import inquiries_dashboard

@admin.register(Appointment)
class AppointmentAdmin(ModelAdmin):
    list_display = (
        'appointment_number_badge', 
        'full_name', 
        'phone', 
        'treatment_badge',
        'preferred_date', 
        'preferred_time_display',
        'status_badge', 
        'source_badge',
        'created_at'
    )
    list_filter = ('status', 'preferred_date', 'treatment', 'doctor', 'chat_used', 'estimator_used', 'utm_source', 'created_at')
    search_fields = ('appointment_number', 'full_name', 'phone', 'email', 'utm_source', 'utm_campaign')
    readonly_fields = ('appointment_number', 'created_at', 'updated_at', 'confirmed_at', 'completed_at')
    
    fieldsets = (
        ("Request Identification", {
            "fields": ("appointment_number", "status", "appointment_type", "created_at", "updated_at")
        }),
        ("Patient Contact", {
            "fields": ("full_name", "phone", "email", "message")
        }),
        ("Clinical Requirements", {
            "fields": ("service", "treatment", "doctor", "pricing_option", "quantity", "estimated_amount")
        }),
        ("Scheduling & Rescheduling", {
            "fields": ("preferred_date", "preferred_time", "original_date", "original_time", "reschedule_reason", "confirmed_at", "completed_at")
        }),
        ("Marketing Attribution & Funnel", {
            "fields": ("utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "landing_page", "referrer", "chat_used", "estimator_used"),
            "classes": ("collapse",)
        }),
        ("Staff Internal Management", {
            "fields": ("internal_note",)
        }),
    )

    actions = ['confirm_appointments', 'mark_completed', 'mark_no_show', 'cancel_appointments']

    def appointment_number_badge(self, obj):
        return format_html('<span style="font-family:monospace; font-weight:bold; color:#0284C7;">{}</span>', obj.appointment_number or f"#{obj.id}")
    appointment_number_badge.short_description = "Request ID"

    def treatment_badge(self, obj):
        name = obj.service.title if obj.service else (obj.get_treatment_display() or "General Consultation")
        return format_html('<span style="font-weight:600; color:#0B2545;">{}</span>', name)
    treatment_badge.short_description = "Treatment"

    def preferred_time_display(self, obj):
        return obj.get_preferred_time_display() or "Flexible"
    preferred_time_display.short_description = "Preferred Time"

    def status_badge(self, obj):
        colors = {
            'new': '#0284C7',
            'pending': '#F59E0B',
            'confirmed': '#10B981',
            'rescheduled': '#8B5CF6',
            'cancelled': '#EF4444',
            'completed': '#059669',
            'no_show': '#64748B',
        }
        color = colors.get(obj.status, '#64748B')
        return format_html('<span style="background:{}; color:#FFF; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:bold;">{}</span>', color, obj.get_status_display())
    status_badge.short_description = "Status"

    def source_badge(self, obj):
        if obj.chat_used:
            return format_html('<span style="color:#0284C7; font-weight:bold;"><i class="bi bi-chat-dots"></i> AI Chatbot</span>')
        if obj.estimator_used:
            return format_html('<span style="color:#8B5CF6; font-weight:bold;"><i class="bi bi-calculator"></i> Estimator</span>')
        if obj.utm_source:
            return format_html('<span style="color:#059669; font-weight:600;">{}</span>', obj.utm_source)
        return format_html('<span style="color:#94A3B8;">Website</span>')
    source_badge.short_description = "Attribution"

    @action(description="✓ Mark as Confirmed")
    def confirm_appointments(self, request, queryset):
        queryset.update(status='confirmed', confirmed_at=timezone.now())
        self.message_user(request, f"{queryset.count()} appointment(s) marked as Confirmed.")

    @action(description="✓ Mark as Completed Visit")
    def mark_completed(self, request, queryset):
        queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f"{queryset.count()} appointment(s) marked as Completed.")

    @action(description="⚠ Mark as No Show")
    def mark_no_show(self, request, queryset):
        queryset.update(status='no_show')
        self.message_user(request, f"{queryset.count()} appointment(s) marked as No Show.")

    @action(description="✕ Cancel Request")
    def cancel_appointments(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"{queryset.count()} appointment(s) cancelled.")


@admin.register(AppointmentFunnelEvent)
class AppointmentFunnelEventAdmin(ModelAdmin):
    list_display = ('event_type_badge', 'treatment_slug', 'source', 'session_id_short', 'created_at')
    list_filter = ('event_type', 'treatment_slug', 'source', 'created_at')
    search_fields = ('session_id', 'treatment_slug', 'source')
    readonly_fields = ('session_id', 'appointment', 'event_type', 'treatment_slug', 'source', 'metadata', 'created_at')

    def session_id_short(self, obj):
        return obj.session_id[:12] if obj.session_id else '-'
    session_id_short.short_description = "Session"

    def event_type_badge(self, obj):
        colors = {
            'STARTED': '#0284C7',
            'TREATMENT_SELECTED': '#0EA5E9',
            'TYPE_SELECTED': '#38BDF8',
            'DATE_SELECTED': '#818CF8',
            'DETAILS_STARTED': '#F59E0B',
            'REVIEW_VIEWED': '#F97316',
            'SUBMITTED': '#10B981',
            'ABANDONED': '#EF4444',
            'CONFIRMED': '#059669',
        }
        color = colors.get(obj.event_type, '#64748B')
        return format_html('<span style="background:{}; color:#FFF; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:bold;">{}</span>', color, obj.get_event_type_display())
    event_type_badge.short_description = "Event"


@admin.register(WhatsAppNotification)
class WhatsAppNotificationAdmin(ModelAdmin):
    list_display = ('patient_name', 'phone_number', 'inquiry_type', 'status', 'created_at')
    list_filter = ('status', 'inquiry_type', 'created_at')
    search_fields = ('patient_name', 'phone_number')


@admin.register(EmailNotification)
class EmailNotificationAdmin(ModelAdmin):
    list_display = ('patient_name', 'email_address', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('patient_name', 'email_address', 'subject')


@admin.register(InquiriesDashboard)
class InquiriesDashboardAdmin(ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(inquiries_dashboard), name='appointments_inquiriesdashboard_changelist'),
        ]
        return custom_urls + urls
