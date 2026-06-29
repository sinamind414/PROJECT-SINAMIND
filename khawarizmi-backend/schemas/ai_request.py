from pydantic import BaseModel, model_validator
from typing import Literal


class ChatOrchestratorRequest(BaseModel):
    mode: Literal["guided", "free", "quick", "methodology", "tutor"]
    message: str
    lang: str = "ar"
    history: list[dict] = []

    sujet_id: str | None = None
    question_id: str | None = None
    niveau_sm2: int = 0
    score_actuel: float = 0.0
    mode_force: str | None = None

    chapitre: str | None = None

    @model_validator(mode="after")
    def validate_mode_fields(self) -> "ChatOrchestratorRequest":
        if self.mode in ("guided", "methodology"):
            if not self.sujet_id or not self.question_id:
                raise ValueError(
                    f"mode={self.mode} requiert sujet_id et question_id"
                )
        if not self.message or not self.message.strip():
            raise ValueError("message ne peut pas être vide")
        if len(self.message) > 5000:
            raise ValueError("message trop long (max 5000 caractères)")
        return self


class EvaluateOrchestratorRequest(BaseModel):
    question_id: str
    reponse_eleve: str
    tentative: int = 1
    lang: str = "fr"
    include_methodology: bool = True

    @model_validator(mode="after")
    def validate_fields(self) -> "EvaluateOrchestratorRequest":
        if not self.question_id.strip():
            raise ValueError("question_id requis")
        if not self.reponse_eleve.strip():
            raise ValueError("reponse_eleve requise")
        if len(self.reponse_eleve) > 10000:
            raise ValueError("reponse_eleve trop longue (max 10000 caractères)")
        return self
