import datetime
import logging
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models import Q

from appointments.models import Appointment, EmailNotification
from appointments.whatsapp_services import (
    generate_whatsapp_templates,
    get_patient_pass_url,
    CLINIC_NAME,
    CLINIC_PHONE,
    CLINIC_LANDLINE,
    CLINIC_LOCATION,
    GOOGLE_MAPS_URL,
)
from main.services.email import get_clinic_contact_info

logger = logging.getLogger(__name__)


def send_24h_appointment_reminder_email(appointment, request=None) -> bool:
    """
    Send an automated bilingual 24-hour pre-visit reminder email to the patient.
    """
    if not appointment.email:
        return False

    pass_url = get_patient_pass_url(appointment, request)
    contact = get_clinic_contact_info()
    patient_name = appointment.full_name or "Valued Patient"
    booking_id = appointment.display_booking_id
    date_str = appointment.preferred_date.strftime("%A, %B %d, %Y") if appointment.preferred_date else "Tomorrow"
    time_str = appointment.get_preferred_time_display() if hasattr(appointment, 'get_preferred_time_display') else appointment.preferred_time or "Flexible"
    service_name = appointment.service.title if appointment.service else (appointment.get_treatment_display() if hasattr(appointment, 'get_treatment_display') else "Dental Treatment")
    doctor_name = f"Dr. {appointment.doctor.name}" if appointment.doctor else "CareFirst Specialist"

    subject = f"⏰ 24-Hour Reminder: Your Dental Visit Tomorrow at {CLINIC_NAME} (ID: {booking_id})"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'carefirstdentalclinic@gmail.com')

    plain_text = f"""Hello {patient_name},

This is a friendly reminder from {CLINIC_NAME} that your dental appointment is scheduled for TOMORROW.

========================================
APPOINTMENT DETAILS
========================================
📋 Booking ID:       {booking_id}
📅 Date:             {date_str}
⏰ Time Slot:        {time_str}
🩺 Service:          {service_name}
👨‍⚕️ Attending Doctor: {doctor_name}
📍 Clinic Location:  {CLINIC_LOCATION}
🗺️ Google Maps:     {GOOGLE_MAPS_URL}
📱 Your Pass Link:  {pass_url}
========================================

PRE-VISIT PREPARATION TIPS:
- Please arrive 5–10 minutes prior to your scheduled time slot.
- Bring your Booking ID ({booking_id}) or show your Digital Pass on your mobile.
- If you take daily medications, please take them as prescribed unless instructed otherwise.

NEED TO RESCHEDULE OR CANCEL?
If you cannot make it tomorrow, please notify our reception as soon as possible via phone or your pass link:
📞 Phone: {CLINIC_PHONE} | {CLINIC_LANDLINE}
💬 WhatsApp: https://wa.me/9779807464136

🇳🇵 नेपालीमा जानकारी:
नमस्ते {patient_name},
केयरफर्स्ट डेन्टल क्लिनिकमा भोलिको लागि तपाईंको दन्त उपचारको समय निश्चित छ (बुकिङ नम्बर: {booking_id})। कृपया आफ्नो समयभन्दा ५-१० मिनेट अगाडि आइपुग्नुहोला। यदि समय परिवर्तन गर्नुपरेमा तुरुन्तै हामीलाई ९८०-७४६४१३६ मा सम्पर्क गर्नुहोस्।

Warm regards,
Clinical Reception Desk
{CLINIC_NAME}
Shankhamul-31, Kathmandu
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #F8FAFC; margin: 0; padding: 24px; color: #0F172A; }}
  .card {{ max-width: 600px; margin: 0 auto; background: #FFFFFF; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 1px solid #E2E8F0; }}
  .header {{ background: linear-gradient(135deg, #081C33 0%, #0B2545 60%, #0284C7 100%); padding: 32px 24px; text-align: center; color: #FFFFFF; }}
  .body {{ padding: 32px 24px; }}
  .box {{ background: #F0F9FF; border-left: 4px solid #0284C7; padding: 20px; border-radius: 8px; margin: 20px 0; }}
  .btn {{ display: inline-block; background: #0284C7; color: #FFFFFF !important; text-decoration: none; padding: 12px 28px; border-radius: 50px; font-weight: bold; margin-top: 16px; }}
  .footer {{ background: #081C33; padding: 20px; text-align: center; color: #94A3B8; font-size: 0.85rem; }}
</style>
</head>
<body>
  <div class="card">
    <div class="header">
      <h2 style="margin:0 0 6px 0; color:#FFFFFF;">CareFirst Dental Clinic</h2>
      <p style="margin:0; color:#BAE6FD; font-size:1.05rem;">⏰ 24-Hour Pre-Appointment Reminder</p>
    </div>
    <div class="body">
      <p>Dear <strong>{patient_name}</strong>,</p>
      <p>This is a friendly reminder from our clinical desk that your dental appointment is scheduled for <strong>tomorrow</strong>.</p>
      
      <div class="box">
        <p style="margin:4px 0;"><strong>📋 Booking ID:</strong> <span style="font-family:monospace; background:#E0F2FE; padding:2px 6px; border-radius:4px;">{booking_id}</span></p>
        <p style="margin:4px 0;"><strong>📅 Date:</strong> {date_str}</p>
        <p style="margin:4px 0;"><strong>⏰ Time Slot:</strong> {time_str}</p>
        <p style="margin:4px 0;"><strong>🩺 Treatment:</strong> {service_name}</p>
        <p style="margin:4px 0;"><strong>👨‍⚕️ Attending Doctor:</strong> {doctor_name}</p>
      </div>

      <div style="text-align: center; margin: 24px 0;">
        <a href="{pass_url}" class="btn">View Digital Pass & Instructions</a>
      </div>

      <p style="font-size:0.9rem; color:#64748B;">
        📍 <strong>Location:</strong> {CLINIC_LOCATION}<br>
        🗺️ <a href="{GOOGLE_MAPS_URL}" style="color:#0284C7;">Open Directions on Google Maps</a><br>
        📞 <strong>Reception Hotline:</strong> {CLINIC_PHONE} | {CLINIC_LANDLINE}
      </p>
    </div>
    <div class="footer">
      &copy; {timezone.now().year} CareFirst Dental Clinic Kathmandu. All rights reserved.
    </div>
  </div>
</body>
</html>
"""

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=from_email,
            to=[appointment.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        EmailNotification.objects.create(
            appointment=appointment,
            recipient_email=appointment.email,
            subject=subject,
            template_used="appointment_reminder_24h",
            status="sent"
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send 24h reminder email to {appointment.email} for app {appointment.id}: {e}")
        EmailNotification.objects.create(
            appointment=appointment,
            recipient_email=appointment.email,
            subject=subject,
            template_used="appointment_reminder_24h",
            status="failed",
            error_message=str(e)
        )
        return False


def send_24h_appointment_reminders(target_date=None, dry_run=False, request=None) -> dict:
    """
    Main job that scans upcoming appointments for tomorrow and dispatches 24-hour reminders.
    Returns audit metrics dictionary.
    """
    if target_date is None:
        target_date = timezone.localdate() + datetime.timedelta(days=1)

    # Find confirmed or pending appointments scheduled for target date that haven't received reminder
    upcoming_appointments = Appointment.objects.filter(
        preferred_date=target_date,
        status__in=['confirmed', 'pending'],
        reminder_sent=False
    ).select_related('service', 'doctor', 'branch')

    total_count = upcoming_appointments.count()
    emails_sent = 0
    whatsapp_ready = 0
    processed_list = []

    logger.info(f"Starting 24h reminder scan for {target_date}. Found {total_count} appointments.")

    for app in upcoming_appointments:
        item = {
            "id": app.id,
            "patient_name": app.full_name,
            "phone": app.phone,
            "email": app.email,
            "time_slot": app.get_preferred_time_display() if hasattr(app, 'get_preferred_time_display') else app.preferred_time,
            "service": app.service.title if app.service else "General Dental Consultation",
            "email_sent": False,
        }

        # 1. Send Email if available
        if app.email and not dry_run:
            success = send_24h_appointment_reminder_email(app, request)
            item["email_sent"] = success
            if success:
                emails_sent += 1

        # 2. WhatsApp templates prepared
        wa_data = generate_whatsapp_templates(app, request)
        item["whatsapp_url"] = wa_data["templates"]["reminder"]["url"]
        if app.phone:
            whatsapp_ready += 1

        # 3. Update appointment record if not dry-run
        if not dry_run:
            app.reminder_sent = True
            app.reminder_sent_at = timezone.now()
            app.reminder_channel = "email+whatsapp_ready" if app.email else "whatsapp_ready"
            app.reminder_count = (app.reminder_count or 0) + 1
            app.save(update_fields=['reminder_sent', 'reminder_sent_at', 'reminder_channel', 'reminder_count'])

        processed_list.append(item)

    return {
        "target_date": str(target_date),
        "total_appointments": total_count,
        "emails_sent": emails_sent,
        "whatsapp_ready": whatsapp_ready,
        "dry_run": dry_run,
        "appointments": processed_list
    }


def get_upcoming_reminders_summary() -> dict:
    """
    Provides a quick metric summary of tomorrow's appointments for the reception dashboard.
    """
    tomorrow = timezone.localdate() + datetime.timedelta(days=1)
    tomorrow_appointments = Appointment.objects.filter(
        preferred_date=tomorrow,
        status__in=['confirmed', 'pending']
    )
    
    total = tomorrow_appointments.count()
    reminded = tomorrow_appointments.filter(reminder_sent=True).count()
    pending = tomorrow_appointments.filter(reminder_sent=False).count()

    return {
        "tomorrow_date": tomorrow,
        "total_tomorrow": total,
        "reminded_count": reminded,
        "pending_count": pending,
    }
