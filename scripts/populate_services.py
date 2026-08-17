import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from main.models import Service

services_data = [
    {
        'title': 'General Dentistry',
        'slug': 'general-dentistry',
        'category': 'general',
        'category_label': 'GENERAL CARE',
        'icon': 'bi-tooth',
        'image': 'services/niko1.jpeg', # Using path strings for now as they match the old static calls
        'is_popular': False,
        'features': "Routine check-ups\nPreventive care\nOral health assessment",
        'starting_price': '1,000',
        'custom_template': 'services/general_dentistry.html',
        'order': 1,
    },
    {
        'title': 'Digital Dental X-Ray',
        'slug': 'digital-dental-x-ray',
        'category': 'diagnostics',
        'category_label': 'DIAGNOSTICS',
        'icon': 'bi-display',
        'image': 'services/dental_x-ray.jpg',
        'is_popular': False,
        'features': "Low radiation imaging\nAccurate diagnosis\nDigital technology",
        'starting_price': '800',
        'custom_template': 'services/digital_xray.html',
        'order': 2,
    },
    {
        'title': 'Dental Filling',
        'slug': 'dental-filling',
        'category': 'restorative',
        'category_label': 'RESTORATIVE',
        'icon': 'bi-bandaid',
        'image': 'services/filling_hero.png',
        'is_popular': False,
        'features': "Tooth-colored fillings\nCavity protection\nNatural appearance",
        'starting_price': '1,500',
        'custom_template': 'services/dental_filling.html',
        'order': 3,
    },
    {
        'title': 'Root Canal Treatment',
        'slug': 'root-canal-treatment',
        'category': 'endodontics',
        'category_label': 'ENDODONTICS',
        'icon': 'bi-droplet',
        'image': 'services/rct_feat_painfree.png',
        'is_popular': False,
        'features': "Pain relief\nSave natural tooth\nAdvanced rotary technology",
        'starting_price': '7,000',
        'custom_template': 'services/root_canal.html',
        'order': 4,
    },
    {
        'title': 'Dental Implants',
        'slug': 'dental-implants',
        'category': 'implants',
        'category_label': 'IMPLANTS',
        'icon': 'bi-gear-wide-connected',
        'image': 'services/dental-implant-hero.jpg',
        'is_popular': True,
        'features': "Permanent tooth replacement\nStrong & natural-looking\nLong-lasting results",
        'starting_price': '60,000',
        'custom_template': 'services/dental_implants.html',
        'order': 5,
    },
    {
        'title': 'Tooth Extraction',
        'slug': 'tooth-extraction',
        'category': 'oral-surgery',
        'category_label': 'ORAL SURGERY',
        'icon': 'bi-scissors',
        'image': 'services/toothextraction-hero.jpg',
        'is_popular': False,
        'features': "Safe & painless extraction\nWisdom tooth removal\nQuick recovery",
        'starting_price': '1,500',
        'custom_template': 'services/tooth_extraction.html',
        'order': 6,
    },
    {
        'title': 'Dentures',
        'slug': 'dentures',
        'category': 'prosthodontics',
        'category_label': 'PROSTHODONTICS',
        'icon': 'bi-layers',
        'image': 'services/dentures-hero.jpeg',
        'is_popular': False,
        'features': "Complete & partial dentures\nComfortable fit\nImprove chewing & smile",
        'starting_price': '25,000',
        'custom_template': 'services/dentures.html',
        'order': 7,
    },
    {
        'title': 'Crowns & Bridges',
        'slug': 'crowns-and-bridges',
        'category': 'restorative',
        'category_label': 'RESTORATIVE',
        'icon': 'bi-shield-check',
        'image': 'services/zirconia-crown.jpg',
        'is_popular': False,
        'features': "Strong & durable crowns\nNatural aesthetics\nRestore function",
        'starting_price': '15,000',
        'custom_template': 'services/crowns_bridges.html',
        'order': 8,
    },
    {
        'title': 'Orthodontic Treatment',
        'slug': 'orthodontic-treatment-braces',
        'category': 'orthodontics',
        'category_label': 'ORTHODONTICS',
        'icon': 'bi-bezier2',
        'image': 'services/braces-hero.jpg',
        'is_popular': False,
        'features': "Braces & aligners\nStraighten your teeth\nImprove bite & smile",
        'starting_price': '45,000',
        'custom_template': 'services/orthodontics.html',
        'order': 9,
    },
    {
        'title': 'Periodontal Treatment',
        'slug': 'periodontal-treatment-gum',
        'category': 'preventive',
        'category_label': 'PERIODONTAL CARE',
        'icon': 'bi-flower1',
        'image': 'services/periodontal-hero.jpg',
        'is_popular': False,
        'features': "Gum disease treatment\nDeep cleaning\nHealthy gums",
        'starting_price': '2,000',
        'custom_template': 'services/periodontal.html',
        'order': 10,
    },
    {
        'title': 'Scaling & Polishing',
        'slug': 'scaling-and-polishing',
        'category': 'preventive',
        'category_label': 'PREVENTIVE',
        'icon': 'bi-stars',
        'image': 'services/scaling-polishing-hero.jpg', # Assuming a similar naming convention
        'is_popular': False,
        'features': "Stain Removal\nGum Health\nFresh Breath",
        'starting_price': '1,500',
        'custom_template': 'services/scaling_polishing.html',
        'order': 11,
    }
]

def run():
    print("Clearing existing services...")
    Service.objects.all().delete()
    
    for item in services_data:
        s = Service.objects.create(**item)
        print(f"Created: {s.title}")
    
    print("Done!")

if __name__ == '__main__':
    run()
