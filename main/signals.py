from django.db.models.signals import pre_save
from django.dispatch import receiver
from modeltranslation.translator import translator
import logging

logger = logging.getLogger(__name__)

# List of all registered translation models
translated_models = translator.get_registered_models()

@receiver(pre_save)
def auto_translate_fields(sender, instance, **kwargs):
    # Only run for models that have translation options registered
    if sender not in translated_models:
        return

    try:
        try:
            from deep_translator import GoogleTranslator
        except ImportError:
            return

        opts = translator.get_options_for_model(sender)
        gt = GoogleTranslator(source='en', target='ne')
        
        for field in opts.fields:
            en_field = f"{field}_en"
            ne_field = f"{field}_ne"
            
            if hasattr(instance, en_field) and hasattr(instance, ne_field):
                en_val = getattr(instance, en_field)
                ne_val = getattr(instance, ne_field)
                
                # If English has a value and Nepali is empty, translate it
                if en_val and isinstance(en_val, str) and not ne_val:
                    try:
                        translated_text = gt.translate(en_val)
                        if translated_text:
                            setattr(instance, ne_field, translated_text)
                    except Exception as e:
                        logger.error(f"Failed to auto-translate {field} for {sender.__name__}: {e}")
                        
    except Exception as e:
        logger.error(f"Error in auto_translate_fields signal for {sender.__name__}: {e}")
