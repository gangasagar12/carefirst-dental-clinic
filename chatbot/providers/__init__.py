from django.conf import settings
from .base import BaseAIProvider, AIResponse

def get_ai_provider() -> BaseAIProvider:
    """
    Factory function to retrieve the configured AI provider instance.
    - If GEMINI_API_KEY is present, uses Google Gemini 1.5.
    - If OLLAMA is configured, uses local Ollama.
    - Otherwise, automatically uses FreeAIProvider (zero API key needed, answers ANY question).
    """
    provider_type = getattr(settings, 'AI_PROVIDER', '').lower()
    gemini_key = getattr(settings, 'GEMINI_API_KEY', '').strip()
    groq_key = getattr(settings, 'GROQ_API_KEY', '').strip()
    
    if (provider_type == 'gemini' or not provider_type) and gemini_key:
        from .gemini import GeminiProvider
        return GeminiProvider(
            api_key=gemini_key,
            model_name=getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-flash')
        )
    elif (provider_type == 'groq' or not gemini_key) and groq_key:
        from .groq import GroqProvider
        return GroqProvider(
            api_key=groq_key,
            model_name=getattr(settings, 'GROQ_MODEL', 'llama-3.3-70b-versatile')
        )
    elif provider_type == 'ollama':
        from .ollama import OllamaProvider
        return OllamaProvider(
            base_url=getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434'),
            model_name=getattr(settings, 'OLLAMA_MODEL', 'llama3:8b')
        )
    else:
        from .gemini import GeminiProvider
        return GeminiProvider(api_key=gemini_key)

__all__ = ['BaseAIProvider', 'AIResponse', 'get_ai_provider']
