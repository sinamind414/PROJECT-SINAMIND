# routes/programme.py
"""Routes pour le programme officiel."""

import unicodedata
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user

router = APIRouter(prefix="/api/programme", tags=["Programme"])


def normalize_filiere(filiere: str) -> str:
    """Normalise la filière pour matcher la DB."""
    # NFC garantit cohérence des accents
    f = unicodedata.normalize("NFC", filiere).strip()
    if f.lower() == "sciences naturelles":
        return "Sciences Experimentales"
    return f


@router.get("/{matiere}/{filiere}")
async def get_programme(
    matiere: str,
    filiere: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retourne le programme complet d'une matière/filière."""

    # Normaliser pour cohérence
    matiere = normalize_filiere(matiere)
    filiere = normalize_filiere(filiere)

    # Query avec UNACCENT pour matcher sans/avec accents
    result = await db.execute(
        text("""
            SELECT
                d.id as domain_id,
                d.numero as domain_numero,
                d.titre_fr as domain_titre_fr,
                d.titre_ar as domain_titre_ar,
                u.id as unit_id,
                u.numero as unit_numero,
                u.titre_fr as unit_titre_fr,
                u.titre_ar as unit_titre_ar,
                u.page as unit_page,
                c.id as chapter_id,
                c.numero as chapter_numero,
                c.titre_fr as chapter_titre_fr,
                c.titre_ar as chapter_titre_ar,
                c.page as chapter_page,
                c.type as chapter_type,
                c.importance as chapter_importance
            FROM domains d
            LEFT JOIN units u ON u.domain_id = d.id
            LEFT JOIN chapters c ON c.unit_id = u.id
            WHERE LOWER(d.matiere) = LOWER(:matiere)
            AND (
                LOWER(d.filiere) = LOWER(:filiere)
                OR LOWER(REPLACE(d.filiere, 'é', 'e')) =
                   LOWER(REPLACE(:filiere, 'é', 'e'))
            )
            ORDER BY d.numero, u.numero, c.numero
        """),
        {"matiere": matiere, "filiere": filiere}
    )

    rows = result.fetchall()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun programme trouvé pour "
                   f"{matiere} - {filiere}"
        )

    # Restructurer en hiérarchie
    domains_map = {}

    for row in rows:
        d_id = str(row.domain_id)

        if d_id not in domains_map:
            domains_map[d_id] = {
                "id": d_id,
                "numero": row.domain_numero,
                "titre_fr": row.domain_titre_fr,
                "titre_ar": row.domain_titre_ar,
                "units": {}
            }

        if row.unit_id:
            u_id = str(row.unit_id)
            domain = domains_map[d_id]

            if u_id not in domain["units"]:
                domain["units"][u_id] = {
                    "id": u_id,
                    "numero": row.unit_numero,
                    "titre_fr": row.unit_titre_fr,
                    "titre_ar": row.unit_titre_ar,
                    "page": row.unit_page,
                    "chapters": []
                }

            if row.chapter_id:
                domain["units"][u_id]["chapters"].append({
                    "id": str(row.chapter_id),
                    "numero": row.chapter_numero,
                    "titre_fr": row.chapter_titre_fr,
                    "titre_ar": row.chapter_titre_ar,
                    "page": row.chapter_page,
                    "type": row.chapter_type,
                    "importance": row.chapter_importance
                })

    # Convertir units dict en list
    domains = []
    for d in domains_map.values():
        d["units"] = list(d["units"].values())
        domains.append(d)

    return {
        "matiere": matiere,
        "filiere": filiere,
        "domains": domains,
        "total_chapters": sum(
            len(u["chapters"])
            for d in domains
            for u in d["units"]
        )
    }


@router.get("/{matiere}/{filiere}/chapters/critical")
async def get_critical_chapters(
    matiere: str,
    filiere: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retourne uniquement les chapitres critiques."""

    matiere = normalize_filiere(matiere)
    filiere = normalize_filiere(filiere)

    result = await db.execute(
        text("""
            SELECT
                c.id, c.numero, c.titre_fr, c.titre_ar,
                c.page, c.type, c.importance,
                u.titre_fr as unit_titre,
                d.titre_fr as domain_titre
            FROM chapters c
            JOIN units u ON u.id = c.unit_id
            JOIN domains d ON d.id = u.domain_id
            WHERE LOWER(d.matiere) = LOWER(:matiere)
            AND (
                LOWER(d.filiere) = LOWER(:filiere)
                OR LOWER(REPLACE(d.filiere, 'é', 'e')) =
                   LOWER(REPLACE(:filiere, 'é', 'e'))
            )
            AND c.importance = 'critique'
            ORDER BY d.numero, u.numero, c.numero
        """),
        {"matiere": matiere, "filiere": filiere}
    )

    chapters = [dict(r._mapping) for r in result.fetchall()]

    return {
        "matiere": matiere,
        "filiere": filiere,
        "critical_chapters": chapters,
        "total": len(chapters)
    }
