import re
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from appointments.models import EmailNotification

def get_email_subject(inquiry_type='contact'):
    if inquiry_type == 'appointment':
        return "✅ Appointment Request Received – CareFirst Dental Clinic"
    return "✅ Thank You for Contacting CareFirst Dental Clinic – We Received Your Message"

def get_email_plain_text(patient_name, inquiry_type='contact', details=None):
    """
    Returns the bilingual (English + Nepali) plain-text version for the patient.
    """
    details = details or {}
    name = patient_name or "Valued Patient"
    app_num = details.get('appointment_number', 'Pending Confirmation')
    pref_date = details.get('preferred_date', 'To be scheduled')
    pref_time = details.get('preferred_time', 'Flexible')
    treatment = details.get('treatment', 'General Dental Care')
    doctor = details.get('doctor', 'CareFirst Specialist Team')

    app_info_en = ""
    if inquiry_type == 'appointment':
        app_info_en = f"""
--- YOUR APPOINTMENT SUMMARY ---
Reference Number: {app_num}
Treatment: {treatment}
Preferred Date: {pref_date}
Preferred Time: {pref_time}
Doctor / Specialist: {doctor}
--------------------------------
"""

    return f"""Hello {name},

Thank you for choosing CareFirst Dental Clinic!

We have successfully received your {('appointment booking request' if inquiry_type == 'appointment' else 'inquiry message')}. Our clinical desk team is reviewing your preferred schedule and will contact you shortly via Phone / WhatsApp to confirm your visit.
{app_info_en}
========================================
PLEASE KEEP CONTACT ON (OUR DIRECT DETAILS)
========================================
📞 Direct Phone / Hotline: +977 980-7464136
💬 WhatsApp Desk: +977 980-7464136 (https://wa.me/9779807464136)
📍 Clinic Location: Pragatinagar Road, Shankhamul-31, Kathmandu, Nepal
⏰ Opening Hours: 7:30 AM – 7:30 PM (Open 7 Days a Week, Monday – Sunday)
✉️ Official Email: carefirstdentalclinic@gmail.com
🗺️ Google Maps: https://maps.google.com/?cid=8403623970546070943
========================================

🇳🇵 नेपालीमा जानकारी (NEPALI SUMMARY):
नमस्ते {name},
CareFirst Dental Clinic मा अपोइन्टमेन्ट अनुरोध गर्नुभएकोमा धन्यवाद! तपाईंको अनुरोध (Ref: {app_num}) प्राप्त भएको छ। हाम्रो क्लिनिक प्रतिनिधिले छिट्टै फोन वा ह्वाट्सएप मार्फत सम्पर्क गरी समय निश्चित गर्नेछ।

क्लिनिक सम्पर्क:
- फोन / ह्वाट्सएप: +९७७ ९८०-७४६४१३६
- ठेगाना: प्रगतिनगर मार्ग, शंखमुल-३१, काठमाडौँ
- समय: बिहान ७:३० देखि बेलुका ७:३० सम्म (दैनिक खुला)

🚨 DENTAL EMERGENCY OR IMMEDIATE HELP:
If you are experiencing severe tooth pain, bleeding, or require emergency dental care, please call or WhatsApp us directly at +977 980-7464136 for priority attention.

Warm regards,
Dr. Subash Banjade & The Clinical Team
CareFirst Dental Clinic
Pragatinagar Road, Shankhamul-31, Kathmandu
Phone / WhatsApp: +977 980-7464136
https://carefirstdental.com.np
"""

