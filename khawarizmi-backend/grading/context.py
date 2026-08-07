"""grading/context.py — Contexte request-scoped du pipeline de correction.

Remplace la liste de 14+ arguments transmise entre les fonctions du pipeline.
Le contexte est créé à l'entrée d'évaluate_answer_v2 et ne doit JAMAIS être
partagé entre requêtes (request-scoped, jamais global).

Les champs sont alignés sur les paramètres réels de evaluate_answer_v2 et du
wrapper cache (grading/cache.py) : question_id/verb_slug/score_max/answer,
les entrées du prompt (scenario, documents, learning_focus, question_text),
et les options runtime (llm_timeout, use_v2_prompt, local_fallback…).

Les champs *result (sanity/savoir/l2/parsed) sont remplis au fil des étapes
par le pipeline (S2.1i) — inutilisés pour l'instant (S2.1a : création seule).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GradingContext:
    """Contexte d'une correction — request-scoped, jamais partagé."""

    # ── Identité de la question ───────────────────────────────────
    question_id: int | str
    verb_slug: str
    score_max: int
    student_answer: str
    model_answer: str

    # ── Entrées du prompt ─────────────────────────────────────────
    scenario_context: str = ""
    documents: list[dict[str, Any]] = field(default_factory=list)
    learning_focus: str = ""
    question_text: str = ""  # prompt_ar de la question
    language: str = "ar"

    # ── Runtime / provenance ──────────────────────────────────────
    llm_timeout: float | None = None
    provider: str = "none"
    model: str = ""
    attempts: int = 0
    request_id: str | None = None

    # ── Options du pipeline ───────────────────────────────────────
    use_v2_prompt: bool = True
    local_fallback: bool = False
    local_fallback_db: Any = None
    rag_context_provider: Any = None

    # ── Étapes (remplies au fil du pipeline) ──────────────────────
    sanity: Any = None
    savoir_result: Any = None
    l2_result: Any = None
    parsed_llm: dict[str, Any] | None = None
