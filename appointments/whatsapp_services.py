import re
import urllib.parse
from django.conf import settings
from django.urls import reverse

CLINIC_NAME = "CareFirst Dental Clinic"
CLINIC_PHONE = "+977 980-7464136"
CLINIC_LANDLINE = "01-5916886"
CLINIC_LOCATION = "Pragatinagar Road, Shankhamul-31, Kathmandu (Near New Baneshwor)"
GOOGLE_MAPS_URL = "https://maps.app.goo.gl/9Z7Z1v6v4X"


def clean_phone_for_whatsapp(phone: str) -> str:
    """
    Sanitize and format phone number for WhatsApp wa.me links.
    Handles Nepal mobile numbers (98XXXXXXXX, 97XXXXXXXX) and international formats.
    """
    if not phone:
        return ""
    
    # Strip all non-digit characters except leading plus if any
    digits = re.sub(r'\D', '', str(phone))
    
    # If standard 10-digit Nepal mobile number starting with 98 or 97
    if len(digits) == 10 and (digits.startswith('98') or digits.startswith('97')):
        return f"977{digits}"
    
    # If 9-digit Kathmandu landline starting with 01
    if len(digits) == 9 and digits.startswith('01'):
        return f"9771{digits[2:]}"
    
    # If already has country code 977 and total 13 digits
    if digits.startswith('977') and len(digits) in (12, 13):
        return digits
        
    return digits


# Function alias for backwards compatibility and test clarity
sanitize_nepal_phone_number = clean_phone_for_whatsapp



def get_patient_pass_url(appointment, request=None) -> str:
    """Build absolute or root URL for patient manage pass."""
    try:
        relative_url = appointment.get_manage_url()
    except Exception:
        token = getattr(appointment, 'access_token', None) or getattr(appointment, 'booking_id', None) or str(appointment.id)
        relative_url = f"/appointment/manage/{token}/"

    if request:
        return request.build_absolute_uri(relative_url)
    
    domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
    protocol = 'https' if not settings.DEBUG else 'http'
    return f"{protocol}://{domain}{relative_url}"


