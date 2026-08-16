from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class AIResponse:
    """Standardized response object across any AI provider."""
    def __init__(self, content: str, intent: Optional[str] = None, raw_data: Optional[Dict[str, Any]] = None, success: bool = True, error_message: Optional[str] = None):
        self.content = content
        self.intent = intent
        self.raw_data = raw_data or {}
        self.success = success
        self.error_message = error_message

    def __str__(self):
        return self.content


class BaseAIProvider(ABC):
    """
    Abstract AI Provider Interface.
    Decouples Django and the Chatbot from specific vendors (Gemini, Ollama, OpenAI, etc.).
    """

    def __init__(self, model_name: Optional[str] = None, timeout: int = 15):
        self.model_name = model_name
        self.timeout = timeout

    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: str, context: Optional[Dict[str, Any]] = None, history: Optional[List[Dict[str, str]]] = None) -> AIResponse:
        """
        Generates a natural language response given prompts, verified tool context, and conversation history.
        """
        pass

    @abstractmethod
    def classify_intent(self, user_message: str, current_treatment: Optional[str] = None) -> str:
        """
        Classifies user intent into supported taxonomy.
        """
        pass
