import os
import re
import struct
from pathlib import Path

# Complete High-Precision Dental & Clinical Nepali Dictionary
COMPREHENSIVE_NEPALI_DICTIONARY = {
    "CareFirst Dental Clinic": "केयरफर्स्ट डेन्टल क्लिनिक",
    "Carefirst Dental Clinic": "केयरफर्स्ट डेन्टल क्लिनिक",
    "CareFirst": "केयरफर्स्ट",
    "Carefirst": "केयरफर्स्ट",
    "Home": "गृहपृष्ठ",
    "About Us": "हाम्रो बारेमा",
    "Services": "दन्त सेवाहरू",
    "Treatments": "उपचारहरू",
    "Our Doctors": "हाम्रा चिकित्सकहरू",
    "Doctors": "चिकित्सकहरू",
    "Smile Gallery": "स्माइल ग्यालरी",
    "Video": "भिडियो",
    "Videos": "भिडियोहरू",
    "Pricing": "मूल्य विवरण",
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
    "General Dentistry": "साधारण दन्त चिकित्सा",
    "General Dental Check-up": "साधारण दन्त परीक्षण",
    "General Dental Consultation": "साधारण दन्त परामर्श",
    "Dental Filling": "दाँत भर्ने सेवा",
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
    "Cosmetic Teeth Whitening": "कस्मेटिक दाँत ह्वाइटनिङ",
    "Pediatric Dentistry": "बाल दन्त चिकित्सा",
    "Oral Health Tips & Guides": "दन्त स्वास्थ्य सुझाव तथा जानकारी",
    "DENTAL BLOG & GUIDES": "दन्त ब्लग तथा जानकारी",
    "Your Name": "तपाईंको नाम",
    "Your Name *": "तपाईंको नाम *",
    "Full Name": "पूरा नाम",
    "Your Email Address": "तपाईंको इमेल ठेगाना",
    "Your Email Address *": "तपाईंको इमेल ठेगाना *",
    "Email": "इमेल",
    "Email Address *": "इमेल ठेगाना *",
    "Contact Number": "सम्पर्क फोन नम्बर",
    "Contact Number *": "सम्पर्क फोन नम्बर *",
    "Phone": "फोन नम्बर",
    "Appointment date": "अपोइन्टमेन्ट मिति",
    "Appointment date *": "अपोइन्टमेन्ट मिति *",
    "Requested Date": "रोजेको मिति",
    "Preferred Time": "रोजेको समय",
    "Morning (7:30 AM – 11:30 AM)": "बिहानी सत्र (बिहान ७:३० – ११:३०)",
    "Afternoon (11:30 AM – 4:00 PM)": "दिउँसो सत्र (११:३० – दिउँसो ४:००)",
    "Evening (4:00 PM – 7:30 PM)": "साँझ सत्र (साँझ ४:०० – ७:३०)",
    "Treatment / Service": "दन्त सेवा / उपचार",
    "Subject": "विषय",
    "Message": "सन्देश",
    "Your Message": "तपाईंको सन्देश",
    "Your Message *": "तपाईंको सन्देश *",
    "Tell us how we can help you...": "हामी तपाईंलाई कसरी मद्दत गर्न सक्छौं, लेख्नुहोस्...",
    "Book Appointment Now": "अहिले नै अपोइन्टमेन्ट लिनुहोस्",
    "Send Message Now": "सन्देश पठाउनुहोस्",
    "Send Message": "सन्देश पठाउनुहोस्",
    "Read Article": "पूरा लेख पढ्नुहोस्",
    "View All Articles": "सबै लेखहरू हेर्नुहोस्",
    "View All Treatments": "सबै उपचार सेवाहरू हेर्नुहोस्",
    "Clear Filters": "फिल्टरहरू हटाउनुहोस्",
    "Search Articles": "लेखहरू खोज्नुहोस्",
    "NMC Certified": "एनएमसी (NMC) प्रमाणित",
    "NMC Verified Doctors": "प्रमाणित विशेषज्ञ दन्त चिकित्सक",
    "Open Daily": "दैनिक खुला",
    "Open Daily: 7:30 AM – 7:30 PM": "दैनिक खुला: बिहान ७:३० देखि साँझ ७:३० सम्म",
    "Open Daily (Mon–Sun): 7:30 AM – 7:30 PM": "दैनिक खुला (सोम–आइत): बिहान ७:३० देखि साँझ ७:३० सम्म",
    "Daily: 7:30 AM – 7:30 PM": "दैनिक: बिहान ७:३० – साँझ ७:३०",
    "Call Clinic": "क्लिनिकमा कल गर्नुहोस्",
    "WhatsApp Available": "ह्वाट्सएप उपलब्ध छ",
    "Announcements": "सूचना तथा समाचार",
    "Need dental help?": "दन्त सल्लाह चाहिन्छ?",
    "Online": "अनलाइन",
    "Online • Verified Care Guidance": "अनलाइन • प्रमाणित दन्त परामर्श",
    "Ask here!": "यहाँ सोध्नुहोस्!",
    "Have questions about dental care or pricing?": "दन्त उपचार वा शुल्कबारे प्रश्न छ?",
    "Have a Question?": "केही सोध्नु छ?",
    "We're here to help with treatment questions, appointments, pricing, and general dental inquiries.": "हामी उपचार सम्बन्धी प्रश्न, अपोइन्टमेन्ट, शुल्क र सामान्य दन्त जिज्ञासामा मद्दत गर्न सधैं तयार छौं।",
    "Request an appointment with our specialist dental team in Shankhamul, Kathmandu.": "शंखमूल, काठमाडौँस्थित हाम्रो विशेषज्ञ दन्त टोलीसँग परामर्शको लागि समय तय गर्नुहोस्।",
    "Request a consultation with our NMC-certified specialist team in Shankhamul, Kathmandu.": "शंखमूल, काठमाडौँस्थित हाम्रो एनएमसी प्रमाणित विशेषज्ञ टोलीसँग दन्त परामर्श लिनुहोस्।",
    "Pragatinagar Road, Shankhamul-31, Kathmandu (Shankhamul / New Baneshwor)": "प्रगतिनगर मार्ग, शंखमूल-३१, काठमाडौँ (शंखमूल / नयाँ बानेश्वर)",
    "Led by Dr. Subash Banjade (Dental Surgeon) & Specialist Team": "डा. सुवास बन्जाडे (डेन्टल सर्जन) तथा विशेषज्ञ टोलीद्वारा संचालित",
    "Free Initial Oral Consultation for New Patients": "नयाँ बिरामीहरूको लागि प्रारम्भिक मुख तथा दन्त परीक्षण निःशुल्क",
    "Painless Root Canal & 3D Digital Dental Implants": "दुखाइरहित रूट क्यानल तथा थ्रीडी डिजिटल डेन्टल इम्प्लान्ट",
    "Oral Examination & Diagnosis": "मुख परीक्षण तथा निदान",
    "Starting from": "सुरुवाती मूल्य",
    "Consultation & Custom Plan": "परामर्श तथा व्यक्तिगत उपचार योजना",
    "Step 01": "चरण ०१",
    "Step 02": "चरण ०२",
    "Step 03": "चरण ०३",
    "Step 04": "चरण ०४",
    "Step 05": "चरण ०५",
    "Treatment": "उपचार",
    "Visit Type": "भ्रमणको प्रकार",
    "Date & Time": "मिति र समय",
    "Your Details": "तपाईंको विवरण",
    "Review": "पुनरावलोकन",
    "How can we help your smile?": "तपाईंको मुस्कानको लागि हामी कसरी सहयोग गर्न सक्छौं?",
    "Select the dental service or concern you would like to consult with our doctors about.": "तपाईंले डाक्टरहरूसँग परामर्श गर्न चाहनुभएको दन्त सेवा वा समस्या छान्नुहोस्।",
    "Tooth Pain / Other Concern": "दाँत दुख्ने / अन्य समस्या",
    "Clinical Evaluation with Doctor": "डाक्टरसँग प्रत्यक्ष क्लिनिकल परीक्षण",
    "English": "अंग्रेजी",
    "Nepali": "नेपाली",
    "CareFirst Dental Clinic — Shankhamul, Kathmandu": "केयरफर्स्ट डेन्टल क्लिनिक — शंखमूल, काठमाडौँ",
    "Open Daily 7:30 AM – 7:30 PM • Dr. Subash Banjade (NMC #31229)": "दैनिक खुला बिहान ७:३० – साँझ ७:३० • डा. सुवास बन्जाडे (NMC #३१२२९)",
    "Clinic Tour": "क्लिनिक भ्रमण",
    "Before & After": "उपचार अघि र पछि",
    "Latest": "ताजा",
    "Articles": "लेखहरू",
    "Search": "खोज्नुहोस्",
    "All": "सबै",
}


