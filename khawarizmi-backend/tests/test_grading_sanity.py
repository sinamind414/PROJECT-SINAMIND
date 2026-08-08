"""tests/test_grading_sanity.py — Extraction sanity (audit S2.1b).

- run_sanity : wrapper pur, codes standardisés.
- PARITÉ RÉELLE : le pipeline (avec le VRAI evaluate_answer_v2 comme
  evaluate_legacy) produit le même résultat que l'ancien moteur, sur les cas
  sanity : vide, court, gibberish, répétitions, copie OK.
- precomputed_sanity ne change PAS le comportement du legacy (rétrocompat).
"""

import json
from unittest.mock import MagicMock

import pytest

from grading.pipeline import assert_parity, evaluate_answer_v2_pipeline
from grading.sanity import run_sanity, sanity_tuple
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

# Cas demandés : vide, court, gibberish, répétitions, copie OK
SANITY_CASES = {
    "vide": "",
    "court": "abc",
    "gibberish": "ERRETREZR",
    "repétitions": "بببببببببببببببب",
    "copie_ok": "الاستنساخ يتم في النواة والترجمة في الهيولى",
}

_V1_JSON = {
    "score": 6,
    "matched_criteria": ["تقديم الوثيقة"],
    "unmatched_criteria": [],
    "highlights": [{"start": 0, "end": 5, "type": "good_element",
                    "message_ar": "عنصر صحيح"}],
    "feedback_ar": "إجابة جيدة",
    "advice_ar": "أضف تفاصيل",
    "confidence": 0.85,
}


def _make_llm_mock():
    """Mock LLM retournant du JSON v1 valide (pour la copie OK)."""

    async def mock_llm(**kwargs):
        resp = MagicMock()
        resp.choices = [MagicMock()]
        resp.choices[0].message.content = json.dumps(_V1_JSON, ensure_ascii=False)
        resp.choices[0].finish_reason = "stop"
        resp._khawarizmi_json_mode = False
        resp._khawarizmi_provider = "primary"
        resp._khawarizmi_model = "test"
        return resp

    return mock_llm


def _llm_kwargs():
    return {"llm_call": _make_llm_mock(), "primary_client": MagicMock(),
            "primary_model": "test"}


# ── run_sanity : wrapper pur ─────────────────────────────────────────

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


# ── Parité réelle pipeline == legacy ─────────────────────────────────

class TestParitySanityRealEngine:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("case_name", list(SANITY_CASES))
    async def test_parity_all_cases(self, case_name):
        """Pipeline (vrai moteur en legacy) == moteur seul, pour chaque cas."""
        answer = SANITY_CASES[case_name]
        kwargs = {k: v for k, v in BASE_KWARGS.items()
                  if k not in ("verb_slug", "model_answer", "score_max")}

        # Moteur seul (comportement historique)
        legacy_result = await evaluate_answer_v2(
            **BASE_KWARGS, student_answer=answer, **_llm_kwargs()
        )

        # Pipeline : sanity extraite + legacy avec precomputed_sanity
        out = await evaluate_answer_v2_pipeline(
            question_id=1,
            verb_slug="analyse",
            score_max=8,
            student_answer=answer,
            model_answer=BASE_KWARGS["model_answer"],
            evaluate_legacy=evaluate_answer_v2,
            **kwargs, **_llm_kwargs(),
        )

        assert_parity(out, legacy_result, extra_volatile={"precomputed_sanity"})
        # La source est la même (sanity pour les rejets, llm pour la copie OK)
        assert out["source"] == legacy_result["source"]
        if case_name != "copie_ok":
            assert out["source"] == "sanity"
            assert out["sanity_code"] in {
                "empty", "too_short", "gibberish", "not_arabic", "repeated_chars",
            }

    @pytest.mark.asyncio
    async def test_precomputed_sanity_does_not_change_legacy(self):
        """Rétrocompat : le legacy AVEC precomputed_sanity produit le même
        résultat que SANS (le paramètre est un passe-plat transparent)."""
        for case_name, answer in SANITY_CASES.items():
            without = await evaluate_answer_v2(
                **BASE_KWARGS, student_answer=answer, **_llm_kwargs()
            )
            sanity = run_sanity(answer)
            with_ = await evaluate_answer_v2(
                **BASE_KWARGS, student_answer=answer,
                precomputed_sanity=sanity_tuple(sanity), **_llm_kwargs(),
            )
            assert_parity(with_, without, extra_volatile={"precomputed_sanity"})

    @pytest.mark.asyncio
    async def test_pipeline_circuit_breaks_on_reject(self):
        """S2.1c : sur rejet sanity, le pipeline retourne directement le
        rejet SANS appeler le legacy (court-circuit)."""
        captured = {"called": False}

        async def legacy_spy(**kwargs):
            captured["called"] = True
            return await evaluate_answer_v2(**kwargs)

        out = await evaluate_answer_v2_pipeline(
            question_id=1, verb_slug="analyse", score_max=8,
            student_answer="", model_answer=BASE_KWARGS["model_answer"],
            evaluate_legacy=legacy_spy,
            **{k: v for k, v in BASE_KWARGS.items()
               if k not in ("verb_slug", "model_answer", "score_max")},
            **_llm_kwargs(),
        )
        assert out["source"] == "sanity"
        assert out["sanity_code"] == "empty"
        assert captured["called"] is False

    @pytest.mark.asyncio
    async def test_pipeline_passes_precomputed_sanity_ok(self):
        """Copie valide → le pipeline transmet precomputed=(True,'ok','') au
        legacy (le legacy ne refait pas le calcul)."""
        captured = {}

        async def legacy_spy(**kwargs):
            captured["precomputed_sanity"] = kwargs.get("precomputed_sanity")
            return await evaluate_answer_v2(**kwargs)

        await evaluate_answer_v2_pipeline(
            question_id=1, verb_slug="analyse", score_max=8,
            student_answer="الاستنساخ يتم في النواة",
            model_answer=BASE_KWARGS["model_answer"],
            evaluate_legacy=legacy_spy,
            **{k: v for k, v in BASE_KWARGS.items()
               if k not in ("verb_slug", "model_answer", "score_max")},
            **_llm_kwargs(),
        )
        assert captured["precomputed_sanity"] == (True, "ok", "")
