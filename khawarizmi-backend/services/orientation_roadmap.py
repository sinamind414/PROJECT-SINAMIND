"""Boussole pédagogique séquentielle du programme SVT 3AS.

La navigation reste libre, mais le parcours recommandé ne déverrouille une
unité qu'après validation réelle de toutes les précédentes. Une validation
combine trois preuves indépendantes : connaissance FSRS, couverture des
concepts essentiels et application sur un exercice BAC d'analyse documentaire.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from services.chapter_identity import normalize_chapter_id
from services.fsrs_unified import get_user_memory
from services.units import DOMAINS, UNITS_CATALOG

KNOWLEDGE_THRESHOLD = 80
COVERAGE_THRESHOLD = 80
BAC_THRESHOLD = 70
TARGET_STABILITY_DAYS = 10.0
SEUIL_DONE = KNOWLEDGE_THRESHOLD  # compatibilité du contrat S5

# Alias public historique : le parcours contient désormais les 11 unités.
PARCOURS = UNITS_CATALOG


def _value(item: object, name: str, default: Any = None) -> Any:
    value = getattr(item, name, default)
    if value is not None:
        return value
    extra = getattr(item, "extra", None)
    return extra.get(name, default) if isinstance(extra, dict) else default


def _chapter_to_id(chapter: object) -> str | None:
    """Compatibilité des anciens consumers, déléguée au normaliseur central."""
    return normalize_chapter_id(chapter)


@lru_cache(maxsize=1)
def _official_chapters() -> dict[str, dict]:
    path = Path(__file__).resolve().parents[1] / "data" / "official" / "programme_svt_3as_canonical.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        chapters: dict[str, dict] = {}
        for domain in payload.get("domaines", []):
            for source in domain.get("chapitres", []):
                chapter_id = normalize_chapter_id(source.get("id"))
                if chapter_id:
                    chapters[chapter_id] = {
                        **source,
                        "id": chapter_id,
                        "title_ar": source.get("nom_ar", ""),
                        "title_fr": source.get("nom_fr", ""),
                        "essential_concepts": source.get("micro_concepts", []),
                    }
        return chapters
    except (OSError, ValueError, TypeError):
        return {}


def _concept_is_observed(item: object) -> bool:
    fsrs_state = _value(item, "fsrs_state", {}) or {}
    return bool(
        float(_value(item, "stability", 0) or 0) > 0
        or _value(item, "last_review")
        or int(fsrs_state.get("reps", 0) or 0) > 0
        or int(_value(item, "attempts", 0) or 0) > 0
        or int(_value(item, "total_reviews", 0) or 0) > 0
    )


def _concept_key(item: object) -> str:
    item_id = _value(item, "item_id") or _value(item, "concept_id")
    return str(item_id) if item_id else f"anonymous:{id(item)}"


def _phase_states(unit: dict, learning_progress: int, learning_ready: bool) -> tuple[list[dict], dict | None]:
    phases = unit["phases"]
    if learning_ready:
        active_index = None
    else:
        active_index = min(int((learning_progress / 100) * len(phases)), len(phases) - 1)

    result = []
    active_phase = None
    for index, phase in enumerate(phases):
        if learning_ready or (active_index is not None and index < active_index):
            status = "done"
        elif index == active_index:
            status = "active"
        else:
            status = "locked"
        snapshot = {
            **phase,
            "status": status,
            "href": f"/lecons-sciences-experimentales/{phase['slug']}",
        }
        result.append(snapshot)
        if status == "active":
            active_phase = snapshot
    return result, active_phase


def _build_objective(unit: dict, active_phase: dict | None) -> dict:
    learning_ready = unit["knowledge_ready"] and unit["coverage_ready"]
    if not learning_ready:
        phase = active_phase or unit["phases"][0]
        reason_ar = (
            f"المعرفة {unit['knowledge']}٪ والتغطية {unit['coverage']}٪. "
            "أكمل الفهم ثم ثبّته بالاسترجاع النشط."
        )
        reason_fr = (
            f"Connaissance {unit['knowledge']} % et couverture {unit['coverage']} %. "
            "Comprends cette phase puis consolide-la par rappel actif."
        )
        return {
            "kind": "lesson",
            "unit_id": unit["id"],
            "roadmap_unit_id": unit["roadmap_id"],
            "chapter_id": unit["chapter_id"],
            "phase": phase,
            "title_ar": phase["title_ar"],
            "title_fr": f"Phase {phase['number']} · {unit['nom_fr']}",
            "reason_ar": reason_ar,
            "reason_fr": reason_fr,
            "unlock_condition_ar": (
                f"ارفع المعرفة والتغطية إلى {KNOWLEDGE_THRESHOLD}٪ على الأقل، "
                "ثم انتقل إلى تطبيق BAC."
            ),
            "unlock_condition_fr": (
                f"Atteins {KNOWLEDGE_THRESHOLD} % de connaissance et de couverture, "
                "puis valide l'application BAC."
            ),
            "href": phase["href"],
            "cta_ar": "ابدأ المرحلة",
            "cta_fr": "Commencer la phase",
        }

    return {
        "kind": "bac_validation",
        "unit_id": unit["id"],
        "roadmap_unit_id": unit["roadmap_id"],
        "chapter_id": unit["chapter_id"],
        "phase": None,
        "title_ar": f"طبّق مكتسبات {unit['nom_ar']} في وضعية BAC",
        "title_fr": f"Valide {unit['nom_fr']} sur une situation BAC",
        "reason_ar": (
            "المعرفة والتغطية جاهزتان، لكن الوحدة لا تُعتمد دون محاولة حقيقية "
            f"في تحليل الوثائق (النتيجة الحالية {unit['bac_score']}٪)."
        ),
        "reason_fr": (
            "La connaissance et la couverture sont prêtes, mais l'unité exige "
            f"une tentative réelle d'analyse documentaire (score actuel {unit['bac_score']} %)."
        ),
        "unlock_condition_ar": f"احصل على {BAC_THRESHOLD}٪ على الأقل في تطبيق BAC.",
        "unlock_condition_fr": f"Obtiens au moins {BAC_THRESHOLD} % à l'application BAC.",
        "href": f"/document-analysis/chapters/{unit['methodology_slug']}",
        "cta_ar": "تحقق في وضعية BAC",
        "cta_fr": "Valider en situation BAC",
    }


def _complete_objective() -> dict:
    return {
        "kind": "annales",
        "unit_id": None,
        "roadmap_unit_id": None,
        "chapter_id": None,
        "phase": None,
        "title_ar": "أتممت المسار الرسمي — انتقل إلى الحوليات",
        "title_fr": "Parcours officiel validé — passe aux annales",
        "reason_ar": "الوحدات الإحدى عشرة مثبتة بالمعرفة والتغطية والتطبيق.",
        "reason_fr": "Les onze unités sont prouvées par connaissance, couverture et application.",
        "unlock_condition_ar": "حافظ على المراجعة المتباعدة وحل مواضيع كاملة.",
        "unlock_condition_fr": "Entretiens la mémoire et résous des sujets complets.",
        "href": "/annales",
        "cta_ar": "افتح الحوليات",
        "cta_fr": "Ouvrir les annales",
    }


async def calculer_roadmap(db: AsyncSession, user_id: object) -> dict:
    memory = await get_user_memory(db, user_id, kinds=("concept", "verb_chapter"))
    official = _official_chapters()

    concept_items: dict[str, dict[str, object]] = {}
    bac_items: dict[str, list[object]] = {}
    for item in memory:
        chapter_id = normalize_chapter_id(_value(item, "chapter"))
        if not chapter_id:
            # Quelques lignes historiques ne portent le chapitre que dans item_id.
            item_id = str(_value(item, "item_id", ""))
            chapter_id = normalize_chapter_id(item_id.partition("::")[2])
        if not chapter_id:
            continue

        kind = _value(item, "kind", "concept")
        if kind == "verb_chapter":
            bac_items.setdefault(chapter_id, []).append(item)
            continue

        chapter_concepts = concept_items.setdefault(chapter_id, {})
        key = _concept_key(item)
        current = chapter_concepts.get(key)
        if current is None or float(_value(item, "stability", 0) or 0) > float(_value(current, "stability", 0) or 0):
            chapter_concepts[key] = item

    units: list[dict] = []
    predecessors_done = True
    active_unit: dict | None = None

    for global_index, source in enumerate(UNITS_CATALOG, start=1):
        chapter_id = source["chapter_id"]
        items = list(concept_items.get(chapter_id, {}).values())
        official_chapter = official.get(chapter_id, {})
        expected_count = max(len(official_chapter.get("essential_concepts", [])), 1)
        observed = [item for item in items if _concept_is_observed(item)]
        covered_count = min(len(observed), expected_count)
        coverage = round(min(100.0, covered_count / expected_count * 100))
        stability_total = sum(
            min(float(_value(item, "stability", 0) or 0), TARGET_STABILITY_DAYS)
            for item in observed
        )
        knowledge = round(min(100.0, stability_total / (expected_count * TARGET_STABILITY_DAYS) * 100))

        attempts = sum(max(int(_value(item, "attempts", 0) or 0), 0) for item in bac_items.get(chapter_id, []))
        scores = [
            int(_value(item, "last_score", 0) or 0)
            for item in bac_items.get(chapter_id, [])
            if int(_value(item, "attempts", 0) or 0) > 0
        ]
        bac_score = max(scores, default=0)
        knowledge_ready = knowledge >= KNOWLEDGE_THRESHOLD
        coverage_ready = coverage >= COVERAGE_THRESHOLD
        bac_validated = attempts > 0 and bac_score >= BAC_THRESHOLD
        validation_complete = knowledge_ready and coverage_ready and bac_validated

        if predecessors_done and validation_complete:
            status = "done"
        elif predecessors_done and active_unit is None:
            status = "active"
        else:
            status = "locked"

        learning_progress = min(knowledge, coverage)
        phases, active_phase = _phase_states(source, learning_progress, knowledge_ready and coverage_ready)
        if status == "locked":
            phases = [{**phase, "status": "locked"} for phase in phases]
            active_phase = None
        unit = {
            "id": source["id"],
            "roadmap_id": source["roadmap_id"],
            "num": global_index,
            "domain_id": source["domain_id"],
            "domain_number": source["domain_number"],
            "unit_number": source["unit_number"],
            "nom_ar": source["unit_ar"],
            "nom_fr": source["unit_fr"],
            "emoji": source["emoji"],
            "chapter_id": chapter_id,
            "methodology_slug": source["methodology_slug"],
            "statut": status,
            "verrouille_par": None if predecessors_done else units[-1]["id"],
            "knowledge": knowledge,
            "coverage": coverage,
            "bac_score": bac_score,
            "bac_attempts": attempts,
            "knowledge_ready": knowledge_ready,
            "coverage_ready": coverage_ready,
            "bac_validated": bac_validated,
            "validation_complete": validation_complete,
            "maitrise": knowledge,
            "progression": round((knowledge + coverage + min(bac_score, 100)) / 3),
            "concepts_seen": covered_count,
            "concepts_expected": expected_count,
            "phases": phases,
            "chapitres": [
                {
                    "id": chapter_id,
                    "nom_ar": official_chapter.get("title_ar", source["unit_ar"]),
                    "nom_fr": official_chapter.get("title_fr", source["unit_fr"]),
                    "maitrise": knowledge,
                    "couverture": coverage,
                    "href": phases[0]["href"],
                }
            ],
        }
        units.append(unit)
        if status == "active":
            active_unit = unit
        predecessors_done = predecessors_done and validation_complete

    if active_unit:
        active_phase = next((phase for phase in active_unit["phases"] if phase["status"] == "active"), None)
        objective = _build_objective(active_unit, active_phase)
        tone = "focus" if active_unit["knowledge"] == 0 and active_unit["coverage"] == 0 else "progress"
        coach = {
            "tone": tone,
            "ar": f"أنت في الوحدة {active_unit['num']} من 11. {objective['reason_ar']}",
            "fr": f"Tu es à l'unité {active_unit['num']} sur 11. {objective['reason_fr']}",
        }
    else:
        objective = _complete_objective()
        coach = {
            "tone": "success",
            "ar": "أحسنت! أثبتَّ الوحدات الإحدى عشرة. حان وقت الحوليات الكاملة.",
            "fr": "Bravo ! Les onze unités sont validées. Passe aux annales complètes.",
        }

    domains = []
    for domain in DOMAINS:
        domain_units = [unit for unit in units if unit["domain_id"] == domain["id"]]
        domains.append(
            {
                **domain,
                "units_total": len(domain_units),
                "units_done": sum(unit["statut"] == "done" for unit in domain_units),
                "unit_ids": [unit["id"] for unit in domain_units],
            }
        )

    done_count = sum(unit["statut"] == "done" for unit in units)
    return {
        "version": "orientation-v2",
        "domains": domains,
        "unites": units,
        "unite_active": active_unit["id"] if active_unit else None,
        "roadmap_unit_active": active_unit["roadmap_id"] if active_unit else None,
        "progression_globale": round(sum(unit["progression"] for unit in units) / len(units)),
        "units_done": done_count,
        "units_total": len(units),
        "phases_total": sum(len(unit["phases"]) for unit in units),
        "criteria": {
            "knowledge_threshold": KNOWLEDGE_THRESHOLD,
            "coverage_threshold": COVERAGE_THRESHOLD,
            "bac_threshold": BAC_THRESHOLD,
            "target_stability_days": TARGET_STABILITY_DAYS,
        },
        "prochain_objectif": {
            **objective,
            # Champs S5 conservés pendant la migration des consumers.
            "num": active_unit["num"] if active_unit else None,
            "nom_ar": active_unit["nom_ar"] if active_unit else objective["title_ar"],
            "nom_fr": active_unit["nom_fr"] if active_unit else objective["title_fr"],
            "maitrise": active_unit["knowledge"] if active_unit else 100,
            "chapitre_faible": (
                active_unit["chapitres"][0]
                if active_unit and objective["kind"] == "lesson"
                else None
            ),
        },
        "coach": coach,
    }
