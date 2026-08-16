from typing import Dict, Any
from main.models import SiteSettings, Doctor

def get_clinic_information() -> Dict[str, Any]:
    """
    Returns single verified Kathmandu clinic location, hours, contact numbers, and director details.
    """
    settings = SiteSettings.objects.first()
    director = Doctor.objects.filter(is_active=True).first()

    return {
        'clinic_name': "CareFirst Dental Clinic",
        'location': "Pragatinagar Road, Shankhamul-31, Kathmandu 44600 (Near Shankhamul / New Baneshwor Junction)",
        'city': "Kathmandu, Nepal",
        'primary_phone': settings.primary_phone if settings else "+977 980-7464136",
        'secondary_phone': settings.secondary_phone if settings else "01-5916886",
        'whatsapp_number': "+977 980-7464136",
        'whatsapp_link': "https://wa.me/9779807464136",
        'email': settings.email if settings else "carefirstdentalclinic@gmail.com",
        'opening_hours': "Monday to Sunday (Open 7 Days): 7:30 AM to 7:30 PM",
        'clinical_director': f"Dr. {director.name} ({director.qualifications}, NMC #{director.nmc_number})" if director else "Dr. Subash Banjade (BDS, Senior Dental Surgeon, NMC #31229)",
        'amenities': [
            "Class-B Autoclave 100% Hospital-Grade Sterilization",
            "Digital Low-Radiation RVG X-Rays",
            "Painless Rotary Endodontics",
            "Comfortable, modern patient operatory",
            "Convenient parking and central Kathmandu access"
        ]
    }
