"""services/orientation_roadmap.py — La BOUSSOLE : parcours unité par unité.

Répond au besoin : « l'élève n'a pas de boussole, il est désorienté ».
Transforme le programme SVT Bac Algérie (3AS) en un parcours ORDONNÉ de
5 unités, calcule la maîtrise réelle de l'élève par unité (depuis la
mémoire FSRS unifiée) et détermine :

  - le statut de chaque unité : done / active / locked
    (l'unité N ne se déverrouille que si l'unité N-1 est maîtrisée) ;
  - l'objectif courant : « maîtrise d'abord l'unité N » + le chapitre le
    plus faible de cette unité ;
  - le message du coach (FR + AR) qui guide phase par phase.

0 appel IA. 100 % depuis la vue consolidée FSRS (get_user_memory).
Latence < 50 ms.

Seuils (constants — calibrés sur le seuil "mastered" existant du FSRS :
stability > 10.0) :
  - MAITRISE_UNITE = 100 × Σ min(stability_i, 10) / (10 × nb_concepts_unité)
    → 100 % = tous les concepts de l'unité à stabilité ≥ 10.
  - SEUIL_DONE = 80 % : unité considérée acquise.
  - SEUIL_DEVERROUILLAGE = 80 % : l'unité suivante ne se débloque que si la
    précédente est done (cohérence : maîtrise d'abord l'unité 1).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from services.fsrs_unified import get_user_memory

logger = logging.getLogger("khawarizmi.orientation_roadmap")

# ── Parcours officiel (ordre d'apprentissage recommandé Bac SVT 3AS) ─

PARCOURS: list[dict[str, Any]] = [
    {
        "id": "u1",
        "num": 1,
        "titre_fr": "Consommation de la matière organique et flux d'énergie",
        "titre_ar": "استهلاك المادة العضوية وتدفق الطاقة",
        "emoji": "⚡",
        "objectif_fr": "Respiration, fermentation, photosynthèse : comment la matière organique libère et stocke l'énergie.",
        "objectif_ar": "التنفس والتخمر والتركيب الضوئي: كيف تحرر المادة العضوية الطاقة وتخزنها",
        "chapitres": ["ch_respiration", "ch_photosynthese", "ch_bilan_energetique"],
        "lecon_slug": "phase_respiration_photosynthese",
    },
    {
        "id": "u2",
        "num": 2,
        "titre_fr": "Spécialisation fonctionnelle des protéines",
        "titre_ar": "التخصص الوظيفي للبروتينات",
        "emoji": "🧬",
        "objectif_fr": "Synthèse des protéines, structure et fonction, activité enzymatique : le lien gène → protéine → fonction.",
        "objectif_ar": "تركيب البروتينات وبنيتها ووظيفتها والنشاط الإنزيمي: العلاقة بين الجين والبروتين والوظيفة",
        "chapitres": ["ch1_proteines", "ch_structure_proteines", "ch2_enzymes"],
        "lecon_slug": "phase_synthese_proteines",
    },
    {
        "id": "u3",
        "num": 3,
        "titre_fr": "La communication nerveuse",
        "titre_ar": "التواصل العصبي",
        "emoji": "🧠",
        "objectif_fr": "Neurone, message nerveux, synapse : comment l'information circule dans le système nerveux.",
        "objectif_ar": "العصبون والرسالة العصبية والمشبك: كيف تنتقل المعلومة في الجهاز العصبي",
        "chapitres": ["ch4_nerveux"],
        "lecon_slug": "phase_communication_nerveuse",
    },
    {
        "id": "u4",
        "num": 4,
        "titre_fr": "L'immunité",
        "titre_ar": "المناعة",
        "emoji": "🛡️",
        "objectif_fr": "Réactions immunitaires innées et adaptatives : comment l'organisme se défend.",
        "objectif_ar": "الاستجابات المناعية الفطرية والتكيفية: كيف يدافع الجسم عن نفسه",
        "chapitres": ["ch3_immunite"],
        "lecon_slug": "phase_immunite",
    },
    {
        "id": "u5",
        "num": 5,
        "titre_fr": "Tectonique globale (Géologie)",
        "titre_ar": "التكتونية العامة (جيولوجيا)",
        "emoji": "🌍",
        "objectif_fr": "Plaques, structure du globe, structures associées : la dynamique de la lithosphère.",
        "objectif_ar": "الصفائح وبنية الكرة الأرضية والتراكيب المرافقة: ديناميكية الغلاف الصخري",
        "chapitres": ["ch_tectonique_plaques", "ch_structure_terre", "ch_banies_geologiques"],
        "lecon_slug": "phase_tectonique",
    },
]

# ── Seuils ───────────────────────────────────────────────────────────

SEUIL_DONE = 80.0          # % de maîtrise pour considérer une unité acquise
STABILITY_MAX = 10.0       # stabilité "maîtrisé" (cohérent avec le FSRS existant)

# ── Chargement du programme (nb de concepts par chapitre) ────────────

_PROGRAMME_PATH = Path(__file__).parent.parent / "data" / "official" / "programme_svt_3as_canonical.json"

_CONCEPTS_PAR_CHAPITRE: dict[str, int] = {}
_NOMS_CHAPITRES: dict[str, dict[str, str]] = {}


def _load_programme() -> None:
    global _CONCEPTS_PAR_CHAPITRE, _NOMS_CHAPITRES
    if _CONCEPTS_PAR_CHAPITRE:
        return
    try:
        data = json.loads(_PROGRAMME_PATH.read_text(encoding="utf-8"))
        for domaine in data.get("domaines", []):
            for ch in domaine.get("chapitres", []):
                _CONCEPTS_PAR_CHAPITRE[ch["id"]] = len(ch.get("micro_concepts", []) or [])
                _NOMS_CHAPITRES[ch["id"]] = {
                    "fr": ch.get("nom_fr", ch["id"]),
                    "ar": ch.get("nom_ar", ch["id"]),
                }
    except Exception as e:  # pragma: no cover — fichier toujours présent
        logger.warning(f"orientation_roadmap: programme illisible ({e})")


def _load_concepts_par_chapitre() -> dict[str, int]:
    _load_programme()
    return _CONCEPTS_PAR_CHAPITRE


# ── Normalisation des chapitres (slugs / nom_fr / nom_ar → id) ───────

_ALIASES: dict[str, str] = {}


def _build_aliases() -> dict[str, str]:
    global _ALIASES
    if _ALIASES:
        return _ALIASES
    try:
        data = json.loads(_PROGRAMME_PATH.read_text(encoding="utf-8"))
        for domaine in data.get("domaines", []):
            for ch in domaine.get("chapitres", []):
                cid = ch["id"]
                for alias in (cid, ch.get("nom_fr", ""), ch.get("nom_ar", "")):
                    key = _norm(alias)
                    if key and key not in _ALIASES:
                        _ALIASES[key] = cid
    except Exception as e:  # pragma: no cover
        logger.warning(f"orientation_roadmap: alias illisible ({e})")
    return _ALIASES


def _norm(value: str) -> str:
    """Normalisation tolérante (minuscules, sans accents ni espaces)."""
    import re
    import unicodedata

    s = unicodedata.normalize("NFKD", value or "").lower()
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9\u0600-\u06ff]", "", s)
    return s


def _chapter_to_id(chapter: str) -> str | None:
    """Mappe une valeur de champ chapter (DB) vers l'id du programme."""
    key = _norm(chapter)
    if not key:
        return None
    return _build_aliases().get(key)


