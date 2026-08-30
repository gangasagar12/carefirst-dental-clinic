import os
import sys
import time
import re
from pathlib import Path
import polib
from deep_translator import GoogleTranslator

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding='utf-8')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from main.models import (
    Service, Doctor, PricingCategory, PricingItem, SpecialOffer,
    AboutPageSettings, Branch, CoreValue, Technology, Testimonial,
    ClinicGallery, SEOFAQCategory, SEOFAQ
)
from blogs.models import Post, Category as BlogCategory

translator = GoogleTranslator(source='en', target='ne')

def dt_translate(text):
    if not text or not isinstance(text, str):
        return text
    clean = text.strip()
    if not clean:
        return text
    # Avoid translating numbers or urls
    if clean.isdigit() or clean.startswith('http') or clean.startswith('/'):
        return clean
    try:
        res = translator.translate(clean)
        return res if res else clean
    except Exception as e:
        print(f"DeepTranslator error on '{clean[:30]}': {e}")
        return clean

def translate_models():
    print("=== Translating All Database Models via Deep Translator ===")
    
    # 1. Services
    print("\n--- Translating Services ---")
    for s in Service.objects.all():
        src_title = s.title_en or s.title
        s.title_en = src_title
        s.title_ne = dt_translate(src_title)
        
        if s.category_label:
            s.category_label_en = s.category_label
            s.category_label_ne = dt_translate(s.category_label)
        
        if s.short_description:
            s.short_description_en = s.short_description
            s.short_description_ne = dt_translate(s.short_description)
        else:
            default_short = s.get_short_description()
            s.short_description_en = default_short
            s.short_description_ne = dt_translate(default_short)
            
        if s.features:
            s.features_en = s.features
            lines = [dt_translate(line) for line in s.features.splitlines() if line.strip()]
            s.features_ne = "\n".join(lines)
            
        s.save()
        print(f"  [Service] {src_title} -> {s.title_ne}")
        time.sleep(0.05)

    # 2. Doctors
    print("\n--- Translating Doctors ---")
    for d in Doctor.objects.all():
        if d.designation:
            d.designation_en = d.designation
            d.designation_ne = dt_translate(d.designation)
        if d.bio:
            d.bio_en = d.bio
            d.bio_ne = dt_translate(d.bio)
        if d.qualifications:
            d.qualifications_en = d.qualifications
            d.qualifications_ne = dt_translate(d.qualifications)
        if d.certifications:
            d.certifications_en = d.certifications
            d.certifications_ne = dt_translate(d.certifications)
        d.save()
        print(f"  [Doctor] {d.name} -> {d.designation_ne}")
        time.sleep(0.05)

    # 3. Pricing Categories & Items
    print("\n--- Translating Pricing ---")
    for pc in PricingCategory.objects.all():
        pc.name_en = pc.name
        pc.name_ne = dt_translate(pc.name)
        pc.save()
        print(f"  [PricingCategory] {pc.name} -> {pc.name_ne}")
        time.sleep(0.05)

    for pi in PricingItem.objects.all():
        pi.name_en = pi.name
        pi.name_ne = dt_translate(pi.name)
        if pi.price:
            pi.price_en = pi.price
            pi.price_ne = dt_translate(pi.price)
        pi.save()
        time.sleep(0.02)
    print("  [PricingItems] All pricing items translated.")

    # 4. Special Offers
    print("\n--- Translating Special Offers ---")
    for so in SpecialOffer.objects.all():
        if so.title:
            so.title_en = so.title
            so.title_ne = dt_translate(so.title)
        if so.description:
            so.description_en = so.description
            so.description_ne = dt_translate(so.description)
        if so.highlight_text:
            so.highlight_text_en = so.highlight_text
            so.highlight_text_ne = dt_translate(so.highlight_text)
        if so.sub_text:
            so.sub_text_en = so.sub_text
            so.sub_text_ne = dt_translate(so.sub_text)
        if so.badge_text:
            so.badge_text_en = so.badge_text
            so.badge_text_ne = dt_translate(so.badge_text)
        if so.button_text:
            so.button_text_en = so.button_text
            so.button_text_ne = dt_translate(so.button_text)
        so.save()
        print(f"  [SpecialOffer] {so.title} -> {so.title_ne}")
        time.sleep(0.05)

    # 5. Core Values & Technology
    print("\n--- Translating Core Values & Technology ---")
    for cv in CoreValue.objects.all():
        cv.title_en = cv.title
        cv.title_ne = dt_translate(cv.title)
        if cv.description:
            cv.description_en = cv.description
            cv.description_ne = dt_translate(cv.description)
        cv.save()
        print(f"  [CoreValue] {cv.title} -> {cv.title_ne}")
        time.sleep(0.05)

    for tech in Technology.objects.all():
        tech.title_en = tech.title
        tech.title_ne = dt_translate(tech.title)
        if tech.description:
            tech.description_en = tech.description
            tech.description_ne = dt_translate(tech.description)
        tech.save()
        print(f"  [Technology] {tech.title} -> {tech.title_ne}")
        time.sleep(0.05)

    # 6. Testimonials
    print("\n--- Translating Testimonials ---")
    for t in Testimonial.objects.all():
        if t.treatment:
            t.treatment_en = t.treatment
            t.treatment_ne = dt_translate(t.treatment)
        if t.review:
            t.review_en = t.review
            t.review_ne = dt_translate(t.review)
        t.save()
        print(f"  [Testimonial] {t.patient_name} -> {t.treatment_ne}")
        time.sleep(0.05)

    # 7. SEO FAQs & Categories
    print("\n--- Translating SEO FAQs ---")
    for cat in SEOFAQCategory.objects.all():
        cat.name_en = cat.name
        cat.name_ne = dt_translate(cat.name)
        if cat.description:
            cat.description_en = cat.description
            cat.description_ne = dt_translate(cat.description)
        cat.save()
        print(f"  [SEOFAQCategory] {cat.name} -> {cat.name_ne}")
        time.sleep(0.05)

    for faq in SEOFAQ.objects.all():
        q_src = faq.question_en or faq.question
        a_src = faq.answer_en or faq.answer
        faq.question_en = q_src
        faq.question_ne = dt_translate(q_src)
        faq.answer_en = a_src
        faq.answer_ne = dt_translate(a_src)
        faq.save()
        print(f"  [SEOFAQ] {q_src[:30]} -> {faq.question_ne[:30]}")
        time.sleep(0.05)

