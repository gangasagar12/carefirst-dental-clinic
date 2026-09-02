import json
import datetime
from decimal import Decimal
from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse

from appointments.models import Appointment
from appointments.utils import generate_booking_id, generate_secure_access_token
from appointments.qr_services import generate_qr_base64, generate_qr_png_bytes, get_appointment_verification_url
from appointments.pdf_services import generate_appointment_confirmation_pdf
from appointments.calendar_services import generate_google_calendar_url, generate_icalendar_content
from main.models import Service, Doctor


class AppointmentConfirmationAndManagementTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.service = Service.objects.create(
            title="Root Canal Treatment (RCT)",
            slug="root-canal-treatment",
            is_active=True
        )
        self.doctor = Doctor.objects.create(
            name="Subash Banjade",
            specialty="Dental Surgeon",
            is_active=True
        )
        self.appointment = Appointment.objects.create(
            full_name="Bikash Adhikari",
            phone="9841234567",
            email="bikash@example.com",
            service=self.service,
            doctor=self.doctor,
            preferred_date=timezone.now().date() + datetime.timedelta(days=2),
            preferred_time="morning",
            message="Experiencing severe toothache in lower molar."
        )

    def test_appointment_creation_generates_unique_booking_id_and_token(self):
        """
        Validates that new appointments receive non-predictable booking IDs,
        cryptographically secure access tokens, and start as 'pending'.
        """
        self.assertIsNotNone(self.appointment.booking_id)
        self.assertTrue(self.appointment.booking_id.startswith("CF-APT-"))
        self.assertIsNotNone(self.appointment.access_token)
        self.assertTrue(len(self.appointment.access_token) >= 32)
        self.assertEqual(self.appointment.status, 'pending')
        self.assertEqual(self.appointment.display_booking_id, self.appointment.booking_id)

    def test_appointment_qr_generation(self):
        """
        Validates high-resolution QR PNG bytes and base64 string generation.
        """
        verif_url = get_appointment_verification_url(self.appointment)
        self.assertIn(self.appointment.access_token, verif_url)

        png_bytes = generate_qr_png_bytes(verif_url)
        self.assertGreater(len(png_bytes), 500)
        self.assertTrue(png_bytes.startswith(b'\x89PNG'))

        b64 = generate_qr_base64(verif_url)
        self.assertTrue(b64.startswith("data:image/png;base64,"))

    def test_appointment_pdf_generation(self):
        """
        Validates ReportLab PDF generation creates a valid %PDF stream with booking details.
        """
        pdf_bytes = generate_appointment_confirmation_pdf(self.appointment)
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_appointment_calendar_integrations(self):
        """
        Validates Google Calendar URL and iCalendar (.ics) exports.
        """
        gcal_url = generate_google_calendar_url(self.appointment)
        self.assertIn("calendar.google.com", gcal_url)
        self.assertIn(self.appointment.booking_id, gcal_url)

        ics_str = generate_icalendar_content(self.appointment)
        self.assertIn("BEGIN:VCALENDAR", ics_str)
        self.assertIn("BEGIN:VEVENT", ics_str)
        self.assertIn(self.appointment.booking_id, ics_str)
        self.assertIn("END:VCALENDAR", ics_str)

    def test_appointment_confirmation_view(self):
        """
        Validates dedicated confirmation page renders with 200 OK and shows Booking ID.
        """
        url = reverse('appointments:confirmation', kwargs={'access_token': self.appointment.access_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.appointment.booking_id)
        self.assertContains(response, "Pending Confirmation")
        self.assertContains(response, "Bikash Adhikari")
        self.assertContains(response, "Root Canal Treatment (RCT)")

    def test_appointment_manage_view(self):
        """
        Validates secure patient management portal renders correctly.
        """
        url = reverse('appointments:manage', kwargs={'access_token': self.appointment.access_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.appointment.booking_id)
        self.assertContains(response, "Reception Verification Pass")

    def test_appointment_pdf_download_endpoint(self):
        """
        Validates PDF download streaming endpoint.
        """
        url = reverse('appointments:download_pdf', kwargs={'access_token': self.appointment.access_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment;', response['Content-Disposition'])

    def test_appointment_calendar_ics_endpoint(self):
        """
        Validates iCal streaming endpoint.
        """
        url = reverse('appointments:calendar_ics', kwargs={'access_token': self.appointment.access_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/calendar; charset=utf-8')
        self.assertIn('attachment;', response['Content-Disposition'])

    def test_patient_reschedule_request(self):
        """
        Validates patient self-service reschedule submission.
        """
        new_date = timezone.now().date() + datetime.timedelta(days=5)
        url = reverse('appointments:request_reschedule', kwargs={'access_token': self.appointment.access_token})
        response = self.client.post(url, {
            'preferred_date': new_date.isoformat(),
            'preferred_time': 'afternoon',
            'reschedule_reason': 'Urgent business meeting conflict.'
        })
        self.assertEqual(response.status_code, 302)

        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.preferred_date, new_date)
        self.assertEqual(self.appointment.preferred_time, 'afternoon')
        self.assertEqual(self.appointment.status, 'rescheduled')
        self.assertEqual(self.appointment.reschedule_reason, 'Urgent business meeting conflict.')

    def test_patient_cancel_request(self):
        """
        Validates patient self-service cancellation.
        """
        url = reverse('appointments:request_cancel', kwargs={'access_token': self.appointment.access_token})
        response = self.client.post(url, {
            'cancel_reason': 'Treatment completed during emergency hospital visit.'
        })
        self.assertEqual(response.status_code, 302)

        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'cancelled')
        self.assertIn('Treatment completed', self.appointment.internal_note)

    def test_ajax_appointment_booking_submission(self):
        """
        Validates JSON submission via the frontend booking funnel.
        """
        target_date = (timezone.now().date() + datetime.timedelta(days=3)).isoformat()
        payload = {
            'full_name': 'Suman Thapa',
            'phone': '9801234888',
            'email': 'suman@example.com',
            'treatment': self.service.slug,
            'appointment_type': 'treatment',
            'preferred_date': target_date,
            'preferred_time': 'evening',
            'message': 'Need wisdom tooth consultation.'
        }
        url = reverse('appointments:submit_ajax')
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['booking_id'].startswith('CF-APT-'))
        self.assertIsNotNone(data['access_token'])
        self.assertIn(data['access_token'], data['redirect_url'])
