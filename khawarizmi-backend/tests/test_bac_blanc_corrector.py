"""Barème et priorité scientifique du correcteur Bac blanc."""
import json
from pathlib import Path

from services.bac_blanc_corrector import correct_bac_answer


def _exercise(**overrides):
    base = {
        "exercise_id": "x",
        "title_ar": "تحليل نشاط إنزيم",
        "instruction_ar": "حلل النتائج وفسرها.",
        "context_ar": "تجربة تقيس نشاط إنزيم حسب الحرارة.",
        "verb_slug": "analyse",
        "points": 5,
        "model_answer_ar": "نلاحظ ارتفاع نشاط الإنزيم حتى الدرجة المثلى ثم ينخفض بسبب تمسخ الموقع الفعال.",
    }
    return {**base, **overrides}


def test_score_is_always_on_declared_points():
    result = correct_bac_answer(_exercise(), _exercise()["model_answer_ar"])
    assert 0 <= result["score"] <= 5
    assert result["score_max"] == 5
    assert result["percentage"] == round(result["score"] / 5 * 100)


def test_scientific_error_blocks_methodological_full_mark():
    answer = (
        "الوثيقة تمثل منحنى ونلاحظ أن القيمة تزداد من 2 إلى 8 ثم تبقى ثابتة. "
        "ينتج التنفس الهوائي 36 ATP."
    )
    result = correct_bac_answer(_exercise(), answer)
    assert result["dominant_error_code"] == "scientific_error"
    assert result["percentage"] <= 40


def test_missing_reference_caps_score_at_fifty_percent():
    result = correct_bac_answer(_exercise(model_answer_ar=""), "الوثيقة تمثل منحنى ونلاحظ ارتفاع القيمة تدريجيا")
    assert result["percentage"] <= 50
    assert "لا توجد إجابة مرجعية" in result["feedback"]


def test_seed_subject_totals_cannot_exceed_declared_total():
    seed = Path(__file__).parents[1] / "scripts" / "bac_blanc_seed.json"
    for subject in json.loads(seed.read_text(encoding="utf-8")):
        total_score = 0
        total_max = 0
        for exercise in subject["exercises"]:
            result = correct_bac_answer(exercise, exercise.get("model_answer_ar", ""))
            total_score += result["score"]
            total_max += result["score_max"]
        assert total_max == sum(int(exercise["points"]) for exercise in subject["exercises"])
        assert 0 <= total_score <= total_max
