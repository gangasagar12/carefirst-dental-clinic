from datetime import timedelta
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import (
    LoyaltyProgram,
    PatientLoyaltyProfile,
    LoyaltyTransaction,
    LoyaltyReward,
    LoyaltyVerificationAuditLog,
    normalize_phone,
    generate_reward_reference
)


def get_or_create_patient_profile(phone, full_name="Valued Patient", email=None, program=None):
    """
    Finds or creates a central Patient Loyalty Profile by phone number.
    Ensures ZERO duplicate profiles for the same phone number.
    """
    if not program:
        program = LoyaltyProgram.get_active_program()

    norm_phone = normalize_phone(phone)
    if not norm_phone:
        raise ValueError("A valid patient phone number is required for the loyalty system.")

    profile, created = PatientLoyaltyProfile.objects.get_or_create(
        normalized_phone=norm_phone,
        program=program,
        defaults={
            'phone': phone.strip(),
            'full_name': full_name.strip() if full_name else "Valued Patient",
            'email': email.strip() if email else None,
            'current_progress': 0,
            'current_cycle': 1,
        }
    )

    if not created:
        updated = False
        if full_name and (profile.full_name == "Valued Patient" or not profile.full_name):
            profile.full_name = full_name.strip()
            updated = True
        if email and not profile.email:
            profile.email = email.strip()
            updated = True
        if updated:
            profile.save(update_fields=['full_name', 'email'])

    return profile


def is_service_eligible(service=None, treatment_str="", program=None):
    """
    Determines if a given clinical treatment qualifies for loyalty progress.
    """
    if not program:
        program = LoyaltyProgram.get_active_program()

    if not program.is_active:
        return False

    # Check basic consultation rule
    treatment_lower = (treatment_str or '').lower()
    service_title_lower = (service.title if service else '').lower()
    is_consultation = ('consult' in treatment_lower or 'consult' in service_title_lower or 
                       treatment_lower in ['consultation', 'checkup', 'follow_up'])
    
    if is_consultation and not program.allow_consultations_eligible:
        return False

    # If service is explicitly excluded
    if service and program.excluded_services.filter(pk=service.pk).exists():
        return False

    # If explicitly eligible services are specified
    if program.eligible_services.exists():
        if service and program.eligible_services.filter(pk=service.pk).exists():
            return True
        return False

    # Otherwise default eligibility setting applies
    return program.allow_all_services_by_default


def stage_appointment_for_verification(appointment):
    """
    Stages an appointment when treatment is marked completed.
    Does NOT add loyalty progress or send notifications.
    Places the appointment in the 'Awaiting Loyalty Verification' queue for receptionist review.
    """
    if appointment and appointment.loyalty_status in ['none', '']:
        appointment.loyalty_status = 'awaiting_verification'
        appointment.save(update_fields=['loyalty_status'])
    return appointment


