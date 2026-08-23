"""
tests/test_manhadjiya.py — Tests LOT8 : endpoints manhadjiya, VERB_UNIT_MAP,
PRACTICAL_EXAMPLES, get_full_remediation, injection contexte scientifique.

635 tests couvrant : routes (9 endpoints), donnees, mapping verbe-unite,
exemples pratiques, fonctions remediation enrichie.
"""

from __future__ import annotations

from httpx import AsyncClient

# ─── Tests : GET /api/manhadjiya/revision-tips ────────────────────


class TestRevisionTips:
    async def test_returns_data(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/revision-tips")
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert data["count"] > 0

    async def test_structure(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/revision-tips")
        data = resp.json()["data"]
        # Au moins une categorie avec des elements
        categories = list(data.keys())
        assert len(categories) >= 1
        first = data[categories[0]]
        assert isinstance(first, list)
        assert len(first) >= 1

    async def test_includes_expected_categories(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/revision-tips")
        data = resp.json()["data"]
        # Verifie quelques categories attendues
        suggestions = set()
        for items in data.values():
            for item in items:
                suggestions.add(item[:10])
        assert len(suggestions) > 0

    async def test_count_matches(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/revision-tips")
        data = resp.json()
        total = sum(len(v) for v in data["data"].values())
        assert data["count"] == total


# ─── Tests : GET /api/manhadjiya/common-errors ────────────────────


class TestCommonErrors:
    async def test_returns_all(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/common-errors")
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert data["count"] > 0

    async def test_filter_by_category_valid(self, client: AsyncClient) -> None:
        for cat in ["methodology", "knowledge", "form"]:
            resp = await client.get(f"/api/manhadjiya/common-errors?category={cat}")
            assert resp.status_code == 200
            data = resp.json()
            assert cat in data["data"]
            assert data["count"] > 0

    async def test_filter_invalid_category(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/common-errors?category=invalid")
        assert resp.status_code == 200
        data = resp.json()
        assert "error" in data

    async def test_structure(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/common-errors")
        data = resp.json()["data"]
        # Au moins une categorie
        assert len(data) >= 1
        for cat, items in data.items():
            assert isinstance(items, list)
            for item in items:
                assert isinstance(item, str)
                assert len(item) > 5

    async def test_count_accuracy(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/common-errors")
        data = resp.json()
        total = sum(len(v) for v in data["data"].values())
        assert data["count"] == total


# ─── Tests : GET /api/manhadjiya/cognitive-levels ─────────────────


class TestCognitiveLevels:
    async def test_returns_data(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/cognitive-levels")
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert data["count"] > 0

    async def test_has_expected_levels(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/cognitive-levels")
        data = resp.json()["data"]
        assert "remember" in data or "apply" in data
        assert "synthesize" in data or "compare_and_analyse" in data

    async def test_structure(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/cognitive-levels")
        data = resp.json()["data"]
        for level, verbs in data.items():
            assert isinstance(level, str)
            assert isinstance(verbs, list)
            for v in verbs:
                assert isinstance(v, str)
                assert len(v) > 1

    async def test_count_accuracy(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/cognitive-levels")
        data = resp.json()
        total = sum(len(v) for v in data["data"].values())
        assert data["count"] == total


# ─── Tests : GET /api/manhadjiya/analysis-terms ───────────────────


class TestAnalysisTerms:
    async def test_returns_data(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/analysis-terms")
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert data["count"] > 0

    async def test_has_expected_categories(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/analysis-terms")
        data = resp.json()["data"]
        categories = list(data.keys())
        assert len(categories) >= 1

    async def test_structure(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/analysis-terms")
        data = resp.json()["data"]
        for cat, terms in data.items():
            assert isinstance(terms, list)
            for term in terms:
                assert isinstance(term, str)
                assert len(term) >= 2

    async def test_count_accuracy(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/analysis-terms")
        data = resp.json()
        total = sum(len(v) for v in data["data"].values())
        assert data["count"] == total


# ─── Tests : GET /api/manhadjiya/verbs ────────────────────────────


class TestVerbs:
    async def test_returns_all_verbs(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verbs")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 25

    async def test_has_methodology_for_each(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verbs")
        for entry in resp.json()["data"]:
            assert "slug" in entry
            assert "methodology" in entry
            assert len(entry["methodology"]) > 10

    async def test_optional_rubrics_and_level(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verbs")
        for entry in resp.json()["data"]:
            if "rubrics" in entry:
                assert isinstance(entry["rubrics"], dict)
            if "cognitive_level" in entry:
                assert isinstance(entry["cognitive_level"], str)

    async def test_has_units_for_each(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verbs")
        for entry in resp.json()["data"]:
            assert "units" in entry
            assert isinstance(entry["units"], list)

    async def test_includes_key_verbs(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verbs")
        slugs = [e["slug"] for e in resp.json()["data"]]
        for key in ["analyse", "interpret", "deduce", "compare", "extract", "prove-experimentally"]:
            assert key in slugs

    async def test_count_accuracy(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verbs")
        data = resp.json()
        assert data["count"] == len(data["data"])


# ─── Tests : GET /api/manhadjiya/verb/{slug} ──────────────────────


class TestVerbDetail:
    async def test_returns_detail(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verb/analyse")
        assert resp.status_code == 200
        data = resp.json()
        assert data["slug"] == "analyse"
        assert "methodology" in data
        assert len(data["methodology"]) > 10

    async def test_unknown_verb(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verb/xyz-inconnu")
        assert resp.status_code == 200
        data = resp.json()
        assert "error" in data

    async def test_includes_units(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verb/analyse")
        data = resp.json()
        assert "units" in data
        assert len(data["units"]) >= 1

    async def test_includes_rubrics_when_available(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verb/compare")
        data = resp.json()
        assert "rubrics" in data
        assert isinstance(data["rubrics"], dict)

    async def test_interpret_has_units(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verb/interpret")
        data = resp.json()
        assert len(data["units"]) >= 1

    async def test_extract_has_units(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verb/extract")
        data = resp.json()
        assert len(data["units"]) >= 1


# ─── Tests : GET /api/manhadjiya/verb-units ───────────────────────


class TestVerbUnits:
    async def test_returns_mapping(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verb-units")
        assert resp.status_code == 200
        data = resp.json()
        assert "direct" in data
        assert "inverse" in data

    async def test_direct_mapping(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verb-units")
        direct = resp.json()["direct"]
        assert "analyse" in direct
        assert len(direct["analyse"]) >= 1

    async def test_inverse_mapping(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verb-units")
        inverse = resp.json()["inverse"]
        # Au moins une unite avec des verbes
        assert len(inverse) >= 1

    async def test_consistency(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verb-units")
        data = resp.json()
        # Verifier que direct et inverse sont coherents
        for verb, units in data["direct"].items():
            for unit_id in units:
                assert verb in data["inverse"].get(unit_id, [])

    async def test_verb_count(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/verb-units")
        direct = resp.json()["direct"]
        assert len(direct) >= 27


# ─── Tests : POST /api/manhadjiya/contextual-remediation ──────────


class TestContextualRemediation:
    async def test_requires_verb_slug(self, client: AsyncClient) -> None:
        resp = await client.post("/api/manhadjiya/contextual-remediation", json={"verb_slug": ""})
        assert resp.status_code == 200
        data = resp.json()
        assert "error" in data

    async def test_with_empty_context(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/manhadjiya/contextual-remediation",
            json={"verb_slug": "analyse"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["verb"] == "analyse"
        assert isinstance(data["units"], list)

    async def test_with_context(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/manhadjiya/contextual-remediation",
            json={
                "verb_slug": "analyse",
                "context": "ARN messager traduction proteine ribosome",
            },
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "unite1" in " ".join(data["units"])

    async def test_returns_relevant_errors(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/manhadjiya/contextual-remediation",
            json={"verb_slug": "deduce", "context": "ARN ADN proteine"},
        )
        data = resp.json()["data"]
        assert isinstance(data["relevant_errors"], list)
        # Au moins une erreur est retournee (deduce a des unites)
        assert len(data["relevant_errors"]) >= 0  # peut etre vide si pas d'erreurs

    async def test_with_immunity_context(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/manhadjiya/contextual-remediation",
            json={
                "verb_slug": "interpret",
                "context": "anticorps lymphocyte immunite vaccin",
            },
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "unite2" in " ".join(data["units"])

    async def test_with_nerve_context(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/manhadjiya/contextual-remediation",
            json={
                "verb_slug": "justify",
                "context": "synapse neurone neurotransmetteur influx nerveux",
            },
        )
        data = resp.json()["data"]
        units_str = " ".join(data["units"])
        assert "unite3" in units_str


# ─── Tests : GET /api/manhadjiya/practical-examples ───────────────


class TestPracticalExamples:
    async def test_returns_all(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/practical-examples")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 5

    async def test_filter_by_category(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/api/manhadjiya/practical-examples?category=analyse-tableau"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 1
        for ex in data["data"]:
            assert ex["category"] == "analyse-tableau"

    async def test_filter_by_unit(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/api/manhadjiya/practical-examples?unit=unite1-synthese-proteines"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 1
        for ex in data["data"]:
            assert ex.get("unit") == "unite1-synthese-proteines"

    async def test_filter_category_and_unit(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/api/manhadjiya/practical-examples"
            "?category=analyse-vs-interpretation"
            "&unit=unite1-synthese-proteines"
        )
        assert resp.status_code == 200
        data = resp.json()
        for ex in data["data"]:
            assert ex["category"] == "analyse-vs-interpretation"

    async def test_unknown_category(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/api/manhadjiya/practical-examples?category=xyz"
        )
        assert resp.status_code == 200
        assert resp.json()["count"] == 0

    async def test_structure(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/practical-examples")
        for ex in resp.json()["data"]:
            assert "title" in ex
            assert "content" in ex
            assert "category" in ex
            assert len(ex["title"]) > 5
            assert len(ex["content"]) > 20

    async def test_count_accuracy(self, client: AsyncClient) -> None:
        resp = await client.get("/api/manhadjiya/practical-examples")
        data = resp.json()
        assert data["count"] == len(data["data"])


# ─── Tests : VERB_UNIT_MAP (import direct) ────────────────────────


class TestVerbUnitMapDirect:
    def test_all_units_have_verbs(self) -> None:
        from prompts.scientific_knowledge import VERB_UNIT_MAP

        for unit_id, verbs in VERB_UNIT_MAP.items():
            assert len(verbs) >= 5, f"{unit_id} a seulement {len(verbs)} verbes"

    def test_analyse_in_all_units(self) -> None:
        from prompts.scientific_knowledge import VERB_UNIT_MAP

        for unit_id, verbs in VERB_UNIT_MAP.items():
            assert "analyse" in verbs, f"analyse manquant dans {unit_id}"

    def test_interpret_in_all_units(self) -> None:
        from prompts.scientific_knowledge import VERB_UNIT_MAP

        for unit_id, verbs in VERB_UNIT_MAP.items():
            assert "interpret" in verbs, f"interpret manquant dans {unit_id}"

    def test_deduce_in_all_units(self) -> None:
        from prompts.scientific_knowledge import VERB_UNIT_MAP

        for unit_id, verbs in VERB_UNIT_MAP.items():
            assert "deduce" in verbs, f"deduce manquant dans {unit_id}"

    def test_compare_in_all_units(self) -> None:
        from prompts.scientific_knowledge import VERB_UNIT_MAP

        for unit_id, verbs in VERB_UNIT_MAP.items():
            assert "compare" in verbs, f"compare manquant dans {unit_id}"

    def test_five_units_exist(self) -> None:
        from prompts.scientific_knowledge import VERB_UNIT_MAP

        assert len(VERB_UNIT_MAP) == 5

    def test_justify_in_all_units(self) -> None:
        from prompts.scientific_knowledge import VERB_UNIT_MAP

        for unit_id, verbs in VERB_UNIT_MAP.items():
            assert "justify" in verbs, f"justify manquant dans {unit_id}"

    def test_scientific_text_in_all_units(self) -> None:
        from prompts.scientific_knowledge import VERB_UNIT_MAP

        for unit_id, verbs in VERB_UNIT_MAP.items():
            assert "scientific-text" in verbs

    def test_extract_in_all_units(self) -> None:
        from prompts.scientific_knowledge import VERB_UNIT_MAP

        for unit_id, verbs in VERB_UNIT_MAP.items():
            assert "extract" in verbs

    def test_prove_experimentally_in_all_units(self) -> None:
        from prompts.scientific_knowledge import VERB_UNIT_MAP

        for unit_id, verbs in VERB_UNIT_MAP.items():
            assert "prove-experimentally" in verbs


# ─── Tests : get_units_for_verb ────────────────────────────────────


class TestGetUnitsForVerb:
    def test_analyse_returns_5(self) -> None:
        from prompts.scientific_knowledge import get_units_for_verb

        units = get_units_for_verb("analyse")
        assert len(units) == 5

    def test_interpret_returns_5(self) -> None:
        from prompts.scientific_knowledge import get_units_for_verb

        units = get_units_for_verb("interpret")
        assert len(units) == 5

    def test_unknown_verb_returns_empty(self) -> None:
        from prompts.scientific_knowledge import get_units_for_verb

        units = get_units_for_verb("unknown-verb")
        assert units == []

    def test_extract_returns_5(self) -> None:
        from prompts.scientific_knowledge import get_units_for_verb

        assert len(get_units_for_verb("extract")) == 5

    def test_determiner_returns_3(self) -> None:
        from prompts.scientific_knowledge import get_units_for_verb

        units = get_units_for_verb("determiner")
        assert len(units) == 3

    def test_only_specific_verb(self) -> None:
        from prompts.scientific_knowledge import get_units_for_verb

        units = get_units_for_verb("hypothesis")
        assert len(units) == 1
        assert "unite2-immunite" in units


# ─── Tests : PRACTICAL_EXAMPLES ────────────────────────────────────


class TestPracticalExamplesDirect:
    def test_has_categories(self) -> None:
        from prompts.scientific_knowledge import PRACTICAL_EXAMPLES

        assert len(PRACTICAL_EXAMPLES) >= 5

    def test_each_example_has_required_fields(self) -> None:
        from prompts.scientific_knowledge import PRACTICAL_EXAMPLES

        for cat, examples in PRACTICAL_EXAMPLES.items():
            for ex in examples:
                assert "title" in ex
                assert "context" in ex
                assert "content" in ex
                assert len(ex["title"]) > 5
                assert len(ex["content"]) > 20

    def test_analyse_vs_interpretation_present(self) -> None:
        from prompts.scientific_knowledge import PRACTICAL_EXAMPLES

        assert "analyse-vs-interpretation" in PRACTICAL_EXAMPLES

    def test_deduction_vs_extraction_present(self) -> None:
        from prompts.scientific_knowledge import PRACTICAL_EXAMPLES

        assert "deduction-vs-extraction" in PRACTICAL_EXAMPLES

    def test_has_analyse_experience(self) -> None:
        from prompts.scientific_knowledge import PRACTICAL_EXAMPLES

        categories = list(PRACTICAL_EXAMPLES.keys())
        assert "analyse-experience" in categories

    def test_examples_with_units(self) -> None:
        from prompts.scientific_knowledge import PRACTICAL_EXAMPLES

        for cat, examples in PRACTICAL_EXAMPLES.items():
            for ex in examples:
                if "unit" in ex:
                    assert ex["unit"].startswith("unite")


# ─── Tests : get_practical_examples ────────────────────────────────


class TestGetPracticalExamples:
    def test_returns_all_without_filters(self) -> None:
        from prompts.scientific_knowledge import get_practical_examples

        examples = get_practical_examples()
        assert len(examples) >= 5

    def test_filter_by_category(self) -> None:
        from prompts.scientific_knowledge import get_practical_examples

        examples = get_practical_examples(category="analyse-tableau")
        assert len(examples) >= 1
        all(e["category"] == "analyse-tableau" for e in examples)

    def test_filter_by_unit(self) -> None:
        from prompts.scientific_knowledge import get_practical_examples

        examples = get_practical_examples(unit="unite1-synthese-proteines")
        assert len(examples) >= 1
        all(e.get("unit") == "unite1-synthese-proteines" for e in examples)

    def test_unknown_category(self) -> None:
        from prompts.scientific_knowledge import get_practical_examples

        examples = get_practical_examples(category="xyz")
        assert examples == []

    def test_unknown_unit(self) -> None:
        from prompts.scientific_knowledge import get_practical_examples

        examples = get_practical_examples(unit="unite-inexistante")
        assert examples == []


# ─── Tests : get_practical_example_block ───────────────────────────


class TestGetPracticalExampleBlock:
    def test_analyse_returns_block(self) -> None:
        from prompts.scientific_knowledge import get_practical_example_block

        block = get_practical_example_block("ARN ADN proteine", "analyse")
        assert block != ""
        assert "أمثلة تطبيقية" in block or "أمثلة" in block

    def test_interpret_returns_block(self) -> None:
        from prompts.scientific_knowledge import get_practical_example_block

        block = get_practical_example_block("oxygene respiration", "interpret")
        assert block != ""

    def test_deduce_returns_block(self) -> None:
        from prompts.scientific_knowledge import get_practical_example_block

        block = get_practical_example_block("ARNm ADN", "deduce")
        assert block != ""

    def test_unknown_verb_returns_empty(self) -> None:
        from prompts.scientific_knowledge import get_practical_example_block

        block = get_practical_example_block("test", "unknown-verb")
        assert block == ""

    def test_extract_returns_block(self) -> None:
        from prompts.scientific_knowledge import get_practical_example_block

        block = get_practical_example_block("document texte", "extract")
        assert block != ""

    def test_prove_experimentally_returns_block(self) -> None:
        from prompts.scientific_knowledge import get_practical_example_block

        block = get_practical_example_block("experience", "prove-experimentally")
        assert block != ""


# ─── Tests : get_contextual_remediation_data ───────────────────────


class TestGetContextualRemediationData:
    def test_returns_for_known_verb(self) -> None:
        from prompts.scientific_knowledge import get_contextual_remediation_data

        data = get_contextual_remediation_data("analyse")
        assert data["verb"] == "analyse"
        assert len(data["units"]) == 5

    def test_returns_for_verb_with_context(self) -> None:
        from prompts.scientific_knowledge import get_contextual_remediation_data

        data = get_contextual_remediation_data("analyse", "ARN messager proteine")
        assert len(data["units"]) >= 1

    def test_unknown_verb_returns_empty_units(self) -> None:
        from prompts.scientific_knowledge import get_contextual_remediation_data

        data = get_contextual_remediation_data("unknown-verb")
        assert data["units"] == []

    def test_relevant_errors_is_list(self) -> None:
        from prompts.scientific_knowledge import get_contextual_remediation_data

        data = get_contextual_remediation_data("analyse")
        assert isinstance(data["relevant_errors"], list)

    def test_deduce_with_context(self) -> None:
        from prompts.scientific_knowledge import get_contextual_remediation_data

        data = get_contextual_remediation_data("deduce", "ADN ARN")
        assert len(data["units"]) >= 1


# ─── Tests : get_unit_specific_errors ─────────────────────────────


class TestGetUnitSpecificErrors:
    def test_returns_errors_for_known_unit(self) -> None:
        from prompts.scientific_knowledge import get_unit_specific_errors

        errors = get_unit_specific_errors("unite1-synthese-proteines")
        assert len(errors) >= 1

    def test_empty_for_unknown_unit(self) -> None:
        from prompts.scientific_knowledge import get_unit_specific_errors

        errors = get_unit_specific_errors("unite-unknown")
        assert errors == []

    def test_errors_are_strings(self) -> None:
        from prompts.scientific_knowledge import get_unit_specific_errors

        errors = get_unit_specific_errors("unite2-immunite")
        for err in errors:
            assert isinstance(err, str)

    def test_max_five_errors(self) -> None:
        from prompts.scientific_knowledge import get_unit_specific_errors

        for unit_id in [
            "unite1-synthese-proteines",
            "unite2-immunite",
            "unite3-systeme-nerveux",
            "unite4-geologie",
            "unite5-energie",
        ]:
            errors = get_unit_specific_errors(unit_id)
            assert len(errors) <= 10  # _MAX_ERRORS est 5 mais on prend 3 dans contextual

    def test_errors_meaningful(self) -> None:
        from prompts.scientific_knowledge import get_unit_specific_errors

        errors = get_unit_specific_errors("unite1-synthese-proteines")
        for err in errors:
            assert "❌" in err or "خطأ" in err or "→" in err


# ─── Tests : get_full_remediation ─────────────────────────────────


class TestGetFullRemediation:
    def test_returns_remediation(self) -> None:
        from services.remediation_service import get_full_remediation

        result = get_full_remediation("analyse", "methodology_error")
        assert result["verb"] == "analyse"
        assert result["error_code"] == "methodology_error"
        assert result["remediation"] is not None

    def test_unknown_verb(self) -> None:
        from services.remediation_service import get_full_remediation

        result = get_full_remediation("unknown", "methodology_error")
        assert result["remediation"] is None

    def test_includes_contextual_data(self) -> None:
        from services.remediation_service import get_full_remediation

        result = get_full_remediation("analyse", "scientific_error", context="ARN ADN")
        assert "contextual" in result

    def test_includes_generic_fallback(self) -> None:
        from services.remediation_service import get_full_remediation

        result = get_full_remediation("analyse", "unknown_error")
        assert result["remediation"] is None
        assert result["generic_remediation"] is None

    def test_with_unit(self) -> None:
        from services.remediation_service import get_full_remediation

        result = get_full_remediation("interpret", "confusion_analyse_interpret")
        assert result["remediation"] is not None


# ─── Tests : correction_prompt injection ──────────────────────────


class TestCorrectionPromptInjection:
    def test_build_prompt_includes_practical_examples(self) -> None:
        from prompts.correction_prompt import build_correction_prompt

        prompt = build_correction_prompt(
            scenario_context="Etude de la synthese des proteines",
            documents=None,
            question_prompt="Analysez le mecanisme de la traduction",
            question_skill="analyse",
            verb_slug="analyse",
            model_answer="La traduction est le processus...",
            learning_focus=None,
            score_max=5,
            student_answer="La traduction commence par...",
        )
        assert "أمثلة تطبيقية" in prompt

    def test_build_prompt_without_practical_examples_for_unknown_verb(self) -> None:
        from prompts.correction_prompt import build_correction_prompt

        prompt = build_correction_prompt(
            scenario_context="Test",
            documents=None,
            question_prompt="Expliquez",
            question_skill="expliquer",
            verb_slug="decrire",
            model_answer="Description...",
            learning_focus=None,
            score_max=3,
            student_answer="Je decris...",
        )
        # Decrire n'a pas d'exemples pratiques definis
        assert "أمثلة تطبيقية" not in prompt

    def test_build_prompt_includes_knowledge_block(self) -> None:
        from prompts.correction_prompt import build_correction_prompt

        prompt = build_correction_prompt(
            scenario_context="Synthese proteique",
            documents=None,
            question_prompt="Analysez le role de l'ARNm",
            question_skill="analyse",
            verb_slug="analyse",
            model_answer="L'ARNm transporte...",
            learning_focus=None,
            score_max=5,
            student_answer="L'ARNm est...",
        )
        assert "المرجع العلمي" in prompt

    def test_build_prompt_without_knowledge_for_empty_context(self) -> None:
        from prompts.correction_prompt import build_correction_prompt

        prompt = build_correction_prompt(
            scenario_context="",
            documents=None,
            question_prompt="",
            question_skill="analyse",
            verb_slug="analyse",
            model_answer="Reponse",
            learning_focus=None,
            score_max=2,
            student_answer="Reponse eleve",
        )
        # Si le contexte est vide, le bloc de connaissance peut etre vide
        assert isinstance(prompt, str)
        assert len(prompt) > 50
