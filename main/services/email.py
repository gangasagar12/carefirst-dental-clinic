from appointments.models import EmailNotification
import re

def get_email_subject():
    return "Appointment Request Received – Carefirst Dental Clinic"

def get_email_template(patient_name):
    """
    Returns the bilingual email body template with the patient name inserted.
    """
    return f"""Hello {patient_name},

Thank you for contacting Carefirst Dental Clinic. We have received your appointment/request successfully. Our team will contact you shortly.

Regards,
Carefirst Dental Clinic

नमस्ते {patient_name},

Carefirst Dental Clinic मा सम्पर्क गर्नु भएकोमा धन्यवाद। तपाईंको अपोइन्टमेन्ट/अनुरोध सफलतापूर्वक प्राप्त भएको छ। हाम्रो टोलीले चाँडै तपाईंलाई सम्पर्क गर्नेछ।

धन्यवाद,
Carefirst Dental Clinic"""

def is_valid_email(email_address):
    """
    Basic email validation.
    """
    if not email_address:
        return False
    return re.match(r"[^@]+@[^@]+\.[^@]+", email_address) is not None

def queue_email_confirmation(name, email, inquiry_type, obj_id):
    """
    Creates a pending EmailNotification record.
    This functions as the placeholder/future-ready hook for the API integration.
    """
    if not is_valid_email(email):
        return False

    notification = EmailNotification.objects.create(
        inquiry_type=inquiry_type,
        inquiry_id=obj_id,
        patient_name=name,
        email_address=email,
        subject=get_email_subject(),
        message_text=get_email_template(name),
        status='pending'
    )
    
    # Trigger the send attempt
    send_pending_email_messages(notification.id)
    return True

def send_pending_email_messages(notification_id=None):
    """
    Simulates sending the email message.
    Currently, this acts as a placeholder. Once you configure SMTP/SendGrid/Gmail,
    replace the TODO block below with the actual Django `send_mail` logic.
    """
    if notification_id:
        notifications = EmailNotification.objects.filter(id=notification_id, status='pending')
    else:
        notifications = EmailNotification.objects.filter(status='pending')
        
    for notification in notifications:
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            # Send the email to the customer
            send_mail(
                subject=notification.subject,
                message=notification.message_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.email_address],
                fail_silently=False,
            )
            
            # If successful, mark as sent
            notification.status = 'sent'
            notification.save()
            
        except Exception as e:
            notification.status = 'failed'
            notification.save()