def get_email_html_template(patient_name, inquiry_type='contact', details=None):
    """
    Returns a responsive, bilingual (English + Nepali) HTML email template for the patient.
    """
    details = details or {}
    name = patient_name or "Valued Patient"
    app_num = details.get('appointment_number', 'Pending')
    pref_date = details.get('preferred_date', 'To be confirmed')
    pref_time = details.get('preferred_time', 'Flexible')
    treatment = details.get('treatment', 'General Consultation')
    doctor = details.get('doctor', 'CareFirst Specialist Team')
    
    app_details_html = ""
    if inquiry_type == 'appointment':
        app_details_html = f"""
        <div style="background: #F1F5F9; border-radius: 12px; padding: 18px 22px; margin: 22px 0; border-left: 4px solid #0284C7;">
          <h4 style="margin: 0 0 12px 0; color: #081C33; font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px;">📅 Your Appointment Details</h4>
          <table style="width: 100%; font-size: 14px; border-collapse: collapse; color: #334155;">
            <tr><td style="padding: 5px 0; font-weight: bold; width: 38%;">Reference ID:</td><td style="color: #0284C7; font-weight: bold;">{app_num}</td></tr>
            <tr><td style="padding: 5px 0; font-weight: bold;">Treatment:</td><td>{treatment}</td></tr>
            <tr><td style="padding: 5px 0; font-weight: bold;">Preferred Date:</td><td>{pref_date}</td></tr>
            <tr><td style="padding: 5px 0; font-weight: bold;">Time Slot:</td><td>{pref_time}</td></tr>
            <tr><td style="padding: 5px 0; font-weight: bold;">Specialist:</td><td>{doctor}</td></tr>
          </table>
        </div>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CareFirst Dental Clinic</title>
</head>
<body style="margin: 0; padding: 0; background-color: #F8FAFC; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #334155; line-height: 1.6;">
  <div style="max-width: 600px; margin: 25px auto; background: #FFFFFF; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(8, 28, 51, 0.08); border: 1px solid #E2E8F0;">
    
    <!-- Header Banner -->
    <div style="background: linear-gradient(135deg, #081C33 0%, #0B2545 60%, #0284C7 100%); padding: 30px 24px; text-align: center; color: #FFFFFF;">
      <h1 style="margin: 0; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">CareFirst Dental Clinic</h1>
      <p style="margin: 6px 0 0 0; font-size: 13px; color: #93C5FD; text-transform: uppercase; letter-spacing: 1px;">Advanced Dental Care • Shankhamul-31, Kathmandu</p>
    </div>

    <!-- Body Content -->
    <div style="padding: 30px 24px;">
      <h2 style="color: #081C33; font-size: 20px; margin-top: 0; font-weight: 700;">Hello {name},</h2>
      <p style="font-size: 15px; color: #475569; margin-bottom: 18px;">
        Thank you for contacting <strong>CareFirst Dental Clinic</strong>! We have successfully received your {('appointment booking request' if inquiry_type == 'appointment' else 'message')}. Our clinical desk team is reviewing your schedule and will reach out to you shortly to confirm.
      </p>

      {app_details_html}

      <!-- Direct Contact Box -->
      <div style="background: #F8FAFC; border: 1.5px solid #CBD5E1; border-radius: 14px; padding: 20px; margin: 22px 0;">
        <h3 style="margin: 0 0 14px 0; color: #081C33; font-size: 16px; font-weight: 800;">
          📞 Please Keep in Contact With Us:
        </h3>
        
        <table style="width: 100%; font-size: 14px; color: #1E293B; border-collapse: collapse;">
          <tr>
            <td style="padding: 6px 0; font-weight: 700; width: 35%;">Direct Phone:</td>
            <td style="padding: 6px 0;"><a href="tel:+9779807464136" style="color: #0284C7; text-decoration: none; font-weight: 700;">+977 980-7464136</a></td>
          </tr>
          <tr>
            <td style="padding: 6px 0; font-weight: 700;">WhatsApp Desk:</td>
            <td style="padding: 6px 0;"><a href="https://wa.me/9779807464136" style="color: #10B981; text-decoration: none; font-weight: 700;">+977 980-7464136 (Click to Chat)</a></td>
          </tr>
          <tr>
            <td style="padding: 6px 0; font-weight: 700;">Clinic Location:</td>
            <td style="padding: 6px 0;">Pragatinagar Road, Shankhamul-31, Kathmandu</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; font-weight: 700;">Opening Hours:</td>
            <td style="padding: 6px 0; color: #0E5A4F; font-weight: 700;">7:30 AM – 7:30 PM (Daily, Mon – Sun)</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; font-weight: 700;">Official Email:</td>
            <td style="padding: 6px 0;"><a href="mailto:carefirstdentalclinic@gmail.com" style="color: #0284C7; text-decoration: none;">carefirstdentalclinic@gmail.com</a></td>
          </tr>
        </table>

        <!-- Quick Action Buttons -->
        <div style="margin-top: 16px; text-align: center;">
          <a href="https://wa.me/9779807464136" style="display: inline-block; background: #25D366; color: #FFFFFF; text-decoration: none; font-weight: 700; font-size: 13px; padding: 10px 20px; border-radius: 50px; margin: 4px;">
            💬 Chat on WhatsApp
          </a>
          <a href="tel:+9779807464136" style="display: inline-block; background: #0284C7; color: #FFFFFF; text-decoration: none; font-weight: 700; font-size: 13px; padding: 10px 20px; border-radius: 50px; margin: 4px;">
            📞 Call Clinic Desk
          </a>
          <a href="https://maps.google.com/?cid=8403623970546070943" style="display: inline-block; background: #FFFFFF; color: #081C33; border: 1px solid #CBD5E1; text-decoration: none; font-weight: 700; font-size: 13px; padding: 9px 18px; border-radius: 50px; margin: 4px;">
            📍 Open in Maps
          </a>
        </div>
      </div>

      <!-- Nepali Information Card -->
      <div style="background: #F0FDF4; border: 1.5px solid #BBF7D0; border-radius: 12px; padding: 16px 20px; margin: 20px 0;">
        <h4 style="margin: 0 0 6px 0; color: #166534; font-size: 15px; font-weight: 800;">🇳🇵 नेपालीमा जानकारी (Nepali Information)</h4>
        <p style="margin: 0 0 8px 0; font-size: 14px; color: #15803D; line-height: 1.5;">
          नमस्ते <strong>{name}</strong>, CareFirst Dental Clinic मा अपोइन्टमेन्ट अनुरोध गर्नुभएकोमा धन्यवाद! तपाईंको अनुरोध (Ref: <strong>{app_num}</strong>) प्राप्त भएको छ। हाम्रो क्लिनिक प्रतिनिधिले फोन वा ह्वाट्सएप मार्फत छिट्टै सम्पर्क गरी समय निश्चित गर्नेछ।
        </p>
        <p style="margin: 0; font-size: 13px; color: #166534;">
          <strong>सम्पर्क:</strong> 📞 ९८०-७४६४१३६ | 📍 प्रगतिनगर मार्ग, शंखमुल-३१, काठमाडौँ | ⏰ बिहान ७:३० – बेलुका ७:३० (दैनिक खुला)
        </p>
      </div>

      <!-- Emergency Help Notice -->
      <div style="background: #FEF2F2; border-left: 4px solid #EF4444; padding: 12px 16px; border-radius: 8px; margin-top: 18px;">
        <p style="margin: 0; font-size: 13px; color: #991B1B; line-height: 1.5;">
          <strong>🚨 Need Urgent Care?</strong> If you are experiencing acute tooth pain or swelling, please call our emergency line directly at <strong>+977 980-7464136</strong> for immediate assistance.
        </p>
      </div>

    </div>

    <!-- Footer -->
    <div style="background: #F1F5F9; padding: 20px 24px; text-align: center; font-size: 12px; color: #64748B; border-top: 1px solid #E2E8F0;">
      <p style="margin: 0 0 4px 0; font-weight: 700; color: #081C33;">CareFirst Dental Clinic</p>
      <p style="margin: 0 0 6px 0;">Pragatinagar Road, Shankhamul-31, Kathmandu, Nepal • NMC Reg. #31229</p>
      <p style="margin: 0;"><a href="https://carefirstdental.com.np" style="color: #0284C7; text-decoration: none;">www.carefirstdental.com.np</a></p>
    </div>

  </div>
</body>
</html>
"""

