import os
import re
from pathlib import Path
import polib

COMPREHENSIVE_NEPALI_DICTIONARY = {
    # Core Clinic Info & Navigation
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

    # Specialized Treatments (Accurate Medical Nepali)
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
    "Orthodontics — Braces": "अर्थोडोन्टिक्स — ब्रेसेस",
    "Orthodontics — Clear Aligners": "अर्थोडोन्टिक्स — पारदर्शी अलाइनर",
    "Dental Implants": "डेन्टल इम्प्लान्ट (दाँत प्रत्यारोपण)",
    "Restorative — Dental Implant": "पुनर्स्थापना — डेन्टल इम्प्लान्ट",
    "Digital Dental X-Ray": "डिजिटल दन्त एक्स-रे",
    "Scaling & Polishing": "दाँत सफा गर्ने (स्केलिङ र पोलिसिङ)",
    "Scaling and Polishing": "दाँत सफा गर्ने (स्केलिङ र पोलिसिङ)",
    "Tooth Extraction": "दाँत निकाल्ने सेवा",
    "Dentures": "नक्कली दाँत (डेन्चर)",
    "Periodontal Treatment (Gum)": "गिजाको विशेष उपचार",
    "Periodontal Treatment": "गिजाको उपचार",
    "Teeth Whitening": "दाँत चम्काउने (ह्वाइटनिङ)",
    "Cosmetic Dentistry — Veneers": "कस्मेटिक दन्तचिकित्सा — भेनियर",
    "Cosmetic — Teeth Whitening": "कस्मेटिक — दाँत ह्वाइटनिङ",
    "Cosmetic — Composite Veneers": "कस्मेटिक — कम्पोजिट भेनियर",
    "Restorative — Crowns & Bridge": "पुनर्स्थापना — दाँतको क्याप र ब्रिज",
    "Full Smile Makeover": "पूर्ण मुस्कान मेकओभर",
    "Full Arch Rehabilitation": "पूर्ण मुख पुनर्स्थापना",
    "Restorative — Tooth-Colored Filling": "पुनर्स्थापना — दाँतकै रङको फिलिङ",
    "Preventative — Scaling & Polishing": "रोकथाम — दाँत सफा गर्ने (स्केलिङ)",
    "Pediatric Dentistry": "बाल दन्त चिकित्सा",

    # Default Service Descriptions
    "Advanced clinical treatment performed by certified dental specialists with pain-free protocols.": "प्रमाणित विशेषज्ञ दन्त चिकित्सकहरूद्वारा दुखाइरहित विधिबाट गरिने उच्चस्तरीय उपचार।",

    # Before / After Transformation Cards
    "BROWSE BY TREATMENT": "उपचार अनुसार हेर्नुहोस्",
    "Treatment": "उपचार",
    "Categories": "प्रकारहरू",
    "All Treatments": "सबै उपचारहरू",
    "Braces & Aligners": "ब्रेसेस र अलाइनर",
    "Veneers": "भेनियरहरू",
    "Whitening": "ह्वाइटनिङ",
    "Implants": "इम्प्लान्टहरू",
    "Smile Makeover": "मुस्कान मेकओभर",
    "General Care": "सामान्य दन्त सेवा",
    "Before": "अघि",
    "After": "पछि",
    "Aligned Smile in 18 Months": "१८ महिनामा मिलेको आकर्षक मुस्कान",
    "Crooked and crowded teeth corrected with metal braces, resulting in a perfectly aligned, confident smile.": "बाङ्गो र खप्टिएको दाँतलाई मेटल ब्रेसेसद्वारा मिलाएर पूर्ण रूपमा पंक्तिबद्ध र सुन्दर मुस्कान बनाइएको।",
    "Hollywood Smile with Porcelain Veneers": "पोर्सिलेन भेनियरद्वारा हलिउड मुस्कान",
    "8 ultra-thin porcelain veneers placed in 2 visits — transforming discoloured, chipped teeth into a stunning Hollywood smile.": "२ पटकको भेटमा ८ वटा पातलो पोर्सिलेन भेनियर लगाएर पहेंलो र फुटेको दाँतलाई आकर्षक हलिउड मुस्कानमा रूपान्तरण गरिएको।",
    "8 Shades Whiter in One Session": "एकै सत्रमा ८ गुणा बढी सेतो दाँत",
    "Professional in-office Zoom! whitening delivered an 8-shade improvement in a single 90-minute appointment.": "मात्र ९० मिनेटको व्यावसायिक जुम ह्वाइटनिङ सत्रद्वारा दाँतलाई ८ गुणा बढी चम्किलो र सेतो बनाइएको।",
    "Natural-Looking Tooth Replacement": "प्राकृतिक देखिने दाँत प्रत्यारोपण",
    "Single dental implant with ceramic crown placed seamlessly to replace a missing molar — indistinguishable from natural teeth.": "झरेको बंगाराको ठाउँमा प्राकृतिक दाँत जस्तै देखिने सिर्यामिक क्यापसहितको एकल डेन्टल इम्प्लान्ट प्रत्यारोपण गरिएको।",
    "Complete Smile Transformation": "पूर्ण मुस्कान रूपान्तरण",
    "A comprehensive smile makeover combining gum contouring, whitening, and 6 veneers to create a perfectly harmonious, magazine-worthy smile.": "गिजाको बनावट सुधार, ह्वाइटनिङ र ६ वटा भेनियर संयोजन गरेर तयार पारिएको पूर्ण आकर्षक मुस्कान।",
    "Same-Day Ceramic Crown": "एकै दिनमा सिर्यामिक क्याप (Crown)",
    "CAD/CAM same-day crown fabricated and placed in a single visit — perfectly matched, strong, and beautiful.": "सीएडी/सीएएम प्रविधिबाट एकै दिनमा तयार गरी लगाइएको बलियो, मिलेको र सुन्दर सिर्यामिक क्याप।",
    "Invisible Aligner Journey": "अदृश्य अलाइनर (Clear Aligner) उपचार",
    "12 months of clear aligner treatment delivered a straight, beautiful smile — without a single visible brace.": "कुनै पनि देखिने तार नबाँधी १२ महिनाको पारदर्शी अलाइनर उपचारबाट मिलेको सुन्दर दाँत।",
    "Instant Smile Makeover — One Visit": "एकै पटकमा तत्काल मुस्कान सुधार",
    "Composite resin veneers shaped and polished in a single appointment to close gaps and perfect smile symmetry.": "दाँतको बीचको खाली ठाउँ भर्न र मिलेको मुस्कान बनाउन एकै पटकमा कम्पोजिट भेनियर तयार गरिएको।",
    "Full-Mouth Reconstruction": "पूर्ण मुख पुनर्निर्माण",
    "A complex full-arch case combining implants, crowns, and gum treatment — restoring both function and a youthful, radiant smile.": "इम्प्लान्ट, क्याप र गिजाको उपचार संयोजन गरेर गरिएको जटिल पूर्ण मुख पुनर्स्थापना जसले प्राकृतिक कार्यक्षमता र उज्यालो मुस्कान फर्काउँछ।",
    "Seamless Decay Removal": "दाँतको किरा हटाएर प्राकृतिक फिलिङ",
    "A deep cavity was cleaned and perfectly restored using composite resin, halting decay and blending naturally with the tooth.": "गहिरो किरा लागेको भागलाई सफा गरी कम्पोजिट दाँतकै रङबाट भरिएको, जसले किरा लाग्न रोक्छ र प्राकृतिक देखिन्छ।",
    "Professional Deep Clean": "व्यावसायिक गहिरो दन्त सफाइ",
    "Hardened tartar and plaque build-up were professionally removed to restore gum health and reveal a brighter, healthier smile.": "गिजा स्वस्थ राख्न र उज्यालो मुस्कान ल्याउन जमेको फोहोर, टार्टर र पहेँलोपन पूर्ण रूपमा सफा गरिएको।",

    # Chatbot & Floating Widget
    "Need dental help?": "दन्त सल्लाह चाहिन्छ?",
    "CareFirst AI • Online": "केयरफर्स्ट एआई • अनलाइन",
    "Online": "अनलाइन",
    "Ask here!": "यहाँ सोध्नुहोस्!",
    "Ask CareFirst AI Receptionist": "केयरफर्स्ट एआई रिसेप्शनिस्टसँग सोध्नुहोस्",
    "Verified Care Guidance": "प्रमाणित दन्त परामर्श",
    "Type your question here...": "तपाईंको प्रश्न यहाँ लेख्नुहोस्...",

    # Forms & Booking
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
    "Tooth Pain / Other Concern": "दाँत दुख्ने / अन्य समस्या",
    "Clinical Evaluation with Doctor": "डाक्टरसँग प्रत्यक्ष क्लिनिकल परीक्षण",
    "NMC Certified": "एनएमसी (NMC) प्रमाणित",
    "NMC Verified Doctors": "प्रमाणित विशेषज्ञ दन्त चिकित्सक",
    "Open Daily": "दैनिक खुला",
    "Open Daily: 7:30 AM – 7:30 PM": "दैनिक खुला: बिहान ७:३० देखि साँझ ७:३० सम्म",
    "Call Clinic": "क्लिनिकमा कल गर्नुहोस्",
    "WhatsApp Available": "ह्वाट्सएप उपलब्ध छ",
}


