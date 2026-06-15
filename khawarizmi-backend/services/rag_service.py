# services/rag_service.py
# Point d'entrée RAG — délègue à embedder et khawarizmi_engine

from services.embedder import EmbedderService
from services.khawarizmi_engine import KhawarizmiTutor

__all__ = ["EmbedderService", "KhawarizmiTutor"]
