from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    sujet_id: str = Field(min_length=3, max_length=100)
    question_id: str = Field(min_length=1, max_length=50)
    message: str = Field(min_length=5, max_length=5000)
    mode_force: str | None = None
    niveau_sm2: int = Field(default=0, ge=0, le=4)
    score_actuel: float = Field(default=0.0, ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    type_erreur: str
    ce_qui_est_correct: str
    question_socratique: str
    indice_si_bloque: str | None = None
    feedback_bienveillant: str
    pre_analyse: dict | None = None
    tokens_utilises: int | None = None
    economie_tokens: int = 0
