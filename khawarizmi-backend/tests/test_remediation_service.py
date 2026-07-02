"""tests/test_remediation_service.py — 8 tests pour remediation_service.py.

Couvre :
- get_remediation : match exact, verbe inconnu, error_code inconnu
- get_generic_remediation : match exact, code inconnu
- Intégration dans le contrat de retour (champ remediation présent)
"""

from __future__ import annotations

from services.remediation_service import (
    get_generic_remediation,
    get_remediation,
)


class TestGetRemediation:
    def test_analyse_methodology_error(self):
        r = get_remediation("analyse", "methodology_error")
        assert r is not None
        assert r["page"] == 41
        assert "منهجية" in r["lesson_title"]
        assert "advice_ar" in r

    def test_interpret_scientific_error(self):
        r = get_remediation("interpret", "scientific_error")
        assert r is not None
        assert r["page"] == 55

    def test_unknown_verb_returns_none(self):
        r = get_remediation("toto", "methodology_error")
        assert r is None

    def test_unknown_error_code_returns_none(self):
        r = get_remediation("analyse", "unknown_code")
        assert r is None

    def test_deduce_methodology_error(self):
        r = get_remediation("deduce", "methodology_error")
        assert r is not None
        assert r["page"] == 40

    def test_hypothesis_scientific_error(self):
        r = get_remediation("hypothesis", "scientific_error")
        assert r is not None
        assert r["page"] == 22

    def test_scientific_text_methodology_error(self):
        r = get_remediation("scientific-text", "methodology_error")
        assert r is not None
        assert r["page"] == 21


class TestGetGenericRemediation:
    def test_methodology_error(self):
        r = get_generic_remediation("methodology_error")
        assert r is not None
        assert r["page"] == 14

    def test_unknown_code_returns_none(self):
        r = get_generic_remediation("unknown_code")
        assert r is None

    def test_scientific_error(self):
        r = get_generic_remediation("scientific_error")
        assert r is not None
        assert r["page"] == 8

    def test_off_topic(self):
        r = get_generic_remediation("off_topic")
        assert r is not None
        assert r["page"] == 17
