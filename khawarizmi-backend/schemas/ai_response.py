from pydantic import BaseModel


class AIResponse(BaseModel):
    mode: str
    from_cache: bool = False
    fallback_active: bool = False
    tokens_used: int = 0

    content: str | None = None
    lang: str = "ar"
    sources: list[dict] = []
    cards: list[dict] = []
    source_rag: str | None = None

    pre_analyse: dict | None = None

    score: int | None = None
    statut: str | None = None
    feedback: str | None = None
    manquant: list[str] = []
    next_review_date: str | None = None
    source_eval: str | None = None
    methodology: dict | None = None
