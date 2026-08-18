from django import forms
from appointments.models import Appointment
from main.models import Service, Doctor, PricingCategory, PricingItem, SpecialOffer, Testimonial, SiteSettings, ContactMessage, HeroSlide, ClinicGallery
from media_center.models import Video


class BootstrapFormMixin:
    """Helper mixin to apply modern bootstrap form styling to all fields."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = widget.attrs.get('class', '') + ' form-check-input'
            elif isinstance(widget, forms.RadioSelect):
                widget.attrs['class'] = widget.attrs.get('class', '') + ' form-check-input'
            elif isinstance(widget, forms.Select):
                widget.attrs['class'] = widget.attrs.get('class', '') + ' form-select'
            elif isinstance(widget, forms.FileInput):
                widget.attrs['class'] = widget.attrs.get('class', '') + ' form-control'
            else:
                widget.attrs['class'] = widget.attrs.get('class', '') + ' form-control'


class AppointmentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'full_name', 'phone', 'email', 'appointment_type', 'service',
            'preferred_date', 'preferred_time', 'doctor', 'branch',
            'message', 'status', 'estimated_amount', 'quantity', 'pricing_option'
        ]
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'message': forms.Textarea(attrs={'rows': 3}),
        }


class ServiceForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'title', 'category', 'category_label', 'icon', 'starting_price',
            'image', 'is_popular', 'is_active', 'order', 'features',
            'detail_content', 'detail_image', 'meta_title', 'meta_description'
        ]
        widgets = {
            'features': forms.Textarea(attrs={'rows': 4, 'placeholder': 'One feature per line'}),
            'detail_content': forms.Textarea(attrs={'rows': 6}),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
        }


class DoctorForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            'name', 'designation', 'specialty', 'photo', 'nmc_number',
            'experience_years', 'qualifications', 'languages', 'email',
            'linkedin', 'bio', 'certifications', 'order', 'is_active'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'certifications': forms.Textarea(attrs={'rows': 3, 'placeholder': 'One certification per line'}),
        }


class PricingCategoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PricingCategory
        fields = ['name', 'order']


class PricingItemForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PricingItem
        fields = ['category', 'name', 'price', 'order']


class SpecialOfferForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SpecialOffer
        fields = [
            'title', 'description', 'highlight_text', 'sub_text', 'badge_text',
            'features', 'image', 'start_date', 'end_date', 'is_active',
            'button_text', 'button_link'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'features': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Title | Description (one per line)'}),
        }


class TestimonialForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['patient_name', 'treatment', 'photo', 'review', 'rating', 'order', 'is_active']
        widgets = {
            'review': forms.Textarea(attrs={'rows': 4}),
        }


class VideoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Video
        fields = [
            'title', 'platform', 'video_url', 'video_id', 'embed_code',
            'thumbnail', 'thumbnail_url', 'category', 'related_service',
            'related_branch', 'short_description', 'is_featured', 'is_published', 'order'
        ]
        widgets = {
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'embed_code': forms.Textarea(attrs={'rows': 3}),
        }


class SiteSettingsForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            'primary_phone', 'secondary_phone', 'whatsapp_number', 'email',
            'address', 'landmark', 'working_hours_weekdays', 'working_hours_weekend',
            'google_maps_iframe_url', 'facebook_url', 'instagram_url', 'youtube_url', 'twitter_url'
        ]
        widgets = {
            'landmark': forms.Textarea(attrs={'rows': 2}),
            'google_maps_iframe_url': forms.Textarea(attrs={'rows': 2}),
        }


class HeroSlideForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = HeroSlide
        fields = ['title', 'subtitle', 'image', 'order', 'is_active']


class ClinicGalleryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ClinicGallery
        fields = ['caption', 'image', 'order']
