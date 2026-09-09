from django.conf import settings
from .base import BaseAIProvider, AIResponse

def get_ai_provider() -> BaseAIProvider:
    """
    Factory function to retrieve the configured primary AI provider instance.
    - If GROQ_API_KEY is present or AI_PROVIDER is 'groq', uses Groq Cloud.
    - If GEMINI_API_KEY is present or AI_PROVIDER is 'gemini', uses Google Gemini.
    - If OLLAMA is configured, uses local Ollama.
    - Otherwise, automatically uses FreeAIProvider (zero API key needed, answers any question).
    """
    provider_type = getattr(settings, 'AI_PROVIDER', '').lower()
    gemini_key = getattr(settings, 'GEMINI_API_KEY', '').strip()
    groq_key = getattr(settings, 'GROQ_API_KEY', '').strip()

    if (provider_type == 'groq' or (groq_key and not gemini_key)) and groq_key:
        from .groq import GroqProvider
        return GroqProvider(
            api_key=groq_key,
            model_name=getattr(settings, 'GROQ_MODEL', 'openai/gpt-oss-120b')
        )
    elif (provider_type == 'gemini' or gemini_key) and gemini_key:
        from .gemini import GeminiProvider
        return GeminiProvider(
            api_key=gemini_key,
            model_name=getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-flash')
        )
    elif provider_type == 'ollama':
        from .ollama import OllamaProvider
        return OllamaProvider(
            base_url=getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434'),
            model_name=getattr(settings, 'OLLAMA_MODEL', 'llama3:8b')
        )
    elif groq_key:
        from .groq import GroqProvider
        return GroqProvider(api_key=groq_key)
    elif gemini_key:
        from .gemini import GeminiProvider
        return GeminiProvider(api_key=gemini_key)
    else:
        from .free_ai import FreeAIProvider
        return FreeAIProvider()


def get_fallback_ai_provider() -> BaseAIProvider:
    """
    Fallback provider if primary provider hits rate limit or network timeout.
    """
    from .free_ai import FreeAIProvider
    return FreeAIProvider()

__all__ = ['BaseAIProvider', 'AIResponse', 'get_ai_provider', 'get_fallback_ai_provider']

