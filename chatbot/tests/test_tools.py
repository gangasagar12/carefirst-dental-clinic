from django.test import TestCase
from main.models import Service, Doctor, FAQ, SiteSettings
from chatbot.tools.treatment_tools import get_treatment, search_treatments
from chatbot.tools.doctor_tools import get_doctor_information
from chatbot.tools.clinic_tools import get_clinic_information
from chatbot.tools.faq_tools import search_faq

class BusinessToolsTest(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            title="Root Canal Treatment",
            slug="root-canal-treatment",
            category="endodontics",
            starting_price="6,000",
            features="Single-visit available\nRotary instrumentation\nLow-radiation digital RVG"
        )
        self.doctor = Doctor.objects.create(
            name="Subash Banjade",
            designation="Chief Dental Surgeon",
            specialty="general",
            qualifications="BDS",
            nmc_number="31229",
            is_active=True
        )
        self.faq = FAQ.objects.create(
            question="Does scaling damage tooth enamel?",
            answer="No, ultrasonic scaling uses gentle water vibrations to remove tartar without harming enamel.",
            is_active=True
        )

    def test_get_treatment(self):
        info = get_treatment("root-canal-treatment")
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], "Root Canal Treatment")
        self.assertIn("NPR 6,000", info['starting_price'])

    def test_search_treatments_keyword(self):
        results = search_treatments("bleeding gums and tartar")
        self.assertGreater(len(results), 0)

    def test_get_doctor_information(self):
        doctors = get_doctor_information("Subash")
        self.assertEqual(len(doctors), 1)
        self.assertEqual(doctors[0]['nmc_number'], "31229")

    def test_get_clinic_information(self):
        clinic = get_clinic_information()
        self.assertEqual(clinic['clinic_name'], "CareFirst Dental Clinic")
        self.assertIn("Shankhamul", clinic['location'])
        self.assertIn("7:30 AM", clinic['opening_hours'])

    def test_search_faq(self):
        faqs = search_faq("scaling enamel")
        self.assertEqual(len(faqs), 1)
        self.assertIn("No, ultrasonic scaling", faqs[0]['answer'])