# ── Calcul principal ─────────────────────────────────────────────────

async def calculer_roadmap(db: AsyncSession, user_id) -> dict[str, Any]:
    """Calcule le parcours boussole complet de l'élève."""
    concepts_par_chapitre = _load_concepts_par_chapitre()

    # Mémoire FSRS : concepts en cours (toutes sources, vue consolidée)
    items = await get_user_memory(db, user_id, kinds=("concept",))
    stability_par_chapitre: dict[str, float] = {}
    for item in items:
        cid = _chapter_to_id(item.chapter or "")
        if cid is None:
            continue
        stability_par_chapitre[cid] = stability_par_chapitre.get(cid, 0.0) + min(
            item.stability, STABILITY_MAX
        )

    unites: list[dict[str, Any]] = []
    premiere_non_done: str | None = None
    tout_done = True

    for u in PARCOURS:
        nb_total = sum(concepts_par_chapitre.get(c, 0) for c in u["chapitres"])
        if nb_total == 0:  # chapitre inconnu du programme → ne pas bloquer
            nb_total = max(len(u["chapitres"]), 1)
        somme = sum(stability_par_chapitre.get(c, 0.0) for c in u["chapitres"])
        maitrise = round(100.0 * min(somme, STABILITY_MAX * nb_total) / (STABILITY_MAX * nb_total))

        # Détail par chapitre (le plus faible = prochaine action)
        chapitres_detail = []
        for c in u["chapitres"]:
            n = concepts_par_chapitre.get(c, 0)
            m = 100.0 * min(stability_par_chapitre.get(c, 0.0), STABILITY_MAX * n) / (STABILITY_MAX * n) if n else 0.0
            chapitres_detail.append({
                "id": c,
                "maitrise": round(m),
            })

        statut = "done" if maitrise >= SEUIL_DONE else "active"
        if statut != "done" and premiere_non_done is None:
            premiere_non_done = u["id"]
        if statut != "done":
            tout_done = False

        unites.append({
            "id": u["id"],
            "num": u["num"],
            "titre_fr": u["titre_fr"],
            "titre_ar": u["titre_ar"],
            "emoji": u["emoji"],
            "objectif_fr": u["objectif_fr"],
            "objectif_ar": u["objectif_ar"],
            "chapitres": chapitres_detail,
            "nb_concepts": nb_total,
            "maitrise": maitrise,
            "statut": statut,
            "verrouille_par": None,
        })

    # Verrouillage : unité N locked si N-1 pas done (séquentiel strict)
    for i in range(1, len(unites)):
        if unites[i]["statut"] == "active" and unites[i - 1]["statut"] != "done":
            unites[i]["statut"] = "locked"
            unites[i]["verrouille_par"] = unites[i - 1]["id"]
            if premiere_non_done == unites[i]["id"]:
                premiere_non_done = unites[i - 1]["id"]

    # Unité courante = première non-done (la boussole pointe dessus)
    unite_active = next((u for u in unites if u["id"] == premiere_non_done), None)
    if unite_active is None and not tout_done:
        unite_active = next((u for u in unites if u["statut"] == "active"), None)

    # Chapitre le plus faible de l'unité courante
    chapitre_faible = None
    if unite_active:
        faible = min(unite_active["chapitres"], key=lambda c: c["maitrise"], default=None)
        if faible is not None:
            _load_programme()
            noms = _NOMS_CHAPITRES.get(faible["id"], {"fr": faible["id"], "ar": faible["id"]})
            chapitre_faible = {
                "id": faible["id"],
                "nom_fr": noms["fr"],
                "nom_ar": noms["ar"],
                "maitrise": faible["maitrise"],
                "href": f"/lecons-sciences-experimentales/{unite_active.get('lecon_slug') or ''}",
            }

    coach = _message_coach(unites, unite_active, tout_done)

    return {
        "unites": unites,
        "unite_active": unite_active["id"] if unite_active else None,
        "prochain_objectif": {
            "unite_id": unite_active["id"] if unite_active else None,
            "num": unite_active["num"] if unite_active else None,
            "titre_fr": unite_active["titre_fr"] if unite_active else "Programme terminé",
            "titre_ar": unite_active["titre_ar"] if unite_active else "اكتمل البرنامج",
            "chapitre_faible": chapitre_faible,
            "href": chapitre_faible["href"] if chapitre_faible else (
                "/lecons-sciences-experimentales" if not tout_done else "/annales"),
        },
        "coach": coach,
        "seuils": {"done": SEUIL_DONE, "stability_max": STABILITY_MAX},
    }


