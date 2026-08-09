"""grading/mapping.py — Mapping v2 → v1 (audit O7, point 2).

Le prompt v2 (PROD) demande un format natif :
    {"score": 0-100, "errors": [{line, type, detail, fix}],
     "feedback": "...", "grade": "retenir | acquis | maîtrisé"}

Le contrat public v1 (et C2) attend : score 0-score_max, highlights,
matched_criteria, unmatched_criteria, feedback_ar, advice_ar, confidence.
Ce module extrait le mapping v2→v1 de evaluate_answer_v2 en fonction PURE
testable — le JSON natif provider garantit une structure parfaite (errors est
une liste, score un entier) : le mapping doit le gérer sans garde de
réparation devenue morte.

Amélioration documentée : le dominant_error_code v2 est maintenant
TYPE-AWARE (scientific_error pour une erreur scientifique) au lieu du
fallback aveugle methodology_error (comportement antérieur : toutes les
erreurs v2 → unmatched → methodology_error, même une erreur scientifique —
ce qui orientait la remédiation vers la méthodologie au lieu du contenu).
"""

from __future__ import annotations

from typing import Any

_ADVICE_BY_GRADE = {
    "retenir": "أعد مراجعة هذا الموضوع وحاول مرة أخرى",
    "acquis": "جيد، لكن يمكنك التعمق أكثر",
    "maîtrisé": "ممتاز! واصل التقدم",
}


def _clamp(value: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(value, max_val))


def _dominant_from_v2_errors(errors: Any, score: int, score_max: int) -> str:
    """Code d'erreur dominant dérivé du format v2 (type-aware).

    - Pas d'erreurs → all_correct / partial_correct / insufficient selon score
    - Type contenant "scient" → scientific_error (remédiation contenu)
    - Type contenant "method"/"منهج" → methodology_error
    - Type "off"/"hors"/"خارج" → off_topic
    - Erreurs non typées → methodology_error (fallback historique)
    """
    if not isinstance(errors, list) or not errors:
        if score >= score_max:
            return "all_correct"
        return "partial_correct" if score > 0 else "insufficient"

    for err in errors:
        if not isinstance(err, dict):
            continue
        t = str(err.get("type", ""))
        tl = t.lower()
        if "scient" in tl:
            return "scientific_error"
        if "method" in tl or "منهج" in t:
            return "methodology_error"
        if "off" in tl or "hors" in tl or "خارج" in t:
            return "off_topic"
    return "methodology_error"


def map_v2_to_v1(
    parsed: dict[str, Any],
    *,
    score_max: int,
    student_answer: str,
) -> dict[str, Any]:
    """Convertit une réponse LLM au format v2 vers le contrat v1.

    Retourne les champs : score, highlights, matched, unmatched, feedback_ar,
    advice_ar, confidence, source, dominant_error_code.
    """
    # Score : v2 retourne 0-100 → normalisé vers 0-score_max
    raw_score = parsed.get("score", 0)
    if isinstance(raw_score, (int, float)):
        score = _clamp(int(raw_score * score_max / 100), 0, score_max)
    else:
        score = 0

    # Highlights : chaque erreur v2 surligne tout le texte (pas de positions
    # dans le format v2) — même comportement que l'ancien mapping inline.
    v2_errors = parsed.get("errors", [])
    highlights: list[dict[str, Any]] = []
    unmatched: list[dict[str, Any]] = []
    if isinstance(v2_errors, list):
        for err in v2_errors:
            if not isinstance(err, dict):
                continue
            highlights.append({
                "start": 0,
                "end": len(student_answer),
                "type": "wrong_formulation",
                "message_ar": err.get("detail", err.get("fix", "")),
            })
            unmatched.append({
                "criterion": err.get("type", "erreur"),
                "why_ar": err.get("detail", ""),
                "from_model_answer": "",
            })

    # Feedback (obligatoire dans le schéma v2, mais robuste si absent)
    feedback_ar = parsed.get("feedback", "")
    if not isinstance(feedback_ar, str):
        feedback_ar = str(feedback_ar)

    # Advice : déduit du grade (mais "grade" n'est PAS le dominant_error_code)
    grade = parsed.get("grade", "")
    advice_ar = _ADVICE_BY_GRADE.get(grade, "")

    confidence = min(1.0, score / score_max) if score_max > 0 else 0.5

    return {
        "score": score,
        "highlights": highlights,
        "matched": [],
        "unmatched": unmatched,
        "feedback_ar": feedback_ar,
        "advice_ar": advice_ar,
        "confidence": confidence,
        "source": "llm_v2",
        "dominant_error_code": _dominant_from_v2_errors(
            v2_errors, score, score_max
        ),
    }