def translate_po_file():
    print("\n=== Translating All Django PO Strings via Deep Translator ===")
    locale_dir = BASE_DIR / 'locale' / 'ne' / 'LC_MESSAGES'
    po_path = locale_dir / 'django.po'
    mo_path = locale_dir / 'django.mo'

    if not po_path.exists():
        print("Error: django.po not found!")
        return

    po = polib.pofile(str(po_path), encoding='utf-8')
    untranslated_count = 0
    updated_count = 0

    for i, entry in enumerate(po):
        msgid = entry.msgid.strip()
        if not msgid:
            continue
        
        # Check if entry needs translation (empty or identical to English msgid without Nepali script)
        needs_translation = False
        if not entry.msgstr or not entry.msgstr.strip():
            needs_translation = True
        elif not re.search(r'[\u0900-\u097F]', entry.msgstr) and len(msgid) > 2 and not msgid.isdigit():
            needs_translation = True

        if needs_translation:
            untranslated_count += 1
            new_val = dt_translate(msgid)
            if new_val:
                entry.msgstr = new_val
                updated_count += 1
                if updated_count % 20 == 0:
                    print(f"  Translated {updated_count} PO entries...")
                time.sleep(0.03)

    po.save(str(po_path))
    po.save_as_mofile(str(mo_path))
    print(f"\nPO File update complete: {updated_count} strings translated via Deep Translator. Compiled into {mo_path}.")

if __name__ == '__main__':
    translate_models()
    translate_po_file()
    print("\nAll translations successfully completed via Deep Translator!")
