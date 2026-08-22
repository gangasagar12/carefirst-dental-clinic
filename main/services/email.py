import re
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from appointments.models import EmailNotification

def get_email_subject(inquiry_type='contact'):
    if inquiry_type == 'appointment':
        return "Appointment Request Received – CareFirst Dental Clinic"
    return "Thank You for Contacting CareFirst Dental Clinic – We Received Your Message"

def get_email_plain_text(patient_name, inquiry_type='contact', details=None):
    """
    Returns the plain-text fallback version with comprehensive CareFirst contact details.
    """
    details = details or {}
    name = patient_name or "Valued Patient"
    
    app_info = ""
    if inquiry_type == 'appointment' and details:
        app_num = details.get('appointment_number', 'Pending Confirmation')
        pref_date = details.get('preferred_date', 'To be scheduled')
        pref_time = details.get('preferred_time', 'Flexible')
        treatment = details.get('treatment', 'General Consultation')
        doctor = details.get('doctor', 'CareFirst Specialist Team')
        app_info = f"""
--- APPOINTMENT SUMMARY ---
Reference Number: {app_num}
Treatment: {treatment}
Preferred Date: {pref_date}
Preferred Time: {pref_time}
Doctor / Specialist: {doctor}
---------------------------
"""

    return f"""Hello {name},

Thank you for reaching out to CareFirst Dental Clinic!

We have successfully received your {('appointment booking' if inquiry_type == 'appointment' else 'message/inquiry')}. Our clinical desk and dental team are reviewing your details and will get back to you shortly to assist you.
{app_info}
========================================
PLEASE KEEP CONTACT ON (OUR DIRECT DETAILS)
========================================
📞 Direct Phone / Hotline: +977 980-7464136
💬 WhatsApp Desk: +977 980-7464136 (https://wa.me/9779807464136)
📍 Clinic Location: Pragatinagar Road, Shankhamul-31, Kathmandu, Nepal
⏰ Opening Hours: 7:30 AM – 7:30 PM (Open 7 Days a Week, Mon – Sun)
✉️ Official Email: carefirstdentalclinic@gmail.com
🗺️ Google Maps: https://maps.google.com/?cid=8403623970546070943
========================================

🚨 DENTAL EMERGENCY OR IMMEDIATE HELP:
If you are experiencing severe tooth pain, bleeding, or require emergency dental care, please call or WhatsApp us directly at +977 980-7464136 for priority attention.

Warm regards,
Dr. Subash Banjade & The Team
CareFirst Dental Clinic
Pragatinagar Road, Shankhamul-31, Kathmandu
Phone / WhatsApp: +977 980-7464136
https://carefirstdental.com.np
"""

def get_email_html_template(patient_name, inquiry_type='contact', details=None):
    """
    Returns a responsive, premium HTML email template with contact cards and direct action buttons.
    """
    details = details or {}
    name = patient_name or "Valued Patient"
    
    app_details_html = ""
    if inquiry_type == 'appointment' and details:
        app_num = details.get('appointment_number', 'Pending Confirmation')
        pref_date = details.get('preferred_date', 'To be scheduled')
        pref_time = details.get('preferred_time', 'Flexible')
        treatment = details.get('treatment', 'General Consultation')
        doctor = details.get('doctor', 'CareFirst Specialist Team')
        app_details_html = f"""
        <div style="background: #F1F5F9; border-radius: 12px; padding: 18px 22px; margin: 24px 0; border-left: 4px solid #0284C7;">
          <h4 style="margin: 0 0 12px 0; color: #081C33; font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px;">Appointment Details</h4>
          <table style="width: 100%; font-size: 14px; border-collapse: collapse; color: #334155;">
            <tr><td style="padding: 4px 0; font-weight: bold; width: 40%;">Reference No:</td><td style="color: #0284C7; font-weight: bold;">{app_num}</td></tr>
            <tr><td style="padding: 4px 0; font-weight: bold;">Treatment:</td><td>{treatment}</td></tr>
            <tr><td style="padding: 4px 0; font-weight: bold;">Preferred Date:</td><td>{pref_date}</td></tr>
            <tr><td style="padding: 4px 0; font-weight: bold;">Preferred Time:</td><td>{pref_time}</td></tr>
            <tr><td style="padding: 4px 0; font-weight: bold;">Specialist:</td><td>{doctor}</td></tr>
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
  <div style="max-width: 600px; margin: 30px auto; background: #FFFFFF; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(8, 28, 51, 0.08); border: 1px solid #E2E8F0;">
    
    <!-- Header Banner -->
    <div style="background: linear-gradient(135deg, #081C33 0%, #0B2545 60%, #0284C7 100%); padding: 32px 28px; text-align: center; color: #FFFFFF;">
      <h1 style="margin: 0; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">CareFirst Dental Clinic</h1>
      <p style="margin: 6px 0 0 0; font-size: 13px; color: #93C5FD; text-transform: uppercase; letter-spacing: 1px;">Advanced Dental Care • Shankhamul, Kathmandu</p>
    </div>

    <!-- Body Content -->
    <div style="padding: 32px 28px;">
      <h2 style="color: #081C33; font-size: 20px; margin-top: 0; font-weight: 700;">Hello {name},</h2>
      <p style="font-size: 15px; color: #475569; margin-bottom: 20px;">
        Thank you for contacting <strong>CareFirst Dental Clinic</strong>! We have received your {('appointment request' if inquiry_type == 'appointment' else 'message')} successfully. Our clinical desk team is reviewing it and will reach out to you shortly.
      </p>

      {app_details_html}

      <!-- Direct Contact Box -->
      <div style="background: #F8FAFC; border: 1.5px solid #CBD5E1; border-radius: 14px; padding: 22px; margin: 26px 0;">
        <h3 style="margin: 0 0 14px 0; color: #081C33; font-size: 16px; font-weight: 800; display: flex; align-items: center; gap: 8px;">
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
        <div style="margin-top: 18px; text-align: center;">
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

      <!-- Emergency Help Notice -->
      <div style="background: #FEF2F2; border-left: 4px solid #EF4444; padding: 14px 18px; border-radius: 8px; margin-top: 20px;">
        <p style="margin: 0; font-size: 13px; color: #991B1B; line-height: 1.5;">
          <strong>🚨 Need Urgent Care?</strong> If you are experiencing severe acute dental pain, swelling, or trauma, please call our direct hotline at <strong>+977 980-7464136</strong> for immediate emergency slot allocation.
        </p>
      </div>

    </div>

    <!-- Footer -->
    <div style="background: #F1F5F9; padding: 22px 28px; text-align: center; font-size: 12px; color: #64748B; border-top: 1px solid #E2E8F0;">
      <p style="margin: 0 0 6px 0; font-weight: 700; color: #081C33;">CareFirst Dental Clinic</p>
      <p style="margin: 0 0 8px 0;">Pragatinagar Road, Shankhamul-31, Kathmandu, Nepal • NMC Reg. #31229</p>
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

def queue_email_confirmation(name, email, inquiry_type, obj_id, details=None):
    """
    Creates a pending EmailNotification record with full contact details and triggers instant dispatch.
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
    
    # Trigger instant send attempt
    send_pending_email_messages(notification.id, html_content=html_text)
    return True

def send_pending_email_messages(notification_id=None, html_content=None):
    """
    Sends email confirmations using Django's configured SMTP backend with HTML and plain-text fallback.
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