def build_and_compile():
    base_dir = Path(__file__).resolve().parent.parent
    locale_dir = base_dir / 'locale' / 'ne' / 'LC_MESSAGES'
    locale_dir.mkdir(parents=True, exist_ok=True)
    po_path = locale_dir / 'django.po'
    mo_path = locale_dir / 'django.mo'

    existing_po = None
    if po_path.exists():
        try:
            existing_po = polib.pofile(str(po_path), encoding='utf-8')
        except Exception:
            pass

    po = polib.POFile(encoding='utf-8')
    po.metadata = {
        'Project-Id-Version': 'CareFirst Dental 1.0',
        'Report-Msgid-Bugs-To': 'info@carefirst.com',
        'POT-Creation-Date': '2026-08-20 15:30+0545',
        'PO-Revision-Date': '2026-08-20 15:30+0545',
        'Last-Translator': 'CareFirst AI Translator <info@carefirst.com>',
        'Language-Team': 'Nepali <ne@carefirst.com>',
        'Language': 'ne',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=UTF-8',
        'Content-Transfer-Encoding': '8bit',
        'Plural-Forms': 'nplurals=2; plural=(n != 1);',
    }

    merged = {}
    if existing_po:
        for entry in existing_po:
            if entry.msgid and entry.msgstr:
                merged[entry.msgid] = entry.msgstr

    for k, v in COMPREHENSIVE_NEPALI_DICTIONARY.items():
        merged[k] = v

    for k in sorted(merged.keys()):
        entry = polib.POEntry(
            msgid=k,
            msgstr=merged[k]
        )
        po.append(entry)

    po.save(str(po_path))
    po.save_as_mofile(str(mo_path))
    print(f"Successfully compiled {len(po)} phrases into standard UTF-8 gettext .mo file at {mo_path}")


if __name__ == '__main__':
    build_and_compile()
