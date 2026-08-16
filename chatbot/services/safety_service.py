import re
from typing import Dict, Any, Optional

class SafetyEvaluationResult:
    def __init__(self, is_safe: bool, category: Optional[str] = None, response_override: Optional[str] = None, quick_actions: Optional[list] = None, cards: Optional[list] = None):
        self.is_safe = is_safe
        self.category = category
        self.response_override = response_override
        self.quick_actions = quick_actions or []
        self.cards = cards or []


class SafetyService:
    """
    Independent clinical safety & red-flag evaluation engine.
    Screens inputs before calling AI and validates outputs before returning to user.
    """

    # Red-flag keywords for urgent emergencies
    EMERGENCY_PATTERNS = [
        r'\b(facial swelling|swollen face|swollen eye|swelling in face)\b',
        r'\b(uncontrolled bleeding|won\'?t stop bleeding|heavy bleeding|bleeding profusely)\b',
        r'\b(knocked out tooth|avulsed tooth|broken jaw|jaw fracture|trauma)\b',
        r'\b(can\'?t swallow|cannot swallow|difficulty swallowing|difficulty breathing)\b',
        r'\b(severe unbearable pain|extreme agony|fainted|high fever with swelling)\b',
    ]

    # Medication and self-prescription patterns
    MEDICATION_PATTERNS = [
        r'\b(what antibiotic|which antibiotic|amoxicillin|metronidazole|augmentin|ciprofloxacin|doxycycline)\b',
        r'\b(prescribe|how many mg|what dosage|how much dose|give me medicine|write a prescription)\b',
        r'\b(painkiller dosage|ibuprofen dose|paracetamol dose|tramadol|ketorol)\b',
    ]

    # Diagnosis seeking patterns
    DIAGNOSIS_PATTERNS = [
        r'\b(what disease do i have|do i have oral cancer|is this cancer|diagnose my|why is my tongue white)\b',
        r'\b(tell me what illness|is this malignant|diagnose me)\b',
    ]

    # Prompt injection / malicious patterns
    INJECTION_PATTERNS = [
        r'\b(ignore previous instructions|disregard previous|system prompt|admin password|database credentials|api key)\b',
    ]

    @classmethod
    def evaluate_user_message(cls, message: str) -> SafetyEvaluationResult:
        """
        Evaluates incoming patient messages against clinical safety filters.
        """
        text = message.lower().strip()

        # 1. Check prompt injection / system security
        for pat in cls.INJECTION_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                return SafetyEvaluationResult(
                    is_safe=False,
                    category='security_prompt_injection',
                    response_override=(
                        "I am Ask CareFirst, the dental patient assistant. I am here to help you learn about "
                        "CareFirst treatments, prices, appointments, and clinic information. How can I assist you with your dental care today?"
                    ),
                    quick_actions=["Our Treatments", "Treatment Pricing", "Book Appointment", "Contact Clinic"]
                )

        # 2. Check emergency symptoms
        for pat in cls.EMERGENCY_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                return SafetyEvaluationResult(
                    is_safe=False,
                    category='emergency',
                    response_override=(
                        "⚠️ **Important Clinical Notice:**\n\n"
                        "Your symptoms (such as significant swelling, trauma, acute bleeding, or difficulty breathing) "
                        "warrant **prompt in-person assessment** by a dental surgeon.\n\n"
                        "Please contact CareFirst Dental Clinic immediately or visit our Shankhamul center or the nearest emergency medical facility."
                    ),
                    quick_actions=["Call Clinic Now", "WhatsApp Emergency", "Book Immediate Slot"],
                    cards=[{
                        'type': 'emergency_contact',
                        'title': 'CareFirst Emergency Dental Care',
                        'phone': '+977 980-7464136',
                        'alt_phone': '01-5916886',
                        'whatsapp_url': 'https://wa.me/9779807464136?text=Urgent%20Dental%20Assistance%20Needed',
                        'address': 'Pragatinagar Road, Shankhamul-31, Kathmandu (Near New Baneshwor)'
                    }]
                )

        # 3. Check medication and prescription queries
        for pat in cls.MEDICATION_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                return SafetyEvaluationResult(
                    is_safe=False,
                    category='medication',
                    response_override=(
                        "💊 **Medication Safety Notice:**\n\n"
                        "I cannot prescribe antibiotics, painkillers, or recommend specific dosages. "
                        "Antibiotics and dental medications require a physical clinical assessment by a licensed dentist "
                        "(such as Dr. Subash Banjade at CareFirst) to diagnose the root cause of infection and ensure safe administration.\n\n"
                        "Would you like to schedule a consultation with our dental team?"
                    ),
                    quick_actions=["Book Consultation", "Call Clinic (+977 9807464136)", "WhatsApp CareFirst"],
                    cards=[{
                        'type': 'contact_action',
                        'title': 'Consult a CareFirst Dental Surgeon',
                        'phone': '+977 980-7464136',
                        'whatsapp_url': 'https://wa.me/9779807464136?text=Consultation%20Inquiry'
                    }]
                )

        # 4. Check medical diagnosis demands
        for pat in cls.DIAGNOSIS_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                return SafetyEvaluationResult(
                    is_safe=False,
                    category='diagnosis',
                    response_override=(
                        "🩺 **Clinical Evaluation Notice:**\n\n"
                        "I am an educational assistant and cannot diagnose medical or dental conditions through chat. "
                        "Dental conditions can have multiple clinical causes that require direct visual inspection, vitality tests, "
                        "or low-radiation digital RVG X-rays.\n\n"
                        "We invite you to visit CareFirst Dental Clinic in Shankhamul, Kathmandu for an accurate and comprehensive oral examination."
                    ),
                    quick_actions=["Book Oral Examination", "Meet Our Doctors", "Clinic Location"]
                )

        return SafetyEvaluationResult(is_safe=True)
