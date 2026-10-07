import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding='utf-8')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.cache import cache
from main.models import SEOFAQCategory, SEOFAQ, SpecialOffer, Testimonial

def update_all():
    print("=" * 70)
    print("UPDATING FAQS, SPECIAL OFFERS & PATIENT STORIES (EN + NE)")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. LOCAL SEO FAQS (HOMEPAGE FAQ ACCORDION)
    # ---------------------------------------------------------
    print("\n--- 1. Updating Homepage Local SEO FAQs ---")
    cat, _ = SEOFAQCategory.objects.get_or_create(
        slug="local-seo",
        defaults={
            "name": "Local SEO & General FAQs",
            "name_en": "Local SEO & General FAQs",
            "name_ne": "सामान्य तथा क्लिनिक सम्बन्धी सोधिने प्रश्नहरू",
            "description": "Essential questions about CareFirst Dental Clinic Kathmandu location, hours, doctors and services.",
            "description_en": "Essential questions about CareFirst Dental Clinic Kathmandu location, hours, doctors and services.",
            "description_ne": "केयरफर्स्ट डेन्टल क्लिनिक काठमाडौँको स्थान, समय, डाक्टर तथा सेवा सम्बन्धी आवश्यक जानकारी।"
        }
    )

    local_faqs = [
        {
            "order": 1,
            "q_en": "Where is CareFirst Dental Clinic located in Kathmandu?",
            "a_en": "CareFirst Dental Clinic is conveniently located at Pragatinagar Road, Shankhamul-31, Kathmandu (in the peaceful Shankhamul / New Baneshwor area, near Shankhamul Bridge). We offer ample parking, wheelchair accessibility, and a modern, hygienic digital dental environment.",
            "q_ne": "केयरफर्स्ट डेन्टल क्लिनिक काठमाडौँमा कहाँ अवस्थित छ?",
            "a_ne": "केयरफर्स्ट डेन्टल क्लिनिक काठमाडौँको शंखमूल-३१ (प्रगतिनगर रोड, शंखमूल पुल नजिक, नयाँ बानेश्वर क्षेत्र) मा अवस्थित छ। क्लिनिकमा पर्याप्त पार्किङ, ह्विलचेयर पहुँच र आधुनिक, स्वच्छ डिजिटल दन्त वातावरण उपलब्ध छ।",
            "keyword": "best dental clinic in Kathmandu",
            "intent": "Local"
        },
        {
            "order": 2,
            "q_en": "Where is the best dental clinic in Kathmandu located?",
            "a_en": "CareFirst Dental Clinic is located at Pragatinagar Road, Shankhamul-31, Kathmandu. Recognized for exceptional clinical standards, we provide comprehensive multi-specialty dental treatments from routine checkups to complex implants under one roof.",
            "q_ne": "काठमाडौँको उत्कृष्ट दन्त क्लिनिक कहाँ अवस्थित छ?",
            "a_ne": "केयरफर्स्ट डेन्टल क्लिनिक काठमाडौँको शंखमूल-३१ (प्रगतिनगर रोड) मा अवस्थित छ। उच्च गुणस्तरीय दन्त सेवा, अत्याधुनिक उपकरण र विशेषज्ञ चिकित्सकहरूको टोलीका साथ हामी साधारण जाँचदेखि जटिल इम्प्लान्टसम्मका सम्पूर्ण सेवाहरू एकै छानामुनि उपलब्ध गराउँछौं।",
            "keyword": "top dental clinic Kathmandu",
            "intent": "Commercial"
        },
        {
            "order": 3,
            "q_en": "Who is the lead dental surgeon at CareFirst Dental Clinic?",
            "a_en": "CareFirst Dental Clinic is led by Dr. Subash Banjade (BDS, Senior Dental Surgeon, Nepal Medical Council Registration #32524) alongside certified specialists in orthodontics, oral and maxillofacial surgery, and endodontics.",
            "q_ne": "केयरफर्स्ट डेन्टल क्लिनिकका प्रमुख दन्त चिकित्सक को हुनुहुन्छ?",
            "a_ne": "केयरफर्स्ट डेन्टल क्लिनिक डा. सुवास बन्जाडे (BDS, बरिष्ठ दन्त चिकित्सक, नेपाल मेडिकल काउन्सिल दर्ता नं. ३२५२४) को नेतृत्वमा सञ्चालित छ। उहाँसँगै अर्थोडोन्टिक्स, ओरल सर्जरी तथा इन्डोडोन्टिक्सका विशेषज्ञ डाक्टरहरूको अनुभवी टोली कार्यरत छ।",
            "keyword": "best dentist in Kathmandu",
            "intent": "Local"
        },
        {
            "order": 4,
            "q_en": "What are your clinic opening hours and do you open on weekends?",
            "a_en": "Our clinic is open 7 days a week from 7:30 AM to 7:30 PM, including Saturdays and public holidays, ensuring timely and accessible dental care whenever you need it.",
            "q_ne": "क्लिनिक खुल्ने समय के हो र के शनिबार पनि खुला रहन्छ?",
            "a_ne": "हाम्रो क्लिनिक हप्ताको सातै दिन बिहान ७:३० बजेदेखि साँझ ७:३० बजेसम्म खुला रहन्छ। शनिबार तथा सार्वजनिक बिदाका दिनहरूमा पनि नियमित तथा आकस्मिक दन्त सेवा पूर्ण रूपमा सञ्चालन हुन्छ।",
            "keyword": "dental clinic open Saturday Kathmandu",
            "intent": "Local"
        },
        {
            "order": 5,
            "q_en": "How do I book an appointment or emergency consultation?",
            "a_en": "You can book an appointment directly through our online booking form on this website, or call / WhatsApp our front desk at +977 980-7464136 for instant scheduling.",
            "q_ne": "अपोइन्टमेन्ट वा आकस्मिक परामर्श कसरी बुक गर्ने?",
            "a_ne": "तपाईं हाम्रो वेबसाइटको अनलाइन फारममार्फत सजिलै अपोइन्टमेन्ट लिन सक्नुहुन्छ, वा हाम्रो हटलाइन नम्बर ९८०७४६४१३६ मा फोन तथा ह्वाट्सएप (WhatsApp) गरेर तत्काल समय तय गर्न सक्नुहुन्छ।",
            "keyword": "dental appointment Kathmandu",
            "intent": "Commercial"
        },
        {
            "order": 6,
            "q_en": "Are dental treatments at CareFirst Dental Clinic painless?",
            "a_en": "Yes! We specialize in pain-free dentistry using advanced local anesthesia, computerized delivery, and gentle techniques to guarantee a completely comfortable visit even for anxious patients.",
            "q_ne": "के केयरफर्स्ट डेन्टल क्लिनिकमा उपचार साँच्चै दुखाइरहित हुन्छ?",
            "a_ne": "हो! हामी विशेष पेनलेस एनेस्थेसिया प्रविधि, कोमल उपचार विधि र तनावमुक्त वातावरण प्रयोग गर्दछौं जसले गर्दा दाँतको उपचारको क्रममा कुनै दुखाइ वा डर महसुस हुँदैन।",
            "keyword": "painless dentistry Kathmandu",
            "intent": "Informational"
        },
        {
            "order": 7,
            "q_en": "What payment options and installment (EMI) plans do you offer?",
            "a_en": "We accept cash, major credit/debit cards, Fonepay, eSewa, and Khalti. We also offer flexible 0% interest EMI installment plans for advanced treatments including dental implants and orthodontic braces.",
            "q_ne": "तपाईंहरू कुन-कुन भुक्तानी विधि र किस्ताबन्दी (EMI) सुविधा स्वीकार गर्नुहुन्छ?",
            "a_ne": "हामी नगद, सबै प्रमुख डेबिट/क्रेडिट कार्ड, फोनपे (Fonepay), इसेवा (eSewa) र खल्ती (Khalti) स्वीकार गर्दछौं। साथै डेन्टल इम्प्लान्ट र ब्रेसेस जस्ता प्रमुख उपचारका लागि ०% ब्याजदरमा सहज किस्ताबन्दी (EMI) सुविधा पनि उपलब्ध छ।",
            "keyword": "affordable dental clinic Kathmandu",
            "intent": "Commercial"
        },
        {
            "order": 8,
            "q_en": "What hygiene and sterilization standards do you follow?",
            "a_en": "We maintain hospital-grade infection control protocols. All instruments undergo strict 6-step sterilization using Class-B vacuum autoclaves, and single-use disposable barriers are used for every patient.",
            "q_ne": "तपाईंहरू सरसफाइ र जीवाणुशोधनका कुन मापदण्ड पालना गर्नुहुन्छ?",
            "a_ne": "हामी अन्तर्राष्ट्रिय अस्पताल स्तरको संक्रमण नियन्त्रण मापदण्ड पालना गर्दछौं। सबै उपकरणहरू क्लास-बी भ्याकुम अटोक्लेभद्वारा ६-चरणको कडा स्टेरिलाइजेसन प्रक्रियाबाट गुज्रिन्छन् र प्रत्येक बिरामीका लागि नयाँ डिस्पोजेबल सामग्री प्रयोग गरिन्छ।",
            "keyword": "safe dental clinic Kathmandu",
            "intent": "Informational"
        },
        {
            "order": 9,
            "q_en": "Do you offer emergency dental services in Kathmandu?",
            "a_en": "Yes, we provide emergency dental care for acute toothaches, dental trauma, knocked-out teeth, broken crowns, and severe facial swelling. Contact our emergency line at +977 980-7464136 immediately.",
            "q_ne": "के तपाईंहरू काठमाडौँमा आकस्मिक दन्त सेवा प्रदान गर्नुहुन्छ?",
            "a_ne": "हो, दाँतको तीव्र दुखाइ, दाँत भाँचिएको, चोटपटक लागेको वा सुन्निएको अवस्थामा हामी तत्काल आकस्मिक सेवा प्रदान गर्दछौं। आकस्मिक सेवाका लागि हामीलाई ९८०७४६४१३६ मा तुरुन्त सम्पर्क गर्नुहोस्।",
            "keyword": "emergency dentist Kathmandu",
            "intent": "Local"
        },
        {
            "order": 10,
            "q_en": "What dental treatments and specialized services do you offer?",
            "a_en": "We provide comprehensive dental care including Dental Implants, Root Canal Treatment (RCT), Braces & Clear Aligners, Teeth Whitening, Cosmetic Veneers, Wisdom Tooth Extraction, Gum Therapy, Pediatric Dentistry, and Digital X-Rays.",
            "q_ne": "केयरफर्स्ट डेन्टल क्लिनिकमा कुन-कुन दन्त उपचार सेवाहरू उपलब्ध छन्?",
            "a_ne": "हामी डेन्टल इम्प्लान्ट, रूट क्यानल (RCT), दाँतमा तार बाँध्ने तथा क्लियर अलाइनर, दाँत चम्काउने (ह्वाइटनिङ), कस्मेटिक भिनियर, बुद्धि बंगारा निकाल्ने, गिजाको उपचार, बाल दन्त चिकित्सा र डिजिटल एक्सरे सहितका सम्पूर्ण सेवाहरू प्रदान गर्दछौं।",
            "keyword": "dental services Kathmandu",
            "intent": "Informational"
        }
    ]

    for item in local_faqs:
        # Check by question_en or question to avoid duplicates
        faq = SEOFAQ.objects.filter(category=cat, question__icontains=item["q_en"][:30]).first()
        if not faq:
            faq = SEOFAQ.objects.filter(category=cat, order=item["order"]).first()

        if faq:
            faq.question = item["q_en"]
            faq.question_en = item["q_en"]
            faq.question_ne = item["q_ne"]
            faq.answer = item["a_en"]
            faq.answer_en = item["a_en"]
            faq.answer_ne = item["a_ne"]
            faq.primary_keyword = item["keyword"]
            faq.search_intent = item["intent"]
            faq.order = item["order"]
            faq.is_active = True
            faq.save()
            print(f"  [Updated] FAQ #{faq.order}: {faq.question[:45]}...")
        else:
            faq = SEOFAQ.objects.create(
                category=cat,
                question=item["q_en"],
                question_en=item["q_en"],
                question_ne=item["q_ne"],
                answer=item["a_en"],
                answer_en=item["a_en"],
                answer_ne=item["a_ne"],
                primary_keyword=item["keyword"],
                search_intent=item["intent"],
                order=item["order"],
                is_active=True
            )
            print(f"  [Created] FAQ #{faq.order}: {faq.question[:45]}...")

    total_local_faqs = SEOFAQ.objects.filter(category=cat, is_active=True).count()
    print(f"Total Active Local SEO FAQs now: {total_local_faqs}")

    # ---------------------------------------------------------
    # 2. SPECIAL OFFERS (ENGLISH & NEPALI)
    # ---------------------------------------------------------
    print("\n--- 2. Updating Special Offers (EN + NE) ---")
    offers = SpecialOffer.objects.all()
    if not offers.exists():
        print("  Creating default Special Offer...")
        from django.utils import timezone
        import datetime
        offer = SpecialOffer.objects.create(
            title="Dental Care Special Offer",
            title_en="Dental Care Special Offer",
            title_ne="दन्त स्वास्थ्य विशेष छुट अफर",
            description="Get 10% discount on comprehensive dental checkup, scaling & polishing at CareFirst Dental Clinic.",
            description_en="Get 10% discount on comprehensive dental checkup, scaling & polishing at CareFirst Dental Clinic.",
            description_ne="केयरफर्स्ट डेन्टल क्लिनिकमा विस्तृत दाँत परीक्षण, स्केलिङ तथा पोलिसिङ सेवामा १०% विशेष छुट पाउनुहोस्।",
            highlight_text="10% OFF",
            highlight_text_en="10% OFF",
            highlight_text_ne="१०% छुट",
            sub_text="ON DENTAL CHECKUP & SCALING",
            sub_text_en="ON DENTAL CHECKUP & SCALING",
            sub_text_ne="दाँत परीक्षण तथा स्केलिङमा",
            badge_text="SPECIAL DENTAL OFFER",
            badge_text_en="SPECIAL DENTAL OFFER",
            badge_text_ne="विशेष दन्त अफर",
            button_text="Book Appointment Now",
            button_text_en="Book Appointment Now",
            button_text_ne="अहिले नै अपोइन्टमेन्ट लिनुहोस्",
            button_link="/contact/#book",
            features="Comprehensive Dental Checkup | Detailed digital consultation by expert dentists\n10% Special Discount | On scaling, polishing and routine prophylaxis\nZero Waiting Time | Hassle-free appointment scheduling at Shankhamul",
            features_en="Comprehensive Dental Checkup | Detailed digital consultation by expert dentists\n10% Special Discount | On scaling, polishing and routine prophylaxis\nZero Waiting Time | Hassle-free appointment scheduling at Shankhamul",
            features_ne="विस्तृत दन्त परीक्षण | अनुभवी दन्त चिकित्सकद्वारा डिजिटल परामर्श\n१०% विशेष छुट | दाँत सफा गर्ने (स्केलिङ) तथा पोलिसिङ सेवामा\nकुनै प्रतीक्षा गर्नु नपर्ने | शंखमूलमा सहज तथा तत्काल अपोइन्टमेन्ट सुविधा",
            start_date=timezone.now() - datetime.timedelta(days=1),
            end_date=timezone.now() + datetime.timedelta(days=90),
            is_active=True
        )
        print(f"  [Created] Special Offer: {offer.title}")
    else:
        for offer in offers:
            offer.title_en = offer.title or "Dental Care Special Offer"
            offer.title_ne = "दन्त स्वास्थ्य विशेष छुट अफर"
            
            offer.description_en = offer.description or "Get 10% discount on comprehensive dental checkup, scaling & polishing at CareFirst Dental Clinic."
            offer.description_ne = "केयरफर्स्ट डेन्टल क्लिनिकमा विस्तृत दाँत परीक्षण, स्केलिङ तथा पोलिसिङ सेवामा १०% विशेष छुट पाउनुहोस्।"

            offer.highlight_text = offer.highlight_text or "10% OFF"
            offer.highlight_text_en = offer.highlight_text
            offer.highlight_text_ne = "१०% छुट"

            offer.sub_text = offer.sub_text or "ON DENTAL CHECKUP & SCALING"
            offer.sub_text_en = offer.sub_text
            offer.sub_text_ne = "दाँत परीक्षण तथा स्केलिङमा"

            offer.badge_text = offer.badge_text or "SPECIAL DENTAL OFFER"
            offer.badge_text_en = offer.badge_text
            offer.badge_text_ne = "विशेष दन्त अफर"

            offer.button_text = offer.button_text or "Book Appointment Now"
            offer.button_text_en = offer.button_text
            offer.button_text_ne = "अहिले नै अपोइन्टमेन्ट लिनुहोस्"

            features_en = "Comprehensive Dental Checkup | Detailed digital consultation by expert dentists\n10% Special Discount | On scaling, polishing and routine prophylaxis\nZero Waiting Time | Hassle-free appointment scheduling at Shankhamul"
            features_ne = "विस्तृत दन्त परीक्षण | अनुभवी दन्त चिकित्सकद्वारा डिजिटल परामर्श\n१०% विशेष छुट | दाँत सफा गर्ने (स्केलिङ) तथा पोलिसिङ सेवामा\nकुनै प्रतीक्षा गर्नु नपर्ने | शंखमूलमा सहज तथा तत्काल अपोइन्टमेन्ट सुविधा"

            if not offer.features or not offer.features.strip():
                offer.features = features_en
            offer.features_en = offer.features
            offer.features_ne = features_ne

            offer.is_active = True
            offer.save()
            print(f"  [Updated] Special Offer #{offer.id}: EN='{offer.title_en}' | NE='{offer.title_ne}'")

    # ---------------------------------------------------------
    # 3. PATIENT STORIES & TESTIMONIALS (ENGLISH & NEPALI)
    # ---------------------------------------------------------
    print("\n--- 3. Updating Patient Stories / Testimonials (EN + NE) ---")
    stories_data = {
        "Rekha Tamang": {
            "name_ne": "रेखा तामाङ",
            "treatment_en": "Composite Veneer Bonding",
            "treatment_ne": "कम्पोजिट भिनियर बन्डिङ (अगाडिका दाँतको कस्मेटिक उपचार)",
            "review_en": "Composite veneers in one sitting — I couldn't believe how different I looked when I saw myself. The gap between my front teeth is gone.",
            "review_ne": "एकै पटकको बसाइमा कम्पोजिट भिनियर — ऐनामा हेर्दा मेरो मुहार कति फरक र सुन्दर देखियो भनेर म विश्वासै गर्न सकिनँ। मेरा अगाडिका दाँत बीचको खाली ठाउँ पूर्ण रूपमा हरायो।",
            "initial_concern": "Patient had noticeable spacing (diastema) between anterior teeth affecting aesthetic confidence.",
            "clinical_journey": "Single-visit direct composite veneer bonding crafted meticulously with shade matching by Dr. Subash Banjade (BDS, NMC #32524).",
            "outcome": "Seamless smile makeover completed in just 90 minutes with zero enamel damage."
        },
        "Prakash Adhikari": {
            "name_ne": "प्रकाश अधिकारी",
            "treatment_en": "Dual Dental Implants",
            "treatment_ne": "डेन्टल इम्प्लान्ट (दाँत प्रत्यारोपण)",
            "review_en": "I was missing two teeth and it affected my confidence. The dental implants look and feel exactly like my natural teeth. I can eat anything now!",
            "review_ne": "मेरा दुईवटा दाँत नहुँदा खान र हाँस्न धेरै असहज हुन्थ्यो। केयरफर्स्टमा लगाएको डेन्टल इम्प्लान्ट ठ्याक्कै प्राकृतिक दाँत जस्तै देखिन्छ र महसुस हुन्छ। अब म जे पनि ढुक्कले खान सक्छु!",
            "initial_concern": "Missing posterior molars causing difficulty chewing and reduced bite efficiency.",
            "clinical_journey": "Precision surgical placement of titanium implants followed by osseointegration and custom zirconia crowns.",
            "outcome": "100% masticatory function restored with permanent, stable artificial tooth roots."
        },
        "Anita Dhungana": {
            "name_ne": "अनिता ढुङ्गाना",
            "treatment_en": "Zoom! Teeth Whitening",
            "treatment_ne": "जुम! दाँत चम्काउने (ह्वाइटनिङ)",
            "review_en": "Got my teeth whitened before my wedding — 8 shades in one session! The results lasted for months and the process was completely painless.",
            "review_ne": "मेरो विवाह अगाडि दाँत ह्वाइटनिङ गराएकी थिएँ — एकै सेसनमा ८ सेड चम्किलो भयो! नतिजा महिनौंसम्म टिक्यो र प्रक्रिया पूर्णतया दुखाइरहित थियो।",
            "initial_concern": "Severe stubborn enamel discoloration prior to a major personal life milestone.",
            "clinical_journey": "Professional in-chair light-accelerated hydrogen peroxide bleaching with protective gingival barrier.",
            "outcome": "Dramatic 8-shade brightening with zero post-operative tooth sensitivity."
        },
        "Sunita Karki": {
            "name_ne": "सुनिता कार्की",
            "treatment_en": "Clear Aligners",
            "treatment_ne": "क्लियर अलाइनर (अदृश्य ब्रेसेस)",
            "review_en": "I had severe crowding for years and always hid my smile. After clear aligners at Carefirst Dental Clinic, I smile in every photo now. The team was so supportive.",
            "review_ne": "वर्षौंदेखि मेरा दाँत बाङ्गाटिङ्गा थिए र म सधैं हाँस्दा मुख छोप्ने गर्थें। केयरफर्स्ट डेन्टल क्लिनिकमा क्लियर अलाइनर लगाएपछि अहिले म प्रत्येक फोटोमा ढुक्कले हाँस्छु। स्वास्थ्य टोली निकै सहयोगी थियो।",
            "initial_concern": "Moderate crowding of maxillary and mandibular teeth with deep bite.",
            "clinical_journey": "Digital 3D intraoral scanning, customized sequential invisible aligners monitored bi-weekly.",
            "outcome": "Perfect dental arch alignment and harmonious smile line achieved without visible metal wires."
        }
    }

    for story in Testimonial.objects.all():
        data = None
        for key in stories_data:
            if key.lower() in story.patient_name.lower():
                data = stories_data[key]
                break

        if data:
            story.patient_name_en = story.patient_name
            story.patient_name_ne = data["name_ne"]
            story.treatment_en = data["treatment_en"]
            story.treatment_ne = data["treatment_ne"]
            story.review_en = data["review_en"]
            story.review_ne = data["review_ne"]
            story.initial_concern = data["initial_concern"]
            story.clinical_journey = data["clinical_journey"]
            story.outcome = data["outcome"]
            story.is_active = True
            story.save()
            print(f"  [Updated] Story #{story.id}: {story.patient_name} -> {story.patient_name_ne}")
        else:
            print(f"  [Skipped / Not matched] Story #{story.id}: {story.patient_name}")

    # ---------------------------------------------------------
    # 4. CLEAR REVIEWS / SOCIAL PROOF CACHE
    # ---------------------------------------------------------
    print("\n--- 4. Invalidating Django Cache ---")
    cache.delete('google_reviews_context_data')
    cache.clear()
    print("  [OK] Cache cleared successfully.")

    print("\n" + "=" * 70)
    print("SYNC COMPLETE SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    update_all()
