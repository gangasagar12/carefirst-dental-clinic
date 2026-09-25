from django.db.models.signals import pre_save
from django.db.backends.signals import connection_created
from django.dispatch import receiver
from modeltranslation.translator import translator
import logging
from main.services.translation_service import translate_to_nepali

logger = logging.getLogger(__name__)


@receiver(connection_created)
def configure_sqlite_wal(sender, connection, **kwargs):
    """
    Enables Write-Ahead Logging (WAL) and 60-second busy timeout for SQLite
    to prevent 'database is locked' errors under concurrent web server traffic.
    """
    if connection.vendor == 'sqlite':
        try:
            with connection.cursor() as cursor:
                cursor.execute('PRAGMA journal_mode = WAL;')
                cursor.execute('PRAGMA busy_timeout = 60000;')
                cursor.execute('PRAGMA synchronous = NORMAL;')
        except Exception:
            pass



@receiver(pre_save)
def auto_translate_fields(sender, instance, **kwargs):
    """
    Automatically translates registered model fields into Nepali if English is provided
    and the Nepali translation field is left blank.
    """
    try:
        registered_models = translator.get_registered_models()
        if sender not in registered_models:
            return

        opts = translator.get_options_for_model(sender)
        
        for field in opts.fields:
            en_field = f"{field}_en"
            ne_field = f"{field}_ne"
            
            # 1. Retrieve the source text (check en_field first, then fallback to base field)
            en_val = getattr(instance, en_field, None)
            if not en_val:
                en_val = getattr(instance, field, None)
            
            # If English value exists, ensure en_field is explicitly set
            if en_val and hasattr(instance, en_field) and not getattr(instance, en_field, None):
                setattr(instance, en_field, en_val)

            # 2. Check if Nepali translation is already provided
            ne_val = getattr(instance, ne_field, None) if hasattr(instance, ne_field) else None
            
            # 3. If English has text and Nepali is empty/blank, auto-translate
            if en_val and isinstance(en_val, str) and en_val.strip() and (not ne_val or not str(ne_val).strip()):
                try:
                    translated_text = translate_to_nepali(en_val)
                    if translated_text and translated_text.strip():
                        setattr(instance, ne_field, translated_text)
                except Exception as e:
                    logger.error(f"Failed to auto-translate {field} for {sender.__name__}: {e}")

    except Exception as e:
        logger.error(f"Error in auto_translate_fields signal for {sender.__name__}: {e}")
