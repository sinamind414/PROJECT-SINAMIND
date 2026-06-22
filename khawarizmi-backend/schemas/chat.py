"""Schémas Pydantic pour le Tuteur Contextuel."""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class ChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatContext(BaseModel):
    chapitre: Optional[str] = None
    page_source: Optional[str] = None
    fsrs_stability: Optional[float] = None
    fsrs_due: Optional[bool] = None
    last_score: Optional[int] = None
    orientation_chapitre: Optional[str] = None
    history: List[ChatHistoryMessage] = []


class ChatCard(BaseModel):
    """Carte cliquable dans le chat (redirection)."""
    titre: str
    raison: str
    action: str
    bouton: str


class TuteurRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    context: ChatContext = ChatContext()


class TuteurResponse(BaseModel):
    reponse: str
    type: Literal["socratique", "explication", "feedback",
                   "motivation", "orientation", "refus", "navigation"]
    question_suivante: Optional[str] = None
    cartes: List[ChatCard] = []
    flashcards_suggerees: List[str] = []
    redirect: Optional[str] = None
    source_rag: Optional[str] = None
    fallback_active: bool = False
