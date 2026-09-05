from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.core.paginator import Paginator

from appointments.models import Appointment
from main.models import Service, Doctor, PricingCategory, PricingItem, SpecialOffer, Testimonial, SiteSettings, ContactMessage, HeroSlide, ClinicGallery
from media_center.models import Video
from loyalty.models import PatientLoyaltyProfile, LoyaltyReward, normalize_phone
from loyalty.services import record_treatment_completion, apply_reward_to_bill
from .forms import (
    AppointmentForm, ServiceForm, DoctorForm, PricingCategoryForm,
    PricingItemForm, SpecialOfferForm, TestimonialForm, VideoForm, SiteSettingsForm,
    HeroSlideForm, ClinicGalleryForm
)


def is_staff_user(user):
    return user.is_authenticated and user.is_staff


# ── Authentication ─────────────────────────────────────────────────────────────

def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard:home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                next_url = request.GET.get('next') or 'dashboard:home'
                return redirect(next_url)
            else:
                messages.error(request, "Access restricted. Staff permissions required.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm(request)
        
    return render(request, 'dashboard/login.html', {'form': form})


def dashboard_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('dashboard:login')


# ── Dashboard Command Center (Overview) ────────────────────────────────────────

@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def dashboard_home(request):
    today = timezone.localdate()
    seven_days_ago = today - timedelta(days=7)

    # Key Metrics
    total_appointments = Appointment.objects.count()
    today_appointments = Appointment.objects.filter(preferred_date=today).count()
    pending_appointments = Appointment.objects.filter(status__in=['new', 'pending']).count()
    confirmed_appointments = Appointment.objects.filter(status='confirmed').count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    
    total_services = Service.objects.count()
    total_doctors = Doctor.objects.count()
    active_offers = SpecialOffer.objects.filter(is_active=True).count()
    
    # Recent appointments
    recent_appointments = Appointment.objects.select_related('doctor', 'service', 'branch').order_by('-id')[:10]
    
    # Recent inquiries
    recent_messages = ContactMessage.objects.order_by('-created_at')[:6]

    # Treatment categories distribution
    treatment_stats = Appointment.objects.values('treatment').annotate(count=Count('id')).order_by('-count')[:5]

    context = {
        'title': 'Clinic Command Center',
        'active_page': 'overview',
        'metrics': {
            'total_appointments': total_appointments,
            'today_appointments': today_appointments,
            'pending_appointments': pending_appointments,
            'confirmed_appointments': confirmed_appointments,
            'completed_appointments': completed_appointments,
            'unread_messages': unread_messages,
            'total_services': total_services,
            'total_doctors': total_doctors,
            'active_offers': active_offers,
        },
        'recent_appointments': recent_appointments,
        'recent_messages': recent_messages,
        'treatment_stats': treatment_stats,
        'today': today,
    }
    return render(request, 'dashboard/index.html', context)


# ── Appointments Management ───────────────────────────────────────────────────

@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def appointments_list(request):
    q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    date_filter = request.GET.get('date', '').strip()
    doctor_filter = request.GET.get('doctor', '').strip()

    queryset = Appointment.objects.select_related('doctor', 'service', 'branch').order_by('-id')

    if q:
        queryset = queryset.filter(
            Q(full_name__icontains=q) |
            Q(phone__icontains=q) |
            Q(email__icontains=q) |
            Q(booking_id__icontains=q) |
            Q(access_token__icontains=q) |
            Q(appointment_number__icontains=q)
        )
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if date_filter:
        queryset = queryset.filter(preferred_date=date_filter)
    if doctor_filter:
        queryset = queryset.filter(doctor_id=doctor_filter)

    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page', 1)
    appointments = paginator.get_page(page_number)
    
    doctors = Doctor.objects.filter(is_active=True)

    context = {
        'title': 'Appointments Manager',
        'active_page': 'appointments',
        'appointments': appointments,
        'doctors': doctors,
        'q': q,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'doctor_filter': doctor_filter,
        'status_choices': Appointment.STATUS_CHOICES,
    }
    return render(request, 'dashboard/appointments.html', context)


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment.objects.select_related('doctor', 'service', 'branch'), pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        new_payment = request.POST.get('payment_status')

        if new_payment in dict(Appointment.PAYMENT_STATUS_CHOICES):
            appointment.payment_status = new_payment

        if new_status in dict(Appointment.STATUS_CHOICES):
            old_status = appointment.status
            was_completed = appointment.status == 'completed'
            was_checked_in = appointment.status == 'checked_in'
            appointment.status = new_status
            
            if new_status == 'checked_in' and not was_checked_in:
                appointment.checked_in_at = timezone.now()
            elif new_status == 'completed' and not was_completed:
                appointment.completed_at = timezone.now()
                if appointment.loyalty_status in ['none', '']:
                    appointment.loyalty_status = 'awaiting_verification'

            appointment.save()

            # Trigger automated status update email to patient if status changed
            if old_status != new_status:
                try:
                    from main.services.email import send_appointment_status_update_email
                    send_appointment_status_update_email(appointment, old_status, new_status)
                except Exception as e:
                    print(f"Error sending status update email: {e}")

            if new_status == 'completed' and not was_completed:
                messages.success(
                    request,
                    f"Visit marked as Completed. Placed in 'Awaiting Loyalty Verification' queue for receptionist review."
                )
            else:
                messages.success(request, f"Appointment status updated to '{appointment.get_status_display()}'.")
            return redirect('dashboard:appointment_detail', pk=pk)

    # Fetch patient's loyalty profile & active rewards for receptionist display
    norm_phone = normalize_phone(appointment.phone)
    loyalty_profile = PatientLoyaltyProfile.objects.filter(normalized_phone=norm_phone).first()

    # Pre-generate WhatsApp message templates for 1-click dispatch
    from appointments.whatsapp_services import generate_whatsapp_templates
    whatsapp_data = generate_whatsapp_templates(appointment, request=request)

    context = {
        'title': f"Appointment {appointment.display_booking_id} - {appointment.full_name}",
        'active_page': 'appointments',
        'appointment': appointment,
        'status_choices': Appointment.STATUS_CHOICES,
        'payment_status_choices': Appointment.PAYMENT_STATUS_CHOICES,
        'loyalty_profile': loyalty_profile,
        'active_rewards': loyalty_profile.active_rewards() if loyalty_profile else [],
        'whatsapp_data': whatsapp_data,
    }
    return render(request, 'dashboard/appointment_detail.html', context)


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def appointment_whatsapp_data(request, pk):
    """
    Returns pre-formatted WhatsApp templates and clean phone numbers for an appointment in JSON.
    """
    appointment = get_object_or_404(Appointment.objects.select_related('doctor', 'service', 'branch'), pk=pk)
    from appointments.whatsapp_services import generate_whatsapp_templates
    data = generate_whatsapp_templates(appointment, request=request)
    return JsonResponse(data)


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def appointment_update_status(request, pk):
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, pk=pk)
        new_status = request.POST.get('status')
        if new_status in dict(Appointment.STATUS_CHOICES):
            old_status = appointment.status
            was_completed = appointment.status == 'completed'
            was_checked_in = appointment.status == 'checked_in'
            appointment.status = new_status
            if new_status == 'checked_in' and not was_checked_in:
                appointment.checked_in_at = timezone.now()
            elif new_status == 'completed' and not was_completed:
                appointment.completed_at = timezone.now()
                if appointment.loyalty_status in ['none', '']:
                    appointment.loyalty_status = 'awaiting_verification'
            appointment.save()

            # Trigger automated status update email to patient if status changed
            if old_status != new_status:
                try:
                    from main.services.email import send_appointment_status_update_email
                    send_appointment_status_update_email(appointment, old_status, new_status)
                except Exception as e:
                    print(f"Error sending status update email: {e}")

            msg = f"Appointment status updated to '{appointment.get_status_display()}'."
            if new_status == 'completed':
                msg += " (Awaiting Loyalty Verification)"

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'status': new_status, 
                    'status_display': appointment.get_status_display(),
                    'loyalty_status': appointment.loyalty_status
                })
            messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:appointments'))


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def appointment_edit(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated successfully.")
            return redirect('dashboard:appointment_detail', pk=pk)
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'dashboard/form_generic.html', {
        'title': f"Edit Appointment #{appointment.id}",
        'active_page': 'appointments',
        'form': form,
        'back_url': 'dashboard:appointments',
    })


