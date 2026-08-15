from django.db import models
from django.utils import timezone
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    featured_image = models.ImageField(upload_to='blogs/', blank=True, null=True)
    excerpt = models.TextField(max_length=500, help_text="A short summary of the post")
    content = models.TextField()
    author = models.CharField(max_length=100, default="Carefirst Dental Clinic Team")
    
    published_date = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    reading_time = models.CharField(max_length=50, default="5 min read")
    
    is_featured = models.BooleanField(default=False, help_text="Show this as the main featured article")
    is_popular = models.BooleanField(default=False, help_text="Show this in the Popular Articles section")
    is_published = models.BooleanField(default=True)
    
    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True, help_text="SEO Title (defaults to title if blank)")
    meta_description = models.TextField(blank=True, help_text="SEO Meta Description (defaults to excerpt if blank)")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_date']
