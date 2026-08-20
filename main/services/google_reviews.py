import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests
from django.utils.dateparse import parse_datetime
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

GOOGLE_PLACE_DETAILS_URL = "https://places.googleapis.com/v1/places/{place_id}"
FIELD_MASK = ",".join([
    "id",
    "displayName",
    "rating",
    "userRatingCount",
    "reviews",
])


class GoogleReviewsError(Exception):
    """Raised when Google review data cannot be fetched safely."""


@dataclass(frozen=True)
class GoogleReviewData:
    google_review_id: str
    author_name: str
    author_photo: str
    author_url: str
    rating: int
    review_text: str
    relative_time: str
    publish_time: datetime | None
    language: str


@dataclass(frozen=True)
class GoogleBusinessData:
    place_id: str
    business_name: str
    google_rating: float
    review_count: int
    reviews: list[GoogleReviewData]


class GoogleReviewsClient:
    def __init__(
        self,
        api_key: str | None = None,
        place_id: str | None = None,
        timeout: int = 10,
        max_retries: int = 3,
        backoff_seconds: float = 1.5,
    ):
        load_dotenv()
        self.api_key = api_key or os.getenv("GOOGLE_PLACES_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
        self.place_id = place_id or os.getenv("GOOGLE_PLACE_ID")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

        if not self.api_key:
            raise GoogleReviewsError("GOOGLE_PLACES_API_KEY or GOOGLE_MAPS_API_KEY is not configured.")
        if not self.place_id:
            raise GoogleReviewsError("GOOGLE_PLACE_ID is not configured.")

    def fetch_business_reviews(self) -> GoogleBusinessData:
        payload = self._request_place_details()
        display_name = payload.get("displayName") or {}

        return GoogleBusinessData(
            place_id=payload.get("id") or self.place_id,
            business_name=display_name.get("text") or "Google Business",
            google_rating=float(payload.get("rating") or 0),
            review_count=int(payload.get("userRatingCount") or 0),
            reviews=[self._normalize_review(review) for review in payload.get("reviews", [])],
        )

    def _request_place_details(self) -> dict[str, Any]:
        url = GOOGLE_PLACE_DETAILS_URL.format(place_id=self.place_id)
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": FIELD_MASK,
        }

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(url, headers=headers, timeout=self.timeout)
                if response.status_code == 429 or 500 <= response.status_code < 600:
                    last_error = GoogleReviewsError(
                        f"Google Places temporary error {response.status_code}: {response.text[:250]}"
                    )
                    if attempt < self.max_retries:
                        time.sleep(self.backoff_seconds * attempt)
                        continue

                if response.status_code >= 400:
                    raise GoogleReviewsError(
                        f"Google Places API error {response.status_code}: {response.text[:250]}"
                    )

                return response.json()
            except requests.RequestException as exc:
                last_error = exc
                logger.warning("Google Places request failed on attempt %s: %s", attempt, exc)
                if attempt < self.max_retries:
                    time.sleep(self.backoff_seconds * attempt)

        raise GoogleReviewsError(f"Google Places API request failed: {last_error}")

    def _normalize_review(self, review: dict[str, Any]) -> GoogleReviewData:
        author = review.get("authorAttribution") or {}
        text = review.get("text") or review.get("originalText") or {}
        publish_time = parse_datetime(review.get("publishTime") or "")

        return GoogleReviewData(
            google_review_id=review.get("name") or self._fallback_review_id(review),
            author_name=author.get("displayName") or "Google User",
            author_photo=author.get("photoUri") or "",
            author_url=author.get("uri") or "",
            rating=int(review.get("rating") or 0),
            review_text=text.get("text") or "",
            relative_time=review.get("relativePublishTimeDescription") or "",
            publish_time=publish_time,
            language=text.get("languageCode") or "",
        )

    def _fallback_review_id(self, review: dict[str, Any]) -> str:
        author = review.get("authorAttribution") or {}
        return "|".join([
            self.place_id or "",
            author.get("displayName") or "Google User",
            review.get("publishTime") or "",
            str(review.get("rating") or ""),
        ])
