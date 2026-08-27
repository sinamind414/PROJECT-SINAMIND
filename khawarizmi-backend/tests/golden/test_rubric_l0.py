"""Golden L0 : 10 grilles × copies types (vide, modèle, partielle, science, hors-sujet…)."""

from __future__ import annotations

import pytest

from services.local_grader import grade
from services.rubric_store import list_question_ids, load

GEOLOGY = (
    "تمثل الوثيقة منحنى تباعد الصفائح عند الأعراف المحيطية. "
    "كلما ابتعدت الصفيحة ازداد الخندق المحيطي. نستنتج غوص اللوح في الاندساس."
)

ATP36 = " وتنتج الخلية 36 ATP في التنفس الهوائي."


def _ids() -> list[str]:
    return list_question_ids()


@pytest.mark.parametrize("qid", _ids())
def test_empty_is_zero(qid: str):
    packed = load(qid)
    assert packed is not None
    r = grade(student_answer="", rubric=packed.rubric, document=packed.document)
    assert r.method_percent == 0
    assert r.sanity_code == "empty"


@pytest.mark.parametrize("qid", _ids())
def test_model_ge_85_science_ok(qid: str):
    packed = load(qid)
    assert packed is not None
    r = grade(
        student_answer=packed.rubric.model_answer,
        rubric=packed.rubric,
        document=packed.document,
    )
    assert r.method_percent >= 85, [(h.id, h.status, h.points_earned) for h in r.criteria]
    assert r.science_status == "ok"


@pytest.mark.parametrize("qid", _ids())
def test_partial_below_model(qid: str):
    packed = load(qid)
    assert packed is not None
    model = packed.rubric.model_answer.strip()
    cut = model.split("。")[0] if "。" in model else model[: max(40, len(model) // 3)]
    r = grade(student_answer=cut, rubric=packed.rubric, document=packed.document)
    full = grade(
        student_answer=model, rubric=packed.rubric, document=packed.document
    )
    if r.sanity_code not in ("ok", "defer"):
        assert r.method_percent == 0
        return
    assert r.method_percent <= full.method_percent


@pytest.mark.parametrize("qid", _ids())
def test_36_atp_science_error(qid: str):
    packed = load(qid)
    assert packed is not None
    r = grade(
        student_answer=packed.rubric.model_answer + ATP36,
        rubric=packed.rubric,
        document=packed.document,
    )
    assert r.science_status == "error"
    assert r.overall_training_percent <= 40


@pytest.mark.parametrize("qid", _ids())
def test_off_topic_geology(qid: str):
    packed = load(qid)
    assert packed is not None
    r = grade(student_answer=GEOLOGY, rubric=packed.rubric, document=packed.document)
    assert r.science_status == "error"
    assert r.diagnosis is not None
    assert r.diagnosis.code in ("off_topic", "science.grave")


@pytest.mark.parametrize("qid", _ids())
def test_stuffing_theme_repeat(qid: str):
    packed = load(qid)
    assert packed is not None
    seeds = [v for v in packed.rubric.theme_variants if not v.startswith("$lex:")]
    if not seeds:
        pytest.skip("pas de theme littéral")
    copy = " ".join(seeds[:3] * 10)
    r = grade(student_answer=copy, rubric=packed.rubric, document=packed.document)
    if r.sanity_code not in ("ok", "defer"):
        pytest.skip("sanity a coupé une copie courte")
    assert r.stuffing_suspected or r.method_percent <= 50 or r.science_status == "error"


def test_analyse_verb_slip_on_yeast():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    copy = packed.rubric.model_answer.replace(
        "فكلما تواجد الغلوكوز تزايد عدد الخلايا والعكس صحيح.",
        "فكلما تواجد الغلوكوز تزايد عدد الخلايا لأن الخميرة تتنفس.",
    )
    r = grade(student_answer=copy, rubric=packed.rubric, document=packed.document)
    assert r.diagnosis is not None
    assert r.diagnosis.code == "verb_slip.interpret"


def test_interpret_verb_slip_kullama_without_cause():
    packed = load("yeast-glucose-interpret")
    assert packed is not None
    copy = (
        "كلما زاد الغلوكوز زاد عدد الخميرة إلى 18 خلية مقابل 6 "
        "والنمو والتكاثر يزيد مادة أيض بدون رابط سببي مكتوب."
    )
    r = grade(student_answer=copy, rubric=packed.rubric, document=packed.document)
    assert r.diagnosis is not None
    assert r.diagnosis.code == "verb_slip.analyse"


def test_disorder_yeast_not_mastered():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    copy = (
        "نستنتج أن الغلوكوز عنصر ضروري لنمو وتكاثر فطر الخميرة. "
        "تمثل الوثيقة جدولا. يزداد العدد من 9 إلى 18. "
        "فكلما تواجد الغلوكوز تزايد عدد الخلايا."
    )
    r = grade(student_answer=copy, rubric=packed.rubric, document=packed.document)
    assert r.order_ok is False
    assert r.method_label_ar != "متقن"
