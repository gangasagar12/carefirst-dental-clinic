import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding='utf-8')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from main.models import Doctor, Testimonial, SEOFAQ, SiteSettings, AboutPageSettings

def fix_all():
    print("Checking Doctor records...")
    for d in Doctor.objects.all():
        changed = False
        if d.nmc_number and "31229" in d.nmc_number:
            d.nmc_number = d.nmc_number.replace("31229", "32524")
            changed = True
        if d.qualifications and "31229" in d.qualifications:
            d.qualifications = d.qualifications.replace("31229", "32524")
            changed = True
        if hasattr(d, 'qualifications_ne') and d.qualifications_ne:
            if "३१२२९" in d.qualifications_ne or "31229" in d.qualifications_ne:
                d.qualifications_ne = d.qualifications_ne.replace("३१२२९", "३२५२४").replace("31229", "32524")
                changed = True
        if d.bio and "31229" in d.bio:
            d.bio = d.bio.replace("31229", "32524")
            changed = True
        if hasattr(d, 'bio_ne') and d.bio_ne:
            if "३१२२९" in d.bio_ne or "31229" in d.bio_ne:
                d.bio_ne = d.bio_ne.replace("३१२२९", "३२५२४").replace("31229", "32524")
                changed = True
        
        if changed:
            d.save()
            print(f"[UPDATED] Doctor {d.id} ({d.name}) -> NMC: {d.nmc_number}, Qual: {d.qualifications}")

    # Check Testimonials
    for t in Testimonial.objects.all():
        changed = False
        for f in ['review', 'clinical_journey', 'review_ne']:
            val = getattr(t, f, None)
            if val and ("31229" in val or "३१२२९" in val):
                setattr(t, f, val.replace("31229", "32524").replace("३१२२९", "३२५२४"))
                changed = True
        if changed:
            t.save()
            print(f"[UPDATED] Testimonial {t.id}")

    # Check SEOFAQ
    for faq in SEOFAQ.objects.all():
        changed = False
        for f in ['question', 'answer', 'question_ne', 'answer_ne']:
            val = getattr(faq, f, None)
            if val and ("31229" in val or "३१२२९" in val):
                setattr(faq, f, val.replace("31229", "32524").replace("३१२२९", "३२५२४"))
                changed = True
        if changed:
            faq.save()
            print(f"[UPDATED] SEOFAQ {faq.id}")

    print("Database check & update completed.")

if __name__ == '__main__':
    fix_all()