@transaction.atomic
def verify_and_grant_loyalty_progress(
    appointment=None,
    phone=None,
    full_name=None,
    email=None,
    service=None,
    treatment_name="",
    invoice_ref="",
    amount_paid=0,
    payment_status="",
    staff_user=None,
    notes=""
):
    """
    HUMAN VERIFICATION GATE:
    Authorized receptionist/admin verifies completed treatment and explicitly grants +1 progress.
    Validates eligibility, duplicate transactions, and payment requirements.
    Updates patient progress, checks threshold for reward unlock, creates audit logs, and dispatches notifications.
    """
    program = LoyaltyProgram.get_active_program()
    if not program.is_active:
        return {
            'success': False,
            'message': 'Loyalty program is currently inactive.'
        }

    # Extract patient and treatment details
    if appointment:
        patient_phone = phone or appointment.phone
        patient_name = full_name or appointment.full_name
        patient_email = email or appointment.email
        service_obj = service or appointment.service
        treatment_label = treatment_name or (service_obj.title if service_obj else appointment.get_treatment_display())
        amount = amount_paid or (Decimal(str(appointment.estimated_amount).replace(',', '')) if appointment.estimated_amount and appointment.estimated_amount.replace(',', '').isdigit() else Decimal('0.00'))
        current_payment_status = payment_status or appointment.payment_status
    else:
        patient_phone = phone
        patient_name = full_name
        patient_email = email
        service_obj = service
        treatment_label = treatment_name or (service_obj.title if service_obj else "Clinical Treatment")
        amount = Decimal(str(amount_paid)) if amount_paid else Decimal('0.00')
        current_payment_status = payment_status or 'paid'

    if not patient_phone:
        return {
            'success': False,
            'message': 'Cannot verify loyalty progress: Patient phone number is missing.'
        }

    # 1. Payment requirement check (if configured)
    if program.require_payment_verification and current_payment_status not in ['paid', 'waived']:
        return {
            'success': False,
            'message': f"Payment verification required. Current payment status is '{current_payment_status}'. Please verify payment before granting loyalty progress."
        }

    # 2. Service Eligibility check
    if not is_service_eligible(service=service_obj, treatment_str=treatment_label, program=program):
        return {
            'success': False,
            'message': f"Treatment '{treatment_label}' is not eligible for loyalty points under active program rules."
        }

    # 3. Get or Create Patient Profile
    patient = get_or_create_patient_profile(
        phone=patient_phone,
        full_name=patient_name,
        email=patient_email,
        program=program
    )

    # 4. Strict Duplicate Check (Database Level)
    if appointment:
        existing_tx = LoyaltyTransaction.objects.filter(
            patient=patient,
            appointment=appointment,
            transaction_type='treatment_completed'
        ).first()
        if existing_tx:
            if appointment.loyalty_status != 'verified':
                appointment.loyalty_status = 'verified'
                appointment.save(update_fields=['loyalty_status'])
            return {
                'success': True,
                'already_processed': True,
                'patient': patient,
                'message': f"Appointment {appointment.appointment_number or appointment.id} was already verified on {existing_tx.created_at.strftime('%Y-%m-%d')}."
            }

    # 5. Capture Previous and New Progress
    previous_progress = patient.current_progress
    new_progress = previous_progress + 1
    patient.current_progress = new_progress
    patient.total_completed_eligible_treatments += 1

    # 6. Log Immutable Loyalty Transaction
    tx = LoyaltyTransaction.objects.create(
        patient=patient,
        program=program,
        appointment=appointment,
        service=service_obj,
        treatment_name=treatment_label,
        invoice_reference=invoice_ref,
        amount_paid=amount,
        transaction_type='treatment_completed',
        progress_added=1,
        previous_progress=previous_progress,
        new_progress=new_progress,
        notes=notes or f"Verified by {staff_user.username if staff_user else 'Staff'}. Progress: {previous_progress}/{program.required_completed_treatments} → {new_progress}/{program.required_completed_treatments}.",
        created_by=staff_user
    )

    reward_unlocked = None

    # 7. Check Reward Threshold (e.g. 3 of 3)
    if new_progress >= program.required_completed_treatments:
        expires_at = timezone.now() + timedelta(days=program.expiry_days)
        reward_unlocked = LoyaltyReward.objects.create(
            patient=patient,
            program=program,
            reward_type=program.reward_type,
            discount_percentage=program.discount_percentage,
            fixed_discount_amount=program.fixed_discount_amount,
            maximum_discount_amount=program.maximum_discount_amount,
            status='available',
            expires_at=expires_at
        )

        # Reset Progress for Next Cycle
        patient.current_progress = 0
        patient.current_cycle += 1
        patient.total_rewards_earned += 1

        LoyaltyTransaction.objects.create(
            patient=patient,
            program=program,
            treatment_name=f"Unlocked Reward: {reward_unlocked.get_reward_display()}",
            transaction_type='reward_unlocked',
            progress_added=0,
            previous_progress=new_progress,
            new_progress=0,
            notes=f"Reward {reward_unlocked.reward_reference} unlocked ({reward_unlocked.get_reward_display()}). Valid until {expires_at.strftime('%Y-%m-%d')}.",
            created_by=staff_user
        )

    patient.save()

    # 8. Create Dedicated Human Verification Audit Log
    LoyaltyVerificationAuditLog.objects.create(
        patient=patient,
        appointment=appointment,
        service=service_obj,
        service_name=treatment_label,
        decision='approved',
        previous_progress=previous_progress,
        new_progress=new_progress,
        reward_unlocked=bool(reward_unlocked),
        payment_status_at_verification=current_payment_status,
        notes=notes,
        verified_by=staff_user
    )

    # 9. Update Appointment Record
    if appointment:
        appointment.loyalty_status = 'verified'
        appointment.loyalty_verified_at = timezone.now()
        appointment.loyalty_verified_by = staff_user
        appointment.save(update_fields=['loyalty_status', 'loyalty_verified_at', 'loyalty_verified_by'])

    # 10. Multi-Channel Patient Notification (ONLY AFTER SUCCESSFUL VERIFICATION)
    try:
        from .notifications import dispatch_loyalty_notifications
        if reward_unlocked:
            dispatch_loyalty_notifications(patient=patient, event_type='reward_unlocked', reward=reward_unlocked)
        else:
            dispatch_loyalty_notifications(patient=patient, event_type='progress_update')
    except Exception as e:
        print(f"Warning: Loyalty notification dispatch error: {e}")

    return {
        'success': True,
        'patient': patient,
        'previous_progress': previous_progress,
        'new_progress': new_progress,
        'cycle_reset': bool(reward_unlocked),
        'reward_unlocked': reward_unlocked,
        'transaction': tx,
        'message': f"Loyalty progress verified (+1 Visit). Progress updated: {previous_progress}/{program.required_completed_treatments} → {new_progress}/{program.required_completed_treatments}."
    }


