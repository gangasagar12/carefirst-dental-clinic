import json

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.templatetags.static import static
from appointments.forms import AppointmentForm
from .forms import ContactMessageForm
from .models import Doctor, Service, PricingCategory, AboutPageSettings, Branch, CoreValue, Technology, Testimonial, ClinicGallery, FAQ, GoogleBusiness, GoogleReview
from blogs.models import Post

def custom_404(request, exception=None):
    return render(request, '404.html', status=404)


def send_notification_email(instance, form_type):
    if not getattr(settings, 'EMAIL_HOST_USER', None) or settings.EMAIL_HOST_USER == 'your_clinic_email@gmail.com':
        return
        
    try:
        if form_type == 'appointment':
            subject = f"New Appointment Request from {instance.full_name}"
            message = (
                f"You have a new appointment request!\n\n"
                f"Name: {instance.full_name}\n"
                f"Phone: {instance.phone}\n"
                f"Email: {instance.email or 'N/A'}\n"
                f"Preferred Date: {instance.preferred_date}\n"
                f"Preferred Time: {instance.get_preferred_time_display() or 'Any'}\n"
                f"Treatment: {instance.get_treatment_display() or 'Not Sure'}\n"
                f"Message: {instance.message or 'N/A'}\n"
            )
        else:
            subject = f"New Contact Message from {instance.name}"
            message = (
                f"You have a new contact message!\n\n"
                f"Name: {instance.name}\n"
                f"Email: {instance.email}\n"
                f"Subject: {instance.subject}\n"
                f"Message:\n{instance.message}\n"
            )
            
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.NOTIFICATION_EMAIL],
            fail_silently=True,
        )
    except Exception:
        pass

def home(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'appointment':
            form = AppointmentForm(request.POST)
            if form.is_valid():
                instance = form.save()
                from main.services.email import send_clinic_admin_alert, queue_email_confirmation
                from main.services.whatsapp import queue_whatsapp_confirmation
                send_clinic_admin_alert(instance, 'appointment')
                queue_whatsapp_confirmation(instance.full_name, instance.phone, 'appointment', instance.id)
                details = {
                    'appointment_number': instance.appointment_number or f"CF-{instance.id:06d}",
                    'preferred_date': str(instance.preferred_date),
                    'preferred_time': instance.get_preferred_time_display() or 'Flexible',
                    'treatment': instance.service.title if getattr(instance, 'service', None) else (instance.get_treatment_display() if hasattr(instance, 'get_treatment_display') else 'General Consultation'),
                    'doctor': instance.doctor.name if getattr(instance, 'doctor', None) else 'CareFirst Clinical Team',
                }
                queue_email_confirmation(instance.full_name, instance.email, 'appointment', instance.id, details=details)
                return redirect('appointments:confirmation', appointment_number=instance.appointment_number)
            else:
                messages.error(request, 'There was an error in your appointment request. Please check the fields and try again.')
            return redirect('main:home')
        elif form_type == 'contact':
            form = ContactMessageForm(request.POST)
            if form.is_valid():
                instance = form.save()
                from main.services.email import send_clinic_admin_alert, queue_email_confirmation
                from main.services.whatsapp import queue_whatsapp_confirmation
                send_clinic_admin_alert(instance, 'contact')
                queue_whatsapp_confirmation(instance.name, getattr(instance, 'phone', None), 'contact', instance.id)
                queue_email_confirmation(instance.name, instance.email, 'contact', instance.id)
                messages.success(request, 'Thank you! Your message has been sent to our clinical desk. We will get back to you shortly.')
            else:
                messages.error(request, 'There was an error sending your message. Please check the fields and try again.')
            return redirect('main:home')

    doctors_qs = Doctor.objects.filter(is_active=True)[:4]
    latest_posts = Post.objects.filter(is_published=True).order_by('-published_date')[:3]
    services = Service.objects.filter(is_active=True).order_by('order')
    from .models import PricingCategory, PricingItem
    pricing_categories = PricingCategory.objects.prefetch_related('items').order_by('order')
    pricing_items = PricingItem.objects.select_related('category').order_by('category__order', 'order')
    from media_center.models import Video
        
    latest_videos = Video.objects.filter(is_published=True).order_by('-published_date')[:12]
    
    from .models import ClinicGallery
    clinic_gallery_images = ClinicGallery.objects.all()

    google_business = GoogleBusiness.objects.order_by('-last_synced', '-updated_at').first()
    google_reviews = []
    google_reviews_schema = None

    if google_business:
        google_reviews = list(
            GoogleReview.objects.filter(business=google_business, is_active=True)
            .order_by('-publish_time', '-created_at')[:10]
        )
        google_reviews_schema = build_google_reviews_schema(request, google_business, google_reviews)
    
    testimonials = Testimonial.objects.filter(is_active=True)

    context = {
        'doctors': doctors_qs,
        'latest_posts': latest_posts,
        'services': services,
        'pricing_items': pricing_items,
        'pricing_categories': pricing_categories,
        'latest_videos': latest_videos,
        'google_business': google_business,
        'google_reviews': google_reviews,
        'google_reviews_schema': google_reviews_schema,
        'clinic_gallery_images': clinic_gallery_images,
        'testimonials': testimonials,
    }
    return render(request, 'home.html', context)


def build_google_reviews_schema(request, business, reviews):
    logo_url = request.build_absolute_uri(static('main/img/logo.jpg'))
    schema = {
        "@context": "https://schema.org",
        "@type": "Dentist",
        "name": business.business_name,
        "image": logo_url,
        "url": request.build_absolute_uri('/'),
        "telephone": "+977-9807464136",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Pragatinagar Road, Shankhamul-31",
            "addressLocality": "Kathmandu",
            "addressRegion": "Bagmati",
            "addressCountry": "NP",
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": str(business.google_rating),
            "reviewCount": business.review_count,
            "bestRating": "5",
            "worstRating": "1",
        },
    }
    if reviews:
        schema["review"] = [
            {
                "@type": "Review",
                "author": {"@type": "Person", "name": review.author_name},
                "datePublished": review.publish_time.date().isoformat() if review.publish_time else "",
                "reviewBody": review.review_text,
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": review.rating,
                    "bestRating": "5",
                    "worstRating": "1",
                },
            }
            for review in reviews[:5]
            if review.review_text
        ]
    return json.dumps(schema, ensure_ascii=False)


