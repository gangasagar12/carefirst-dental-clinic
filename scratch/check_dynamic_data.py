import os, sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding='utf-8')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from blogs.models import Post, Category
from media_center.models import Video
from main.models import Doctor, SpecialOffer, Service

print("=== BLOG POSTS ===")
for p in Post.objects.all():
    print(f"ID {p.id}: {p.title[:50]}")
    print(f"  title_en: {getattr(p, 'title_en', None)}")
    print(f"  title_ne: {getattr(p, 'title_ne', None)}")
    print(f"  excerpt_ne: {bool(getattr(p, 'excerpt_ne', None))}")
    print(f"  content_ne: {bool(getattr(p, 'content_ne', None))}")

print("\n=== SPECIAL OFFERS ===")
for o in SpecialOffer.objects.all():
    print(f"ID {o.id}: {o.title}")
    print(f"  title_ne: {getattr(o, 'title_ne', None)}")
    print(f"  desc_ne: {getattr(o, 'description_ne', None)}")

print("\n=== VIDEOS ===")
for v in Video.objects.all()[:3]:
    print(f"ID {v.id}: {v.title[:40]}")
    print(f"  title_ne: {getattr(v, 'title_ne', None)}")
