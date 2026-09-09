from typing import Dict, Any
from main.models import SiteSettings, Doctor

def get_clinic_information() -> Dict[str, Any]:
    """
    Returns verified Kathmandu clinic location, hours, contact numbers, and director details dynamically from the database.
    """
    settings = SiteSettings.objects.first()
    director = Doctor.objects.filter(is_active=True).first()

    primary_phone = settings.primary_phone if settings and settings.primary_phone else "+977 980-7464136"
    secondary_phone = settings.secondary_phone if settings and settings.secondary_phone else "01-5916886"
    whatsapp_number = settings.whatsapp_number if settings and settings.whatsapp_number else "+977 980-7464136"
    clean_whatsapp = whatsapp_number.replace('+', '').replace('-', '').replace(' ', '')
    email = settings.email if settings and settings.email else "carefirstdentalclinic@gmail.com"
    address = settings.address if settings and settings.address else "Pragatinagar Road, Shankhamul-31, Kathmandu 44600"
    landmark = settings.landmark if settings and settings.landmark else "Near Shankhamul / New Baneshwor Junction"
    hours = settings.working_hours_weekdays if settings and settings.working_hours_weekdays else "Monday to Sunday (Open 7 Days): 7:30 AM to 7:30 PM"

    director_str = f"Dr. {director.name} ({director.designation}, {director.qualifications}, NMC #{director.nmc_number})" if director else "Dr. Subash Banjade (Clinical Director & Senior Dental Surgeon, BDS, NMC #31229)"

    return {
        'clinic_name': "CareFirst Dental Clinic",
        'location': f"{address} ({landmark})",
        'city': "Kathmandu, Nepal",
        'primary_phone': primary_phone,
        'secondary_phone': secondary_phone,
        'whatsapp_number': whatsapp_number,
        'whatsapp_link': f"https://wa.me/{clean_whatsapp}",
        'email': email,
        'opening_hours': hours,
        'clinical_director': director_str,
        'amenities': [
            "Class-B Autoclave 100% Hospital-Grade Sterilization",
            "Digital Low-Radiation RVG X-Rays",
            "Painless Rotary Endodontics",
            "Comfortable modern operatory",
            "Convenient parking and central Kathmandu location"
        ]
    }

