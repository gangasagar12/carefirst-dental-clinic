import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding='utf-8')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from main.models import SEOFAQCategory, SEOFAQ, SpecialOffer, Testimonial

print("=== 1. SEO FAQ CATEGORIES & COUNTS ===")
for cat in SEOFAQCategory.objects.all():
    faqs = SEOFAQ.objects.filter(category=cat)
    active_faqs = faqs.filter(is_active=True)
    print(f"Category: {cat.name} (slug={cat.slug}) -> Total: {faqs.count()}, Active: {active_faqs.count()}")
    for f in faqs:
        print(f"   [{f.id}] active={f.is_active} order={f.order}")
        print(f"       EN Q: {f.question}")
        print(f"       NE Q: {f.question_ne}")

print("\n=== 2. SPECIAL OFFERS ===")
offers = SpecialOffer.objects.all()
print(f"Total Offers: {offers.count()}")
for o in offers:
    print(f"[{o.id}] active={o.is_active} valid={o.is_currently_valid()}")
    print(f"  EN Title: {o.title}")
    print(f"  NE Title: {o.title_ne}")
    print(f"  EN Badge: {o.badge_text}")
    print(f"  NE Badge: {o.badge_text_ne}")
    print(f"  EN Highlight: {o.highlight_text}")
    print(f"  NE Highlight: {o.highlight_text_ne}")
    print(f"  EN Sub: {o.sub_text}")
    print(f"  NE Sub: {o.sub_text_ne}")
    print(f"  EN Features: {repr(o.features)}")
    print(f"  NE Features: {repr(o.features_ne)}")

print("\n=== 3. TESTIMONIALS / PATIENT STORIES ===")
stories = Testimonial.objects.all()
print(f"Total Stories: {stories.count()}")
for s in stories:
    print(f"[{s.id}] active={s.is_active} order={s.order}")
    print(f"  EN Name: {s.patient_name} | NE Name: {s.patient_name_ne}")
    print(f"  EN Treatment: {s.treatment} | NE Treatment: {s.treatment_ne}")
    print(f"  EN Review: {repr(s.review)}")
    print(f"  NE Review: {repr(s.review_ne)}")
    print(f"  EN Headline: {getattr(s, 'headline', None)}")
    print(f"  EN Initial Concern: {getattr(s, 'initial_concern', None)}")
    print(f"  EN Clinical Journey: {getattr(s, 'clinical_journey', None)}")
    print(f"  EN Outcome: {getattr(s, 'outcome', None)}")

from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("DESCRIBE main_testimonial")
    cols = [row[0] for row in cursor.fetchall()]
    print("\nmain_testimonial columns:", cols)

    cursor.execute("DESCRIBE main_specialoffer")
    cols_so = [row[0] for row in cursor.fetchall()]
    print("\nmain_specialoffer columns:", cols_so)