# ── Inquiries & Patient Messages ───────────────────────────────────────────────

@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def inquiries_list(request):
    q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    queryset = ContactMessage.objects.order_by('-created_at')

    if q:
        queryset = queryset.filter(
            Q(name__icontains=q) |
            Q(email__icontains=q) |
            Q(subject__icontains=q) |
            Q(message__icontains=q)
        )
    if status_filter == 'unread':
        queryset = queryset.filter(is_read=False)
    elif status_filter == 'read':
        queryset = queryset.filter(is_read=True)

    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page', 1)
    inquiries = paginator.get_page(page_number)

    context = {
        'title': 'Patient Inquiries & Messages',
        'active_page': 'inquiries',
        'inquiries': inquiries,
        'q': q,
        'status_filter': status_filter,
    }
    return render(request, 'dashboard/inquiries.html', context)


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def inquiry_toggle_read(request, pk):
    inquiry = get_object_or_404(ContactMessage, pk=pk)
    inquiry.is_read = not inquiry.is_read
    inquiry.save()
    messages.success(request, f"Marked message from {inquiry.name} as {'read' if inquiry.is_read else 'unread'}.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:inquiries'))


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def inquiry_delete(request, pk):
    inquiry = get_object_or_404(ContactMessage, pk=pk)
    name = inquiry.name
    inquiry.delete()
    messages.success(request, f"Message from {name} deleted.")
    return redirect('dashboard:inquiries')


# ── Services Management ───────────────────────────────────────────────────────

@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def services_list(request):
    services = Service.objects.all().order_by('order', 'title')
    return render(request, 'dashboard/services.html', {
        'title': 'Dental Services Catalog',
        'active_page': 'services',
        'services': services,
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save()
            messages.success(request, f"Service '{service.title}' created successfully.")
            return redirect('dashboard:services')
    else:
        form = ServiceForm()

    return render(request, 'dashboard/form_generic.html', {
        'title': 'Add New Dental Service',
        'active_page': 'services',
        'form': form,
        'back_url': 'dashboard:services',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, f"Service '{service.title}' updated successfully.")
            return redirect('dashboard:services')
    else:
        form = ServiceForm(instance=service)

    return render(request, 'dashboard/form_generic.html', {
        'title': f"Edit Service: {service.title}",
        'active_page': 'services',
        'form': form,
        'back_url': 'dashboard:services',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def service_toggle_active(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.is_active = not service.is_active
    service.save()
    messages.success(request, f"Service '{service.title}' is now {'Active' if service.is_active else 'Hidden'}.")
    return redirect('dashboard:services')


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    title = service.title
    service.delete()
    messages.success(request, f"Service '{title}' deleted.")
    return redirect('dashboard:services')


# ── Doctors Management ─────────────────────────────────────────────────────────

@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def doctors_list(request):
    doctors = Doctor.objects.all().order_by('order', 'name')
    return render(request, 'dashboard/doctors.html', {
        'title': 'Doctors & Clinical Team',
        'active_page': 'doctors',
        'doctors': doctors,
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def doctor_create(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, f"Doctor Dr. {doctor.name} added successfully.")
            return redirect('dashboard:doctors')
    else:
        form = DoctorForm()

    return render(request, 'dashboard/form_generic.html', {
        'title': 'Add New Doctor / Specialist',
        'active_page': 'doctors',
        'form': form,
        'back_url': 'dashboard:doctors',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def doctor_edit(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, f"Dr. {doctor.name} details updated.")
            return redirect('dashboard:doctors')
    else:
        form = DoctorForm(instance=doctor)

    return render(request, 'dashboard/form_generic.html', {
        'title': f"Edit Dr. {doctor.name}",
        'active_page': 'doctors',
        'form': form,
        'back_url': 'dashboard:doctors',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    name = doctor.name
    doctor.delete()
    messages.success(request, f"Dr. {name} removed.")
    return redirect('dashboard:doctors')


# ── Pricing Management ────────────────────────────────────────────────────────

@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def pricing_list(request):
    categories = PricingCategory.objects.prefetch_related('items').order_by('order', 'name')
    return render(request, 'dashboard/pricing.html', {
        'title': 'Pricing Categories & Procedure Rates',
        'active_page': 'pricing',
        'categories': categories,
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def pricing_category_create(request):
    if request.method == 'POST':
        form = PricingCategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Pricing category '{cat.name}' created.")
            return redirect('dashboard:pricing')
    else:
        form = PricingCategoryForm()

    return render(request, 'dashboard/form_generic.html', {
        'title': 'Add Pricing Category',
        'active_page': 'pricing',
        'form': form,
        'back_url': 'dashboard:pricing',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def pricing_category_edit(request, pk):
    cat = get_object_or_404(PricingCategory, pk=pk)
    if request.method == 'POST':
        form = PricingCategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{cat.name}' updated.")
            return redirect('dashboard:pricing')
    else:
        form = PricingCategoryForm(instance=cat)

    return render(request, 'dashboard/form_generic.html', {
        'title': f"Edit Category: {cat.name}",
        'active_page': 'pricing',
        'form': form,
        'back_url': 'dashboard:pricing',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def pricing_category_delete(request, pk):
    cat = get_object_or_404(PricingCategory, pk=pk)
    name = cat.name
    cat.delete()
    messages.success(request, f"Category '{name}' deleted.")
    return redirect('dashboard:pricing')


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def pricing_item_create(request):
    category_id = request.GET.get('category')
    initial = {}
    if category_id:
        initial['category'] = category_id

    if request.method == 'POST':
        form = PricingItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, f"Item '{item.name}' added.")
            return redirect('dashboard:pricing')
    else:
        form = PricingItemForm(initial=initial)

    return render(request, 'dashboard/form_generic.html', {
        'title': 'Add Procedure / Pricing Item',
        'active_page': 'pricing',
        'form': form,
        'back_url': 'dashboard:pricing',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def pricing_item_edit(request, pk):
    item = get_object_or_404(PricingItem, pk=pk)
    if request.method == 'POST':
        form = PricingItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"Item '{item.name}' updated.")
            return redirect('dashboard:pricing')
    else:
        form = PricingItemForm(instance=item)

    return render(request, 'dashboard/form_generic.html', {
        'title': f"Edit Item: {item.name}",
        'active_page': 'pricing',
        'form': form,
        'back_url': 'dashboard:pricing',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def pricing_item_delete(request, pk):
    item = get_object_or_404(PricingItem, pk=pk)
    name = item.name
    item.delete()
    messages.success(request, f"Pricing item '{name}' deleted.")
    return redirect('dashboard:pricing')


# ── Special Offers ─────────────────────────────────────────────────────────────

@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def offers_list(request):
    offers = SpecialOffer.objects.all().order_by('-start_date')
    return render(request, 'dashboard/offers.html', {
        'title': 'Special Offers & Promotions',
        'active_page': 'offers',
        'offers': offers,
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def offer_create(request):
    if request.method == 'POST':
        form = SpecialOfferForm(request.POST, request.FILES)
        if form.is_valid():
            offer = form.save()
            messages.success(request, f"Offer '{offer.title}' created.")
            return redirect('dashboard:offers')
    else:
        form = SpecialOfferForm()

    return render(request, 'dashboard/form_generic.html', {
        'title': 'Create Special Offer',
        'active_page': 'offers',
        'form': form,
        'back_url': 'dashboard:offers',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def offer_edit(request, pk):
    offer = get_object_or_404(SpecialOffer, pk=pk)
    if request.method == 'POST':
        form = SpecialOfferForm(request.POST, request.FILES, instance=offer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Offer '{offer.title}' updated.")
            return redirect('dashboard:offers')
    else:
        form = SpecialOfferForm(instance=offer)

    return render(request, 'dashboard/form_generic.html', {
        'title': f"Edit Offer: {offer.title}",
        'active_page': 'offers',
        'form': form,
        'back_url': 'dashboard:offers',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def offer_delete(request, pk):
    offer = get_object_or_404(SpecialOffer, pk=pk)
    title = offer.title
    offer.delete()
    messages.success(request, f"Offer '{title}' removed.")
    return redirect('dashboard:offers')


# ── Testimonials ───────────────────────────────────────────────────────────────

@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def testimonials_list(request):
    testimonials = Testimonial.objects.all().order_by('order', '-id')
    return render(request, 'dashboard/testimonials.html', {
        'title': 'Patient Testimonials',
        'active_page': 'testimonials',
        'testimonials': testimonials,
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def testimonial_create(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            t = form.save()
            messages.success(request, f"Testimonial from '{t.patient_name}' added.")
            return redirect('dashboard:testimonials')
    else:
        form = TestimonialForm()

    return render(request, 'dashboard/form_generic.html', {
        'title': 'Add Patient Testimonial',
        'active_page': 'testimonials',
        'form': form,
        'back_url': 'dashboard:testimonials',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def testimonial_edit(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES, instance=testimonial)
        if form.is_valid():
            form.save()
            messages.success(request, "Testimonial updated.")
            return redirect('dashboard:testimonials')
    else:
        form = TestimonialForm(instance=testimonial)

    return render(request, 'dashboard/form_generic.html', {
        'title': f"Edit Testimonial: {testimonial.patient_name}",
        'active_page': 'testimonials',
        'form': form,
        'back_url': 'dashboard:testimonials',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def testimonial_delete(request, pk):
    t = get_object_or_404(Testimonial, pk=pk)
    name = t.patient_name
    t.delete()
    messages.success(request, f"Testimonial from '{name}' deleted.")
    return redirect('dashboard:testimonials')


# ── Media & Videos ────────────────────────────────────────────────────────────

@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def media_list(request):
    videos = Video.objects.all().order_by('-published_date')
    return render(request, 'dashboard/media.html', {
        'title': 'Media Center & Videos',
        'active_page': 'media',
        'videos': videos,
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def video_create(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            v = form.save()
            messages.success(request, f"Video '{v.title}' added.")
            return redirect('dashboard:media')
    else:
        form = VideoForm()

    return render(request, 'dashboard/form_generic.html', {
        'title': 'Add Video / Reel',
        'active_page': 'media',
        'form': form,
        'back_url': 'dashboard:media',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def video_edit(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, f"Video '{video.title}' updated.")
            return redirect('dashboard:media')
    else:
        form = VideoForm(instance=video)

    return render(request, 'dashboard/form_generic.html', {
        'title': f"Edit Video: {video.title}",
        'active_page': 'media',
        'form': form,
        'back_url': 'dashboard:media',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def video_delete(request, pk):
    v = get_object_or_404(Video, pk=pk)
    title = v.title
    v.delete()
    messages.success(request, f"Video '{title}' deleted.")
    return redirect('dashboard:media')


# ── Global Site & Clinic Settings ─────────────────────────────────────────────

@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def settings_view(request):
    settings_obj = SiteSettings.objects.first()
    if not settings_obj:
        settings_obj = SiteSettings.objects.create()

    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Clinic settings updated successfully.")
            return redirect('dashboard:settings')
    else:
        form = SiteSettingsForm(instance=settings_obj)

    return render(request, 'dashboard/settings.html', {
        'title': 'Clinic & Site Settings',
        'active_page': 'settings',
        'form': form,
    })


# ── Hero Sliders & Gallery Banners ────────────────────────────────────────────

@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def sliders_list(request):
    slides = HeroSlide.objects.all().order_by('order', 'id')
    gallery_images = ClinicGallery.objects.all().order_by('order', 'id')
    return render(request, 'dashboard/sliders.html', {
        'title': 'Hero Sliders & Gallery Banners',
        'active_page': 'sliders',
        'slides': slides,
        'gallery_images': gallery_images,
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def slide_create(request):
    if request.method == 'POST':
        form = HeroSlideForm(request.POST, request.FILES)
        if form.is_valid():
            slide = form.save()
            messages.success(request, f"Hero slide '{slide.title or slide.id}' added.")
            return redirect('dashboard:sliders')
    else:
        form = HeroSlideForm()

    return render(request, 'dashboard/form_generic.html', {
        'title': 'Add Hero Background Slide',
        'active_page': 'sliders',
        'form': form,
        'back_url': 'dashboard:sliders',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def slide_edit(request, pk):
    slide = get_object_or_404(HeroSlide, pk=pk)
    if request.method == 'POST':
        form = HeroSlideForm(request.POST, request.FILES, instance=slide)
        if form.is_valid():
            form.save()
            messages.success(request, "Hero slide updated.")
            return redirect('dashboard:sliders')
    else:
        form = HeroSlideForm(instance=slide)

    return render(request, 'dashboard/form_generic.html', {
        'title': f"Edit Hero Slide #{slide.id}",
        'active_page': 'sliders',
        'form': form,
        'back_url': 'dashboard:sliders',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def slide_toggle_active(request, pk):
    slide = get_object_or_404(HeroSlide, pk=pk)
    slide.is_active = not slide.is_active
    slide.save()
    messages.success(request, f"Slide #{slide.id} is now {'Active' if slide.is_active else 'Disabled'}.")
    return redirect('dashboard:sliders')


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def slide_delete(request, pk):
    slide = get_object_or_404(HeroSlide, pk=pk)
    slide.delete()
    messages.success(request, "Hero slide removed.")
    return redirect('dashboard:sliders')


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def gallery_create(request):
    if request.method == 'POST':
        form = ClinicGalleryForm(request.POST, request.FILES)
        if form.is_valid():
            g = form.save()
            messages.success(request, f"Gallery photo '{g.caption or g.id}' added.")
            return redirect('dashboard:sliders')
    else:
        form = ClinicGalleryForm()

    return render(request, 'dashboard/form_generic.html', {
        'title': 'Add Clinic Gallery Photo',
        'active_page': 'sliders',
        'form': form,
        'back_url': 'dashboard:sliders',
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def gallery_delete(request, pk):
    g = get_object_or_404(ClinicGallery, pk=pk)
    g.delete()
    messages.success(request, "Gallery photo removed.")
    return redirect('dashboard:sliders')


from loyalty.models import (
    LoyaltyProgram, PatientLoyaltyProfile, LoyaltyReward, 
    LoyaltyTransaction, LoyaltyNotificationLog, LoyaltyVerificationAuditLog
)
from loyalty.services import (
    verify_and_grant_loyalty_progress, reject_loyalty_progress, 
    record_treatment_completion, apply_reward_to_bill, expire_stale_rewards
)
from .forms import LoyaltyProgramForm


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def loyalty_reception(request):
    """
    Primary Receptionist Desk & Patient Lookup:
    Enables quick phone number search, visual progress indicator, available rewards,
    and 1-click reward redemption for invoices without requiring any patient login.
    """
    expire_stale_rewards()
    program = LoyaltyProgram.get_active_program()
    q = request.GET.get('q', '').strip()

    patient_result = None
    all_patients_count = PatientLoyaltyProfile.objects.count()
    active_rewards_count = LoyaltyReward.objects.filter(status='available', expires_at__gt=timezone.now()).count()
    redeemed_rewards_count = LoyaltyReward.objects.filter(status='applied').count()
    lifetime_treatments = PatientLoyaltyProfile.objects.aggregate(total=Sum('total_completed_eligible_treatments'))['total'] or 0

    if q:
        norm_q = normalize_phone(q)
        patient_result = PatientLoyaltyProfile.objects.filter(
            Q(normalized_phone__icontains=norm_q) |
            Q(phone__icontains=q) |
            Q(full_name__icontains=q) |
            Q(patient_id__icontains=q)
        ).first()

    recent_transactions = LoyaltyTransaction.objects.select_related('patient', 'service').order_by('-created_at')[:10]
    services = Service.objects.filter(is_active=True).order_by('order')

    context = {
        'title': 'CareFirst Smile Rewards — Reception Desk',
        'active_page': 'loyalty',
        'active_tab': 'reception',
        'program': program,
        'q': q,
        'patient': patient_result,
        'all_patients_count': all_patients_count,
        'active_rewards_count': active_rewards_count,
        'redeemed_rewards_count': redeemed_rewards_count,
        'lifetime_treatments': lifetime_treatments,
        'recent_transactions': recent_transactions,
        'services': services,
    }
    return render(request, 'dashboard/loyalty_reception.html', context)


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def loyalty_patient_lookup(request):
    """AJAX endpoint for instant phone/patient search at reception."""
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'success': False, 'error': 'No query provided'})

    norm_q = normalize_phone(q)
    patient = PatientLoyaltyProfile.objects.filter(
        Q(normalized_phone__icontains=norm_q) |
        Q(phone__icontains=q) |
        Q(full_name__icontains=q) |
        Q(patient_id__icontains=q)
    ).first()

    if not patient:
        return JsonResponse({'success': False, 'found': False, 'message': 'No patient loyalty profile found for this query.'})

    active_rewards = []
    for r in patient.active_rewards():
        active_rewards.append({
            'id': r.id,
            'reference': r.reward_reference,
            'label': r.get_reward_display(),
            'discount_percentage': float(r.discount_percentage),
            'expires_at': r.expires_at.strftime('%d %b %Y'),
            'days_remaining': r.days_remaining,
        })

    return JsonResponse({
        'success': True,
        'found': True,
        'patient': {
            'id': patient.id,
            'patient_id': patient.patient_id,
            'full_name': patient.full_name,
            'phone': patient.phone,
            'current_progress': patient.current_progress,
            'required_treatments': patient.program.required_completed_treatments,
            'current_cycle': patient.current_cycle,
            'progress_dots': patient.progress_dots,
            'total_completed': patient.total_completed_eligible_treatments,
            'total_rewards_earned': patient.total_rewards_earned,
            'total_rewards_redeemed': patient.total_rewards_redeemed,
            'active_rewards': active_rewards,
        }
    })


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def loyalty_apply_reward(request):
    """Processes 1-click reward redemption on an invoice."""
    if request.method != 'POST':
        return redirect('dashboard:loyalty_reception')

    reward_id = request.POST.get('reward_id')
    phone = request.POST.get('phone', '').strip()
    invoice_ref = request.POST.get('invoice_ref', '').strip()
    bill_amount = request.POST.get('bill_amount', '0').strip()
    notes = request.POST.get('notes', '').strip()

    res = apply_reward_to_bill(
        reward_id_or_ref=reward_id,
        patient_phone=phone,
        invoice_ref=invoice_ref,
        total_bill_amount=bill_amount,
        staff_user=request.user,
        notes=notes
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(res)

    if res.get('success'):
        messages.success(request, res.get('message', 'Reward successfully redeemed!'))
    else:
        messages.error(request, res.get('error', 'Could not apply reward.'))

    return redirect(f"/dashboard/loyalty/?q={phone}")


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def loyalty_record_visit(request):
    """Manually records a completed treatment visit for walk-in patients."""
    if request.method != 'POST':
        return redirect('dashboard:loyalty_reception')

    phone = request.POST.get('phone', '').strip()
    full_name = request.POST.get('full_name', '').strip()
    service_id = request.POST.get('service_id')
    treatment_name = request.POST.get('treatment_name', '').strip()
    invoice_ref = request.POST.get('invoice_ref', '').strip()
    amount_paid = request.POST.get('amount_paid', '0').strip()
    notes = request.POST.get('notes', '').strip()

    service_obj = Service.objects.filter(pk=service_id).first() if service_id else None

    res = record_treatment_completion(
        phone=phone,
        full_name=full_name,
        service=service_obj,
        treatment_name=treatment_name,
        invoice_ref=invoice_ref,
        amount_paid=amount_paid,
        staff_user=request.user,
        notes=notes
    )

    if res.get('success'):
        if res.get('reward_unlocked'):
            messages.success(request, f"🎉 3rd visit completed! Reward Unlocked for {full_name} ({res['reward_unlocked'].reward_reference} - 10% OFF)")
        elif not res.get('already_processed'):
            messages.success(request, f"Loyalty visit recorded: {res['new_progress']}/3 completed visits.")
    else:
        messages.error(request, res.get('message', 'Failed to record treatment visit.'))

    return redirect(f"/dashboard/loyalty/?q={phone}")


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def loyalty_rewards_list(request):
    """Complete audit ledger of all issued, redeemed, and expired rewards."""
    expire_stale_rewards()
    q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    queryset = LoyaltyReward.objects.select_related('patient', 'program', 'applied_by').order_by('-unlocked_at')

    if q:
        norm_q = normalize_phone(q)
        queryset = queryset.filter(
            Q(reward_reference__icontains=q) |
            Q(patient__normalized_phone__icontains=norm_q) |
            Q(patient__phone__icontains=q) |
            Q(patient__full_name__icontains=q) |
            Q(applied_invoice_ref__icontains=q)
        )
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page', 1)
    rewards = paginator.get_page(page_number)

    context = {
        'title': 'Rewards Audit Ledger — CareFirst Smile Rewards',
        'active_page': 'loyalty',
        'active_tab': 'rewards',
        'rewards': rewards,
        'q': q,
        'status_filter': status_filter,
        'status_choices': LoyaltyReward.STATUS_CHOICES,
    }
    return render(request, 'dashboard/loyalty_rewards.html', context)


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def loyalty_reward_cancel(request, pk):
    """Staff override to cancel an active reward with audit reason."""
    if request.method == 'POST':
        reward = get_object_or_404(LoyaltyReward, pk=pk)
        reason = request.POST.get('reason', '').strip() or "Staff manual override"
        reward.status = 'cancelled'
        reward.cancellation_reason = reason
        reward.save(update_fields=['status', 'cancellation_reason'])

        LoyaltyTransaction.objects.create(
            patient=reward.patient,
            program=reward.program,
            treatment_name=f"Cancelled Reward: {reward.reward_reference}",
            transaction_type='reward_cancelled',
            progress_added=0,
            notes=f"Reward {reward.reward_reference} cancelled by {request.user.username}. Reason: {reason}",
            created_by=request.user
        )
        messages.success(request, f"Reward {reward.reward_reference} was cancelled.")
    return redirect('dashboard:loyalty_rewards')


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def loyalty_program_settings(request):
    """Admin configuration UI for CareFirst Smile Rewards rules."""
    program = LoyaltyProgram.get_active_program()

    if request.method == 'POST':
        form = LoyaltyProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            messages.success(request, "CareFirst Smile Rewards configuration updated successfully.")
            return redirect('dashboard:loyalty_program')
    else:
        form = LoyaltyProgramForm(instance=program)

    context = {
        'title': 'Loyalty Program Rules & Settings',
        'active_page': 'loyalty',
        'active_tab': 'program',
        'form': form,
        'program': program,
    }
    return render(request, 'dashboard/loyalty_programs.html', context)


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def loyalty_transactions_list(request):
    """Complete immutable audit stream of all points, rewards, and redemptions."""
    q = request.GET.get('q', '').strip()
    tx_type = request.GET.get('type', '').strip()

    queryset = LoyaltyTransaction.objects.select_related('patient', 'service', 'created_by').order_by('-created_at')

    if q:
        norm_q = normalize_phone(q)
        queryset = queryset.filter(
            Q(patient__normalized_phone__icontains=norm_q) |
            Q(patient__phone__icontains=q) |
            Q(patient__full_name__icontains=q) |
            Q(invoice_reference__icontains=q) |
            Q(treatment_name__icontains=q)
        )
    if tx_type:
        queryset = queryset.filter(transaction_type=tx_type)

    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page', 1)
    transactions = paginator.get_page(page_number)

    context = {
        'title': 'Loyalty Activity Ledger & Audit Logs',
        'active_page': 'loyalty',
        'active_tab': 'transactions',
        'transactions': transactions,
        'q': q,
        'tx_type': tx_type,
        'transaction_types': LoyaltyTransaction.TRANSACTION_TYPES,
    }
    return render(request, 'dashboard/loyalty_transactions.html', context)


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def loyalty_verification_queue(request):
    """
    HUMAN VERIFICATION DESK:
    Displays completed treatments awaiting receptionist verification for loyalty points.
    Enforces human review before any loyalty points or notifications are granted.
    """
    program = LoyaltyProgram.get_active_program()
    status_filter = request.GET.get('status', 'awaiting_verification')
    q = request.GET.get('q', '').strip()

    queryset = Appointment.objects.filter(status='completed').select_related('service', 'doctor', 'loyalty_verified_by')

    if status_filter == 'awaiting_verification':
        queryset = queryset.filter(loyalty_status='awaiting_verification')
    elif status_filter == 'verified':
        queryset = queryset.filter(loyalty_status='verified')
    elif status_filter == 'not_eligible':
        queryset = queryset.filter(loyalty_status='not_eligible')
    elif status_filter == 'all':
        queryset = queryset.filter(loyalty_status__in=['awaiting_verification', 'verified', 'not_eligible'])

    if q:
        norm_q = normalize_phone(q)
        queryset = queryset.filter(
            Q(phone__icontains=q) |
            Q(full_name__icontains=q) |
            Q(appointment_number__icontains=q) |
            Q(service__title__icontains=q)
        )

    queryset = queryset.order_by('-completed_at', '-created_at')
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page', 1)
    appointments = paginator.get_page(page_number)

    # Attach current loyalty progress preview for each appointment
    for app in appointments:
        norm_phone = normalize_phone(app.phone)
        prof = PatientLoyaltyProfile.objects.filter(normalized_phone=norm_phone, program=program).first()
        app.patient_profile = prof
        current_p = prof.current_progress if prof else 0
        app.preview_current_progress = current_p
        app.preview_new_progress = current_p + 1
        app.preview_will_unlock = (current_p + 1) >= program.required_completed_treatments

    counts = {
        'awaiting': Appointment.objects.filter(status='completed', loyalty_status='awaiting_verification').count(),
        'verified': Appointment.objects.filter(status='completed', loyalty_status='verified').count(),
        'not_eligible': Appointment.objects.filter(status='completed', loyalty_status='not_eligible').count(),
    }

    context = {
        'title': 'CareFirst Smile Rewards — Human Verification Desk',
        'active_page': 'loyalty',
        'active_tab': 'verification',
        'program': program,
        'appointments': appointments,
        'status_filter': status_filter,
        'counts': counts,
        'q': q,
    }
    return render(request, 'dashboard/loyalty_verification_queue.html', context)


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def loyalty_verify_appointment(request, pk):
    """
    POST Action: Receptionist approves completed service for loyalty progress (+1 visit).
    """
    if request.method != 'POST':
        return redirect('dashboard:loyalty_verification_queue')

    appointment = get_object_or_404(Appointment, pk=pk)
    notes = request.POST.get('notes', '').strip()
    payment_status = request.POST.get('payment_status', appointment.payment_status)

    if payment_status in dict(Appointment.PAYMENT_STATUS_CHOICES):
        appointment.payment_status = payment_status
        appointment.save(update_fields=['payment_status'])

    res = verify_and_grant_loyalty_progress(
        appointment=appointment,
        staff_user=request.user,
        notes=notes,
        payment_status=payment_status
    )

    if res.get('success'):
        if res.get('reward_unlocked'):
            reward = res['reward_unlocked']
            messages.success(
                request,
                f"🎉 Loyalty Verified for {appointment.full_name}! Threshold reached: Unlocked Reward {reward.reward_reference} ({reward.get_reward_display()}). Patient notified!"
            )
        elif res.get('already_processed'):
            messages.info(request, res['message'])
        else:
            messages.success(
                request,
                f"✓ Loyalty Verified for {appointment.full_name} (+1 Visit). Progress updated: {res['previous_progress']}/3 → {res['new_progress']}/3. Notification dispatched!"
            )
    else:
        messages.error(request, f"Verification Failed: {res.get('message', 'Unknown error')}")

    return redirect(request.META.get('HTTP_REFERER', 'dashboard:loyalty_verification_queue'))


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def loyalty_reject_appointment(request, pk):
    """
    POST Action: Receptionist marks completed service as NOT eligible for loyalty points.
    Requires mandatory rejection reason.
    """
    if request.method != 'POST':
        return redirect('dashboard:loyalty_verification_queue')

    appointment = get_object_or_404(Appointment, pk=pk)
    reason = request.POST.get('reason', '').strip()
    custom_reason = request.POST.get('custom_reason', '').strip()
    final_reason = custom_reason if reason == 'other' and custom_reason else reason
    notes = request.POST.get('notes', '').strip()

    if not final_reason:
        messages.error(request, "A valid reason is required to mark a treatment as not eligible.")
        return redirect('dashboard:loyalty_verification_queue')

    res = reject_loyalty_progress(
        appointment=appointment,
        reason=final_reason,
        staff_user=request.user,
        notes=notes
    )

    if res.get('success'):
        messages.warning(request, f"✕ Appointment #{appointment.id} marked as Not Eligible ({final_reason}). No loyalty points were granted.")
    else:
        messages.error(request, f"Action failed: {res.get('message')}")

    return redirect(request.META.get('HTTP_REFERER', 'dashboard:loyalty_verification_queue'))


@user_passes_test(is_staff_user, login_url='/dashboard/login/')
def loyalty_verification_logs(request):
    """
    Audit log of all human verification decisions (Approvals, Rejections, and Overrides).
    """
    q = request.GET.get('q', '').strip()
    decision_filter = request.GET.get('decision', '').strip()

    queryset = LoyaltyVerificationAuditLog.objects.select_related('patient', 'appointment', 'service', 'verified_by').order_by('-verified_at')

    if q:
        norm_q = normalize_phone(q)
        queryset = queryset.filter(
            Q(patient__normalized_phone__icontains=norm_q) |
            Q(patient__full_name__icontains=q) |
            Q(patient__phone__icontains=q) |
            Q(service_name__icontains=q) |
            Q(rejection_reason__icontains=q)
        )
    if decision_filter:
        queryset = queryset.filter(decision=decision_filter)

    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page', 1)
    logs = paginator.get_page(page_number)

    context = {
        'title': 'Loyalty Human Verification Audit Logs',
        'active_page': 'loyalty',
        'active_tab': 'verification_logs',
        'logs': logs,
        'q': q,
        'decision_filter': decision_filter,
    }
    return render(request, 'dashboard/loyalty_verification_logs.html', context)



