# CareFirst Dental Clinic - WhatsApp Reception Quick Dispatch & 24h Reminder Engine

## 1. Executive Summary

This module introduces two mission-critical patient communication capabilities to the CareFirst Dental Clinic platform:
1. **1-Click WhatsApp Quick Dispatch for Reception**: Instant receptionist tool located at `/dashboard/appointments/` and `/dashboard/appointments/<id>/` that crafts personalized WhatsApp messages with booking IDs, appointments times, Google Maps clinic directions, and digital passes.
2. **Automated 24-Hour Pre-Appointment Reminders**: Daily background cron worker (powered by `django_apscheduler` and management commands) that scans tomorrow's confirmed visits, dispatches multi-channel email alerts, updates database reminder audit fields, and provides a manual 1-click trigger in the clinic dashboard overview.

---

## 2. Architecture & Components

### A. Phone Sanitizer & WhatsApp Dispatch Engine (`appointments/whatsapp_services.py`)
- **Phone Number Normalization**:
  - Nepal 10-digit mobile (`98XXXXXXXX`, `97XXXXXXXX`) ➔ Normalized to `97798XXXXXXXX`.
  - Kathmandu 9-digit landline (`01-XXXXXXX`) ➔ Normalized to `9771XXXXXXX`.
  - Strips spaces, dashes, parentheses, and leading plus/zeroes.
- **4 Pre-Formatted Clinical Message Templates**:
  - `confirmation`: Booking details, doctor assigned, branch location, Google Maps link, digital QR pass URL.
  - `reminder`: 24-hour pre-visit checklist, scheduled slot, location link, and arrival notice.
  - `reschedule`: Updated schedule notification with patient confirmation link.
  - `inquiry`: Warm welcome and follow-up for initial inquiries.

### B. Automated 24-Hour Reminder Engine (`appointments/reminder_services.py`)
- Scans `Appointment` records where `preferred_date == tomorrow` and `status == 'confirmed'`.
- Sends responsive HTML reminder emails with direct links to the patient's digital pass.
- Updates appointment model fields:
  - `reminder_sent = True`
  - `reminder_sent_at = timezone.now()`
  - `reminder_channel = 'email_whatsapp'`
  - `reminder_count += 1`
- Generates summary statistics and ready-to-use WhatsApp dispatch links for reception backup.

### C. Management Command & Cron Scheduler
- **Management Command**:
  ```bash
  # Execute dry-run scan
  python manage.py run_appointment_reminders --dry-run

  # Execute live scan and dispatch
  python manage.py run_appointment_reminders
  ```
- **APScheduler Hook (`appointments/scheduler.py`)**:
  - Automatically runs every morning at 08:00 AM NPT.

### D. Reception Dashboard UI Integrations
- **Appointments Table (`/dashboard/appointments/`)**:
  - Green WhatsApp action button on every appointment row opens the dynamic WhatsApp Quick Dispatch modal.
  - Interactive tabs switch between Confirmation, Reminder, Reschedule, and Inquiry in real-time.
  - One-click "Copy Message Text" and "Open & Send via WhatsApp" buttons.
  - Top reminder alert banner with count of upcoming visits and instant 1-click dispatch trigger.
- **Appointment Detail View (`/dashboard/appointments/<id>/`)**:
  - Dedicated WhatsApp Quick Dispatch card.
  - 24h Reminder status widget displaying dispatch timestamps and channels.
- **Dashboard Command Center Overview (`/dashboard/`)**:
  - Blue notification bar displaying pending 24h reminders for tomorrow with quick filter and batch dispatch trigger.

---

## 3. Database Schema Extensions

Added to `appointments.models.Appointment`:
- `reminder_sent`: Boolean (default=False, db_index=True)
- `reminder_sent_at`: DateTime (null=True, blank=True)
- `reminder_channel`: CharField (default='whatsapp')
- `reminder_count`: PositiveIntegerField (default=0)
