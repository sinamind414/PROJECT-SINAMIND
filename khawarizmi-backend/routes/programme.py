# routes/programme.py
"""Routes pour le programme officiel.

Strategie de resolution :
  1. Tentative DB (tables domains -> units -> chapters)
  2. Si DB vide -> fallback JSON (data/programmes/svt_sciences_experimentales.json)
  3. Si JSON absent -> 404
"""

import json
import logging
import unicodedata
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user
from fallback_programme_data import FALLBACK_PROGRAMME_DATA

router = APIRouter(prefix="/api/programme", tags=["Programme"])
logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════
# Normalisation filiere
# ════════════════════════════════════════════════════════════════

_FILIERE_ALIASES: dict[str, str] = {
    "sciences naturelles": "Sciences Experimentales",
    "sciences experimentales": "Sciences Experimentales",
    "se": "Sciences Experimentales",
    "snv": "Sciences Experimentales",
}


def normalize_filiere(filiere: str) -> str:
    """Normalise la filiere pour matcher la DB."""
    f = unicodedata.normalize("NFC", filiere).strip()
    return _FILIERE_ALIASES.get(f.lower(), f)


# ════════════════════════════════════════════════════════════════
# Fallback JSON (charge 1x au demarrage)
# ════════════════════════════════════════════════════════════════

_JSON_PATH = Path(__file__).parent.parent / "data" / "programmes" / "svt_sciences_experimentales.json"

_programme_cache: dict | None = None


def _load_programme_fallback() -> dict:
    """Charge le programme. Tente JSON d'abord, sinon data/fallback_programme_data.py (embarqué)."""
    global _programme_cache
    if _programme_cache is not None:
        return _programme_cache

    # Priorité 1: fichier JSON (si présent dans l'image Docker)
    if _JSON_PATH.exists():
        try:
            with open(_JSON_PATH, encoding="utf-8") as f:
                raw = json.load(f)
            logger.info("Programme fallback JSON loaded from %s", _JSON_PATH)
            _programme_cache = raw
            return _programme_cache
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Programme fallback JSON error: %s", exc)

    # Priorité 2: données embarquées (toujours disponible)
    logger.info("Using embedded fallback programme data (%d domains)", len(FALLBACK_PROGRAMME_DATA.get("domains", [])))
    _programme_cache = FALLBACK_PROGRAMME_DATA
    return _programme_cache


def _restructure_json_to_response(raw: dict) -> dict:
    """Convertit le format JSON import en format reponse API (avec UUID)."""
    domains_out = []
    for d in raw.get("domains", []):
        domain_id = str(uuid4())
        units_out = []
        for u in d.get("units", []):
            unit_id = str(uuid4())
            chapters_out = []
            for ch in u.get("chapters", []):
                chapters_out.append({
                    "id": str(uuid4()),
                    "numero": ch["numero"],
                    "titre_fr": ch["titre_fr"],
                    "titre_ar": ch.get("titre_ar"),
                    "page": ch.get("page"),
                    "type": ch.get("type"),
                    "importance": ch.get("importance", "moyenne"),
                })
            units_out.append({
                "id": unit_id,
                "numero": u["numero"],
                "titre_fr": u["titre_fr"],
                "titre_ar": u.get("titre_ar"),
                "page": u.get("page"),
                "chapters": chapters_out,
            })
        domains_out.append({
            "id": domain_id,
            "numero": d["numero"],
            "titre_fr": d["titre_fr"],
            "titre_ar": d.get("titre_ar"),
            "units": units_out,
        })

    return {
        "matiere": raw.get("matiere", ""),
        "filiere": raw.get("filiere", ""),
        "domains": domains_out,
        "total_chapters": sum(
            len(ch) for d in domains_out for u in d["units"] for ch in [u["chapters"]]
        ),
    }


# ════════════════════════════════════════════════════════════════
# Debug endpoint (AVANT le catch-all pour ne pas etre intercepte)
# ════════════════════════════════════════════════════════════════

