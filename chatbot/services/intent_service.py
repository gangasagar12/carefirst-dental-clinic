import re
from typing import Optional

class IntentService:
    """
    Deterministic intent classification pipeline with full bilingual (English & Nepali) keyword recognition.
    """

    INTENT_KEYWORDS = {
        'TOOTH_PAIN': [
            r'\b(pain|hurts|hurting|ache|aching|toothache|swelling|swollen|bleed|bleeding|sensitive|sensitivity|broken|cavity|decay|wisdom tooth|emergency|dant dukh|dukheko)\b',
            r'(दाँत दुख्|दुखेको|सुन्निएको|रगत आएको|भाँचिएको|किरा लागेको|झरेको|असह्य दुखाइ)'
        ],
        'TREATMENT_PRICE': [
            r'\b(how much|cost|price|pricing|charge|fee|rate|estimate|expensive|cheap|how much for|cost of|what does it cost|budget|rs|npr|paisa)\b',
            r'(कति पर्छ|मूल्य|शुल्क|खर्च|दर|पैसा|कति लाग्छ)'
        ],
        'APPOINTMENT': [
            r'\b(book|appointment|schedule|consult|visit|see dentist|slot|reserve|book appointment|fix date|time slot|register)\b',
            r'(अपोइन्टमेन्ट|समय लिन|भेट्ने|दर्ता|पालो|बुकिङ|समय मिलाउन)'
        ],
        'OPENING_HOURS': [
            r'\b(hours|time|timing|timings|open|close|closing|working hours|sunday open|saturday open|when open|schedule)\b',
            r'(कहिले खुल्छ|समय|खुल्ने समय|खुला|बन्द|शनिबार|आइतबार)'
        ],
        'LOCATION': [
            r'\b(location|address|where are you|where clinic|directions|map|shankhamul|baneshwor|how to reach|where is carefirst|place)\b',
            r'(ठेगाना|कहाँ छ|स्थान|शंखमूल|बानेश्वर|पुग्ने बाटो|लोकेसन)'
        ],
        'CONTACT': [
            r'\b(phone|call|mobile|telephone|contact number|email|whatsapp|how to contact|get in touch|viber)\b',
            r'(फोन|सम्पर्क|मोबाइल|इमेल|ह्वाट्सएप|नम्बर)'
        ],
        'DOCTOR_INFORMATION': [
            r'\b(doctor|dentist|surgeon|dr|subash|banjade|qualification|experience|specialist|who operates|team|doctors)\b',
            r'(डाक्टर|चिकित्सक|सुवास|बन्जाडे|योग्यता|अनुभव|विशेषज्ञ)'
        ],
        'SERVICES_LIST': [
            r'\b(what services|treatments available|all services|what do you do|service list|treatments list|all treatments)\b',
            r'(के के सेवा|उपचारहरू|दन्त सेवाहरू|सुविधाहरू|सबै सेवा)'
        ],
        'GREETING': [
            r'^(hi|hello|hey|namaste|good morning|good afternoon|good evening|howdy|hola|yo|k chha|k cha)\b',
            r'\b(who are you|what can you do|help me|how can you help)\b',
            r'(नमस्ते|नमस्कार|हेलो|हाई|के छ|सञ्चै)'
        ],
        'TREATMENT_DURATION': [
            r'\b(how long|duration|how many visits|how many sessions|how much time does it take|recovery time|timeline)\b',
            r'(कति समय लाग्छ|कति दिन|कति पटक जानुपर्छ|समय कति)'
        ],
        'TREATMENT_PROCESS': [
            r'\b(procedure|process|steps|how is it done|how does it work|painful|does it hurt|pain free|anesthesia|safe)\b',
            r'(कसरी गरिन्छ|दुख्छ कि|विधि|प्रक्रिया|दुखाइ हुन्छ)'
        ],
        'FAQ': [
            r'\b(faq|question|safe|side effects|aftercare|precautions|is scaling bad|does rct hurt)\b',
            r'(प्रश्न|सोधपुछ|सुरक्षित|सावधानी)'
        ],
        'REVIEW': [
            r'\b(review|rating|feedback|testimonial|experience|what do patients say|is it good)\b',
            r'(प्रतिक्रिया|समीक्षा|अनुभव|कस्तो छ)'
        ],
        'WHATSAPP': [
            r'\b(whatsapp|chat on whatsapp|message on whatsapp)\b',
            r'(ह्वाट्सएप)'
        ],
        'TREATMENT_INFORMATION': [
            r'\b(what is|tell me about|information on|details of|explain|types of)\b',
            r'(के हो|जानकारी|विवरण|बारेमा)'
        ]
    }

    @classmethod
    def detect_intent(cls, message: str, current_treatment: Optional[str] = None) -> str:
        text = message.lower().strip()

        # Check in priority order
        for intent, patterns in cls.INTENT_KEYWORDS.items():
            for pat in patterns:
                if re.search(pat, text, re.IGNORECASE):
                    return intent

        # If user names a specific treatment directly
        treatments = [
            'filling', 'implant', 'rct', 'root canal', 'brace', 'aligner',
            'scaling', 'polishing', 'whitening', 'crown', 'bridge', 'extraction',
            'wisdom', 'denture', 'xray', 'x-ray', 'gum', 'दाँत', 'इम्प्लान्ट', 'ब्रेसेस'
        ]
        if any(t in text for t in treatments):
            return 'TREATMENT_INFORMATION'

        return 'GENERAL_DENTAL_INFORMATION'
