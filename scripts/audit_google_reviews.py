import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding='utf-8')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from main.models import GoogleBusiness, GoogleReview
from main.services.google_reviews import GoogleReviewsClient, GoogleReviewsError

print("=== GOOGLE REVIEWS AUDIT ===")
api_key = os.getenv("GOOGLE_PLACES_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
place_id = os.getenv("GOOGLE_PLACE_ID")
print(f"GOOGLE_PLACES_API_KEY exists: {bool(api_key)} (length: {len(api_key) if api_key else 0})")
print(f"GOOGLE_PLACE_ID: {place_id}")

print(f"\nGoogleBusiness records: {GoogleBusiness.objects.count()}")
for gb in GoogleBusiness.objects.all():
    print(f"  ID: {gb.id}")
    print(f"  Business Name: {gb.business_name}")
    print(f"  Place ID: {gb.place_id}")
    print(f"  Google Rating: {gb.google_rating}")
    print(f"  Review Count: {gb.review_count}")
    print(f"  Sync Status: {gb.sync_status}")
    print(f"  Sync Message: {gb.sync_message}")
    print(f"  Last Synced: {gb.last_synced}")

print(f"\nGoogleReview records: {GoogleReview.objects.count()}")
for gr in GoogleReview.objects.all():
    print(f"  [{gr.id}] business_id={gr.business_id} {gr.author_name} ({gr.rating}★) active={gr.is_active}: {gr.review_text[:60]}...")


print("\nAttempting GoogleReviewsClient sync test...")
try:
    client = GoogleReviewsClient()
    data = client.fetch_business_reviews()
    print("Fetch SUCCESS!")
    print(f"Business: {data.business_name}")
    print(f"Rating: {data.google_rating}")
    print(f"Review count: {data.review_count}")
    print(f"Reviews fetched: {len(data.reviews)}")
    import requests, json
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    resp = requests.get(url, headers={"X-Goog-Api-Key": api_key, "X-Goog-FieldMask": "id,displayName,rating,userRatingCount,reviews"})
    print("Raw API response:", json.dumps(resp.json(), indent=2))
except Exception as e:
    print(f"Fetch FAILED: {type(e).__name__} - {e}")
