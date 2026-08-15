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
