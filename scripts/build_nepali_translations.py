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

    # Crowns & Bridges Procedure & Pricing Details
    "Metal Crown": "मेटल क्याप (धातु क्राउन)",
    "METAL CROWN": "मेटल क्याप (धातु क्राउन)",
    "Durable, non-aesthetic": "अत्यधिक बलियो, पछाडिको दाँतका लागि उपयुक्त",
    "PFM Crown": "PFM क्याप (दाँतको रङ मिल्ने)",
    "PFM CROWN": "PFM क्याप (दाँतको रङ मिल्ने)",
    "Porcelain Fused to Metal": "दाँतको रङ मिल्ने पोर्सिलेन र धातुको मजबुत मिश्रण",
    "Porcelain fused to metal for strength and natural appearance. A perfect balance of durability and aesthetics.": "दाँतको रङ मिल्ने पोर्सिलेन र धातुको बलियो मिश्रण, जसले प्राकृतिक र आकर्षक मुस्कान दिन्छ।",
    "Zirconia Crown": "प्रिमियम जिर्कोनिया क्याप",
    "ZIRCONIA CROWN": "प्रिमियम जिर्कोनिया क्याप",
    "High strength, natural aesthetic": "उच्च मजबुती, प्राकृतिक सौन्दर्य",
    "Made from high-strength zirconia ceramic. Extremely durable with excellent natural appearance.": "अत्यन्त बलियो जिर्कोनिया सिरामिकबाट बनेको, जीवनभर टिक्ने र प्राकृतिक दाँत जस्तै देखिने प्रिमियम क्याप।",
    "E-max Crown": "इ-म्याक्स क्याप (E-max Crown)",
    "E-MAX CROWN": "इ-म्याक्स क्याप (E-max Crown)",
    "Premium All-Ceramic": "प्रिमियम अल-सिरामिक",
    "Premium all-ceramic crown known for its lifelike translucency and beautiful aesthetics.": "अगाडिका दाँतहरूलाई प्राकृतिक चमक र उत्कृष्ट सौन्दर्य दिने प्रिमियम अल-सिरामिक क्याप।",
    "1. Preparation": "१. दाँतको तयारी (Preparation)",
    "The tooth is numbed, and a thin layer of enamel is shaped to make room for the crown to fit over it perfectly.": "दाँतलाई लठ्याएर क्याप राम्रोसँग बस्नका लागि इनामेलको पातलो तहलाई उपयुक्त आकार दिइन्छ।",
    "2. Digital Impressions": "२. डिजिटल ३D स्क्यान (Digital Impressions)",
    "We take a precise 3D scan of your mouth and send the data to our dental lab to custom-mill your crown or bridge.": "हामी तपाईंको मुखको सटीक ३D स्क्यान गरी दाँतको क्याप वा ब्रिज निर्माणका लागि आधुनिक दन्त ल्याबमा पठाउँछौं।",
    "3. Temporary Placement": "३. अस्थायी क्याप (Temporary Placement)",
    "While your permanent crown is being crafted, we place a temporary crown to protect your tooth.": "स्थायी क्याप तयार नहुन्जेल दाँतको पूर्ण सुरक्षाका लागि अस्थायी क्याप लगाइन्छ।",
    "4. Final Cementation": "४. स्थायी सिमेन्टेसन (Final Cementation)",
    "On your return visit, we verify the fit, shade, and bite, then permanently bond the crown in place.": "अर्को पटक आउँदा क्यापको फिटिङ, रङ र टोकाइ (Bite) जाँच गरी स्थायी रूपमा टाँसिन्छ।",
    "* Note: Prices are per unit (per tooth). A 3-tooth bridge made of PFM would be NPR 6,000 x 3 = NPR 18,000. Final costs depend on clinical evaluation.": "* नोट: शुल्क प्रति एकाइ (प्रति दाँत) को हो। उदाहरणका लागि, PFM क्यापबाट बनेको ३-दाँतको ब्रिजको शुल्क NPR ६,००० × ३ = NPR १८,००० हुनेछ। अन्तिम शुल्क क्लिनिकल परीक्षणमा निर्भर गर्दछ।",
    "Back teeth and molars where strength is the top priority.": "पछाडिको बंगारा जहाँ दाँतको मजबुती मुख्य प्राथमिकता हुन्छ।",
    "Front and back teeth where strength and aesthetics are needed.": "अगाडि र पछाडिका दाँत जहाँ मजबुती र सौन्दर्य दुवै आवश्यक हुन्छ।",
    "Both front and back teeth. Best all-round performance.": "अगाडि र पछाडि दुवै दाँतका लागि उत्कृष्ट र टिकाउ समाधान।",
    "Front teeth and visible areas for the best aesthetics.": "अगाडिका देखिने दाँतहरूका लागि सर्वोत्तम सौन्दर्य।",
    "Highly durable": "अत्यधिक टिकाउ र बलियो",
    "Resistant to wear and fracture": "घोटिन र भाँचिनबाट सुरक्षित",
    "Ideal for back molars": "पछाडिका बंगाराका लागि उपयुक्त",
    "Cost-effective": "किफायती शुल्क",
    "Strong and durable": "मजबुत र दीर्घकालीन",
    "Natural tooth-colored appearance": "दाँतको प्राकृतिक रङ मिल्ने",
    "Good for front and back teeth": "अगाडि र पछाडिका दुवै दाँतका लागि उपयुक्त",
    "More affordable than all-ceramic": "अल-सिरामिक भन्दा किफायती",
    "Superior aesthetics": "उत्कृष्ट सौन्दर्य",
    "Natural translucency": "प्राकृतिक दाँतको जस्तै चमक",
    "Perfect for front teeth": "अगाडिका दाँतका लागि उत्तम",
    "Ideal for all teeth": "सबै दाँतका लागि उपयुक्त",
    "Tooth Protection": "दाँतको सुरक्षा",
    "Provides a protective shield for brittle or root-canal treated teeth.": "रूट क्यानल गरिएको वा कमजोर दाँतलाई भाँचिनबाट जोगाउन सुरक्षा कवच प्रदान गर्दछ।",
    "Prevents Shifting": "दाँत हल्लिन वा सर्नबाट रोक्छ",
    "Restores Chewing": "चपाउने शक्ति पुनर्स्थापना गर्दछ",
    "Allows you to eat your favorite foods without pain or hesitation.": "बिना कुनै दुखाइ आफ्नो मनपर्ने खाना मज्जाले खान मद्दत गर्दछ।",
    "Why Choose Carefirst Dental Clinic?": "केयरफर्स्ट डेन्टल क्लिनिक किन रोज्ने?",
    "Why Choose CareFirst Dental Clinic?": "केयरफर्स्ट डेन्टल क्लिनिक किन रोज्ने?",
    "Digital Impressions:": "डिजिटल ३D स्क्यान:",
    "We use precise 3D scanners instead of messy, uncomfortable putty to mold your teeth.": "हामी परम्परागत फोहोर पेस्टको साटो सटीक ३D डिजिटल स्क्यानर प्रयोग गर्दछौं।",
    "Top-tier Labs:": "अन्तर्राष्ट्रिय स्तरका ल्याब:",
    "Our crowns are milled by expert technicians ensuring a perfect, micro-precise fit.": "हाम्रा क्यापहरू आधुनिक ल्याबका प्राविधिकहरूद्वारा माइक्रो-सटीक नापमा निर्माण गरिन्छ।",
    "Aesthetic Matching:": "प्राकृतिक रङ मिलान:",
    "We take lighting and natural translucency into account for an invisible restoration.": "हामी प्राकृतिक प्रकाश र चमक मिलाएर दाँतको रङ दुरुस्त मिलाउँछौं।",
    "Warranty:": "वारेन्टी तथा ग्यारेन्टी:",
    "We stand by the quality of our premium Zirconia and E-max crowns.": "हामी हाम्रा प्रिमियम जिर्कोनिया र इ-म्याक्स क्यापहरूको गुणस्तरमा पूर्ण विश्वस्त छौं।",

    # Steps for Implants, Dentures, RCT, Scaling, Extraction, Braces
    "3. Placement": "३. इम्प्लान्ट प्रत्यारोपण (Implant Placement)",
    "3. Wax Try-In": "३. मोमको दाँत परीक्षण (Wax Try-In)",
    "1. Consultation & Treatment Planning": "१. दन्त परामर्श तथा उपचार योजना",
    "2. Tooth Extraction (If needed)": "२. दाँत निकाल्ने (आवश्यक परेमा)",
    "4. Final Denture Delivery": "४. स्थायी नक्कली दाँत डेलिभरी",
    "1. Examination & X-Ray": "१. दन्त परीक्षण तथा डिजिटल एक्स-रे",
    "2. Cleaning & Shaping": "२. नसा सफाइ तथा आकार निर्धारण",
    "3. Obturation (Filling)": "३. जराको नसा भर्ने (Obturation)",
    "4. Crown Placement": "४. क्याप लगाउने (Crown Placement)",
    "1. Consultation & 3D Imaging": "१. परामर्श तथा ३D डिजिटल स्क्यान",
    "2. Implant Placement Surgery": "२. इम्प्लान्ट प्रत्यारोपण शल्यक्रिया",
    "3. Healing & Osseointegration": "३. हड्डीसँग जोड्ने अवधि (Healing)",
    "4. Permanent Crown Attachment": "४. स्थायी क्याप जडान",
    "1. Oral Assessment & Diagnosis": "१. मौखिक परीक्षण तथा निदान",
    "2. Cavity Cleaning & Decay Removal": "२. किराले खाएको भाग सफाइ",
    "3. Composite Layering & Bonding": "३. कम्पोजिट फिलिङ तथा लेयरिङ",
    "4. Polishing & Bite Check": "४. पोलिसिङ तथा टोकाइ (Bite) परीक्षण",
    "1. Clinical Examination & Consultation": "१. क्लिनिकल परीक्षण तथा परामर्श",
    "2. Ultrasonic Plaque & Tartar Removal": "२. अल्ट्रासोनिक मेसिनद्वारा फोहोर सफाइ",
    "3. Deep Stain Polishing": "३. दाँतको दाग तथा पहेँलोपन पोलिसिङ",
    "4. Fluoride Protection & Home Care Advice": "४. फ्लोराइड सुरक्षा तथा दाँत हेरचाह सल्लाह",

    # Review and Patient Stories Section
    "Exceptional care, in our patients' own words.": "उत्कृष्ट दन्त सेवा, हाम्रा बिरामीहरूको आफ्नै शब्दमा।",
    "PATIENT STORIES & REVIEWS": "बिरामी कथाहरू र समीक्षाहरू",
    "From independent Google ratings to real patient experiences, discover why thousands of patients trust CareFirst Dental Clinic in Kathmandu.": "स्वतन्त्र गुगल मूल्याङ्कनदेखि वास्तविक बिरामी अनुभवहरूसम्म, थाहा पाउनुहोस् किन हजारौं बिरामीहरूले काठमाडौँको केयरफर्स्ट डेन्टल क्लिनिकमा विश्वास गर्छन्।",
    "Google Business Rating": "गुगल व्यापार मूल्याङ्कन",
    "100% Verified": "१००% प्रमाणित",
    "Google Reviews": "गुगल समीक्षाहरू",
    "Rated 5.0 / 5.0 based on": "५.० / ५.० मूल्याङ्कन प्राप्त",
    "Real Patient Testimonials": "वास्तविक बिरामीहरूका अनुभव",
    "Verified Reviews": "प्रमाणित समीक्षाहरू",
    "Write a Review on Google": "गुगलमा समीक्षा लेख्नुहोस्",
    "View on Google Maps": "गुगल म्यापमा हेर्नुहोस्",

    # Cleaned Service Workflows & Steps
    "CLINICAL WORKFLOW": "क्लिनिकल कार्यप्रवाह",
    "Clinical Workflow": "क्लिनिकल कार्यप्रवाह",
    "Our Patient Care Process": "हाम्रो बिरामी सेवा प्रक्रिया",
    "Appointment Booking": "अपोइन्टमेन्ट बुकिङ",
    "Consultation": "परामर्श",
    "Oral Examination": "मौखिक परीक्षा",
    "Accurate Diagnosis": "सटीक निदान",
    "Custom Plan": "अनुकूलन योजना",
    "Follow-up Care": "फलो-अप हेरचाह",
    "Treatment Pricing": "उपचार मूल्य निर्धारण",
    "Transparent, Ethical & Fair Rates": "पारदर्शी, नैतिक र उचित दरहरू",
    "Registration & Basic Check-up": "दर्ता र आधारभूत जाँच",
    "Includes digital file setup & exam": "डिजिटल फाइल सेटअप र परीक्षा समावेश छ",
    "Doctor Consultation": "डाक्टर परामर्श",
    "In-depth clinical discussion & advice": "गहन क्लिनिकल छलफल र सल्लाह",
    "Schedule Check-up": "अनुसूची चेक-अप",
    "Schedule Your Check-up": "अनुसूची चेक-अप",
    "What to Expect During Your General Check-up": "साधारण जाँचको बेला के अपेक्षा गर्ने",
    "PATIENT PREPARATION & EXPECTATIONS": "बिरामी तयारी र अपेक्षाहरू",
    "20–30 Minutes Duration": "२०–३० मिनेट अवधि",
    "100% Pain-Free & Gentle": "१००% दुखाइरहित र कोमल",
    "No Judgement Promise": "कुनै न्याय नगरिने वाचा",

    # Digital X-Ray
    "DIAGNOSTIC WORKFLOW": "डायग्नोस्टिक कार्यप्रवाह",
    "Our Digital X-Ray Process": "हाम्रो डिजिटल एक्स-रे प्रक्रिया",
    "Clinical Assessment": "क्लिनिकल मूल्याङ्कन",
    "Protective Setup": "सुरक्षा तयारी",
    "Fast Digital Capture": "द्रुत डिजिटल क्याप्चर",
    "Chairside Review": "चेयरसाइड समीक्षा",
    "Transparent Review": "पारदर्शी समीक्षा",
    "Targeted Care Plan": "लक्षित हेरचाह योजना",
    "X-Ray Diagnostics Pricing": "एक्स-रे डायग्नोस्टिक्स मूल्य निर्धारण",
    "Transparent & Fair Diagnostic Rates": "पारदर्शी र उचित डायग्नोस्टिक दरहरू",

    # Dental Filling
    "Our Filling Treatment Process": "हाम्रो दाँत भर्ने उपचार प्रक्रिया",
    "Examination & Scan": "परीक्षण र स्क्यान",
    "Gentle Numbing": "कोमल लठ्याउने कार्य",
    "Decay Removal": "किरा लागेको भाग हटाउने",
    "Enamel Bonding": "इनामेल बन्डिङ",
    "Layered Composite": "स्तरित कम्पोजिट",
    "Occlusal Polish": "अक्लुजल पालिस",
    "Filling Treatment Charges": "दाँत भर्ने सेवा शुल्क",

    # Dentures & Crowns & Bridges & RCT
    "Consultation & Impressions": "परामर्श र प्रभावहरू",
    "Bite Registration": "बाइट दर्ता",
    "Wax Try-In": "मोम परीक्षण",
    "Final Delivery": "अन्तिम डेलिभरी",
    "Preparation": "दाँतको तयारी",
    "Digital Impressions": "डिजिटल प्रभावहरू",
    "Temporary Placement": "अस्थायी क्याप",
    "Final Cementation": "अन्तिम सिमेन्टेसन",
    "Our Root Canal Process": "हाम्रो रूट क्यानल प्रक्रिया",
    "X-Ray & Diagnosis": "एक्स-रे र निदान",
    "Local Anesthesia": "स्थानीय एनेस्थेसिया",
    "Cleaning & Disinfection": "सफाइ र कीटाणुशोधन",
    "Root Canal Filling": "रूट क्यानल भर्ने कार्य",
    "Tooth Restoration": "दाँत पुनर्स्थापना",
    "Crown Placement": "क्याप (क्राउन) लगाउने",
}

def extract_strings_from_workspace():
    base_dir = Path(__file__).resolve().parent.parent
    extracted = set()

    # 1. HTML templates
    template_dir = base_dir / 'templates'
    for f in template_dir.rglob('*.html'):
        content = f.read_text(encoding='utf-8', errors='ignore')
        for m in re.findall(r'{%\s*trans\s+"([^"]+)"\s*%}', content):
            if m.strip():
                extracted.add(m.strip())
        for m in re.findall(r"{%\s*trans\s+'([^']+)'\s*%}", content):
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
        for m in re.findall(r'_\("([^"]+)"\)', content):
            if m.strip():
                extracted.add(m.strip())
        for m in re.findall(r"_\('([^']+)'\)", content):
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
