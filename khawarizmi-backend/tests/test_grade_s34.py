"""S34 — hygiène trend des Documents (audit F7). cites_trend dormant sécurisé.

Un doc dont trend_variants contredit le trend déclaré est un piège pour le
premier auteur qui branche cites_trend. validate_rubrics FAIL désormais.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from schemas.document_model import DocumentModel
from services.local_grader import _trend_hits
from services.arabic import normalize_arabic
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "validate_rubrics", BACKEND / "scripts" / "validate_rubrics.py"
)
_vr = importlib.util.module_from_spec(_spec)
sys.modules["validate_rubrics"] = _vr
_spec.loader.exec_module(_vr)


def _doc(trend: str, variants: list[str]) -> DocumentModel:
    return DocumentModel(doc_id="test-doc", trend=trend, trend_variants=variants)  # type: ignore[arg-type]


class TestRegleDirection:
    def test_increase_avec_mot_decroissant_fail(self):
        fails = _vr._doc_trend_fails(_doc("increase_then_plateau", ["يزداد", "يتناقص"]))
        assert any("contredit" in f for f in fails)

    def test_decrease_avec_mot_croissant_fail(self):
        fails = _vr._doc_trend_fails(_doc("decrease", ["تتناقص", "يرتفع"]))
        assert any("contredit" in f for f in fails)

    def test_bell_autorise_les_deux_phases(self):
        """bell = montée ET descente : les deux directions sont légitimes."""
        assert _vr._doc_trend_fails(_doc("bell", ["يزداد", "ينقص", "قصوى"])) == []

    def test_unknown_avec_variants_fail(self):
        fails = _vr._doc_trend_fails(_doc("unknown", ["يزداد"]))
        assert any("données mortes" in f for f in fails)

    def test_trend_sans_variants_fail(self):
        fails = _vr._doc_trend_fails(_doc("increase", []))
        assert any("sourd" in f for f in fails)


class TestDocsReels:
    def test_yeast_doc_nettoye(self):
        """يتناقص retiré (contredisait increase_then_plateau). v1.0.2."""
        packed = load("yeast-glucose-interpret")
        assert packed is not None
        d = packed.document
        assert d is not None
        assert d.version == "1.0.2"
        assert "يتناقص" not in d.trend_variants
        assert _vr._doc_trend_fails(d) == []

    def test_tous_les_docs_git_propres(self):
        for qid in _vr.list_question_ids():
            packed = load(qid)
            if packed is None or packed.document is None:
                continue
            assert _vr._doc_trend_fails(packed.document) == [], qid

    def test_cites_trend_toujours_dormant(self):
        """Aucune grille git n'utilise cites_trend (le garde reste utile)."""
        for qid in _vr.list_question_ids():
            packed = load(qid)
            assert packed is not None
            for c in packed.rubric.criteria:
                assert c.check != "cites_trend", qid

    def test_trend_hits_semantique_inchangee(self):
        """_trend_hits ne voit QUE le trend déclaré (cites_trend futur)."""
        packed = load("yeast-glucose-interpret")
        assert packed is not None
        d = packed.document
        assert d is not None
        ok, _ = _trend_hits(normalize_arabic("يزداد عدد الخلايا"), d)
        assert ok is True
        ok2, _ = _trend_hits(normalize_arabic("يتناقص العدد"), d)
        assert ok2 is False
