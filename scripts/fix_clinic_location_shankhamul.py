import os
import sys
import pathlib
import time

# Ensure project root is in sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.db import connection, transaction
from main.models import SiteSettings, SEOFAQ, FAQ, Branch

def safe_retry(action_fn, max_retries=10, delay=1.0):
    for attempt in range(1, max_retries + 1):
        try:
            return action_fn()
        except Exception as e:
            if "locked" in str(e).lower() and attempt < max_retries:
                connection.close()
                time.sleep(delay)
            else:
                raise

def fix_locations():
    print("=" * 70)
    print("UPDATING CAREFIRST DENTAL CLINIC LOCATION TO SHANKHAMUL-31, KATHMANDU")
    print("=" * 70)

    # 1. Update SiteSettings
    def update_site_settings():
        settings, created = SiteSettings.objects.get_or_create(id=1)
        settings.address = "Pragatinagar Road, Shankhamul-31, Kathmandu 44600"
        settings.landmark = "Shankhamul / New Baneshwor Area (Near Shankhamul Bridge)"
        settings.primary_phone = "+977 980-7464136"
        settings.secondary_phone = "01-5916886"
        settings.email = "carefirstdentalclinic@gmail.com"
        settings.working_hours_weekdays = "Mon - Sun: 7:30 AM - 7:30 PM"
        settings.working_hours_weekend = "Mon - Sun: 7:30 AM - 7:30 PM"
        settings.save()
        print(f"[OK] SiteSettings updated:")
        print(f"  Address : {settings.address}")
        print(f"  Landmark: {settings.landmark}")

    safe_retry(update_site_settings)

    # 2. Update SEOFAQ location records
    def update_seofaqs():
        updated_count = 0
        shankhamul_en = (
            "CareFirst Dental Clinic is conveniently located at Pragatinagar Road, Shankhamul-31, "
            "Kathmandu (in the peaceful Shankhamul / New Baneshwor area, near Shankhamul Bridge). "
            "We offer ample parking, wheelchair accessibility, and a modern, hygienic digital dental environment."
        )
        shankhamul_ne = (
            "केयरफर्स्ट डेन्टल क्लिनिक काठमाडौँको शंखमूल-३१ (प्रगतिनगर रोड, नयाँ बानेश्वर नजिक) "
            "मा अवस्थित छ। क्लिनिकमा पर्याप्त पार्किङ, ह्विलचेयर पहुँच र अत्याधुनिक डिजिटल दन्त सुविधा उपलब्ध छ।"
        )

        for faq in SEOFAQ.objects.all():
            changed = False
            ans = faq.answer or ''
            ans_ne = getattr(faq, 'answer_ne', '') or ''
            
            # Check for old Koteshwor / Sanima / Police Office landmarks
            for term in ['koteshwor', 'sanima', 'police office', 'mahadevsthan']:
                if term in ans.lower() or term in (faq.question or '').lower():
                    faq.answer = shankhamul_en
                    changed = True
                    break

            for term in ['कोटेश्वर', 'सानिमा', 'प्रहरी चौकी', 'महादेवस्थान']:
                if term in ans_ne.lower() or term in (getattr(faq, 'question_ne', '') or '').lower():
                    faq.answer_ne = shankhamul_ne
                    changed = True
                    break

            # Explicit check for location questions
            if 'where is carefirst dental clinic located' in (faq.question or '').lower():
                faq.answer = shankhamul_en
                faq.answer_ne = shankhamul_ne
                changed = True

            if changed:
                faq.save()
                updated_count += 1
                print(f"[OK] SEOFAQ updated (ID {faq.id}): {faq.question[:50]}...")

        print(f"[OK] Total SEOFAQs updated: {updated_count}")

    safe_retry(update_seofaqs)

    # 3. Update Standard FAQ records if any
    def update_faqs():
        faqs_updated = 0
        shankhamul_en = (
            "CareFirst Dental Clinic is located at Pragatinagar Road, Shankhamul-31, Kathmandu "
            "(Shankhamul / New Baneshwor Area). Open 7:30 AM to 7:30 PM daily."
        )
        for faq in FAQ.objects.all():
            changed = False
            for term in ['koteshwor', 'sanima', 'police office', 'mahadevsthan']:
                if term in (faq.answer or '').lower():
                    faq.answer = shankhamul_en
                    changed = True
                    break
            if changed:
                faq.save()
                faqs_updated += 1
                print(f"[OK] FAQ updated (ID {faq.id})")
        print(f"[OK] Total standard FAQs updated: {faqs_updated}")

    safe_retry(update_faqs)

    # 4. Update Branch records if any
    def update_branches():
        branches = Branch.objects.all()
        for b in branches:
            if 'koteshwor' in (b.name or '').lower() or 'koteshwor' in (b.location or '').lower():
                b.name = "Shankhamul Central Clinic"
                b.location = "Pragatinagar Road, Shankhamul-31, Kathmandu"
                b.save()
                print(f"[OK] Branch updated: {b.name} ({b.location})")

    safe_retry(update_branches)

    print("\n" + "=" * 70)
    print("LOCATION CORRECTION COMPLETE! ALL DATABASE TABLES SYNCED TO SHANKHAMUL-31.")
    print("=" * 70)

if __name__ == '__main__':
    fix_locations()
