import logging
import re
from typing import Dict, Any, Optional, List
from django.utils import timezone
from django.urls import reverse

from chatbot.models import Conversation, ChatMessage, ChatInteraction, UnansweredQuestion
from chatbot.services.safety_service import SafetyService
from chatbot.services.intent_service import IntentService
from chatbot.services.context_service import ContextService
from chatbot.services.tool_service import ToolService
from chatbot.providers import get_ai_provider
from chatbot.prompts.system_prompt import CAREFIRST_SYSTEM_PROMPT
from chatbot.tools.appointment_tools import generate_whatsapp_link
from main.models import Service, PricingCategory, PricingItem, Doctor, FAQ, SiteSettings

logger = logging.getLogger(__name__)

def is_nepali_text(text: str, current_page: str = '') -> bool:
    """Checks if text contains Devanagari or user is browsing /ne/ page."""
    if '/ne/' in current_page or current_page.startswith('/ne'):
        return True
    return bool(re.search(r'[\u0900-\u097F]', text))


class ChatService:
    """
    CareFirst Dental AI Patient Assistant.
    Calls the live AI LLM model dynamically for all questions with real-time clinic database context.
    """

    @classmethod
    def process_message(
        cls,
        session_id: str,
        message: str,
        current_page: str = '/',
        current_treatment: str = '',
        user=None,
        utm_params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        cleaned_msg = message.strip()
        if not cleaned_msg:
            return {'error': 'Empty message received.'}

        is_ne = is_nepali_text(cleaned_msg, current_page)

        # 1. Retrieve or initialize Conversation
        conversation, _ = Conversation.objects.get_or_create(
            session_id=session_id,
            status='active',
            defaults={
                'user': user if user and user.is_authenticated else None,
                'current_page': current_page,
                'current_treatment': current_treatment,
                'landing_page': current_page,
                'utm_source': (utm_params or {}).get('utm_source', ''),
                'utm_medium': (utm_params or {}).get('utm_medium', ''),
                'utm_campaign': (utm_params or {}).get('utm_campaign', ''),
            }
        )

        if current_page:
            conversation.current_page = current_page
        if current_treatment:
            conversation.current_treatment = current_treatment
        conversation.save(update_fields=['current_page', 'current_treatment', 'updated_at'])

        # Save incoming User message
        ChatMessage.objects.create(
            conversation=conversation,
            role='user',
            content=cleaned_msg
        )

        # 2. Pre-AI Safety Screening (Medical emergency red-flags)
        safety_eval = SafetyService.evaluate_user_message(cleaned_msg)
        if not safety_eval.is_safe:
            assistant_msg = ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=safety_eval.response_override,
                intent=f"SAFETY_{safety_eval.category.upper()}",
                quick_actions=safety_eval.quick_actions,
                cards=safety_eval.cards,
                metadata={'safety_triggered': True, 'category': safety_eval.category}
            )
            ChatInteraction.objects.create(
                conversation=conversation,
                intent=f"SAFETY_{safety_eval.category.upper()}",
                action='emergency_alerted' if safety_eval.category == 'emergency' else 'answer',
                extra_data={'category': safety_eval.category}
            )
            return cls._format_response(assistant_msg)

        # 3. Context & Treatment Resolution
        resolved_treatment = ContextService.resolve_treatment_context(
            cleaned_msg,
            current_page=current_page,
            current_treatment=current_treatment,
            conversation=conversation
        )
        if resolved_treatment:
            conversation.current_treatment = resolved_treatment
            conversation.save(update_fields=['current_treatment'])

        # 4. Intent Detection
        intent = IntentService.detect_intent(cleaned_msg, current_treatment=resolved_treatment)

        # 5. Database Tools Execution (Gathers real-time verified prices, doctors, hours)
        tool_data = ToolService.execute_tools_for_intent(intent, cleaned_msg, treatment_slug=resolved_treatment)

        # 6. Live AI Model Generation (Real-time LLM inference)
        history = ContextService.get_recent_history(conversation, limit=6)
        provider = get_ai_provider()
        ai_resp = None

        try:
            ai_resp = provider.generate_response(
                prompt=cleaned_msg,
                system_prompt=CAREFIRST_SYSTEM_PROMPT,
                context=tool_data,
                history=history
            )
        except Exception as e:
            logger.warning(f"AI Provider execution error: {e}")

        final_content = ""
        cards = []
        quick_actions = []

        if ai_resp and ai_resp.success and ai_resp.content:
            final_content = ai_resp.content
            cards, quick_actions = cls._generate_supplementary_ui(intent, tool_data, resolved_treatment, is_ne=is_ne)
        else:
            # Fallback only if live AI endpoint is offline or rate-limited
            clinic = tool_data.get('clinic', {})
            phone = clinic.get('primary_phone', '+977 9807464136')
            if is_ne:
                final_content = (
                    f"केयरफर्स्ट डेन्टल क्लिनिक (शंखमूल, काठमाडौँ) मा स्वागत छ।\n\n"
                    f"तपाईंको प्रश्न सम्बन्धी थप जानकारी वा डाक्टरसँग भेट्न **{phone}** मा कल गर्नुहोस् वा अनलाइन अपोइन्टमेन्ट लिनुहोस्।"
                )
                quick_actions = ["अपोइन्टमेन्ट लिनुहोस्", "क्लिनिकमा कल गर्नुहोस्", "शुल्क विवरण", "ह्वाट्सएप"]
            else:
                final_content = (
                    f"Welcome to CareFirst Dental Clinic (Shankhamul, Kathmandu).\n\n"
                    f"For personalized guidance or to consult Dr. Subash Banjade and our team, please contact us at **{phone}** or book an appointment online."
                )
                quick_actions = ["Book Appointment", "Call Clinic", "Treatment Pricing", "WhatsApp Us"]

        assistant_msg = ChatMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=final_content,
            intent=intent,
            quick_actions=quick_actions,
            cards=cards,
            metadata={'provider': provider.__class__.__name__, 'ai_success': (ai_resp.success if ai_resp else False)}
        )

        cls._log_interaction(conversation, intent, resolved_treatment, 'answer')
        return cls._format_response(assistant_msg)

    @classmethod
    def _generate_supplementary_ui(
        cls,
        intent: str,
        tool_data: Dict[str, Any],
        treatment_slug: Optional[str],
        is_ne: bool = False
    ):
        cards = []
        if is_ne:
            quick_actions = ["अपोइन्टमेन्ट लिनुहोस्", "उपचार शुल्क", "दाँतको दुखाइ सल्लाह", "क्लिनिक सम्पर्क"]
        else:
            quick_actions = ["Book Appointment", "Treatment Prices", "Tooth Pain Advice", "Clinic Contact"]

        if intent == 'TREATMENT_PRICE' or (tool_data.get('pricing') and tool_data['pricing'].get('found')):
            pricing = tool_data.get('pricing', {})
            cards.append({
                'type': 'pricing_card',
                'treatment': pricing.get('treatment'),
                'starting_price': pricing.get('starting_price'),
                'items': pricing.get('items', [])[:4],
                'note': pricing.get('note')
            })
            quick_actions = ["अपोइन्टमेन्ट लिनुहोस्", "ह्वाट्सएपमा बुझ्नुहोस्", "अन्य उपचारहरू"] if is_ne else ["Book Consultation", "WhatsApp CareFirst", "Other Treatments"]

        elif tool_data.get('current_treatment_details'):
            details = tool_data['current_treatment_details']
            cards.append({
                'type': 'treatment_card',
                'name': details.get('name'),
                'category': details.get('category'),
                'starting_price': details.get('starting_price'),
                'url': details.get('url'),
                'features': details.get('features', [])[:3]
            })

        return cards, quick_actions

    @classmethod
    def _log_interaction(cls, conversation: Conversation, intent: str, treatment: Optional[str], action: str):
        try:
            ChatInteraction.objects.create(
                conversation=conversation,
                intent=intent,
                treatment=treatment or '',
                action=action
            )
        except Exception:
            pass

    @classmethod
    def _format_response(cls, message: ChatMessage) -> Dict[str, Any]:
        return {
            'id': message.id,
            'role': message.role,
            'content': message.content,
            'intent': message.intent,
            'quick_actions': message.quick_actions,
            'cards': message.cards,
            'created_at': message.created_at.strftime('%I:%M %p')
        }
