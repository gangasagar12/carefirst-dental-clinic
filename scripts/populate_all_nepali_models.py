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

from main.models import (
    Service, Doctor, PricingCategory, PricingItem, SpecialOffer,
    AboutPageSettings, Branch, CoreValue, Technology, Testimonial,
    ClinicGallery, SEOFAQCategory, SEOFAQ
)
from media_center.models import Video, VideoCategory
from blogs.models import Category as BlogCategory, Post as BlogPost

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
    "Crowns & Bridges": {
        "title_ne": "दाँतको क्याप तथा ब्रिज",
        "category_label_ne": "प्रोस्थोडोन्टिक्स",
        "short_desc_ne": "कमजोर वा हराएको दाँतलाई बलियो बनाउन प्रिमियम जिर्कोनिया र सिरेमिक क्याप तथा ब्रिज।",
        "features_ne": "प्रिमियम जिर्कोनिया तथा सिरामिक\nप्राकृतिक दाँत जस्तै मजबुत\nदाँतको आकार र सौन्दर्य पुनर्स्थापना"
    },
    "Tooth Extraction": {
        "title_ne": "दाँत निकाल्ने सेवा",
        "category_label_ne": "शल्यक्रिया",
        "short_desc_ne": "निको हुन नसक्ने वा बुद्धि बंगाराको दुखाइरहित र सुरक्षित शल्यक्रिया तथा निकाल्ने सेवा।",
        "features_ne": "सुरक्षित तथा कोमल विधि\nबुद्धि बंगारा (Wisdom Tooth) निकाल्ने\nन्यूनतम असुविधा र छिटो निको हुने"
    },
    "Dentures": {
        "title_ne": "नक्कली दाँत (डेन्चर)",
        "category_label_ne": "प्रोस्थोडोन्टिक्स",
        "short_desc_ne": "आरामदायी, प्राकृतिक देखिने र चपाउन सजिलो हुने पूर्ण तथा आंशिक नक्कली दाँत।",
        "features_ne": "पूर्ण तथा आंशिक डेन्चर\nप्राकृतिक देखिने र आरामदायी\nसजिलै सफा गर्न मिल्ने"
    },
    "Orthodontic Treatment": {
        "title_ne": "तार बाँध्ने उपचार (अर्थोडोन्टिक्स / ब्रेसेस)",
        "category_label_ne": "अर्थोडोन्टिक्स",
        "short_desc_ne": "बाङ्गो-टिङ्गो दाँत मिलाउन आधुनिक मेटल/सिरेमिक ब्रेसेस र अदृश्य क्लियर अलाइनर उपचार।",
        "features_ne": "मेटल तथा सिरेमिक ब्रेसेस\nअदृश्य क्लियर अलाइनर (Clear Aligners)\nसुन्दर मुस्कान र मिलेको दाँत"
    },
    "Periodontal Treatment": {
        "title_ne": "गिजा रोगको उपचार",
        "category_label_ne": "पेरियोडोन्टिक्स",
        "short_desc_ne": "गिजाबाट रगत आउने, सुन्निने र गिजाका अन्य समस्याहरूको विशेषज्ञ तथा लेजर उपचार।",
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
                safe_update_model(
                    Service.objects.filter(id=s.id),
                    title_en=title_en,
                    title_ne=data["title_ne"],
                    category_label_ne=data["category_label_ne"],
                    short_description_en=s.short_description or title_en,
                    short_description_ne=data["short_desc_ne"],
                    features_ne=data["features_ne"]
                )
                print(f"  [Service] {title_en} -> {data['title_ne']}")
                matched = True
                break
        if not matched:
            print(f"  [Service Skipped] {title_en}")

    print("\n--- 2. Updating Doctors ---")
    doctors_translations = {
        "subash": {
            "designation_en": "Clinical Director & Senior Dental Surgeon",
            "designation_ne": "क्लिनिकल निर्देशक तथा वरिष्ठ दन्त शल्यचिकित्सक",
            "qualifications_en": "BDS (KU), NMC #31229, Fellow in Advanced Endodontics",
            "qualifications_ne": "बीडीएस (केयू), एनएमसी #३१२२९, एडभान्स्ड इन्डोडोन्टिक्स फेलो",
            "bio_en": "Dr. Subash Banjade is a senior dental surgeon with extensive clinical expertise in painless root canal therapy, digital cosmetic smile design, and modern oral surgery. He leads CareFirst Dental Clinic with strict adherence to hospital-grade sterilization and patient-centric care.",
            "bio_ne": "डा. सुभाष बन्जाडे दुखाइरहित रूट क्यानल उपचार, डिजिटल कस्मेटिक स्माइल डिजाइन र आधुनिक दन्त शल्यक्रियामा विशेष दक्षता हासिल गर्नुभएका वरिष्ठ दन्त चिकित्सक हुनुहुन्छ। उहाँले उच्च अस्पताल मापदण्डको स्टेरिलाइजेसन र बिरामीमैत्री सेवाका साथ केयरफर्स्ट डेन्टल क्लिनिकको नेतृत्व गरिरहनुभएको छ।"
        },
        "bijaya": {
            "designation_en": "Dental Surgeon & General Practitioner",
            "designation_ne": "दन्त सर्जन",
            "qualifications_en": "BDS (KU)",
            "qualifications_ne": "बीडीएस (केयू)",
            "bio_en": "Dr. Bijaya Acharya focuses on patient comfort and comprehensive preventive dentistry, routine check-ups, aesthetic restorations, and gentle dental care.",
            "bio_ne": "डा. विजया आचार्यले रोगीको आराममा ध्यान केन्द्रित गरी रोकथाम, पुनर्स्थापना, र कस्मेटिक दन्त उपचार सहित व्यापक दन्त उपचार प्रदान गर्नुहुन्छ।"
        },
        "sudeep": {
            "designation_en": "Consultant Prosthodontist & Implantologist",
            "designation_ne": "परामर्शदाता प्रोस्थोडोन्टिस्ट",
            "qualifications_en": "MDS (BPKIHS, Dharan), BDS",
            "qualifications_ne": "एमडीएस (बीपीकेआईएचएस, धरान)",
            "bio_en": "Dr. Sudeep Subedi is a Consultant Prosthodontist dedicated to restoring oral function, aesthetics, and confidence through advanced crowns, bridges, dentures, and dental implant restorations.",
            "bio_ne": "डा. सुदीप सुवेदी आधुनिक क्राउन, ब्रिज, डेन्चर तथा डेन्टल इम्प्लान्टको माध्यमबाट बिरामीको दाँतको कार्यक्षमता, प्राकृतिक सौन्दर्य र आत्मविश्वास पुनर्स्थापना गर्न समर्पित विशेषज्ञ प्रोस्थोडोन्टिस्ट हुनुहुन्छ।"
        },
        "aarati": {
            "designation_en": "Senior Orthodontic Consultant",
            "designation_ne": "वरिष्ठ अर्थोडन्टिक परामर्शदाता",
            "qualifications_en": "BDS, MDS (Orthodontics & Dentofacial Orthopedics)",
            "qualifications_ne": "बीडीएस, एमडीएस (अर्थोडन्टिक्स)",
            "bio_en": "Dr. Aarati Sharma specializes in interceptive and comprehensive orthodontics, fixed metal & ceramic braces, clear aligners, and bite correction.",
            "bio_ne": "डा. आरती शर्मा बालबालिका तथा वयस्कहरूका लागि दाँत सिधा बनाउने, मेटल तथा सिरेमिक ब्रेसेस, क्लियर अलाइनर र बाङ्गाटिङ्गा दाँतको उपचारमा विशेषज्ञ हुनुहुन्छ।"
        },
        "pratik": {
            "designation_en": "Periodontist & Implant Surgeon",
            "designation_ne": "पेरियोडोन्टिस्ट तथा इम्प्लान्ट सर्जन",
            "qualifications_en": "BDS, MDS (Periodontology & Oral Implantology)",
            "qualifications_ne": "बीडीएस, एमडीएस (पेरियोडोन्टोलोजी र इम्प्लान्टोलोजी)",
            "bio_en": "Dr. Pratik Adhikari is an experienced periodontist and implantologist specializing in computer-guided titanium dental implants, sinus lift bone grafting, and advanced laser periodontal therapies.",
            "bio_ne": "डा. प्रतीक अधिकारी कम्प्यूटर निर्देशित टाइटेनियम डेन्टल इम्प्लान्ट, साइनस लिफ्ट बोन ग्राफ्टिङ र उन्नत लेजर गिजा उपचारमा अनुभवी विशेषज्ञ पेरियोडोन्टिस्ट हुनुहुन्छ।"
        },
        "sneha": {
            "designation_en": "Pediatric & Preventive Dental Surgeon",
            "designation_ne": "बाल दन्तरोग तथा रोकथाम विशेषज्ञ",
            "qualifications_en": "BDS (Dental Surgeon)",
            "qualifications_ne": "बीडीएस (दन्त शल्यचिकित्सक)",
            "bio_en": "Dr. Sneha Shrestha creates a fun, anxiety-free dental experience for children and teenagers. She focuses on pediatric preventive care, pit & fissure sealants, gentle fillings, and fluoride enamel therapies.",
            "bio_ne": "डा. स्नेहा श्रेष्ठले बालबालिका र किशोरकिशोरीहरूका लागि रमाइलो र डररहित दन्त उपचार वातावरण सिर्जना गर्नुहुन्छ। उहाँ बाल दन्त रोकथाम, सिल्यान्ट, कोमल फिलिङ र फ्लोराइड उपचारमा केन्द्रित हुनुहुन्छ।"
        }
    }

    for doc in Doctor.objects.all():
        name_lower = doc.name.lower()
        matched = False
        for key, trans in doctors_translations.items():
            if key in name_lower:
                safe_update_model(
                    Doctor.objects.filter(id=doc.id),
                    designation_en=trans["designation_en"],
                    designation_ne=trans["designation_ne"],
                    qualifications_en=trans["qualifications_en"],
                    qualifications_ne=trans["qualifications_ne"],
                    bio_en=trans["bio_en"],
                    bio_ne=trans["bio_ne"]
                )
                print(f"  [Doctor] Dr. {doc.name} updated in Nepali & English")
                matched = True
                break
        if not matched:
            print(f"  [Doctor Skipped/Unchanged] Dr. {doc.name}")

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
                safe_update_model(
                    CoreValue.objects.filter(id=cv.id),
                    title_en=title_en,
                    title_ne=t_ne,
                    description_en=cv.description or "",
                    description_ne=d_ne
                )
                print(f"  [CoreValue] {title_en} -> {t_ne}")
                break

    print("\n--- 4. Updating Testimonials ---")
    for t in Testimonial.objects.all():
        if t.review and not t.review_ne:
            safe_update_model(
                Testimonial.objects.filter(id=t.id),
                review_en=t.review,
                treatment_en=t.treatment or "Dental Care"
            )

    print("\n--- 5. Updating Educational Videos & Video Categories ---")
    video_cat_trans = {
        "Patient Education & Guides": "बिरामी शिक्षा तथा गाइडहरू",
        "Treatment Walkthroughs": "उपचार प्रक्रिया थ्रीडी भिडियोहरू",
        "Cosmetic & Smile Makeovers": "कस्मेटिक तथा मुस्कान सुधार",
        "Dental Implants & Surgery": "डेन्टल इम्प्लान्ट तथा शल्यक्रिया"
    }
    for vc in VideoCategory.objects.all():
        for k, v_ne in video_cat_trans.items():
            if k.lower() in vc.name.lower():
                safe_update_model(
                    VideoCategory.objects.filter(id=vc.id),
                    name_en=vc.name,
                    name_ne=v_ne
                )
                print(f"  [VideoCategory] {vc.name} -> {v_ne}")
                break

    videos_translations = {
        "root canal": {
            "title_ne": "रूट क्यानल उपचारको क्रममा के हुन्छ? (3D प्रक्रिया गाइड)",
            "short_desc_ne": "केयरफर्स्ट डेन्टल क्लिनिकमा माइक्रोस्कोपिक दुखाइरहित रूट क्यानल थेरापीको चरणबद्ध थ्रीडी प्रक्रिया।"
        },
        "implants": {
            "title_ne": "डेन्टल इम्प्लान्टको सम्पूर्ण जानकारी: एउटा दाँतदेखि पूरै मुखसम्म",
            "short_desc_ne": "हराएको दाँतको ठाउँमा आधुनिक थ्रीडी टाइटेनियम डेन्टल इम्प्लान्टले कसरी प्राकृतिक र स्थायी समाधान दिन्छ जान्नुहोस्।"
        },
        "aligners": {
            "title_ne": "क्लियर एलाइनर र परम्परागत ब्रेसेस: तपाईंको लागि कुन उपयुक्त छ?",
            "short_desc_ne": "बाङ्गो दाँत मिलाउन अदृश्य क्लियर एलाइनर र आधुनिक मेटल/सिरेमिक ब्रेसेस बीचको तुलना।"
        },
        "scaling": {
            "title_ne": "दाँत सफा (स्केलिङ) गर्दा दाँत कमजोर किन हुँदैन? भ्रम र यथार्थ",
            "short_desc_ne": "अल्ट्रासोनिक दाँत सफाइबारे गलत भ्रमहरू र नियमित स्केलिङले कसरी गिजाको रोग र मुखको दुर्गन्ध रोक्छ।"
        },
        "composite": {
            "title_ne": "कम्पोजिट डेन्टल फिलिङ: दाँतकै रङको प्राकृतिक दन्त पुनर्स्थापना",
            "short_desc_ne": "दाँतकै रङको कम्पोजिट रेजिन फिलिङले प्राकृतिक इनामेलसँग मिलेर किराले खाएको दाँत कसरी मर्मत गर्छ हेर्नुहोस्।"
        },
        "x-ray": {
            "title_ne": "डिजिटल डेन्टल एक्स-रे र ओपिजी: सुरक्षित र न्यून-रेडिएसन निदान",
            "short_desc_ne": "डिजिटल सेन्सर र प्यानोरामिक आरभीजीले फिल्मभन्दा ९०% कम रेडिएसनमा कसरी तत्काल उच्च गुणस्तरको स्क्यान दिन्छ।"
        },
        "brush": {
            "title_ne": "दाँत माझ्ने र फ्लस गर्ने सही तरिका: डाक्टरको दैनिक हेरचाह गाइड",
            "short_desc_ne": "दैनिक २ मिनेट दाँत माझ्ने वैज्ञानिक तरिका र डा. सुभाष बन्जाडेद्वारा सिफारिस गरिएको फ्लसिङ सल्लाह।"
        },
        "wisdom": {
            "title_ne": "अक्कल दाँत (Wisdom Tooth) निकाल्ने कहिले आवश्यक हुन्छ र निको पार्ने सुझावहरू",
            "short_desc_ne": "फसेको अक्कल दाँतका लक्षणहरू, दुखाइरहित निकाल्ने तरिका र छिटो निको हुने दिशानिर्देशहरू जान्नुहोस्।"
        }
    }
    for vid in Video.objects.all():
        title_lower = vid.title.lower()
        for k, vdata in videos_translations.items():
            if k in title_lower:
                safe_update_model(
                    Video.objects.filter(id=vid.id),
                    title_en=vid.title,
                    title_ne=vdata["title_ne"],
                    short_description_en=vid.short_description or vid.title,
                    short_description_ne=vdata["short_desc_ne"]
                )
                print(f"  [Video] {vid.title} -> {vdata['title_ne']}")
                break

    print("\n--- 6. Updating Blog Categories & Articles ---")
    from scripts.seed_blogs_nepali import seed_all_nepali_blogs
    seed_all_nepali_blogs()

    print("\n--- 7. Updating Pricing Categories & Items ---")
    pricing_cat_trans = {
        "General Dentistry": "साधारण दन्त चिकित्सा",
        "Root Canal": "रूट क्यानल उपचार (RCT)",
        "Crowns & Bridges": "दाँतको क्याप तथा ब्रिज",
        "Tooth Extraction": "दाँत निकाल्ने सेवा",
        "Dentures": "नक्कली दाँत (डेन्चर)",
        "Orthodontic": "तार बाँध्ने उपचार (अर्थोडोन्टिक्स / ब्रेसेस)",
        "Periodontal": "गिजा रोगको विशेष उपचार",
        "Dental Implants": "डेन्टल इम्प्लान्ट (दाँत प्रत्यारोपण)"
    }
    for pcat in PricingCategory.objects.all():
        name_en = pcat.name_en or pcat.name
        for k, c_ne in pricing_cat_trans.items():
            if k.lower() in name_en.lower():
                safe_update_model(
                    PricingCategory.objects.filter(id=pcat.id),
                    name_en=name_en,
                    name_ne=c_ne
                )
                print(f"  [PricingCategory] {name_en} -> {c_ne}")
                break

    pricing_item_trans = {
        "Registration & Check-up": "दर्ता तथा सम्पूर्ण दाँत परीक्षण",
        "Digital Dental X-Ray": "डिजिटल दाँतको एक्स-रे (RVG)",
        "Specialist Consultation": "विशेषज्ञ दन्त परामर्श",
        "Dental Filling": "दाँत भर्ने (कम्पोजिट लाइट क्योर फिलिङ)",
        "Scaling & Polishing": "दाँत सफाइ र पोलिसिङ (स्केलिङ)",
        "Curettage": "क्युटेज (गिजाको भित्री सफाइ)",
        "Child RCT": "बालबालिकाको रूट क्यानल (पल्पेक्टोमी)",
        "Adult RCT": "वयस्क रूट क्यानल (प्रति दाँत)",
        "Single-Sitting RCT": "एकै बसाइमा गरिने रूट क्यानल (Single Sitting RCT)",
        "All Metal": "मेटल क्याप (All Metal Crown)",
        "Metal Ceramic": "मेटल सिरामिक क्याप (PFM Crown)",
        "E-max": "ई-म्याक्स अल-सिरामिक क्याप (E-max Crown)",
        "Zirconia": "प्रिमियम जिर्कोनिया क्याप (Zirconia Crown)",
        "Child Extraction": "बालबालिकाको दाँत निकाल्ने",
        "Adult Extraction": "सामान्य दाँत निकाल्ने (वयस्क)",
        "Wisdom Tooth": "बुद्धि बंगारा निकाल्ने (Wisdom Tooth)",
        "Surgical Extraction": "शल्यक्रियाद्वारा बंगारा निकाल्ने (Surgical Extraction)",
        "Removable Partial Denture": "निकाल्न मिल्ने आंशिक नक्कली दाँत (RPD)",
        "Complete Denture": "पूरै मुखको नक्कली दाँत सेट (Complete Denture)",
        "Braces Treatment": "तार बाँध्ने उपचार (मेटल / सिरेमिक / क्लियर अलाइनर)",
        "Deep Cleaning": "गहिरो जरा सफाइ (Root Planing / Deep Cleaning)",
        "Flap Surgery": "गिजाको शल्यक्रिया (Flap Surgery)",
        "Splinting": "हल्लिरहेको दाँत बाँध्ने (Splinting)",
        "Dental Implant": "टाइटेनियम डेन्टल इम्प्लान्ट (Fixture Only)",
        "Bone Grafting": "हड्डी थप्ने प्रक्रिया (Bone Grafting)"
    }
    for pitem in PricingItem.objects.all():
        name_en = pitem.name_en or pitem.name
        matched = False
        for k, i_ne in pricing_item_trans.items():
            if k.lower() in name_en.lower():
                safe_update_model(
                    PricingItem.objects.filter(id=pitem.id),
                    name_en=name_en,
                    name_ne=i_ne,
                    price_en=pitem.price,
                    price_ne=pitem.price
                )
                print(f"  [PricingItem] {name_en} -> {i_ne}")
                matched = True
                break
        if not matched and not pitem.name_ne:
            safe_update_model(
                PricingItem.objects.filter(id=pitem.id),
                name_en=name_en,
                name_ne=name_en
            )

    print("\nAll database model translations successfully synchronized!")

if __name__ == '__main__':
    populate_all()
