import json
import re
import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from django.urls import reverse

from .models import Appointment, AppointmentFunnelEvent
from main.models import Service, Doctor, SiteSettings
from main.services.whatsapp import queue_whatsapp_confirmation
from main.services.email import queue_email_confirmation

def validate_nepal_phone(phone: str) -> bool:
    """
    Validates Nepali mobile (98XXXXXXXX, 97XXXXXXXX) and standard landline numbers.
    """
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    # Starts with 977 or directly 98/97/01
    if cleaned.startswith('977'):
        cleaned = cleaned[3:]
    
    # Mobile: 10 digits starting with 98 or 97 or 96
    if re.match(r'^[9][678]\d{8}$', cleaned):
        return True
    
    # Kathmandu landline: 8 digits starting with 01 or 1
    if re.match(r'^(01|1)?\d{7}$', cleaned) and len(cleaned) >= 7:
        return True

    # General fallback for international / valid digits
    return len(cleaned) >= 7 and len(cleaned) <= 15 and cleaned.isdigit()


def appointment_funnel_view(request):
    """
    Primary Appointment view: /appointment/
    Handles both standard form submissions and query parameters.
    """
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip() or None
        treatment_val = request.POST.get('treatment', 'general-consultation').strip()
        preferred_date_str = request.POST.get('preferred_date', '').strip()
        preferred_time = request.POST.get('preferred_time', 'morning').strip()
        message = request.POST.get('message', '').strip()

        if full_name and phone:
            preferred_date = timezone.now().date() + datetime.timedelta(days=1)
            if preferred_date_str:
                try:
                    preferred_date = datetime.date.fromisoformat(preferred_date_str)
                except ValueError:
                    pass

            appointment = Appointment.objects.create(
                full_name=full_name,
                phone=phone,
                email=email,
                treatment=treatment_val,
                preferred_date=preferred_date,
                preferred_time=preferred_time,
                message=message,
                status='pending'
            )

            # Notifications
            try:
                from main.services.email import send_clinic_admin_alert
                send_clinic_admin_alert(appointment, 'appointment')
                queue_whatsapp_confirmation(appointment.full_name, appointment.phone, 'appointment', appointment.id)
                if appointment.email:
                    details = {
                        'booking_id': appointment.display_booking_id,
                        'appointment_number': appointment.display_booking_id,
                        'access_token': appointment.access_token,
                        'preferred_date': appointment.preferred_date.strftime('%B %d, %Y') if appointment.preferred_date else 'Flexible',
                        'preferred_time': appointment.get_preferred_time_display() or 'Flexible',
                        'treatment': appointment.service.title if getattr(appointment, 'service', None) else 'General Dental Consultation',
                        'doctor': appointment.doctor.name if getattr(appointment, 'doctor', None) else 'CareFirst Clinical Team',
                    }
                    queue_email_confirmation(appointment.full_name, appointment.email, 'appointment', appointment.id, details=details)
            except Exception as e:
                print(f"Notification error: {e}")

            return redirect('appointments:confirmation', access_token=appointment.access_token)

    treatment_slug = request.GET.get('treatment', '').strip().lower()
    doctor_id = request.GET.get('doctor', '').strip()
    appointment_type = request.GET.get('type', 'consultation')
    pricing_option = request.GET.get('option', '')
    quantity = request.GET.get('qty', '1')
    estimated_amount = request.GET.get('est', '')

    active_services = Service.objects.filter(is_active=True).order_by('order', 'title')
    active_doctors = Doctor.objects.filter(is_active=True).order_by('order', 'name')
    settings = SiteSettings.objects.first()

    # Preselected service if valid
    preselected_service = None
    if treatment_slug:
        preselected_service = active_services.filter(slug=treatment_slug).first()
        if not preselected_service:
            preselected_service = active_services.filter(title__icontains=treatment_slug).first()

    # Preselected doctor if valid
    preselected_doctor = None
    if doctor_id and doctor_id.isdigit():
        preselected_doctor = active_doctors.filter(id=int(doctor_id)).first()

    context = {
        'services': active_services,
        'doctors': active_doctors,
        'preselected_service': preselected_service,
        'preselected_doctor': preselected_doctor,
        'preselected_type': appointment_type,
        'pricing_option': pricing_option,
        'quantity': quantity,
        'estimated_amount': estimated_amount,
        'settings': settings,
    }
    return render(request, 'appointments/book.html', context)


