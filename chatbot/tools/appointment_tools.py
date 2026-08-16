import datetime
from typing import Dict, Any
from django.utils import timezone
from appointments.models import Appointment
from main.services.whatsapp import queue_whatsapp_confirmation
from main.services.email import queue_email_confirmation

def validate_and_create_appointment(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates patient appointment data collected via chatbot, creates Appointment record in Django database,
    and automatically triggers WhatsApp & Email confirmation queues.
    """
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip() or None
    treatment = data.get('treatment', '').strip()
    preferred_date_str = data.get('preferred_date', '').strip()
    preferred_time = data.get('preferred_time', '').strip()
    message = data.get('message', '').strip()

    if not full_name:
        return {'success': False, 'error': 'Full name is required.'}
    if not phone or len(phone) < 7:
        return {'success': False, 'error': 'A valid contact phone number is required.'}

    # Parse preferred date
    preferred_date = None
    if preferred_date_str:
        try:
            preferred_date = datetime.date.fromisoformat(preferred_date_str)
        except ValueError:
            try:
                preferred_date = datetime.datetime.strptime(preferred_date_str, '%Y-%m-%d').date()
            except ValueError:
                preferred_date = timezone.now().date() + datetime.timedelta(days=1)
    else:
        preferred_date = timezone.now().date() + datetime.timedelta(days=1)

    # Ensure appointment is not in the past
    if preferred_date < timezone.now().date():
        preferred_date = timezone.now().date() + datetime.timedelta(days=1)

    # Map treatment choices if applicable
    treatment_code = 'other'
    t_lower = treatment.lower()
    if 'clean' in t_lower or 'scal' in t_lower:
        treatment_code = 'cleaning'
    elif 'fill' in t_lower:
        treatment_code = 'filling'
    elif 'rct' in t_lower or 'root' in t_lower:
        treatment_code = 'rct'
    elif 'extract' in t_lower or 'wisdom' in t_lower:
        treatment_code = 'extraction'
    elif 'implant' in t_lower:
        treatment_code = 'implants'
    elif 'brace' in t_lower or 'ortho' in t_lower or 'align' in t_lower:
        treatment_code = 'braces'
    elif not treatment:
        treatment_code = ''

    # Resolve Service FK
    from main.models import Service
    service_obj = None
    if treatment:
        service_obj = Service.objects.filter(slug=treatment).first() or Service.objects.filter(title__icontains=treatment).first()

    try:
        appointment = Appointment(
            full_name=full_name,
            phone=phone,
            email=email,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            service=service_obj,
            treatment=service_obj.slug if service_obj else treatment_code,
            appointment_type='consultation',
            message=f"[Booked via Ask CareFirst AI Assistant] {message}".strip(),
            status='new',
            chat_used=True,
            source='chatbot' if hasattr(Appointment, 'source') else ''
        )
        appointment.save()

        # Trigger WhatsApp and Email notification queues
        try:
            queue_whatsapp_confirmation(full_name, phone, 'appointment', appointment.id)
        except Exception:
            pass

        if email:
            try:
                queue_email_confirmation(full_name, email, 'appointment', appointment.id)
            except Exception:
                pass

        return {
            'success': True,
            'appointment_id': appointment.id,
            'full_name': full_name,
            'phone': phone,
            'preferred_date': preferred_date.strftime('%B %d, %Y'),
            'preferred_time': preferred_time or 'Flexible / Clinic To Confirm',
            'treatment': treatment or 'General Check-up',
            'message': 'Your appointment request has been submitted. The CareFirst clinic team will contact you shortly to confirm your scheduled slot.'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Database error creating appointment request: {str(e)}"
        }


def generate_whatsapp_link(treatment_name: str = '', topic: str = '') -> str:
    """
    Generates a prefilled WhatsApp consultation link without leaking sensitive medical details.
    """
    phone = "9779807464136"
    if treatment_name:
        text = f"Hello CareFirst Dental Clinic, I am interested in {treatment_name} treatment and would like to inquire about a consultation."
    elif topic:
        text = f"Hello CareFirst Dental Clinic, I have a question regarding {topic}."
    else:
        text = "Hello CareFirst Dental Clinic, I would like to schedule a consultation."

    import urllib.parse
    encoded_text = urllib.parse.quote(text)
    return f"https://wa.me/{phone}?text={encoded_text}"
