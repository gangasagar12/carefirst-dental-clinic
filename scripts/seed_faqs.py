import os
import django

# Setup django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

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
            "question": "Where is the best dental clinic in Kathmandu located?",
            "answer": "Carefirst Dental Clinic is conveniently located in Koteshwor-32, Kathmandu, exactly in front of Sanima Bank and 200m ahead of the Police Office towards Mahadevsthan. We are easily accessible and provide a comfortable, state-of-the-art environment for all your dental needs.",
            "primary_keyword": "best dental clinic in Kathmandu",
            "search_intent": "Local",
            "order": 1
        },
        {
            "category_slug": "local-seo",
            "question": "Do you offer emergency dental services in Kathmandu?",
            "answer": "Yes, we provide emergency dental care in Kathmandu for severe toothaches, knocked-out teeth, broken crowns, and dental trauma. If you are experiencing a dental emergency, please call our clinic immediately at 984-8631371 for prompt assistance.",
            "primary_keyword": "emergency dentist in Kathmandu",
            "search_intent": "Local",
            "order": 2
        },
    ]

    for f_data in faqs:
        category = SEOFAQCategory.objects.get(slug=f_data['category_slug'])
        faq, created = SEOFAQ.objects.get_or_create(
            category=category,
            question=f_data['question'],
            defaults={
                'answer': f_data['answer'],
                'primary_keyword': f_data['primary_keyword'],
                'search_intent': f_data['search_intent'],
                'order': f_data['order']
            }
        )
        print(f"[{'Added' if created else 'Exists'}] {faq.question}")

if __name__ == '__main__':
    seed_faqs()
    print("Database seeding completed.")
