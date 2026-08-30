import os
import re
import sys
import time
from pathlib import Path
import polib
from deep_translator import GoogleTranslator

sys.stdout.reconfigure(encoding='utf-8')

CURATED_NEPALI_DICTIONARY = {
    # Core Clinic Info & Navigation
    "CareFirst Dental Clinic": "केयरफर्स्ट डेन्टल क्लिनिक",
    "Carefirst Dental Clinic": "केयरफर्स्ट डेन्टल क्लिनिक",
    "CareFirst Dental": "केयरफर्स्ट डेन्टल",
    "Carefirst Dental": "केयरफर्स्ट डेन्टल",
    "CareFirst": "केयरफर्स्ट",
    "Carefirst": "केयरफर्स्ट",
    "Home": "गृहपृष्ठ",
    "About": "हाम्रो बारेमा",
    "About Us": "हाम्रो बारेमा",
    "Our Clinic": "हाम्रो क्लिनिक",
    "Why Choose Us": "हामीलाई किन रोज्ने?",
    "Why Choose CareFirst": "केयरफर्स्ट किन रोज्ने?",
    "Services": "दन्त सेवाहरू",
    "Treatments": "उपचारहरू",
    "Our Doctors": "हाम्रा चिकित्सकहरू",
    "Doctors": "चिकित्सकहरू",
    "Meet Our Doctors": "हाम्रा चिकित्सकहरूलाई भेट्नुहोस्",
    "Meet the Doctors": "हाम्रा डाक्टरहरूलाई भेट्नुहोस्",
    "Meet All Doctors": "सबै डाक्टरहरू हेर्नुहोस्",
    "Smile Gallery": "स्माइल ग्यालरी",
    "Clinic Gallery": "क्लिनिक ग्यालरी",
    "Video": "भिडियो",
    "Videos": "भिडियोहरू",
    "Pricing": "शुल्क विवरण",
    "Blog": "ब्लग तथा लेख",
    "Contact": "सम्पर्क",
    "Contact Us": "सम्पर्क गर्नुहोस्",
    "Book Appointment": "अपोइन्टमेन्ट लिनुहोस्",
    "Book an Appointment": "दन्त परामर्शको लागि समय लिनुहोस्",
    "Schedule Your Smile Visit": "तपाईंको दाँत परीक्षणको लागि समय तय गर्नुहोस्",
    "APPOINTMENT DESK": "अपोइन्टमेन्ट डेस्क",
    "Appointment Desk": "अपोइन्टमेन्ट डेस्क",
    "CAREFIRST CONTACT DESK": "केयरफर्स्ट सम्पर्क डेस्क",
    "CONTACT CAREFIRST": "सम्पर्क केयरफर्स्ट",
    "Contact CareFirst": "सम्पर्क केयरफर्स्ट",
    "ALL 11 SPECIALIZED PROCEDURES": "सबै ११ विशेष दन्त उपचारहरू",
    "Explore All Clinical Treatments": "सबै क्लिनिकल उपचार सेवाहरू हेर्नुहोस्",
    "Click any treatment to review detailed procedure steps, transparent pricing, recovery timelines, and specialist doctors.": "विस्तृत उपचार विधि, पारदर्शी शुल्क र विशेषज्ञ डाक्टरहरूको जानकारीका लागि उपचारमा क्लिक गर्नुहोस्।",
    "LEARN MORE": "थप जान्नुहोस्",
    "Learn More": "थप जान्नुहोस्",
    "From": "बाट",
    "Starting from": "सुरुवाती मूल्य",
    "Starting From": "सुरुवाती मूल्य",
    "Consultation": "परामर्श",
    "Book Slot": "समय लिनुहोस्",
    "Details": "विवरण",
    "Painless Anesthesia Protocol": "दुखाइरहित एनेस्थेसिया विधि",
    "Class-B Sterile Equipment": "क्लास-बी पूर्ण जीवाणुरहित उपकरण",
    "Digital Diagnosis & Planning": "डिजिटल दन्त परीक्षण र योजना",
    "Most Popular": "सबैभन्दा लोकप्रिय",
    "Expert Diagnosis & Care": "विशेषज्ञ निदान तथा उपचार",
    "Comfortable & Pain-Free": "आरामदायी र दुखाइरहित",
    "Transparent Pricing": "पारदर्शी शुल्क",

    # 4 Home Intro Features
    "Pain-Free Anesthesia": "दुखाइरहित एनेस्थेसिया",
    "Gentle techniques designed to eliminate dental anxiety during all treatments.": "सबै उपचारको क्रममा दन्त डर र चिन्ता हटाउन अपनाइने कोमल विधिहरू।",
    "Class-B Autoclave": "क्लास-बी अटोक्लेभ",
    "Strict sterilization protocols following international hospital standards.": "अन्तर्राष्ट्रिय अस्पताल मापदण्ड अनुसार १००% पूर्ण जीवाणुरहित विधि।",
    "100% strict sterilization protocols following international hospital standards.": "अन्तर्राष्ट्रिय अस्पताल मापदण्ड अनुसार १००% पूर्ण जीवाणुरहित विधि।",
    "Digital RVG & OPG": "डिजिटल RVG र OPG",
    "Instant low-radiation digital radiography for accurate diagnosis.": "सटीक परीक्षण र निदानका लागि तत्काल कम विकिरण डिजिटल एक्स-रे।",
    "Open Daily (7:30am – 7:30pm)": "दैनिक खुला (बिहान ७:३० – साँझ ७:३०)",
    "Flexible appointments 7 days a week, including routine and emergency care.": "नियमित तथा आकस्मिक सेवाका लागि हप्ताको ७ दिन लचिलो अपोइन्टमेन्ट सुविधा।",
    "Kathmandu's Trusted Dental Clinic": "काठमाडौँको भरपर्दो दन्त क्लिनिक",
    "Need an appointment? Open Booking Desk →": "अपोइन्टमेन्ट चाहिन्छ? बुकिङ डेस्क खोल्नुहोस् →",

    # Key Headings
    "Why Patients Trust CareFirst Dental": "बिरामीहरूले CareFirst Dental लाई किन विश्वास गर्छन्?",
    "A Trusted Dental Experience in the Heart of Kathmandu": "काठमाडौँको मुटुमा एक भरपर्दो दन्त सेवा अनुभव",
    "Expert Dental Care, Beautiful & Confident Smiles.": "विशेषज्ञ दन्त सेवा, सुन्दर तथा आत्मविश्वासी मुस्कान।",
    "We Create Healthy, Long-Lasting Smiles With Modern Gentle Care.": "हामी आधुनिक र कोमल सेवाका साथ स्वस्थ र दीर्घकालीन मुस्कान निर्माण गर्दछौं।",
    "Comprehensive Dental Treatments": "सम्पूर्ण दन्त उपचार सेवाहरू",
    "Meet Our Dental Specialists": "हाम्रा विशेषज्ञ दन्त चिकित्सकहरूलाई भेट्नुहोस्",
    "Transparent Treatment Pricing": "पारदर्शी उपचार शुल्क विवरण",
    "Complete Fee Schedule": "सम्पूर्ण शुल्क तालिका",
    "Dental Tourism in Kathmandu, Nepal": "काठमाडौँ, नेपालमा डेन्टल टुरिजम",
    "What's Included?": "के-के समावेश छ?",
    "Qualified Specialists, Dedicated to Your Smile": "तपाईंको मुस्कानप्रति समर्पित, योग्य विशेषज्ञहरू",
    "Designed for Your Comfort & Safety": "तपाईंको आराम र सुरक्षाको लागि डिजाइन गरिएको",
    "State-of-the-Art Dental Technology": "अत्याधुनिक दन्त प्रविधि",
    "A Dental Experience Unlike Any Other": "अरूभन्दा फरक र उत्कृष्ट दन्त अनुभव",
    "Powered by Advanced Dental Technology": "उन्नत दन्त प्रविधिद्वारा सञ्चालित",
    "Latest Articles": "नवीनतम लेखहरू",
    "Frequently Asked Questions": "बारम्बार सोधिने प्रश्नहरू",
    "Got Questions? We Have Answers.": "केही प्रश्न छन्? हामीसँग उत्तर छन्।",
    "FREQUENTLY ASKED QUESTIONS": "बारम्बार सोधिने प्रश्नहरू",
    "Answers to Your Questions": "तपाईंका प्रश्नहरूको उत्तर",
    "Everything you need to know before your appointment.": "तपाईंको अपोइन्टमेन्ट अघि जान्नुपर्ने सम्पूर्ण जानकारी।",
    "Find Us in Kathmandu": "हामीलाई काठमाडौँमा भेट्नुहोस्",
    "Browse Our Clinic Spaces": "हाम्रो क्लिनिक परिसर हेर्नुहोस्",
    "Treatment Categories": "उपचारका विधाहरू",
    "Every Smile Has a Story Worth Telling": "प्रत्येक मुस्कानको आफ्नै विशेष कथा हुन्छ",
    "What Our Patients Say": "हाम्रा बिरामीहरूको अनुभव",
    "Trusted by Patients • Rated on Google": "बिरामीहरूद्वारा विश्वासिलो • गुगलमा उत्कृष्ट मूल्याङ्कन",
    "Read All Reviews": "सबै समीक्षाहरू पढ्नुहोस्",
    "Leave a Review": "समीक्षा लेख्नुहोस्",
    "Still have questions?": "अझै केही प्रश्नहरू छन्?",
    "Our friendly reception team is ready to assist you on WhatsApp or phone.": "हाम्रो स्वागत कक्ष टोली तपाईंलाई ह्वाट्सएप वा फोनमा सहयोग गर्न तयार छ।",

    # Service Terminology
    "General Dentistry": "साधारण दन्त चिकित्सा",
    "General Dental Check-up": "साधारण दन्त परीक्षण",
    "General Dental Consultation": "साधारण दन्त परामर्श",
    "Dental Filling": "दाँत भर्ने सेवा (कम्पोजिट फिलिङ)",
    "Tooth Fillings & Restoration": "दाँत भर्ने तथा पुनर्स्थापना",
    "Root Canal Treatment": "रूट क्यानल उपचार (RCT)",
    "Root Canal Treatment (RCT)": "रूट क्यानल उपचार (RCT)",
    "Crowns & Bridges": "दाँतको क्याप तथा ब्रिज",
    "Crowns and Bridges": "दाँतको क्याप तथा ब्रिज",
    "Orthodontic Treatment (Braces)": "तार बाँध्ने उपचार (ब्रेसेस)",
    "Orthodontics & Braces": "तार बाँध्ने सेवा (अर्थोडोन्टिक्स / ब्रेसेस)",
    "Dental Implants": "डेन्टल इम्प्लान्ट (दाँत प्रत्यारोपण)",
    "Digital Dental X-Ray": "डिजिटल दन्त एक्स-रे",
    "Scaling & Polishing": "दाँत सफा गर्ने (स्केलिङ र पोलिसिङ)",
    "Scaling and Polishing": "दाँत सफा गर्ने (स्केलिङ र पोलिसिङ)",
    "Tooth Extraction": "दाँत निकाल्ने सेवा",
    "Dentures": "नक्कली दाँत (डेन्चर)",
    "Periodontal Treatment (Gum)": "गिजाको विशेष उपचार",
    "Periodontal Treatment": "गिजाको उपचार",
    "Teeth Whitening": "दाँत चम्काउने (ह्वाइटनिङ)",

    # Button CTAs
    "Book Consultation": "परामर्श बुक गर्नुहोस्",
    "Book Check-up": "चेक-अप बुक गर्नुहोस्",
    "Book Assessment": "परीक्षण बुक गर्नुहोस्",
    "Book Evaluation": "मूल्याङ्कन बुक गर्नुहोस्",
    "Book Urgent Care": "आकस्मिक सेवा लिनुहोस्",
    "Book Tooth Restoration": "दाँत पुनर्स्थापना बुक गर्नुहोस्",
    "Book Diagnostic Scan": "डिजिटल स्क्यान बुक गर्नुहोस्",
    "Book Your Cleaning Now": "दाँत सफाइ बुक गर्नुहोस्",
    "View Smile Gallery": "स्माइल ग्यालरी हेर्नुहोस्",
    "Call Now": "अहिले फोन गर्नुहोस्",
    "Send Message": "सन्देश पठाउनुहोस्",
    "View Complete Treatment Directory & Packages": "सम्पूर्ण उपचार सूची तथा प्याकेजहरू हेर्नुहोस्",
    "Explore Smile Gallery": "स्माइल ग्यालरी हेर्नुहोस्",

    # FAQ Questions from Components
    "What payment methods do you accept?": "तपाईंहरू कुन-कुन भुक्तानी विधिहरू स्वीकार गर्नुहुन्छ?",
    "We accept Cash, major Credit/Debit Cards, Fonepay, eSewa, and Khalti.": "हामी नगद, सबै प्रमुख क्रेडिट/डेबिट कार्डहरू, फोनपे (Fonepay), इसेवा (eSewa), र खल्ती (Khalti) स्वीकार गर्दछौं।",
    "How much does a dental implant cost in Nepal?": "नेपालमा डेन्टल इम्प्लान्टको लागत कति पर्छ?",
    "How much do braces cost in Nepal?": "नेपालमा दाँतमा तार बाँध्ने (ब्रेसेस) को शुल्क कति पर्छ?",
    "Do you offer installment (EMI) options?": "के तपाईंहरू किस्ताबन्दी (EMI) सुविधा उपलब्ध गराउनुहुन्छ?",
    "Yes, we offer flexible installment plans for major treatments like orthodontics (braces) and dental implants.": "हो, हामी अर्थोडोन्टिक्स (ब्रेसेस) र डेन्टल इम्प्लान्ट जस्ता प्रमुख उपचारहरूका लागि लचिलो किस्ताबन्दी सुविधा प्रदान गर्दछौं।",
    "Do you accept dental insurance?": "के तपाईंहरू दन्त बीमा स्वीकार गर्नुहुन्छ?",
    "Are consultation fees adjustable against treatment?": "के परामर्श शुल्क उपचार खर्चमा समायोजन हुन्छ?",
    "Are there any hidden fees?": "के कुनै लुकेको शुल्क छ?",
    "Not at all. We believe in transparent pricing. You will be given a clear cost estimate before any treatment begins.": "बिल्कुल छैन। हामी १००% पारदर्शी शुल्कमा विश्वास गर्दछौं। कुनै पनि उपचार सुरु गर्नुअघि तपाईंलाई स्पष्ट लागत अनुमान दिइनेछ।",
    "Is teeth cleaning painful?": "के दाँत सफा गर्दा (स्केलिङ) दुख्छ?",
    "No, professional scaling using modern ultrasonic technology is completely safe and generally painless.": "छैन, आधुनिक अल्ट्रासोनिक प्रविधि प्रयोग गरी गरिने व्यावसायिक दाँत सफाइ पूर्णतया सुरक्षित र सामान्यतया दुखाइरहित हुन्छ।",
    "How often should I visit the dentist for a check-up?": "मैले कति समयको अन्तरालमा दन्त चिकित्सकलाई भेट्नुपर्छ?",
    "We recommend visiting every 6 months for a comprehensive routine check-up and professional cleaning to prevent tooth decay and gum disease.": "दाँत किराले खाने र गिजाको समस्याबाट बच्न हामी हरेक ६ महिनामा एक पटक नियमित चेक-अप र सफाइ गराउन सिफारिस गर्दछौं।"
}

