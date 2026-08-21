"""grading/savoir.py — Étage Savoir Corrector (audit S2.1c).

Extrait du wrapper cache (grading/cache.py) vers sa vraie place : l'orchestration
de la notation vit dans le pipeline, le cache ne fait que cacher.

Règles de promotion (design validé + mesuré par le golden set) :
- Feature flag PAR VERBE (config.savoir_enabled_verbs, défaut vide).
- can_handle (question couverte par le lexique — jamais généraliste).
- ≥ SAVOIR_HIGH_CONFIDENCE_MIN_CONCEPTS concepts trouvés DANS LA COPIE
  (périmètre validé : MAE 0.279 global, copies modèles MAE 0.000).
  NB : le seuil 0.92 est DÉRIVÉ (3/3) — ne pas l'ajuster dynamiquement.
- Remédiation : gate config.savoir_remediation_enabled (défaut False).
  Le golden set actuel mesure κ = 0.858 ≥ 0.65 → le processus golden dit
  « RÉACTIVER » — activation en prod via SAVOIR_REMEDIATION_ENABLED=true.

Retourne un résultat PROMU au contrat v2 (source="local_savoir",
parse_status="local", attempts=0, remediation=None, métadonnées _savoir_*
incluses — retirées du payload caché par project/to_cache_payload).
"""

from __future__ import annotations

from typing import Any

from config import get_settings
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
    # Remédiation : gate de production (κ golden = 0.858 ≥ 0.65, 2026-08-20).
    # Défaut désactivé → comportement identique à l'historique (tests gelés).
    # Activée, la remédiation réutilise la MÊME matrice que le chemin LLM
    # (services.remediation_service) pour un shape de payload identique.
    result["remediation"] = None
    result["remediation_reason"] = "local_savoir_no_remediation"
    if get_settings().savoir_remediation_enabled:
        from services.remediation_service import get_generic_remediation, get_remediation

        remediation = get_remediation(verb_slug, result["dominant_error_code"])
        if remediation is None:
            remediation = get_generic_remediation(result["dominant_error_code"])
        if remediation is not None:
            result["remediation"] = remediation
            result["remediation_reason"] = "local_savoir_lexique"
    return result
