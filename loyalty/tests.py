from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from main.models import Service
from appointments.models import Appointment
from loyalty.models import (
    LoyaltyProgram,
    PatientLoyaltyProfile,
    LoyaltyReward,
    LoyaltyTransaction,
    LoyaltyNotificationLog,
    LoyaltyVerificationAuditLog,
    normalize_phone
)
from loyalty.services import (
    get_or_create_patient_profile,
    stage_appointment_for_verification,
    verify_and_grant_loyalty_progress,
    reject_loyalty_progress,
    apply_reward_to_bill
)

User = get_user_model()


class HumanVerifiedLoyaltyWorkflowTestCase(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='receptionist_anita',
            password='Password123!',
            is_staff=True
        )
        self.program = LoyaltyProgram.objects.create(
            name="CareFirst Smile Rewards",
            tagline="Your care deserves a little extra.",
            required_completed_treatments=3,
            reward_type='percentage',
            discount_percentage=Decimal('10.00'),
            expiry_days=60,
            require_payment_verification=False,
            allow_all_services_by_default=True,
            is_active=True
        )
        self.service = Service.objects.create(
            title="Root Canal Treatment (RCT)",
            slug="root-canal-treatment",
            is_active=True
        )

    def test_workflow_no_auto_grant_until_human_verification(self):
        """
        Validates that booking, confirming, checking in, and marking completed
        do NOT grant points until authorized human verification.
        """
        # 1. Booking Submitted
        app = Appointment.objects.create(
            full_name="Rajesh Maharjan",
            phone="9841998877",
            preferred_date=timezone.now().date(),
            service=self.service,
            status='new'
        )
        self.assertEqual(app.loyalty_status, 'none')

        # 2. Receptionist Confirms
        app.status = 'confirmed'
        app.confirmed_at = timezone.now()
        app.save()
        self.assertEqual(app.loyalty_status, 'none')

        # 3. Patient Checks In
        app.status = 'checked_in'
        app.checked_in_at = timezone.now()
        app.save()
        self.assertEqual(app.loyalty_status, 'none')

        # 4. Doctor Completes Treatment
        app.status = 'completed'
        app.completed_at = timezone.now()
        stage_appointment_for_verification(app)
        app.refresh_from_db()

        self.assertEqual(app.loyalty_status, 'awaiting_verification')

        # Ensure NO profile progress was granted yet
        norm_phone = normalize_phone("9841998877")
        prof = PatientLoyaltyProfile.objects.filter(normalized_phone=norm_phone).first()
        current_p = prof.current_progress if prof else 0
        self.assertEqual(current_p, 0)
        self.assertEqual(LoyaltyTransaction.objects.filter(appointment=app).count(), 0)

        # 5. Receptionist Reviews & Verifies
        res = verify_and_grant_loyalty_progress(
            appointment=app,
            staff_user=self.staff_user,
            notes="Verified after successful RCT session."
        )

        self.assertTrue(res['success'])
        self.assertEqual(res['previous_progress'], 0)
        self.assertEqual(res['new_progress'], 1)

        app.refresh_from_db()
        self.assertEqual(app.loyalty_status, 'verified')
        self.assertEqual(app.loyalty_verified_by, self.staff_user)

        # Audit Log Verified
        audit = LoyaltyVerificationAuditLog.objects.filter(appointment=app).first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.decision, 'approved')
        self.assertEqual(audit.previous_progress, 0)
        self.assertEqual(audit.new_progress, 1)
        self.assertEqual(audit.verified_by, self.staff_user)

    def test_receptionist_rejection_stores_reason_and_grants_zero_points(self):
        """
        Validates marking visit Not Eligible requires reason and grants 0 points.
        """
        app = Appointment.objects.create(
            full_name="Bina Tamang",
            phone="9801122445",
            preferred_date=timezone.now().date(),
            service=self.service,
            status='completed',
            loyalty_status='awaiting_verification'
        )

        res = reject_loyalty_progress(
            appointment=app,
            reason="Follow-up visit",
            staff_user=self.staff_user,
            notes="Routine postoperative checkup, no new fee charged."
        )

        self.assertTrue(res['success'])
        app.refresh_from_db()
        self.assertEqual(app.loyalty_status, 'not_eligible')
        self.assertEqual(app.loyalty_rejection_reason, "Follow-up visit")
        self.assertEqual(app.loyalty_verified_by, self.staff_user)

        # Ensure no points or rewards
        norm_phone = normalize_phone("9801122445")
        prof = PatientLoyaltyProfile.objects.filter(normalized_phone=norm_phone).first()
        self.assertEqual(prof.current_progress, 0)

        # Ensure audit log created
        audit = LoyaltyVerificationAuditLog.objects.filter(appointment=app).first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.decision, 'rejected')
        self.assertEqual(audit.rejection_reason, "Follow-up visit")

    def test_configurable_payment_validation(self):
        """
        Validates Option B: Treatment completed + Payment completed + Receptionist verified.
        """
        self.program.require_payment_verification = True
        self.program.save()

        app = Appointment.objects.create(
            full_name="Kishor Shrestha",
            phone="9841556677",
            preferred_date=timezone.now().date(),
            service=self.service,
            status='completed',
            payment_status='pending',
            loyalty_status='awaiting_verification'
        )

        # Verification MUST fail when payment is pending
        res_fail = verify_and_grant_loyalty_progress(
            appointment=app,
            staff_user=self.staff_user
        )
        self.assertFalse(res_fail['success'])
        self.assertIn('Payment verification required', res_fail['message'])

        # Update payment to Paid
        app.payment_status = 'paid'
        app.save()

        res_success = verify_and_grant_loyalty_progress(
            appointment=app,
            staff_user=self.staff_user
        )
        self.assertTrue(res_success['success'])
        self.assertEqual(res_success['new_progress'], 1)

    def test_duplicate_verification_prevention(self):
        """
        Validates that verifying the same appointment twice never adds duplicate points.
        """
        app = Appointment.objects.create(
            full_name="Samir Khanal",
            phone="9860112233",
            preferred_date=timezone.now().date(),
            service=self.service,
            status='completed',
            loyalty_status='awaiting_verification'
        )

        res1 = verify_and_grant_loyalty_progress(appointment=app, staff_user=self.staff_user)
        self.assertTrue(res1['success'])
        self.assertEqual(res1['new_progress'], 1)

        # Second attempt
        res2 = verify_and_grant_loyalty_progress(appointment=app, staff_user=self.staff_user)
        self.assertTrue(res2['success'])
        self.assertTrue(res2.get('already_processed'))

        norm_phone = normalize_phone("9860112233")
        prof = PatientLoyaltyProfile.objects.get(normalized_phone=norm_phone)
        self.assertEqual(prof.current_progress, 1)
        self.assertEqual(prof.total_completed_eligible_treatments, 1)
