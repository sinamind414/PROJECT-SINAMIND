# Khawarizmi Pro — Schémas Pydantic (Annales)
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from models.annales import TypeAnnale, Niveau, Filiere, Difficulte


# ── Matière (léger, pour les réponses) ─────────────────────────────────
class MatiereLite(BaseModel):
    id: int
    nom: str
    slug: str

    model_config = {"from_attributes": True}


# ── Annales ────────────────────────────────────────────────────────────
class AnnaleBase(BaseModel):
    titre: str = Field(..., min_length=3, max_length=300)
    slug: str = Field(..., min_length=3, max_length=300)
    matiere_id: int
    niveau: Niveau
    filiere: Filiere
    annee: int = Field(..., ge=1900, le=2100)
    type: TypeAnnale = TypeAnnale.examen
    fichier_sujet: str = Field(..., max_length=500)
    fichier_correction: Optional[str] = Field(None, max_length=500)
    tags: list[str] = Field(default_factory=list, max_length=10)
    difficulté: Difficulte = Difficulte.moyen

    @field_validator("annee")
    @classmethod
    def annee_plausible(cls, v: int) -> int:
        if v < 1900 or v > datetime.now().year + 1:
            raise ValueError(f"Année {v} hors plage 1900-{datetime.now().year + 1}")
        return v


class AnnaleCreate(AnnaleBase):
    """Payload pour POST /annales."""
    pass


class AnnaleUpdate(BaseModel):
    """Payload pour PATCH /annales/{id}. Tous les champs optionnels."""
    titre: Optional[str] = Field(None, min_length=3, max_length=300)
    slug: Optional[str] = Field(None, min_length=3, max_length=300)
    matiere_id: Optional[int] = None
    niveau: Optional[Niveau] = None
    filiere: Optional[Filiere] = None
    annee: Optional[int] = Field(None, ge=1900, le=2100)
    type: Optional[TypeAnnale] = None
    fichier_sujet: Optional[str] = Field(None, max_length=500)
    fichier_correction: Optional[str] = Field(None, max_length=500)
    tags: Optional[list[str]] = Field(None, max_length=10)
    difficulté: Optional[Difficulte] = None


class AnnaleResponse(AnnaleBase):
    """Réponse GET /annales – inclus l'id, timestamps et la matière liée."""
    id: int
    matiere: Optional[MatiereLite] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AnnaleListe(BaseModel):
    """Réponse paginée."""
    total: int
    page: int
    taille: int
    items: list[AnnaleResponse]
