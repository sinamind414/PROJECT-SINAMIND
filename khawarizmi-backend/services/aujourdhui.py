"""services/aujourdhui.py — Mission du jour (10 minutes) pour l'élève bac.

Sélectionne UN SEUL micro-concept à réviser aujourd'hui en se basant sur :
  • l'ordre du programme (déverrouillage progressif)
  • les erreurs passées de l'élève
  • un algo déterministe reproductible par jour (pas d'aléatoire angoissant)

Retourne la structure "carte concept" (phrase clé, erreur fréquente, mnémo)
+ une QCM rapide pour valider la maîtrise.

ZÉRO LLM. 100% déterministe.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
_ESSENTIALS_FILE = _ROOT / "data" / "essential" / "bac_essentials.json"

_cache: dict[str, Any] | None = None


def _load() -> dict[str, Any]:
    global _cache
    if _cache is None:
        with open(_ESSENTIALS_FILE, encoding="utf-8") as f:
            _cache = json.load(f)
    return _cache


def _seed_for_today(user_id: str) -> int:
    """Graine déterministe par utilisateur × par jour."""
    today = date.today().isoformat()
    h = hashlib.sha256(f"{user_id}:{today}".encode()).hexdigest()
    return int(h[:8], 16)


def get_mission_du_jour(user_id: str, mastered: set[str] | None = None) -> dict[str, Any]:
    """Retourne la mission d'aujourd'hui (1 MC) + les métriques globales."""
    data = _load()
    mcs = data["micro_concepts"]
    unites = {u["unit_id"]: u for u in data["unites"]}
    mastered = mastered or set()

    # Trouver le PREMIER MC non maîtrisé dans l'ordre du programme (progression linéaire).
    # Si tous sont maîtrisés → prendre un MC de révision (celui du jour).
    next_mc = None
    for mc in mcs:
        if mc["id"] not in mastered:
            next_mc = mc
            break
    if next_mc is None:
        # Tous maîtrisés → révision du jour (selon graine)
        seed = _seed_for_today(user_id)
        next_mc = mcs[seed % len(mcs)]
        is_revision = True
    else:
        is_revision = False

    # MCs maîtrisés, MCs restants
    nb_mc = len(mcs)
    nb_maitrise = sum(1 for mc in mcs if mc["id"] in mastered)
    pct = round(nb_maitrise / nb_mc * 100)

    # Unité en cours
    current_unit = unites.get(next_mc["unit_id"], {})
    unit_position = next(
        (i for i, mc in enumerate(mcs) if mc["unit_id"] == next_mc["unit_id"]), 0
    ) + 1
    unit_total = current_unit.get("mc_count", 0)
    unit_done = sum(1 for mc in mcs if mc["unit_id"] == next_mc["unit_id"] and mc["id"] in mastered)

    # Construire la question QCM rapide
    qcm = _build_qcm(next_mc, mcs)

    return {
        "date": date.today().isoformat(),
        "is_revision": is_revision,
        "mission": {
            "type": "carte_concept",
            "id": next_mc["id"],
            "titre": next_mc["titre"],
            "phrase_cle": next_mc["phrase_cle"],
            "erreur_frequente": next_mc["erreur_frequente"],
            "mnemo": next_mc["mnemo"],
            "points_bac": next_mc.get("points_bac", 0.5),
            "niveau": next_mc.get("niveau", "moyen"),
            "unite": {
                "titre_fr": current_unit.get("titre_fr", ""),
                "titre_ar": current_unit.get("titre_ar", ""),
                "position": current_unit.get("position", 0),
                "mc_progress": unit_done,
                "mc_total": unit_total,
            },
            "duree_estimee_minutes": 10,
        },
        "quiz": qcm,
        "progress": {
            "mc_total": nb_mc,
            "mc_maitrise": nb_maitrise,
            "mc_restants": nb_mc - nb_maitrise,
            "pourcentage": pct,
            "unites": [
                {
                    "unit_id": u["unit_id"],
                    "titre_ar": u["titre_ar"],
                    "position": u["position"],
                    "mc_total": u["mc_count"],
                    "mc_maitrise": sum(
                        1 for mc in mcs if mc["unit_id"] == u["unit_id"] and mc["id"] in mastered
                    ),
                }
                for u in sorted(data["unites"], key=lambda x: x["position"])
            ],
        },
        "phrases_bac_clefs": data["phrases_bac_clefs"][:3],
        "erreurs_graves": data["erreurs_graves"][:3],
    }


def get_matrix(mastered: set[str] | None = None) -> dict[str, Any]:
    """Retourne la matrice thermomètre 57 MC (vert/jaune/rouge)."""
    data = _load()
    mastered = mastered or set()
    return {
        "total": len(data["micro_concepts"]),
        "unites": [
            {
                "unit_id": u["unit_id"],
                "titre_ar": u["titre_ar"],
                "titre_fr": u["titre_fr"],
                "position": u["position"],
                "mc_count": u["mc_count"],
                "items": [
                    {
                        "id": mc["id"],
                        "titre": mc["titre"],
                        "etat": "vert" if mc["id"] in mastered else "rouge",
                    }
                    for mc in data["micro_concepts"]
                    if mc["unit_id"] == u["unit_id"]
                ],
            }
            for u in sorted(data["unites"], key=lambda x: x["position"])
        ],
    }


def get_carte_concept(mc_id: str) -> dict[str, Any] | None:
    data = _load()
    for mc in data["micro_concepts"]:
        if mc["id"] == mc_id:
            return mc
    return None


def get_fiche_j1() -> dict[str, Any]:
    """Fiche J-1 (page A4 imprimable) : phrases clés + erreurs graves."""
    data = _load()
    return {
        "titre": "ورقة المراجعة النهائية — قبل الباك بيوم",
        "phrases_bac_clefs": data["phrases_bac_clefs"],
        "erreurs_graves": data["erreurs_graves"],
        "total_phrases": len(data["phrases_bac_clefs"]),
        "total_erreurs": len(data["erreurs_graves"]),
    }


# ── QCM builder ────────────────────────────────────────────

_QCM_QUESTIONS = {
    "mc044": ("ما هي الحصيلة الصحيحة لـ ATP في التنفس الهوائي؟", "38 ATP", ["38 ATP", "36 ATP", "32 ATP", "2 ATP"]),
    "mc001": "أين تتم ترجمة المعلومة الوراثية؟",
}
# QCM generic builder : la question est toujours "quelle est la bonne phrase clé ?",
# distracteurs = erreurs fréquentes d'autres MCs du même chapitre.


def _build_qcm(mc: dict, all_mcs: list[dict]) -> dict[str, Any]:
    correct = mc["phrase_cle"]
    titre = mc["titre"]
    question = f"أي من الجمل التالية صحيحة بخصوص {titre}؟"

    # Distracteurs = erreur fréquente de ce MC + 2 erreurs fréquentes d'autres MCs
    distracteurs = [mc["erreur_frequente"].split(" — خطأ")[0] if " — خطأ" in mc["erreur_frequente"] else mc["erreur_frequente"]]
    same_unit = [m for m in all_mcs if m["unit_id"] == mc["unit_id"] and m["id"] != mc["id"]]
    # 2 autres erreurs de la même unité
    import random as _r
    _r.seed(hash(mc["id"]) & 0xFFFF)
    others = _r.sample(same_unit, k=min(2, len(same_unit)))
    for o in others:
        err = o["erreur_frequente"]
        if " — خطأ" in err:
            err = err.split(" — خطأ")[0]
        # Extraire la phrase d'erreur
        distracteurs.append(err)

    choices = [correct] + distracteurs
    _r.shuffle(choices)
    correct_idx = choices.index(correct)

    return {
        "question": question,
        "choices": choices,
        "correct_index": correct_idx,
        "explanation": mc["phrase_cle"],
        "conseil": mc["mnemo"],
    }
