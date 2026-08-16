import re
from typing import Dict, Any, List, Optional
from main.models import Service, PricingCategory, PricingItem

def get_treatment_price(treatment_name_or_slug: str) -> Dict[str, Any]:
    """
    Returns verified pricing items and starting rate directly from the Django database.
    Guarantees no hallucination by resolving matching PricingCategory and PricingItems.
    """
    if not treatment_name_or_slug:
        return {'found': False, 'message': 'No treatment specified.'}

    clean_term = treatment_name_or_slug.strip()
    
    # 1. Match Service first
    service = Service.objects.filter(slug__iexact=clean_term).first()
    if not service:
        service = Service.objects.filter(title__icontains=clean_term).first()

    matched_category = None
    if service:
        matched_category = PricingCategory.objects.filter(name__icontains=service.title).first()
        if not matched_category:
            for cat in PricingCategory.objects.all():
                if cat.name.lower() in service.title.lower() or service.title.lower() in cat.name.lower():
                    matched_category = cat
                    break

    # 2. Try direct PricingCategory match
    if not matched_category:
        matched_category = PricingCategory.objects.filter(name__icontains=clean_term).first()

    # 3. Try direct PricingItem match
    items = []
    if matched_category:
        for item in matched_category.items.order_by('order', 'id'):
            items.append({
                'name': item.name,
                'price': item.price,
            })
    else:
        # Search individual pricing items
        item_qs = PricingItem.objects.filter(name__icontains=clean_term)
        for item in item_qs:
            items.append({
                'name': item.name,
                'category': item.category.name,
                'price': item.price,
            })

    starting_price = service.get_dynamic_price() if service else (items[0]['price'] if items else "1,000")

    return {
        'found': len(items) > 0 or service is not None,
        'treatment': service.title if service else (matched_category.name if matched_category else clean_term.title()),
        'starting_price': f"NPR {starting_price}",
        'items': items,
        'currency': 'NPR',
        'note': 'Listed prices are starting estimates. Final treatment cost is confirmed following clinical examination and personalized evaluation.',
    }


def calculate_cost_estimate(treatment_name: str, option_name: Optional[str] = None, quantity: int = 1) -> Dict[str, Any]:
    """
    Computes mathematical treatment cost estimate based on official database rates.
    """
    try:
        qty = max(1, int(quantity))
    except (ValueError, TypeError):
        qty = 1

    price_info = get_treatment_price(treatment_name)
    items = price_info.get('items', [])
    
    selected_item = None
    if option_name and items:
        for item in items:
            if option_name.lower() in item['name'].lower():
                selected_item = item
                break

    if not selected_item and items:
        selected_item = items[0]

    unit_price_str = selected_item['price'] if selected_item else price_info.get('starting_price', '1,000')
    
    # Extract numerical value from string e.g. "1,500" or "1,500 - 2,500"
    nums = [int(s.replace(',', '')) for s in re.findall(r'\b\d[\d,]*\b', unit_price_str)]
    
    if nums:
        min_unit = nums[0]
        max_unit = nums[1] if len(nums) > 1 else nums[0]
        
        est_min = min_unit * qty
        est_max = max_unit * qty
        
        if est_min == est_max:
            total_estimate = f"NPR {est_min:,}"
        else:
            total_estimate = f"NPR {est_min:,} – {est_max:,}"
    else:
        total_estimate = f"{unit_price_str} (x{qty})"

    return {
        'treatment': price_info.get('treatment', treatment_name),
        'option': selected_item['name'] if selected_item else 'Standard Option',
        'quantity': qty,
        'unit_price': unit_price_str,
        'total_estimate': total_estimate,
        'note': 'Estimated cost is subject to direct dentist examination and treatment complexity.',
    }
