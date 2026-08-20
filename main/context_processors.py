from django.utils import timezone
from django.utils.text import slugify
from .models import SpecialOffer, PricingItem, SiteSettings

def active_offer(request):
    """
    Returns the currently active special offer (if any) to all templates.
    """
    now = timezone.now()
    offer = SpecialOffer.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).order_by('-start_date').first()
    
    return {
        'active_offer': offer
    }

def dynamic_pricing(request):
    """
    Returns pricing items as a dictionary for templates.
    """
    prices = {}
    lang = getattr(request, 'LANGUAGE_CODE', 'en')
    for item in PricingItem.objects.all():
        key = slugify(item.name).replace("-", "_")
        price = item.price
        if lang == 'ne' and getattr(item, 'price_ne', None):
            price = item.price_ne
        prices[key] = price
    return {
        'dynamic_prices': prices
    }

def site_settings(request):
    """
    Returns the SiteSettings object to all templates so footer/navbar can
    display real contact details, social links and working hours.
    """
    settings_obj = SiteSettings.objects.first()
    return {
        'site_settings': settings_obj
    }


def google_reviews_context(request):
    """
    Returns cached Google Business data, Google reviews, and Patient Stories to all templates.
    """
    import os
    from django.core.cache import cache
    from .models import GoogleBusiness, GoogleReview, Testimonial

    cached_data = cache.get('google_reviews_context_data')
    if cached_data is None:
        business = GoogleBusiness.objects.order_by('-last_synced', '-updated_at').first()
        reviews = []
        if business:
            reviews = list(GoogleReview.objects.filter(business=business, is_active=True).order_by('-publish_time', '-created_at')[:10])
        
        patient_stories = list(Testimonial.objects.filter(is_active=True).order_by('order', '-id')[:10])
        cached_data = {
            'google_business': business,
            'google_reviews': reviews,
            'patient_stories': patient_stories,
        }
        try:
            cache_ttl = int(os.getenv('GOOGLE_REVIEWS_CACHE_TTL', 21600))
        except (ValueError, TypeError):
            cache_ttl = 21600
        cache.set('google_reviews_context_data', cached_data, cache_ttl)

    return cached_data



