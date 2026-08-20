from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime

class Service(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('preventive', 'Preventive'),
        ('restorative', 'Restorative'),
        ('cosmetic', 'Cosmetic'),
        ('orthodontics', 'Orthodontics'),
        ('implants', 'Implants'),
        ('diagnostics', 'Diagnostics'),
        ('endodontics', 'Endodontics'),
        ('oral-surgery', 'Oral Surgery'),
        ('prosthodontics', 'Prosthodontics'),
        ('periodontal', 'Periodontal Care'),
    ]

    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    category_label = models.CharField(max_length=50, help_text="e.g. GENERAL CARE")
    icon = models.CharField(max_length=50, help_text="Bootstrap icon class, e.g. bi-tooth")
    image = models.ImageField(upload_to='services/', blank=True, null=True, help_text="Image for the service card")
    is_popular = models.BooleanField(default=False)
    features = models.TextField(help_text="One feature per line (for the checkmark list)", blank=True)
    starting_price = models.CharField(max_length=50, help_text="e.g. 1,000", blank=True)
    
    # Detail Page Fields
    custom_template = models.CharField(max_length=200, blank=True, null=True, help_text="e.g. services/dental_implants.html. If blank, generic template is used.")
    detail_content = models.TextField(blank=True, help_text="Content for the generic service detail page")
    detail_image = models.ImageField(upload_to='services/details/', blank=True, null=True, help_text="Hero image for the generic detail page")

    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    
    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True, help_text="SEO Title (defaults to service title if blank)")
    meta_description = models.TextField(blank=True, help_text="SEO Meta Description")

    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_features_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]

    def get_dynamic_price(self):
        """
        Dynamically retrieves the latest price from PricingCategory and PricingItem.
        When pricing items are edited/updated on the pricing page, service cards
        automatically reflect the new rates.
        """
        try:
            # 1. Direct Category Match
            cat = PricingCategory.objects.filter(name__iexact=self.title).first()
            if not cat:
                for c in PricingCategory.objects.all():
                    if c.name.lower() in self.title.lower() or self.title.lower() in c.name.lower():
                        cat = c
                        break
            
            if cat:
                first_item = cat.items.order_by('order', 'id').first()
                if first_item and first_item.price:
                    return first_item.price

            # 2. Direct Item Match
            item = PricingItem.objects.filter(name__icontains=self.title).first()
            if item and item.price:
                return item.price
        except Exception:
            pass

        return self.starting_price or "1,000"

class Doctor(models.Model):
    SPECIALTY_CHOICES = [
        ('general', 'General Dentistry'),
        ('cosmetic', 'Cosmetic Dentistry'),
        ('orthodontics', 'Orthodontics'),
        ('implants', 'Dental Implants'),
        ('endodontics', 'Endodontics / Root Canal'),
        ('pediatric', 'Pediatric Dentistry'),
        ('oral_surgery', 'Oral Surgery'),
        ('periodontics', 'Periodontics'),
    ]

    name = models.CharField(max_length=120)
    designation = models.CharField(max_length=120, help_text="e.g. Chief Dental Surgeon")
    specialty = models.CharField(max_length=50, choices=SPECIALTY_CHOICES, default='general')
    photo = models.ImageField(upload_to='doctors/', blank=True, null=True)
    bio = models.TextField(blank=True)
    qualifications = models.CharField(max_length=255, help_text="e.g. BDS, MDS, FICOI", blank=True)
    nmc_number = models.CharField(max_length=50, blank=True, null=True, help_text="Nepal Medical Council Number (e.g. 31229)")
    experience_years = models.PositiveSmallIntegerField(default=0)
    certifications = models.TextField(blank=True, help_text="One per line")
    languages = models.CharField(max_length=120, blank=True, help_text="e.g. English, Nepali, Hindi")
    email = models.EmailField(blank=True)
    linkedin = models.URLField(blank=True)
    order = models.PositiveSmallIntegerField(default=0, help_text="Display order (lower = first)")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"

    def __str__(self):
        return f"Dr. {self.name} — {self.get_specialty_display()}"

    def get_certifications_list(self):
        """Returns certifications as a Python list."""
        return [c.strip() for c in self.certifications.splitlines() if c.strip()]

    def photo_url(self):
        if self.photo:
            return self.photo.url
        return None

