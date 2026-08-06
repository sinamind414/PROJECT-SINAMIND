"""services/dix_minutes.py — Mode 10 minutes : 5 MCs enchaînés, 0 LLM, 100% déterministe."""
from __future__ import annotations

import random as _r
from typing import Any

from services.aujourdhui import _load, _build_qcm
from pathlib import Path
from datetime import date
import json

_MASTERY_DIR = Path(__file__).resolve().parent.parent / "data" / "mastery"
_MASTERY_DIR.mkdir(parents=True, exist_ok=True)


def _mastery_file(user_id: str) -> Path:
    return _MASTERY_DIR / f"{user_id}.json"


def _load_mastered(user_id: str) -> set[str]:
    p = _mastery_file(user_id)
    if not p.exists():
        return set()
    try:
        return set(json.loads(p.read_text(encoding="utf-8")).get("mastered", []))
    except Exception:
        return set()


def _save_mastered(user_id: str, mastered: set[str]) -> None:
    p = _mastery_file(user_id)
    p.write_text(json.dumps({
        "user_id": user_id,
        "mastered": sorted(mastered),
        "updated_at": date.today().isoformat(),
    }, ensure_ascii=False, indent=2), encoding="utf-8")


def get_session_dix_minutes(user_id: str, mastered: set[str] | None = None) -> dict[str, Any]:
    """Retourne une session de 5 questions (QCM) sur les MC non maîtrisés, dans l'ordre du programme."""
    data = _load()
    mcs = data["micro_concepts"]
    mastered = mastered or _load_mastered(user_id)

    # Prendre jusqu'à 5 MC non maîtrisés, dans l'ordre du programme
    restants = [mc for mc in mcs if mc["id"] not in mastered][:5]
    if not restants:
        # Tous maîtrisés → session de révision
        _r.seed(hash(user_id) & 0xFFFF)
        restants = _r.sample(mcs, k=5)

    questions = []
    for mc in restants:
        q = _build_qcm(mc, mcs)
        questions.append({
            "mc_id": mc["id"],
            "titre": mc["titre"],
            "question": q["question"],
            "choices": q["choices"],
            "correct_index": q["correct_index"],
        })

    return {
        "session_id": f"dix_{user_id}",
        "nombre_questions": len(questions),
        "duree_estimee_minutes": 10,
        "questions": questions,
        "progression_actuelle": {
            "mc_maitrise": len(mastered),
            "mc_total": len(mcs),
        },
    }


def corriger_session_dix_minutes(user_id: str, reponses: list[dict[str, int]]) -> dict[str, Any]:
    """Corrige une session 10 minutes et marque les MC justes comme maîtrisés."""
    data = _load()
    mcs = data["micro_concepts"]
    mcs_by_id = {mc["id"]: mc for mc in mcs}
    mastered = _load_mastered(user_id)

    resultats = []
    nb_correct = 0
    for rep in reponses:
        mc_id = rep.get("mc_id", "")
        given = rep.get("answer_index", -1)
        mc = mcs_by_id.get(mc_id)
        if not mc:
            resultats.append({"mc_id": mc_id, "correct": False, "erreur": "MC introuvable"})
            continue
        q = _build_qcm(mc, mcs)
        ok = given == q["correct_index"]
        resultats.append({
            "mc_id": mc_id,
            "titre": mc["titre"],
            "correct": ok,
            "bonne_reponse_index": q["correct_index"],
            "phrase_cle": mc["phrase_cle"] if ok else q["explanation"],
            "conseil": q["conseil"],
        })
        if ok:
            nb_correct += 1
            mastered.add(mc_id)

    _save_mastered(user_id, mastered)

    return {
        "note": f"{nb_correct}/{len(reponses)}",
        "nb_correct": nb_correct,
        "nb_total": len(reponses),
        "pourcentage": round(nb_correct / max(1, len(reponses)) * 100),
        "resultats": resultats,
        "progression": {
            "mc_maitrise": len(mastered),
            "mc_total": len(mcs),
            "pourcentage": round(len(mastered) / len(mcs) * 100),
        },
    }
