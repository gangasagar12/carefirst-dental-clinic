"""
CareFirst Dental Clinic - Dynamic Post-Deployment Setup & Data Initializer
Runs automatically on cloud deploy (Render, Railway, Heroku, Fly.io, etc.)
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from main.models import Service

def setup_superuser():
    """
    Dynamically creates or updates the admin superuser from environment variables.
    Supported variables:
      - DJANGO_SUPERUSER_USERNAME or ADMIN_USERNAME (default: 'admin')
      - DJANGO_SUPERUSER_EMAIL or ADMIN_EMAIL (default: 'carefirstdentalclinic@gmail.com')
      - DJANGO_SUPERUSER_PASSWORD or ADMIN_PASSWORD
    """
    User = get_user_model()
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME') or os.environ.get('ADMIN_USERNAME')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL') or os.environ.get('ADMIN_EMAIL') or 'carefirstdentalclinic@gmail.com'
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD') or os.environ.get('ADMIN_PASSWORD')

    if not username or not password:
        print("[INFO] No DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD provided in env. Skipping superuser auto-creation.")
        return

    try:
        user = User.objects.filter(username=username).first()
        if user:
            user.set_password(password)
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print(f"[SUCCESS] Superuser '{username}' updated successfully.")
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"[SUCCESS] Superuser '{username}' created successfully.")
    except Exception as e:
        print(f"[WARNING] Could not auto-create superuser: {e}")

def seed_core_services():
    """
    Ensures all primary CareFirst clinical services are seeded in the database.
    """
    core_services = [
        {
            "title": "Root Canal Treatment",
            "slug": "root-canal-treatment",
            "category": "endodontics",
            "category_label": "ENDODONTICS",
            "icon": "bi-bandaid",
            "is_popular": True,
            "starting_price": "4,500",
            "custom_template": "services/root_canal.html",
            "order": 1,
            "features": "Rotary Endodontic Technology\nDigital Apex Locator Precision\nSingle-Sitting or Multi-Visit Care\nMicroscopic Canal Debridement"
        },
        {
            "title": "Dental Implants",
            "slug": "dental-implants",
            "category": "implants",
            "category_label": "IMPLANTOLOGY",
            "icon": "bi-shield-plus",
            "is_popular": True,
            "starting_price": "55,000",
            "custom_template": "services/dental_implants.html",
            "order": 2,
            "features": "Grade-5 Titanium Implants\nComputer-Guided Placement\nLifetime Bone Integration\nNatural Tooth Appearance"
        },
        {
            "title": "Teeth Whitening",
            "slug": "teeth-whitening",
            "category": "cosmetic",
            "category_label": "COSMETIC DENTISTRY",
            "icon": "bi-stars",
            "is_popular": True,
            "starting_price": "6,000",
            "custom_template": "services/teeth_whitening.html",
            "order": 3,
            "features": "In-Office Laser Light Activation\nUp to 6-8 Shades Lighter\nEnamel-Safe Formulation\nLong-Lasting Bright Smile"
        },
        {
            "title": "Composite Fillings",
            "slug": "composite-fillings",
            "category": "restorative",
            "category_label": "RESTORATIVE CARE",
            "icon": "bi-gem",
            "is_popular": False,
            "starting_price": "1,200",
            "custom_template": "services/composite_fillings.html",
            "order": 4,
            "features": "Tooth-Colored Resin Matrix\nPrecision Shade Matching\nMercury-Free Formulation\nInstant Light-Curing Strength"
        },
        {
            "title": "Orthodontic Braces & Aligners",
            "slug": "orthodontic-braces",
            "category": "orthodontics",
            "category_label": "ORTHODONTICS",
            "icon": "bi-emoji-smile",
            "is_popular": True,
            "starting_price": "40,000",
            "custom_template": "services/braces_aligners.html",
            "order": 5,
            "features": "Metal & Ceramic Braces\nClear Invisible Aligners\nBite Alignment Correction\nCustom Smile Mapping"
        },
        {
            "title": "Dental Crowns & Bridges",
            "slug": "dental-crowns-bridges",
            "category": "prosthodontics",
            "category_label": "PROSTHODONTICS",
            "icon": "bi-award",
            "is_popular": False,
            "starting_price": "7,000",
            "custom_template": "services/crowns_bridges.html",
            "order": 6,
            "features": "Zirconia & PFM Options\nCAD/CAM Digital Milling\nNatural Tooth Contour\nHigh Fracture Resistance"
        },
        {
            "title": "Tooth Extraction & Wisdom Surgery",
            "slug": "tooth-extraction",
            "category": "oral-surgery",
            "category_label": "ORAL SURGERY",
            "icon": "bi-scissors",
            "is_popular": False,
            "starting_price": "1,000",
            "custom_template": "services/tooth_extraction.html",
            "order": 7,
            "features": "Pain-Free Local Anesthesia\nImpacted Wisdom Molar Extraction\nGentle Tissue-Preserving Technique\nPost-Op Care & Follow-Up"
        },
        {
            "title": "Teeth Scaling & Deep Polishing",
            "slug": "teeth-scaling-polishing",
            "category": "preventive",
            "category_label": "PREVENTIVE CARE",
            "icon": "bi-water",
            "is_popular": True,
            "starting_price": "1,500",
            "custom_template": "services/teeth_scaling.html",
            "order": 8,
            "features": "Ultrasonic Plaque Removal\nStain & Tartar Elimination\nAir-Flow Prophy Polishing\nFresh Breath & Gum Health"
        },
        {
            "title": "Digital Dental X-Ray (RVG & OPG)",
            "slug": "digital-dental-xray",
            "category": "diagnostics",
            "category_label": "DIAGNOSTICS",
            "icon": "bi-camera",
            "is_popular": False,
            "starting_price": "500",
            "custom_template": "services/digital_xray.html",
            "order": 9,
            "features": "Ultra-Low Radiation RVG\nFull Panoramic OPG Screening\nInstant High-Res Image Display\nPrecise Pathology Detection"
        }
    ]

    created_count = 0
    updated_count = 0

    for s_data in core_services:
        slug = s_data["slug"]
        service, created = Service.objects.get_or_create(slug=slug, defaults=s_data)
        if created:
            created_count += 1
        else:
            # Update fields to match current code configuration
            for key, val in s_data.items():
                setattr(service, key, val)
            service.is_active = True
            service.save()
            updated_count += 1

    print(f"[SUCCESS] Core Clinical Services Verified: {created_count} created, {updated_count} verified/updated (Total active: {Service.objects.filter(is_active=True).count()}).")

def verify_system_health():
    """
    Performs quick DB queries to ensure everything is ready for live traffic.
    """
    from appointments.models import Appointment
    total_services = Service.objects.count()
    total_appointments = Appointment.objects.count()
    print(f"[HEALTH] Database connection verified. Services: {total_services}, Appointments in DB: {total_appointments}.")

def main():
    print("--------------------------------------------------")
    print(" CareFirst Dynamic Deployment Initializer")
    print("--------------------------------------------------")
    setup_superuser()
    seed_core_services()
    verify_system_health()
    print("--------------------------------------------------")
    print("[READY] Application is initialized and ready for production.")

if __name__ == '__main__':
    main()