def _message_coach(
    unites: list[dict[str, Any]],
    unite_active: dict[str, Any] | None,
    tout_done: bool,
) -> dict[str, str]:
    """Message du coach (FR/AR) selon l'avancement — ton professeur."""
    if tout_done:
        return {
            "fr": "Félicitations ! Tu maîtrises les 5 unités du programme. "
                  "Passe aux annales du BAC et aux révisions ciblées — garde tes révisions FSRS à jour.",
            "ar": "مبروك! لقد أتقنت الوحدات الخمس كلها. انتقل إلى مواضيع البكالوريا والمراجعة الموجهة، "
                  "وواصل مراجعاتك لتبقى المعلومات راسخة.",
            "tone": "success",
        }
    if unite_active is None:
        unite_active = next((u for u in unites if u["statut"] == "active"), None)
    if unite_active is None:
        return {"fr": "Commence par l'unité 1.", "ar": "ابدأ بالوحدة 1.", "tone": "info"}

    m = unite_active["maitrise"]
    num = unite_active["num"]
    titre_ar = unite_active["titre_ar"]
    if m == 0:
        return {
            "fr": f"🎯 Objectif : maîtrise d'abord l'unité {num} — {unite_active['titre_fr']}. "
                  "Travaille les leçons et les flashcards de cette unité avant de passer à la suite.",
            "ar": f"🎯 الهدف: أتقن أولاً الوحدة {num}: {titre_ar}. "
                  "اعمل على دروس وبطاقات هذه الوحدة قبل الانتقال إلى ما بعدها.",
            "tone": "focus",
        }
    if m < SEUIL_DONE:
        return {
            "fr": f"Tu progresses sur l'unité {num} ({m} %). Continue : renforce le chapitre "
                  "le plus faible, puis valide l'unité pour débloquer la suivante.",
            "ar": f"أنت تتقدم في الوحدة {num} ({m} %). واصل تقوية أضعف فصل، ثم أتقن الوحدة "
                  "لفتح الوحدة الموالية.",
            "tone": "progress",
        }
    return {
        "fr": f"L'unité {num} est maîtrisée ✅ — passe à l'unité suivante.",
        "ar": f"الوحدة {num} متقنة ✅ — انتقل إلى الوحدة الموالية.",
        "tone": "success",
    }
