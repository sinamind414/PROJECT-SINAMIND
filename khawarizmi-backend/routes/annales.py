"""Routes pour les annales BAC."""

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user

router = APIRouter(prefix="/api/annales", tags=["Annales"])


@router.get("/")
async def lister_annales(
    page: int = Query(1, ge=1),
    taille: int = Query(20, ge=1, le=100),
    matiere: str | None = None,
    niveau: str | None = None,
    filiere: str | None = None,
    annee: int | None = None,
    type_: str = Query(None, alias="type"),
    recherche: str | None = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conditions = []
    params = {}

    if matiere:
        conditions.append("matiere = :matiere")
        params["matiere"] = matiere
    if niveau:
        conditions.append("niveau = :niveau")
        params["niveau"] = niveau
    if filiere:
        conditions.append("filiere = :filiere")
        params["filiere"] = filiere
    if annee:
        conditions.append("annee = :annee")
        params["annee"] = annee
    if type_:
        conditions.append("type = :type")
        params["type"] = type_
    if recherche:
        conditions.append("(titre ILIKE :recherche OR :recherche2 = ANY(tags))")
        params["recherche"] = f"%{recherche}%"
        params["recherche2"] = recherche

    where_clause = " AND ".join(conditions) if conditions else "TRUE"

    offset = (page - 1) * taille

    count_sql = text(f"SELECT COUNT(*) FROM annales WHERE {where_clause}")
    total = await db.scalar(count_sql, params)

    data_sql = text(f"""
        SELECT * FROM annales
        WHERE {where_clause}
        ORDER BY annee DESC, created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    params["limit"] = taille
    params["offset"] = offset
    result = await db.execute(data_sql, params)
    items = [dict(r._mapping) for r in result.fetchall()]

    return {"total": total, "page": page, "taille": taille, "items": items}


@router.get("/{annale_id}")
async def obtenir_annale(
    annale_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("SELECT * FROM annales WHERE id = :id"), {"id": annale_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(404, "Annale introuvable")
    return dict(row._mapping)


@router.post("/seed")
async def seed_annales(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    seed_path = Path(__file__).parent.parent / "data" / "annales_seed.json"
    if not seed_path.exists():
        raise HTTPException(404, "Fichier seed introuvable")

    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for annale in data.get("annales", []):
        await db.execute(
            text("""
                INSERT INTO annales (titre, titre_ar, slug, matiere, niveau, filiere, annee, type,
                                     fichier_sujet, fichier_correction, tags, difficulte)
                VALUES (:titre, :titre_ar, :slug, :matiere, :niveau, :filiere, :annee, :type,
                        :fichier_sujet, :fichier_correction, :tags, :difficulte)
                ON CONFLICT (slug) DO UPDATE SET titre_ar = EXCLUDED.titre_ar
            """),
            {
                "titre": annale["titre"],
                "titre_ar": annale.get("titre_ar", annale["titre"]),
                "slug": annale["slug"],
                "matiere": annale.get("matiere", "SVT"),
                "niveau": annale.get("niveau", "3ème année"),
                "filiere": annale.get("filiere", "S"),
                "annee": annale["annee"],
                "type": annale.get("type", "examen"),
                "fichier_sujet": annale["fichier_sujet"],
                "fichier_correction": annale.get("fichier_correction"),
                "tags": annale.get("tags", []),
                "difficulte": annale.get("difficulté", 3),
            },
        )
        count += 1

    await db.commit()
    return {"message": f"{count} annales importées"}
