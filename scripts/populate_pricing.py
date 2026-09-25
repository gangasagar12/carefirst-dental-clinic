import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding='utf-8')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
if connection.vendor == 'sqlite':
    try:
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA busy_timeout = 60000;")
            cursor.execute("PRAGMA journal_mode = WAL;")
            cursor.execute("PRAGMA synchronous = NORMAL;")
    except Exception:
        pass

from main.models import PricingCategory, PricingItem

PRICING_DATA = [
    {
        "category_en": "General Dentistry",
        "category_ne": "साधारण दन्त चिकित्सा",
        "items": [
            {
                "name_en": "Registration & Check-up",
                "name_ne": "दर्ता तथा सम्पूर्ण दाँत परीक्षण",
                "price": "300"
            },
            {
                "name_en": "Digital Dental X-Ray (RVG)",
                "name_ne": "डिजिटल दाँतको एक्स-रे (RVG)",
                "price": "300"
            },
            {
                "name_en": "Specialist Consultation",
                "name_ne": "विशेषज्ञ दन्त परामर्श",
                "price": "500"
            },
            {
                "name_en": "Dental Filling (Light Cure)",
                "name_ne": "दाँत भर्ने (कम्पोजिट लाइट क्योर फिलिङ)",
                "price": "1,000 - 2,500"
            },
            {
                "name_en": "Scaling & Polishing",
                "name_ne": "दाँत सफाइ र पोलिसिङ (स्केलिङ)",
                "price": "1,000 - 1,500"
            },
            {
                "name_en": "Curettage",
                "name_ne": "क्युटेज (गिजाको भित्री सफाइ)",
                "price": "1,000"
            },
        ]
    },
    {
        "category_en": "Root Canal Treatment",
        "category_ne": "रूट क्यानल उपचार (RCT)",
        "items": [
            {
                "name_en": "Child RCT (Pulpectomy)",
                "name_ne": "बालबालिकाको रूट क्यानल (पल्पेक्टोमी)",
                "price": "2,500 - 3,500"
            },
            {
                "name_en": "Adult RCT",
                "name_ne": "वयस्क रूट क्यानल (प्रति दाँत)",
                "price": "3,500 - 5,500"
            },
            {
                "name_en": "Single-Sitting RCT",
                "name_ne": "एकै बसाइमा गरिने रूट क्यानल (Single Sitting RCT)",
                "price": "7,000 - 10,000"
            },
        ]
    },
    {
        "category_en": "Crowns & Bridges",
        "category_ne": "दाँतको क्याप तथा ब्रिज",
        "items": [
            {
                "name_en": "Dental Crown - All Metal",
                "name_ne": "मेटल क्याप (All Metal Crown)",
                "price": "4,000 per unit"
            },
            {
                "name_en": "Dental Crown - Metal Ceramic",
                "name_ne": "मेटल सिरामिक क्याप (PFM Crown)",
                "price": "5,000 per unit"
            },
            {
                "name_en": "Dental Crown - E-max",
                "name_ne": "ई-म्याक्स अल-सिरामिक क्याप (E-max Crown)",
                "price": "12,000"
            },
            {
                "name_en": "Dental Crown - Zirconia",
                "name_ne": "प्रिमियम जिर्कोनिया क्याप (Zirconia Crown)",
                "price": "17,000 - 20,000"
            },
        ]
    },
    {
        "category_en": "Tooth Extraction",
        "category_ne": "दाँत निकाल्ने सेवा",
        "items": [
            {
                "name_en": "Child Extraction",
                "name_ne": "बालबालिकाको दाँत निकाल्ने",
                "price": "500 - 1,000"
            },
            {
                "name_en": "Adult Extraction",
                "name_ne": "सामान्य दाँत निकाल्ने (वयस्क)",
                "price": "1,000 - 2,500"
            },
            {
                "name_en": "Wisdom Tooth Extraction",
                "name_ne": "बुद्धि बंगारा निकाल्ने (Wisdom Tooth)",
                "price": "2,500 - 5,000"
            },
            {
                "name_en": "Surgical Extraction (Impaction)",
                "name_ne": "शल्यक्रियाद्वारा बंगारा निकाल्ने (Surgical Extraction)",
                "price": "5,000 - 15,000"
            },
        ]
    },
    {
        "category_en": "Dentures",
        "category_ne": "नक्कली दाँत (डेन्चर)",
        "items": [
            {
                "name_en": "Removable Partial Denture (RPD)",
                "name_ne": "निकाल्न मिल्ने आंशिक नक्कली दाँत (RPD)",
                "price": "1,000 + 500/tooth"
            },
            {
                "name_en": "Complete Denture (CD)",
                "name_ne": "पूरै मुखको नक्कली दाँत सेट (Complete Denture)",
                "price": "20,000 - 35,000"
            },
        ]
    },
    {
        "category_en": "Orthodontic Treatment",
        "category_ne": "तार बाँध्ने उपचार (अर्थोडोन्टिक्स / ब्रेसेस)",
        "items": [
            {
                "name_en": "Braces Treatment",
                "name_ne": "तार बाँध्ने उपचार (मेटल / सिरेमिक / क्लियर अलाइनर)",
                "price": "35,000 - 1,50,000"
            },
        ]
    },
    {
        "category_en": "Periodontal Treatment",
        "category_ne": "गिजा रोगको विशेष उपचार",
        "items": [
            {
                "name_en": "Deep Cleaning (Root Planing)",
                "name_ne": "गहिरो जरा सफाइ (Root Planing / Deep Cleaning)",
                "price": "2,000 - 4,000"
            },
            {
                "name_en": "Flap Surgery",
                "name_ne": "गिजाको शल्यक्रिया (Flap Surgery)",
                "price": "5,000 - 15,000"
            },
            {
                "name_en": "Splinting",
                "name_ne": "हल्लिरहेको दाँत बाँध्ने (Splinting)",
                "price": "3,000 - 8,000"
            },
        ]
    },
    {
        "category_en": "Dental Implants",
        "category_ne": "डेन्टल इम्प्लान्ट (दाँत प्रत्यारोपण)",
        "items": [
            {
                "name_en": "Dental Implant (Fixture Only)",
                "name_ne": "टाइटेनियम डेन्टल इम्प्लान्ट (Fixture Only)",
                "price": "45,000 - 65,000"
            },
            {
                "name_en": "Bone Grafting",
                "name_ne": "हड्डी थप्ने प्रक्रिया (Bone Grafting)",
                "price": "10,000 - 30,000"
            },
        ]
    },
]

def run():
    print("Clearing and re-populating pricing categories and items with English & Nepali translations...")
    PricingItem.objects.all().delete()
    PricingCategory.objects.all().delete()

    cat_order = 1
    item_order = 1

    for block in PRICING_DATA:
        cat = PricingCategory.objects.create(
            name=block["category_en"],
            name_en=block["category_en"],
            name_ne=block["category_ne"],
            order=cat_order
        )
        cat_order += 1
        print(f"[Category] {cat.name_en} -> {cat.name_ne}")

        for item_data in block["items"]:
            item = PricingItem.objects.create(
                category=cat,
                name=item_data["name_en"],
                name_en=item_data["name_en"],
                name_ne=item_data["name_ne"],
                price=item_data["price"],
                price_en=item_data["price"],
                price_ne=item_data["price"],
                order=item_order
            )
            item_order += 1
            print(f"   [Item] {item.name_en} -> {item.name_ne} ({item.price})")

    print("\nPricing data populated successfully with complete English and Nepali translations!")

if __name__ == '__main__':
    run()
