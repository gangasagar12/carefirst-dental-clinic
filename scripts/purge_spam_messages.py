import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding='utf-8')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from main.models import ContactMessage
from appointments.models import Appointment
from main.services.spam_filter import is_spam_submission

def purge_spam():
    print("=" * 60)
    print("PURGING SPAM SUBMISSIONS FROM DATABASE")
    print("=" * 60)

    # 1. Contact Messages
    deleted_contacts = 0
    for msg in ContactMessage.objects.all():
        spam, reason = is_spam_submission(name=msg.name, email=msg.email, message=msg.message, subject=msg.subject)
        if spam:
            msg.delete()
            deleted_contacts += 1

    print(f"[OK] Purged {deleted_contacts} spam ContactMessages.")

    # 2. Appointments
    deleted_appointments = 0
    for app in Appointment.objects.all():
        spam, reason = is_spam_submission(name=app.full_name, email=app.email, message=app.message)
        if spam:
            app.delete()
            deleted_appointments += 1

    print(f"[OK] Purged {deleted_appointments} spam Appointments.")
    print("=" * 60)
    print("SPAM PURGE COMPLETE! Clean inbox & dashboard restored.")
    print("=" * 60)

if __name__ == '__main__':
    purge_spam()