@transaction.atomic
def reject_loyalty_progress(
    appointment,
    reason,
    staff_user=None,
    notes=""
):
    """
    Marks a completed visit as NOT eligible for loyalty progress.
    Requires mandatory rejection reason and stores in audit logs.
    Sends ZERO patient notifications.
    """
    if not appointment:
        return {'success': False, 'message': 'Appointment record is required.'}

    if not reason or not reason.strip():
        return {'success': False, 'message': 'A reason is required to mark a treatment as not eligible.'}

    program = LoyaltyProgram.get_active_program()
    patient = get_or_create_patient_profile(
        phone=appointment.phone,
        full_name=appointment.full_name,
        email=appointment.email,
        program=program
    )

    appointment.loyalty_status = 'not_eligible'
    appointment.loyalty_rejection_reason = reason.strip()
    appointment.loyalty_verified_at = timezone.now()
    appointment.loyalty_verified_by = staff_user
    appointment.save(update_fields=['loyalty_status', 'loyalty_rejection_reason', 'loyalty_verified_at', 'loyalty_verified_by'])

    # Log in Verification Audit Table
    LoyaltyVerificationAuditLog.objects.create(
        patient=patient,
        appointment=appointment,
        service=appointment.service,
        service_name=appointment.service.title if appointment.service else appointment.get_treatment_display(),
        decision='rejected',
        previous_progress=patient.current_progress,
        new_progress=patient.current_progress,
        reward_unlocked=False,
        payment_status_at_verification=appointment.payment_status,
        rejection_reason=reason.strip(),
        notes=notes,
        verified_by=staff_user
    )

    return {
        'success': True,
        'message': f"Visit marked as Not Eligible ({reason.strip()}). No loyalty points were granted."
    }


# Backwards compatibility alias
record_treatment_completion = verify_and_grant_loyalty_progress


