import os
import re
import time
from pathlib import Path
import polib
from deep_translator import GoogleTranslator

CURATED_NEPALI_DICTIONARY = {
    # Core Clinic Info & Navigation
    "CareFirst Dental Clinic": "केयरफर्स्ट डेन्टल क्लिनिक",
    "Carefirst Dental Clinic": "केयरफर्स्ट डेन्टल क्लिनिक",
    "CareFirst Dental": "CareFirst Dental",
    "Carefirst Dental": "CareFirst Dental",
    "CareFirst": "केयरफर्स्ट",
    "Carefirst": "केयरफर्स्ट",
    "Home": "गृहपृष्ठ",
    "About": "हाम्रो बारेमा",
    "About Us": "हाम्रो बारेमा",
    "Services": "दन्त सेवाहरू",
    "Treatments": "उपचारहरू",
    "Our Doctors": "हाम्रा चिकित्सकहरू",
    "Doctors": "चिकित्सकहरू",
    "Meet Our Doctors": "हाम्रा चिकित्सकहरूलाई भेट्नुहोस्",
    "Meet the Doctors": "हाम्रा डाक्टरहरूलाई भेट्नुहोस्",
    "Meet All Doctors": "सबै डाक्टरहरू हेर्नुहोस्",
    "Smile Gallery": "स्माइल ग्यालरी",
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
    "Consultation": "परामर्श",
    "Book Slot": "समय लिनुहोस्",
    "Details": "विवरण",
    "Painless Anesthesia Protocol": "दुखाइरहित एनेस्थेसिया विधि",
    "Class-B Sterile Equipment": "क्लास-बी पूर्ण जीवाणुरहित उपकरण",
    "Digital Diagnosis & Planning": "डिजिटल दन्त परीक्षण र योजना",

    # 4 Home Intro Features (Refined Native Nepali)
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

    # Key Headings (Complete Semantic Units)
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
    "Find Us in Kathmandu": "हामीलाई काठमाडौँमा भेट्नुहोस्",
    "Browse Our Clinic Spaces": "हाम्रो क्लिनिक परिसर हेर्नुहोस्",
    "Treatment Categories": "उपचारका विधाहरू",
    "Every Smile Has a Story Worth Telling": "प्रत्येक मुस्कानको आफ्नै विशेष कथा हुन्छ",

    # Service Headings & Procedures
    "What Are Crowns & Bridges?": "क्राउन र ब्रिज (क्याप) के हुन्?",
    "Types of Crowns": "क्राउन (क्याप) का प्रकारहरू",
    "Our Treatment Process": "हाम्रो उपचार प्रक्रिया",
    "Smile Restorations": "मुस्कान पुनर्स्थापना सेवा",
    "What is a Dental Filling?": "दाँत भर्ने सेवा (डेन्टल फिलिङ) के हो?",
    "Before & After Filling Cases": "फिलिङ उपचार अघि र पछिको नतिजा",
    "Types of Dental Filling Materials": "दाँत भर्ने सामग्रीका प्रकारहरू",
    "Our Filling Treatment Process": "दाँत भर्ने हाम्रो उपचार प्रक्रिया",
    "Dental Filling Treatment Gallery": "दाँत फिलिङ उपचार ग्यालरी",
    "What Are Dental Implants?": "डेन्टल इम्प्लान्ट (दाँत प्रत्यारोपण) के हुन्?",
    "Our Implant Treatment Process": "इम्प्लान्ट उपचारको हाम्रो प्रक्रिया",
    "Smile Transformation Timeline": "मुस्कान रूपान्तरण समयतालिका",
    "Before & After Implant Cases": "इम्प्लान्ट उपचार अघि र पछिका परिणामहरू",
    "What Are Dentures?": "डेन्चर (नक्कली दाँत) के हुन्?",
    "Types of Dentures": "डेन्चरका प्रकारहरू",
    "Our Denture Treatment Process": "डेन्चर निर्माण तथा उपचार प्रक्रिया",
    "Denture Treatment Gallery": "डेन्चर उपचार ग्यालरी",
    "What is a Digital Dental X-Ray?": "डिजिटल दन्त एक्स-रे के हो?",
    "Our Digital X-Ray Process": "हाम्रो डिजिटल एक्स-रे प्रक्रिया",
    "Diagnostic Suite & Technology Gallery": "निदान तथा प्रविधि ग्यालरी",
    "What is General Dentistry?": "सामान्य दन्त चिकित्सा के हो?",
    "Before & After Results": "उपचार अघि र पछिका परिणामहरू",
    "Our Patient Care Process": "हाम्रो बिरामी सेवा प्रक्रिया",
    "Related Videos": "सम्बन्धित भिडियोहरू",
    "What is Braces Treatment?": "ब्रेसेस (तार बाँध्ने) उपचार के हो?",
    "Types of Braces Available": "उपलब्ध ब्रेसेसका प्रकारहरू",
    "Compare Braces Options": "ब्रेसेस विकल्पहरूको तुलना गर्नुहोस्",
    "Which Braces Are Right for You?": "तपाईंको लागि कुन ब्रेसेस उपयुक्त छ?",
    "Smile Transformation Gallery": "मुस्कान रूपान्तरण ग्यालरी",
    "Our Orthodontic Treatment Journey": "हाम्रो अर्थोडोन्टिक उपचार यात्रा",
    "What is Gum Disease?": "गिजाको समस्या (रोग) के हो?",
    "Stages of Gum Disease": "गिजाको समस्याका चरणहरू",
    "What is Root Canal Treatment?": "रूट क्यानल उपचार (RCT) के हो?",
    "What is a Root Canal?": "रूट क्यानल उपचार (RCT) के हो?",
    "Benefits of Root Canal Treatment": "रूट क्यानल उपचारका फाइदाहरू",
    "Our Root Canal Process": "हाम्रो रूट क्यानल उपचार प्रक्रिया",
    "Clinical Gallery": "क्लिनिकल ग्यालरी",
    "What is Scaling & Polishing?": "दाँत सफाइ र पोलिसिङ (स्केलिङ) के हो?",
    "What is Tooth Extraction?": "दाँत निकाल्ने सेवा के हो?",
    "When is Extraction Required?": "दाँत कुन अवस्थामा निकाल्नुपर्छ?",
    "Step-by-Step Treatment Process": "चरणबद्ध उपचार प्रक्रिया",
    "Rated 5.0 / 5.0 based on Google Reviews": "गुगल रिभ्युका आधारमा ५.० / ५.० रेटिङ प्राप्त",

    # Terminology Overrides
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
                if entry.msgid and entry.msgstr:
                    if '%(' in entry.msgid and '%(' in entry.msgstr:
                        orig_vars = set(re.findall(r'%\(([a-zA-Z0-9_]+)\)', entry.msgid))
                        trans_vars = set(re.findall(r'%\(([a-zA-Z0-9_]+)\)', entry.msgstr))
                        if orig_vars != trans_vars:
                            continue
                    existing_map[entry.msgid] = entry.msgstr
        except Exception as e:
            print(f"Warning reading existing po: {e}")

    extracted_strings = extract_strings_from_workspace()
    print(f"Total unique strings extracted from workspace: {len(extracted_strings)}")

    translator = GoogleTranslator(source='en', target='ne')
    final_dict = {}

    for k, v in CURATED_NEPALI_DICTIONARY.items():
        final_dict[k] = v

    for k, v in existing_map.items():
        if k not in final_dict and v.strip():
            final_dict[k] = v

    to_translate = [s for s in extracted_strings if s not in final_dict or not final_dict[s].strip()]
    print(f"Strings to translate via deep-translator: {len(to_translate)}")

    for i, s in enumerate(to_translate):
        translated = clean_and_translate(s, translator)
        final_dict[s] = translated
        if (i + 1) % 15 == 0 or (i + 1) == len(to_translate):
            print(f"  Translated {i + 1}/{len(to_translate)} strings...")
        time.sleep(0.04)

    po = polib.POFile(encoding='utf-8')
    po.metadata = {
        'Project-Id-Version': 'CareFirst Dental 1.0',
        'Report-Msgid-Bugs-To': 'info@carefirst.com',
        'POT-Creation-Date': '2026-08-30 10:00+0545',
        'PO-Revision-Date': '2026-08-30 10:00+0545',
        'Last-Translator': 'DeepTranslator & Medical Board <info@carefirst.com>',
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
