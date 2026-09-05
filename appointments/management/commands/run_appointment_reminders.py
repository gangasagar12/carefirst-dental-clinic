import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from appointments.reminder_services import send_24h_appointment_reminders


class Command(BaseCommand):
    help = "Scan upcoming confirmed appointments scheduled for tomorrow and dispatch 24-hour pre-visit reminders."

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Target appointment date in YYYY-MM-DD format (defaults to tomorrow).'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate reminder scan without updating database records or sending real emails.'
        )

    def handle(self, *args, **options):
        date_str = options.get('date')
        dry_run = options.get('dry_run', False)

        target_date = None
        if date_str:
            try:
                target_date = datetime.date.fromisoformat(date_str)
            except ValueError:
                self.stderr.write(self.style.ERROR(f"Invalid date format: {date_str}. Expected YYYY-MM-DD."))
                return

        if not target_date:
            target_date = timezone.localdate() + datetime.timedelta(days=1)

        self.stdout.write(self.style.NOTICE(
            f"🔍 Scanning appointments for 24h reminder (Target Date: {target_date}, Dry Run: {dry_run})..."
        ))

        results = send_24h_appointment_reminders(target_date=target_date, dry_run=dry_run)

        total = results['total_appointments']
        emails = results['emails_sent']
        wa = results['whatsapp_ready']

        self.stdout.write(self.style.SUCCESS(
            f"✅ Reminder Scan Completed for {target_date}:\n"
            f"   - Total Scheduled: {total}\n"
            f"   - Emails Dispatched: {emails}\n"
            f"   - WhatsApp Links Ready: {wa}"
        ))
