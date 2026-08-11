"""Normalisation centrale des identités de chapitre/unité historiques.

Les producteurs stockent encore plusieurs formes (``ch_*``, ``u1``, slugs
méthodologiques ou libellés). Toute lecture et toute nouvelle écriture doivent
passer ici afin que la progression ne soit pas fragmentée.
"""

from __future__ import annotations

import re
import unicodedata

from services.units import PHASES_BY_SLUG, UNITS_BY_CHAPTER, UNITS_BY_ID, UNITS_CATALOG

EXPLICIT_ALIASES = {
    # Identités historiques observées en production.
    "ch1_synthese_proteines": "ch1_proteines",
    "ch_proteines": "ch1_proteines",
    "ch_structure": "ch_structure_proteines",
    "ch2_structure_proteines": "ch_structure_proteines",
    "ch_enzymes": "ch2_enzymes",
    "ch3_enzymes": "ch2_enzymes",
    "ch_immunite": "ch3_immunite",
    "ch4_immunite": "ch3_immunite",
    "ch_nerveux": "ch4_nerveux",
    "ch5_nerveux": "ch4_nerveux",
    "ch5_photosynthese": "ch_photosynthese",
    "ch6_photosynthese": "ch_photosynthese",
    "ch_respiration": "ch_respiration",
    "ch6_respiration": "ch_respiration",
    "ch7_respiration": "ch_respiration",
    "ch_energetique": "ch_bilan_energetique",
    "ch8_energetique": "ch_bilan_energetique",
    "ch_tectonique": "ch_tectonique_plaques",
    "ch9_tectonique": "ch_tectonique_plaques",
    "ch_globe": "ch_structure_terre",
    "ch10_structure_globe": "ch_structure_terre",
    "ch_geologie": "ch_structures_geologiques",
    "ch11_structures_geologiques": "ch_structures_geologiques",
    "ch1_protein_synthesis": "ch1_proteines",
    "ch3_immune": "ch3_immunite",
    "ch_respiration_fermentation": "ch_respiration",
    "ch5_tectonique": "ch_tectonique_plaques",
    "ch_structure_globe": "ch_structure_terre",
    "ch_banies_geologiques": "ch_structures_geologiques",
}


def fold_identity(value: object) -> str:
    """Forme comparable stable (minuscules, accents et ponctuation retirés)."""
    if value is None:
        return ""
    text = unicodedata.normalize("NFKD", str(value).strip().lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^\w\u0600-\u06ff]+", " ", text).strip()


def _unit_for_domain_number(domain_number: int, unit_number: int) -> dict | None:
    return next(
        (
            unit
            for unit in UNITS_CATALOG
            if unit["domain_number"] == domain_number and unit["unit_number"] == unit_number
        ),
        None,
    )


_DIRECT: dict[str, str] = {}
for canonical in UNITS_BY_CHAPTER:
    _DIRECT[fold_identity(canonical)] = canonical
for alias, canonical in EXPLICIT_ALIASES.items():
    _DIRECT[fold_identity(alias)] = canonical
for unit in UNITS_CATALOG:
    for identity in (
        unit["id"],
        unit["roadmap_id"],
        unit["unit_ar"],
        unit["unit_fr"],
        unit["methodology_slug"],
    ):
        _DIRECT[fold_identity(identity)] = unit["chapter_id"]
    for phase in unit["phases"]:
        _DIRECT[fold_identity(phase["slug"])] = unit["chapter_id"]


# Des libellés historiques précis qui ne sont pas des titres d'unité.
_HISTORICAL_HINTS = sorted(
    (
        (fold_identity(keyword), unit["chapter_id"])
        for unit in UNITS_CATALOG
        for keyword in unit["keywords"]
        if len(fold_identity(keyword)) >= 6
    ),
    key=lambda pair: len(pair[0]),
    reverse=True,
)


def normalize_chapter_id(value: object) -> str | None:
    """Résout une identité connue vers l'un des 11 ``chapter_id`` officiels.

    Retourne ``None`` pour une valeur absente ou ambiguë : mieux vaut ne pas
    attribuer une preuve au mauvais chapitre que gonfler une progression.
    """
    folded = fold_identity(value)
    if not folded:
        return None

    direct = _DIRECT.get(folded)
    if direct:
        return direct

    # Slugs de validation BAC : d2-u1-c3-... ; IDs roadmap : d2_u1.
    domain_unit = re.search(r"(?:^|\s)d\s*(\d+)\s*u\s*(\d+)(?:\s|$)", folded)
    if domain_unit:
        unit = _unit_for_domain_number(int(domain_unit.group(1)), int(domain_unit.group(2)))
        if unit:
            return unit["chapter_id"]

    # IDs globaux du drill : u1..u11. ``u_1`` est toléré pour l'historique.
    global_unit = re.fullmatch(r"u\s*(\d{1,2})", folded)
    if global_unit:
        unit = UNITS_BY_ID.get(f"u{int(global_unit.group(1))}")
        if unit:
            return unit["chapter_id"]

    matches = {chapter for hint, chapter in _HISTORICAL_HINTS if hint in folded}
    if len(matches) == 1:
        return matches.pop()
    return None


def canonical_chapter(value: object, *, fallback: str | None = None) -> str | None:
    """Alias explicite pour les producteurs : normalise, puis fallback documenté."""
    return normalize_chapter_id(value) or fallback


def unit_for_chapter(value: object) -> dict | None:
    canonical = normalize_chapter_id(value)
    return UNITS_BY_CHAPTER.get(canonical) if canonical else None


def chapter_for_phase(phase_slug: str) -> str | None:
    if phase_slug not in PHASES_BY_SLUG:
        return None
    return normalize_chapter_id(phase_slug)
