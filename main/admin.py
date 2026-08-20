from django.contrib import admin, messages
from django.core.management import call_command
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline
from unfold.admin import ModelAdmin, TabularInline
from .models import Doctor, Service, PricingCategory, PricingItem

@admin.register(Service)
class ServiceAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('title', 'category', 'is_popular', 'is_active', 'order')
    list_editable = ('is_popular', 'is_active', 'order')
    list_filter = ('category', 'is_active', 'is_popular')
    search_fields = ('title', 'category_label')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order', 'title')


@admin.register(Doctor)
class DoctorAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('name', 'designation', 'specialty', 'nmc_number', 'experience_years', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('specialty', 'is_active')
    search_fields = ('name', 'designation', 'qualifications', 'nmc_number')
    ordering = ('order', 'name')

class PricingItemInline(TabularInline, TranslationTabularInline):
    model = PricingItem
    extra = 1

@admin.register(PricingCategory)
class PricingCategoryAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)
    ordering = ('order', 'name')
    inlines = [PricingItemInline]

from .models import SpecialOffer

@admin.register(SpecialOffer)
class SpecialOfferAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active', 'is_currently_valid')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')

from django.utils.html import format_html
from .models import Branch, Testimonial, ClinicGallery, FAQ

@admin.register(Branch)
class BranchAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('name', 'location', 'order')
    list_editable = ('order',)
    ordering = ('order', 'name')

@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('photo_preview', 'patient_name', 'treatment', 'tag_color', 'rating', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('treatment', 'rating', 'is_active', 'tag_color')
    search_fields = ('patient_name', 'treatment', 'headline', 'review')

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width:36px; height:36px; object-fit:cover; border-radius:50%; border:2px solid #0284C7;">', obj.photo.url)
        return format_html('<div style="width:36px; height:36px; border-radius:50%; background:#E2E8F0; color:#64748B; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:bold;">{}</div>', obj.patient_name[:2].upper())
    photo_preview.short_description = "Photo"

@admin.register(ClinicGallery)
class ClinicGalleryAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('caption', 'order')
    list_editable = ('order',)

@admin.register(FAQ)
class FAQAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('question', 'is_active', 'order')
    list_editable = ('is_active', 'order')

from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    
    from unfold.decorators import action
    from django.shortcuts import redirect
    
    actions_detail = ["back_to_dashboard"]

    @action(description="← Back to Dashboard")
    def back_to_dashboard(self, request, object_id):
        return redirect('admin:appointments_inquiriesdashboard_changelist')

from .models import SEOFAQCategory, SEOFAQ

@admin.register(SEOFAQCategory)
class SEOFAQCategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(SEOFAQ)
class SEOFAQAdmin(ModelAdmin):
    list_display = ('question', 'category', 'search_intent', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('category', 'search_intent', 'is_active')
    search_fields = ('question', 'answer', 'primary_keyword')


from .models import GoogleBusiness, GoogleReview


@admin.register(GoogleBusiness)
class GoogleBusinessAdmin(ModelAdmin):
    change_list_template = "admin/main/googlebusiness/change_list.html"
    list_display = (
        'business_name',
        'rating_badge',
        'review_count',
        'last_synced',
        'sync_status_badge',
    )
    readonly_fields = (
        'place_id',
        'business_name',
        'google_rating',
        'review_count',
        'last_synced',
        'sync_status',
        'sync_message',
        'created_at',
        'updated_at',
    )
    search_fields = ('business_name', 'place_id')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'sync-now/',
                self.admin_site.admin_view(self.sync_now),
                name='main_googlebusiness_sync_now',
            ),
        ]
        return custom_urls + urls

    def sync_now(self, request):
        try:
            call_command('sync_google_reviews')
            self.message_user(request, "Google reviews synced successfully.", messages.SUCCESS)
        except Exception as exc:
            self.message_user(request, f"Google reviews sync failed: {exc}", messages.ERROR)
        return redirect('admin:main_googlebusiness_changelist')

    @admin.display(description="Current Rating")
    def rating_badge(self, obj):
        return format_html(
            '<strong style="color:#f4a300;">★ {}</strong>',
            obj.google_rating,
        )

    @admin.display(description="Sync Status")
    def sync_status_badge(self, obj):
        color = '#15803d' if obj.sync_status == 'Success' else '#b45309'
        if obj.sync_status == 'Failed':
            color = '#b91c1c'
        return format_html('<strong style="color:{};">{}</strong>', color, obj.sync_status)


@admin.register(GoogleReview)
class GoogleReviewAdmin(ModelAdmin):
    list_display = ('author_name', 'rating', 'relative_time', 'publish_time', 'is_active')
    list_filter = ('rating', 'is_active', 'publish_time', 'language')
    search_fields = ('author_name', 'review_text', 'google_review_id')
    readonly_fields = (
        'business',
        'google_review_id',
        'author_name',
        'author_photo',
        'author_url',
        'rating',
        'review_text',
        'relative_time',
        'publish_time',
        'language',
        'created_at',
        'updated_at',
    )
    list_editable = ('is_active',)


# Unregister Django APScheduler models
from django_apscheduler.models import DjangoJob, DjangoJobExecution
try:
    admin.site.unregister(DjangoJob)
    admin.site.unregister(DjangoJobExecution)
except admin.sites.NotRegistered:
    pass