@transaction.atomic
def apply_reward_to_bill(
    reward_id_or_ref,
    patient_phone,
    invoice_ref="",
    total_bill_amount=0,
    staff_user=None,
    notes=""
):
    """
    Validates and redeems an active reward at reception during billing.
    Checks identity, availability, expiration, and records redemption audit.
    """
    norm_phone = normalize_phone(patient_phone)
    now = timezone.now()

    if str(reward_id_or_ref).isdigit():
        reward = LoyaltyReward.objects.filter(pk=int(reward_id_or_ref)).select_related('patient', 'program').first()
    else:
        reward = LoyaltyReward.objects.filter(reward_reference__iexact=str(reward_id_or_ref).strip()).select_related('patient', 'program').first()

    if not reward:
        return {
            'success': False,
            'error': 'Reward record not found.'
        }

    if reward.patient.normalized_phone != norm_phone:
        return {
            'success': False,
            'error': f"Phone number mismatch. This reward belongs to registered phone {reward.patient.phone}."
        }

    if reward.status == 'applied':
        return {
            'success': False,
            'error': f"Reward {reward.reward_reference} has already been redeemed on {reward.used_at.strftime('%Y-%m-%d')} (Invoice: {reward.applied_invoice_ref or 'N/A'})."
        }
    if reward.status == 'expired' or reward.expires_at <= now:
        reward.status = 'expired'
        reward.save(update_fields=['status'])
        return {
            'success': False,
            'error': f"Reward {reward.reward_reference} expired on {reward.expires_at.strftime('%Y-%m-%d')}."
        }
    if reward.status == 'cancelled':
        return {
            'success': False,
            'error': f"Reward {reward.reward_reference} was cancelled ({reward.cancellation_reason or 'Admin override'})."
        }

    bill_decimal = Decimal(str(total_bill_amount)) if total_bill_amount else Decimal('0.00')
    calc_discount = Decimal('0.00')

    if reward.reward_type == 'percentage':
        calc_discount = bill_decimal * (reward.discount_percentage / Decimal('100.0'))
        if reward.maximum_discount_amount > 0 and calc_discount > reward.maximum_discount_amount:
            calc_discount = reward.maximum_discount_amount
    elif reward.reward_type == 'fixed_amount':
        calc_discount = min(reward.fixed_discount_amount, bill_decimal)
    
    calc_discount = round(calc_discount, 2)

    reward.status = 'applied'
    reward.used_at = now
    reward.applied_invoice_ref = invoice_ref or f"INV-{now.strftime('%Y%m%d%H%M')}"
    reward.discount_amount_applied = calc_discount
    reward.applied_by = staff_user
    reward.save()

    patient = reward.patient
    patient.total_rewards_redeemed += 1
    patient.save(update_fields=['total_rewards_redeemed'])

    LoyaltyTransaction.objects.create(
        patient=patient,
        program=reward.program,
        treatment_name=f"Applied Reward: {reward.get_reward_display()}",
        invoice_reference=reward.applied_invoice_ref,
        amount_paid=calc_discount,
        transaction_type='reward_applied',
        progress_added=0,
        notes=notes or f"Redeemed {reward.reward_reference} ({reward.get_reward_display()}). Total discount given: NPR {calc_discount:,.2f}.",
        created_by=staff_user
    )

    try:
        from .notifications import dispatch_loyalty_notifications
        dispatch_loyalty_notifications(patient=patient, event_type='reward_applied', reward=reward)
    except Exception as e:
        print(f"Warning: Reward redemption notification error: {e}")

    return {
        'success': True,
        'reward': reward,
        'discount_amount': calc_discount,
        'final_payable': max(Decimal('0.00'), bill_decimal - calc_discount),
        'message': f"Reward {reward.reward_reference} applied successfully! Discount: NPR {calc_discount:,.2f}."
    }


def expire_stale_rewards():
    """
    Automated housekeeping function.
    Finds available rewards past their expiry date and updates status to 'expired'.
    """
    now = timezone.now()
    stale_rewards = LoyaltyReward.objects.filter(status='available', expires_at__lte=now)
    count = stale_rewards.count()
    if count > 0:
        for r in stale_rewards:
            r.status = 'expired'
            r.save(update_fields=['status'])
            LoyaltyTransaction.objects.create(
                patient=r.patient,
                program=r.program,
                treatment_name=f"Expired Reward: {r.reward_reference}",
                transaction_type='reward_expired',
                progress_added=0,
                notes=f"Reward {r.reward_reference} expired automatically after validity period."
            )
    return count
