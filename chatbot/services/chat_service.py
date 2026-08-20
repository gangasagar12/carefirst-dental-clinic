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
from chatbot.services.educational_kb import find_educational_concept

logger = logging.getLogger(__name__)

def is_nepali_text(text: str, current_page: str = '') -> bool:
    """Checks if text contains Devanagari or user is browsing /ne/ page."""
    if '/ne/' in current_page or current_page.startswith('/ne'):
        return True
    return bool(re.search(r'[\u0900-\u097F]', text))


class ChatService:
    """
    CareFirst Dental Clinical AI Assistant.
    Provides verified doctor-approved answers, real-time pricing from DB,
    emergency home care guidance, and seamless appointment booking.
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

        # 2. Safety Screening
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

        # 5. Database Tools Execution (Gather verified real-time context)
        tool_data = ToolService.execute_tools_for_intent(intent, cleaned_msg, treatment_slug=resolved_treatment)

        # 6. Live AI Model Generation (Real LLM Inference)
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
            logger.warning(f"AI Provider error: {e}")

        final_content = ""
        cards = []
        quick_actions = []

        if ai_resp and ai_resp.success and ai_resp.content:
            final_content = ai_resp.content
            cards, quick_actions = cls._generate_supplementary_ui(intent, tool_data, resolved_treatment, is_ne=is_ne)
        else:
            # Fallback to rich fast-path only if AI provider is unreachable
            fast_path_response = cls._try_fast_path(intent, tool_data, resolved_treatment, cleaned_msg, is_ne=is_ne)
            if fast_path_response:
                final_content = fast_path_response['content']
                quick_actions = fast_path_response.get('quick_actions', [])
                cards = fast_path_response.get('cards', [])
            else:
                final_content = cls._generate_smart_fallback(intent, tool_data, resolved_treatment, cleaned_msg, is_ne=is_ne)
                cards, quick_actions = cls._generate_supplementary_ui(intent, tool_data, resolved_treatment, is_ne=is_ne)

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
    def _try_fast_path(
        cls,
        intent: str,
        tool_data: Dict[str, Any],
        treatment_slug: Optional[str],
        message: str,
        is_ne: bool = False
    ) -> Optional[Dict[str, Any]]:
        clinic = tool_data.get('clinic', {})
        phone = clinic.get('primary_phone', '+977 9807464136')
        msg_lower = message.lower()

        # ==========================================
        # 1. GREETINGS
        # ==========================================
        if intent == 'GREETING':
            if is_ne:
                return {
                    'content': (
                        "👋 **नमस्ते! केयरफर्स्ट डेन्टल क्लिनिकमा स्वागत छ।**\n\n"
                        "म केयरफर्स्ट एआई सहायक हुँ। म तपाईंलाई दन्त उपचार, शुल्क विवरण, दुखाइ समाधान सल्लाह वा डाक्टरसँग अपोइन्टमेन्ट लिन सहयोग गर्न सक्छु।\n\n"
                        "💡 **तपाईं तलका कुनै पनि विषयमा सोध्न सक्नुहुन्छ:**\n"
                        "• उपचार शुल्क कति पर्छ? (RCT, फिलिङ, इम्प्लान्ट, आदि)\n"
                        "• दाँत दुखेको बेला के गर्ने?\n"
                        "• डाक्टर सुवास बन्जाडेको अनुभव तथा योग्यता\n"
                        "• क्लिनिक खुल्ने समय र ठेगाना"
                    ),
                    'quick_actions': ["अपोइन्टमेन्ट लिनुहोस्", "उपचार शुल्क हेर्नुहोस्", "दाँत दुख्ने सल्लाह", "क्लिनिक खुल्ने समय"],
                    'cards': []
                }
            return {
                'content': (
                    "👋 **Hello & Welcome to CareFirst Dental Clinic!**\n\n"
                    "I'm your CareFirst AI Dental Assistant. How can I help your smile today?\n\n"
                    "💡 **Popular topics you can ask me about:**\n"
                    "• **Treatment Prices** (e.g. RCT, Fillings, Implants, Braces, Scaling)\n"
                    "• **Tooth Pain & First-Aid Guidance**\n"
                    "• **Our Specialist Doctors** (Led by Dr. Subash Banjade, NMC #31229)\n"
                    "• **Clinic Opening Hours & Location**\n"
                    "• **Book an Appointment**"
                ),
                'quick_actions': ["Book Appointment", "Treatment Pricing", "Tooth Pain Help", "Opening Hours & Location"],
                'cards': []
            }

        # ==========================================
        # 2. TOOTH PAIN & SYMPTOM GUIDANCE
        # ==========================================
        elif intent == 'TOOTH_PAIN':
            if is_ne:
                return {
                    'content': (
                        "🦷 **दाँत दुखेको बेला तत्काल गर्नुपर्ने प्राथमिक उपचार सल्लाह:**\n\n"
                        "१. **मनतातो नुन पानीले कुल्ला गर्नुहोस्:** १ गिलास मनतातो पानीमा आधा चम्चा नुन मिसाएर बिस्तारै कुल्ला गर्नुहोस्।\n"
                        "२. **चिसो बरफको सेकाइ:** गाला बाहिरबाट १५ मिनेट बरफले सेक्नुहोस् (सुन्निएको कम गर्न मद्दत गर्छ)।\n"
                        "३. **के नगर्ने:** दुखेको दाँतमा सिधै पेनकिलर औषधि नराख्नुहोस् र धेरै चिसो वा तातो खाना नखानुहोस्।\n"
                        "४. **अत्यावश्यक सल्लाह:** दाँतको दुखाइ संक्रमण वा नशामा असर परेकाले हुनसक्छ। समयमै डाक्टरसँग परीक्षण गराउनुहोस्।\n\n"
                        f"📞 **तत्काल परामर्शको लागि कल गर्नुहोस्:** [{phone}](tel:{phone.replace(' ', '')})"
                    ),
                    'quick_actions': ["अपोइन्टमेन्ट लिनुहोस्", "क्लिनिकमा कल गर्नुहोस्", "ह्वाट्सएपमा कुरा गर्नुहोस्", "रूट क्यानल शुल्क"],
                    'cards': [{
                        'type': 'contact_card',
                        'phone': phone,
                        'secondary_phone': clinic.get('secondary_phone', '01-4796136'),
                        'whatsapp_url': clinic.get('whatsapp_link')
                    }]
                }
            return {
                'content': (
                    "🦷 **Immediate Home Relief Guidance for Tooth Pain:**\n\n"
                    "1. **Warm Saltwater Rinse:** Dissolve 1/2 tsp of salt in a glass of warm water and gently swish for 30 seconds to reduce bacteria and inflammation.\n"
                    "2. **Cold Compress:** Apply an ice pack wrapped in a cloth to the outside of your cheek (15 mins on, 15 mins off) if there is swelling.\n"
                    "3. **What to Avoid:** Do not place aspirin or painkillers directly against the tooth/gum (it causes chemical burns). Avoid chewing on that side and avoid extreme hot/cold foods.\n"
                    "4. **Clinical Next Step:** Persistent throbbing or sensitivity indicates deep decay or nerve inflammation. A gentle clinical exam and digital X-ray will pinpoint the exact cause.\n\n"
                    f"📞 **Speak with our clinic staff:** [{phone}](tel:{phone.replace(' ', '')})"
                ),
                'quick_actions': ["Book Urgent Slot", "Call Clinic Now", "WhatsApp Doctor", "Root Canal Pricing"],
                'cards': [{
                    'type': 'contact_card',
                    'phone': phone,
                    'secondary_phone': clinic.get('secondary_phone', '01-4796136'),
                    'whatsapp_url': clinic.get('whatsapp_link')
                }]
            }

        # ==========================================
        # 3. TREATMENT PRICING
        # ==========================================
        elif intent == 'TREATMENT_PRICE':
            pricing_data = tool_data.get('pricing', {})
            items = pricing_data.get('items', [])
            treatment_name = pricing_data.get('treatment', 'Dental Treatment')
            starting_price = pricing_data.get('starting_price', 'NPR 1,000')

            price_rows = []
            for it in items[:6]:
                price_rows.append(f"• **{it['name']}**: NPR {it['price']}")

            items_text = "\n".join(price_rows) if price_rows else (
                "• **General Consultation:** Free for first-time booked patients\n"
                "• **Scaling & Polishing (Deep Clean):** NPR 1,000 – 2,500\n"
                "• **Tooth-Colored Composite Filling:** NPR 1,000 – 2,500 / tooth\n"
                "• **Root Canal Treatment (RCT):** NPR 2,500 – 4,500\n"
                "• **Ceramic Crowns & Bridges:** NPR 3,500 – 15,000\n"
                "• **Dental Implants (Complete):** NPR 45,000 – 65,000\n"
                "• **Orthodontics / Braces:** NPR 35,000 – 65,000\n"
                "• **Teeth Whitening (In-Office):** NPR 5,000 – 12,000\n"
                "• **Tooth Extraction:** NPR 500 – 2,000"
            )

            if is_ne:
                return {
                    'content': (
                        f"💰 **केयरफर्स्ट डेन्टल क्लिनिक मूल्य विवरण ({treatment_name}):**\n\n"
                        f"सुरुवाती शुल्क: **{starting_price}**\n\n"
                        f"{items_text}\n\n"
                        "✨ *हाम्रा सबै दरहरू पारदर्शी छन्। क्लिनिकल परीक्षण पश्चात डाक्टरले तपाईंको अवस्था अनुसार यकिन लागत बताउनुहुनेछ।*"
                    ),
                    'quick_actions': ["अपोइन्टमेन्ट लिनुहोस्", "ह्वाट्सएपमा बुझ्नुहोस्", "सबै उपचार सेवाहरू", "क्लिनिक खुल्ने समय"],
                    'cards': [{
                        'type': 'pricing_card',
                        'treatment': treatment_name,
                        'starting_price': starting_price,
                        'items': items[:4]
                    }]
                }
            return {
                'content': (
                    f"💰 **CareFirst Dental Transparent Pricing ({treatment_name}):**\n\n"
                    f"Starting from: **{starting_price}**\n\n"
                    f"{items_text}\n\n"
                    "✨ *All prices are fully transparent with zero hidden costs. Final exact estimate is confirmed after a clinical evaluation with our specialist doctor.*"
                ),
                'quick_actions': ["Book Consultation", "Estimate Total Cost", "WhatsApp CareFirst", "View All Treatments"],
                'cards': [{
                    'type': 'pricing_card',
                    'treatment': treatment_name,
                    'starting_price': starting_price,
                    'items': items[:4]
                }]
            }

        # ==========================================
        # 4. APPOINTMENT / BOOKING
        # ==========================================
        elif intent == 'APPOINTMENT':
            if is_ne:
                return {
                    'content': (
                        "📅 **केयरफर्स्ट डेन्टल क्लिनिकमा अपोइन्टमेन्ट लिने तरिका:**\n\n"
                        "हामी दैनिक बिहान ७:३० देखि साँझ ७:३० सम्म खुला छौं। तपाईं ३ वटा सिफ्ट मध्ये अनुकूल समय छनोट गर्न सक्नुहुन्छ:\n"
                        "• **बिहानी सत्र:** बिहान ७:३० – ११:३०\n"
                        "• **दिउँसो सत्र:** बिहान ११:३० – दिउँसो ४:००\n"
                        "• **साँझ सत्र:** दिउँसो ४:०० – साँझ ७:३०\n\n"
                        "👉 तलको बटन थिचेर १ मिनेटमै अनलाइन अपोइन्टमेन्ट लिन सक्नुहुन्छ वा सिधै ह्वाट्सएपमा सन्देश पठाउन सक्नुहुन्छ।"
                    ),
                    'quick_actions': ["अपोइन्टमेन्ट लिनुहोस्", "ह्वाट्सएप बुकिङ", "क्लिनिकमा कल गर्नुहोस्", "उपचार शुल्क"],
                    'cards': [{
                        'type': 'contact_card',
                        'phone': phone,
                        'secondary_phone': clinic.get('secondary_phone', '01-4796136'),
                        'whatsapp_url': clinic.get('whatsapp_link')
                    }]
                }
            return {
                'content': (
                    "📅 **Book Your Visit at CareFirst Dental Clinic:**\n\n"
                    "We are open 7 days a week (Monday to Sunday) from 7:30 AM to 7:30 PM. You can choose your preferred time slot:\n"
                    "• **Morning Shift:** 7:30 AM – 11:30 AM\n"
                    "• **Afternoon Shift:** 11:30 AM – 4:00 PM\n"
                    "• **Evening Shift:** 4:00 PM – 7:30 PM\n\n"
                    "👉 Click below to complete your 1-minute smart appointment request or message our front desk directly on WhatsApp."
                ),
                'quick_actions': ["Book Online Now", "WhatsApp Direct Booking", "Call Front Desk", "View Treatments"],
                'cards': [{
                    'type': 'contact_card',
                    'phone': phone,
                    'secondary_phone': clinic.get('secondary_phone', '01-4796136'),
                    'whatsapp_url': clinic.get('whatsapp_link')
                }]
            }

        # ==========================================
        # 5. ALL SERVICES LIST
        # ==========================================
        elif intent == 'SERVICES_LIST':
            services_qs = Service.objects.filter(is_active=True).order_by('order')
            serv_lines = []
            for s in services_qs:
                price = s.get_dynamic_price()
                serv_lines.append(f"• **{s.title}** — *From NPR {price}*")

            content_text = "\n".join(serv_lines) if serv_lines else (
                "• **General Dentistry & Consultation**\n"
                "• **Root Canal Treatment (Painless RCT)**\n"
                "• **Tooth-Colored Fillings & Restorations**\n"
                "• **Crowns & Bridges (Zirconia / Ceramic)**\n"
                "• **Orthodontic Treatment (Braces & Clear Aligners)**\n"
                "• **3D Digital Dental Implants**\n"
                "• **Scaling & Polishing (Deep Cleaning)**\n"
                "• **Cosmetic Teeth Whitening**\n"
                "• **Tooth Extractions & Wisdom Tooth Surgery**\n"
                "• **Dentures (Complete & Partial)**\n"
                "• **Periodontal Gum Treatment**"
            )

            if is_ne:
                return {
                    'content': (
                        "🦷 **केयरफर्स्ट डेन्टल क्लिनिकमा उपलब्ध सम्पूर्ण सेवाहरू:**\n\n"
                        f"{content_text}\n\n"
                        "सबै उपचारहरू अस्पताल स्तरको क्लास-बी अटोक्लेभ निसंक्रमण र डिजिटल एक्स-रे प्रविधिबाट गरिन्छ।"
                    ),
                    'quick_actions': ["अपोइन्टमेन्ट लिनुहोस्", "शुल्क विवरण", "डाक्टर सुवास बन्जाडे", "क्लिनिक ठेगाना"],
                    'cards': []
                }
            return {
                'content': (
                    "🦷 **Complete Clinical Services at CareFirst Dental Clinic:**\n\n"
                    f"{content_text}\n\n"
                    "All procedures adhere to hospital-grade Class-B autoclave sterilization and digital low-radiation diagnostics for a completely safe, pain-free visit."
                ),
                'quick_actions': ["Book Appointment", "Treatment Pricing", "Meet Our Doctors", "Clinic Location"],
                'cards': []
            }

        # ==========================================
        # 6. OPENING HOURS
        # ==========================================
        elif intent == 'OPENING_HOURS':
            if is_ne:
                return {
                    'content': (
                        "⏰ **केयरफर्स्ट डेन्टल क्लिनिक खुल्ने समय:**\n\n"
                        "हाम्रो क्लिनिक **हप्ताको ७ दिन (आइतबारदेखि शनिबारसम्म)** दैनिक **बिहान ७:३० देखि साँझ ७:३० सम्म** खुला रहन्छ।\n\n"
                        "बिहान कार्यालय जानु अघि वा साँझ कार्यालय सकिएपछि पनि सहजै सेवा लिन सक्नुहुन्छ।"
                    ),
                    'quick_actions': ["अपोइन्टमेन्ट लिनुहोस्", "क्लिनिकमा कल गर्नुहोस्", "ठेगाना र नक्सा"],
                    'cards': [{
                        'type': 'clinic_card',
                        'title': 'केयरफर्स्ट डेन्टल क्लिनिक',
                        'hours': 'दैनिक बिहान ७:३० – साँझ ७:३०',
                        'phone': phone,
                        'location': 'प्रगतिनगर मार्ग, शंखमूल-३१, काठमाडौँ'
                    }]
                }
            return {
                'content': (
                    "⏰ **CareFirst Dental Clinic Opening Hours:**\n\n"
                    "We are open **7 days a week (Monday to Sunday)** from **7:30 AM to 7:30 PM**.\n\n"
                    "Both early morning consultations and evening after-work visits are fully available."
                ),
                'quick_actions': ["Book Appointment", "Call Clinic", "Location & Directions"],
                'cards': [{
                    'type': 'clinic_card',
                    'title': 'CareFirst Dental Clinic',
                    'hours': clinic.get('opening_hours', 'Daily: 7:30 AM – 7:30 PM'),
                    'phone': phone,
                    'location': clinic.get('location', 'Pragatinagar Road, Shankhamul-31, Kathmandu')
                }]
            }

        # ==========================================
        # 7. LOCATION & DIRECTIONS
        # ==========================================
        elif intent == 'LOCATION':
            if is_ne:
                return {
                    'content': (
                        "📍 **केयरफर्स्ट डेन्टल क्लिनिकको ठेगाना:**\n\n"
                        "**ठेगाना:** प्रगतिनगर मार्ग, शंखमूल-३१, काठमाडौँ ४४६००\n"
                        "*(शंखमूल र नयाँ बानेश्वर चोक नजिकै)*\n\n"
                        "क्लिनिकमा पर्याप्त पार्किङ र आधुनिक उपकरणसहितको सुविधा उपलब्ध छ।"
                    ),
                    'quick_actions': ["गुगल नक्सा हेर्नुहोस्", "क्लिनिकमा कल गर्नुहोस्", "अपोइन्टमेन्ट लिनुहोस्"],
                    'cards': [{
                        'type': 'map_card',
                        'title': 'केयरफर्स्ट काठमाडौँ क्लिनिक',
                        'address': 'प्रगतिनगर मार्ग, शंखमूल-३१, काठमाडौँ',
                        'hours': 'दैनिक बिहान ७:३० – साँझ ७:३०',
                        'google_maps_url': 'https://maps.app.goo.gl/9Z7Z1v6v4X'
                    }]
                }
            return {
                'content': (
                    "📍 **CareFirst Dental Clinic Location:**\n\n"
                    "**Address:** Pragatinagar Road, Shankhamul-31, Kathmandu 44600\n"
                    "*(Conveniently situated near the Shankhamul / New Baneshwor junction)*\n\n"
                    "We have modern on-site operatory suites with convenient patient parking."
                ),
                'quick_actions': ["Get Directions", "Call Clinic", "Book Visit"],
                'cards': [{
                    'type': 'map_card',
                    'title': 'CareFirst Kathmandu Clinic',
                    'address': clinic.get('location', 'Pragatinagar Road, Shankhamul-31, Kathmandu'),
                    'hours': clinic.get('opening_hours', 'Daily: 7:30 AM – 7:30 PM'),
                    'google_maps_url': 'https://maps.app.goo.gl/9Z7Z1v6v4X'
                }]
            }

        # ==========================================
        # 8. CONTACT & PHONE
        # ==========================================
        elif intent == 'CONTACT':
            if is_ne:
                return {
                    'content': (
                        "📞 **केयरफर्स्ट डेन्टल क्लिनिक सम्पर्क विवरण:**\n\n"
                        f"• **मोबाइल / इमरजेन्सी:** [{phone}](tel:{phone.replace(' ', '')})\n"
                        f"• **ल्याण्डलाइन:** [०१-४७९६१३६](tel:014796136)\n"
                        f"• **इमेल:** `info@carefirstdental.com`\n"
                        f"• **ह्वाट्सएप:** सिधै सन्देश पठाउन उपलब्ध छ।\n\n"
                        "हाम्रो रिसेप्शन टोली दैनिक बिहान ७:३० देखि साँझ ७:३० सम्म उपलब्ध छ।"
                    ),
                    'quick_actions': ["ह्वाट्सएप च्याट", "अहिले कल गर्नुहोस्", "अनलाइन अपोइन्टमेन्ट"],
                    'cards': [{
                        'type': 'contact_card',
                        'phone': phone,
                        'secondary_phone': '01-4796136',
                        'whatsapp_url': clinic.get('whatsapp_link')
                    }]
                }
            return {
                'content': (
                    "📞 **Contact CareFirst Dental Clinic:**\n\n"
                    f"• **Mobile / Direct:** [{phone}](tel:{phone.replace(' ', '')})\n"
                    f"• **Landline:** [01-4796136](tel:014796136)\n"
                    f"• **Email:** `info@carefirstdental.com`\n"
                    f"• **WhatsApp:** Instant direct messaging available.\n\n"
                    "Our clinical reception team is available daily from 7:30 AM to 7:30 PM."
                ),
                'quick_actions': ["WhatsApp Consultation", "Call Now", "Book Appointment Online"],
                'cards': [{
                    'type': 'contact_card',
                    'phone': phone,
                    'secondary_phone': '01-4796136',
                    'whatsapp_url': clinic.get('whatsapp_link')
                }]
            }

        # ==========================================
        # 9. DOCTOR INFORMATION
        # ==========================================
        elif intent == 'DOCTOR_INFORMATION':
            docs = Doctor.objects.filter(is_active=True).order_by('order')
            doc_cards_data = []
            lines = []
            for d in docs:
                lines.append(f"• **{d.name}** — {d.designation} ({d.qualifications})\n  *NMC Reg: #{d.nmc_number} | Experience: {d.experience_years} years*")
                doc_cards_data.append({
                    'name': d.name,
                    'designation': d.designation,
                    'qualifications': d.qualifications,
                    'nmc_number': d.nmc_number
                })

            doc_text = "\n\n".join(lines) if lines else (
                "• **Dr. Subash Banjade** — Senior Dental Surgeon & Clinical Director (BDS, NMC #31229)\n"
                "  *Specialist in Painless Endodontics (RCT), Digital Implantology & Aesthetic Restorations (8+ Years Experience)*"
            )

            if is_ne:
                return {
                    'content': (
                        "👨‍⚕️ **केयरफर्स्ट डेन्टल क्लिनिकका विशेषज्ञ चिकित्सकहरू:**\n\n"
                        f"{doc_text}\n\n"
                        "हाम्रा सम्पूर्ण चिकित्सकहरू नेपाल मेडिकल काउन्सिल (NMC) बाट प्रमाणित हुनुहुन्छ र आधुनिक डिजिटल प्रविधिबाट उपचार गर्नुहुन्छ।"
                    ),
                    'quick_actions': ["डा. सुवाससँग परामर्श", "उपचार सेवाहरू हेर्नुहोस्", "क्लिनिक खुल्ने समय"],
                    'cards': [{
                        'type': 'doctor_card',
                        'doctors': doc_cards_data[:2]
                    }] if doc_cards_data else []
                }
            return {
                'content': (
                    "👨‍⚕️ **Our Certified Dental Specialists at CareFirst:**\n\n"
                    f"{doc_text}\n\n"
                    "Our dentists utilize digital low-radiation RVG X-rays and Class-B autoclave sterilization for international-standard care."
                ),
                'quick_actions': ["Book Consultation with Dr. Subash", "Our Treatments", "Clinic Hours"],
                'cards': [{
                    'type': 'doctor_card',
                    'doctors': doc_cards_data[:2]
                }] if doc_cards_data else []
            }

        # ==========================================
        # 10. TREATMENT SPECIFIC INFORMATION & EDUCATIONAL CONCEPT
        # ==========================================
        elif intent in ('TREATMENT_INFORMATION', 'TREATMENT_PROCESS', 'TREATMENT_DURATION') or True:
            # Check educational encyclopedia first for deep clinical definition
            edu_concept = find_educational_concept(message)
            if not edu_concept and treatment_slug:
                edu_concept = find_educational_concept(treatment_slug)

            details = tool_data.get('current_treatment_details')
            name = details['name'] if details else (edu_concept['en']['title'] if edu_concept else 'Dental Procedure')
            price = details.get('starting_price', 'NPR 1,000') if details else 'NPR 1,000'

            if edu_concept:
                lang_key = 'ne' if is_ne else 'en'
                edu = edu_concept[lang_key]

                if is_ne:
                    full_answer = (
                        f"🦷 **{edu['title']}**\n\n"
                        f"{edu['definition']}\n\n"
                        f"{edu['how_it_works']}\n\n"
                        f"{edu['benefits']}\n\n"
                        f"🏥 **केयरफर्स्ट क्लिनिकमा उपचार:**\n"
                        f"केयरफर्स्ट डेन्टल क्लिनिकमा यो सेवा सुरुवाती **{price}** मा उपलब्ध छ। डा. सुवास बन्जाडेको टोलीले डिजिटल प्रविधि र पूर्ण दुखाइरहित विधिबाट सेवा प्रदान गर्दछ।"
                    )
                    return {
                        'content': full_answer,
                        'quick_actions': ["अपोइन्टमेन्ट लिनुहोस्", "शुल्क विवरण", "डाक्टरको जानकारी", "अन्य उपचारहरू"],
                        'cards': [{
                            'type': 'treatment_card',
                            'name': name,
                            'category': details.get('category', 'Dental Care') if details else 'Dental Care',
                            'starting_price': price,
                            'url': details.get('url', '/services/'),
                            'features': details.get('features', [])[:3] if details else ["Painless Protocol", "Digital Planning"]
                        }] if details else []
                    }
                else:
                    full_answer = (
                        f"🦷 **{edu['title']}**\n\n"
                        f"{edu['definition']}\n\n"
                        f"{edu['how_it_works']}\n\n"
                        f"{edu['benefits']}\n\n"
                        f"🏥 **At CareFirst Dental Clinic:**\n"
                        f"This procedure starts from **{price}** with transparent pricing and zero hidden fees. Performed by Dr. Subash Banjade (BDS, NMC #31229) and our specialist team using computer-guided, hospital-grade Class-B sterile standards.\n\n"
                        f"Would you like to schedule an oral evaluation or consult our team?"
                    )
                    return {
                        'content': full_answer,
                        'quick_actions': ["Book Appointment", "View Pricing Breakdown", "Meet the Doctor", "Ask Another Question"],
                        'cards': [{
                            'type': 'treatment_card',
                            'name': name,
                            'category': details.get('category', 'Dental Care') if details else 'Dental Care',
                            'starting_price': price,
                            'url': details.get('url', '/services/'),
                            'features': details.get('features', [])[:3] if details else ["Painless Protocol", "Digital Planning"]
                        }] if details else []
                    }

            if details:
                feat_list = "\n".join([f"✓ {f}" for f in details.get('features', [])[:4]])
                if is_ne:
                    return {
                        'content': (
                            f"🦷 **{name} सम्बन्धी जानकारी:**\n\n"
                            f"केयरफर्स्ट डेन्टल क्लिनिकमा {name} को सुरुवाती शुल्क **{price}** रहेको छ।\n\n"
                            f"**मुख्य विशेषताहरू:**\n{feat_list}\n\n"
                            "डा. सुवास बन्जाडेको टोलीले डिजिटल प्रविधि र दुखाइरहित विधिबाट यो उपचार सम्पन्न गर्दछ। के तपाईं यस सम्बन्धी परामर्शको लागि समय लिन चाहनुहुन्छ?"
                        ),
                        'quick_actions': ["अपोइन्टमेन्ट लिनुहोस्", "शुल्क विवरण", "डाक्टरको जानकारी", "अन्य उपचारहरू"],
                        'cards': [{
                            'type': 'treatment_card',
                            'name': name,
                            'category': details.get('category'),
                            'starting_price': price,
                            'url': details.get('url'),
                            'features': details.get('features', [])[:3]
                        }]
                    }
                return {
                    'content': (
                        f"🦷 **About {name} at CareFirst:**\n\n"
                        f"{name} starts from **{price}** at CareFirst Dental Clinic.\n\n"
                        f"**Key Clinical Highlights:**\n{feat_list}\n\n"
                        "Performed by our specialist team led by Dr. Subash Banjade (BDS, NMC #31229) using computer-guided protocols and sterile Class-B standards. Would you like to schedule an oral evaluation?"
                    ),
                    'quick_actions': ["Book Appointment", "View Pricing Breakdown", "Meet the Doctor", "Ask Another Question"],
                    'cards': [{
                        'type': 'treatment_card',
                        'name': name,
                        'category': details.get('category'),
                        'starting_price': price,
                        'url': details.get('url'),
                        'features': details.get('features', [])[:3]
                    }]
                }

        return None

    @classmethod
    def _generate_smart_fallback(
        cls,
        intent: str,
        tool_data: Dict[str, Any],
        treatment_slug: Optional[str],
        message: str,
        is_ne: bool = False
    ) -> str:
        clinic = tool_data.get('clinic', {})
        phone = clinic.get('primary_phone', '+977 9807464136')

        if tool_data.get('current_treatment_details'):
            details = tool_data['current_treatment_details']
            if is_ne:
                return (
                    f"**{details['name']}** केयरफर्स्ट डेन्टल क्लिनिकमा सुरुवाती शुल्क **{details['starting_price']}** मा उपलब्ध छ।\n\n"
                    f"हाम्रो विशेषज्ञ दन्त टोलीले डिजिटल एक्स-रे र अस्पताल स्तरको पूर्ण निसंक्रमण विधिबाट सेवा प्रदान गर्दछ।\n\n"
                    f"थप जानकारी वा डाक्टरसँग भेट्न **{phone}** मा सम्पर्क गर्नुहोस् वा अनलाइन अपोइन्टमेन्ट लिनुहोस्।"
                )
            return (
                f"**{details['name']}** at CareFirst Dental Clinic starts from **{details['starting_price']}**.\n\n"
                f"Our clinical team led by Dr. Subash Banjade (BDS, NMC #31229) utilizes modern digital imaging and hospital-grade sterilization for gentle, precision care.\n\n"
                f"Would you like to schedule an oral consultation or speak directly with our team at **{phone}**?"
            )

        if is_ne:
            return (
                f"केयरफर्स्ट डेन्टल क्लिनिक (शंखमूल, काठमाडौँ) मा हामी हप्ताको ७ दिन (बिहान ७:३० देखि साँझ ७:३० सम्म) आधुनिक दन्त उपचार सेवा प्रदान गर्दछौं।\n\n"
                f"तपाईंको समस्या बारे थप जानकारी लिन वा परामर्श तय गर्न सिधै **{phone}** मा कल गर्नुहोस् वा अनलाइन अपोइन्टमेन्ट लिनुहोस्।"
            )

        return (
            f"At CareFirst Dental Clinic in Shankhamul, Kathmandu, we provide international-standard, pain-free dental care 7 days a week (7:30 AM – 7:30 PM).\n\n"
            f"Please feel free to ask about specific treatments (like RCT, Fillings, Implants, Braces), check our prices, or contact our team directly at **{phone}**."
        )

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
