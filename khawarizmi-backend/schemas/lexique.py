from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LexiqueTermeResponse(BaseModel):
    id: str
    terme_fr: str
    terme_ar: str
    abreviation: Optional[str] = None
    type: str
    definition_fr: str
    definition_ar: str
    synonymes_fr: Optional[list[str]] = None
    synonymes_ar: Optional[list[str]] = None
    importance: str
    bac_frequent: bool
    chapitre_principal: str
    micro_concept_id: Optional[str] = None
    exemples_contexte: Optional[list[str]] = None
    termes_lies: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    categorie_fr: Optional[str] = None
    categorie_ar: Optional[str] = None
    domaine_fr: Optional[str] = None
    domaine_ar: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LexiqueSearchResponse(BaseModel):
    results: list[LexiqueTermeResponse]
    total: int
    query: str
