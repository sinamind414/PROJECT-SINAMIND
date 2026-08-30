"""S4 — G11 GET /correction, persist hash, FSRS science/<10."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from services.grade_adapter import may_write_fsrs

BACKEND = Path(__file__).resolve().parent.parent
DA_SRC = (BACKEND / "routes" / "document_analysis.py").read_text(encoding="utf-8")
BAC_SRC = (BACKEND / "routes" / "bac_blanc.py").read_text(encoding="utf-8")
GRADE_SRC = (BACKEND / "routes" / "grade.py").read_text(encoding="utf-8")


def test_g11_da_correction_requires_own_eval():
    assert "JOIN da_answers" in DA_SRC
    assert "sess.user_id = :uid" in DA_SRC
    assert "Correction indisponible" in DA_SRC
    assert "async def correction_scenario" in DA_SRC


def test_da_v1_persists_hash_not_plaintext():
    assert "hash_answer(ans.answer)" in DA_SRC
    assert '"answer_text": ans.answer' not in DA_SRC
    assert "from services.hashing import hash_answer" in DA_SRC


def test_da_evaluate_does_not_load_model_answer():
    """Évaluer ne lit plus model_answer_ar (fuite / tentation de fallback)."""
    assert "SELECT id, verb_slug FROM da_questions" in DA_SRC
    assert "SELECT id, verb_slug, model_answer_ar FROM da_questions" not in DA_SRC


def test_bac_submit_hashes_then_get_hides_copy():
    assert "hash_answer(answer_text)" in BAC_SRC
    assert "student_answer=\"\"" in BAC_SRC or "student_answer=''," in BAC_SRC


def test_grade_route_does_not_persist_copy():
    """P7 : grade() / routes/grade.py n'écrivent pas la copie."""
    assert "hash_answer" not in GRADE_SRC
    assert "INSERT INTO da_answers" not in GRADE_SRC


def test_may_write_fsrs_blocks_sanity_low_and_capped_mastery():
    assert not may_write_fsrs(
        SimpleNamespace(sanity_code="empty", method_percent=0, science_status="not_applicable")
    )
    assert not may_write_fsrs(
        SimpleNamespace(sanity_code="ok", method_percent=5, science_status="ok")
    )
    assert not may_write_fsrs(
        SimpleNamespace(sanity_code="ok", method_percent=90, science_status="error")
    )
    assert may_write_fsrs(
        SimpleNamespace(sanity_code="ok", method_percent=70, science_status="ok")
    )
    assert may_write_fsrs(
        SimpleNamespace(sanity_code="ok", method_percent=40, science_status="error")
    )
