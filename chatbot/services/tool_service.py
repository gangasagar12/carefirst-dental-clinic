from typing import Dict, Any, Optional
from chatbot.tools.treatment_tools import get_treatment, search_treatments, get_related_treatments
from chatbot.tools.pricing_tools import get_treatment_price, calculate_cost_estimate
from chatbot.tools.doctor_tools import get_doctor_information
from chatbot.tools.clinic_tools import get_clinic_information
from chatbot.tools.appointment_tools import generate_whatsapp_link
from chatbot.tools.faq_tools import search_faq
from chatbot.tools.review_tools import get_treatment_reviews

class ToolService:
    """
    Business logic orchestrator connecting intent & context to Django database tools.
    """

    @classmethod
    def execute_tools_for_intent(cls, intent: str, message: str, treatment_slug: Optional[str] = None) -> Dict[str, Any]:
        context_data = {
            'clinic': get_clinic_information(),
            'intent': intent,
        }

        # 1. Treatment Context
        if treatment_slug:
            treatment_info = get_treatment(treatment_slug)
            if treatment_info:
                context_data['current_treatment_details'] = treatment_info
                context_data['related_treatments'] = get_related_treatments(treatment_slug)
                context_data['pricing'] = get_treatment_price(treatment_slug)
                context_data['whatsapp_url'] = generate_whatsapp_link(treatment_info['name'])

        # 2. Intent-specific tool executions
        if intent == 'TREATMENT_PRICE':
            slug = treatment_slug or message
            context_data['pricing'] = get_treatment_price(slug)
            if treatment_slug:
                context_data['whatsapp_url'] = generate_whatsapp_link(treatment_slug, topic="Pricing Inquiry")

        elif intent == 'TREATMENT_INFORMATION' or intent == 'TREATMENT_PROCESS' or intent == 'TREATMENT_DURATION':
            if not treatment_slug:
                found_treatments = search_treatments(message)
                context_data['search_results'] = found_treatments
            else:
                context_data['treatment_faqs'] = search_faq(treatment_slug)

        elif intent == 'DOCTOR_INFORMATION':
            context_data['doctors'] = get_doctor_information(message)

        elif intent == 'FAQ':
            context_data['faqs'] = search_faq(message)

        elif intent == 'REVIEW':
            context_data['reviews'] = get_treatment_reviews(treatment_slug)

        elif intent == 'WHATSAPP':
            context_data['whatsapp_url'] = generate_whatsapp_link(treatment_slug or '')

        return context_data
