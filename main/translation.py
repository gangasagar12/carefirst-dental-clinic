from modeltranslation.translator import register, TranslationOptions
from .models import Service, Doctor, PricingCategory, PricingItem, SpecialOffer

@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('title', 'category_label', 'features', 'detail_content')

@register(Doctor)
class DoctorTranslationOptions(TranslationOptions):
    fields = ('designation', 'bio', 'qualifications', 'certifications')

@register(PricingCategory)
class PricingCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(PricingItem)
class PricingItemTranslationOptions(TranslationOptions):
    fields = ('name', 'price')

@register(SpecialOffer)
class SpecialOfferTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'highlight_text', 'sub_text', 'badge_text', 'features', 'button_text')

from .models import AboutPageSettings, Branch, CoreValue, Technology, Testimonial, ClinicGallery, FAQ, SEOFAQCategory, SEOFAQ

@register(AboutPageSettings)
class AboutPageSettingsTranslationOptions(TranslationOptions):
    fields = (
        'hero_title', 'hero_subtitle', 'story_title', 'story_content',
        'stats_years', 'stats_patients', 'stats_treatments', 'stats_rating',
        'mission_content', 'vision_content', 'cta_title', 'cta_content',
        'meta_title', 'meta_description'
    )

@register(Branch)
class BranchTranslationOptions(TranslationOptions):
    fields = ('name', 'location', 'short_description', 'services_list')

@register(CoreValue)
class CoreValueTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(Technology)
class TechnologyTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(Testimonial)
class TestimonialTranslationOptions(TranslationOptions):
    fields = ('patient_name', 'treatment', 'review')

@register(ClinicGallery)
class ClinicGalleryTranslationOptions(TranslationOptions):
    fields = ('caption',)

@register(FAQ)
class FAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')

@register(SEOFAQCategory)
class SEOFAQCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(SEOFAQ)
class SEOFAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')
