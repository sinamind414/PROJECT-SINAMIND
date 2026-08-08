"""grading/pipeline.py — Orchestrateur du pipeline de correction (audit S2.1).

⚠️ ÉTAT ACTUEL (S2.1a) : MODE SHADOW. Le pipeline délègue à l'ancien moteur
(evaluate_answer_v2 / evaluate_answer_v2_with_retry) et construit le contexte
autour de l'appel. Objectif strict : `nouveau pipeline(input) == ancien
moteur(input)` — la parité est démontrée par tests (test_grading_pipeline.py)
AVANT de brancher la route. Les étapes (sanity → savoir → L2 → LLM → parser →
post-validation) seront extraites une à une dans les commits S2.1b..j.

Contraintes architecturales (critère S2.1) :
- AUCUN import FastAPI / SQLAlchemy / Redis ici (le cache C2 reste un
  décorateur extérieur dans grading/cache.py).
- Le contexte est request-scoped (grading/context.py) — jamais global.
- La route reste branchée sur services/correction_v2 (façade de compat).
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any

from grading.context import PipelineContext
from grading.sanity import run_sanity, sanity_tuple

# Champs variables exclus de la comparaison de parité (tests) : ils dépendent
# du run (hashes, horodatage) ou d'étapes pas encore extraites.
VOLATILE_FIELDS = {
    "attempts",
    "prompt_hash",
    "student_answer_hash",
    "llm_raw_hash",
    "latency_ms",
}


async def evaluate_answer_v2_pipeline(
    *,
    question_id: int | str,
    verb_slug: str,
    score_max: int,
    student_answer: str,
    model_answer: str,
    evaluate_legacy: Callable[..., Awaitable[dict[str, Any]]],
    **kwargs: Any,
) -> dict[str, Any]:
    """Shadow : délègue à l'ancien moteur et remplit le contexte.

    Mêmes paramètres que evaluate_answer_v2 (via **kwargs) + :
        question_id, verb_slug, score_max, model_answer : composants du
        contexte (la copie reste l'ORIGINALE — règle 1, jamais normalisée ici)
        evaluate_legacy : l'ancien moteur (evaluate_answer_v2[_with_retry])

    Retourne EXACTEMENT le résultat de l'ancien moteur (parité) ; le contexte
    est rempli pour les métriques/observabilité futures.
    """
    ctx = PipelineContext(
        question_id=question_id,
        verb_slug=verb_slug,
        score_max=score_max,
        student_answer=student_answer,
        model_answer=model_answer,
        scenario_context=kwargs.get("scenario_context", ""),
        documents=kwargs.get("documents") or [],
        learning_focus=kwargs.get("learning_focus", ""),
        question_text=kwargs.get("question_prompt", ""),
        llm_timeout=kwargs.get("llm_timeout"),
        request_id=kwargs.get("request_id"),
        use_v2_prompt=bool(kwargs.get("use_v2_prompt", True)),
        local_fallback=bool(kwargs.get("local_fallback")),
        local_fallback_db=kwargs.get("local_fallback_db"),
    )

    # S2.1b : Étape 1 — SANITY, extraite du monolithe. Toujours première,
    # même si le rejet est immédiat (déterministe, ~µs). Le résultat est porté
    # par le contexte ET transmis au legacy via precomputed_sanity : l'ancien
    # moteur ne refait pas le calcul, mais reste la source du format (parité).
    t_sanity = time.perf_counter()
    sanity = run_sanity(student_answer)
    ctx.sanity_result = sanity
    ctx.steps["sanity_ms"] = (time.perf_counter() - t_sanity) * 1000.0

    t_legacy = time.perf_counter()
    result = await evaluate_legacy(
        student_answer=student_answer,
        score_max=score_max,
        verb_slug=verb_slug,
        model_answer=model_answer,
        precomputed_sanity=sanity_tuple(sanity),
        **kwargs,
    )
    ctx.steps["legacy_total_ms"] = (time.perf_counter() - t_legacy) * 1000.0

    # Traçabilité du résultat (source réelle de l'ancien moteur)
    ctx.final_result = result
    ctx.source = result.get("source", "unknown")
    ctx.parse_strategy = result.get("parse_strategy", "none")
    ctx.llm_called = result.get("source", "") not in {
        "sanity", "local_savoir", "cached_evaluation",
    }

    return result


def assert_parity(
    pipeline_result: dict[str, Any],
    legacy_result: dict[str, Any],
    *,
    extra_volatile: set[str] | None = None,
) -> None:
    """Compare un résultat pipeline vs ancien moteur (champs fonctionnels).

    Ignore les champs VOLATILE_FIELDS (variables par run) + extra_volatile.
    Lève AssertionError avec le détail des différences sinon.
    """
    ignored = VOLATILE_FIELDS | (extra_volatile or set())
    p = {k: v for k, v in pipeline_result.items() if k not in ignored}
    l = {k: v for k, v in legacy_result.items() if k not in ignored}
    assert p == l, (
        f"PARITÉ CASSÉE — pipeline ≠ legacy\n"
        f"  champs pipeline seuls : {set(p) - set(l)}\n"
        f"  champs legacy seuls : {set(l) - set(p)}\n"
        f"  différences : {[(k, p.get(k), l.get(k)) for k in set(p) & set(l) if p[k] != l[k]][:5]}"
    )
