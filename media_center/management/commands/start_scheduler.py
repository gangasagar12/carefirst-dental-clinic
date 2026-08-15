import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

logger = logging.getLogger(__name__)

def sync_job():
    """Runs the actual sync command."""
    print("Running social media sync job...")
    call_command("sync_social_media")
    print("Social media sync job completed.")

def sync_google_reviews_job():
    """Runs the Google reviews sync command."""
    print("Running Google reviews sync job...")
    call_command("sync_google_reviews", quiet=True)
    print("Google reviews sync job completed.")

@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """Deletes APScheduler job execution entries older than `max_age` (7 days)."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

class Command(BaseCommand):
    help = "Runs APScheduler to automatically sync social media (YouTube/Facebook) in the background."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Add the social media sync job to run every 24 hours
        scheduler.add_job(
            sync_job,
            trigger=IntervalTrigger(days=1),
            id="sync_social_media_job",
            max_instances=1,
            replace_existing=True,
        )
        self.stdout.write("Added daily job: 'sync_social_media_job'.")

        scheduler.add_job(
            sync_google_reviews_job,
            trigger=CronTrigger(hour=2, minute=0),
            id="sync_google_reviews_job",
            max_instances=1,
            replace_existing=True,
        )
        self.stdout.write("Added daily 2:00 AM job: 'sync_google_reviews_job'.")

        # Add a maintenance job to clear out old execution records
        scheduler.add_job(
            delete_old_job_executions,
            trigger=IntervalTrigger(days=7),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        self.stdout.write("Added weekly job: 'delete_old_job_executions'.")

        try:
            self.stdout.write("Starting scheduler... (Press Ctrl+C to stop)")
            scheduler.start()
        except KeyboardInterrupt:
            self.stdout.write("Stopping scheduler...")
            scheduler.shutdown()
            self.stdout.write("Scheduler shut down successfully!")
