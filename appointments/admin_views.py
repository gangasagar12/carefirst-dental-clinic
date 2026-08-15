from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from appointments.models import Appointment
from main.models import ContactMessage
from django.db.models import Q
from itertools import chain
from operator import attrgetter

@staff_member_required
def inquiries_dashboard(request):
    q = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    appointments = Appointment.objects.all()
    messages = ContactMessage.objects.all()

    if q:
        appointments = appointments.filter(
            Q(full_name__icontains=q) | 
            Q(email__icontains=q) | 
            Q(phone__icontains=q)
        )
        messages = messages.filter(
            Q(name__icontains=q) | 
            Q(email__icontains=q) | 
            Q(subject__icontains=q)
        )

    if status_filter:
        if status_filter in ['pending', 'confirmed', 'completed', 'cancelled']:
            appointments = appointments.filter(status=status_filter)
            # Contact messages don't have these statuses yet, so if filtering by specific appointment status, we can hide messages or show only unread/read based on logic
            # For simplicity, if status filter is applied, hide contact messages unless status is mapped
            if status_filter == 'pending':
                messages = messages.filter(is_read=False)
            elif status_filter == 'completed':
                messages = messages.filter(is_read=True)
            else:
                messages = messages.none()

    # Normalize data to a common structure
    items = []
    for app in appointments:
        items.append({
            'id_str': f"APT-{app.id:04d}",
            'name': app.full_name,
            'email': app.email or app.phone,
            'phone': app.phone,
            'date': app.created_at,
            'source': 'Appointment Booking',
            'status': app.status,
            'type': 'appointment',
            'obj_id': app.id,
            'doctor': app.doctor.name if app.doctor else None,
            'branch': app.branch.name if app.branch else None,
        })
    
    for msg in messages:
        msg_status = 'completed' if msg.is_read else 'pending'
        items.append({
            'id_str': f"MSG-{msg.id:04d}",
            'name': msg.name,
            'email': msg.email,
            'phone': '',  # ContactMessage does not have a phone field
            'date': msg.created_at,
            'source': 'Contact Form',
            'status': msg_status,
            'type': 'message',
            'obj_id': msg.id
        })

    # Sort by date descending
    items.sort(key=lambda x: x['date'], reverse=True)

    context = {
        'title': 'Inquiries & Appointments',
        'items': items,
        'q': q,
        'status_filter': status_filter
    }
    
    return render(request, 'admin/inquiries_dashboard.html', context)
