import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from blogs.models import Category, Post
from django.utils.text import slugify

print("Clearing existing blog data...")
Post.objects.all().delete()
Category.objects.all().delete()

print("Creating categories...")
categories_data = [
    "General Dentistry",
    "Dental Implants",
    "Root Canal Treatment",
    "Orthodontics",
    "Gum Treatment",
    "Oral Hygiene",
]

cats = {}
for name in categories_data:
    cat = Category.objects.create(name=name, slug=slugify(name))
    cats[name] = cat

print("Creating posts...")
posts_data = [
    {
        "title": "The Ultimate Guide to Dental Implants in 2026",
        "category": cats["Dental Implants"],
        "excerpt": "Everything you need to know about replacing missing teeth with durable, natural-looking dental implants.",
        "content": "Full content goes here...",
        "is_featured": True,
        "is_popular": True,
        "reading_time": "8 min read"
    },
    {
        "title": "5 Signs You Might Need a Root Canal",
        "category": cats["Root Canal Treatment"],
        "excerpt": "Don't ignore tooth pain. Learn the top five warning signs that indicate you might need endodontic therapy to save your tooth.",
        "content": "Full content goes here...",
        "is_featured": False,
        "is_popular": True,
        "reading_time": "5 min read"
    },
    {
        "title": "Invisalign vs. Traditional Braces: Which is Right for You?",
        "category": cats["Orthodontics"],
        "excerpt": "Compare the pros and cons of clear aligners and traditional metal braces to find the best orthodontic solution for your smile.",
        "content": "Full content goes here...",
        "is_featured": False,
        "is_popular": True,
        "reading_time": "6 min read"
    },
    {
        "title": "How to Prevent Gum Disease Before It Starts",
        "category": cats["Gum Treatment"],
        "excerpt": "Periodontal disease is common but preventable. Discover the best daily habits to keep your gums healthy and strong.",
        "content": "Full content goes here...",
        "is_featured": False,
        "is_popular": False,
        "reading_time": "4 min read"
    },
    {
        "title": "Why Professional Scaling is Essential Twice a Year",
        "category": cats["Oral Hygiene"],
        "excerpt": "Brushing at home isn't enough to remove hardened tartar. Find out why a professional dental cleaning is crucial for your oral health.",
        "content": "Full content goes here...",
        "is_featured": False,
        "is_popular": False,
        "reading_time": "3 min read"
    },
    {
        "title": "What to Expect During Your First Visit to Carefirst Dental Clinic",
        "category": cats["General Dentistry"],
        "excerpt": "Nervous about your upcoming dental appointment? Here is a step-by-step breakdown of what happens during your first comprehensive exam.",
        "content": "Full content goes here...",
        "is_featured": False,
        "is_popular": True,
        "reading_time": "5 min read"
    }
]

for p in posts_data:
    Post.objects.create(
        title=p['title'],
        category=p['category'],
        excerpt=p['excerpt'],
        content=p['content'],
        is_featured=p['is_featured'],
        is_popular=p['is_popular'],
        reading_time=p['reading_time'],
        author="Dr. Niko"
    )

print("Mock data populated successfully!")