class PricingCategory(models.Model):
    name = models.CharField(max_length=150)
    order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Pricing Category"
        verbose_name_plural = "Pricing Categories"

    def __str__(self):
        return self.name

class PricingItem(models.Model):
    category = models.ForeignKey(PricingCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    price = models.CharField(max_length=100, help_text="e.g. 1,000 - 2,500")
    order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Pricing Item"
        verbose_name_plural = "Pricing Items"

    def __str__(self):
        return self.name

from django.utils import timezone

class SpecialOffer(models.Model):
    title = models.CharField(max_length=200, help_text="e.g. Dashain Mega Offer (Used for admin and Top Bar)")
    description = models.TextField(help_text="Short description of the offer (Used for Top Bar)")
    highlight_text = models.CharField(max_length=50, blank=True, help_text="e.g. 20% OFF")
    sub_text = models.CharField(max_length=150, blank=True, help_text="e.g. ON TEETH WHITENING & SCALING")
    badge_text = models.CharField(max_length=50, blank=True, help_text="e.g. SPECIAL DASHAIN OFFER")
    features = models.TextField(blank=True, help_text="Format: Title | Description (one per line). e.g. Safe & Painless | Advanced tech with gentle techniques.")
    image = models.ImageField(upload_to='offers/', blank=True, null=True, help_text="Promotional banner image for the popup right side")
    start_date = models.DateTimeField(help_text="When the offer should start appearing")
    end_date = models.DateTimeField(help_text="When the offer should stop appearing")
    is_active = models.BooleanField(default=True, help_text="Uncheck to instantly hide the offer regardless of dates")
    button_text = models.CharField(max_length=50, default="Book Appointment Now")
    button_link = models.CharField(max_length=200, default="/contact/#book")

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Special Offer"
        verbose_name_plural = "Special Offers"

    def __str__(self):
        return self.title

    def is_currently_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def get_features_list(self):
        """Returns a list of dictionaries with title and desc from the features field."""
        result = []
        if self.features:
            lines = self.features.splitlines()
            for line in lines:
                parts = line.split('|', 1)
                if len(parts) == 2:
                    result.append({'title': parts[0].strip(), 'desc': parts[1].strip()})
                elif len(parts) == 1 and parts[0].strip():
                    result.append({'title': parts[0].strip(), 'desc': ''})
        return result

# ── About Page Models ──────────────────────────────────────────

class AboutPageSettings(models.Model):
    # Hero
    hero_title = models.CharField(max_length=200, default="Caring for Every Smile with Excellence, Compassion & Innovation")
    hero_subtitle = models.TextField(default="Carefirst Dental Clinic as a modern multi-specialty dental clinic dedicated to providing advanced, ethical, and patient-centered dental care across Nepal.")
    hero_image = models.ImageField(upload_to='about/', blank=True, null=True)
    # Story
    story_title = models.CharField(max_length=200, default="Our Story")
    story_content = models.TextField()
    story_image = models.ImageField(upload_to='about/', blank=True, null=True)
    # Stats
    stats_years = models.CharField(max_length=50, default="2+ Years of Service")
    stats_patients = models.CharField(max_length=50, default="10,000+ Happy Patients")
    stats_treatments = models.CharField(max_length=50, default="25,000+ Successful Treatments")
    stats_rating = models.CharField(max_length=50, default="4.9★ Patient Rating")
    # Mission & Vision
    mission_content = models.TextField()
    vision_content = models.TextField()
    # CTA
    cta_title = models.CharField(max_length=200, default="Ready to Transform Your Smile?")
    cta_content = models.TextField(default="Book your appointment today and experience advanced, comfortable, and personalized dental care at Carefirst Dental Clinic.")
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)

    class Meta:
        verbose_name = "About Page Settings"
        verbose_name_plural = "About Page Settings"

    def __str__(self):
        return "About Page Settings"

