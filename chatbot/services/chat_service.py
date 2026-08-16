import logging
from typing import Dict, Any, Optional
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

logger = logging.getLogger(__name__)

class ChatService:
    """
    Master Conversation Service.
    Pipeline:
    1. Validate Session & Conversation State
    2. Run Pre-AI Safety Screening (Emergency, Red Flags, Prescription)
    3. Resolve Page Context & Pronouns
    4. Detect Intent & Execute Database Tools
    5. Fast-Path Deterministic Routing (Instant DB responses for hours, location, contact)
    6. Synthesize Natural AI Response (via Provider Abstraction)
    7. Graceful Fallback if AI unavailable
    8. Log Interactions & Analytics
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

        # Update latest page
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

        # 2. Safety Screening
        safety_eval = SafetyService.evaluate_user_message(cleaned_msg)
        if not safety_eval.is_safe:
            # Create safety response
            assistant_msg = ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=safety_eval.response_override,
                intent=f"SAFETY_{safety_eval.category.upper()}",
                quick_actions=safety_eval.quick_actions,
                cards=safety_eval.cards,
                metadata={'safety_triggered': True, 'category': safety_eval.category}
            )

            # Log interaction
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

        # 5. Database Tools Execution
        tool_data = ToolService.execute_tools_for_intent(intent, cleaned_msg, treatment_slug=resolved_treatment)

        # 6. Fast-Path Deterministic Routing (Instant DB replies without calling LLM)
        fast_path_response = cls._try_fast_path(intent, tool_data, resolved_treatment, cleaned_msg)
        if fast_path_response:
            assistant_msg = ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=fast_path_response['content'],
                intent=intent,
                quick_actions=fast_path_response.get('quick_actions', []),
                cards=fast_path_response.get('cards', []),
                metadata={'fast_path': True}
            )
            cls._log_interaction(conversation, intent, resolved_treatment, 'answer')
            return cls._format_response(assistant_msg)

        # 7. AI Provider Synthesis
        history = ContextService.get_recent_history(conversation, limit=6)
        provider = get_ai_provider()
        ai_resp = provider.generate_response(
            prompt=cleaned_msg,
            system_prompt=CAREFIRST_SYSTEM_PROMPT,
            context=tool_data,
            history=history
        )

        final_content = ""
        cards = []
        quick_actions = []

        if ai_resp.success and ai_resp.content:
            final_content = ai_resp.content
            # Attach structured cards based on intent and resolved treatment
            cards, quick_actions = cls._generate_supplementary_ui(intent, tool_data, resolved_treatment)
        else:
            # Fallback when AI fails or is offline
            logger.warning(f"AI Provider fallback triggered: {ai_resp.error_message}")
            final_content = cls._generate_offline_fallback(intent, tool_data, resolved_treatment)
            cards, quick_actions = cls._generate_supplementary_ui(intent, tool_data, resolved_treatment)

            # Record unanswered question for staff review
            UnansweredQuestion.objects.create(
                question=cleaned_msg,
                conversation=conversation,
                category=intent
            )

        # Save Assistant message
        assistant_msg = ChatMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=final_content,
            intent=intent,
            quick_actions=quick_actions,
            cards=cards,
            metadata={'provider': provider.__class__.__name__, 'ai_success': ai_resp.success}
        )

        cls._log_interaction(conversation, intent, resolved_treatment, 'answer')
        return cls._format_response(assistant_msg)

    @classmethod
    def _try_fast_path(cls, intent: str, tool_data: Dict[str, Any], treatment_slug: Optional[str], message: str) -> Optional[Dict[str, Any]]:
        clinic = tool_data.get('clinic', {})

        if intent == 'OPENING_HOURS':
            return {
                'content': (
                    f"⏰ **CareFirst Dental Clinic Opening Hours:**\n\n"
                    f"We are open **7 days a week (Monday to Sunday)** from **7:30 AM to 7:30 PM**.\n\n"
                    f"Both morning consultations and evening after-work visits are available."
                ),
                'quick_actions': ["Book Appointment", "Call Clinic", "Location & Directions"],
                'cards': [{
                    'type': 'clinic_card',
                    'title': 'CareFirst Dental Clinic',
                    'hours': clinic.get('opening_hours'),
                    'phone': clinic.get('primary_phone'),
                    'location': clinic.get('location')
                }]
            }

        elif intent == 'LOCATION':
            return {
                'content': (
                    f"📍 **CareFirst Dental Clinic Location:**\n\n"
                    f"**Address:** Pragatinagar Road, Shankhamul-31, Kathmandu 44600\n"
                    f"*(Conveniently situated near the Shankhamul / New Baneshwor junction)*\n\n"
                    f"We have modern on-site operatory suites with convenient patient parking."
                ),
                'quick_actions': ["Get Directions", "Call Clinic (+977 9807464136)", "Book Visit"],
                'cards': [{
                    'type': 'map_card',
                    'title': 'CareFirst Kathmandu Clinic',
                    'address': clinic.get('location'),
                    'hours': clinic.get('opening_hours'),
                    'google_maps_url': 'https://maps.app.goo.gl/9Z7Z1v6v4X'
                }]
            }

        elif intent == 'CONTACT':
            return {
                'content': (
                    f"📞 **Contact CareFirst Dental Clinic:**\n\n"
                    f"• **Mobile / Emergency:** [{clinic.get('primary_phone')}](tel:{clinic.get('primary_phone', '').replace(' ', '')})\n"
                    f"• **Landline:** [{clinic.get('secondary_phone')}](tel:{clinic.get('secondary_phone', '')})\n"
                    f"• **Email:** `{clinic.get('email')}`\n"
                    f"• **WhatsApp:** Instant direct messaging available.\n\n"
                    f"Our clinical reception team is available daily from 7:30 AM to 7:30 PM."
                ),
                'quick_actions': ["WhatsApp Consultation", "Call Now", "Book Appointment Online"],
                'cards': [{
                    'type': 'contact_card',
                    'phone': clinic.get('primary_phone'),
                    'secondary_phone': clinic.get('secondary_phone'),
                    'whatsapp_url': clinic.get('whatsapp_link')
                }]
            }

        elif intent == 'APPOINTMENT' and 'book' in message.lower() and not treatment_slug:
            return {
                'content': (
                    "🗓️ **Schedule Your CareFirst Consultation:**\n\n"
                    "I can help you submit an appointment request directly. "
                    "Which dental treatment or consultation would you like to visit us for?"
                ),
                'quick_actions': [
                    "General Check-up",
                    "Scaling & Polishing",
                    "Dental Filling",
                    "Root Canal (RCT)",
                    "Dental Implants",
                    "Braces / Aligners"
                ],
                'cards': [{
                    'type': 'appointment_launcher',
                    'title': 'Start Appointment Request',
                    'treatment': 'General Check-up'
                }]
            }

        return None

    @classmethod
    def _generate_supplementary_ui(cls, intent: str, tool_data: Dict[str, Any], treatment_slug: Optional[str]):
        cards = []
        quick_actions = []

        if intent == 'TREATMENT_PRICE' or (tool_data.get('pricing') and tool_data['pricing'].get('found')):
            pricing = tool_data.get('pricing', {})
            cards.append({
                'type': 'pricing_card',
                'treatment': pricing.get('treatment'),
                'starting_price': pricing.get('starting_price'),
                'items': pricing.get('items', [])[:4],
                'note': pricing.get('note')
            })
            quick_actions = ["Estimate Cost (2+ teeth)", "Book Consultation", "WhatsApp CareFirst", "Other Treatments"]

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
            quick_actions = ["View Pricing", "Book Appointment", "Meet Doctor", "Ask Another Question"]

        elif tool_data.get('doctors'):
            docs = tool_data['doctors']
            cards.append({
                'type': 'doctor_card',
                'doctors': docs[:2]
            })
            quick_actions = ["Book with Dr. Subash", "Clinic Location", "Treatment Pricing"]

        else:
            quick_actions = ["Our Treatments", "Treatment Prices", "Book Appointment", "Clinic Contact"]

        return cards, quick_actions

    @classmethod
    def _generate_offline_fallback(cls, intent: str, tool_data: Dict[str, Any], treatment_slug: Optional[str]) -> str:
        clinic = tool_data.get('clinic', {})
        if tool_data.get('current_treatment_details'):
            details = tool_data['current_treatment_details']
            return (
                f"**{details['name']}** at CareFirst Dental Clinic starts from **{details['starting_price']}**.\n\n"
                f"Our clinical team led by Dr. Subash Banjade (BDS, NMC #31229) utilizes modern digital imaging and hospital-grade sterilization for gentle, precision care.\n\n"
                f"Would you like to schedule an oral consultation or speak directly with our team?"
            )
        
        return (
            f"At CareFirst Dental Clinic in Shankhamul, Kathmandu, we provide international-standard dental care 7 days a week (7:30 AM – 7:30 PM).\n\n"
            f"Please contact our team directly at **{clinic.get('primary_phone')}** or book an appointment online."
        )

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
