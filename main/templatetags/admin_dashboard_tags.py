from django import template
from main.models import Doctor, Service, ContactMessage
from django.contrib.admin.models import LogEntry

register = template.Library()

@register.simple_tag
def get_dashboard_stats():
    return {
        'total_doctors': Doctor.objects.filter(is_active=True).count(),
        'total_services': Service.objects.filter(is_active=True).count(),
        'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
        'total_messages': ContactMessage.objects.count(),
        'recent_activities': LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:10]
    }
