import re
from typing import Dict, Any, Optional, List
from chatbot.models import Conversation, ChatMessage
from main.models import Service

class ContextService:
    """
    Context Management & Page Awareness Service.
    Resolves pronouns ('it', 'this', 'that') and extracts treatment context from the URL/page or conversation history.
    """

    PRONOUN_PATTERNS = [
        r'\b(it|this|that|the procedure|the treatment|this one|its|the cost of it)\b'
    ]

    TREATMENT_ALIASES = {
        'root-canal-treatment': ['rct', 'root canal', 'nerve filling', 'endodontic'],
        'dental-implants': ['implant', 'implants', 'artificial tooth', 'tooth replacement'],
        'orthodontic-treatment-braces': ['braces', 'aligners', 'invisalign', 'teeth straightening', 'clips'],
        'dental-filling': ['filling', 'cavity fill', 'composite', 'tooth restoration', 'glass ionomer'],
        'scaling-and-polishing': ['scaling', 'cleaning', 'teeth cleaning', 'polishing', 'tartar removal'],
        'teeth-whitening': ['whitening', 'bleaching', 'teeth brightening', 'yellow teeth'],
        'crowns-and-bridges': ['crown', 'cap', 'bridge', 'zirconia', 'ceramic cap'],
        'tooth-extraction': ['extraction', 'tooth removal', 'pull tooth', 'wisdom tooth'],
        'dentures': ['denture', 'false teeth', 'complete denture', 'removable teeth'],
        'digital-dental-x-ray': ['xray', 'x-ray', 'rvg', 'dental scan', 'radiograph'],
        'periodontal-treatment-gum': ['gum treatment', 'pyorrhea', 'gingivitis', 'deep cleaning'],
    }

    @classmethod
    def resolve_treatment_context(cls, user_message: str, current_page: str = '', current_treatment: str = '', conversation: Optional[Conversation] = None) -> Optional[str]:
        """
        Determines the relevant treatment for the message using:
        1. Explicit mention in message
        2. Implicit pronoun reference + Page Context
        3. Prior conversation context
        """
        text = user_message.lower().strip()

        # 1. Direct search in message for treatment names or aliases
        for slug, aliases in cls.TREATMENT_ALIASES.items():
            if slug.replace('-', ' ') in text:
                return slug
            for alias in aliases:
                if re.search(r'\b' + re.escape(alias) + r'\b', text, re.IGNORECASE):
                    return slug

        # Check all active database services
        for s in Service.objects.filter(is_active=True):
            if s.title.lower() in text or s.slug in text:
                return s.slug

        # 2. Pronoun match with Page Context
        has_pronoun = any(re.search(pat, text, re.IGNORECASE) for pat in cls.PRONOUN_PATTERNS)
        
        if current_treatment:
            return current_treatment

        # Extract from URL path (e.g. /services/dental-implants/)
        if current_page:
            match = re.search(r'/services/([a-zA-Z0-9\-_]+)/?', current_page)
            if match:
                slug_candidate = match.group(1)
                if Service.objects.filter(slug=slug_candidate).exists():
                    return slug_candidate

        # 3. Fallback to Conversation's last mentioned treatment
        if conversation and conversation.current_treatment:
            return conversation.current_treatment

        return None

    @classmethod
    def get_recent_history(cls, conversation: Conversation, limit: int = 6) -> List[Dict[str, str]]:
        """
        Retrieves compact recent conversation history for LLM synthesis.
        """
        messages = conversation.messages.order_by('-created_at')[:limit]
        history = []
        for msg in reversed(messages):
            history.append({
                'role': msg.role,
                'content': msg.content
            })
        return history
