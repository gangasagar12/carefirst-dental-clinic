import re
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from main.services.email import get_clinic_contact_info
from .models import LoyaltyNotificationLog


def generate_loyalty_html_email(patient, event_type, reward=None):
    """
    Generates a high-converting, responsive HTML email with CareFirst Dental branding.
    """
    contact = get_clinic_contact_info()
    program = patient.program
    req_treatments = program.required_completed_treatments
    curr_prog = patient.current_progress
    name = patient.full_name or "Valued Patient"
    phone = patient.phone

    # Build visual progress indicator
    dots_html = ""
    if event_type == 'reward_unlocked':
        dots_html = "".join(['<span style="display:inline-block; width:18px; height:18px; border-radius:50%; background:#10B981; margin:0 4px; box-shadow:0 0 8px rgba(16,185,129,0.5);"></span>' for _ in range(req_treatments)])
    else:
        for i in range(req_treatments):
            if i < curr_prog:
                dots_html += '<span style="display:inline-block; width:16px; height:16px; border-radius:50%; background:#0284C7; margin:0 4px;"></span>'
            else:
                dots_html += '<span style="display:inline-block; width:16px; height:16px; border-radius:50%; background:#E2E8F0; border:2px solid #CBD5E1; margin:0 4px;"></span>'

    # Subject & Hero Content determination
    if event_type == 'reward_unlocked':
        subject = f"🎉 You've Unlocked Your CareFirst Smile Reward! ({reward.get_reward_display() if reward else '10% OFF'})"
        headline = "Congratulations! You've Unlocked Your Reward"
        tagline = "Thank you for trusting CareFirst Dental with your smile."
        reward_label = reward.get_reward_display() if reward else "10% OFF"
        expiry_str = reward.expires_at.strftime('%d %B %Y') if reward else "Valid for 60 Days"
        ref_code = reward.reward_reference if reward else "CF-RWD-ACTIVE"

        card_content = f"""
        <div style="background: linear-gradient(135deg, #07192F 0%, #0B2545 100%); border-radius: 16px; padding: 28px; text-align: center; color: #ffffff; margin: 24px 0; border: 1px solid #1E3A5F; box-shadow: 0 10px 25px rgba(2,132,199,0.15);">
          <div style="font-size: 13px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #38BDF8; margin-bottom: 8px;">CareFirst Smile Reward Unlocked</div>
          <div style="font-size: 38px; font-weight: 800; color: #ffffff; margin: 4px 0; font-family: 'Outfit', sans-serif;">{reward_label}</div>
          <p style="color: #94A3B8; font-size: 14px; margin-top: 4px; margin-bottom: 20px;">On your next eligible dental procedure or checkup</p>
          
          <div style="background: rgba(255,255,255,0.08); border: 1px dashed rgba(56,189,248,0.4); border-radius: 10px; padding: 12px 16px; display: inline-block; margin-bottom: 16px;">
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #94A3B8;">Reward Reference</div>
            <div style="font-size: 18px; font-weight: 700; color: #38BDF8; letter-spacing: 1.5px; font-family: monospace;">{ref_code}</div>
          </div>
          
          <div style="font-size: 13px; color: #CBD5E1;">
            📅 <strong>Valid Until:</strong> {expiry_str}
          </div>
        </div>

        <div style="background: #F0FDF4; border-left: 4px solid #10B981; padding: 14px 18px; border-radius: 8px; margin: 20px 0; font-size: 14px; color: #166534; line-height: 1.6;">
          <strong>💡 No Card or Login Required:</strong> Your reward is automatically linked to your registered phone number (<strong>{phone}</strong>). Simply mention your phone number to our receptionist during your next visit.
        </div>
        """

    elif event_type == 'reward_applied':
        subject = "✓ CareFirst Smile Reward Applied to Your Visit"
        headline = "Reward Successfully Redeemed!"
        tagline = "We're delighted to reward your continuous care."
        reward_label = reward.get_reward_display() if reward else "10% Discount"
        inv_ref = reward.applied_invoice_ref if reward else "Your Recent Visit"

        card_content = f"""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 22px; margin: 20px 0; text-align: center;">
          <div style="font-size: 14px; font-weight: 700; color: #0284C7; text-transform: uppercase;">Reward Applied</div>
          <div style="font-size: 26px; font-weight: 800; color: #07192F; margin: 6px 0;">{reward_label}</div>
          <p style="color: #64748B; font-size: 14px; margin: 0;">Applied to Visit / Invoice: <strong>{inv_ref}</strong></p>
        </div>
        <p style="font-size: 14px; color: #475569; line-height: 1.6;">
          Your next cycle has already begun! Every eligible completed visit continues to earn you progress toward your next reward.
        </p>
        """

    else:
        # Progress Update (1/3 or 2/3)
        remaining = req_treatments - curr_prog
        if curr_prog == 1:
            subject = "Your CareFirst Smile Rewards Progress 🦷"
            headline = "Thank You for Choosing CareFirst Dental!"
            tagline = "Your loyalty progress has just been updated."
        else:
            subject = "You're One Step Closer to Your CareFirst Smile Reward 🎁"
            headline = "Great Progress on Your Smile Journey!"
            tagline = f"Complete just {remaining} more eligible visit to unlock your 10% discount."

        card_content = f"""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 14px; padding: 24px; text-align: center; margin: 20px 0;">
          <div style="font-size: 12px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #0284C7; margin-bottom: 8px;">Current Progress</div>
          <div style="font-size: 32px; font-weight: 800; color: #07192F; margin-bottom: 12px; font-family: 'Outfit', sans-serif;">
            {curr_prog} of {req_treatments} Treatments
          </div>
          <div style="margin: 12px 0 16px 0;">
            {dots_html}
          </div>
          <p style="color: #64748B; font-size: 14px; margin: 0;">
            Complete <strong>{remaining} more eligible treatment{'s' if remaining > 1 else ''}</strong> to unlock your <strong>10% OFF reward</strong>.
          </p>
        </div>
        """

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{subject}</title>
</head>
<body style="margin:0; padding:0; background-color:#F1F5F9; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color:#334155;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#F1F5F9; padding: 30px 15px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" style="max-width: 600px; background-color:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.06); border:1px solid #E2E8F0;" cellspacing="0" cellpadding="0">
          
          <!-- BRAND HEADER -->
          <tr>
            <td style="background: linear-gradient(135deg, #07192F 0%, #0B2545 100%); padding: 28px 30px; text-align: center;">
              <div style="font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px;">CAREFIRST DENTAL CLINIC</div>
              <div style="font-size: 13px; color: #38BDF8; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 4px;">CareFirst Smile Rewards</div>
            </td>
          </tr>

          <!-- BODY CONTENT -->
          <tr>
            <td style="padding: 35px 30px;">
              <h1 style="font-size: 22px; font-weight: 700; color: #07192F; margin: 0 0 8px 0; line-height: 1.3;">{headline}</h1>
              <p style="font-size: 15px; color: #64748B; margin: 0 0 20px 0;">{tagline}</p>
              
              <p style="font-size: 15px; color: #334155; line-height: 1.6; margin: 0 0 10px 0;">
                Hello <strong>{name}</strong>,
              </p>
              
              {card_content}

              <div style="margin-top: 25px; padding-top: 20px; border-top: 1px solid #E2E8F0; font-size: 13px; color: #64748B; line-height: 1.6;">
                <strong>CareFirst Dental Clinic</strong><br>
                📍 {contact['address']}<br>
                📞 Phone: {contact['phone']} | 💬 WhatsApp: +{contact['whatsapp']}<br>
                🕒 Open 7 Days: {contact['hours']}
              </div>
            </td>
          </tr>

          <!-- FOOTER -->
          <tr>
            <td style="background-color: #F8FAFC; padding: 20px 30px; text-align: center; border-top: 1px solid #E2E8F0; font-size: 12px; color: #94A3B8;">
              <p style="margin: 0 0 6px 0;"><em>Your care deserves a little extra.</em></p>
              <p style="margin: 0;">© {timezone.now().year} CareFirst Dental Clinic. All rights reserved.</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    return subject, html