class Branch(models.Model):
    name = models.CharField(max_length=150, help_text="e.g. Koteshwor Branch")
    location = models.CharField(max_length=200, help_text="e.g. Koteshwor, Kathmandu")
    image = models.ImageField(upload_to='branches/', blank=True, null=True)
    short_description = models.TextField(blank=True)
    map_url = models.URLField(blank=True)
    contact_url = models.URLField(blank=True)
    services_list = models.TextField(help_text="One service per line")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Branch"
        verbose_name_plural = "Branches"

    def __str__(self):
        return self.name

    def get_services(self):
        return [s.strip() for s in self.services_list.splitlines() if s.strip()]

class CoreValue(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Bootstrap icon class, e.g. bi-heart-pulse")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Technology(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class, e.g. bi-cpu")
    image = models.ImageField(upload_to='tech/', blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Technologies"

    def __str__(self):
        return self.title

class Testimonial(models.Model):
    TAG_COLOR_CHOICES = [
        ('default', 'Teal (Standard)'),
        ('cosmetic', 'Purple (Cosmetic)'),
        ('whitening', 'Sky Blue (Whitening)'),
        ('implant', 'Emerald (Implants)'),
    ]

    patient_name = models.CharField(max_length=150)
    treatment = models.CharField(max_length=150, blank=True)
    headline = models.CharField(max_length=255, blank=True, help_text="Editorial story headline (e.g. A confident smile, restored.)")
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True, help_text="Patient portrait or clinical transformation image")
    review = models.TextField(help_text="Patient quote or story excerpt")
    initial_concern = models.TextField(blank=True, help_text="Patient's initial dental concern/problem")
    clinical_journey = models.TextField(blank=True, help_text="Procedure performed by Dr. Subash Banjade and clinical team")
    outcome = models.TextField(blank=True, help_text="Final aesthetic and clinical outcome")
    tag_color = models.CharField(max_length=50, choices=TAG_COLOR_CHOICES, default='default', help_text="Badge color styling")
    rating = models.PositiveSmallIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']
        verbose_name = "Patient Story / Testimonial"
        verbose_name_plural = "Patient Stories & Testimonials"

    def __str__(self):
        return f"{self.patient_name} — {self.treatment or 'Patient Story'}"

    def get_headline(self):
        if self.headline:
            return self.headline
        return f"A healthier, radiant smile restored."

    def get_concern(self):
        if self.initial_concern:
            return self.initial_concern
        return f"Patient sought expert clinical care for {self.treatment or 'dental rehabilitation'} to regain comfort and oral health."

    def get_journey(self):
        if self.clinical_journey:
            return self.clinical_journey
        return f"Comprehensive digital evaluation followed by painless, state-of-the-art procedure performed by Dr. Subash Banjade (BDS, NMC #31229)."

    def get_outcome(self):
        if self.outcome:
            return self.outcome
        return f"Successful functional restoration and harmonious natural aesthetics achieved."

    def get_image_url(self):
        if self.photo:
            try:
                return self.photo.url
            except Exception:
                pass
        t_lower = (self.treatment or '').lower()
        if 'implant' in t_lower:
            return '/static/main/img/clinic/implants_story.jpg'
        elif 'whiten' in t_lower:
            return '/static/main/img/clinic/whitening_story.jpg'
        elif 'veneer' in t_lower or 'makeover' in t_lower or 'rehab' in t_lower:
            return '/static/main/img/clinic/smile_makeover_story.jpg'
        return '/static/images/hero_section1.jpeg'


class ClinicGallery(models.Model):
    image = models.ImageField(upload_to='clinic_gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Clinic Gallery Images"

    def __str__(self):
        return self.caption or f"Gallery Image {self.id}"

class HeroSlide(models.Model):
    title = models.CharField(max_length=200, blank=True, help_text="e.g. Modern Operatory & Care")
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='hero_slides/', help_text="High-resolution banner image")
    order = models.PositiveSmallIntegerField(default=0, help_text="Lower number appears first")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Hero Slide"
        verbose_name_plural = "Hero Slides"

    def __str__(self):
        return self.title or f"Slide #{self.id}"

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question

class SEOFAQCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "SEO FAQ Categories"

    def __str__(self):
        return self.name

