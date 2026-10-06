import os, sys
from pathlib import Path
sys.path.insert(0, str(Path('.')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from blogs.models import Post, Category

cat = Category.objects.first()
p = Post(
    title='Testing Dynamic Translation in Real Time',
    title_en='Testing Dynamic Translation in Real Time',
    title_ne='',
    excerpt='This is a dynamic test to verify real-time translation.',
    excerpt_en='This is a dynamic test to verify real-time translation.',
    excerpt_ne='',
    content='<p>Root canal therapy is painless and quick.</p>',
    content_en='<p>Root canal therapy is painless and quick.</p>',
    content_ne='',
    category=cat,
    author='Dr. Subash Banjade'
)
print("Before save:")
print(" title_ne:", repr(p.title_ne))
print(" excerpt_ne:", repr(p.excerpt_ne))
print(" content_ne:", repr(p.content_ne))

p.save()

print("\nAfter save (instance in memory):")
print(" title_ne:", repr(p.title_ne))
print(" excerpt_ne:", repr(p.excerpt_ne))
print(" content_ne:", repr(p.content_ne))

p_db = Post.objects.get(id=p.id)
print("\nFrom Database:")
print(" title_ne:", repr(p_db.title_ne))
print(" excerpt_ne:", repr(p_db.excerpt_ne))
print(" content_ne:", repr(p_db.content_ne))

p.delete()
