"""grading/context.py — Contexte request-scoped du pipeline de correction.

Remplace la liste de 14+ arguments transmise entre les fonctions du pipeline.
Le contexte est créé à l'entrée d'évaluate_answer_v2 et ne doit JAMAIS être
partagé entre requêtes (request-scoped, jamais global).

Règles (audit S2.1a) :
1. `student_answer` reste la COPIE ORIGINALE de l'élève, jamais la version
   normalisée (RAG/cache). La normalisation est appliquée au moment de
   l'appel LLM / de la clé de cache, pas dans le contexte.
2. Le contexte ne contient JAMAIS `llm_raw` (ni aucun contenu brut du LLM)
   : il transite uniquement dans la réponse interne du provider, jamais dans
   une structure destinée à l'API.
3. `steps` : durées en MILLISECONDES (documenté — float).
4. `source` initial = "unknown" (état transitoire interne ; jamais exposé en
   résultat final).

Les champs *result (sanity/savoir/l2/parsed/final) sont remplis au fil des
étapes par le pipeline (S2.1i) ; le wrapper shadow (S2.1a) remplit
final_result/source/parse_strategy depuis l'ancien moteur.
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
    student_answer: str  # copie ORIGINALE (règle 1) — jamais normalisée
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

    # ── Traçabilité pipeline ──────────────────────────────────────
    source: str = "unknown"            # état initial transitoire (règle 4)
    parse_strategy: str = "none"       # stratégie de parsing (parser.py)
    steps: dict[str, float] = field(default_factory=dict)  # MILLISECONDES (règle 3)
    llm_called: bool = False
    cache_hit: bool = False

    # ── Étapes (remplies au fil du pipeline) ──────────────────────
    sanity_result: dict[str, Any] | None = None
    savoir_result: dict[str, Any] | None = None
    l2_result: Any = None
    prompt: str | None = None
    llm_response: Any = None
    parsed_llm: dict[str, Any] | None = None
    final_result: dict[str, Any] | None = None

    # NOTE : jamais de llm_raw ici (règle 2) — il vit dans llm_response
    # (objet réponse du provider), retiré avant toute exposition.


# Alias de nomenclature (le pipeline et les tests peuvent utiliser l'un ou
# l'autre nom ; même type).
PipelineContext = GradingContext
