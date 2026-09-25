import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding='utf-8')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
if connection.vendor == 'sqlite':
    try:
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA busy_timeout = 60000;")
            cursor.execute("PRAGMA journal_mode = WAL;")
            cursor.execute("PRAGMA synchronous = NORMAL;")
    except Exception:
        pass

from main.models import SEOFAQCategory, SEOFAQ

def seed_faqs():
    categories = [
        {"name": "Dental Implants", "slug": "dental-implants", "desc": "FAQs regarding dental implants cost, pain, and longevity in Nepal."},
        {"name": "Root Canal", "slug": "root-canal", "desc": "FAQs about root canal treatment process and cost."},
        {"name": "Orthodontics", "slug": "orthodontics", "desc": "FAQs regarding braces, clear aligners, and orthodontic treatment."},
        {"name": "Local SEO", "slug": "local-seo", "desc": "General local SEO questions about the clinic in Kathmandu."}
    ]

    for cat_data in categories:
        cat, created = SEOFAQCategory.objects.get_or_create(
            slug=cat_data['slug'],
            defaults={'name': cat_data['name'], 'description': cat_data['desc']}
        )
        print(f"[{'Created' if created else 'Exists'}] Category: {cat.name}")

    faqs = [
        # DENTAL IMPLANTS
        {
            "category_slug": "dental-implants",
            "question": "What is the cost of dental implants in Nepal?",
            "answer": "The cost of dental implants in Nepal depends on the brand of the implant, the material of the crown, and whether additional procedures like bone grafting are required. At Carefirst Dental Clinic in Kathmandu, we offer highly competitive and transparent pricing for premium titanium implants. Contact us for a precise estimate based on your specific clinical needs.",
            "primary_keyword": "dental implant cost in Nepal",
            "search_intent": "Commercial",
            "order": 1
        },
        {
            "category_slug": "dental-implants",
            "question": "How long do dental implants last?",
            "answer": "With proper oral hygiene and regular dental checkups, dental implants can last a lifetime. The titanium post fuses with your jawbone (osseointegration), making it incredibly stable. The visible crown on top may need replacement after 10 to 15 years depending on wear and tear.",
            "primary_keyword": "how long do dental implants last",
            "search_intent": "Informational",
            "order": 2
        },
        {
            "category_slug": "dental-implants",
            "question": "Is getting a dental implant painful?",
            "answer": "The dental implant procedure is performed under local anesthesia, so you will not feel pain during the surgery. Post-operative discomfort is usually mild and easily managed with over-the-counter pain relievers. Most of our patients report that extracting a tooth was actually more uncomfortable than placing the implant.",
            "primary_keyword": "is dental implant painful",
            "search_intent": "Informational",
            "order": 3
        },
        {
            "category_slug": "dental-implants",
            "question": "Am I a good candidate for dental implants?",
            "answer": "Most adults with missing teeth are excellent candidates for implants. Ideal candidates have healthy gums and sufficient jawbone density to support the implant. If you lack bone density, our experienced oral surgeons at Carefirst Dental Clinic can perform a bone grafting procedure to prepare your jaw for successful implantation.",
            "primary_keyword": "candidate for dental implants",
            "search_intent": "Informational",
            "order": 4
        },
        
        # ROOT CANAL
        {
            "category_slug": "root-canal",
            "question": "How long does a root canal take?",
            "answer": "A standard root canal treatment usually takes between 60 to 90 minutes. Depending on the severity of the infection and the specific tooth (molars have more canals than front teeth), it may be completed in a single visit or split across two appointments to ensure the infection is completely cleared.",
            "primary_keyword": "how long does a root canal take",
            "search_intent": "Informational",
            "order": 1
        },
        {
            "category_slug": "root-canal",
            "question": "What is the root canal cost in Nepal?",
            "answer": "Root canal cost in Nepal varies based on the tooth affected and the complexity of the treatment. Front teeth generally cost less than molars. At Carefirst Dental Clinic in Kathmandu, we use advanced rotary endodontics for painless and highly successful root canals at an affordable price.",
            "primary_keyword": "root canal cost in Nepal",
            "search_intent": "Local",
            "order": 2
        },
        {
            "category_slug": "root-canal",
            "question": "Is a root canal painful?",
            "answer": "Modern root canal therapy is practically painless. We use highly effective local anesthetics to completely numb the area before beginning. In fact, a root canal eliminates the severe tooth pain caused by the internal infection. Patients typically compare the experience to getting a standard dental filling.",
            "primary_keyword": "is root canal painful",
            "search_intent": "Informational",
            "order": 3
        },
        
        # ORTHODONTICS
        {
            "category_slug": "orthodontics",
            "question": "What is the braces price in Nepal?",
            "answer": "The braces price in Nepal depends on the type of braces you choose (traditional metal, ceramic, or clear aligners) and the complexity of your orthodontic case. At Carefirst Dental Clinic, we offer flexible installment plans for high-quality braces. Schedule a consultation for a personalized cost breakdown.",
            "primary_keyword": "braces price in Nepal",
            "search_intent": "Commercial",
            "order": 1
        },
        {
            "category_slug": "orthodontics",
            "question": "At what age should children get braces?",
            "answer": "The American Association of Orthodontists recommends that children have their first orthodontic evaluation by age 7. Early screening allows us to detect and correct jaw growth issues before they become severe. However, actual treatment with braces usually begins between ages 9 and 14 once most permanent teeth have erupted.",
            "primary_keyword": "when to get braces",
            "search_intent": "Informational",
            "order": 2
        },
        {
            "category_slug": "orthodontics",
            "question": "Do you offer invisible braces or aligners in Kathmandu?",
            "answer": "Yes! We offer state-of-the-art clear aligner therapy as an alternative to traditional metal braces. Clear aligners are virtually invisible, removable for eating and brushing, and highly comfortable. They are the perfect aesthetic choice for adults and teens looking to straighten their teeth discreetly.",
            "primary_keyword": "invisible braces Kathmandu",
            "search_intent": "Local",
            "order": 3
        },
        
        # LOCAL SEO
        {
            "category_slug": "local-seo",
            "question": "Where is CareFirst Dental Clinic located in Kathmandu?",
            "answer": "CareFirst Dental Clinic is conveniently located in Shankhamul-31 (Pragati Nagar Road), Kathmandu, directly in front of Sanima Bank and 200 meters ahead of the Police Office towards Mahadevsthan. We offer ample parking, wheelchair accessibility, and a modern, hygienic clinical environment.",
            "primary_keyword": "best dental clinic in Kathmandu",
            "search_intent": "Local",
            "order": 1
        },
        {
            "category_slug": "local-seo",
            "question": "Who is the lead dental surgeon at CareFirst Dental Clinic?",
            "answer": "CareFirst Dental Clinic is led by Dr. Subash Banjade (BDS, Senior Dental Surgeon, Nepal Medical Council Registration #31229) alongside a dedicated team of certified specialists in orthodontics, oral surgery, and endodontics.",
            "primary_keyword": "best dentist in Kathmandu",
            "search_intent": "Local",
            "order": 2
        },
        {
            "category_slug": "local-seo",
            "question": "What are your clinic opening hours and do you open on weekends?",
            "answer": "Our clinic is open 7 days a week from 7:30 AM to 7:30 PM, including Saturdays and public holidays, to ensure you receive timely dental care whenever you need it.",
            "primary_keyword": "dental clinic open on Saturday Kathmandu",
            "search_intent": "Local",
            "order": 3
        },
        {
            "category_slug": "local-seo",
            "question": "How do I book an appointment or emergency consultation?",
            "answer": "You can easily book an appointment online through our website, or call / WhatsApp us directly at +977 980-7464136 for immediate scheduling.",
            "primary_keyword": "dental appointment Kathmandu",
            "search_intent": "Commercial",
            "order": 4
        },
        {
            "category_slug": "local-seo",
            "question": "Are treatments at CareFirst Dental Clinic really painless?",
            "answer": "Yes! We specialize in pain-free dentistry using advanced local anesthesia techniques, computerized delivery systems, and gentle clinical methods to ensure maximum comfort even for patients with dental anxiety.",
            "primary_keyword": "painless dentistry Kathmandu",
            "search_intent": "Informational",
            "order": 5
        },
        {
            "category_slug": "local-seo",
            "question": "What payment options and installment (EMI) plans do you offer?",
            "answer": "We accept cash, all major debit/credit cards, Fonepay, eSewa, and Khalti digital wallets. We also provide flexible 0% interest installment (EMI) options for high-tier treatments such as dental implants and braces.",
            "primary_keyword": "affordable dental clinic Kathmandu",
            "search_intent": "Commercial",
            "order": 6
        },
        {
            "category_slug": "local-seo",
            "question": "What hygiene and sterilization standards do you follow?",
            "answer": "We adhere to international hospital-grade infection control protocols. All reusable instruments undergo a rigorous 6-step sterilization process using Class-B autoclaves, and single-use disposable barriers are used for every patient.",
            "primary_keyword": "safe dental clinic Kathmandu",
            "search_intent": "Informational",
            "order": 7
        },
        {
            "category_slug": "local-seo",
            "question": "Do you offer emergency dental services in Kathmandu?",
            "answer": "Yes, we provide emergency dental care for acute toothaches, dental trauma, knocked-out teeth, broken crowns, and facial swelling. Please contact our emergency hotline immediately at +977 980-7464136.",
            "primary_keyword": "emergency dentist Kathmandu",
            "search_intent": "Local",
            "order": 8
        },
    ]

    import time
    def safe_execute(func):
        for attempt in range(10):
            try:
                return func()
            except Exception as e:
                if 'locked' in str(e).lower() and attempt < 9:
                    connection.close()
                    time.sleep(1)
                else:
                    raise e

    for f_data in faqs:
        category = safe_execute(lambda s=f_data['category_slug']: SEOFAQCategory.objects.get(slug=s))
        faq, created = safe_execute(lambda c=category, fd=f_data: SEOFAQ.objects.update_or_create(
            category=c,
            question=fd['question'],
            defaults={
                'answer': fd['answer'],
                'primary_keyword': fd['primary_keyword'],
                'search_intent': fd['search_intent'],
                'order': fd['order']
            }
        ))
        print(f"[{'Added' if created else 'Updated'}] {faq.question}")

if __name__ == '__main__':
    seed_faqs()
    print("Database seeding completed.")

