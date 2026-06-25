from pydantic import BaseModel


class MethodologyResult(BaseModel):
    verb_identifie: str | None
    type_tache: str
    note_methodologie: int
    note_max: int
    points_forts: list[str] = []
    points_faibles: list[str] = []
    feedback_principal: str
    recommandation: str
    structure: dict | None = None
