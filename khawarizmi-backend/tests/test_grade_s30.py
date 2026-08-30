"""S30 — enclitiques suffixaux (لأنها = لأن + ها). 1.1.8. Pas de stemming, pas ة→ت."""

from __future__ import annotations

from pathlib import Path

from services.arabic import normalize_arabic
from services.local_grader import (
    GRADER_VERSION,
    _ENCLITICS,
    _PROCLITICS,
    _hit_pos,
    grade,
)
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")


def _n(s: str) -> str:
    return normalize_arabic(s)


class TestEnclitiques:
    def test_cause_avec_enclitique_matche(self):
        """لأنها / لأنه / لاني / لاننا / لانكم = لأن + pronom collé."""
        for w in ("لأنها", "لأنه", "لأني", "لأننا", "لأنكم"):
            assert _hit_pos(_n(w), _n("لأن")) is not None, w

    def test_because_avec_enclitique_matche(self):
        for w in ("بسببها", "بسببه", "بسببهم"):
            assert _hit_pos(_n(w), _n("بسبب")) is not None, w

    def test_combo_proclitique_enclitique(self):
        """و + لأن + ها = ولأنها — un seul match, pas de produit énuméré."""
        for w in ("ولأنها", "ولأنه", "فلأنها"):
            assert _hit_pos(_n(w), _n("لأن")) is not None, w

    def test_non_regressions_frontieres(self):
        assert _hit_pos(_n("لانطلاق"), _n("لان")) is None
        assert _hit_pos(_n("الانزيم"), _n("لان")) is None
        assert _hit_pos(_n("النموذج"), _n("نمو")) is None

    def test_short_copy_does_not_invent_long_needle(self):
        assert _hit_pos(_n("كن"), _n("لكن")) is None

    def test_proclitiques_s29_intacts(self):
        assert _hit_pos(_n("كالخميرة"), _n("خميرة")) is not None
        assert _hit_pos(_n("كالخميرة"), _n("الخميرة")) is not None
        assert _hit_pos(_n("فالخميرة"), _n("خميرة")) is not None

    def test_limite_ta_marbuta_non_gegree(self):
        """خميرة+ها s'écrit خميرتها (ة→ت). Hors liste fermée : pas géré (S30 ≠ stemming)."""
        assert _hit_pos(_n("خميرتها"), _n("خميرة")) is None


class TestGradeEnclitiques:
    def test_modele_avec_lanha_restaure_100(self):
        """F1 (audit 2026-08-30) : 75 % → 100 %. L'élève a écrit la cause."""
        packed = load("yeast-glucose-interpret")
        assert packed is not None
        for w in ("لأنها", "لأنه"):
            copy = packed.rubric.model_answer.replace("لأن", w)
            r = grade(
                student_answer=copy, rubric=packed.rubric, document=packed.document
            )
            assert r.method_percent == 100, f"{w}: {r.method_percent}"
            assert r.diagnosis is not None and r.diagnosis.code == "all_correct"
            cause = next(c for c in r.criteria if c.id == "cause")
            assert cause.status == "full"

    def test_modele_avec_sababaha(self):
        packed = load("yeast-glucose-interpret")
        assert packed is not None
        copy = packed.rubric.model_answer.replace("لأن", "بسببها")
        r = grade(student_answer=copy, rubric=packed.rubric, document=packed.document)
        assert r.method_percent == 100
        cause = next(c for c in r.criteria if c.id == "cause")
        assert cause.status == "full"

    def test_sanity_et_caps_inchanges(self):
        """L'enclitique ne touche ni sanity ni filet : 36 ATP reste cap 40."""
        packed = load("yeast-glucose-interpret")
        assert packed is not None
        copy = packed.rubric.model_answer.replace("لأن", "لأنها")
        r = grade(
            student_answer=copy + " وتنتج 36 ATP.",
            rubric=packed.rubric,
            document=packed.document,
        )
        assert r.science_status == "error"
        assert r.overall_training_percent <= 40
        assert r.method_percent == 100  # l'axe méthode reste honest


class TestContratFerme:
    def test_version_et_listes(self):
        assert GRADER_VERSION == "1.1.8"
        assert 'GRADER_VERSION = "1.1.8"' in GRADER
        assert "ها" in _ENCLITICS and "ه" in _ENCLITICS and "ي" in _ENCLITICS
        assert "ات" not in _ENCLITICS  # pluriel ≠ pronom
        assert "كال" in _PROCLITICS  # S29 intact
        assert "فل" not in _PROCLITICS
        assert "openai" not in GRADER
        assert "evaluate.router" not in INIT
        assert "ai_evaluate.router" not in INIT

    def test_occurrence_count_coherent(self):
        from services.local_grader import _occurrence_count

        text = _n("لأنها كبيرة لأنه صغير لانطلاق")
        assert _occurrence_count(text, [_n("لأن")]) == 2
