"""Schémas Pydantic pour le Tuteur Contextuel."""

from typing import Literal

from pydantic import BaseModel, Field


class ChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatContext(BaseModel):
    chapitre: str | None = None
    page_source: str | None = None
    fsrs_stability: float | None = None
    fsrs_due: bool | None = None
    last_score: int | None = None
    orientation_chapitre: str | None = None
    history: list[ChatHistoryMessage] = []


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
    type: Literal["socratique", "explication", "feedback", "motivation", "orientation", "refus", "navigation"]
    question_suivante: str | None = None
    cartes: list[ChatCard] = []
    flashcards_suggerees: list[str] = []
    redirect: str | None = None
    source_rag: str | None = None
    fallback_active: bool = False
