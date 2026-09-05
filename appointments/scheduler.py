import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def schedule_appointment_reminders():
    """
    Hook to register the daily 24h appointment reminder job in APScheduler.
    Runs every morning at 08:00 AM (local time).
    """
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from django_apscheduler.jobstores import DjangoJobStore, register_events
        from appointments.reminder_services import send_24h_appointment_reminders

        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_24h_appointment_reminders,
            trigger="cron",
            hour=8,
            minute=0,
            id="send_24h_appointment_reminders",
            max_instances=1,
            replace_existing=True,
        )

        register_events(scheduler)
        scheduler.start()
        logger.info("APScheduler: Registered daily 24h appointment reminder job at 08:00 AM.")
        return scheduler
    except Exception as e:
        logger.warning(f"Could not initialize APScheduler appointment reminders: {e}")
        return None