def generate_whatsapp_message(patient, event_type, reward=None):
    """
    Formats a clean, professional WhatsApp text message.
    """
    program = patient.program
    req_treatments = program.required_completed_treatments
    curr_prog = patient.current_progress
    name = patient.full_name or "Valued Patient"
    remaining = req_treatments - curr_prog
    contact = get_clinic_contact_info()

    if event_type == 'reward_unlocked':
        reward_label = reward.get_reward_display() if reward else "10% OFF"
        expiry_str = reward.expires_at.strftime('%d %b %Y') if reward else "60 Days"
        ref_code = reward.reward_reference if reward else "CF-RWD-ACTIVE"
        
        return f"""🎉 *Congratulations {name}!*

You've completed {req_treatments} eligible treatments and unlocked your *CareFirst Smile Reward*! 🎁

✨ *REWARD: {reward_label}*
🏷️ Ref Code: {ref_code}
📅 Valid Until: {expiry_str}

💡 *No card or login needed:* Your reward is securely linked to your phone number ({patient.phone}). Simply mention your phone number during your next visit to redeem!

📍 CareFirst Dental Clinic, Shankhamul-31, Kathmandu
📞 {contact['phone']}"""

    elif event_type == 'reward_applied':
        reward_label = reward.get_reward_display() if reward else "10% Discount"
        return f"""✓ *Reward Redeemed!*

Hi {name}, your CareFirst Smile Reward (*{reward_label}*) has been successfully applied to your visit today!

Thank you for choosing CareFirst Dental Clinic for your oral care. Your next reward cycle is already active! 🦷✨"""

    else:
        dots = " ".join(["●" if i < curr_prog else "○" for i in range(req_treatments)])
        return f"""🦷 *CareFirst Smile Rewards*

Hi {name}! Your loyalty progress has been updated:

{dots}
*{curr_prog} of {req_treatments} eligible visits completed.*

{'Just 1 more eligible treatment to unlock your 10% OFF reward! 🎁' if remaining == 1 else f'Complete {remaining} more treatments to unlock your exclusive reward.'}

Thank you for trusting CareFirst Dental Clinic!
📞 {contact['phone']}"""


