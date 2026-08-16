import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from .base import BaseAIProvider, AIResponse

logger = logging.getLogger(__name__)

class FreeAIProvider(BaseAIProvider):
    """
    Free Zero-Config AI Provider powered by open inference endpoints (Pollinations.ai / OpenAI compatible).
    Requires ZERO API Key and responds to ANY general dental, medical, oral care, or treatment question.
    """

    def __init__(self, model_name: str = 'openai', timeout: int = 20):
        super().__init__(model_name=model_name, timeout=timeout)
        self.endpoint = "https://text.pollinations.ai/openai"

    def generate_response(self, prompt: str, system_prompt: str, context: Optional[Dict[str, Any]] = None, history: Optional[List[Dict[str, str]]] = None) -> AIResponse:
        messages = [
            {"role": "system", "content": system_prompt}
        ]

        if history:
            for item in history[-6:]:
                messages.append({
                    "role": item.get('role', 'user'),
                    "content": item.get('content', '')
                })

        context_str = ""
        if context:
            context_str = f"\n[CAREFIRST CLINIC & DATABASE CONTEXT]:\n{json.dumps(context, indent=2)}\n"

        messages.append({
            "role": "user",
            "content": f"{context_str}\nPatient question: {prompt}"
        })

        payload = {
            "model": "openai",
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
                    'User-Agent': 'CareFirstDentalAI/1.0'
                },
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                choices = data.get('choices', [])
                if choices:
                    content = choices[0].get('message', {}).get('content', '').strip()
                    if content:
                        return AIResponse(content=content, success=True, raw_data=data)
        except Exception as e:
            logger.warning(f"Free AI Primary API error: {str(e)}. Trying fallback endpoint...")

        # Fallback to simple direct GET/POST endpoint if /openai fails
        try:
            simple_endpoint = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}?system={urllib.parse.quote(system_prompt[:500])}"
            req = urllib.request.Request(
                simple_endpoint,
                headers={'User-Agent': 'CareFirstDentalAI/1.0'},
                method='GET'
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                text = resp.read().decode('utf-8').strip()
                if text:
                    return AIResponse(content=text, success=True)
        except Exception as e2:
            logger.warning(f"Free AI simple fallback error: {str(e2)}")
            return AIResponse(content="", success=False, error_message=str(e2))

        return AIResponse(content="", success=False, error_message="Could not generate AI response.")

    def classify_intent(self, user_message: str, current_treatment: Optional[str] = None) -> str:
        return "GENERAL_DENTAL_INFORMATION"
