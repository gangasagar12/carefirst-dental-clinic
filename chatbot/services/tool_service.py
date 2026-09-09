from typing import Dict, Any, Optional
from main.models import Doctor, Service, SiteSettings, PricingCategory
from chatbot.tools.treatment_tools import get_treatment, search_treatments, get_related_treatments
from chatbot.tools.pricing_tools import get_treatment_price, calculate_cost_estimate
from chatbot.tools.doctor_tools import get_doctor_information
from chatbot.tools.clinic_tools import get_clinic_information
from chatbot.tools.appointment_tools import generate_whatsapp_link
from chatbot.tools.faq_tools import search_faq
from chatbot.tools.review_tools import get_treatment_reviews

class ToolService:
    """
    Business logic orchestrator connecting intent & context to dynamic Django database tools.
    """

    @classmethod
    def execute_tools_for_intent(cls, intent: str, message: str, treatment_slug: Optional[str] = None) -> Dict[str, Any]:
        # 1. Fetch dynamic live doctors snapshot
        active_doctors = []
        for doc in Doctor.objects.filter(is_active=True).order_by('order', 'name'):
            active_doctors.append({
                'name': f"Dr. {doc.name}",
                'designation': doc.designation,
                'specialty': doc.get_specialty_display(),
                'qualifications': doc.qualifications,
                'nmc_number': doc.nmc_number,
                'bio': doc.bio,
            })

        # 2. Fetch dynamic live services & pricing snapshot
        active_services = []
        for s in Service.objects.filter(is_active=True).order_by('order', 'title'):
            active_services.append({
                'name': s.title,
                'slug': s.slug,
                'category': s.get_category_display(),
                'price_npr': s.get_dynamic_price(),
                'features': s.get_features_list()[:3],
            })

        context_data = {
            'clinic': get_clinic_information(),
            'doctors_team': active_doctors,
            'services_and_pricing': active_services,
            'intent': intent,
        }

        # 3. Treatment-specific Context
        if treatment_slug:
            treatment_info = get_treatment(treatment_slug)
            if treatment_info:
                context_data['current_treatment_details'] = treatment_info
                context_data['related_treatments'] = get_related_treatments(treatment_slug)
                context_data['pricing'] = get_treatment_price(treatment_slug)
                context_data['whatsapp_url'] = generate_whatsapp_link(treatment_info['name'])

        # 4. Intent-specific tool executions
        if intent == 'TREATMENT_PRICE':
            slug = treatment_slug or message
            context_data['pricing'] = get_treatment_price(slug)
            if treatment_slug:
                context_data['whatsapp_url'] = generate_whatsapp_link(treatment_slug, topic="Pricing Inquiry")

        elif intent in ('TREATMENT_INFORMATION', 'TREATMENT_PROCESS', 'TREATMENT_DURATION'):
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