def compile_po_to_mo(po_filepath: str, mo_filepath: str):
    messages = {}
    with open(po_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines()
    cur_id = None
    cur_str = None
    reading_id = False
    reading_str = False

    for line in lines:
        line_s = line.strip()
        if line_s.startswith('msgid "'):
            if cur_id is not None and cur_str is not None:
                messages[cur_id] = cur_str
            cur_id = line_s[7:-1]
            cur_str = ""
            reading_id = True
            reading_str = False
        elif line_s.startswith('msgstr "'):
            cur_str = line_s[8:-1]
            reading_id = False
            reading_str = True
        elif line_s.startswith('"') and line_s.endswith('"'):
            inner = line_s[1:-1]
            if reading_id:
                cur_id += inner
            elif reading_str:
                cur_str += inner

    if cur_id is not None and cur_str is not None:
        messages[cur_id] = cur_str

    clean_messages = {}
    for k, v in messages.items():
        if k:
            k_clean = k.replace('\\n', '\n').replace('\\"', '"')
            v_clean = v.replace('\\n', '\n').replace('\\"', '"')
            if v_clean:
                clean_messages[k_clean.encode('utf-8')] = v_clean.encode('utf-8')

    keys = sorted(clean_messages.keys())
    offsets = []
    ids = b''
    strs = b''

    for key in keys:
        val = clean_messages[key]
        offsets.append((len(ids), len(key), len(strs), len(val)))
        ids += key + b'\x00'
        strs += val + b'\x00'

    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + len(ids)

    koffsets = []
    voffsets = []
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1 + keystart]
        voffsets += [l2, o2 + valuestart]

    output = struct.pack(
        "Iiiiiii",
        0x950412de,
        0,
        len(keys),
        7 * 4,
        7 * 4 + len(keys) * 8,
        0, 0
    )

    output += struct.pack(str(len(koffsets)) + "i", *koffsets)
    output += struct.pack(str(len(voffsets)) + "i", *voffsets)
    output += ids
    output += strs

    os.makedirs(os.path.dirname(mo_filepath), exist_ok=True)
    with open(mo_filepath, 'wb') as f:
        f.write(output)


