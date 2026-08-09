"""grading/savoir.py — Étage Savoir Corrector (audit S2.1c).

Extrait du wrapper cache (grading/cache.py) vers sa vraie place : l'orchestration
de la notation vit dans le pipeline, le cache ne fait que cacher.

Règles de promotion (design validé + mesuré par le golden set) :
- Feature flag PAR VERBE (config.savoir_enabled_verbs, défaut vide).
- can_handle (question couverte par le lexique — jamais généraliste).
- ≥ SAVOIR_HIGH_CONFIDENCE_MIN_CONCEPTS concepts trouvés DANS LA COPIE
  (périmètre validé : MAE 0.279 global, copies modèles MAE 0.000).
  NB : le seuil 0.92 est DÉRIVÉ (3/3) — ne pas l'ajuster dynamiquement.
- Remédiation DÉSACTIVÉE (κ 0.449 < 0.65) : jamais de mauvaise page de livre.

Retourne un résultat PROMU au contrat v2 (source="local_savoir",
parse_status="local", attempts=0, remediation=None, métadonnées _savoir_*
incluses — retirées du payload caché par project/to_cache_payload).
"""

from __future__ import annotations

from typing import Any

from services.savoir_corrector import (
    SAVOIR_HIGH_CONFIDENCE_MIN_CONCEPTS,
    deterministic_correct_v2,
    is_savoir_enabled,
)


def run_savoir(
    *,
    question: str,
    student_answer: str,
    verb_slug: str,
    score_max: int,
    model_answer: str = "",
) -> dict[str, Any] | None:
    """Étage savoir (spécialiste haute confiance, 0 token, 0 clé).

    Retourne un résultat promu au contrat v2 si applicable, sinon None
    (le pipeline continue vers le LLM/L2). Le calcul est purement local.
    """
    if not is_savoir_enabled(verb_slug):
        return None

    result = deterministic_correct_v2(
        question=question,
        student_answer=student_answer,
        score_max=score_max,
        language="ar",
        model_answer=model_answer,
    )

    if not (
        result["_savoir_can_handle"]
        and result["_savoir_n_concepts"] >= SAVOIR_HIGH_CONFIDENCE_MIN_CONCEPTS
    ):
        return None

    # Promotion au contrat v2 (mêmes conventions que l'ancien emplacement)
    result["attempts"] = 0
    result["parse_status"] = "local"
    result["finish_reason"] = "savoir_high_confidence"
    # κ modéré (0.449 < 0.65) : jamais de remédiation erronée (audit V0.2)
    result["remediation"] = None
    result["remediation_reason"] = "local_savoir_no_remediation"
    return result
