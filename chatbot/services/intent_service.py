import re
from typing import Optional

class IntentService:
    """
    Deterministic intent classification pipeline with fallback.
    Identifies patient intent instantly to enable direct DB routing.
    """

    INTENT_KEYWORDS = {
        'GREETING': [
            r'^(hi|hello|hey|namaste|good morning|good afternoon|good evening|howdy|hola|yo)\b',
            r'\b(who are you|what can you do|help me)\b'
        ],
        'TREATMENT_PRICE': [
            r'\b(how much|cost|price|pricing|charge|fee|rate|estimate|expensive|cheap|how much for|cost of|what does it cost)\b',
        ],
        'APPOINTMENT': [
            r'\b(book|appointment|schedule|consult|visit|see dentist|slot|reserve|book appointment|fix date)\b',
        ],
        'OPENING_HOURS': [
            r'\b(hours|time|timing|timings|open|close|closing|working hours|sunday open|saturday open|when open)\b',
        ],
        'LOCATION': [
            r'\b(location|address|where are you|where clinic|directions|map|shankhamul|baneshwor|how to reach|where is carefirst)\b',
        ],
        'CONTACT': [
            r'\b(phone|call|mobile|telephone|contact number|email|whatsapp|how to contact|get in touch)\b',
        ],
        'DOCTOR_INFORMATION': [
            r'\b(doctor|dentist|surgeon|dr|subash|banjade|qualification|experience|specialist|who operates|team)\b',
        ],
        'TREATMENT_DURATION': [
            r'\b(how long|duration|how many visits|how many sessions|how much time does it take|recovery time)\b',
        ],
        'TREATMENT_PROCESS': [
            r'\b(procedure|process|steps|how is it done|how does it work|painful|does it hurt|pain free|anesthesia)\b',
        ],
        'TREATMENT_BENEFITS': [
            r'\b(benefit|benefits|advantage|why should i|advantages|is it worth)\b',
        ],
        'FAQ': [
            r'\b(faq|question|safe|side effects|aftercare|precautions)\b',
        ],
        'REVIEW': [
            r'\b(review|rating|feedback|testimonial|experience|what do patients say)\b',
        ],
        'WHATSAPP': [
            r'\b(whatsapp|chat on whatsapp|message on whatsapp)\b',
        ],
        'TREATMENT_INFORMATION': [
            r'\b(what is|tell me about|information on|details of|explain|types of)\b',
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
            'wisdom', 'denture', 'xray', 'x-ray', 'gum'
        ]
        if any(t in text for t in treatments):
            return 'TREATMENT_INFORMATION'

        return 'GENERAL_DENTAL_INFORMATION'