# ── About Section ─────────────────────────────────────────────
def about_us(request):
    context = {
        'settings': AboutPageSettings.objects.first(),
        'branches': Branch.objects.all(),
        'core_values': CoreValue.objects.all(),
        'technologies': Technology.objects.all(),
        'testimonials': Testimonial.objects.filter(is_active=True),
        'gallery': ClinicGallery.objects.all()[:6],
        'faqs': FAQ.objects.filter(is_active=True),
        'doctors': Doctor.objects.filter(is_active=True),
        'services': Service.objects.all()
    }
    return render(request, 'about/about_us.html', context)


def our_clinic(request):
    return render(request, 'about/our_clinic.html')


def doctors(request):
    doctors_qs = Doctor.objects.filter(is_active=True)
    return render(request, 'about/doctors.html', {'doctors': doctors_qs})


def why_choose(request):
    return render(request, 'about/why_choose.html')


def about(request):
    return about_us(request)


# ── Gallery Section ───────────────────────────────────────────
def clinic_gallery(request):
    from main.models import ClinicGallery
    gallery_images = ClinicGallery.objects.all()
    return render(request, 'gallery/clinic_gallery.html', {'gallery_images': gallery_images})


def smile_transformations(request):
    testimonials = Testimonial.objects.filter(is_active=True)
    return render(request, 'gallery/smile_transformations.html', {'testimonials': testimonials})


# ── Services Section ──────────────────────────────────────────
from django.shortcuts import get_object_or_404
from django.http import Http404

def services_list(request):
    services = Service.objects.filter(is_active=True).order_by('order')
    return render(request, 'services/services_list.html', {'services': services})


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, is_active=True)
    related_services = Service.objects.filter(is_active=True).exclude(id=service.id).order_by('?')[:3]
    
    from media_center.models import Video
    related_videos = Video.objects.filter(is_published=True, related_service=service).order_by('-published_date')[:3]
    
    context = {
        'service': service,
        'related_services': related_services,
        'related_videos': related_videos,
    }
    
    if service.custom_template:
        return render(request, service.custom_template, context)
    
    return render(request, 'services/generic_service_detail.html', context)

# ── Pricing Section ───────────────────────────────────────────
def pricing(request):
    categories = PricingCategory.objects.prefetch_related('items').order_by('order')
    return render(request, 'pricing.html', {'categories': categories})

# ── Contact Section ───────────────────────────────────────────
def contact(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'appointment':
            form = AppointmentForm(request.POST)
            if form.is_valid():
                instance = form.save()
                from main.services.email import send_clinic_admin_alert, queue_email_confirmation
                from main.services.whatsapp import queue_whatsapp_confirmation
                send_clinic_admin_alert(instance, 'appointment')
                queue_whatsapp_confirmation(instance.full_name, instance.phone, 'appointment', instance.id)
                details = {
                    'appointment_number': instance.appointment_number or f"CF-{instance.id:06d}",
                    'preferred_date': str(instance.preferred_date),
                    'preferred_time': instance.get_preferred_time_display() or 'Flexible',
                    'treatment': instance.service.title if getattr(instance, 'service', None) else (instance.get_treatment_display() if hasattr(instance, 'get_treatment_display') else 'General Consultation'),
                    'doctor': instance.doctor.name if getattr(instance, 'doctor', None) else 'CareFirst Clinical Team',
                }
                queue_email_confirmation(instance.full_name, instance.email, 'appointment', instance.id, details=details)
                return redirect('appointments:confirmation', appointment_number=instance.appointment_number)
            else:
                messages.error(request, 'There was an error in your appointment request. Please check the fields and try again.')
        elif form_type == 'contact':
            form = ContactMessageForm(request.POST)
            if form.is_valid():
                instance = form.save()
                from main.services.email import send_clinic_admin_alert, queue_email_confirmation
                from main.services.whatsapp import queue_whatsapp_confirmation
                send_clinic_admin_alert(instance, 'contact')
                queue_whatsapp_confirmation(instance.name, getattr(instance, 'phone', None), 'contact', instance.id)
                queue_email_confirmation(instance.name, instance.email, 'contact', instance.id)
                messages.success(request, 'Thank you! Your request has been received. We will contact you soon.')
                return redirect('main:contact')
            else:
                messages.error(request, 'There was an error sending your message. Please check the fields and try again.')
    return render(request, 'contact.html')