def is_valid_email(email_address):
    """
    Basic email validation.
    """
    if not email_address:
        return False
    return re.match(r"[^@]+@[^@]+\.[^@]+", email_address.strip()) is not None

def send_clinic_admin_alert(instance, inquiry_type='appointment'):
    """
    Sends an immediate CLINIC-ONLY notification alert email to carefirstdentalclinic@gmail.com with complete patient details.
    """
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'carefirstdentalclinic@gmail.com')
        to_email = getattr(settings, 'NOTIFICATION_EMAIL', 'carefirstdentalclinic@gmail.com')
        
        if inquiry_type == 'appointment':
            ref_num = getattr(instance, 'appointment_number', None) or f"CF-{instance.id:06d}"
            patient_phone = str(instance.phone or 'N/A')
            wa_phone = patient_phone.replace('+', '').replace(' ', '').replace('-', '')
            pref_time = instance.get_preferred_time_display() if hasattr(instance, 'get_preferred_time_display') else str(getattr(instance, 'preferred_time', 'Flexible'))
            treatment = instance.service.title if getattr(instance, 'service', None) else (instance.get_treatment_display() if hasattr(instance, 'get_treatment_display') else 'General Dental Care')
            doctor_name = f"Dr. {instance.doctor.name}" if getattr(instance, 'doctor', None) else 'CareFirst Clinical Team'
            patient_notes = instance.message or 'No additional notes provided by patient.'
            
            subject = f"🚨 [New Booking Alert] {instance.full_name} | Ref: {ref_num} | {patient_phone}"
            
            plain_body = f"""CAREFIRST CLINIC - NEW APPOINTMENT BOOKING ALERT
============================================================
REFERENCE ID:        {ref_num}
PATIENT NAME:        {instance.full_name}
PHONE NUMBER:        {patient_phone}
EMAIL ADDRESS:       {instance.email or 'N/A'}
PREFERRED DATE:      {instance.preferred_date}
TIME WINDOW:         {pref_time}
SELECTED TREATMENT:  {treatment}
ASSIGNED SPECIALIST: {doctor_name}

PATIENT NOTES & CONCERNS:
"{patient_notes}"
============================================================
Direct WhatsApp Patient: https://wa.me/{wa_phone}
Manage in Staff Dashboard: https://carefirstdental.com.np/dashboard/appointments/{instance.id}/
"""
            html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; background: #F1F5F9; padding: 20px; color: #1E293B; margin: 0;">
  <div style="max-width: 600px; margin: 0 auto; background: #FFFFFF; border-radius: 12px; overflow: hidden; border: 1.5px solid #CBD5E1; box-shadow: 0 10px 25px rgba(0,0,0,0.08);">
    
    <div style="background: #081C33; padding: 20px 24px; color: #FFFFFF;">
      <span style="background: #DC2626; color: #FFFFFF; font-size: 11px; font-weight: 800; padding: 3px 10px; border-radius: 50px; text-transform: uppercase; letter-spacing: 0.5px;">New Booking Request</span>
      <h2 style="margin: 8px 0 0 0; font-size: 20px; font-weight: 800;">Patient: {instance.full_name}</h2>
      <p style="margin: 4px 0 0 0; font-size: 13px; color: #94A3B8;">Reference ID: <strong style="color: #38BDF8;">{ref_num}</strong></p>
    </div>

    <div style="padding: 24px;">
      <table style="width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 20px;">
        <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 10px 0; font-weight: bold; width: 38%; color: #64748B;">Patient Phone:</td><td style="padding: 10px 0; font-weight: bold; color: #081C33;"><a href="tel:{patient_phone}" style="color: #0284C7; text-decoration: none;">{patient_phone}</a></td></tr>
        <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 10px 0; font-weight: bold; color: #64748B;">Patient Email:</td><td style="padding: 10px 0;">{instance.email or 'N/A'}</td></tr>
        <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 10px 0; font-weight: bold; color: #64748B;">Preferred Date:</td><td style="padding: 10px 0; font-weight: bold; color: #0E5A4F;">{instance.preferred_date}</td></tr>
        <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 10px 0; font-weight: bold; color: #64748B;">Time Window:</td><td style="padding: 10px 0;">{pref_time}</td></tr>
        <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 10px 0; font-weight: bold; color: #64748B;">Treatment:</td><td style="padding: 10px 0; font-weight: bold; color: #0284C7;">{treatment}</td></tr>
        <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 10px 0; font-weight: bold; color: #64748B;">Specialist:</td><td style="padding: 10px 0;">{doctor_name}</td></tr>
      </table>

      <div style="background: #F8FAFC; border: 1.5px solid #E2E8F0; border-radius: 10px; padding: 14px 18px; margin-bottom: 22px;">
        <strong style="color: #081C33; font-size: 13px; display: block; margin-bottom: 6px;">💬 Patient Notes & Message:</strong>
        <p style="margin: 0; font-size: 14px; color: #334155; font-style: italic;">"{patient_notes}"</p>
      </div>

      <div style="text-align: center; padding-top: 10px;">
        <a href="https://wa.me/{wa_phone}?text=Hello%20{instance.full_name}%2C%20greeting%20from%20CareFirst%20Dental%20Clinic%20regarding%20your%20appointment%20request%20({ref_num})." target="_blank" style="display: inline-block; background: #25D366; color: #FFFFFF; font-weight: bold; font-size: 13px; text-decoration: none; padding: 11px 22px; border-radius: 50px; margin: 4px;">
          💬 WhatsApp Patient Instantly
        </a>
        <a href="tel:{patient_phone}" style="display: inline-block; background: #0284C7; color: #FFFFFF; font-weight: bold; font-size: 13px; text-decoration: none; padding: 11px 22px; border-radius: 50px; margin: 4px;">
          📞 Call Patient
        </a>
      </div>
    </div>

    <div style="background: #F8FAFC; padding: 14px 24px; font-size: 12px; color: #64748B; border-top: 1px solid #E2E8F0; text-align: center;">
      CareFirst Dental Clinic Automated Command Notification
    </div>
  </div>
