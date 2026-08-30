import os
import sys
from pathlib import Path

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
from django.db import connection

SERVICES_DATA = {
    "General Dentistry": {
        "title_ne": "साधारण दन्त चिकित्सा",
        "category_label_ne": "नियमित हेरचाह",
        "short_desc_ne": "सम्पूर्ण मुख तथा दाँत परीक्षण, दाँत सफाइ र स्वस्थ दाँतका लागि व्यक्तिगत परामर्श।",
        "features_ne": "नियमित चेक-अप\nरोकथाम हेरचाह\nमौखिक स्वास्थ्य परीक्षण"
    },
    "Digital Dental X-Ray": {
        "title_ne": "डिजिटल दन्त एक्स-रे",
        "category_label_ne": "दन्त निदान",
        "short_desc_ne": "सटीक र तत्काल निदानका लागि उच्च गुणस्तरीय तथा कम विकिरण भएको आधुनिक डिजिटल एक्स-रे।",
        "features_ne": "कम विकिरण प्रविधि\nसटीक तथा तत्काल निदान\nआधुनिक डिजिटल सेन्सर"
    },
    "Dental Filling": {
        "title_ne": "दाँत भर्ने सेवा (फिलिङ)",
        "category_label_ne": "पुनर्स्थापना",
        "short_desc_ne": "किराले खाएको वा भाँचिएको दाँतलाई प्राकृतिक रूप दिने उच्च गुणस्तरीय कम्पोजिट फिलिङ।",
        "features_ne": "दाँतको प्राकृतिक रङ मिल्ने\nकिरा लाग्नबाट पूर्ण सुरक्षा\nप्राकृतिक दाँतको संरक्षण"
    },
    "Scaling & Polishing": {
        "title_ne": "दाँत सफाइ र पोलिसिङ (स्केलिङ)",
        "category_label_ne": "रोकथाम तथा सरसफाइ",
        "short_desc_ne": "अल्ट्रासोनिक मेसिनद्वारा दाँतमा जमेको फोहोर, पहेँलोपन र दाग हटाई गिजा स्वस्थ बनाउने सेवा।",
        "features_ne": "दाग र फोहोर हटाउने\nगिजा स्वस्थ राख्ने\nताजा र दुर्गन्धरहित सास"
    },
    "Root Canal Treatment": {
        "title_ne": "रूट क्यानल उपचार (RCT)",
        "category_label_ne": "इन्डोडोन्टिक्स",
        "short_desc_ne": "दाँतको भित्री नसाको संक्रमण हटाई प्राकृतिक दाँत जोगाउने आधुनिक र दुखाइरहित उपचार।",
        "features_ne": "दुखाइरहित आधुनिक विधि\nप्राकृतिक दाँतको संरक्षण\nरोटरी प्रविधिद्वारा उपचार"
    },
    "Tooth Extraction": {
        "title_ne": "दाँत निकाल्ने सेवा",
        "category_label_ne": "शल्यक्रिया",
        "short_desc_ne": "सडेको वा समस्याग्रस्त बुद्धि बंगारा (Wisdom Tooth) बिना दुखाइ सहजै निकाल्ने सेवा।",
        "features_ne": "कोमल तथा दुखाइरहित विधि\nबुद्धि बंगारा निकाल्ने\nद्रुत निको हुने प्रविधि"
    },
    "Crowns & Bridges": {
        "title_ne": "दाँतको क्याप तथा ब्रिज",
        "category_label_ne": "प्रोस्थोडोन्टिक्स",
        "short_desc_ne": "कमजोर दाँतलाई बलियो बनाउन र हराएको दाँत भर्न प्रिमियम जिर्कोनिया तथा सिरामिक क्याप।",
        "features_ne": "प्रिमियम जिर्कोनिया क्याप\nदाँतको प्राकृतिक लुक\nदीर्घकालीन मजबुती"
    },
    "Dentures": {
        "title_ne": "नक्कली दाँत (डेन्चर)",
        "category_label_ne": "दाँत पुनर्स्थापना",
        "short_desc_ne": "खाना खान र बोल्न सहज बनाउने आधुनिक, आरामदायी तथा निकाल्न मिल्ने नक्कली दाँत।",
        "features_ne": "पूर्ण तथा आंशिक डेन्चर\nआरामदायी र प्राकृतिक बनावट\nचपाउन सहज र टिकाउ"
    },
    "Orthodontic Treatment (Braces)": {
        "title_ne": "तार बाँध्ने उपचार (ब्रेसेस)",
        "category_label_ne": "अर्थोडोन्टिक्स",
        "short_desc_ne": "बाङ्गो-टिङ्गो वा मिलेको नभएको दाँतलाई सीधा र सुन्दर बनाउन आधुनिक ब्रेसेस र अलाइनर।",
        "features_ne": "मेटल तथा सिरामिक ब्रेसेस\nअदृश्य क्लियर अलाइनर\nआकर्षक मुस्कान निर्माण"
    },
    "Periodontal Treatment (Gum)": {
        "title_ne": "गिजाको विशेष उपचार",
        "category_label_ne": "पेरियोडोन्टिक्स",
        "short_desc_ne": "गिजाबाट रगत आउने, सुन्निने र पाक्ने समस्याको उपचार गरी दाँतको जग बलियो बनाउने सेवा।",
        "features_ne": "गिजा रोगको उपचार\nगहिरो जरा सफाइ (Root Planing)\nगिजाबाट रगत आउन रोक्ने"
    },
    "Dental Implants": {
        "title_ne": "डेन्टल इम्प्लान्ट (दाँत प्रत्यारोपण)",
        "category_label_ne": "इम्प्लान्टोलोजी",
        "short_desc_ne": "हराएको दाँतको ठाउँमा प्राकृतिक दाँत जस्तै जीवनभर टिक्ने टाइटेनियम दाँत प्रत्यारोपण।",
        "features_ne": "प्रिमियम टाइटेनियम इम्प्लान्ट\nप्राकृतिक दाँत जस्तै बलियो\nजीवनभर टिक्ने स्थायी समाधान"
    }
}

