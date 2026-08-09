"""tests/golden/scoring.py — Scores SYSTÈME des moteurs locaux (golden).

Helpers partagés entre test_golden_local.py (CI) et
scripts/golden_human_report.py (rapport de qualité post-annotation).
Reproduisent EXACTEMENT la logique de prod (0 token, 0 clé) :
- L2 : evaluate_l2 (fallback_v2) avec redistribution des poids quand
  l'embedder sémantique est en fallback (CI sans ONNX) ;
- savoir : deterministic_correct_v2 (chemin prod réel, concepts déduits de
  la RÉPONSE MODÈLE) ;
- dominant_error : dérivé du score (all_correct / partial_correct /
  insufficient) pour L2.
"""

from __future__ import annotations

from services.embedder import get_embedder
from services.fallback_v2 import evaluate_l2
from services.savoir_corrector import deterministic_correct_v2


def dominant_from_score(score: float, score_max: float) -> str:
    if score >= score_max:
        return "all_correct"
    if score > 0:
        return "partial_correct"
    return "insufficient"


async def l2_score(item: dict) -> tuple[int, str]:
    """Score L2 normalisé — même logique que la prod
    (correction_v2._evaluate_local_fallback) : redistribution des poids
    quand l'embedder sémantique est en fallback (CI sans ONNX)."""
    question_data = {
        "reponse_attendue": item["reponse_attendue"],
        "concepts_requis": item["mots_cles_attendus"],
        "points_cles": [item["reponse_attendue"]],
        "question_id": None,
    }
    res = await evaluate_l2(
        reponse_eleve=item["student_answer"],
        question_data=question_data,
        db=None,
    )
    final = res.score_final
    try:
        if bool(getattr(get_embedder(), "is_fallback", False)):
            w_t, w_r = 0.25, 0.35
            final = (w_t * res.coverage_score + w_r * res.structural_score) / (w_t + w_r)
            final = max(0.0, min(1.0, final))
    except Exception:
        pass
    score = round(final * item["bareme"])
    return score, dominant_from_score(score, item["bareme"])


def savoir_result(item: dict) -> dict:
    """Score savoir — CHEMIN PROD RÉEL : deterministic_correct_v2 avec
    déduction des concepts depuis la RÉPONSE MODÈLE (pas les mots-clés du
    golden, qui ne sont pas dans da_questions)."""
    return deterministic_correct_v2(
        question=item["question"],
        student_answer=item["student_answer"],
        score_max=item["bareme"],
        language="ar",
        model_answer=item["reponse_attendue"],
    )
