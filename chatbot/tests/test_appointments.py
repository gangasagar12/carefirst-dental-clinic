from django.test import TestCase
from appointments.models import Appointment
from chatbot.tools.appointment_tools import validate_and_create_appointment

class AppointmentToolsTest(TestCase):
    def test_create_appointment_success(self):
        payload = {
            'full_name': 'Ram Sharma',
            'phone': '9841234567',
            'email': 'ram@example.com',
            'treatment': 'Dental Filling',
            'preferred_date': '2026-08-25',
            'preferred_time': 'morning',
            'message': 'Need filling for lower molar'
        }
        result = validate_and_create_appointment(payload)
        self.assertTrue(result['success'])
        self.assertEqual(result['full_name'], 'Ram Sharma')

        # Check DB record
        apt = Appointment.objects.get(id=result['appointment_id'])
        self.assertEqual(apt.phone, '9841234567')
        self.assertEqual(apt.status, 'pending')
        self.assertIn('[Booked via Ask CareFirst AI Assistant]', apt.message)

    def test_create_appointment_missing_phone(self):
        payload = {
            'full_name': 'Ram Sharma',
            'phone': '',
            'treatment': 'Dental Filling'
        }
        result = validate_and_create_appointment(payload)
        self.assertFalse(result['success'])
        self.assertIn('phone', result['error'])
