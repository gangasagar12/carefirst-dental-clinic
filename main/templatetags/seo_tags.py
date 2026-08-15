from django import template
from main.models import SEOFAQCategory, SEOFAQ

register = template.Library()

@register.inclusion_tag('components/seo_faqs.html')
def render_seo_faqs(category_slug):
    try:
        category = SEOFAQCategory.objects.get(slug=category_slug)
        faqs = SEOFAQ.objects.filter(category=category, is_active=True).order_by('order')
    except SEOFAQCategory.DoesNotExist:
        faqs = []

    return {'faqs': faqs}
