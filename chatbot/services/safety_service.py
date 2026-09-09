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
    Clinical safety & prompt security screening.
    Intercepts security threats and critical life-threatening emergencies while
    allowing all dental questions, symptoms, and general knowledge queries to flow dynamically to AI.
    """

    # Critical life-threatening emergencies requiring immediate hospital/clinic triage
    CRITICAL_EMERGENCY_PATTERNS = [
        r'\b(uncontrolled bleeding|won\'?t stop bleeding|bleeding profusely|hemorrhage)\b',
        r'\b(broken jaw|jaw fracture|severe facial trauma|knocked out unconscious)\b',
        r'\b(can\'?t breathe|cannot breathe|difficulty breathing|throat closing)\b',
    ]

    # Prompt injection / malicious system access attempts
    INJECTION_PATTERNS = [
        r'\b(ignore previous instructions|disregard previous|system prompt|admin password|database credentials|api key|bypass safety)\b',
    ]

    @classmethod
    def evaluate_user_message(cls, message: str) -> SafetyEvaluationResult:
        """
        Evaluates incoming patient messages.
        """
        text = message.lower().strip()

        # 1. Prompt Injection / Malicious attempts
        for pat in cls.INJECTION_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                return SafetyEvaluationResult(
                    is_safe=False,
                    category='security_prompt_injection',
                    response_override=(
                        "Hello! I am Ask CareFirst, your AI Patient Assistant for CareFirst Dental Clinic. "
                        "How can I assist you with your dental health, treatments, appointments, or questions today?"
                    ),
                    quick_actions=["Our Treatments", "Treatment Pricing", "Book Appointment", "Contact Clinic"]
                )

        # 2. Critical acute life-threatening emergency
        for pat in cls.CRITICAL_EMERGENCY_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                return SafetyEvaluationResult(
                    is_safe=False,
                    category='emergency',
                    response_override=(
                        "⚠️ **Immediate Dental Emergency Alert:**\n\n"
                        "For severe emergencies like uncontrolled bleeding, difficulty breathing, or severe facial trauma, "
                        "please contact CareFirst Dental Clinic immediately at **+977 980-7464136** or visit our center in Shankhamul, Kathmandu, "
                        "or the nearest emergency hospital immediately."
                    ),
                    quick_actions=["Call Clinic Now", "WhatsApp Emergency", "Book Urgent Slot"],
                    cards=[{
                        'type': 'emergency_contact',
                        'title': 'CareFirst Emergency Dental Care',
                        'phone': '+977 980-7464136',
                        'alt_phone': '01-5916886',
                        'whatsapp_url': 'https://wa.me/9779807464136?text=Urgent%20Dental%20Assistance%20Needed',
                        'address': 'Pragatinagar Road, Shankhamul-31, Kathmandu (Near New Baneshwor)'
                    }]
                )

        # Allow all other dental symptoms, treatments, prices, general knowledge, science, and conversational queries to proceed to the AI
        return SafetyEvaluationResult(is_safe=True)

