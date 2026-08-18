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
    cat_edu, _ = VideoCategory.objects.get_or_create(name="Patient Education & Guides", defaults={"order": 1})
    cat_walk, _ = VideoCategory.objects.get_or_create(name="Treatment Walkthroughs", defaults={"order": 2})
    cat_cosmetic, _ = VideoCategory.objects.get_or_create(name="Cosmetic & Smile Makeovers", defaults={"order": 3})
    cat_implant, _ = VideoCategory.objects.get_or_create(name="Dental Implants & Surgery", defaults={"order": 4})

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
            "video_url": "https://www.youtube.com/watch?v=jHLp_m24sW4",
            "category": cat_walk,
            "related_service": service_rct,
            "short_description": "A gentle 3D step-by-step walkthrough of microscopic painless root canal therapy at CareFirst Dental Clinic.",
            "is_featured": True,
            "thumbnail_url": "https://img.youtube.com/vi/jHLp_m24sW4/hqdefault.jpg",
            "order": 1,
        },
        {
            "title": "Dental Implants Explained: Single Tooth to Full Mouth",
            "video_url": "https://www.youtube.com/watch?v=kYv_8RjC_wE",
            "category": cat_implant,
            "related_service": service_implant,
            "short_description": "Learn how modern 3D titanium dental implants provide a permanent, natural-looking replacement for missing teeth.",
            "is_featured": True,
            "thumbnail_url": "https://img.youtube.com/vi/kYv_8RjC_wE/hqdefault.jpg",
            "order": 2,
        },
        {
            "title": "Clear Aligners vs Traditional Braces: Which is Right for You?",
            "video_url": "https://www.youtube.com/watch?v=fDoxd_W3w90",
            "category": cat_cosmetic,
            "related_service": service_ortho,
            "short_description": "Compare invisible clear aligners and modern metal/ceramic braces for straightening crooked teeth and bite alignment.",
            "is_featured": True,
            "thumbnail_url": "https://img.youtube.com/vi/fDoxd_W3w90/hqdefault.jpg",
            "order": 3,
        },
        {
            "title": "Why Scaling and Teeth Cleaning Does Not Weaken Your Enamel",
            "video_url": "https://www.youtube.com/watch?v=4R4U0r5C8wA",
            "category": cat_edu,
            "related_service": service_clean,
            "short_description": "Debunking common myths about ultrasonic dental scaling and why routine cleaning prevents gum disease and bad breath.",
            "is_featured": True,
            "thumbnail_url": "https://img.youtube.com/vi/4R4U0r5C8wA/hqdefault.jpg",
            "order": 4,
        },
        {
            "title": "Composite Dental Fillings: Tooth-Colored Natural Restoration",
            "video_url": "https://www.youtube.com/watch?v=S8pB4k_8Zto",
            "category": cat_walk,
            "related_service": service_fill,
            "short_description": "See how tooth-colored composite resin fillings seamlessly repair dental cavities while blending with your natural enamel.",
            "is_featured": False,
            "thumbnail_url": "https://img.youtube.com/vi/S8pB4k_8Zto/hqdefault.jpg",
            "order": 5,
        },
        {
            "title": "Digital Dental X-Rays & OPG: Safe Low-Radiation Diagnostics",
            "video_url": "https://www.youtube.com/watch?v=X6P6k_8w7bY",
            "category": cat_edu,
            "related_service": service_xray,
            "short_description": "How digital sensors and panoramic RVG provide instant high-definition scans with 90% less radiation than film.",
            "is_featured": False,
            "thumbnail_url": "https://img.youtube.com/vi/X6P6k_8w7bY/hqdefault.jpg",
            "order": 6,
        },
        {
            "title": "How to Properly Brush and Floss: Doctor's Daily Oral Care Guide",
            "video_url": "https://www.youtube.com/watch?v=xm9c5HAUBpY",
            "category": cat_edu,
            "related_service": service_clean,
            "short_description": "Essential 2-minute daily brushing techniques and interdental flossing tips recommended by Dr. Subash Banjade.",
            "is_featured": False,
            "thumbnail_url": "https://img.youtube.com/vi/xm9c5HAUBpY/hqdefault.jpg",
            "order": 7,
        },
        {
            "title": "Wisdom Tooth Extraction: When is it Necessary & Healing Tips",
            "video_url": "https://www.youtube.com/watch?v=pD4U6k_8wZo",
            "category": cat_walk,
            "related_service": service_rct,
            "short_description": "Learn the signs of impacted wisdom teeth, painless extraction protocols, and rapid recovery guidelines.",
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
