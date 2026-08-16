import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from .base import BaseAIProvider, AIResponse

logger = logging.getLogger(__name__)

class GroqProvider(BaseAIProvider):
    """
    Groq Cloud Provider (Free ultra-fast inference for Llama 3.3 70B / Llama 3 8B).
    Free tier allows 30 RPM at zero cost (from https://console.groq.com/keys).
    """

    def __init__(self, api_key: str = '', model_name: str = 'llama-3.3-70b-versatile', timeout: int = 15):
        super().__init__(model_name=model_name, timeout=timeout)
        self.api_key = api_key
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def generate_response(self, prompt: str, system_prompt: str, context: Optional[Dict[str, Any]] = None, history: Optional[List[Dict[str, str]]] = None) -> AIResponse:
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
            context_str = f"\n[VERIFIED CAREFIRST CLINIC CONTEXT]:\n{json.dumps(context, indent=2)}\n"

        messages.append({
            "role": "user",
            "content": f"{context_str}\nPatient question: {prompt}"
        })

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 800
        }

        try:
            req = urllib.request.Request(
                self.endpoint,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                },
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                choices = data.get('choices', [])
                if choices:
                    content = choices[0].get('message', {}).get('content', '').strip()
                    return AIResponse(content=content, success=True, raw_data=data)
        except Exception as e:
            logger.warning(f"Groq API invocation error: {str(e)}")
            return AIResponse(content="", success=False, error_message=str(e))

        return AIResponse(content="", success=False, error_message="Empty Groq response.")

    def classify_intent(self, user_message: str, current_treatment: Optional[str] = None) -> str:
        return "GENERAL_DENTAL_INFORMATION"
