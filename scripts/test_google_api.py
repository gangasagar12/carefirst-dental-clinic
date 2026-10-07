import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_PLACES_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
place_id = os.getenv("GOOGLE_PLACE_ID")

print(f"Testing with API Key: {api_key[:8]}... Place ID: {place_id}")

# Test 1: New API with languageCode=en
url1 = f"https://places.googleapis.com/v1/places/{place_id}?languageCode=en"
r = requests.get(f"https://places.googleapis.com/v1/places/{place_id}", headers={"X-Goog-Api-Key": api_key, "X-Goog-FieldMask": "*"})
data = r.json()
print("All keys with * mask:", list(data.keys()))
if "reviews" in data:
    print("Found reviews in * mask! Count:", len(data["reviews"]))


