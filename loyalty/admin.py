from django.contrib import admin
from .models import (
    LoyaltyProgram,
    PatientLoyaltyProfile,
    LoyaltyTransaction,
    LoyaltyReward,
    LoyaltyNotificationLog
)


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'required_completed_treatments', 'reward_type', 'discount_percentage', 'expiry_days', 'is_active')
    list_filter = ('is_active', 'reward_type')
    search_fields = ('name', 'description')
    filter_horizontal = ('eligible_services', 'excluded_services')


@admin.register(PatientLoyaltyProfile)
class PatientLoyaltyProfileAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'full_name', 'phone', 'current_progress', 'current_cycle', 'total_completed_eligible_treatments', 'total_rewards_earned', 'updated_at')
    search_fields = ('patient_id', 'full_name', 'phone', 'normalized_phone', 'email')
    list_filter = ('program', 'current_progress', 'current_cycle')
    readonly_fields = ('patient_id', 'normalized_phone', 'created_at', 'updated_at')


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'transaction_type', 'progress_added', 'treatment_name', 'invoice_reference', 'created_at')
    search_fields = ('patient__full_name', 'patient__phone', 'invoice_reference', 'treatment_name')
    list_filter = ('transaction_type', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(LoyaltyReward)
class LoyaltyRewardAdmin(admin.ModelAdmin):
    list_display = ('reward_reference', 'patient', 'get_reward_display', 'status', 'unlocked_at', 'expires_at', 'used_at', 'applied_invoice_ref')
    search_fields = ('reward_reference', 'patient__full_name', 'patient__phone', 'applied_invoice_ref')
    list_filter = ('status', 'reward_type', 'unlocked_at', 'expires_at')
    readonly_fields = ('reward_reference', 'unlocked_at')


@admin.register(LoyaltyNotificationLog)
class LoyaltyNotificationLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'channel', 'event_type', 'recipient', 'status', 'sent_at')
    search_fields = ('patient__full_name', 'recipient', 'subject')
    list_filter = ('channel', 'event_type', 'status', 'sent_at')
    readonly_fields = ('sent_at',)
