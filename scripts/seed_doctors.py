import os
import sys
import django

# Add root project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from main.models import Doctor

def seed_doctors():
    print("Seeding CareFirst Doctors & Specialists...")

    doctors_data = [
        {
            "name": "Subash Banjade",
            "designation": "Clinical Director & Dental Surgeon",
            "specialty": "general",
            "qualifications": "BDS (Bachelor of Dental Surgery)",
            "nmc_number": "31229",
            "experience_years": 6,
            "bio": "Dr. Subash Banjade is the Clinical Director at CareFirst Dental Clinic. Dedicated to ethical, patient-centric oral healthcare, he specializes in painless microscopic root canal therapy, aesthetic restorations, and comprehensive dental surgery with hospital-grade sterilization protocols.",
            "certifications": "Certified in Advanced Rotary Endodontics\nCertified in Aesthetic Restorative Dentistry\nMember of Nepal Dental Association (NDA)",
            "languages": "English, Nepali, Hindi",
            "order": 1,
            "is_active": True,
        },
        {
            "name": "Aarati Sharma",
            "designation": "Senior Orthodontic Consultant",
            "specialty": "orthodontics",
            "qualifications": "BDS, MDS (Orthodontics & Dentofacial Orthopedics)",
            "nmc_number": "24185",
            "experience_years": 8,
            "bio": "Dr. Aarati Sharma specializes in correcting crooked teeth, severe bite misalignments, and invisible smile transformations utilizing modern self-ligating ceramic braces and digital clear aligner systems.",
            "certifications": "Certified Clear Aligner Provider\nFellow of World Federation of Orthodontists (WFO)\nSpecialist in Adult & Teen Orthodontics",
            "languages": "English, Nepali",
            "order": 2,
            "is_active": True,
        },
        {
            "name": "Pratik Adhikari",
            "designation": "Periodontist & Implant Surgeon",
            "specialty": "implants",
            "qualifications": "BDS, MDS (Periodontology & Oral Implantology)",
            "nmc_number": "21950",
            "experience_years": 7,
            "bio": "Dr. Pratik Adhikari is an experienced periodontist and implantologist specializing in computer-guided titanium dental implants, sinus lift bone grafting, and advanced laser periodontal therapies.",
            "certifications": "International Congress of Oral Implantologists (ICOI)\nCertified in Guided Bone Regeneration\nExpert in Laser Periodontal Therapy",
            "languages": "English, Nepali, Hindi",
            "order": 3,
            "is_active": True,
        },
        {
            "name": "Sneha Shrestha",
            "designation": "Pediatric & Preventive Dental Surgeon",
            "specialty": "pediatric",
            "qualifications": "BDS (Dental Surgeon)",
            "nmc_number": "34812",
            "experience_years": 4,
            "bio": "Dr. Sneha Shrestha creates a fun, anxiety-free dental experience for children and teenagers. She focuses on pediatric preventive care, pit & fissure sealants, gentle fillings, and fluoride enamel therapies.",
            "certifications": "Child-Friendly Behavioral Dentistry Certification\nPreventive Pediatric Oral Health Specialist\nMember of Nepal Dental Association",
            "languages": "English, Nepali, Newari",
            "order": 4,
            "is_active": True,
        }
    ]

    for d in doctors_data:
        doc, created = Doctor.objects.update_or_create(
            name=d["name"],
            defaults={
                "designation": d["designation"],
                "specialty": d["specialty"],
                "qualifications": d["qualifications"],
                "nmc_number": d["nmc_number"],
                "experience_years": d["experience_years"],
                "bio": d["bio"],
                "certifications": d["certifications"],
                "languages": d["languages"],
                "order": d["order"],
                "is_active": d["is_active"],
            }
        )
        status = "Created" if created else "Updated"
        print(f"  {status} Doctor: Dr. {doc.name} ({doc.designation})")

    print(f"Successfully seeded {Doctor.objects.count()} doctor profiles into the database!")

if __name__ == "__main__":
    seed_doctors()