def extract_strings_from_workspace():
    base_dir = Path(__file__).resolve().parent.parent
    extracted = set()

    # 1. HTML templates
    template_dir = base_dir / 'templates'
    for f in template_dir.rglob('*.html'):
        content = f.read_text(encoding='utf-8', errors='ignore')
        for m in re.findall(r'{%\s*trans\s+[\'"]([^\'"]+)[\'"]\s*%}', content):
            if m.strip():
                extracted.add(m.strip())
        for _, body in re.findall(r'{%\s*blocktrans\b(.*?)%}(.*?){%\s*endblocktrans\s*%}', content, re.DOTALL):
            cleaned = body.strip()
            if cleaned:
                extracted.add(cleaned)

    # 2. Python files
    for py_file in base_dir.rglob('*.py'):
        if 'venv' in str(py_file) or '.git' in str(py_file) or 'scratch' in str(py_file):
            continue
        content = py_file.read_text(encoding='utf-8', errors='ignore')
        for m in re.findall(r'_\([\'"]([^\'"]+)[\'"]\)', content):
            if m.strip():
                extracted.add(m.strip())

    return extracted

def has_nepali_chars(text):
    return bool(re.search(r'[\u0900-\u097F]', text))

def clean_and_translate(text, translator):
    if text in CURATED_NEPALI_DICTIONARY:
        return CURATED_NEPALI_DICTIONARY[text]

    if text.isdigit() or len(text) <= 1 or text.startswith('http') or text.startswith('/'):
        return text

    placeholders = {}
    counter = 0

    def replacer(match):
        nonlocal counter
        ph = f"VARNUM{counter}TAG"
        placeholders[ph] = match.group(0)
        counter += 1
        return ph

    protected = re.sub(r'%\([a-zA-Z0-9_]+\)[sdrf]|%[sdrf]', replacer, text)
    protected = re.sub(r'\{\{\s*[a-zA-Z0-9_|\."\'\s]+\s*\}\}', replacer, protected)
    protected = re.sub(r'<[^>]+>', replacer, protected)

    clean_input = protected.replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'")

    try:
        translated = translator.translate(clean_input)
        for ph, orig in placeholders.items():
            translated = re.sub(re.escape(ph), orig, translated, flags=re.IGNORECASE)
            translated = translated.replace(ph.lower(), orig).replace(ph.upper(), orig)
        return translated.strip()
    except Exception:
        try:
            raw_trans = translator.translate(text)
            return raw_trans.strip()
        except Exception:
            return text

