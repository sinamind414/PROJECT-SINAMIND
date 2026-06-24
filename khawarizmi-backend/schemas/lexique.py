from datetime import datetime

from pydantic import BaseModel


class LexiqueTermeResponse(BaseModel):
    id: str
    terme_fr: str
    terme_ar: str
    abreviation: str | None = None
    type: str
    definition_fr: str
    definition_ar: str
    synonymes_fr: list[str] | None = None
    synonymes_ar: list[str] | None = None
    importance: str
    bac_frequent: bool
    chapitre_principal: str
    micro_concept_id: str | None = None
    exemples_contexte: list[str] | None = None
    termes_lies: list[str] | None = None
    tags: list[str] | None = None
    categorie_fr: str | None = None
    categorie_ar: str | None = None
    domaine_fr: str | None = None
    domaine_ar: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class LexiqueSearchResponse(BaseModel):
    results: list[LexiqueTermeResponse]
    total: int
    query: str
