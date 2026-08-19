from django import template
from django.utils.translation import get_language
from main.services.translation_service import translate_to_nepali

register = template.Library()

@register.filter(name='to_nepali')
def to_nepali_filter(value):
    """
    Translates text to Nepali if current language is 'ne', otherwise returns original.
    Usage: {{ service.title|to_nepali }}
    """
    if not value:
        return value
    
    current_lang = get_language()
    if current_lang == 'ne':
        return translate_to_nepali(str(value))
    return value

@register.simple_tag(takes_context=True)
def trans_ne(context, text):
    """
    Template tag to dynamically translate a string if language is Nepali.
    Usage: {% trans_ne "Request a consultation" %}
    """
    current_lang = context.get('request').LANGUAGE_CODE if 'request' in context else get_language()
    if current_lang == 'ne':
        return translate_to_nepali(text)
    return text
