from pydantic import BaseModel


class StructureResult(BaseModel):
    parts: dict[str, bool] = {}
    score: float = 1.0
    total: int = 1
    found: int = 1


class MethodologyResult(BaseModel):
    verb_identifie: str | None = None
    type_tache: str = "unknown"
    note_methodologie: int = 0
    note_max: int = 10
    points_forts: list[str] = []
    points_faibles: list[str] = []
    feedback_principal: str = ""
    recommandation: str = ""
    structure: StructureResult | None = None
