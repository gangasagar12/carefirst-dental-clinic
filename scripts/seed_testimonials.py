import os
import django
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from main.models import Testimonial

testimonials = [
    {
        "patient_name": "Sunita Karki",
        "treatment": "Clear Aligners",
        "review": "I had severe crowding for years and always hid my smile. After clear aligners at Carefirst Dental Clinic, I smile in every photo now. The team was so supportive.",
        "rating": 5,
        "is_active": True
    },
    {
        "patient_name": "Roshan Poudel",
        "treatment": "Smile Makeover",
        "review": "My smile makeover with 8 veneers was absolutely life-changing. Dr. Niko's team crafted a smile that looks completely natural \u2014 not overdone at all.",
        "rating": 5,
        "is_active": True
    },
    {
        "patient_name": "Anita Dhungana",
        "treatment": "Zoom! Teeth Whitening",
        "review": "Got my teeth whitened before my wedding \u2014 8 shades in one session! The results lasted for months and the process was completely painless.",
        "rating": 5,
        "is_active": True
    },
    {
        "patient_name": "Prakash Adhikari",
        "treatment": "Dual Dental Implants",
        "review": "I was missing two teeth and it affected my confidence. The dental implants look and feel exactly like my natural teeth. I can eat anything now!",
        "rating": 5,
        "is_active": True
    },
    {
        "patient_name": "Rekha Tamang",
        "treatment": "Composite Veneer Bonding",
        "review": "Composite veneers in one sitting \u2014 I couldn't believe how different I looked when I saw myself. The gap between my front teeth is gone.",
        "rating": 5,
        "is_active": True
    },
    {
        "patient_name": "Deepak Shrestha",
        "treatment": "Full Arch Rehabilitation",
        "review": "Full arch rehabilitation was a big investment but absolutely worth it. I now have a functional, beautiful smile. The team's skill is exceptional.",
        "rating": 5,
        "is_active": True
    }
]

print('Seeding Testimonials...')
Testimonial.objects.all().delete()
for t_data in testimonials:
    Testimonial.objects.create(**t_data)
print('Successfully seeded Testimonials!')
