# services/ai_service.py
# Point d'entrée IA — délègue à llm et fallback

from services.llm import LLMService
from services.fallback import FallbackService
from services.fallback_v2 import FallbackV2Service

__all__ = ["LLMService", "FallbackService", "FallbackV2Service"]