@router.get("/_debug/status")
async def debug_status(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Diagnostic : etat DB + JSON fallback."""
    try:
        result = await db.execute(text("SELECT COUNT(*) FROM domains"))
        db_count = result.scalar_one()
    except Exception as exc:
        db_count = f"ERROR: {exc}"

    raw = _load_programme_fallback()
    json_domain_count = len(raw.get("domains", [])) if raw else 0

    return {
        "db_domains_count": db_count,
        "json_fallback_loaded": bool(raw),
        "json_domain_count": json_domain_count,
        "json_path": str(_JSON_PATH),
        "filiere_aliases": _FILIERE_ALIASES,
    }


# ════════════════════════════════════════════════════════════════
# Route principale
# ════════════════════════════════════════════════════════════════

@router.get("/{matiere}/{filiere}")
async def get_programme(
    matiere: str,
    filiere: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne le programme complet d'une matiere/filiere."""

    matiere = normalize_filiere(matiere)
    filiere = normalize_filiere(filiere)

    # 1. Tentative DB
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
                OR LOWER(REPLACE(d.filiere, '\u00e9', 'e')) =
                   LOWER(REPLACE(:filiere, '\u00e9', 'e'))
            )
            ORDER BY d.numero, u.numero, c.numero
        """),
        {"matiere": matiere, "filiere": filiere},
    )

    rows = result.fetchall()

    if rows:
        return _restructure_db_rows(rows, matiere, filiere)

    # 2. Fallback JSON
    logger.warning(
        "Programme DB empty for matiere=%s filiere=%s -- using JSON fallback",
        matiere,
        filiere,
    )

    raw = _load_programme_fallback()
    if not raw or not raw.get("domains"):
        raise HTTPException(
            status_code=404,
            detail=f"Aucun programme trouve pour {matiere} - {filiere}",
        )

    return _restructure_json_to_response(raw)


def _restructure_db_rows(rows, matiere: str, filiere: str) -> dict:
    """Convertit les rows DB en format reponse hiérarchique."""
    domains_map = {}

    for row in rows:
        d_id = str(row.domain_id)

        if d_id not in domains_map:
            domains_map[d_id] = {
                "id": d_id,
                "numero": row.domain_numero,
                "titre_fr": row.domain_titre_fr,
                "titre_ar": row.domain_titre_ar,
                "units": {},
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
                    "chapters": [],
                }

            if row.chapter_id:
                domain["units"][u_id]["chapters"].append(
                    {
                        "id": str(row.chapter_id),
                        "numero": row.chapter_numero,
                        "titre_fr": row.chapter_titre_fr,
                        "titre_ar": row.chapter_titre_ar,
                        "page": row.chapter_page,
                        "type": row.chapter_type,
                        "importance": row.chapter_importance,
                    }
                )

    domains = []
    for d in domains_map.values():
        d["units"] = list(d["units"].values())
        domains.append(d)

    return {
        "matiere": matiere,
        "filiere": filiere,
        "domains": domains,
        "total_chapters": sum(len(u["chapters"]) for d in domains for u in d["units"]),
    }


# ════════════════════════════════════════════════════════════════
# Endpoint critique (inchangé)
# ════════════════════════════════════════════════════════════════

@router.get("/{matiere}/{filiere}/chapters/critical")
async def get_critical_chapters(
    matiere: str, filiere: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)
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
                OR LOWER(REPLACE(d.filiere, '\u00e9', 'e')) =
                   LOWER(REPLACE(:filiere, '\u00e9', 'e'))
            )
            AND c.importance = 'critique'
            ORDER BY d.numero, u.numero, c.numero
        """),
        {"matiere": matiere, "filiere": filiere},
    )

    chapters = [dict(r._mapping) for r in result.fetchall()]

    return {"matiere": matiere, "filiere": filiere, "critical_chapters": chapters, "total": len(chapters)}
