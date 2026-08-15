import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from main.models import GoogleBusiness, GoogleReview
from main.services.google_reviews import GoogleReviewsClient, GoogleReviewsError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Synchronize Google Business rating and latest Google reviews into the database."

    def add_arguments(self, parser):
        parser.add_argument("--quiet", action="store_true", help="Only output errors.")

    def handle(self, *args, **options):
        quiet = options["quiet"]

        try:
            data = GoogleReviewsClient().fetch_business_reviews()
        except GoogleReviewsError as exc:
            GoogleBusiness.objects.filter(place_id__isnull=False).update(
                sync_status="Failed",
                sync_message=str(exc),
                updated_at=timezone.now(),
            )
            logger.exception("Google reviews sync failed")
            raise CommandError(str(exc))

        now = timezone.now()
        with transaction.atomic():
            business, _ = GoogleBusiness.objects.update_or_create(
                place_id=data.place_id,
                defaults={
                    "business_name": data.business_name,
                    "google_rating": data.google_rating,
                    "review_count": data.review_count,
                    "last_synced": now,
                    "sync_status": "Success",
                    "sync_message": f"Synced {len(data.reviews)} latest reviews.",
                },
            )

            synced_ids = []
            for review in data.reviews:
                synced_ids.append(review.google_review_id)
                GoogleReview.objects.update_or_create(
                    google_review_id=review.google_review_id,
                    defaults={
                        "business": business,
                        "author_name": review.author_name,
                        "author_photo": review.author_photo,
                        "author_url": review.author_url,
                        "rating": review.rating,
                        "review_text": review.review_text,
                        "relative_time": review.relative_time,
                        "publish_time": review.publish_time,
                        "language": review.language,
                        "is_active": True,
                    },
                )

            if synced_ids:
                GoogleReview.objects.filter(business=business).exclude(
                    google_review_id__in=synced_ids
                ).update(is_active=False)

        if not quiet:
            self.stdout.write(self.style.SUCCESS(
                f"Google reviews synced: {business.business_name}, "
                f"{business.google_rating} rating, {business.review_count} reviews."
            ))
