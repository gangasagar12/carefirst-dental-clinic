import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from blogs.models import Category, Post
from django.utils.text import slugify

print("Creating categories...")
categories_data = [
    ("General Dentistry", "साधारण दन्त चिकित्सा"),
    ("Dental Implants", "डेन्टल इम्प्लान्ट"),
    ("Root Canal Treatment", "रूट क्यानल उपचार"),
    ("Orthodontics", "तार बाँध्ने उपचार (ब्रेसेस)"),
    ("Gum Treatment", "गिजाको उपचार"),
    ("Oral Hygiene", "मुखको सरसफाइ"),
]

cats = {}
for name_en, name_ne in categories_data:
    cat, _ = Category.objects.get_or_create(
        name=name_en,
        defaults={
            'name_en': name_en,
            'name_ne': name_ne,
            'slug': slugify(name_en),
        }
    )
    cat.name_en = name_en
    cat.name_ne = name_ne
    cat.save()
    cats[name_en] = cat

print("Creating posts...")
posts_data = [
    {
        "title": "The Ultimate Guide to Dental Implants in 2026",
        "title_ne": "२०२६ मा डेन्टल इम्प्लान्टको सम्पूर्ण जानकारी",
        "category": cats["Dental Implants"],
        "excerpt": "Everything you need to know about replacing missing teeth with durable, natural-looking dental implants.",
        "excerpt_ne": "हराएको दाँतको ठाउँमा प्राकृतिक देखिने र जीवनभर टिक्ने डेन्टल इम्प्लान्ट सम्बन्धी सम्पूर्ण आवश्यक जानकारी।",
        "content": "<p>Dental implants are the gold standard for replacing missing teeth, offering unmatched durability and natural aesthetics...</p>",
        "content_ne": "<p>डेन्टल इम्प्लान्ट आधुनिक दन्त चिकित्साको सबैभन्दा भरपर्दो र दिगो समाधान हो, जसले हराएको दाँतलाई प्राकृतिक रूपमा पुनर्स्थापना गर्दछ...</p>",
        "is_featured": True,
        "is_popular": True,
        "reading_time": "8 min read",
        "reading_time_ne": "८ मिनेट पढाइ",
    },
    {
        "title": "5 Signs You Might Need a Root Canal",
        "title_ne": "५ मुख्य लक्षणहरू जसले तपाईंलाई रूट क्यानल चाहिन्छ भन्ने जनाउँछ",
        "category": cats["Root Canal Treatment"],
        "excerpt": "Don't ignore tooth pain. Learn the top five warning signs that indicate you might need endodontic therapy to save your tooth.",
        "excerpt_ne": "दाँतको दुखाइलाई बेवास्ता नगर्नुहोस्। दाँत जोगाउन रूट क्यानल थेरापी आवश्यक पर्ने ५ मुख्य संकेतहरू जान्नुहोस्।",
        "content": "<p>Severe toothaches, prolonged sensitivity to hot and cold, and swollen gums are key signs that your dental pulp may be infected...</p>",
        "content_ne": "<p>दाँतको गहिरो दुखाइ, तातो-चिसो खाँदा अत्यधिक संवेदनशीलता, र गिजा सुन्निने समस्या रूट क्यानल उपचार आवश्यक पर्ने प्रमुख लक्षणहरू हुन्...</p>",
        "is_featured": False,
        "is_popular": True,
        "reading_time": "5 min read",
        "reading_time_ne": "५ मिनेट पढाइ",
    },
    {
        "title": "Invisalign vs. Traditional Braces: Which is Right for You?",
        "title_ne": "क्लियर एलाइनर र परम्परागत ब्रेसेस: कुन तपाईंको लागि सही छ?",
        "category": cats["Orthodontics"],
        "excerpt": "Compare the pros and cons of clear aligners and traditional metal braces to find the best orthodontic solution for your smile.",
        "excerpt_ne": "आफ्नो मुस्कान सुधारका लागि क्लियर एलाइनर र मेटल ब्रेसेस बीचको फाइदा र बेफाइदा तुलना गर्नुहोस्।",
        "content": "<p>Both clear aligners and modern braces can straighten teeth and correct bite alignment with remarkable precision...</p>",
        "content_ne": "<p>अदृश्य क्लियर एलाइनर र आधुनिक मेटल ब्रेसेस दुवैले दाँत सिधा बनाउन र टोकाइ सच्याउन उत्कृष्ट परिणाम दिन्छन्...</p>",
        "is_featured": False,
        "is_popular": True,
        "reading_time": "6 min read",
        "reading_time_ne": "६ मिनेट पढाइ",
    },
    {
        "title": "How to Prevent Gum Disease Before It Starts",
        "title_ne": "गिजाको रोग सुरु हुनु अघि नै कसरी रोक्ने?",
        "category": cats["Gum Treatment"],
        "excerpt": "Periodontal disease is common but preventable. Discover the best daily habits to keep your gums healthy and strong.",
        "excerpt_ne": "गिजाको रोग सामान्य भए पनि रोकथाम गर्न सकिन्छ। गिजा स्वस्थ र बलियो राख्ने दैनिक बानीहरू जान्नुहोस्।",
        "content": "<p>Daily brushing, interdental flossing, and routine dental cleanings are the strongest defenses against gingivitis and periodontitis...</p>",
        "content_ne": "<p>दैनिक दुई पटक ब्रसिङ, इन्टरडेन्टल फ्लसिङ र नियमित दन्त परीक्षणले गिजाबाट रगत आउने र सुन्निने समस्या रोक्न मद्दत गर्छ...</p>",
        "is_featured": False,
        "is_popular": False,
        "reading_time": "4 min read",
        "reading_time_ne": "४ मिनेट पढाइ",
    },
    {
        "title": "Why Professional Scaling is Essential Twice a Year",
        "title_ne": "वर्षमा दुई पटक दाँतको व्यावसायिक सफाइ (स्केलिङ) किन आवश्यक छ?",
        "category": cats["Oral Hygiene"],
        "excerpt": "Brushing at home isn't enough to remove hardened tartar. Find out why a professional dental cleaning is crucial for your oral health.",
        "excerpt_ne": "घरमा ब्रस गर्दा कडा टारटार हट्दैन। दाँत र गिजाको स्वास्थ्यका लागि व्यावसायिक स्केलिङ किन जरुरी छ जान्नुहोस्।",
        "content": "<p>Ultrasonic dental scaling safely eliminates hardened plaque and tartar without touching or harming your natural tooth enamel...</p>",
        "content_ne": "<p>अल्ट्रासोनिक स्केलिङले दाँतको इनामेललाई कुनै क्षति नगरी फोहोर, पहेँलोपन र कडा टारटार हटाउँछ...</p>",
        "is_featured": False,
        "is_popular": False,
        "reading_time": "3 min read",
        "reading_time_ne": "३ मिनेट पढाइ",
    },
    {
        "title": "What to Expect During Your First Visit to Carefirst Dental Clinic",
        "title_ne": "केयरफर्स्ट डेन्टल क्लिनिकमा पहिलो भ्रमणको क्रममा के अपेक्षा गर्ने?",
        "category": cats["General Dentistry"],
        "excerpt": "Nervous about your upcoming dental appointment? Here is a step-by-step breakdown of what happens during your first comprehensive exam.",
        "excerpt_ne": "दन्त परीक्षणका लागि आउँदै हुनुहुन्छ? पहिलो परामर्श र डिजिटल एक्स-रे परीक्षणको चरणबद्ध विवरण।",
        "content": "<p>From digital RVG imaging to personalized treatment discussions with Dr. Subash Banjade, your comfort is always our first priority...</p>",
        "content_ne": "<p>डिजिटल आरभीजी एक्स-रे स्क्यानदेखि डा. सुभाष बन्जाडेसँगको व्यक्तिगत परामर्शसम्म, तपाईंको आराम र सुरक्षा हाम्रो पहिलो प्राथमिकता हो...</p>",
        "is_featured": False,
        "is_popular": True,
        "reading_time": "5 min read",
        "reading_time_ne": "५ मिनेट पढाइ",
    }
]

for p in posts_data:
    post, created = Post.objects.update_or_create(
        title=p['title'],
        defaults={
            'title_en': p['title'],
            'title_ne': p['title_ne'],
            'category': p['category'],
            'excerpt': p['excerpt'],
            'excerpt_en': p['excerpt'],
            'excerpt_ne': p['excerpt_ne'],
            'content': p['content'],
            'content_en': p['content'],
            'content_ne': p['content_ne'],
            'is_featured': p['is_featured'],
            'is_popular': p['is_popular'],
            'reading_time': p['reading_time'],
            'reading_time_en': p['reading_time'],
            'reading_time_ne': p['reading_time_ne'],
            'author': "CareFirst Specialist Dental Team",
            'is_published': True,
        }
    )
    status = "Created" if created else "Updated"
    print(f"  {status} Post: {post.title} (Nepali: {post.title_ne})")

print("Blog categories and posts successfully populated with English and Nepali content!")
