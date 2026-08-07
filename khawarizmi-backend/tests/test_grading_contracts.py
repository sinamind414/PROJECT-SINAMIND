"""tests/test_grading_contracts.py — Contrat v2 (audit S2.1a).

Vérifie que grading/contracts.py est ALIGNÉ sur :
1. Le schéma Pydantic runtime (schemas/evaluation_v2.py) — superset, pas de
   champ oublié.
2. Les valeurs réellement produites par le pipeline (sources, parse_status).
"""

from typing import get_args

from grading.contracts import (
    CACHEABLE_PARSE_STATUS,
    CACHEABLE_SOURCES,
    EvaluationV2,
    ParseStatus,
    SourceV2,
)
from schemas.evaluation_v2 import EvaluationResultV2Internal, EvaluationResultV2Public
from schemas.evaluation_v2 import SourceV2 as SchemaSourceV2


class TestSourceV2:
    def test_superset_of_schema_literal(self):
        """Chaque source du Literal Pydantic est valide côté grading.

        Écart documenté : grading ajoute "local_savoir" (étage savoir S1)
        absent de schemas — à unifier lors du refactor des schémas.
        """
        grading_sources = set(get_args(SourceV2))
        schema_sources = set(get_args(SchemaSourceV2))
        assert schema_sources <= grading_sources
        assert grading_sources - schema_sources == {"local_savoir"}

    def test_reality_sources_present(self):
        """Toutes les sources réellement produites par le pipeline."""
        reality = {
            "local", "local_savoir", "llm", "llm_v2", "llm_recovered",
            "llm_retried", "sanity", "llm_error", "cached_evaluation",
        }
        assert reality <= set(get_args(SourceV2))


class TestParseStatus:
    def test_reality_statuses_present(self):
        reality = {
            "not_called", "ok", "recovered", "failed",
            "local_fallback", "local", "cached",
        }
        assert reality <= set(get_args(ParseStatus))


class TestCacheableSets:
    def test_cacheable_sources_match_cache_policy(self):
        """Aligné sur CACHE_WRITE_ALLOWED de grading/cache.py."""
        assert {
            "llm", "llm_v2", "llm_retried", "local_savoir", "local_l2_high_conf",
        } == CACHEABLE_SOURCES
        # Jamais une note dégradée (piège 3 C2)
        assert "local" not in CACHEABLE_SOURCES
        assert "llm_error" not in CACHEABLE_SOURCES
        assert "sanity" not in CACHEABLE_SOURCES

    def test_cacheable_parse_status(self):
        assert {"ok", "recovered", "local"} == CACHEABLE_PARSE_STATUS


class TestEvaluationV2TypedDict:
    def test_covers_public_schema_fields(self):
        """Tous les champs du modèle Pydantic Public sont dans le TypedDict
        (le TypedDict sert à l'autocomplétion — aucun champ oublié)."""
        public_fields = set(EvaluationResultV2Public.model_fields)
        internal_fields = set(EvaluationResultV2Internal.model_fields)
        typed_fields = set(EvaluationV2.__annotations__)

        assert public_fields <= typed_fields, (
            f"champs Public manquants : {public_fields - typed_fields}"
        )
        # Champs INTERNES (llm_raw) couverts aussi (debug)
        assert internal_fields <= typed_fields, (
            f"champs Internal manquants : {internal_fields - typed_fields}"
        )

    def test_internal_only_field_is_llm_raw(self):
        """Seul llm_raw distingue Internal de Public — et il est bien
        présent dans le TypedDict (marqué INTERNE)."""
        internal_only = set(EvaluationResultV2Internal.model_fields) - set(
            EvaluationResultV2Public.model_fields
        )
        assert internal_only == {"llm_raw"}

    def test_reality_extra_fields_present(self):
        """Champs additionnels réels du pipeline (hors Pydantic) couverts."""
        for field in ("from_cache", "error_message", "remediation_reason"):
            assert field in EvaluationV2.__annotations__, field
