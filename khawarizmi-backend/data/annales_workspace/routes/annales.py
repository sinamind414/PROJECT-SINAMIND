# Khawarizmi Pro — Routes API (Annales)
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from database import get_db
from models.annales import Annale, TypeAnnale, Niveau, Filiere
from schemas.annales import AnnaleCreate, AnnaleUpdate, AnnaleResponse, AnnaleListe

router = APIRouter(prefix="/annales", tags=["annales"])

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SEED_FILE = DATA_DIR / "annales_seed.json"


# ═══════════════════════════════════════════════════════════════════════
#  CRUD
# ═══════════════════════════════════════════════════════════════════════

@router.get("/", response_model=AnnaleListe)
def lister_annales(
    page: int = Query(1, ge=1),
    taille: int = Query(20, ge=1, le=100),
    matiere_id: Optional[int] = None,
    niveau: Optional[Niveau] = None,
    filiere: Optional[Filiere] = None,
    annee: Optional[int] = None,
    type_: Optional[TypeAnnale] = Query(None, alias="type"),
    recherche: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Retourne la liste paginée des annales avec filtres."""
    q = db.query(Annale)

    if matiere_id is not None:
        q = q.filter(Annale.matiere_id == matiere_id)
    if niveau is not None:
        q = q.filter(Annale.niveau == niveau)
    if filiere is not None:
        q = q.filter(Annale.filiere == filiere)
    if annee is not None:
        q = q.filter(Annale.annee == annee)
    if type_ is not None:
        q = q.filter(Annale.type == type_)
    if recherche:
        pattern = f"%{recherche}%"
        q = q.filter(
            or_(
                Annale.titre.ilike(pattern),
                Annale.tags.any(recherche),  # PostgreSQL array overlap
            )
        )

    total = q.count()
    items = (
        q.order_by(Annale.annee.desc(), Annale.created_at.desc())
        .offset((page - 1) * taille)
        .limit(taille)
        .all()
    )

    return AnnaleListe(total=total, page=page, taille=taille, items=items)


@router.get("/{annale_id}", response_model=AnnaleResponse)
def obtenir_annale(annale_id: int, db: Session = Depends(get_db)):
    """Retourne une annale par son ID."""
    annale = db.query(Annale).filter(Annale.id == annale_id).first()
    if not annale:
        raise HTTPException(status_code=404, detail="Annale introuvable")
    return annale


@router.post("/", response_model=AnnaleResponse, status_code=status.HTTP_201_CREATED)
def creer_annale(payload: AnnaleCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle annale."""
    annale = Annale(**payload.model_dump())
    db.add(annale)
    db.commit()
    db.refresh(annale)
    return annale


@router.patch("/{annale_id}", response_model=AnnaleResponse)
def modifier_annale(annale_id: int, payload: AnnaleUpdate, db: Session = Depends(get_db)):
    """Modifie une annale existante (patch partiel)."""
    annale = db.query(Annale).filter(Annale.id == annale_id).first()
    if not annale:
        raise HTTPException(status_code=404, detail="Annale introuvable")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(annale, field, value)

    db.commit()
    db.refresh(annale)
    return annale


@router.delete("/{annale_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_annale(annale_id: int, db: Session = Depends(get_db)):
    """Supprime une annale."""
    annale = db.query(Annale).filter(Annale.id == annale_id).first()
    if not annale:
        raise HTTPException(status_code=404, detail="Annale introuvable")
    db.delete(annale)
    db.commit()


# ═══════════════════════════════════════════════════════════════════════
#  Seed
# ═══════════════════════════════════════════════════════════════════════

@router.post("/seed", status_code=status.HTTP_201_CREATED)
def seed_annales(db: Session = Depends(get_db)):
    """Importe les données seed depuis data/annales_seed.json."""
    if not SEED_FILE.exists():
        raise HTTPException(404, detail=f"Fichier seed introuvable : {SEED_FILE}")

    data = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    matieres = data.get("matieres", [])
    annales = data.get("annales", [])

    from models.matiere import Matiere

    created_matieres = 0
    for m in matieres:
        if not db.query(Matiere).filter(Matiere.slug == m["slug"]).first():
            db.add(Matiere(**m))
            created_matieres += 1

    created_annales = 0
    for a in annales:
        if not db.query(Annale).filter(Annale.slug == a["slug"]).first():
            db.add(Annale(**a))
            created_annales += 1

    db.commit()
    return {
        "detail": "Seed exécuté avec succès",
        "matieres_creées": created_matieres,
        "annales_créées": created_annales,
    }