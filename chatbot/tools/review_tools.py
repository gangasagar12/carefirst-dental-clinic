from typing import List, Dict, Any, Optional
from main.models import Testimonial, GoogleReview

def get_treatment_reviews(treatment_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves approved patient testimonials and Google reviews.
    Never fabricates reviews.
    """
    reviews = []

    # 1. Testimonials
    test_qs = Testimonial.objects.filter(is_active=True)
    if treatment_name:
        matched = test_qs.filter(treatment__icontains=treatment_name.strip())
        if matched.exists():
            test_qs = matched

    for t in test_qs[:3]:
        reviews.append({
            'author': t.patient_name,
            'rating': f"{t.rating}★",
            'treatment': t.treatment or "Dental Care",
            'text': t.review,
            'source': 'Verified Patient Testimonial'
        })

    # 2. Google Reviews if available
    google_qs = GoogleReview.objects.filter(is_active=True).order_by('-rating', '-publish_time')
    for g in google_qs[:2]:
        reviews.append({
            'author': g.author_name,
            'rating': f"{g.rating}★",
            'treatment': "CareFirst Patient Review",
            'text': g.review_text,
            'source': 'Google Verified Review'
        })

    return reviews[:4]
