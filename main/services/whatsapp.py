import re
from appointments.models import WhatsAppNotification

def get_whatsapp_template(patient_name):
    """
    Returns the bilingual message template with the patient name inserted.
    """
    return f"""Hello {patient_name}, thank you for contacting *Carefirst Dental Clinic*. We have received your appointment/request successfully. Our team will contact you shortly.

नमस्ते {patient_name}, *Carefirst Dental Clinic* मा सम्पर्क गर्नु भएकोमा धन्यवाद। तपाईंको अपोइन्टमेन्ट/अनुरोध सफलतापूर्वक प्राप्त भएको छ। हाम्रो टोलीले चाँडै तपाईंलाई सम्पर्क गर्नेछ।"""

def is_valid_phone(phone_number):
    """
    Basic validation to check if a phone number contains at least 10 digits.
    """
    if not phone_number:
        return False
    digits = re.sub(r'\D', '', phone_number)
    return len(digits) >= 10

def queue_whatsapp_confirmation(name, phone, inquiry_type, obj_id):
    """
    Creates a pending WhatsAppNotification record.
    This functions as the placeholder/future-ready hook for the API integration.
    """
    if not is_valid_phone(phone):
        # Create record but mark it failed directly if the number is invalid
        WhatsAppNotification.objects.create(
            inquiry_type=inquiry_type,
            inquiry_id=obj_id,
            patient_name=name,
            phone_number=phone or "N/A",
            message_text=get_whatsapp_template(name),
            status='failed'
        )
        return False

    notification = WhatsAppNotification.objects.create(
        inquiry_type=inquiry_type,
        inquiry_id=obj_id,
        patient_name=name,
        phone_number=phone,
        message_text=get_whatsapp_template(name),
        status='pending'
    )
    
    # Trigger the send attempt
    send_pending_whatsapp_messages(notification.id)
    return True

def send_pending_whatsapp_messages(notification_id=None):
    """
    Simulates sending the WhatsApp message.
    Currently, this acts as a placeholder. Once you get Meta Cloud API credentials,
    replace the TODO block below with the actual `requests.post()` call.
    """
    if notification_id:
        notifications = WhatsAppNotification.objects.filter(id=notification_id, status='pending')
    else:
        notifications = WhatsAppNotification.objects.filter(status='pending')
        
    for notification in notifications:
        try:
            # =========================================================================
            # TODO: INTEGRATE META WHATSAPP CLOUD API OR TWILIO HERE
            # 
            # 1. Retrieve API Keys from settings.py or .env (e.g., META_ACCESS_TOKEN)
            # 2. Extract phone number: phone = notification.phone_number
            # 3. Clean phone format if needed (e.g. +977...)
            # 4. Make REST API request:
            #    response = requests.post(
            #        'https://graph.facebook.com/v17.0/<PHONE_NUMBER_ID>/messages',
            #        headers={'Authorization': f'Bearer {settings.META_ACCESS_TOKEN}'},
            #        json={
            #            "messaging_product": "whatsapp",
            #            "to": phone,
            #            "type": "text",
            #            "text": {"body": notification.message_text}
            #        }
            #    )
            # 5. If response.status_code == 200, mark as 'sent'. Else mark as 'failed'.
            # =========================================================================
            
            # Since this is currently a placeholder module, we leave it as 'pending'
            # (or mark as sent if you just want to clear the queue for testing).
            # For now, we will leave it as 'pending' so you can see them in the admin dashboard.
            pass
            
        except Exception as e:
            notification.status = 'failed'
            notification.save()
