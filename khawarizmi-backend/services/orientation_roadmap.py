"""Boussole pédagogique : parcours du programme unité par unité.

Le service transforme le programme canonique de SVT 3AS en cinq unités
ordonnées, calcule leur maîtrise depuis la mémoire FSRS unifiée et impose un
verrouillage séquentiel : une unité n'est accessible que lorsque la précédente
atteint 80 %.

Le calcul ne fait aucun appel IA :

    maîtrise = 100 × Σ min(stability, 10) / (10 × nombre de concepts)
"""

from __future__ import annotations

import json
import logging
import re
import unicodedata
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from services.fsrs_unified import get_user_memory

logger = logging.getLogger("khawarizmi.orientation_roadmap")

PARCOURS: list[dict[str, Any]] = [
    {
        "id": "u1",
        "num": 1,
        "titre_fr": "Consommation de la matière organique et flux d'énergie",
        "titre_ar": "استهلاك المادة العضوية وتدفق الطاقة",
        "emoji": "⚡",
        "objectif_fr": (
            "Respiration, fermentation, photosynthèse : comment la matière "
            "organique libère et stocke l'énergie."
        ),
        "objectif_ar": (
            "التنفس والتخمر والتركيب الضوئي: كيف تحرر المادة العضوية الطاقة وتخزنها"
        ),
        "chapitres": [
            "ch_respiration",
            "ch_photosynthese",
            "ch_bilan_energetique",
        ],
        "lecon_slug": "phase_respiration_photosynthese",
    },
    {
        "id": "u2",
        "num": 2,
        "titre_fr": "Spécialisation fonctionnelle des protéines",
        "titre_ar": "التخصص الوظيفي للبروتينات",
        "emoji": "🧬",
        "objectif_fr": (
            "Synthèse, structure, fonction et activité enzymatique : le lien "
            "gène → protéine → fonction."
        ),
        "objectif_ar": (
            "تركيب البروتينات وبنيتها ووظيفتها والنشاط الإنزيمي: العلاقة بين "
            "الجين والبروتين والوظيفة"
        ),
        "chapitres": [
            "ch1_proteines",
            "ch_structure_proteines",
            "ch2_enzymes",
        ],
        "lecon_slug": "phase_synthese_proteines",
    },
    {
        "id": "u3",
        "num": 3,
        "titre_fr": "La communication nerveuse",
        "titre_ar": "التواصل العصبي",
        "emoji": "🧠",
        "objectif_fr": (
            "Neurone, message nerveux, synapse : comment l'information circule "
            "dans le système nerveux."
        ),
        "objectif_ar": (
            "العصبون والرسالة العصبية والمشبك: كيف تنتقل المعلومة في الجهاز العصبي"
        ),
        "chapitres": ["ch4_nerveux"],
        "lecon_slug": "phase_communication_nerveuse",
    },
    {
        "id": "u4",
        "num": 4,
        "titre_fr": "L'immunité",
        "titre_ar": "المناعة",
        "emoji": "🛡️",
        "objectif_fr": (
            "Réactions immunitaires innées et adaptatives : comment l'organisme "
            "se défend."
        ),
        "objectif_ar": (
            "الاستجابات المناعية الفطرية والتكيفية: كيف يدافع الجسم عن نفسه"
        ),
        "chapitres": ["ch3_immunite"],
        "lecon_slug": "phase_immunite",
    },
    {
        "id": "u5",
        "num": 5,
        "titre_fr": "Tectonique globale (Géologie)",
        "titre_ar": "التكتونية العامة (جيولوجيا)",
        "emoji": "🌍",
        "objectif_fr": (
            "Plaques, structure du globe et structures associées : la dynamique "
            "de la lithosphère."
        ),
        "objectif_ar": (
            "الصفائح وبنية الكرة الأرضية والتراكيب المرافقة: ديناميكية الغلاف الصخري"
        ),
        "chapitres": [
            "ch_tectonique_plaques",
            "ch_structure_terre",
            "ch_banies_geologiques",
        ],
        "lecon_slug": "phase_tectonique",
    },
]

SEUIL_DONE = 80.0
STABILITY_MAX = 10.0

