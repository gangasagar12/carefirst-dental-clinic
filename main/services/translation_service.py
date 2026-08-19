import logging
import os
from functools import lru_cache
from typing import Optional, Dict
from deep_translator import GoogleTranslator
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Pre-compiled high-accuracy dental and medical Nepali dictionary
DENTAL_NEPALI_GLOSSARY: Dict[str, str] = {
    "CareFirst Dental Clinic": "केयरफर्स्ट डेन्टल क्लिनिक",
    "Carefirst Dental Clinic": "केयरफर्स्ट डेन्टल क्लिनिक",
    "CareFirst": "केयरफर्स्ट",
    "Carefirst": "केयरफर्स्ट",
    "Home": "गृहपृष्ठ",
    "About Us": "हाम्रो बारेमा",
    "Services": "दन्त सेवाहरू",
    "Treatments": "उपचारहरू",
    "Our Doctors": "हाम्रा डाक्टरहरू",
    "Doctors": "डाक्टरहरू",
    "Smile Gallery": "स्माइल ग्यालरी",
    "Video": "भिडियो",
    "Videos": "भिडियोहरू",
    "Pricing": "मूल्य विवरण",
    "Blog": "ब्लग तथा जानकारी",
    "Contact": "सम्पर्क",
    "Contact Us": "सम्पर्क गर्नुहोस्",
    "Book Appointment": "अपोइन्टमेन्ट लिनुहोस्",
    "Book an Appointment": "दन्त परामर्शको लागि समय लिनुहोस्",
    "Schedule Your Smile Visit": "तपाईंको दाँत परीक्षणको लागि समय तय गर्नुहोस्",
    "Root Canal Treatment": "रूट क्यानल उपचार (RCT)",
    "Root Canal Treatment (RCT)": "रूट क्यानल उपचार (RCT)",
    "Dental Implants": "डेन्टल इम्प्लान्ट (दाँत प्रत्यारोपण)",
    "Teeth Whitening": "दाँत चम्काउने (ह्वाइटनिङ)",
    "Orthodontics & Braces": "तार बाँध्ने (अर्थोडोन्टिक्स / ब्रेसेस)",
    "Tooth Extraction": "दाँत निकाल्ने सेवा",
    "Tooth Fillings & Restoration": "दाँत भर्ने तथा पुनर्स्थापना",
    "General Dental Check-up": "साधारण दन्त परीक्षण",
    "Pediatric Dentistry": "बाल दन्त चिकित्सा",
    "Periodontal Treatment": "गिजाको उपचार",
    "Scaling & Polishing": "दाँत सफा गर्ने (स्केलिङ र पोलिसिङ)",
    "Dentures": "नक्कली दाँत (डेन्चर)",
    "Crowns & Bridges": "दाँतको क्याप तथा ब्रिज",
    "Your Name": "तपाईंको नाम",
    "Your Email Address": "तपाईंको इमेल ठेगाना",
    "Contact Number": "सम्पर्क फोन नम्बर",
    "Appointment date": "अपोइन्टमेन्ट मिति",
    "Preferred Time": "रोजेको समय",
    "Treatment / Service": "दन्त सेवा / उपचार",
    "Message": "सन्देश",
    "Your Message": "तपाईंको सन्देश",
    "Book Appointment Now": "अहिले नै अपोइन्टमेन्ट बुक गर्नुहोस्",
    "Send Message Now": "सन्देश पठाउनुहोस्",
    "Send Message": "सन्देश पठाउनुहोस्",
    "Read Article": "पूरा लेख पढ्नुहोस्",
    "View All Articles": "सबै लेखहरू हेर्नुहोस्",
    "Oral Health Tips & Guides": "दन्त स्वास्थ्य सुझाव तथा जानकारी",
    "Announcements": "सूचना तथा समाचार",
    "Need dental help?": "दन्त सल्लाह चाहिन्छ?",
    "Online": "अनलाइन",
    "NMC Certified": "एनएमसी (NMC) प्रमाणित",
    "NMC Verified Doctors": "प्रमाणित विशेषज्ञ दन्त चिकित्सक",
    "Open Daily": "दैनिक खुला",
    "Open Daily (Mon–Sun): 7:30 AM – 7:30 PM": "दैनिक खुला (सोम–आइत): बिहान ७:३० देखि साँझ ७:३० सम्म",
    "Pragatinagar Road, Shankhamul-31, Kathmandu (Shankhamul / New Baneshwor)": "प्रगतिनगर मार्ग, शंखमूल-३१, काठमाडौँ (शंखमूल / नयाँ बानेश्वर)",
}


class TranslationService:
    """
    High-performance translation service powered by Deep Translator.
    Features in-memory dictionary priority, Redis/Django caching, and automatic fallback.
    """

    def __init__(self, source: str = 'en', target: str = 'ne'):
        self.source = source
        self.target = target
        try:
            self._translator = GoogleTranslator(source=source, target=target)
        except Exception as e:
            logger.warning(f"DeepTranslator initialization warning: {e}")
            self._translator = None

    def translate(self, text: str) -> str:
        """
        Translates a given string into Nepali.
        Checks glossary first, then Django cache, then calls Deep Translator.
        """
        if not text or not isinstance(text, str):
            return text

        clean_text = text.strip()
        if not clean_text:
            return text

        # 1. Exact Glossary Match
        if clean_text in DENTAL_NEPALI_GLOSSARY:
            return DENTAL_NEPALI_GLOSSARY[clean_text]

        # 2. Cache Lookup
        cache_key = f"dt_trans_{self.source}_{self.target}_{hash(clean_text)}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # 3. Deep Translator API call
        try:
            if not self._translator:
                self._translator = GoogleTranslator(source=self.source, target=self.target)
            
            translated = self._translator.translate(clean_text)
            if translated:
                cache.set(cache_key, translated, timeout=86400 * 30)  # Cache for 30 days
                return translated
        except Exception as e:
            logger.error(f"DeepTranslator translation error for '{clean_text}': {e}")

        # Fallback to original text if translation fails
        return text


# Global instance
nepali_translator = TranslationService(source='en', target='ne')


def translate_to_nepali(text: str) -> str:
    """Convenience helper function"""
    return nepali_translator.translate(text)
