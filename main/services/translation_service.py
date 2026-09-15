import logging
import os
import re
from functools import lru_cache
from typing import Optional, Dict, List
from deep_translator import GoogleTranslator, MyMemoryTranslator
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
    "5 min read": "५ मिनेटको पढाइ",
    "6 min read": "६ मिनेटको पढाइ",
    "7 min read": "७ मिनेटको पढाइ",
    "8 min read": "८ मिनेटको पढाइ",
    "10 min read": "१० मिनेटको पढाइ",
}


class TranslationService:
    """
    High-performance translation service powered by Deep Translator.
    Features:
    - In-memory glossary priority
    - Redis / Django caching
    - Primary Google Translator engine
    - Automatic secondary fallback to MyMemory Translator
    - Smart HTML and multi-paragraph chunking
    """

    def __init__(self, source: str = 'en', target: str = 'ne'):
        self.source = source
        self.target = target
        try:
            self._google_translator = GoogleTranslator(source=source, target=target)
        except Exception:
            self._google_translator = None

        try:
            self._mymemory_translator = MyMemoryTranslator(source='en-US', target='ne-NP')
        except Exception:
            self._mymemory_translator = None

    def _translate_raw_chunk(self, chunk: str) -> str:
        """Helper to translate a single chunk (<1500 chars) with fallback and caching."""
        clean = chunk.strip()
        if not clean:
            return chunk

        if clean in DENTAL_NEPALI_GLOSSARY:
            return DENTAL_NEPALI_GLOSSARY[clean]

        cache_key = f"dt_trans_{self.source}_{self.target}_{hash(clean)}"
        try:
            cached = cache.get(cache_key)
            if cached:
                return cached
        except Exception:
            pass

        # Attempt 1: Google Translator
        try:
            if not self._google_translator:
                self._google_translator = GoogleTranslator(source=self.source, target=self.target)
            translated = self._google_translator.translate(clean)
            if translated and translated.strip():
                try:
                    cache.set(cache_key, translated, timeout=86400 * 30)
                except Exception:
                    pass
                return translated
        except Exception as e:
            logger.warning(f"GoogleTranslator rate-limited/failed for '{clean[:40]}...': {e}. Trying fallback...")

        # Attempt 2: MyMemory Translator Fallback
        try:
            if not self._mymemory_translator:
                self._mymemory_translator = MyMemoryTranslator(source='en-US', target='ne-NP')
            translated = self._mymemory_translator.translate(clean)
            if translated and translated.strip() and not translated.startswith("MYMEMORY WARNING"):
                try:
                    cache.set(cache_key, translated, timeout=86400 * 30)
                except Exception:
                    pass
                return translated
        except Exception as e:
            logger.error(f"MyMemoryTranslator fallback also failed for '{clean[:40]}...': {e}")

        # Fallback to original text if both services fail
        return chunk

    def translate(self, text: str) -> str:
        """
        Translates a given string into Nepali.
        Handles short strings, long articles, and HTML content transparently.
        """
        if not text or not isinstance(text, str):
            return text

        clean_text = text.strip()
        if not clean_text:
            return text

        # 1. Exact Glossary Match
        if clean_text in DENTAL_NEPALI_GLOSSARY:
            return DENTAL_NEPALI_GLOSSARY[clean_text]

        # 2. Short string (<1500 chars, no HTML tags)
        if len(clean_text) <= 1500 and not ('<' in clean_text and '>' in clean_text):
            return self._translate_raw_chunk(clean_text)

        # 3. HTML / Multi-paragraph text chunking
        if '<p>' in clean_text or '<h3>' in clean_text or '<div>' in clean_text or '<br>' in clean_text:
            parts = re.split(r'(</?(?:p|h[1-6]|div|li|ul|ol|blockquote|section|br\s*/?|hr\s*/?)>)', clean_text)
            translated_parts = []
            for part in parts:
                if part.startswith('<') and part.endswith('>'):
                    translated_parts.append(part)
                elif part.strip():
                    translated_parts.append(self._translate_raw_chunk(part))
                else:
                    translated_parts.append(part)
            return "".join(translated_parts)

        # 4. Long plain text: split by double newlines
        paragraphs = clean_text.split('\n\n')
        translated_paragraphs = [self._translate_raw_chunk(p) for p in paragraphs]
        return '\n\n'.join(translated_paragraphs)


# Global instance
nepali_translator = TranslationService(source='en', target='ne')


def translate_to_nepali(text: str) -> str:
    """Convenience helper function"""
    return nepali_translator.translate(text)
