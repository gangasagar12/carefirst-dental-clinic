from datetime import timedelta
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import (
    LoyaltyProgram,
    PatientLoyaltyProfile,
    LoyaltyTransaction,
    LoyaltyReward,
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

    # If existing profile, update latest name/email if currently generic/blank
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
        # If explicit list exists and this service isn't in it, return False
        return False

    # Otherwise default eligibility setting applies
    return program.allow_all_services_by_default


@transaction.atomic
def record_treatment_completion(
    appointment=None,
    phone=None,
    full_name=None,
    email=None,
    service=None,
    treatment_name="",
    invoice_ref="",
    amount_paid=0,
    staff_user=None,
    notes=""
):
    """
    Primary loyalty engine function.
    Processes a completed clinical treatment with strict transactional duplicate prevention.
    Increments progress, triggers rewards at threshold, and queues notifications.
    """
    program = LoyaltyProgram.get_active_program()
    if not program.is_active:
        return {
            'success': False,
            'message': 'Loyalty program is currently inactive.'
        }

    # Extract patient identity
    if appointment:
        patient_phone = phone or appointment.phone
        patient_name = full_name or appointment.full_name
        patient_email = email or appointment.email
        service_obj = service or appointment.service
        treatment_label = treatment_name or (service_obj.title if service_obj else appointment.get_treatment_display())
        amount = amount_paid or (Decimal(str(appointment.estimated_amount).replace(',', '')) if appointment.estimated_amount and appointment.estimated_amount.replace(',', '').isdigit() else Decimal('0.00'))
    else:
        patient_phone = phone
        patient_name = full_name
        patient_email = email
        service_obj = service
        treatment_label = treatment_name or (service_obj.title if service_obj else "Clinical Treatment")
        amount = Decimal(str(amount_paid)) if amount_paid else Decimal('0.00')

    if not patient_phone:
        return {
            'success': False,
            'message': 'Cannot add loyalty progress: Phone number is missing.'
        }

    # 1. Eligibility Check
    if not is_service_eligible(service=service_obj, treatment_str=treatment_label, program=program):
        return {
            'success': False,
            'message': f"Treatment '{treatment_label}' is excluded or not eligible for loyalty points."
        }

    # 2. Get or Create Patient Profile
    patient = get_or_create_patient_profile(
        phone=patient_phone,
        full_name=patient_name,
        email=patient_email,
        program=program
    )

    # 3. Strict Duplicate Check
    if appointment:
        existing_tx = LoyaltyTransaction.objects.filter(
            patient=patient,
            appointment=appointment,
            transaction_type='treatment_completed'
        ).first()
        if existing_tx:
            return {
                'success': True,
                'already_processed': True,
                'patient': patient,
                'message': f"Appointment {appointment.appointment_number or appointment.id} was already credited on {existing_tx.created_at.strftime('%Y-%m-%d')}."
            }

    # 4. Increment Progress & Total Completed
    old_progress = patient.current_progress
    new_progress = old_progress + 1
    patient.current_progress = new_progress
    patient.total_completed_eligible_treatments += 1

    # 5. Log Transaction
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
        notes=notes or f"Completed treatment '{treatment_label}'. Progress {new_progress}/{program.required_completed_treatments}.",
        created_by=staff_user
    )

    reward_unlocked = None

    # 6. Check Reward Threshold
    if new_progress >= program.required_completed_treatments:
        # Create Unlocked Reward
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

        # Log Reward Unlocked Transaction
        LoyaltyTransaction.objects.create(
            patient=patient,
            program=program,
            treatment_name=f"Unlocked Reward: {reward_unlocked.get_reward_display()}",
            transaction_type='reward_unlocked',
            progress_added=0,
            notes=f"Reward {reward_unlocked.reward_reference} generated ({reward_unlocked.get_reward_display()}). Valid until {expires_at.strftime('%Y-%m-%d')}.",
            created_by=staff_user
        )

    patient.save()

    # 7. Multi-Channel Notifications Trigger
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
        'progress_added': 1,
        'new_progress': patient.current_progress if not reward_unlocked else program.required_completed_treatments,
        'cycle_reset': bool(reward_unlocked),
        'reward_unlocked': reward_unlocked,
        'transaction': tx,
        'message': f"Loyalty progress successfully recorded for {patient.full_name} ({patient.phone})."
    }


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

    # Find reward by ID or reference string
    if str(reward_id_or_ref).isdigit():
        reward = LoyaltyReward.objects.filter(pk=int(reward_id_or_ref)).select_related('patient', 'program').first()
    else:
        reward = LoyaltyReward.objects.filter(reward_reference__iexact=str(reward_id_or_ref).strip()).select_related('patient', 'program').first()

    if not reward:
        return {
            'success': False,
            'error': 'Reward record not found.'
        }

    # Validate Phone Match
    if reward.patient.normalized_phone != norm_phone:
        return {
            'success': False,
            'error': f"Phone number mismatch. This reward belongs to registered phone {reward.patient.phone}."
        }

    # Validate Status
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

    # Calculate Discount Amount
    bill_decimal = Decimal(str(total_bill_amount)) if total_bill_amount else Decimal('0.00')
    calc_discount = Decimal('0.00')

    if reward.reward_type == 'percentage':
        calc_discount = bill_decimal * (reward.discount_percentage / Decimal('100.0'))
        if reward.maximum_discount_amount > 0 and calc_discount > reward.maximum_discount_amount:
            calc_discount = reward.maximum_discount_amount
    elif reward.reward_type == 'fixed_amount':
        calc_discount = min(reward.fixed_discount_amount, bill_decimal)
    
    calc_discount = round(calc_discount, 2)

    # Mark Reward as Applied
    reward.status = 'applied'
    reward.used_at = now
    reward.applied_invoice_ref = invoice_ref or f"INV-{now.strftime('%Y%m%d%H%M')}"
    reward.discount_amount_applied = calc_discount
    reward.applied_by = staff_user
    reward.save()

    # Update Patient Lifetime Stats
    patient = reward.patient
    patient.total_rewards_redeemed += 1
    patient.save(update_fields=['total_rewards_redeemed'])

    # Audit Transaction
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

    # Proactive Redemption Notification
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
