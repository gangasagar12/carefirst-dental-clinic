from modeltranslation.translator import register, TranslationOptions
from .models import LoyaltyProgram

@register(LoyaltyProgram)
class LoyaltyProgramTranslationOptions(TranslationOptions):
    fields = ('name', 'tagline', 'description')