def generate_whatsapp_templates(appointment, request=None) -> dict:
    """
    Generate a suite of pre-formatted WhatsApp message templates for reception dispatch.
    Returns a dictionary of template types with text and direct wa.me URLs.
    """
    phone_clean = clean_phone_for_whatsapp(appointment.phone)
    pass_url = get_patient_pass_url(appointment, request)
    
    patient_name = appointment.full_name or "Valued Patient"
    booking_id = appointment.display_booking_id
    date_str = appointment.preferred_date.strftime("%A, %B %d, %Y") if appointment.preferred_date else "Scheduled Date"
    time_str = appointment.get_preferred_time_display() if hasattr(appointment, 'get_preferred_time_display') else appointment.preferred_time or "Flexible"
    service_name = appointment.service.title if appointment.service else (appointment.get_treatment_display() if hasattr(appointment, 'get_treatment_display') else "Dental Consultation")
    doctor_name = f"Dr. {appointment.doctor.name}" if appointment.doctor else "CareFirst Senior Consultant"

    # 1. BOOKING CONFIRMATION TEMPLATE
    confirmation_msg = (
        f"🦷 *{CLINIC_NAME} — Appointment Confirmation*\n\n"
        f"Dear *{patient_name}*,\n"
        f"Your dental appointment has been *CONFIRMED*! Here are your visit details:\n\n"
        f"📋 *Booking ID:* `{booking_id}`\n"
        f"🩺 *Treatment / Service:* {service_name}\n"
        f"👨‍⚕️ *Attending Doctor:* {doctor_name}\n"
        f"📅 *Date:* {date_str}\n"
        f"⏰ *Time Slot:* {time_str}\n\n"
        f"📍 *Clinic Location:*\n{CLINIC_LOCATION}\n"
        f"🗺️ *Google Maps Directions:*\n{GOOGLE_MAPS_URL}\n\n"
        f"📱 *Your Digital Pass & PDF Confirmation:*\n{pass_url}\n\n"
        f"📞 Reception: {CLINIC_PHONE} | {CLINIC_LANDLINE}\n"
        f"_Please arrive 5–10 minutes early. We look forward to seeing your smile!_"
    )

    # 2. 24-HOUR APPOINTMENT REMINDER TEMPLATE
    reminder_msg = (
        f"⏰ *Reminder: Dental Appointment Tomorrow at {CLINIC_NAME}*\n\n"
        f"Dear *{patient_name}*,\n"
        f"This is a friendly reminder for your scheduled dental appointment *tomorrow*:\n\n"
        f"📋 *Booking ID:* `{booking_id}`\n"
        f"📅 *Date:* {date_str}\n"
        f"⏰ *Time Slot:* {time_str}\n"
        f"🩺 *Service:* {service_name} ({doctor_name})\n\n"
        f"📍 *Location:* {CLINIC_LOCATION}\n"
        f"🗺️ *Google Maps:* {GOOGLE_MAPS_URL}\n"
        f"📱 *View Pass:* {pass_url}\n\n"
        f"If you need to reschedule or have any questions, please reply to this message or call {CLINIC_PHONE}.\n"
        f"_See you tomorrow!_"
    )

    # 3. RESCHEDULE NOTICE TEMPLATE
    reschedule_msg = (
        f"🗓️ *{CLINIC_NAME} — Updated Appointment Schedule*\n\n"
        f"Dear *{patient_name}*,\n"
        f"Your dental appointment has been updated to a new confirmed time slot:\n\n"
        f"📋 *Booking ID:* `{booking_id}`\n"
        f"📅 *New Date:* {date_str}\n"
        f"⏰ *New Time Slot:* {time_str}\n"
        f"🩺 *Service:* {service_name}\n\n"
        f"📱 *Updated Digital Pass:* {pass_url}\n"
        f"📍 *Google Maps:* {GOOGLE_MAPS_URL}\n\n"
        f"Feel free to reach us at {CLINIC_PHONE} if you have any questions."
    )

    # 4. GENERAL FOLLOW-UP / GREETING TEMPLATE
    inquiry_msg = (
        f"👋 *Greeting from {CLINIC_NAME}*\n\n"
        f"Hello *{patient_name}*,\n"
        f"Thank you for contacting CareFirst Dental Clinic in Shankhamul, Kathmandu regarding *{service_name}*.\n\n"
        f"How can our clinical reception team assist you today?\n"
        f"📞 Phone: {CLINIC_PHONE} | {CLINIC_LANDLINE}\n"
        f"📍 Location: {GOOGLE_MAPS_URL}\n\n"
        f"_We're always here to help you achieve a healthy, confident smile._"
    )

    def build_url(msg: str) -> str:
        if not phone_clean:
            return ""
        return f"https://wa.me/{phone_clean}?text={urllib.parse.quote(msg)}"

    return {
        "phone_clean": phone_clean,
        "phone_original": appointment.phone,
        "booking_id": booking_id,
        "patient_name": patient_name,
        "templates": {
            "confirmation": {
                "title": "Booking Confirmation",
                "label": "Send Booking Confirmation & Pass",
                "message": confirmation_msg,
                "url": build_url(confirmation_msg),
            },
            "reminder": {
                "title": "24h Pre-Visit Reminder",
                "label": "Send 24-Hour Reminder",
                "message": reminder_msg,
                "url": build_url(reminder_msg),
            },
            "reschedule": {
                "title": "Schedule Update",
                "label": "Send Rescheduled Schedule",
                "message": reschedule_msg,
                "url": build_url(reschedule_msg),
            },
            "inquiry": {
                "title": "General Consultation",
                "label": "Send General Follow-Up",
                "message": inquiry_msg,
                "url": build_url(inquiry_msg),
            },
        }
    }


def get_all_whatsapp_templates(appointment, request=None) -> dict:
    """Convenience helper returning the templates sub-dictionary."""
    return generate_whatsapp_templates(appointment, request=request)["templates"]

