"""Tests G1–G8 / G12–G15 du correcteur local (0 LLM)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from services.local_grader import (
    GRADER_VERSION,
    TRAINING_BANNER_AR,
    UngradedError,
    grade,
    grade_question,
)
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent
GRADER_SRC = BACKEND / "services" / "local_grader.py"


def _yeast():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    return packed


class TestG1NoGenerativeImports:
    def test_ast_forbids_openai_llm_pipeline(self):
        tree = ast.parse(GRADER_SRC.read_text(encoding="utf-8"))
        banned = {"openai", "llm", "pipeline", "fallback_v2", "evaluate"}
        found: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in banned or alias.name in banned:
                        found.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                root = mod.split(".")[0]
                if root in banned or any(part in banned for part in mod.split(".")):
                    found.add(mod)
        assert not found, f"imports interdits dans local_grader: {found}"


class TestG2Deterministe:
    def test_same_copy_three_calls(self):
        p = _yeast()
        copies = [
            grade(student_answer=p.rubric.model_answer, rubric=p.rubric, document=p.document)
            for _ in range(3)
        ]
        dumped = [c.model_dump() for c in copies]
        assert dumped[0] == dumped[1] == dumped[2]
        assert copies[0].grader_version == GRADER_VERSION


class TestG3VerbSlipAnalyse:
    def test_lian_is_forbidden_and_slip(self):
        p = _yeast()
        copy = (
            "تمثل الوثيقة جدولا. يزداد العدد من 9 إلى 18. "
            "كلما تواجد الغلوكوز تزايد عدد الخلايا لأن الخميرة تتنفس. "
            "نستنتج أن الغلوكوز عنصر ضروري لنمو الخميرة."
        )
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        no_cause = next(h for h in r.criteria if h.id == "no_cause")
        assert no_cause.status == "absent"
        assert r.diagnosis is not None
        assert r.diagnosis.code == "verb_slip.interpret"


class TestG4ScienceCap:
    def test_36_atp_caps_overall(self):
        p = _yeast()
        copy = p.rubric.model_answer + " وتنتج الخلية 36 ATP في التنفس."
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        assert r.science_status == "error"
        assert r.science_capped
        assert r.overall_training_percent <= 40
        assert r.method_percent >= 85


class TestG5ModelAnswer:
    def test_yeast_model_ge_85(self):
        p = _yeast()
        r = grade(
            student_answer=p.rubric.model_answer, rubric=p.rubric, document=p.document
        )
        assert r.method_percent >= 85, [(h.id, h.status) for h in r.criteria]
        assert r.science_status == "ok"


class TestG6Stuffing:
    def test_lexicon_dump_without_document(self):
        p = _yeast()
        copy = " ".join(["خميرة", "غلوكوز", "تكاثر"] * 12)
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        assert r.stuffing_suspected
        assert r.overall_training_percent <= 50
        assert "stuffing" in r.caps_applied

    def test_g6b_short_correct_not_stuffing(self):
        p = _yeast()
        copy = "الوثيقة تظهر 18 خلية مع الغلوكوز."
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        assert r.sanity_code in ("ok", "too_short")
        if r.sanity_code == "ok":
            assert r.stuffing_suspected is False


class TestG7DeferChemistry:
    def test_latin_atp_is_defer_not_not_arabic_stop(self):
        p = _yeast()
        r = grade(student_answer="38 ATP · P/O=3", rubric=p.rubric, document=p.document)
        assert r.sanity_code == "defer"
        assert r.science_status != "not_applicable" or r.method_percent >= 0
        # on a CONTINUÉ : cacheable False
        assert r.cacheable is False


class TestN1NumericDumpStops:
    """Hotfix N1 : digits ≠ chimie. Dump sans arabe → 0, pas 38 %."""

    DUMP = "1 2 3 4 5 6 7 8 9 10 20 37 80 100 0 2,5 4,8 18 6 10 5"

    @pytest.mark.parametrize(
        "qid",
        [
            "enzyme-temp-analyse",
            "manhadjiya-yeast-analyse",
            "greffe-ltc-analyse",
            "photo-o2-analyse",
        ],
    )
    def test_number_salad_is_not_arabic_zero(self, qid: str):
        r = grade_question(qid, self.DUMP)
        assert r.sanity_code == "not_arabic"
        assert r.method_percent == 0
        assert r.method_points == 0
        assert r.overall_training_percent == 0
        assert r.science_status == "not_applicable"
        assert r.cacheable is False

    def test_digits_alone_do_not_count_as_chemistry(self):
        from services.local_grader import _chemistry_signal_count

        assert _chemistry_signal_count(self.DUMP) == 0
        assert _chemistry_signal_count("38 ATP · P/O=3") >= 2


class TestN2ArabicDecimalKeypoint:
    def test_arabic_decimal_matches_greffe_25(self):
        packed = load("greffe-ltc-analyse")
        assert packed is not None
        copy = "تمثل الوثيقة منحنى رفض الطعم. القيمة ٢٫٥ بعد أيام."
        r = grade(student_answer=copy, rubric=packed.rubric, document=packed.document)
        kp = next(h for h in r.criteria if h.id == "keypoint")
        assert kp.status == "full"


class TestG8Ungraded:
    def test_unknown_question_raises(self):
        with pytest.raises(UngradedError) as ei:
            grade_question("question-qui-nexiste-pas", "نلاحظ أن الغلوكوز يزداد في الوثيقة")
        assert ei.value.question_id == "question-qui-nexiste-pas"


class TestG12Banner:
    def test_banner_exists_and_percent_not_glued_to_bac(self):
        assert "تدريبية" in TRAINING_BANNER_AR
        assert "بكالوريا" in TRAINING_BANNER_AR
        p = _yeast()
        r = grade(
            student_answer=p.rubric.model_answer, rubric=p.rubric, document=p.document
        )
        blob = f"{r.method_percent}%{r.phrase_ar}{r.method_label_ar}"
        assert "بكالوريا" not in blob


class TestG13OffTopic:
    def test_geology_on_yeast(self):
        p = _yeast()
        copy = (
            "تمثل الوثيقة منحنى تباعد الصفائح عند الذروة الوسطى. "
            "كلما ابتعدت الصفيحة ازداد الخندق. نستنتج غوص اللوح."
        )
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        assert r.science_status == "error"
        assert r.diagnosis is not None
        assert r.diagnosis.code == "off_topic"


class TestG14FakeNumber:
    def test_one_does_not_anchor(self):
        p = _yeast()
        copy = (
            "تمثل الوثيقة جدولا. العدد يساوي 1 فقط. "
            "كلما تواجد شيء تزايد شيء. نستنتج أن الغلوكوز عنصر ضروري لنمو الخميرة."
        )
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        kp = next(h for h in r.criteria if h.id == "keypoint")
        assert kp.status == "absent"


class TestG15Disorder:
    def test_all_steps_out_of_order(self):
        p = _yeast()
        copy = (
            "نستنتج أن الغلوكوز عنصر ضروري لنمو وتكاثر فطر الخميرة. "
            "تمثل الوثيقة جدولا يوضح تغيرات عدد خلايا الخميرة. "
            "يزداد العدد من 9 إلى 18 خلية. "
            "فكلما تواجد الغلوكوز تزايد عدد الخلايا."
        )
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        assert r.method_percent >= 85
        assert r.order_ok is False
        assert r.method_label_ar != "متقن"


class TestSanityStops:
    def test_empty(self):
        p = _yeast()
        r = grade(student_answer="   ", rubric=p.rubric, document=p.document)
        assert r.sanity_code == "empty"
        assert r.method_percent == 0
        assert r.science_status == "not_applicable"

    def test_schematiser_no_auto_score(self):
        from schemas.rubric import Criterion, Rubric

        rub = Rubric(
            rubric_id="schema-x",
            version="1.0.0",
            verb_slug="schematiser",
            chapter_slug="x",
            total_points=1.0,
            criteria=[
                Criterion(id="a", label_ar="x", points=1.0, check="any_of", variants=["x"])
            ],
        )
        r = grade(student_answer="رسم", rubric=rub, document=None)
        assert r.diagnosis is not None
        assert r.diagnosis.code == "schematiser_manual"
        assert r.method_points == 0


class TestErratumDalil10e4:
    """دليل p.25 : 10⁶ livre → 10⁴ vérité. Jaune, pas cap 40."""

    def test_book_typo_arnr_is_warn_not_cap(self):
        p = _yeast()
        copy = (
            p.rubric.model_answer
            + " الوزن الجزيئي لـ ARNr 5S يساوي 3.6×10^6 ."
        )
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        assert r.science_status == "ok"
        assert r.science_capped is False
        assert r.overall_training_percent == r.method_percent
        assert r.method_percent >= 85
        assert any("10⁴" in f or "10^4" in f or "تصويب الدليل" in f for f in r.science_flags)
        assert r.diagnosis is not None
        assert r.diagnosis.code == "science.erratum"

    def test_correct_1e4_is_silent(self):
        p = _yeast()
        copy = (
            p.rubric.model_answer
            + " الوزن الجزيئي لـ ARNr 5S يساوي 3.6×10^4 ."
        )
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        assert r.science_status == "ok"
        assert not any("تصويب الدليل" in f for f in r.science_flags)
        assert r.diagnosis is not None
        assert r.diagnosis.code != "science.erratum"

    def test_1e6_without_arn_context_silent(self):
        p = _yeast()
        copy = p.rubric.model_answer + " القيمة 3.6×10^6 ليست كتلة ARNm هنا."
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        assert r.science_status == "ok"
        assert not any("تصويب الدليل" in f for f in r.science_flags)

    def test_arnt_book_typo(self):
        p = _yeast()
        copy = p.rubric.model_answer + " ARNt : 2.5×10^6 ."
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        assert r.science_status == "ok"
        assert r.science_capped is False
        assert any("ARNt" in f for f in r.science_flags)