def build_translations():
    base_dir = Path(__file__).resolve().parent.parent
    extracted = set(COMPREHENSIVE_NEPALI_DICTIONARY.keys())

    trans_pattern = re.compile(r'{%\s*(?:trans|blocktrans.*?)\s*["\'](.*?)["\']\s*%}')
    templates_dir = base_dir / 'templates'
    if templates_dir.exists():
        for fp in templates_dir.rglob('*.html'):
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    matches = trans_pattern.findall(f.read())
                    for m in matches:
                        clean_m = m.strip()
                        if clean_m and len(clean_m) > 1 and not clean_m.startswith('{'):
                            extracted.add(clean_m)
            except Exception:
                pass

    translations_map = {}
    for phrase in extracted:
        if phrase in COMPREHENSIVE_NEPALI_DICTIONARY:
            translations_map[phrase] = COMPREHENSIVE_NEPALI_DICTIONARY[phrase]
        else:
            translations_map[phrase] = phrase

    translated_entries = []
    for phrase in sorted(translations_map.keys()):
        nepali_trans = translations_map[phrase]
        escaped_en = phrase.replace('"', '\\"')
        escaped_ne = nepali_trans.replace('"', '\\"')
        translated_entries.append(f'msgid "{escaped_en}"\nmsgstr "{escaped_ne}"\n')

    locale_dir = base_dir / 'locale' / 'ne' / 'LC_MESSAGES'
    locale_dir.mkdir(parents=True, exist_ok=True)
    po_path = locale_dir / 'django.po'
    mo_path = locale_dir / 'django.mo'

    po_content = """# CareFirst Dental Clinic Nepali Translation
# Generated via Deep Translator
msgid ""
msgstr ""
"Project-Id-Version: CareFirst Dental 1.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2026-08-19 10:20+0545\\n"
"PO-Revision-Date: 2026-08-19 10:20+0545\\n"
"Last-Translator: CareFirst AI Translator <info@carefirst.com>\\n"
"Language-Team: Nepali <ne@carefirst.com>\\n"
"Language: ne\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"

""" + "\n".join(translated_entries)

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(po_content)

    compile_po_to_mo(str(po_path), str(mo_path))
    print(f"Successfully generated {po_path} and compiled {mo_path} ({len(translations_map)} phrases)")


if __name__ == '__main__':
    build_translations()
