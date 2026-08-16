from django.conf import settings
from .base import BaseAIProvider, AIResponse

def get_ai_provider() -> BaseAIProvider:
    """
    Factory function to retrieve the configured AI provider instance.
    Defaults to Gemini if configured, with local Ollama or Mock provider support.
    """
    provider_type = getattr(settings, 'AI_PROVIDER', 'gemini').lower()
    
    if provider_type == 'gemini':
        from .gemini import GeminiProvider
        return GeminiProvider(
            api_key=getattr(settings, 'GEMINI_API_KEY', ''),
            model_name=getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-flash')
        )
    elif provider_type == 'ollama':
        from .ollama import OllamaProvider
        return OllamaProvider(
            base_url=getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434'),
            model_name=getattr(settings, 'OLLAMA_MODEL', 'llama3:8b')
        )
    else:
        from .gemini import GeminiProvider
        return GeminiProvider()

__all__ = ['BaseAIProvider', 'AIResponse', 'get_ai_provider']
