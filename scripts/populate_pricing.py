import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from main.models import PricingCategory, PricingItem

pricing_data = [
    {
        "category": "General Dentistry",
        "items": [
            ("Registration & Check-up", "300"),
            ("Digital Dental X-Ray (RVG)", "300"),
            ("Specialist Consultation", "500"),
            ("Dental Filling (Light Cure)", "1,000 - 2,500"),
            ("Scaling & Polishing", "1,000 - 1,500"),
            ("Curettage", "1,000"),
        ]
    },
    {
        "category": "Root Canal Treatment",
        "items": [
            ("Child RCT (Pulpectomy)", "2,500 - 3,500"),
            ("Adult RCT", "3,500 - 5,500"),
            ("Single-Sitting RCT", "7,000 - 10,000"),
        ]
    },
    {
        "category": "Crowns & Bridges",
        "items": [
            ("Dental Crown - All Metal", "4,000 per unit"),
            ("Dental Crown - Metal Ceramic", "5,000 per unit"),
            ("Dental Crown - E-max", "12,000"),
            ("Dental Crown - Zirconia", "17,000 - 20,000"),
        ]
    },
    {
        "category": "Tooth Extraction",
        "items": [
            ("Child Extraction", "500 - 1,000"),
            ("Adult Extraction", "1,000 - 2,500"),
            ("Wisdom Tooth Extraction", "2,500 - 5,000"),
            ("Surgical Extraction (Impaction)", "5,000 - 15,000"),
        ]
    },
    {
        "category": "Dentures",
        "items": [
            ("Removable Partial Denture (RPD)", "1,000 + 500/tooth"),
            ("Complete Denture (CD)", "20,000 - 35,000"),
        ]
    },
    {
        "category": "Orthodontic Treatment",
        "items": [
            ("Braces Treatment", "35,000 - 1,50,000"),
        ]
    },
    {
        "category": "Periodontal Treatment",
        "items": [
            ("Deep Cleaning (Root Planing)", "2,000 - 4,000"),
            ("Flap Surgery", "5,000 - 15,000"),
            ("Splinting", "3,000 - 8,000"),
        ]
    },
    {
        "category": "Dental Implants",
        "items": [
            ("Dental Implant (Fixture Only)", "45,000 - 65,000"),
            ("Bone Grafting", "10,000 - 30,000"),
        ]
    },
]

def run():
    print("Clearing existing pricing data...")
    PricingCategory.objects.all().delete()
    PricingItem.objects.all().delete()

    cat_order = 1
    item_order = 1
    
    for block in pricing_data:
        category_name = block["category"]
        cat = PricingCategory.objects.create(name=category_name, order=cat_order)
        cat_order += 1
        
        for name, price in block["items"]:
            PricingItem.objects.create(
                category=cat,
                name=name,
                price=price,
                order=item_order
            )
            item_order += 1

    print("Pricing data populated successfully.")

if __name__ == '__main__':
    run()
