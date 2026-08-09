"""tests/test_grading_l2.py — Extraction L2 (audit S2.1d).

- run_l2 : évaluation locale fidèle à l'original (concepts depuis
  skill+modèle, redistribution des poids si embedder fallback, format v2).
- PARITÉ : le monolithe (evaluate_answer_v2, local_fallback=True, LLM en
  panne) passe par run_l2 — résultat identique à l'appel direct.
- None sur échec (l'appelant construit un llm_error).
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from grading.l2 import run_l2
from services.correction_v2 import evaluate_answer_v2

BASE_KWARGS = {
    "scenario_context": "دراسة تأثير التغذية على نسبة الغلوكوز",
    "documents": [{"title": "وثيقة 1", "caption": "منحنى", "data": None}],
    "question_prompt": "حلّل الوثيقة 1",
    "question_skill": "تحليل وثيقة",
    "verb_slug": "analyse",
    "model_answer": "نلاحظ من الوثيقة أن نسبة الغلوكوز تزداد من 0.8 إلى 1.4 غ/ل",
    "learning_focus": "التنظيم الهرموني",
    "score_max": 8,
}

ANS = "نلاحظ ارتفاع نسبة الغلوكوز بعد الوجبة ثم انخفاضها"


def _fake_l2_result(*, score_final=0.6, coverage=0.5, structural=0.7,
                    trouve=("غلوكوز",), manquant=("الغلوكوز",),
                    feedback="إجابة جزئية"):
    return SimpleNamespace(
        score_final=score_final,
        semantic_score=0.5,
        coverage_score=coverage,
        structural_score=structural,
        concepts_trouves=list(trouve),
        concepts_manquants=list(manquant),
        verdict="partiel",
        feedback_fallback=feedback,
        needs_l1_review=False,
    )


def _patch_l2(fake_result):
    """Mocke services.fallback_v2.evaluate_l2 (importé dans run_l2)."""
    return patch("services.fallback_v2.evaluate_l2",
                 new=AsyncMock(return_value=fake_result))


def _patch_embedder(is_fallback: bool):
    emb = MagicMock()
    emb.is_fallback = is_fallback
    return patch("services.embedder.get_embedder", return_value=emb)


# ── Tests unitaires run_l2 ───────────────────────────────────────────

class TestRunL2:
    @pytest.mark.asyncio
    async def test_basic_result_format(self):
        with _patch_l2(_fake_l2_result()), _patch_embedder(False):
            r = await run_l2(student_answer=ANS, model_answer=BASE_KWARGS["model_answer"],
                             question_skill="تحليل وثيقة", score_max=8, db=None)
        assert r is not None
        assert r["source"] == "local"
        assert r["parse_status"] == "local_fallback"
        assert r["model"] == "fallback_l2"
        assert r["provider"] == "local"
        assert r["confidence"] == 0.6
        assert r["finish_reason"] == "local"
        assert r["sanity_code"] == "ok"
        assert r["score_max"] == 8
        assert 0 <= r["score"] <= 8
        assert r["percentage"] == round(r["score"] / 8 * 100)
        assert r["matched_criteria"] == ["غلوكوز"]
        assert r["unmatched_criteria"][0]["criterion"] == "الغلوكوز"
        assert r["missing"][0]["expected"] == "الغلوكوز"
        assert r["success"] == ["غلوكوز"]
        assert r["errors"] == ["الغلوكوز"]
        assert r["remediation"] is None
        assert r["student_answer_hash"]  # hash RGPD présent
        assert r["llm_raw_hash"] is None

    @pytest.mark.asyncio
    async def test_score_uses_final_when_embedder_real(self):
        """Embedder réel (is_fallback=False) → score = score_final."""
        with _patch_l2(_fake_l2_result(score_final=0.625)), _patch_embedder(False):
            r = await run_l2(student_answer=ANS, model_answer="m",
                             question_skill="", score_max=8, db=None)
        assert r["score"] == 5  # round(0.625 * 8)

    @pytest.mark.asyncio
    async def test_score_redistributed_when_embedder_fallback(self):
        """Embedder fallback (CI sans ONNX) → redistribution TF-IDF + struct."""
        with _patch_l2(_fake_l2_result(score_final=0.1, coverage=0.5,
                                       structural=0.9)), _patch_embedder(True):
            r = await run_l2(student_answer=ANS, model_answer="m",
                             question_skill="", score_max=8, db=None)
        # final = (0.25*0.5 + 0.35*0.9) / (0.25+0.35) = (0.125+0.315)/0.6 = 0.7333
        assert r["score"] == round(0.7333 * 8)

    @pytest.mark.asyncio
    async def test_dominant_error_codes(self):
        for score_final, expected in [(1.0, "all_correct"),
                                      (0.5, "partial_correct"),
                                      (0.0, "insufficient")]:
            with _patch_l2(_fake_l2_result(score_final=score_final)), _patch_embedder(False):
                r = await run_l2(student_answer=ANS, model_answer="m",
                                 question_skill="", score_max=4, db=None)
            assert r["dominant_error_code"] == expected, score_final

    @pytest.mark.asyncio
    async def test_returns_none_on_failure(self):
        with patch("services.fallback_v2.evaluate_l2",
                   new=AsyncMock(side_effect=RuntimeError("boom"))), _patch_embedder(False):
            r = await run_l2(student_answer=ANS, model_answer="m",
                             question_skill="", score_max=4, db=None)
        assert r is None

    @pytest.mark.asyncio
    async def test_concepts_from_skill_and_model(self):
        """Les concepts requis incluent le skill + mots significatifs."""
        captured = {}

        async def fake_evaluate_l2(**kwargs):
            captured.update(kwargs)
            return _fake_l2_result()

        with patch("services.fallback_v2.evaluate_l2",
                   new=AsyncMock(side_effect=fake_evaluate_l2)), _patch_embedder(False):
            await run_l2(student_answer=ANS,
                         model_answer="الغلوكوز يرتفع في الدم بعد الوجبة",
                         question_skill="تحليل وثيقة", score_max=8, db=None)

        qd = captured["question_data"]
        assert qd["reponse_attendue"] == "الغلوكوز يرتفع في الدم بعد الوجبة"
        assert "تحليل وثيقة" in qd["concepts_requis"]
        assert "الغلوكوز" in qd["concepts_requis"]
        assert len(qd["concepts_requis"]) <= 10
        assert captured["reponse_eleve"] == ANS
        assert captured["db"] is None


# ── Parité : le monolithe passe par run_l2 ───────────────────────────

class TestLegacyDelegation:
    @pytest.mark.asyncio
    async def test_evaluate_answer_v2_local_fallback_matches_run_l2(self):
        """evaluate_answer_v2 (LLM en panne + local_fallback) produit le même
        résultat que run_l2 appelé directement (la délégation est fidèle)."""
        async def llm_down(**kwargs):
            from services.llm_guard import LLMDisabledError
            raise LLMDisabledError("chat.completions.create (external LLM disabled)")

        # Résultat via le monolithe (chemin prod : délègue à run_l2)
        via_legacy = await evaluate_answer_v2(
            **BASE_KWARGS, student_answer=ANS, llm_call=llm_down,
            primary_client=MagicMock(), primary_model="test",
            local_fallback=True, local_fallback_db=None,
        )
        # Résultat via run_l2 direct
        direct = await run_l2(
            student_answer=ANS, model_answer=BASE_KWARGS["model_answer"],
            question_skill=BASE_KWARGS["question_skill"],
            score_max=BASE_KWARGS["score_max"], db=None,
        )

        assert via_legacy["source"] == "local"
        assert direct is not None
        assert via_legacy == direct

    @pytest.mark.asyncio
    async def test_local_fallback_off_keeps_llm_error(self):
        """Sans local_fallback → llm_error (comportement historique conservé)."""
        async def llm_down(**kwargs):
            from services.llm_guard import LLMDisabledError
            raise LLMDisabledError("chat.completions.create (external LLM disabled)")

        result = await evaluate_answer_v2(
            **BASE_KWARGS, student_answer=ANS, llm_call=llm_down,
            primary_client=MagicMock(), primary_model="test",
        )
        assert result["source"] == "llm_error"
