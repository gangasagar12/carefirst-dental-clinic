import json
import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from appointments.models import Appointment, AppointmentFunnelEvent
from main.models import Service, Doctor


class SmartAppointmentFunnelTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.service = Service.objects.create(
            slug='root-canal-treatment',
            title='Root Canal Treatment',
            starting_price='5000',
            is_active=True,
            order=1
        )
        self.doctor = Doctor.objects.create(
            name='Subash Banjade',
            designation='Lead Dental Surgeon',
            nmc_number='31229',
            is_active=True
        )

    def test_appointment_number_generation(self):
        """Test human-readable unique request ID e.g. CF-2026-000001"""
        apt = Appointment.objects.create(
            full_name="Ram Sharma",
            phone="9841234567",
            preferred_date=timezone.now().date() + datetime.timedelta(days=2),
            status="new"
        )
        self.assertTrue(apt.appointment_number.startswith("CF-"))
        self.assertIn(str(timezone.now().year), apt.appointment_number)

    def test_funnel_view_loads_with_context(self):
        """Test GET /appointment/?treatment=root-canal-treatment"""
        response = self.client.get(reverse('appointments:book'), {'treatment': 'root-canal-treatment'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Root Canal Treatment')
        self.assertEqual(response.context['preselected_service'], self.service)

    def test_submit_appointment_ajax_success(self):
        """Test valid AJAX submission creating Appointment and attribution"""
        tomorrow = (timezone.now().date() + datetime.timedelta(days=1)).isoformat()
        payload = {
            'full_name': 'Sita Koirala',
            'phone': '9801234567',
            'email': 'sita@example.com',
            'treatment': 'root-canal-treatment',
            'appointment_type': 'consultation',
            'preferred_date': tomorrow,
            'preferred_time': 'morning',
            'doctor_id': self.doctor.id,
            'message': 'Experiencing mild sensitivity',
            'utm_source': 'instagram',
            'utm_campaign': 'rct_special',
            'chat_used': False,
            'session_id': 'test-session-123'
        }

        response = self.client.post(
            reverse('appointments:submit_ajax'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['appointment_number'].startswith("CF-"))

        # Verify DB record
        apt = Appointment.objects.get(phone='9801234567')
        self.assertEqual(apt.full_name, 'Sita Koirala')
        self.assertEqual(apt.service, self.service)
        self.assertEqual(apt.doctor, self.doctor)
        self.assertEqual(apt.utm_source, 'instagram')
        self.assertEqual(apt.status, 'new')

        # Verify funnel event was created
        event = AppointmentFunnelEvent.objects.filter(session_id='test-session-123', event_type='SUBMITTED').first()
        self.assertIsNotNone(event)

    def test_submit_appointment_validation_errors(self):
        """Test rejection of invalid phone numbers and past dates"""
        # 1. Invalid short phone
        payload = {
            'full_name': 'Hari Test',
            'phone': '123',
            'preferred_date': (timezone.now().date() + datetime.timedelta(days=1)).isoformat()
        }
        res = self.client.post(reverse('appointments:submit_ajax'), data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json()['success'])

        # 2. Past date rejection
        yesterday = (timezone.now().date() - datetime.timedelta(days=1)).isoformat()
        payload2 = {
            'full_name': 'Hari Test',
            'phone': '9841234567',
            'preferred_date': yesterday
        }
        res2 = self.client.post(reverse('appointments:submit_ajax'), data=json.dumps(payload2), content_type='application/json')
        self.assertEqual(res2.status_code, 400)
        self.assertIn('past', res2.json()['error'].lower())

    def test_duplicate_submission_prevention(self):
        """Test that submitting identical request within 30 seconds returns existing record without duplicate row"""
        tomorrow = (timezone.now().date() + datetime.timedelta(days=1)).isoformat()
        payload = {
            'full_name': 'Duplicate Tester',
            'phone': '9851122334',
            'preferred_date': tomorrow,
            'treatment': 'root-canal-treatment'
        }

        # First submit
        res1 = self.client.post(reverse('appointments:submit_ajax'), data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res1.status_code, 200)
        apt_num1 = res1.json()['appointment_number']

        # Second instant submit with same phone and date
        res2 = self.client.post(reverse('appointments:submit_ajax'), data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res2.status_code, 200)
        apt_num2 = res2.json()['appointment_number']

        self.assertEqual(apt_num1, apt_num2)
        # Ensure only 1 record created in database
        self.assertEqual(Appointment.objects.filter(phone='9851122334').count(), 1)

    def test_track_funnel_event_api(self):
        """Test logging step transitions for conversion analytics"""
        payload = {
            'session_id': 'sess-analytics-99',
            'event_type': 'DATE_SELECTED',
            'treatment_slug': 'root-canal-treatment',
            'source': 'google'
        }
        res = self.client.post(reverse('appointments:track_event'), data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['success'])
        self.assertTrue(AppointmentFunnelEvent.objects.filter(session_id='sess-analytics-99', event_type='DATE_SELECTED').exists())

    def test_confirmation_view(self):
        """Test receipt confirmation page /appointment/confirmation/<appointment_number>/"""
        apt = Appointment.objects.create(
            full_name="Bikash Thapa",
            phone="9861234567",
            preferred_date=timezone.now().date() + datetime.timedelta(days=3),
            service=self.service
        )
        response = self.client.get(reverse('appointments:confirmation', kwargs={'appointment_number': apt.appointment_number}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, apt.appointment_number)
        self.assertContains(response, 'Bikash Thapa')
        self.assertContains(response, 'Root Canal Treatment')
