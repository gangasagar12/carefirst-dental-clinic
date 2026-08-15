from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from unfold.admin import ModelAdmin
from unfold.decorators import action
from .models import Appointment, InquiriesDashboard
from .admin_views import inquiries_dashboard

@admin.register(Appointment)
class AppointmentAdmin(ModelAdmin):
    list_display = ('full_name', 'phone', 'preferred_date', 'status', 'doctor', 'branch', 'created_at')
    list_filter = ('status', 'preferred_date', 'treatment', 'doctor', 'branch')
    search_fields = ('full_name', 'phone', 'email')
    readonly_fields = ('created_at',)
    
    actions_detail = ["back_to_dashboard"]

    @action(description="← Back to Dashboard")
    def back_to_dashboard(self, request, object_id):
        return redirect('admin:appointments_inquiriesdashboard_changelist')

@admin.register(InquiriesDashboard)
class InquiriesDashboardAdmin(ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(inquiries_dashboard), name='appointments_inquiriesdashboard_changelist'),
        ]
        return custom_urls + urls
