import os
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding='utf-8')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from main.services.translation_service import translate_to_nepali

def safe_update_model(queryset, **kwargs):
    for attempt in range(10):
        try:
            return queryset.update(**kwargs)
        except Exception as e:
            if 'locked' in str(e).lower() and attempt < 9:
                connection.close()
                time.sleep(1)
            else:
                raise e

if connection.vendor == 'sqlite':
    try:
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA busy_timeout = 60000;")
            cursor.execute("PRAGMA journal_mode = WAL;")
            cursor.execute("PRAGMA synchronous = NORMAL;")
    except Exception:
        pass

from blogs.models import Post as BlogPost, Category as BlogCategory
from media_center.models import Video, VideoCategory
from main.models import (
    Doctor, SpecialOffer, Service, CoreValue, Testimonial,
    HeroSlide, SEOFAQ, SEOFAQCategory, PricingCategory, PricingItem
)

def translate_all_dynamic_models():
    print("=" * 60)
    print("STARTING FULL DYNAMIC MODEL TRANSLATION SYNC")
    print("=" * 60)

    # 1. BLOG POSTS
    print("\n--- 1. Translating Blog Posts (Title, Excerpt, Content) ---")
    for post in BlogPost.objects.all():
        updates = {}
        title_source = post.title_en or post.title
        if not getattr(post, 'title_en', None):
            updates['title_en'] = title_source
        if not getattr(post, 'title_ne', None) or getattr(post, 'title_ne', '').strip() == title_source.strip():
            print(f"  Translating Post Title: {title_source[:50]}...")
            updates['title_ne'] = translate_to_nepali(title_source)

        excerpt_source = post.excerpt_en or post.excerpt or ""
        if excerpt_source:
            if not getattr(post, 'excerpt_en', None):
                updates['excerpt_en'] = excerpt_source
            if not getattr(post, 'excerpt_ne', None) or getattr(post, 'excerpt_ne', '').strip() == excerpt_source.strip():
                print(f"  Translating Post Excerpt...")
                updates['excerpt_ne'] = translate_to_nepali(excerpt_source)

        content_source = post.content_en or post.content or ""
        if content_source:
            if not getattr(post, 'content_en', None):
                updates['content_en'] = content_source
            if not getattr(post, 'content_ne', None) or getattr(post, 'content_ne', '').strip() == content_source.strip():
                print(f"  Translating Post Content ({len(content_source)} chars)...")
                updates['content_ne'] = translate_to_nepali(content_source)

        if updates:
            safe_update_model(BlogPost.objects.filter(id=post.id), **updates)
            print(f"  [OK] Updated Blog Post ID {post.id}: {title_source[:40]}")

    # 2. BLOG CATEGORIES
    print("\n--- 2. Translating Blog Categories ---")
    for cat in BlogCategory.objects.all():
        name_source = cat.name_en or cat.name
        updates = {}
        if not getattr(cat, 'name_en', None):
            updates['name_en'] = name_source
        if not getattr(cat, 'name_ne', None) or getattr(cat, 'name_ne', '').strip() == name_source.strip():
            updates['name_ne'] = translate_to_nepali(name_source)
        if updates:
            safe_update_model(BlogCategory.objects.filter(id=cat.id), **updates)
            print(f"  [OK] Category: {name_source} -> {updates.get('name_ne', cat.name_ne)}")

    # 3. SPECIAL OFFERS
    print("\n--- 3. Translating Special Offers ---")
    for offer in SpecialOffer.objects.all():
        updates = {}
        title_source = offer.title_en or offer.title
        if not getattr(offer, 'title_en', None):
            updates['title_en'] = title_source
        if not getattr(offer, 'title_ne', None) or getattr(offer, 'title_ne', '').strip() == title_source.strip():
            updates['title_ne'] = translate_to_nepali(title_source)

        desc_source = offer.description_en or offer.description or ""
        if desc_source:
            if not getattr(offer, 'description_en', None):
                updates['description_en'] = desc_source
            if not getattr(offer, 'description_ne', None) or getattr(offer, 'description_ne', '').strip() == desc_source.strip():
                updates['description_ne'] = translate_to_nepali(desc_source)

        if hasattr(offer, 'badge_text'):
            badge = offer.badge_text_en or offer.badge_text or ""
            if badge:
                if not getattr(offer, 'badge_text_en', None):
                    updates['badge_text_en'] = badge
                if not getattr(offer, 'badge_text_ne', None) or getattr(offer, 'badge_text_ne', '').strip() == badge.strip():
                    updates['badge_text_ne'] = translate_to_nepali(badge)

        if hasattr(offer, 'discount_text'):
            disc = offer.discount_text_en or offer.discount_text or ""
            if disc:
                if not getattr(offer, 'discount_text_en', None):
                    updates['discount_text_en'] = disc
                if not getattr(offer, 'discount_text_ne', None) or getattr(offer, 'discount_text_ne', '').strip() == disc.strip():
                    updates['discount_text_ne'] = translate_to_nepali(disc)

        if updates:
            safe_update_model(SpecialOffer.objects.filter(id=offer.id), **updates)
            print(f"  [OK] Special Offer ID {offer.id}: {title_source}")

    # 4. VIDEOS & VIDEO CATEGORIES
    print("\n--- 4. Translating Videos ---")
    for vid in Video.objects.all():
        updates = {}
        title_source = vid.title_en or vid.title
        if not getattr(vid, 'title_en', None):
            updates['title_en'] = title_source
        if not getattr(vid, 'title_ne', None) or getattr(vid, 'title_ne', '').strip() == title_source.strip():
            updates['title_ne'] = translate_to_nepali(title_source)

        desc_source = vid.short_description_en or vid.short_description or ""
        if desc_source:
            if not getattr(vid, 'short_description_en', None):
                updates['short_description_en'] = desc_source
            if not getattr(vid, 'short_description_ne', None) or getattr(vid, 'short_description_ne', '').strip() == desc_source.strip():
                updates['short_description_ne'] = translate_to_nepali(desc_source)

        if updates:
            safe_update_model(Video.objects.filter(id=vid.id), **updates)
            print(f"  [OK] Video ID {vid.id}: {title_source[:40]}")

    for vcat in VideoCategory.objects.all():
        name_source = vcat.name_en or vcat.name
        updates = {}
        if not getattr(vcat, 'name_en', None):
            updates['name_en'] = name_source
        if not getattr(vcat, 'name_ne', None) or getattr(vcat, 'name_ne', '').strip() == name_source.strip():
            updates['name_ne'] = translate_to_nepali(name_source)
        if updates:
            safe_update_model(VideoCategory.objects.filter(id=vcat.id), **updates)
            print(f"  [OK] Video Category: {name_source}")

    # 5. HERO SLIDES
    print("\n--- 5. Translating Hero Slides ---")
    for slide in HeroSlide.objects.all():
        updates = {}
        h_source = slide.heading_en or slide.heading
        if not getattr(slide, 'heading_en', None):
            updates['heading_en'] = h_source
        if not getattr(slide, 'heading_ne', None) or getattr(slide, 'heading_ne', '').strip() == h_source.strip():
            updates['heading_ne'] = translate_to_nepali(h_source)

        sub_source = slide.subheading_en or slide.subheading or ""
        if sub_source:
            if not getattr(slide, 'subheading_en', None):
                updates['subheading_en'] = sub_source
            if not getattr(slide, 'subheading_ne', None) or getattr(slide, 'subheading_ne', '').strip() == sub_source.strip():
                updates['subheading_ne'] = translate_to_nepali(sub_source)

        badge_source = slide.badge_text_en or slide.badge_text or ""
        if badge_source:
            if not getattr(slide, 'badge_text_en', None):
                updates['badge_text_en'] = badge_source
            if not getattr(slide, 'badge_text_ne', None) or getattr(slide, 'badge_text_ne', '').strip() == badge_source.strip():
                updates['badge_text_ne'] = translate_to_nepali(badge_source)

        btn_source = slide.button_text_en or slide.button_text or ""
        if btn_source:
            if not getattr(slide, 'button_text_en', None):
                updates['button_text_en'] = btn_source
            if not getattr(slide, 'button_text_ne', None) or getattr(slide, 'button_text_ne', '').strip() == btn_source.strip():
                updates['button_text_ne'] = translate_to_nepali(btn_source)

        if updates:
            safe_update_model(HeroSlide.objects.filter(id=slide.id), **updates)
            print(f"  [OK] HeroSlide ID {slide.id}: {h_source[:40]}")

    # 6. DOCTORS
    print("\n--- 6. Translating Doctors ---")
    for doc in Doctor.objects.all():
        updates = {}
        des_source = doc.designation_en or doc.designation or ""
        if des_source:
            if not getattr(doc, 'designation_en', None):
                updates['designation_en'] = des_source
            if not getattr(doc, 'designation_ne', None) or getattr(doc, 'designation_ne', '').strip() == des_source.strip():
                updates['designation_ne'] = translate_to_nepali(des_source)

        qual_source = doc.qualifications_en or doc.qualifications or ""
        if qual_source:
            if not getattr(doc, 'qualifications_en', None):
                updates['qualifications_en'] = qual_source
            if not getattr(doc, 'qualifications_ne', None) or getattr(doc, 'qualifications_ne', '').strip() == qual_source.strip():
                updates['qualifications_ne'] = translate_to_nepali(qual_source)

        bio_source = doc.bio_en or doc.bio or ""
        if bio_source:
            if not getattr(doc, 'bio_en', None):
                updates['bio_en'] = bio_source
            if not getattr(doc, 'bio_ne', None) or getattr(doc, 'bio_ne', '').strip() == bio_source.strip():
                updates['bio_ne'] = translate_to_nepali(bio_source)

        if updates:
            safe_update_model(Doctor.objects.filter(id=doc.id), **updates)
            print(f"  [OK] Doctor: Dr. {doc.name}")

    # 7. SERVICES
    print("\n--- 7. Translating Services ---")
    for s in Service.objects.all():
        updates = {}
        t_source = s.title_en or s.title
        if not getattr(s, 'title_en', None):
            updates['title_en'] = t_source
        if not getattr(s, 'title_ne', None) or getattr(s, 'title_ne', '').strip() == t_source.strip():
            updates['title_ne'] = translate_to_nepali(t_source)

        cat_source = s.category_label_en or s.category_label or ""
        if cat_source:
            if not getattr(s, 'category_label_en', None):
                updates['category_label_en'] = cat_source
            if not getattr(s, 'category_label_ne', None) or getattr(s, 'category_label_ne', '').strip() == cat_source.strip():
                updates['category_label_ne'] = translate_to_nepali(cat_source)

        desc_source = s.short_description_en or s.short_description or ""
        if desc_source:
            if not getattr(s, 'short_description_en', None):
                updates['short_description_en'] = desc_source
            if not getattr(s, 'short_description_ne', None) or getattr(s, 'short_description_ne', '').strip() == desc_source.strip():
                updates['short_description_ne'] = translate_to_nepali(desc_source)

        feat_source = s.features_en or s.features or ""
        if feat_source:
            if not getattr(s, 'features_en', None):
                updates['features_en'] = feat_source
            if not getattr(s, 'features_ne', None) or getattr(s, 'features_ne', '').strip() == feat_source.strip():
                updates['features_ne'] = translate_to_nepali(feat_source)

        if updates:
            safe_update_model(Service.objects.filter(id=s.id), **updates)
            print(f"  [OK] Service: {t_source}")

    # 8. TESTIMONIALS & CORE VALUES
    print("\n--- 8. Translating Testimonials & Core Values ---")
    for t in Testimonial.objects.all():
        updates = {}
        rev_source = t.review_en or t.review or ""
        if rev_source:
            if not getattr(t, 'review_en', None):
                updates['review_en'] = rev_source
            if not getattr(t, 'review_ne', None) or getattr(t, 'review_ne', '').strip() == rev_source.strip():
                updates['review_ne'] = translate_to_nepali(rev_source)

        treat_source = t.treatment_en or t.treatment or ""
        if treat_source:
            if not getattr(t, 'treatment_en', None):
                updates['treatment_en'] = treat_source
            if not getattr(t, 'treatment_ne', None) or getattr(t, 'treatment_ne', '').strip() == treat_source.strip():
                updates['treatment_ne'] = translate_to_nepali(treat_source)

        if updates:
            safe_update_model(Testimonial.objects.filter(id=t.id), **updates)

    for cv in CoreValue.objects.all():
        updates = {}
        t_source = cv.title_en or cv.title
        if not getattr(cv, 'title_en', None):
            updates['title_en'] = t_source
        if not getattr(cv, 'title_ne', None) or getattr(cv, 'title_ne', '').strip() == t_source.strip():
            updates['title_ne'] = translate_to_nepali(t_source)

        d_source = cv.description_en or cv.description or ""
        if d_source:
            if not getattr(cv, 'description_en', None):
                updates['description_en'] = d_source
            if not getattr(cv, 'description_ne', None) or getattr(cv, 'description_ne', '').strip() == d_source.strip():
                updates['description_ne'] = translate_to_nepali(d_source)

        if updates:
            safe_update_model(CoreValue.objects.filter(id=cv.id), **updates)
            print(f"  [OK] CoreValue: {t_source}")

    print("\n" + "=" * 60)
    print("ALL DYNAMIC MODELS SYNCHRONIZED AND TRANSLATED INTO NEPALI!")
    print("=" * 60)

if __name__ == '__main__':
    translate_all_dynamic_models()
