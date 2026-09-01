from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from main.models import Service
from appointments.models import Appointment
from loyalty.models import (
    LoyaltyProgram,
    PatientLoyaltyProfile,
    LoyaltyReward,
    LoyaltyTransaction,
    LoyaltyNotificationLog,
    normalize_phone
)
from loyalty.services import (
    get_or_create_patient_profile,
    record_treatment_completion,
    apply_reward_to_bill
)


class CareFirstSmileRewardsTestCase(TestCase):
    def setUp(self):
        self.program = LoyaltyProgram.objects.create(
            name="CareFirst Smile Rewards",
            tagline="Your care deserves a little extra.",
            required_completed_treatments=3,
            reward_type='percentage',
            discount_percentage=Decimal('10.00'),
            expiry_days=60,
            allow_all_services_by_default=True,
            is_active=True
        )
        self.service = Service.objects.create(
            title="Root Canal Treatment (RCT)",
            slug="root-canal-treatment",
            is_active=True
        )

    def test_phone_normalization_and_profile_lookup(self):
        phone_raw = "+977 980-7464136"
        norm = normalize_phone(phone_raw)
        self.assertEqual(norm, "9807464136")

        p1 = get_or_create_patient_profile(phone_raw, full_name="Suman Sharma", program=self.program)
        p2 = get_or_create_patient_profile("9807464136", full_name="Suman Sharma", program=self.program)
        self.assertEqual(p1.id, p2.id)
        self.assertEqual(p1.current_progress, 0)

    def test_progress_increment_and_reward_unlock_at_threshold(self):
        phone = "9801234567"
        name = "Aayush Thapa"

        # 1st Visit
        res1 = record_treatment_completion(phone=phone, full_name=name, service=self.service)
        self.assertTrue(res1['success'])
        self.assertEqual(res1['new_progress'], 1)
        self.assertIsNone(res1['reward_unlocked'])

        profile = PatientLoyaltyProfile.objects.get(normalized_phone="9801234567")
        self.assertEqual(profile.current_progress, 1)
        self.assertEqual(profile.total_completed_eligible_treatments, 1)

        # 2nd Visit
        res2 = record_treatment_completion(phone=phone, full_name=name, service=self.service)
        self.assertTrue(res2['success'])
        self.assertEqual(res2['new_progress'], 2)

        # 3rd Visit (Threshold Reached -> Reward Unlocked)
        res3 = record_treatment_completion(phone=phone, full_name=name, service=self.service)
        self.assertTrue(res3['success'])
        self.assertIsNotNone(res3['reward_unlocked'])
        reward = res3['reward_unlocked']

        self.assertEqual(reward.status, 'available')
        self.assertEqual(reward.discount_percentage, Decimal('10.00'))
        self.assertTrue(reward.reward_reference.startswith('CF-RWD-'))

        profile.refresh_from_db()
        self.assertEqual(profile.current_progress, 0)
        self.assertEqual(profile.current_cycle, 2)
        self.assertEqual(profile.total_rewards_earned, 1)
        self.assertEqual(profile.total_completed_eligible_treatments, 3)

    def test_duplicate_prevention_on_same_appointment(self):
        appointment = Appointment.objects.create(
            full_name="Bikash Shrestha",
            phone="9841112233",
            preferred_date=timezone.now().date(),
            service=self.service,
            status='completed'
        )

        res1 = record_treatment_completion(appointment=appointment)
        self.assertTrue(res1['success'])
        self.assertEqual(res1.get('progress_added'), 1)

        # Attempt to process the exact same appointment again
        res2 = record_treatment_completion(appointment=appointment)
        self.assertTrue(res2['success'])
        self.assertTrue(res2.get('already_processed'))

        profile = PatientLoyaltyProfile.objects.get(normalized_phone="9841112233")
        self.assertEqual(profile.current_progress, 1)
        self.assertEqual(profile.total_completed_eligible_treatments, 1)

    def test_reward_redemption_and_double_use_protection(self):
        phone = "9860001122"
        profile = get_or_create_patient_profile(phone, "Kiran Adhikari", program=self.program)

        # Create active reward
        reward = LoyaltyReward.objects.create(
            patient=profile,
            program=self.program,
            discount_percentage=Decimal('10.00'),
            status='available',
            expires_at=timezone.now() + timedelta(days=60)
        )

        # Apply reward to NPR 8,000 bill
        apply_res = apply_reward_to_bill(
            reward_id_or_ref=reward.id,
            patient_phone=phone,
            invoice_ref="CF-INV-2026-0099",
            total_bill_amount=8000
        )
        self.assertTrue(apply_res['success'])
        self.assertEqual(apply_res['discount_amount'], Decimal('800.00'))
        self.assertEqual(apply_res['final_payable'], Decimal('7200.00'))

        reward.refresh_from_db()
        self.assertEqual(reward.status, 'applied')
        self.assertEqual(reward.applied_invoice_ref, "CF-INV-2026-0099")

        # Second redemption attempt MUST fail
        reapply_res = apply_reward_to_bill(
            reward_id_or_ref=reward.id,
            patient_phone=phone,
            invoice_ref="CF-INV-2026-0100",
            total_bill_amount=8000
        )
        self.assertFalse(reapply_res['success'])
        self.assertIn('already been redeemed', reapply_res['error'])
