"""grading/contracts.py — Contrat v2 de correction (audit S2.1a).

Types, Literals et TypedDict du résultat d'évaluation — pour l'autocomplétion
et la lisibilité interne du pipeline. Le schéma Pydantic
(schemas/evaluation_v2.py, Sprint 0) reste la source de validation runtime.

Alignement avec schemas/evaluation_v2.py :
- SourceV2 aligné sur le Literal Pydantic (mis à jour en S2.1a : local_savoir,
  local_l2_high_conf, unknown ajoutés). La provenance n'est JAMAIS convertie
  en "local" : elle compte pour les métriques, l'audit et le taux de promotion.
- ParseStatus n'existe pas côté Pydantic (champ str) ; ici il reflète les
  valeurs réellement produites par le pipeline, scindé en
  ParseStatusInternal (avec "not_called" transitoire) / ParseStatusPublic.
- Le TypedDict est volontairement SUPERSET du modèle Public : il couvre aussi
  les champs internes/additionnels réels (llm_raw pour llm_error, error_message,
  from_cache pour les hits cache, remediation_reason pour local_savoir).
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

SourceV2 = Literal[
    "local",
    "local_savoir",       # étage savoir haute confiance (S1) — provenance
    "local_l2_high_conf",  # futur étage L2 haute confiance (O1)
    "llm",
    "llm_v2",
    "llm_recovered",
    "llm_retried",
    "sanity",
    "llm_error",
    "cached_evaluation",
    # État transitoire interne du pipeline (jamais exposé en réponse finale)
    "unknown",
]

# ParseStatus INTERNE : inclut "not_called" (état transitoire avant l'appel
# LLM — rejet sanity). Utilisé par le pipeline pour son état courant.
ParseStatusInternal = Literal[
    "not_called",       # rejet sanity (pas d'appel LLM) / état initial
    "ok",               # parse direct
    "recovered",        # parse après stratégie de rattrapage (ou v2)
    "failed",           # erreur LLM / parse impossible
    "local_fallback",   # évaluation locale L2
    "local",            # étage savoir
    "cached",           # rehydratation depuis le cache
]

# ParseStatus PUBLIC : "not_called" est un état transitoire interne — il n'a
# pas de sens dans un résultat final exposé (un résultat final est soit noté,
# soit en erreur). "local" (étage savoir) est conservé : c'est une valeur
# RÉELLEMENT produite par le pipeline et cacheable (politique C2).
ParseStatusPublic = Literal[
    "ok",
    "recovered",
    "failed",
    "local_fallback",
    "local",
    "cached",
]

# Alias rétrocompatible (le pipeline interne utilise l'ensemble complet).
ParseStatus = ParseStatusInternal

DominantErrorCode = Literal[
    "scientific_error", "methodology_error", "off_topic", "partial_correct",
    "all_correct", "insufficient", "gibberish", "too_short", "empty",
    "not_arabic", "repeated_chars", "server_error", "unknown",
]

# Sources dont la note est CACHABLE (cf. grading/cache.py CACHE_WRITE_ALLOWED).
CACHEABLE_SOURCES: frozenset[str] = frozenset({
    "llm", "llm_v2", "llm_retried", "local_savoir", "local_l2_high_conf",
})

# ParseStatus acceptés pour une mise en cache (cf. CACHE_PARSE_ALLOWED).
CACHEABLE_PARSE_STATUS: frozenset[str] = frozenset({"ok", "recovered", "local"})


class HighlightV2(TypedDict):
    start: int
    end: int
    type: str
    message_ar: str


class UnmatchedCriterionV2(TypedDict, total=False):
    criterion: str
    why_ar: str
    from_model_answer: str


class RemediationV2(TypedDict, total=False):
    page: int | None
    lesson_title: str | None
    advice_ar: str | None


class EvaluationV2(TypedDict, total=False):
    """Résultat d'évaluation — superset du contrat Public (champs réels).

    total=False : les builders ne remplissent pas tous les champs
    (le rejet sanity n'a pas de provider LLM, etc.).
    """

    # Origine / métadonnées
    source: SourceV2
    provider: str
    model: str
    finish_reason: str
    attempts: int
    parse_status: ParseStatus

    # Note
    score: int
    score_max: int
    percentage: int
    confidence: float

    # Contenu pédagogique
    highlights: list[HighlightV2]
    matched_criteria: list[str]
    unmatched_criteria: list[UnmatchedCriterionV2]
    missing: list[dict[str, Any]]
    success: list[str]
    errors: list[str]
    dominant_error_code: str
    remediation: dict[str, Any] | None
    remediation_reason: str | None  # savoir : remédiation désactivée (κ < 0.65)
    feedback_ar: str
    advice_ar: str
    sanity_code: str

    # Traçabilité (hash-only — jamais de contenu en clair)
    student_answer_hash: str | None
    llm_raw_hash: str | None
    prompt_hash: str | None

    # Cache / observabilité
    from_cache: bool  # hit du cache de correction (source d'origine préservée)
    error_message: str | None  # uniquement sur llm_error
    llm_raw: str | None  # INTERNE (debug) — jamais dans le contrat Public