def build_and_compile():
    base_dir = Path(__file__).resolve().parent.parent
    locale_dir = base_dir / 'locale' / 'ne' / 'LC_MESSAGES'
    locale_dir.mkdir(parents=True, exist_ok=True)
    po_path = locale_dir / 'django.po'
    mo_path = locale_dir / 'django.mo'

    existing_map = {}
    if po_path.exists():
        try:
            old_po = polib.pofile(str(po_path), encoding='utf-8')
            for entry in old_po:
                if entry.msgid and entry.msgstr and entry.msgstr.strip():
                    # Check if entry is genuinely translated in Nepali (has Devanagari or is a curated phrase)
                    if has_nepali_chars(entry.msgstr) or entry.msgid in CURATED_NEPALI_DICTIONARY:
                        existing_map[entry.msgid] = entry.msgstr
        except Exception as e:
            print(f"Warning reading existing po: {e}")

    extracted_strings = extract_strings_from_workspace()
    print(f"Total unique strings extracted from workspace: {len(extracted_strings)}")

    translator = GoogleTranslator(source='en', target='ne')
    final_dict = {}

    # Seed curated dictionary
    for k, v in CURATED_NEPALI_DICTIONARY.items():
        final_dict[k] = v

    # Seed verified existing translations
    for k, v in existing_map.items():
        if k not in final_dict and v.strip():
            final_dict[k] = v

    to_translate = [s for s in extracted_strings if s not in final_dict or not final_dict[s].strip()]
    print(f"Strings to translate via Google Translator: {len(to_translate)}")

    for i, s in enumerate(to_translate):
        translated = clean_and_translate(s, translator)
        final_dict[s] = translated
        if (i + 1) % 25 == 0 or (i + 1) == len(to_translate):
            print(f"  Translated {i + 1}/{len(to_translate)} strings...")
        time.sleep(0.02)

    po = polib.POFile(encoding='utf-8')
    po.metadata = {
        'Project-Id-Version': 'CareFirst Dental 1.0',
        'Report-Msgid-Bugs-To': 'info@carefirst.com',
        'POT-Creation-Date': '2026-08-30 10:00+0545',
        'PO-Revision-Date': '2026-08-30 10:00+0545',
        'Last-Translator': 'CareFirst Dental Clinic <info@carefirst.com>',
        'Language-Team': 'Nepali <ne@carefirst.com>',
        'Language': 'ne',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=UTF-8',
        'Content-Transfer-Encoding': '8bit',
        'Plural-Forms': 'nplurals=2; plural=(n != 1);',
    }

    for k in sorted(final_dict.keys()):
        val = final_dict[k]
        entry = polib.POEntry(
            msgid=k,
            msgstr=val
        )
        po.append(entry)

    po.save(str(po_path))
    po.save_as_mofile(str(mo_path))
    print(f"Successfully compiled {len(po)} total translations into {po_path} and {mo_path}")

if __name__ == '__main__':
    build_and_compile()
