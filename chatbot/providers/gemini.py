import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from .base import BaseAIProvider, AIResponse

logger = logging.getLogger(__name__)

class GeminiProvider(BaseAIProvider):
    """
    Google Gemini REST API implementation.
    Uses standard Python HTTPS requests for maximum portability without heavy SDK dependencies.
    """

    def __init__(self, api_key: str = '', model_name: str = 'gemini-1.5-flash', timeout: int = 15):
        super().__init__(model_name=model_name, timeout=timeout)
        self.api_key = api_key

    def generate_response(self, prompt: str, system_prompt: str, context: Optional[Dict[str, Any]] = None, history: Optional[List[Dict[str, str]]] = None) -> AIResponse:
        if not self.api_key:
            return AIResponse(
                content="",
                success=False,
                error_message="Gemini API key is not configured."
            )

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        
        # Build contents payload
        contents = []
        
        # Add conversation history
        if history:
            for item in history[-6:]: # Keep recent conversation context bounded
                role = "user" if item.get('role') == 'user' else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": item.get('content', '')}]
                })
        
        # Build context injection for prompt
        context_str = ""
        if context:
            context_str = f"\n[VERIFIED CAREFIRST DATABASE CONTEXT]:\n{json.dumps(context, indent=2)}\n"

        full_user_content = f"{context_str}\nUser question: {prompt}"
        contents.append({
            "role": "user",
            "parts": [{"text": full_user_content}]
        })

        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2, # Low temperature for strict factual accuracy
                "maxOutputTokens": 800,
                "topP": 0.95
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
                
                candidates = data.get('candidates', [])
                if candidates:
                    first_candidate = candidates[0]
                    parts = first_candidate.get('content', {}).get('parts', [])
                    if parts:
                        text = parts[0].get('text', '').strip()
                        return AIResponse(content=text, success=True, raw_data=data)
                
                return AIResponse(content="", success=False, error_message="Empty candidate response from Gemini.")
                
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
            logger.warning(f"Gemini API HTTP Error {e.code}: {err_body}")
            return AIResponse(content="", success=False, error_message=f"Gemini HTTP {e.code}")
        except Exception as e:
            logger.warning(f"Gemini API invocation error: {str(e)}")
            return AIResponse(content="", success=False, error_message=str(e))

    def classify_intent(self, user_message: str, current_treatment: Optional[str] = None) -> str:
        """
        Lightweight fallback intent classification via Gemini if deterministic rule fails.
        """
        if not self.api_key:
            return "GENERAL_DENTAL_INFORMATION"

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        
        prompt = (
            "Classify the following dental patient message into EXACTLY one category from this list: "
            "[GREETING, TREATMENT_INFORMATION, TREATMENT_PRICE, TREATMENT_PROCESS, TREATMENT_DURATION, "
            "TREATMENT_BENEFITS, DOCTOR_INFORMATION, CLINIC_INFORMATION, OPENING_HOURS, LOCATION, "
            "CONTACT, APPOINTMENT, EMERGENCY, FAQ, REVIEW, GENERAL_DENTAL_INFORMATION, WHATSAPP, UNKNOWN].\n"
            f"User message: \"{user_message}\"\n"
            "Return ONLY the category name."
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.0, "maxOutputTokens": 20}
        }

        try:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                parts = data.get('candidates', [{}])[0].get('content', {}).get('parts', [])
                if parts:
                    return parts[0].get('text', '').strip().upper()
        except Exception:
            pass

        return "GENERAL_DENTAL_INFORMATION"
