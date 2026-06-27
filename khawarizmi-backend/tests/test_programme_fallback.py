"""Tests pour le fallback JSON du programme et la normalisation filiere."""

from routes.programme import (
    normalize_filiere,
    _load_programme_fallback,
    _restructure_json_to_response,
)


class TestNormalizeFiliere:
    def test_sciences_naturelles(self):
        assert normalize_filiere("Sciences Naturelles") == "Sciences Experimentales"

    def test_se_abbreviation(self):
        assert normalize_filiere("SE") == "Sciences Experimentales"

    def test_snv(self):
        assert normalize_filiere("SNV") == "Sciences Experimentales"

    def test_canonical_unchanged(self):
        assert normalize_filiere("Sciences Experimentales") == "Sciences Experimentales"

    def test_unknown_passthrough(self):
        assert normalize_filiere("Filiere Inconnue") == "Filiere Inconnue"

    def test_empty(self):
        assert normalize_filiere("") == ""

    def test_case_insensitive(self):
        assert normalize_filiere("SCIENCES NATURELLES") == "Sciences Experimentales"

    def test_whitespace_stripped(self):
        assert normalize_filiere("  SE  ") == "Sciences Experimentales"


class TestJsonFallback:
    def test_loads_without_crash(self):
        result = _load_programme_fallback()
        assert isinstance(result, dict)

    def test_has_domains(self):
        result = _load_programme_fallback()
        if result:
            assert "domains" in result
            assert len(result["domains"]) > 0

    def test_restructure_output_format(self):
        raw = _load_programme_fallback()
        if not raw or not raw.get("domains"):
            return

        response = _restructure_json_to_response(raw)

        assert "matiere" in response
        assert "filiere" in response
        assert "domains" in response
        assert "total_chapters" in response

        assert isinstance(response["domains"], list)
        assert response["total_chapters"] > 0

        domain = response["domains"][0]
        assert "id" in domain
        assert "numero" in domain
        assert "titre_fr" in domain
        assert "units" in domain
        assert isinstance(domain["units"], list)

        unit = domain["units"][0]
        assert "id" in unit
        assert "chapters" in unit
        assert isinstance(unit["chapters"], list)

        chapter = unit["chapters"][0]
        assert "id" in chapter
        assert "titre_fr" in chapter
        assert "importance" in chapter

    def test_uuids_are_unique(self):
        raw = _load_programme_fallback()
        if not raw or not raw.get("domains"):
            return

        r1 = _restructure_json_to_response(raw)
        r2 = _restructure_json_to_response(raw)

        d1_ids = {d["id"] for d in r1["domains"]}
        d2_ids = {d["id"] for d in r2["domains"]}
        assert d1_ids != d2_ids, "UUIDs must be unique across calls"
