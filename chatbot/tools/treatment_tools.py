from typing import Dict, Any, List, Optional
from django.urls import reverse
from main.models import Service

def get_treatment(treatment_identifier: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves full verified clinical & service details for a specific treatment from Django database.
    Matches by slug or case-insensitive title.
    """
    if not treatment_identifier:
        return None

    service = Service.objects.filter(slug__iexact=treatment_identifier.strip(), is_active=True).first()
    if not service:
        service = Service.objects.filter(title__icontains=treatment_identifier.strip(), is_active=True).first()

    if not service:
        return None

    detail_url = reverse('main:service_detail', kwargs={'slug': service.slug})

    return {
        'name': service.title,
        'slug': service.slug,
        'category': service.get_category_display(),
        'starting_price': f"NPR {service.get_dynamic_price()}",
        'features': service.get_features_list(),
        'detail_content': service.detail_content or f"{service.title} at CareFirst Dental Clinic Kathmandu.",
        'url': detail_url,
        'is_popular': service.is_popular,
    }


def search_treatments(query: str) -> List[Dict[str, Any]]:
    """
    Searches treatments by keyword or patient concerns (e.g. 'bleeding gums', 'yellow teeth', 'crooked').
    """
    if not query:
        return []

    q = query.lower().strip()
    
    # Concern keywords mapping to services
    concern_map = {
        'yellow': ['scaling-and-polishing', 'teeth-whitening', 'cosmetic-dentistry'],
        'stain': ['scaling-and-polishing', 'teeth-whitening'],
        'bleed': ['periodontal-treatment-gum', 'scaling-and-polishing'],
        'gum': ['periodontal-treatment-gum', 'scaling-and-polishing'],
        'pain': ['root-canal-treatment', 'dental-filling', 'tooth-extraction'],
        'ache': ['root-canal-treatment', 'dental-filling'],
        'cavity': ['dental-filling', 'root-canal-treatment'],
        'hole': ['dental-filling', 'root-canal-treatment'],
        'decay': ['dental-filling', 'root-canal-treatment'],
        'crooked': ['orthodontic-treatment-braces'],
        'align': ['orthodontic-treatment-braces'],
        'brace': ['orthodontic-treatment-braces'],
        'gap': ['orthodontic-treatment-braces', 'crowns-and-bridges', 'dental-implants'],
        'missing': ['dental-implants', 'crowns-and-bridges', 'dentures'],
        'broken': ['crowns-and-bridges', 'dental-filling', 'root-canal-treatment'],
        'wisdom': ['tooth-extraction'],
        'xray': ['digital-dental-x-ray'],
        'x-ray': ['digital-dental-x-ray'],
        'clean': ['scaling-and-polishing'],
        'polish': ['scaling-and-polishing'],
    }

    matched_slugs = set()
    for kw, slugs in concern_map.items():
        if kw in q:
            matched_slugs.update(slugs)

    services_qs = Service.objects.filter(is_active=True)
    results = []

    # Priority 1: Direct text match on title or features
    for s in services_qs:
        if s.title.lower() in q or q in s.title.lower() or any(q in f.lower() for f in s.get_features_list()):
            matched_slugs.add(s.slug)

    for slug in matched_slugs:
        s = services_qs.filter(slug=slug).first()
        if s:
            results.append({
                'name': s.title,
                'slug': s.slug,
                'category': s.get_category_display(),
                'starting_price': f"NPR {s.get_dynamic_price()}",
                'url': reverse('main:service_detail', kwargs={'slug': s.slug})
            })

    # If still empty, return top 3 popular services
    if not results:
        for s in services_qs[:3]:
            results.append({
                'name': s.title,
                'slug': s.slug,
                'category': s.get_category_display(),
                'starting_price': f"NPR {s.get_dynamic_price()}",
                'url': reverse('main:service_detail', kwargs={'slug': s.slug})
            })

    return results[:4]


def get_related_treatments(treatment_slug: str) -> List[Dict[str, Any]]:
    """
    Returns verified related treatments with direct URLs.
    """
    current = Service.objects.filter(slug=treatment_slug).first()
    if not current:
        return []

    related_qs = Service.objects.filter(is_active=True).exclude(id=current.id)
    # Prefer same category first
    same_cat = list(related_qs.filter(category=current.category)[:2])
    other_cat = list(related_qs.exclude(category=current.category)[:2])

    combined = (same_cat + other_cat)[:3]
    return [
        {
            'name': s.title,
            'slug': s.slug,
            'url': reverse('main:service_detail', kwargs={'slug': s.slug})
        }
        for s in combined
    ]
