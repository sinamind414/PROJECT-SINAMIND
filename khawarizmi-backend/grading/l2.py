"""grading/l2.py — Étage L2 : évaluation locale (audit S2.1d).

Extrait de correction_v2._evaluate_local_fallback : l'évaluation 100 % locale
(0 token, 0 clé API) via services/fallback_v2.evaluate_l2 — TF-IDF + regex
structurelle + embeddings locaux. Utilisée quand le LLM est indisponible
(pas de clé API, panne, quota) ou que le JSON est irrécupérable.

Logique FIDÈLE à l'original :
- concepts requis = skill du verbe + mots significatifs de la réponse modèle
  (stop words arabes filtrés, limités à 10) ;
- redistribution des poids quand l'embedder sémantique est en fallback
  (ONNX absent) : le signal sémantique est du bruit → poids reportés sur
  TF-IDF + structurel ;
- résultat au contrat v2 : source="local", parse_status="local_fallback",
  model="fallback_l2", confidence=0.6, dominant_error_code dérivé du score.
- Retourne None sur échec (l'appelant décide du llm_error).
"""

from __future__ import annotations

import logging
import re
from typing import Any

from services.hashing import hash_answer

logger = logging.getLogger("khawarizmi.grading_l2")

# Stop words arabes de l'extraction de concepts (fidèle à l'original).
_L2_STOP_WORDS = {
    "التي", "الذي", "حيث", "على", "الى", "إلى", "من", "في", "عن", "مع",
    "هذا", "هذه", "ذلك", "بعد", "قبل", "عند", "خلال", "أن", "ان", "ثم",
    "كل", "بين", "كان", "هو", "هي", "لا", "ما", "لأن", "حسب", "وقد",
    "يتم", "تم", "يكون", "تكون", "عبارة",
}


def _clamp(value: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(value, max_val))


def _extract_concepts(question_skill: str, model_answer: str) -> list[str]:
    """Concepts requis : skill du verbe + mots significatifs du modèle."""
    concepts: list[str] = []
    if question_skill:
        concepts.append(question_skill)
    if model_answer:
        words = re.findall(r"[\w\u0600-\u06FF]{4,}", model_answer)
        for w in words:
            if w not in _L2_STOP_WORDS and w not in concepts:
                concepts.append(w)
        concepts = concepts[:10]
    return concepts


async def run_l2(
    *,
    student_answer: str,
    model_answer: str,
    question_skill: str,
    score_max: int,
    db: Any,
    log_prefix: str = "",
) -> dict[str, Any] | None:
    """Évaluation locale L2 — retourne un résultat au format v2 (source=
    "local"), ou None si l'échec (l'appelant construit alors un llm_error).
    """
    try:
        from services.fallback_v2 import evaluate_l2

        concepts_requis = _extract_concepts(question_skill, model_answer)

        question_data = {
            "reponse_attendue": model_answer or "",
            "concepts_requis": concepts_requis,
            "points_cles": [model_answer] if model_answer else [],
            "question_id": None,
        }
        res = await evaluate_l2(
            reponse_eleve=student_answer,
            question_data=question_data,
            db=db,
        )

        # Si l'embedder sémantique est en fallback (modèle ONNX absent), le
        # signal sémantique s1 est du bruit : on redistribue son poids sur
        # TF-IDF + structurel.
        final_score = res.score_final
        try:
            from services.embedder import get_embedder

            if bool(getattr(get_embedder(), "is_fallback", False)):
                w_s, w_t, w_r = 0.40, 0.25, 0.35
                denom = w_t + w_r
                final_score = (w_t * res.coverage_score + w_r * res.structural_score) / denom
                final_score = max(0.0, min(1.0, final_score))
        except Exception:
            pass

        score = _clamp(int(round(final_score * score_max)), 0, score_max)
        percentage = round((score / score_max) * 100) if score_max > 0 else 0
        missing = [
            {"expected": c, "why_ar": "مفهوم غير موجود في الإجابة", "from_model_answer": ""}
            for c in res.concepts_manquants
        ]
        unmatched = [{"criterion": c, "why_ar": "مفهوم غير موجود في الإجابة", "from_model_answer": ""}
                     for c in res.concepts_manquants]

        if score == score_max:
            dominant = "all_correct"
        elif score > 0:
            dominant = "partial_correct"
        else:
            dominant = "insufficient"

        advice = (
            "أحسنت! راجع التفاصيل الدقيقة لتكتمل الإجابة."
            if score > 0 else
            "أعد كتابة إجابتك بالاعتماد على المفاهيم الأساسية للدرس."
        )

        logger.info(
            f"{log_prefix}local_fallback_done | score={score}/{score_max} "
            f"({percentage}%) concepts_trouves={res.concepts_trouves} "
            f"manquants={res.concepts_manquants}"
        )

        return {
            "source": "local",
            "score": score,
            "score_max": score_max,
            "percentage": percentage,
            "highlights": [],
            "matched_criteria": list(res.concepts_trouves),
            "unmatched_criteria": unmatched,
            "feedback_ar": res.feedback_fallback,
            "advice_ar": advice,
            "confidence": 0.6,
            "sanity_code": "ok",
            "provider": "local",
            "model": "fallback_l2",
            "finish_reason": "local",
            "prompt_hash": None,
            "student_answer_hash": hash_answer(student_answer),
            "llm_raw_hash": None,
            "parse_status": "local_fallback",
            "missing": missing,
            "dominant_error_code": dominant,
            "success": list(res.concepts_trouves),
            "errors": list(res.concepts_manquants),
            "remediation": None,
        }
    except Exception as exc:
        logger.warning(f"{log_prefix}local_fallback_failed | {exc}")
        return None