# Routes réellement disponibles dans le catalogue de leçons interactives.
_LESSON_SLUG_BY_CHAPTER = {
    "ch_respiration": "phase13_chapitres_25_26",
    "ch_photosynthese": "phase11_chapitres_21_22",
    "ch_bilan_energetique": "phase15_chapitres_29_30",
    "ch1_proteines": "phase1_chapitres_1_2",
    "ch_structure_proteines": "phase3_chapitres_5_6",
    "ch2_enzymes": "phase4_chapitres_7_8",
    "ch4_nerveux": "phase8_chapitres_15_16",
    "ch3_immunite": "phase5_chapitres_9_10",
    "ch_tectonique_plaques": "phase16_chapitres_31_32",
    "ch_structure_terre": "phase19_chapitres_37_38",
    "ch_banies_geologiques": "phase21_chapitres_41_42",
}

_PROGRAMME_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "official"
    / "programme_svt_3as_canonical.json"
)
_CONCEPTS_PAR_CHAPITRE: dict[str, int] = {}
_NOMS_CHAPITRES: dict[str, dict[str, str]] = {}
_ALIASES: dict[str, str] = {}


def _norm(value: str) -> str:
    """Normalise un identifiant ou titre de chapitre de manière tolérante."""
    normalized = unicodedata.normalize("NFKD", value or "").lower()
    without_accents = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return re.sub(r"[^a-z0-9\u0600-\u06ff]", "", without_accents)


def _load_programme() -> None:
    """Charge une seule fois les chapitres et leurs alias canoniques."""
    if _CONCEPTS_PAR_CHAPITRE:
        return

    try:
        data = json.loads(_PROGRAMME_PATH.read_text(encoding="utf-8"))
        for domaine in data.get("domaines", []):
            for chapitre in domaine.get("chapitres", []):
                chapter_id = chapitre["id"]
                _CONCEPTS_PAR_CHAPITRE[chapter_id] = len(
                    chapitre.get("micro_concepts", []) or []
                )
                _NOMS_CHAPITRES[chapter_id] = {
                    "fr": chapitre.get("nom_fr", chapter_id),
                    "ar": chapitre.get("nom_ar", chapter_id),
                }
                for alias in (
                    chapter_id,
                    chapitre.get("nom_fr", ""),
                    chapitre.get("nom_ar", ""),
                ):
                    key = _norm(alias)
                    if key:
                        _ALIASES.setdefault(key, chapter_id)
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("Programme canonique illisible pour la boussole : %s", exc)


def _load_concepts_par_chapitre() -> dict[str, int]:
    _load_programme()
    return _CONCEPTS_PAR_CHAPITRE


def _chapter_to_id(chapter: str) -> str | None:
    """Résout un slug, un titre français ou arabe vers l'id canonique."""
    _load_programme()
    key = _norm(chapter)
    return _ALIASES.get(key) if key else None


def _chapter_mastery(
    chapter_id: str,
    stability_by_chapter: dict[str, float],
    concepts_by_chapter: dict[str, int],
) -> int:
    concept_count = concepts_by_chapter.get(chapter_id, 0)
    if concept_count <= 0:
        return 0
    maximum = STABILITY_MAX * concept_count
    stability = min(stability_by_chapter.get(chapter_id, 0.0), maximum)
    return round(100.0 * stability / maximum)


