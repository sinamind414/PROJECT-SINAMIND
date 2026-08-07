"""routes/aujourdhui.py — Endpoint "Aujourd'hui" (mission du jour 10 min).

GET  /api/aujourdhui           → mission du jour + progression
GET  /api/aujourdhui/matrix    → thermomètre 57 MC vert/rouge
GET  /api/aujourdhui/fiche-j1  → fiche J-1 imprimable
POST /api/aujourdhui/valider   → valide la réponse QCM et marque MC comme maîtrisé

100% déterministe, 0 LLM, 0 appel externe.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from deps import get_current_user

router = APIRouter(prefix="/api/aujourdhui", tags=["Aujourd'hui"])

# ── Stockage persistant local des MC maîtrisés (fichier JSON par user) ──
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


# ── Import tardif du service ──
def _mission(user_id: str, mastered: set[str]):
    from services.aujourdhui import get_mission_du_jour
    return get_mission_du_jour(user_id, mastered)


# ── Endpoints ──

@router.get("")
async def aujourdhui(user=Depends(get_current_user)):
    """Mission du jour — 1 concept, 10 minutes, pas de choix à faire."""
    user_id = str(user.get("id", "guest"))
    mastered = _load_mastered(user_id)
    result = _mission(user_id, mastered)
    return result


@router.get("/matrix")
async def matrix(user=Depends(get_current_user)):
    """Matrice 57 MC vert/rouge (thermomètre de maîtrise)."""
    from services.aujourdhui import get_matrix
    user_id = str(user.get("id", "guest"))
    mastered = _load_mastered(user_id)
    return get_matrix(mastered)


@router.get("/fiche-j1")
async def fiche_j1(user=Depends(get_current_user)):
    """Fiche J-1 imprimable (1 page A4, 12 phrases clés + 10 erreurs graves)."""
    from services.aujourdhui import get_fiche_j1
    return get_fiche_j1()


class ValiderBody(BaseModel):
    mc_id: str
    answer_index: int


class DixMinutesReponse(BaseModel):
    mc_id: str
    answer_index: int


class DixMinutesBody(BaseModel):
    reponses: list[DixMinutesReponse]


@router.post("/valider")
async def valider(body: ValiderBody, user=Depends(get_current_user)):
    """Valide la réponse QCM du jour. Si juste, marque MC comme vert."""
    from services.aujourdhui import _build_qcm, _load
    user_id = str(user.get("id", "guest"))

    data = _load()
    mc = None
    for m in data["micro_concepts"]:
        if m["id"] == body.mc_id:
            mc = m
            break
    if not mc:
        raise HTTPException(404, "MC introuvable")

    qcm = _build_qcm(mc, data["micro_concepts"])
    correct = body.answer_index == qcm["correct_index"]

    mastered = _load_mastered(user_id)
    if correct:
        mastered.add(body.mc_id)
        _save_mastered(user_id, mastered)
    # Si mauvais, on garde le MC dans la mission de demain

    # Prochaine mission (pour le "continue" bouton)
    from services.aujourdhui import get_mission_du_jour
    next_mission = get_mission_du_jour(user_id, mastered)

    return {
        "correct": correct,
        "explanation": qcm["explanation"],
        "conseil": qcm["conseil"],
        "bonne_reponse_index": qcm["correct_index"],
        "progression": {
            "mc_maitrise": len(mastered),
            "mc_total": len(data["micro_concepts"]),
            "pourcentage": round(len(mastered) / len(data["micro_concepts"]) * 100),
        },
        "next_mission_id": next_mission["mission"]["id"],
        "next_mission_titre": next_mission["mission"]["titre"],
        "next_mission_is_revision": next_mission["is_revision"],
    }


@router.get("/dix-minutes")
async def dix_minutes(user=Depends(get_current_user)):
    """Session 10 minutes : 5 QCM de suite sur les MC non maîtrisés."""
    from services.dix_minutes import get_session_dix_minutes
    user_id = str(user.get("id", "guest"))
    return get_session_dix_minutes(user_id)


@router.post("/dix-minutes")
async def corriger_dix_minutes(body: DixMinutesBody, user=Depends(get_current_user)):
    """Corrige une session 10 minutes (5 réponses)."""
    from services.dix_minutes import corriger_session_dix_minutes
    user_id = str(user.get("id", "guest"))
    reponses = [{"mc_id": r.mc_id, "answer_index": r.answer_index} for r in body.reponses]
    return corriger_session_dix_minutes(user_id, reponses)


@router.post("/reset")
async def reset_progress(user=Depends(get_current_user)):
    """Remet la progression à zéro (pour debug/test)."""
    user_id = str(user.get("id", "guest"))
    _save_mastered(user_id, set())
    return {"status": "ok", "message": "Progression réinitialisée."}
