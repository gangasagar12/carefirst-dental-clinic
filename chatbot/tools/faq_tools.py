from typing import List, Dict, Any
from main.models import FAQ, SEOFAQ

def search_faq(query: str) -> List[Dict[str, Any]]:
    """
    Searches both general FAQs and SEO FAQs in the database.
    """
    if not query:
        return []

    q = query.strip().lower()
    results = []

    # 1. Search General FAQs
    faqs = FAQ.objects.filter(is_active=True)
    for f in faqs:
        if q in f.question.lower() or any(w in f.question.lower() for w in q.split() if len(w) > 3):
            results.append({
                'question': f.question,
                'answer': f.answer,
                'source': 'general_faq'
            })

    # 2. Search SEO FAQs
    seo_faqs = SEOFAQ.objects.filter(is_active=True)
    for f in seo_faqs:
        if q in f.question.lower() or q in f.primary_keyword.lower() or any(w in f.question.lower() for w in q.split() if len(w) > 3):
            results.append({
                'question': f.question,
                'answer': f.answer,
                'source': 'seo_faq'
            })

    return results[:3]
