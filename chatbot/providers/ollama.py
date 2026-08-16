import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from .base import BaseAIProvider, AIResponse

logger = logging.getLogger(__name__)

class OllamaProvider(BaseAIProvider):
    """
    Local Ollama LLM provider (e.g. Llama 3, Mistral, Gemma) for on-premise or offline deployments.
    """

    def __init__(self, base_url: str = 'http://localhost:11434', model_name: str = 'llama3:8b', timeout: int = 25):
        super().__init__(model_name=model_name, timeout=timeout)
        self.base_url = base_url.rstrip('/')

    def generate_response(self, prompt: str, system_prompt: str, context: Optional[Dict[str, Any]] = None, history: Optional[List[Dict[str, str]]] = None) -> AIResponse:
        endpoint = f"{self.base_url}/api/chat"
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            for item in history[-6:]:
                messages.append({
                    "role": item.get('role', 'user'),
                    "content": item.get('content', '')
                })
        
        context_str = ""
        if context:
            context_str = f"\n[VERIFIED CAREFIRST DATABASE CONTEXT]:\n{json.dumps(context, indent=2)}\n"

        messages.append({
            "role": "user",
            "content": f"{context_str}\nUser question: {prompt}"
        })

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }

        try:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                message = data.get('message', {})
                content = message.get('content', '').strip()
                return AIResponse(content=content, success=True, raw_data=data)
        except Exception as e:
            logger.warning(f"Ollama provider connection error ({self.base_url}): {str(e)}")
            return AIResponse(content="", success=False, error_message=f"Ollama error: {str(e)}")

    def classify_intent(self, user_message: str, current_treatment: Optional[str] = None) -> str:
        endpoint = f"{self.base_url}/api/chat"
        
        prompt = (
            "Classify the following dental patient message into EXACTLY one category from this list: "
            "[GREETING, TREATMENT_INFORMATION, TREATMENT_PRICE, TREATMENT_PROCESS, TREATMENT_DURATION, "
            "TREATMENT_BENEFITS, DOCTOR_INFORMATION, CLINIC_INFORMATION, OPENING_HOURS, LOCATION, "
            "CONTACT, APPOINTMENT, EMERGENCY, FAQ, REVIEW, GENERAL_DENTAL_INFORMATION, WHATSAPP, UNKNOWN].\n"
            f"User message: \"{user_message}\"\n"
            "Return ONLY the category name."
        )

        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.0}
        }

        try:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                content = data.get('message', {}).get('content', '').strip().upper()
                return content
        except Exception:
            return "GENERAL_DENTAL_INFORMATION"
