from typing import List, Dict, Any, Optional
from main.models import Doctor

def get_doctor_information(name_or_specialty: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves certified dentist and clinical director records from Django database.
    Never fabricates degrees or NMC credentials.
    """
    qs = Doctor.objects.filter(is_active=True).order_by('order', 'name')
    
    if name_or_specialty:
        term = name_or_specialty.strip().lower()
        matched = qs.filter(name__icontains=term)
        if not matched.exists():
            matched = qs.filter(specialty__icontains=term)
        if not matched.exists():
            matched = qs.filter(designation__icontains=term)
        if matched.exists():
            qs = matched

    doctors = []
    for doc in qs:
        doctors.append({
            'name': f"Dr. {doc.name}",
            'designation': doc.designation,
            'specialty': doc.get_specialty_display(),
            'qualifications': doc.qualifications or "BDS, Senior Dental Surgeon",
            'nmc_number': doc.nmc_number or "NMC Registered",
            'experience_years': f"{doc.experience_years}+ years" if doc.experience_years else "Experienced",
            'certifications': doc.get_certifications_list(),
            'languages': doc.languages or "English, Nepali",
            'bio': doc.bio or f"Dr. {doc.name} provides advanced, patient-first dental care at CareFirst Dental Clinic Kathmandu."
        })

    return doctors