class SEOFAQ(models.Model):
    category = models.ForeignKey(SEOFAQCategory, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=500)
    answer = models.TextField()
    primary_keyword = models.CharField(max_length=200, blank=True)
    secondary_keywords = models.TextField(blank=True, help_text="Comma separated")
    search_intent = models.CharField(max_length=100, blank=True, choices=[
        ('Informational', 'Informational'),
        ('Commercial', 'Commercial'),
        ('Transactional', 'Transactional'),
        ('Local', 'Local'),
    ])
    suggested_internal_links = models.TextField(blank=True)
    related_services = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "SEO FAQ"
        verbose_name_plural = "SEO FAQs"

    def __str__(self):
        return self.question

class SiteSettings(models.Model):
    # Contact Details
    primary_phone = models.CharField(max_length=50, default="980-7464136")
    secondary_phone = models.CharField(max_length=50, blank=True, default="01-5916886")
    whatsapp_number = models.CharField(max_length=50, default="9779807464136", help_text="Number with country code for WhatsApp link (e.g. 9779807464136)")
    email = models.EmailField(default="carefirstdentalclinic@gmail.com")
    
    # Address
    address = models.CharField(max_length=200, default="Pragatinagar Road, Shankhamul-31, Kathmandu 44600")
    landmark = models.TextField(default="Shankhamul / New Baneshwor area")
    google_maps_iframe_url = models.URLField(max_length=1000, blank=True, help_text="The 'src' URL from Google Maps Embed iframe")
    
    # Social Media
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    
    # Other Settings
    working_hours_weekdays = models.CharField(max_length=100, default="Mon - Sun: 7:30 AM - 7:30 PM")
    working_hours_weekend = models.CharField(max_length=100, default="Mon - Sun: 7:30 AM - 7:30 PM")

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Global Site Settings"

class ContactMessage(models.Model):
    name = models.CharField(max_length=200, verbose_name="Name")
    email = models.EmailField(verbose_name="Email Address")
    subject = models.CharField(max_length=200, blank=True, verbose_name="Subject")
    message = models.TextField(verbose_name="Message")
    is_read = models.BooleanField(default=False, verbose_name="Is Read")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.name} - {self.subject}"


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Password Reset OTP'
        verbose_name_plural = 'Password Reset OTPs'
        ordering = ['-created_at']

    def is_valid(self):
        # OTP is valid for 10 minutes
        expiration_time = self.created_at + datetime.timedelta(minutes=10)
        return not self.is_used and timezone.now() <= expiration_time

    def __str__(self):
        return f'{self.user.username} - {self.otp}'


class GoogleBusiness(models.Model):
    place_id = models.CharField(max_length=255, unique=True)
    business_name = models.CharField(max_length=255)
    google_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    last_synced = models.DateTimeField(blank=True, null=True)
    sync_status = models.CharField(max_length=30, default='Never synced')
    sync_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Google Business"
        verbose_name_plural = "Google Business"

    def __str__(self):
        return self.business_name or self.place_id


class GoogleReview(models.Model):
    business = models.ForeignKey(GoogleBusiness, on_delete=models.CASCADE, related_name='reviews')
    google_review_id = models.CharField(max_length=255, unique=True)
    author_name = models.CharField(max_length=255)
    author_photo = models.URLField(max_length=1000, blank=True)
    author_url = models.URLField(max_length=1000, blank=True)
    rating = models.PositiveSmallIntegerField(default=5)
    review_text = models.TextField(blank=True)
    relative_time = models.CharField(max_length=100, blank=True)
    publish_time = models.DateTimeField(blank=True, null=True)
    language = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-publish_time', '-created_at']
        verbose_name = "Google Review"
        verbose_name_plural = "Google Reviews"

    def __str__(self):
        return f"{self.author_name} - {self.rating} stars"


# Invalidate google reviews context cache on updates
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

@receiver([post_save, post_delete], sender=GoogleBusiness)
@receiver([post_save, post_delete], sender=GoogleReview)
@receiver([post_save, post_delete], sender=Testimonial)
def clear_reviews_context_cache(sender, **kwargs):
    cache.delete('google_reviews_context_data')

