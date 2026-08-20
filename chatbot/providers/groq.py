import json
import logging
import requests
from typing import Dict, Any, List, Optional
from .base import BaseAIProvider, AIResponse

logger = logging.getLogger(__name__)

class GroqProvider(BaseAIProvider):
    """
    Groq Cloud Provider (Ultra-fast real-time inference).
    Uses official Groq endpoints with automatic model fallbacks.
    """

    FALLBACK_MODELS = [
        'openai/gpt-oss-120b',
        'qwen/qwen3.6-27b',
        'openai/gpt-oss-20b',
        'groq/compound',
        'groq/compound-mini',
    ]

    def __init__(self, api_key: str = '', model_name: str = 'openai/gpt-oss-120b', timeout: int = 20):
        super().__init__(model_name=model_name, timeout=timeout)
        self.api_key = api_key
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def generate_response(
        self,
        prompt: str,
        system_prompt: str,
        context: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> AIResponse:
        if not self.api_key:
            return AIResponse(content="", success=False, error_message="Groq API key is not configured.")

        messages = [{"role": "system", "content": system_prompt}]

        if history:
            for item in history[-6:]:
                messages.append({
                    "role": item.get('role', 'user'),
                    "content": item.get('content', '')
                })

        context_str = ""
        if context:
            context_str = f"\n[VERIFIED CAREFIRST CLINIC CONTEXT & REAL-TIME PRICING]:\n{json.dumps(context, indent=2)}\n"

        messages.append({
            "role": "user",
            "content": f"{context_str}\nPatient Question: {prompt}"
        })

        models_to_try = [self.model_name] + [m for m in self.FALLBACK_MODELS if m != self.model_name]
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }

        last_error = ""
        for model in models_to_try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.4,
                "max_tokens": 1000
            }
            try:
                resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get('choices', [])
                    if choices:
                        content = choices[0].get('message', {}).get('content', '').strip()
                        if content:
                            return AIResponse(content=content, success=True, raw_data=data)
                else:
                    last_error = f"Model {model} returned HTTP {resp.status_code}: {resp.text}"
                    logger.warning(last_error)
            except Exception as e:
                last_error = f"Model {model} exception: {str(e)}"
                logger.warning(last_error)

        return AIResponse(content="", success=False, error_message=last_error or "All Groq models failed.")

    def classify_intent(self, user_message: str, current_treatment: Optional[str] = None) -> str:
        return "GENERAL_DENTAL_INFORMATION"