</body>
</html>
"""
        else:
            subject = f"📬 [New Contact Inquiry] From: {instance.name} – {instance.subject}"
            plain_body = f"""CAREFIRST CLINIC - NEW CONTACT MESSAGE INQUIRY
============================================================
SENDER NAME:   {instance.name}
EMAIL ADDRESS: {instance.email}
PHONE NUMBER:  {getattr(instance, 'phone', 'N/A')}
SUBJECT:       {instance.subject}

MESSAGE BODY:
"{instance.message}"
============================================================
Reply directly to: {instance.email}
"""
            html_body = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; background: #F1F5F9; padding: 20px; color: #1E293B; margin: 0;">
  <div style="max-width: 600px; margin: 0 auto; background: #FFFFFF; border-radius: 12px; overflow: hidden; border: 1.5px solid #CBD5E1;">
    <div style="background: #0B2545; padding: 20px 24px; color: #FFFFFF;">
      <span style="background: #0284C7; color: #FFFFFF; font-size: 11px; font-weight: bold; padding: 3px 10px; border-radius: 50px; text-transform: uppercase;">Website Contact Inquiry</span>
      <h3 style="margin: 8px 0 0 0; font-size: 18px;">From: {instance.name}</h3>
      <p style="margin: 4px 0 0 0; font-size: 13px; color: #94A3B8;">Subject: {instance.subject}</p>
    </div>
    <div style="padding: 24px;">
      <p><strong>Email:</strong> <a href="mailto:{instance.email}">{instance.email}</a></p>
      <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; margin: 16px 0;">
        <strong style="display: block; margin-bottom: 6px; color: #081C33;">Message:</strong>
        <p style="margin: 0; color: #334155; font-size: 14px;">{instance.message}</p>
      </div>
      <a href="mailto:{instance.email}?subject=Re:%20{instance.subject}" style="display: inline-block; background: #0284C7; color: #FFFFFF; text-decoration: none; font-weight: bold; font-size: 13px; padding: 10px 20px; border-radius: 50px;">
        ✉️ Reply via Email
      </a>
    </div>
  </div>
</body></html>"""

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_body,
            from_email=from_email,
            to=[to_email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending clinic notification email: {e}")
        return False

def queue_email_confirmation(name, email, inquiry_type, obj_id, details=None):
    """
    Creates a pending EmailNotification record for the patient and triggers instant dispatch.
    """
    if not is_valid_email(email):
        return False

    email = email.strip()
    subject = get_email_subject(inquiry_type)
    plain_text = get_email_plain_text(name, inquiry_type, details)
    html_text = get_email_html_template(name, inquiry_type, details)

    notification = EmailNotification.objects.create(
        inquiry_type=inquiry_type,
        inquiry_id=obj_id,
        patient_name=name,
        email_address=email,
        subject=subject,
        message_text=plain_text,
        status='pending'
    )
    
    # Trigger instant send attempt to patient
    send_pending_email_messages(notification.id, html_content=html_text)
    return True

def send_pending_email_messages(notification_id=None, html_content=None):
    """
    Sends email confirmations to the patient using Django's configured SMTP backend.
    """
    if notification_id:
        notifications = EmailNotification.objects.filter(id=notification_id, status='pending')
    else:
        notifications = EmailNotification.objects.filter(status='pending')
        
    for notification in notifications:
        try:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'carefirstdentalclinic@gmail.com')
            
            # Prepare email with plain text
            msg = EmailMultiAlternatives(
                subject=notification.subject,
                body=notification.message_text,
                from_email=from_email,
                to=[notification.email_address]
            )
            
            # Attach HTML version if available
            html = html_content or get_email_html_template(notification.patient_name, notification.inquiry_type)
            msg.attach_alternative(html, "text/html")
            
            msg.send(fail_silently=False)
            
            # If successful, mark as sent
            notification.status = 'sent'
            notification.save()
            
        except Exception as e:
            notification.status = 'failed'
            notification.save()