async def calculer_roadmap(db: AsyncSession, user_id) -> dict[str, Any]:
    """Calcule les cinq unités, l'objectif courant et le message du coach."""
    concepts_by_chapter = _load_concepts_par_chapitre()
    memory_items = await get_user_memory(db, user_id, kinds=("concept",))

    stability_by_chapter: dict[str, float] = {}
    for item in memory_items:
        chapter_id = _chapter_to_id(item.chapter or "")
        if chapter_id is None:
            continue
        stability_by_chapter[chapter_id] = (
            stability_by_chapter.get(chapter_id, 0.0)
            + min(max(float(item.stability or 0.0), 0.0), STABILITY_MAX)
        )

    unites: list[dict[str, Any]] = []
    prerequisites_done = True
    active_assigned = False

    for unit in PARCOURS:
        concept_count = sum(
            concepts_by_chapter.get(chapter_id, 0)
            for chapter_id in unit["chapitres"]
        )
        if concept_count <= 0:
            concept_count = max(len(unit["chapitres"]), 1)

        maximum = STABILITY_MAX * concept_count
        stability = min(
            sum(
                stability_by_chapter.get(chapter_id, 0.0)
                for chapter_id in unit["chapitres"]
            ),
            maximum,
        )
        mastery = round(100.0 * stability / maximum)

        chapters = [
            {
                "id": chapter_id,
                "maitrise": _chapter_mastery(
                    chapter_id,
                    stability_by_chapter,
                    concepts_by_chapter,
                ),
            }
            for chapter_id in unit["chapitres"]
        ]

        if not prerequisites_done:
            status = "locked"
            locked_by = PARCOURS[unit["num"] - 2]["id"]
        elif mastery >= SEUIL_DONE:
            status = "done"
            locked_by = None
        else:
            status = "active" if not active_assigned else "locked"
            locked_by = None if status == "active" else PARCOURS[unit["num"] - 2]["id"]
            active_assigned = True
            prerequisites_done = False

        unites.append(
            {
                "id": unit["id"],
                "num": unit["num"],
                "titre_fr": unit["titre_fr"],
                "titre_ar": unit["titre_ar"],
                "emoji": unit["emoji"],
                "objectif_fr": unit["objectif_fr"],
                "objectif_ar": unit["objectif_ar"],
                "chapitres": chapters,
                "nb_concepts": concept_count,
                "maitrise": mastery,
                "statut": status,
                "verrouille_par": locked_by,
            }
        )

    active_unit = next(
        (unit for unit in unites if unit["statut"] == "active"),
        None,
    )
    all_done = all(unit["statut"] == "done" for unit in unites)

    weakest_chapter = None
    if active_unit:
        weakest = min(
            active_unit["chapitres"],
            key=lambda chapter: chapter["maitrise"],
            default=None,
        )
        if weakest:
            names = _NOMS_CHAPITRES.get(
                weakest["id"],
                {"fr": weakest["id"], "ar": weakest["id"]},
            )
            lesson_slug = _LESSON_SLUG_BY_CHAPTER.get(weakest["id"])
            weakest_chapter = {
                "id": weakest["id"],
                "nom_fr": names["fr"],
                "nom_ar": names["ar"],
                "maitrise": weakest["maitrise"],
                "href": (
                    f"/lecons-sciences-experimentales/{lesson_slug}"
                    if lesson_slug
                    else "/lecons-sciences-experimentales"
                ),
            }

    coach = _message_coach(active_unit, all_done)
    objective_href = (
        weakest_chapter["href"]
        if weakest_chapter
        else "/annales"
        if all_done
        else "/lecons-sciences-experimentales"
    )

    return {
        "unites": unites,
        "unite_active": active_unit["id"] if active_unit else None,
        "prochain_objectif": {
            "unite_id": active_unit["id"] if active_unit else None,
            "num": active_unit["num"] if active_unit else None,
            "titre_fr": (
                active_unit["titre_fr"] if active_unit else "Programme terminé"
            ),
            "titre_ar": (
                active_unit["titre_ar"] if active_unit else "اكتمل البرنامج"
            ),
            "chapitre_faible": weakest_chapter,
            "href": objective_href,
        },
        "coach": coach,
        "seuils": {"done": SEUIL_DONE, "stability_max": STABILITY_MAX},
    }


def _message_coach(
    active_unit: dict[str, Any] | None,
    all_done: bool,
) -> dict[str, str]:
    """Produit le message bilingue correspondant à l'avancement réel."""
    if all_done:
        return {
            "fr": (
                "Félicitations ! Tu maîtrises les 5 unités du programme. "
                "Passe aux annales du BAC et garde tes révisions FSRS à jour."
            ),
            "ar": (
                "مبروك! لقد أتقنت الوحدات الخمس كلها. انتقل إلى مواضيع "
                "البكالوريا وواصل مراجعاتك لتبقى المعلومات راسخة."
            ),
            "tone": "success",
        }

    if active_unit is None:
        return {
            "fr": "Commence par l'unité 1.",
            "ar": "ابدأ بالوحدة 1.",
            "tone": "info",
        }

    mastery = active_unit["maitrise"]
    number = active_unit["num"]
    if mastery == 0:
        return {
            "fr": (
                f"🎯 Objectif : maîtrise d'abord l'unité {number} — "
                f"{active_unit['titre_fr']}. Travaille ses leçons et ses "
                "flashcards avant de passer à la suite."
            ),
            "ar": (
                f"🎯 الهدف: أتقن أولاً الوحدة {number}: "
                f"{active_unit['titre_ar']}. اعمل على دروس وبطاقات هذه الوحدة "
                "قبل الانتقال إلى ما بعدها."
            ),
            "tone": "focus",
        }

    return {
        "fr": (
            f"Tu progresses sur l'unité {number} ({mastery} %). Renforce le "
            "chapitre le plus faible, puis atteins 80 % pour débloquer la suite."
        ),
        "ar": (
            f"أنت تتقدم في الوحدة {number} ({mastery} %). واصل تقوية أضعف فصل، "
            "ثم بلغ 80٪ لفتح الوحدة الموالية."
        ),
        "tone": "progress",
    }
