"""tests/test_grading_sanity.py — Extraction sanity (audit S2.1b, S2.1f).

- run_sanity : wrapper pur, codes standardisés.
- Le PIPELINE (S2.1f : logique complète) rejette les copies invalides avec
  le format historique (build_sanity_result) et court-circuite AVANT l'appel
  LLM ; la copie OK passe au LLM.
- precomputed_sanity (S2.1b) : rétrocompat — même résultat avec ou sans.
"""

import json
from unittest.mock import MagicMock

import pytest

from grading.pipeline import assert_parity, evaluate_answer_v2_pipeline
from grading.sanity import run_sanity, sanity_tuple

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

# Cas demandés : vide, court, gibberish, répétitions, copie OK
SANITY_CASES = {
    "vide": "",
    "court": "abc",
    "gibberish": "ERRETREZR",
    "repétitions": "بببببببببببببببب",
    "copie_ok": "الاستنساخ يتم في النواة والترجمة في الهيولى",
}


def _llm_factory(llm_called: dict):
    """Crée un llm_call mocké (JSON v1) qui compte ses appels."""

    async def llm_mock(**kwargs):
        llm_called["n"] += 1
        resp = MagicMock()
        resp.choices = [MagicMock()]
        resp.choices[0].message.content = json.dumps({
            "score": 6, "matched_criteria": [], "unmatched_criteria": [],
            "highlights": [], "feedback_ar": "f", "advice_ar": "",
            "confidence": 0.8,
        }, ensure_ascii=False)
        resp.choices[0].finish_reason = "stop"
        resp._khawarizmi_provider = "primary"
        resp._khawarizmi_model = "test"
        return resp

    return llm_mock


async def _run(llm_mock, answer: str, **overrides) -> dict:
    kwargs = {k: v for k, v in BASE_KWARGS.items()
              if k not in ("verb_slug", "model_answer", "score_max")}
    kwargs.update(overrides)
    return await evaluate_answer_v2_pipeline(
        question_id=1, verb_slug="analyse", score_max=8,
        student_answer=answer, model_answer=BASE_KWARGS["model_answer"],
        llm_call=llm_mock, primary_client=MagicMock(), primary_model="test",
        **kwargs,
    )


class TestRunSanity:
    @pytest.mark.parametrize("case,expected_code", [
        ("", "empty"),
        ("abc", "too_short"),
        ("ERRETREZR", "gibberish"),  # keyboard smash détecté avant le ratio arabe
        ("بببببببببببببببب", "repeated_chars"),
    ])
    def test_reject_codes(self, case, expected_code):
        r = run_sanity(case)
        assert r["is_valid"] is False
        assert r["sanity_code"] == expected_code
        assert isinstance(r["message_ar"], str)

    def test_valid_copy(self):
        r = run_sanity("الاستنساخ يتم في النواة والترجمة في الهيولى")
        assert r == {"is_valid": True, "sanity_code": "ok", "message_ar": ""}

    def test_sanity_tuple_roundtrip(self):
        r = run_sanity("")
        assert sanity_tuple(r) == (False, "empty", r["message_ar"])


class TestPipelineSanity:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("case_name", list(SANITY_CASES))
    async def test_reject_or_pass_like_legacy(self, case_name):
        """Le pipeline rejette les copies invalides (format build_sanity_result)
        et laisse passer la copie OK (appel LLM)."""
        answer = SANITY_CASES[case_name]
        llm_called = {"n": 0}
        out = await _run(_llm_factory(llm_called), answer)

        if case_name == "copie_ok":
            assert out["source"] == "llm"
            assert llm_called["n"] == 1
        else:
            assert out["source"] == "sanity"
            assert out["sanity_code"] in {
                "empty", "too_short", "gibberish", "not_arabic", "repeated_chars",
            }
            assert out["score"] == 0
            assert llm_called["n"] == 0  # court-circuit avant l'appel LLM

    @pytest.mark.asyncio
    async def test_precomputed_sanity_does_not_change_result(self):
        """precomputed_sanity (S2.1b) : rétrocompat — même résultat avec ou
        sans (le paramètre est absorbé par le pipeline)."""
        for answer in SANITY_CASES.values():
            llm_called = {"n": 0}
            without = await _run(_llm_factory(llm_called), answer)
            sanity = run_sanity(answer)
            with_ = await _run(_llm_factory(llm_called), answer,
                               precomputed_sanity=sanity_tuple(sanity))
            assert_parity(with_, without, extra_volatile={"precomputed_sanity"})

    @pytest.mark.asyncio
    async def test_reject_never_calls_llm(self):
        """Preuve du court-circuit : 3 rejets successifs → 0 appel LLM."""
        llm_called = {"n": 0}
        for answer in ("", "abc", "ERRETREZR"):
            await _run(_llm_factory(llm_called), answer)
        assert llm_called["n"] == 0

    @pytest.mark.asyncio
    async def test_valid_copy_calls_llm_once(self):
        llm_called = {"n": 0}
        await _run(_llm_factory(llm_called), "الاستنساخ يتم في النواة والترجمة في الهيولى")
        assert llm_called["n"] == 1