def populate_all():
    print("--- 1. Updating Services ---")
    for s in Service.objects.all():
        title_en = s.title_en or s.title
        matched = False
        for k, data in SERVICES_DATA.items():
            if k.lower() in title_en.lower() or title_en.lower() in k.lower():
                s.title_en = title_en
                s.title_ne = data["title_ne"]
                s.category_label_ne = data["category_label_ne"]
                s.short_description_en = s.short_description or title_en
                s.short_description_ne = data["short_desc_ne"]
                s.features_ne = data["features_ne"]
                s.save()
                print(f"  [Service] {title_en} -> {data['title_ne']}")
                matched = True
                break
        if not matched:
            print(f"  [Service Skipped] {title_en}")

    print("\n--- 2. Updating Doctors ---")
    for doc in Doctor.objects.all():
        if "Subash" in doc.name or "सुभाष" in doc.name:
            doc.designation_en = "Clinical Director & Senior Dental Surgeon"
            doc.designation_ne = "क्लिनिकल निर्देशक तथा वरिष्ठ दन्त शल्यचिकित्सक"
            doc.qualifications_en = "BDS (KU), NMC #31229, Fellow in Advanced Endodontics"
            doc.qualifications_ne = "बीडीएस (केयू), एनएमसी #३१२२९, एडभान्स्ड इन्डोडोन्टिक्स फेलो"
            doc.bio_en = "Dr. Subash Banjade is a senior dental surgeon with extensive clinical expertise in painless root canal therapy, digital cosmetic smile design, and modern oral surgery. He leads CareFirst Dental Clinic with strict adherence to hospital-grade sterilization and patient-centric care."
            doc.bio_ne = "डा. सुभाष बन्जाडे दुखाइरहित रूट क्यानल उपचार, डिजिटल कस्मेटिक स्माइल डिजाइन र आधुनिक दन्त शल्यक्रियामा विशेष दक्षता हासिल गर्नुभएका वरिष्ठ दन्त चिकित्सक हुनुहुन्छ। उहाँले उच्च अस्पताल मापदण्डको स्टेरिलाइजेसन र बिरामीमैत्री सेवाका साथ केयरफर्स्ट डेन्टल क्लिनिकको नेतृत्व गरिरहनुभएको छ।"
            doc.save()
            print(f"  [Doctor] Dr. Subash Banjade updated in Nepali & English")

    print("\n--- 3. Updating Core Values & Clinic Features ---")
    core_values_ne = {
        "Senior Specialist Team": ("वरिष्ठ विशेषज्ञ टोली", "विभिन्न दन्त विधाका अनुभवी तथा एनएमसी प्रमाणित विशेषज्ञ चिकित्सकहरूद्वारा सम्पूर्ण उपचार सञ्चालन।"),
        "Modern Digital Technology": ("आधुनिक डिजिटल प्रविधि", "सटीक उपचारका लागि डिजिटल आरभीजी (RVG) सेन्सर, अल्ट्रासोनिक युनिट र रोटरी प्रविधि उपलब्ध।"),
        "Zero Dental Anxiety": ("डररहित कोमल उपचार", "बिरामीको डर र चिन्ता हटाउन विशेष कोमल विधि र पेनलेस एनेस्थेसियाको प्रयोग।"),
        "Hospital-Grade Sterilization": ("अस्पताल मापदण्डको सरसफाइ", "क्लास-बी अटोक्लेभ र ६-चरणको कडा स्टेरिलाइजेसन विधिद्वारा १००% जीवाणुरहित वातावरण।"),
        "100% Transparent Fees": ("१००% पारदर्शी शुल्क", "कुनै लुकेको शुल्क नभएको, उपचार अघि नै लिखित शुल्क विवरण र सस्तो किस्ताबन्दी सुविधा।"),
        "Prime Kathmandu Location": ("काठमाडौँको सुगम स्थान", "शंखमूल-३१ प्रगतिनगरमा पर्याप्त पार्किङसहित हप्ताको सातै दिन बिहान ७:३० देखि साँझ ७:३० सम्म खुला।")
    }
    for cv in CoreValue.objects.all():
        title_en = cv.title_en or cv.title
        for k, (t_ne, d_ne) in core_values_ne.items():
            if k.lower() in title_en.lower():
                cv.title_en = title_en
                cv.title_ne = t_ne
                cv.description_en = cv.description or ""
                cv.description_ne = d_ne
                cv.save()
                print(f"  [CoreValue] {title_en} -> {t_ne}")
                break

    print("\n--- 4. Updating Testimonials ---")
    for t in Testimonial.objects.all():
        if t.review and not t.review_ne:
            t.review_en = t.review
            t.treatment_en = t.treatment or "Dental Care"
            # Keep authentic review translation
            t.save()

    print("\nAll database model translations successfully synchronized!")

if __name__ == '__main__':
    populate_all()