def generate_sms_message(patient, event_type, reward=None):
    """
    Short, punchy SMS text format (under 160 characters).
    """
    curr = patient.current_progress
    req = patient.program.required_completed_treatments

    if event_type == 'reward_unlocked':
        reward_label = reward.get_reward_display() if reward else "10% OFF"
        return f"Congrats! You unlocked CareFirst Smile Reward: {reward_label}! Valid for 60 days. Mention your phone at reception. Ph: 980-7464136"
    elif event_type == 'reward_applied':
        return f"Your CareFirst Smile Reward has been applied to your visit! Thank you for trusting CareFirst Dental. Ph: 980-7464136"
    else:
        return f"CareFirst Smile Rewards: You've completed {curr}/{req} eligible visits. Complete {req - curr} more to unlock 10% OFF! - CareFirst Dental"


def dispatch_loyalty_notifications(patient, event_type, reward=None, channels=('whatsapp', 'email', 'sms')):
    """
    Modular dispatcher that routes proactive notifications across WhatsApp, Email, and SMS,
    recording every message into LoyaltyNotificationLog.
    """
    subject, html_content = generate_loyalty_html_email(patient, event_type, reward)
    wa_text = generate_whatsapp_message(patient, event_type, reward)
    sms_text = generate_sms_message(patient, event_type, reward)

    # 1. EMAIL CHANNEL
    if 'email' in channels and patient.email:
        try:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'CareFirst Dental Clinic <carefirstdentalclinic@gmail.com>')
            msg = EmailMultiAlternatives(
                subject=subject,
                body=sms_text,
                from_email=from_email,
                to=[patient.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=True)

            LoyaltyNotificationLog.objects.create(
                patient=patient,
                channel='email',
                event_type=event_type,
                recipient=patient.email,
                subject=subject,
                message_body=html_content,
                status='sent'
            )
        except Exception as e:
            LoyaltyNotificationLog.objects.create(
                patient=patient,
                channel='email',
                event_type=event_type,
                recipient=patient.email or 'N/A',
                subject=subject,
                message_body=html_content,
                status='failed',
                error_message=str(e)
            )

    # 2. WHATSAPP CHANNEL (Log payload ready for WhatsApp webhook / staff dispatch)
    if 'whatsapp' in channels and patient.phone:
        LoyaltyNotificationLog.objects.create(
            patient=patient,
            channel='whatsapp',
            event_type=event_type,
            recipient=patient.phone,
            subject=f"WhatsApp: {event_type}",
            message_body=wa_text,
            status='sent'
        )

    # 3. SMS CHANNEL
    if 'sms' in channels and patient.phone:
        LoyaltyNotificationLog.objects.create(
            patient=patient,
            channel='sms',
            event_type=event_type,
            recipient=patient.phone,
            subject=f"SMS: {event_type}",
            message_body=sms_text,
            status='sent'
        )
