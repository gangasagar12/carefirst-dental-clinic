import os
import sys
import django

# Add root project path to resolve core settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from media_center.models import Video, VideoCategory
from main.models import Service

def seed_videos():
    print("Seeding Video Library Categories & Videos...")

    # 1. Categories
    cat_edu, _ = VideoCategory.objects.get_or_create(
        name="Patient Education & Guides",
        defaults={"name_en": "Patient Education & Guides", "name_ne": "बिरामी शिक्षा तथा गाइडहरू", "order": 1}
    )
    cat_walk, _ = VideoCategory.objects.get_or_create(
        name="Treatment Walkthroughs",
        defaults={"name_en": "Treatment Walkthroughs", "name_ne": "उपचार प्रक्रिया थ्रीडी भिडियोहरू", "order": 2}
    )
    cat_cosmetic, _ = VideoCategory.objects.get_or_create(
        name="Cosmetic & Smile Makeovers",
        defaults={"name_en": "Cosmetic & Smile Makeovers", "name_ne": "कस्मेटिक तथा मुस्कान सुधार", "order": 3}
    )
    cat_implant, _ = VideoCategory.objects.get_or_create(
        name="Dental Implants & Surgery",
        defaults={"name_en": "Dental Implants & Surgery", "name_ne": "डेन्टल इम्प्लान्ट तथा शल्यक्रिया", "order": 4}
    )

    # Update category translations if already existed
    cat_edu.name_ne = "बिरामी शिक्षा तथा गाइडहरू"; cat_edu.save()
    cat_walk.name_ne = "उपचार प्रक्रिया थ्रीडी भिडियोहरू"; cat_walk.save()
    cat_cosmetic.name_ne = "कस्मेटिक तथा मुस्कान सुधार"; cat_cosmetic.save()
    cat_implant.name_ne = "डेन्टल इम्प्लान्ट तथा शल्यक्रिया"; cat_implant.save()

    # 2. Services mapping
    service_rct = Service.objects.filter(slug__icontains="root-canal").first()
    service_implant = Service.objects.filter(slug__icontains="dental-implant").first()
    service_ortho = Service.objects.filter(slug__icontains="orthodontic").first()
    service_clean = Service.objects.filter(slug__icontains="scaling").first()
    service_fill = Service.objects.filter(slug__icontains="filling").first()
    service_xray = Service.objects.filter(slug__icontains="x-ray").first()

    videos_data = [
        {
            "title": "What Happens During a Root Canal Treatment?",
            "title_ne": "रूट क्यानल उपचारको क्रममा के हुन्छ? (3D प्रक्रिया गाइड)",
            "video_url": "https://www.youtube.com/watch?v=jHLp_m24sW4",
            "category": cat_walk,
            "related_service": service_rct,
            "short_description": "A gentle 3D step-by-step walkthrough of microscopic painless root canal therapy at CareFirst Dental Clinic.",
            "short_description_ne": "केयरफर्स्ट डेन्टल क्लिनिकमा माइक्रोस्कोपिक दुखाइरहित रूट क्यानल थेरापीको चरणबद्ध थ्रीडी प्रक्रिया。",
            "is_featured": True,
            "thumbnail_url": "https://img.youtube.com/vi/jHLp_m24sW4/hqdefault.jpg",
            "order": 1,
        },
        {
            "title": "Dental Implants Explained: Single Tooth to Full Mouth",
            "title_ne": "डेन्टल इम्प्लान्टको सम्पूर्ण जानकारी: एउटा दाँतदेखि पूरै मुखसम्म",
            "video_url": "https://www.youtube.com/watch?v=kYv_8RjC_wE",
            "category": cat_implant,
            "related_service": service_implant,
            "short_description": "Learn how modern 3D titanium dental implants provide a permanent, natural-looking replacement for missing teeth.",
            "short_description_ne": "हराएको दाँतको ठाउँमा आधुनिक थ्रीडी टाइटेनियम डेन्टल इम्प्लान्टले कसरी प्राकृतिक र स्थायी समाधान दिन्छ जान्नुहोस्।",
            "is_featured": True,
            "thumbnail_url": "https://img.youtube.com/vi/kYv_8RjC_wE/hqdefault.jpg",
            "order": 2,
        },
        {
            "title": "Clear Aligners vs Traditional Braces: Which is Right for You?",
            "title_ne": "क्लियर एलाइनर र परम्परागत ब्रेसेस: तपाईंको लागि कुन उपयुक्त छ?",
            "video_url": "https://www.youtube.com/watch?v=fDoxd_W3w90",
            "category": cat_cosmetic,
            "related_service": service_ortho,
            "short_description": "Compare invisible clear aligners and modern metal/ceramic braces for straightening crooked teeth and bite alignment.",
            "short_description_ne": "बाङ्गो दाँत मिलाउन अदृश्य क्लियर एलाइनर र आधुनिक मेटल/सिरेमिक ब्रेसेस बीचको तुलना।",
            "is_featured": True,
            "thumbnail_url": "https://img.youtube.com/vi/fDoxd_W3w90/hqdefault.jpg",
            "order": 3,
        },
        {
            "title": "Why Scaling and Teeth Cleaning Does Not Weaken Your Enamel",
            "title_ne": "दाँत सफा (स्केलिङ) गर्दा दाँत कमजोर किन हुँदैन? भ्रम र यथार्थ",
            "video_url": "https://www.youtube.com/watch?v=4R4U0r5C8wA",
            "category": cat_edu,
            "related_service": service_clean,
            "short_description": "Debunking common myths about ultrasonic dental scaling and why routine cleaning prevents gum disease and bad breath.",
            "short_description_ne": "अल्ट्रासोनिक दाँत सफाइबारे गलत भ्रमहरू र नियमित स्केलिङले कसरी गिजाको रोग र मुखको दुर्गन्ध रोक्छ।",
            "is_featured": True,
            "thumbnail_url": "https://img.youtube.com/vi/4R4U0r5C8wA/hqdefault.jpg",
            "order": 4,
        },
        {
            "title": "Composite Dental Fillings: Tooth-Colored Natural Restoration",
            "title_ne": "कम्पोजिट डेन्टल फिलिङ: दाँतकै रङको प्राकृतिक दन्त पुनर्स्थापना",
            "video_url": "https://www.youtube.com/watch?v=S8pB4k_8Zto",
            "category": cat_walk,
            "related_service": service_fill,
            "short_description": "See how tooth-colored composite resin fillings seamlessly repair dental cavities while blending with your natural enamel.",
            "short_description_ne": "दाँतकै रङको कम्पोजिट रेजिन फिलिङले प्राकृतिक इनामेलसँग मिलेर किराले खाएको दाँत कसरी मर्मत गर्छ हेर्नुहोस्।",
            "is_featured": False,
            "thumbnail_url": "https://img.youtube.com/vi/S8pB4k_8Zto/hqdefault.jpg",
            "order": 5,
        },
        {
            "title": "Digital Dental X-Rays & OPG: Safe Low-Radiation Diagnostics",
            "title_ne": "डिजिटल डेन्टल एक्स-रे र ओपिजी: सुरक्षित र न्यून-रेडिएसन निदान",
            "video_url": "https://www.youtube.com/watch?v=X6P6k_8w7bY",
            "category": cat_edu,
            "related_service": service_xray,
            "short_description": "How digital sensors and panoramic RVG provide instant high-definition scans with 90% less radiation than film.",
            "short_description_ne": "डिजिटल सेन्सर र प्यानोरामिक आरभीजीले फिल्मभन्दा ९०% कम रेडिएसनमा कसरी तत्काल उच्च गुणस्तरको स्क्यान दिन्छ।",
            "is_featured": False,
            "thumbnail_url": "https://img.youtube.com/vi/X6P6k_8w7bY/hqdefault.jpg",
            "order": 6,
        },
        {
            "title": "How to Properly Brush and Floss: Doctor's Daily Oral Care Guide",
            "title_ne": "दाँत माझ्ने र फ्लस गर्ने सही तरिका: डाक्टरको दैनिक हेरचाह गाइड",
            "video_url": "https://www.youtube.com/watch?v=xm9c5HAUBpY",
            "category": cat_edu,
            "related_service": service_clean,
            "short_description": "Essential 2-minute daily brushing techniques and interdental flossing tips recommended by Dr. Subash Banjade.",
            "short_description_ne": "दैनिक २ मिनेट दाँत माझ्ने वैज्ञानिक तरिका र डा. सुभाष बन्जाडेद्वारा सिफारिस गरिएको फ्लसिङ सल्लाह।",
            "is_featured": False,
            "thumbnail_url": "https://img.youtube.com/vi/xm9c5HAUBpY/hqdefault.jpg",
            "order": 7,
        },
        {
            "title": "Wisdom Tooth Extraction: When is it Necessary & Healing Tips",
            "title_ne": "अक्कल दाँत (Wisdom Tooth) निकाल्ने कहिले आवश्यक हुन्छ र निको पार्ने सुझावहरू",
            "video_url": "https://www.youtube.com/watch?v=pD4U6k_8wZo",
            "category": cat_walk,
            "related_service": service_rct,
            "short_description": "Learn the signs of impacted wisdom teeth, painless extraction protocols, and rapid recovery guidelines.",
            "short_description_ne": "फसेको अक्कल दाँतका लक्षणहरू, दुखाइरहित निकाल्ने तरिका र छिटो निको हुने दिशानिर्देशहरू जान्नुहोस्।",
            "is_featured": False,
            "thumbnail_url": "https://img.youtube.com/vi/pD4U6k_8wZo/hqdefault.jpg",
            "order": 8,
        },
        {
            "title": "Professional In-Clinic Teeth Whitening vs Home Kits",
            "video_url": "https://www.youtube.com/watch?v=kYv_8RjC_wE",
            "category": cat_cosmetic,
            "related_service": service_clean,
            "short_description": "Achieve 6 to 8 shades whiter smile safely in a single 45-minute dental laser teeth whitening session.",
            "is_featured": False,
            "thumbnail_url": "https://img.youtube.com/vi/kYv_8RjC_wE/hqdefault.jpg",
            "order": 9,
        }
    ]

    for item in videos_data:
        v, created = Video.objects.update_or_create(
            title=item["title"],
            defaults={
                "video_url": item["video_url"],
                "platform": "youtube",
                "category": item["category"],
                "related_service": item["related_service"],
                "short_description": item["short_description"],
                "is_featured": item["is_featured"],
                "thumbnail_url": item["thumbnail_url"],
                "is_published": True,
                "order": item["order"]
            }
        )
        status = "Created" if created else "Updated"
        print(f"  {status} Video: {v.title}")

    print(f"Successfully seeded {Video.objects.count()} videos into the database!")

if __name__ == "__main__":
    seed_videos()