def submit_appointment_ajax(request):
    """
    Secure AJAX endpoint to validate & create appointment request.
    Handles anti-duplicate locks, UTM persistence, and instant confirmation receipt generation.
    """
    if request.method != 'POST':
        return redirect('appointments:book')

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON request payload.'}, status=400)

    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip() or None
    treatment_slug = data.get('treatment', '').strip()
    appointment_type = data.get('appointment_type', 'consultation')
    preferred_date_str = data.get('preferred_date', '').strip()
    preferred_time = data.get('preferred_time', '').strip()
    doctor_id = data.get('doctor_id')
    message = data.get('message', '').strip()
    pricing_option = data.get('pricing_option', '').strip()
    quantity_str = data.get('quantity', '1')
    estimated_amount = data.get('estimated_amount', '').strip()

    # Attribution metadata
    utm_source = data.get('utm_source', '')
    utm_medium = data.get('utm_medium', '')
    utm_campaign = data.get('utm_campaign', '')
    utm_content = data.get('utm_content', '')
    utm_term = data.get('utm_term', '')
    landing_page = data.get('landing_page', '')
    referrer = data.get('referrer', '')
    chat_used = bool(data.get('chat_used', False))
    estimator_used = bool(data.get('estimator_used', False))
    session_id = data.get('session_id', '')

    # 1. Validation
    if not full_name or len(full_name) < 2:
        return JsonResponse({'success': False, 'error': 'Please enter your full name.'}, status=400)

    if not phone or not validate_nepal_phone(phone):
        return JsonResponse({'success': False, 'error': 'Please enter a valid contact phone number (e.g. 98XXXXXXXX).'}, status=400)

    # Preferred Date Validation
    if not preferred_date_str:
        return JsonResponse({'success': False, 'error': 'Please select your preferred appointment date.'}, status=400)

    try:
        preferred_date = datetime.date.fromisoformat(preferred_date_str)
    except ValueError:
        try:
            preferred_date = datetime.datetime.strptime(preferred_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid date format.'}, status=400)

    today = timezone.now().date()
    if preferred_date < today:
        return JsonResponse({'success': False, 'error': 'Preferred date cannot be in the past.'}, status=400)

    # 2. Anti-Duplicate submission protection (within 30 seconds for same phone & date)
    recent_duplicate = Appointment.objects.filter(
        phone=phone,
        preferred_date=preferred_date,
        created_at__gte=timezone.now() - datetime.timedelta(seconds=30)
    ).first()

    if recent_duplicate:
        return JsonResponse({
            'success': True,
            'booking_id': recent_duplicate.display_booking_id,
            'access_token': recent_duplicate.access_token,
            'appointment_number': recent_duplicate.display_booking_id,
            'full_name': recent_duplicate.full_name,
            'preferred_date': recent_duplicate.preferred_date.strftime('%B %d, %Y') if recent_duplicate.preferred_date else 'Flexible',
            'preferred_time': recent_duplicate.get_preferred_time_display() or 'Flexible',
            'treatment': recent_duplicate.service.title if recent_duplicate.service else 'General Dental Check-up',
            'redirect_url': recent_duplicate.get_confirmation_url()
        })

    # 3. Resolve Service & Doctor
    service = None
    if treatment_slug:
        service = Service.objects.filter(slug=treatment_slug, is_active=True).first()
        if not service:
            service = Service.objects.filter(title__icontains=treatment_slug, is_active=True).first()

    doctor = None
    if doctor_id:
        try:
            doctor = Doctor.objects.filter(id=int(doctor_id), is_active=True).first()
        except (ValueError, TypeError):
            pass

    try:
        quantity = max(1, int(quantity_str))
    except (ValueError, TypeError):
        quantity = 1

    # 4. Create Database Record
    appointment = Appointment(
        full_name=full_name,
        phone=phone,
        email=email,
        appointment_type=appointment_type,
        service=service,
        treatment=service.slug if service else (treatment_slug if treatment_slug in dict(Appointment.TREATMENT_CHOICES) else ''),
        pricing_option=pricing_option,
        quantity=quantity,
        estimated_amount=estimated_amount,
        preferred_date=preferred_date,
        preferred_time=preferred_time,
        doctor=doctor,
        message=message,
        status='pending',
        utm_source=utm_source,
        utm_medium=utm_medium,
        utm_campaign=utm_campaign,
        utm_content=utm_content,
        utm_term=utm_term,
        landing_page=landing_page,
        referrer=referrer,
        chat_used=chat_used,
        estimator_used=estimator_used,
    )
    appointment.save()

    # 5. Record Funnel Conversion Event
    if session_id:
        AppointmentFunnelEvent.objects.create(
            session_id=session_id,
            appointment=appointment,
            event_type='SUBMITTED',
            treatment_slug=service.slug if service else treatment_slug,
            source=utm_source or 'website_direct',
            metadata={'booking_id': appointment.display_booking_id, 'appointment_number': appointment.display_booking_id}
        )

    # 6. Queue WhatsApp & Email Notifications
    try:
        from main.services.email import send_clinic_admin_alert
        send_clinic_admin_alert(appointment, 'appointment')
        queue_whatsapp_confirmation(appointment.full_name, appointment.phone, 'appointment', appointment.id)
    except Exception as e:
        print(f"Error sending clinic alert: {e}")

    if appointment.email:
        try:
            details = {
                'booking_id': appointment.display_booking_id,
                'appointment_number': appointment.display_booking_id,
                'access_token': appointment.access_token,
                'preferred_date': appointment.preferred_date.strftime('%B %d, %Y') if appointment.preferred_date else 'Flexible',
                'preferred_time': appointment.get_preferred_time_display() or 'Flexible',
                'treatment': appointment.service.title if appointment.service else (treatment_slug.title() or 'General Consultation'),
                'doctor': appointment.doctor.name if appointment.doctor else 'CareFirst Clinical Team',
            }
            queue_email_confirmation(appointment.full_name, appointment.email, 'appointment', appointment.id, details=details)
        except Exception as e:
            print(f"Error sending patient email: {e}")

    return JsonResponse({
        'success': True,
        'booking_id': appointment.display_booking_id,
        'access_token': appointment.access_token,
        'appointment_number': appointment.display_booking_id,
        'full_name': appointment.full_name,
        'phone': appointment.phone,
        'preferred_date': appointment.preferred_date.strftime('%B %d, %Y'),
        'preferred_time': appointment.get_preferred_time_display() or 'Flexible',
        'treatment': appointment.service.title if appointment.service else (treatment_slug.title() or 'General Consultation'),
        'redirect_url': appointment.get_confirmation_url()
    })


@require_POST
def track_funnel_event_api(request):
    """
    Logs funnel transition events (STARTED, TREATMENT_SELECTED, ABANDONED)
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False}, status=400)

    session_id = data.get('session_id')
    event_type = data.get('event_type')
    treatment_slug = data.get('treatment_slug', '')
    source = data.get('source', '')
    metadata = data.get('metadata', {})

    if session_id and event_type:
        AppointmentFunnelEvent.objects.create(
            session_id=session_id,
            event_type=event_type,
            treatment_slug=treatment_slug,
            source=source,
            metadata=metadata
        )

    return JsonResponse({'success': True})


def get_appointment_by_token_or_404(token: str) -> Appointment:
    """
    Safely retrieves an Appointment instance by access_token, booking_id, or legacy appointment_number.
    """
    appointment = Appointment.objects.filter(access_token=token).first()
    if not appointment:
        appointment = Appointment.objects.filter(booking_id=token).first()
    if not appointment:
        appointment = Appointment.objects.filter(appointment_number=token).first()
    if not appointment and token.isdigit():
        appointment = Appointment.objects.filter(id=int(token)).first()
    
    if not appointment:
        from django.http import Http404
        raise Http404("Appointment not found or invalid access pass.")
    return appointment


def appointment_confirmation_view(request, access_token: str):
    """
    Displays the dedicated, professional post-submission Appointment Confirmation page
    featuring the unique Booking ID, Status Badge, Patient & Treatment Details,
    embedded QR Pass, PDF download, and Calendar export options.
    """
    appointment = get_appointment_by_token_or_404(access_token)
    settings = SiteSettings.objects.first()

    # Pre-generate QR code base64
    from .qr_services import generate_qr_base64, get_appointment_verification_url
    verification_url = get_appointment_verification_url(appointment, request=request)
    qr_code_base64 = generate_qr_base64(verification_url)

    # Calendar links
    from .calendar_services import generate_google_calendar_url
    google_calendar_url = generate_google_calendar_url(appointment, request=request)
    ical_url = appointment.get_calendar_ics_url()
    pdf_url = appointment.get_pdf_url()
    manage_url = appointment.get_manage_url()

    # WhatsApp pre-filled text
    service_name = appointment.service.title if appointment.service else (appointment.get_treatment_display() or 'Dental Consultation')
    date_str = appointment.preferred_date.strftime('%B %d, %Y') if appointment.preferred_date else 'Flexible'
    whatsapp_text = (
        f"Hello CareFirst Dental Clinic, I have submitted an appointment request "
        f"({appointment.display_booking_id}) for {service_name} on {date_str}. "
        f"I would like to check on my confirmation status."
    )
    import urllib.parse
    whatsapp_url = f"https://wa.me/9779807464136?text={urllib.parse.quote(whatsapp_text)}"

    context = {
        'appointment': appointment,
        'settings': settings,
        'qr_code_base64': qr_code_base64,
        'google_calendar_url': google_calendar_url,
        'ical_url': ical_url,
        'pdf_url': pdf_url,
        'manage_url': manage_url,
        'whatsapp_url': whatsapp_url,
        'today_iso': timezone.now().date().isoformat(),
    }
    return render(request, 'appointments/confirmation.html', context)


def appointment_manage_view(request, access_token: str):
    """
    Displays the patient self-service management page for tracking live status,
    rescheduling requests, cancellation requests, PDF downloads, and clinic communication.
    """
    appointment = get_appointment_by_token_or_404(access_token)
    settings = SiteSettings.objects.first()

    from .qr_services import generate_qr_base64, get_appointment_verification_url
    verification_url = get_appointment_verification_url(appointment, request=request)
    qr_code_base64 = generate_qr_base64(verification_url)

    from .calendar_services import generate_google_calendar_url
    google_calendar_url = generate_google_calendar_url(appointment, request=request)
    ical_url = appointment.get_calendar_ics_url()
    pdf_url = appointment.get_pdf_url()

    service_name = appointment.service.title if appointment.service else (appointment.get_treatment_display() or 'Dental Care')
    date_str = appointment.preferred_date.strftime('%B %d, %Y') if appointment.preferred_date else 'Flexible'
    whatsapp_text = (
        f"Hello CareFirst Dental Clinic, regarding my appointment "
        f"({appointment.display_booking_id}) for {service_name} on {date_str}, "
        f"I have an inquiry."
    )
    import urllib.parse
    whatsapp_url = f"https://wa.me/9779807464136?text={urllib.parse.quote(whatsapp_text)}"

    context = {
        'appointment': appointment,
        'settings': settings,
        'qr_code_base64': qr_code_base64,
        'google_calendar_url': google_calendar_url,
        'ical_url': ical_url,
        'pdf_url': pdf_url,
        'whatsapp_url': whatsapp_url,
        'today_iso': timezone.now().date().isoformat(),
    }
    return render(request, 'appointments/manage.html', context)


def appointment_download_pdf_view(request, access_token: str):
    """
    Generates and streams a official Appointment Confirmation PDF document.
    """
    from django.http import HttpResponse
    from .pdf_services import generate_appointment_confirmation_pdf

    appointment = get_appointment_by_token_or_404(access_token)
    pdf_bytes = generate_appointment_confirmation_pdf(appointment, request=request)

    filename = f"CareFirst_Appointment_{appointment.display_booking_id}.pdf"
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def appointment_calendar_ics_view(request, access_token: str):
    """
    Streams an RFC-5545 iCalendar (.ics) file for 1-click import into Apple / Outlook / Mobile calendars.
    """
    from django.http import HttpResponse
    from .calendar_services import generate_icalendar_content

    appointment = get_appointment_by_token_or_404(access_token)
    ics_text = generate_icalendar_content(appointment, request=request)

    filename = f"CareFirst_Appointment_{appointment.display_booking_id}.ics"
    response = HttpResponse(ics_text, content_type='text/calendar; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@require_POST
def appointment_request_reschedule_view(request, access_token: str):
    """
    Handles patient self-service reschedule requests and flags the appointment for receptionist review.
    """
    from django.contrib import messages
    appointment = get_appointment_by_token_or_404(access_token)

    new_date_str = request.POST.get('preferred_date', '').strip()
    new_time = request.POST.get('preferred_time', 'morning').strip()
    reason = request.POST.get('reschedule_reason', '').strip()

    if new_date_str:
        try:
            new_date = datetime.date.fromisoformat(new_date_str)
            if new_date >= timezone.now().date():
                appointment.original_date = appointment.preferred_date
                appointment.original_time = appointment.preferred_time
                appointment.preferred_date = new_date
                appointment.preferred_time = new_time
                appointment.reschedule_reason = reason
                appointment.status = 'rescheduled'
                appointment.save()

                messages.success(request, f"Your reschedule request for {new_date.strftime('%B %d, %Y')} has been submitted. Our team will verify and confirm your updated slot.")
            else:
                messages.error(request, "Selected appointment date cannot be in the past.")
        except ValueError:
            messages.error(request, "Invalid date format submitted.")

    return redirect('appointments:manage', access_token=appointment.access_token)


@require_POST
def appointment_request_cancel_view(request, access_token: str):
    """
    Handles patient self-service cancellation requests.
    """
    from django.contrib import messages
    appointment = get_appointment_by_token_or_404(access_token)

    cancel_reason = request.POST.get('cancel_reason', '').strip()
    appointment.status = 'cancelled'
    if cancel_reason:
        appointment.internal_note = f"Patient Cancel Reason: {cancel_reason}\n" + (appointment.internal_note or '')
    appointment.save()

    messages.info(request, f"Your appointment request ({appointment.display_booking_id}) has been cancelled. You are welcome to book anytime when ready.")
    return redirect('appointments:manage', access_token=appointment.access_token)
