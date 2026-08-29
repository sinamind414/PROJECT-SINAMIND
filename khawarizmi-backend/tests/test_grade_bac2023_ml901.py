"""L1 — Bac 2023 S1 ex.2 Q2 حلّل (ML901 ترجمة). Chiffres سلم seulement. 0 graphe inventé."""

from __future__ import annotations

from services.local_grader import grade
from services.rubric_store import load

QID = "bac2023-s1-ex2-analyse-traduction"


def _p():
    packed = load(QID)
    assert packed is not None
    assert packed.document is not None
    return packed


def test_keypoints_are_only_salam_numbers():
    vals = sorted(k.value for k in _p().document.keypoints)
    assert vals == [1.5, 5.0, 100.0]


def test_model_is_mastered_science_ok():
    p = _p()
    r = grade(student_answer=p.rubric.model_answer, rubric=p.rubric, document=p.document)
    assert r.method_percent >= 85
    assert r.science_status == "ok"
    assert r.method_label_ar == "متقن"
    assert r.diagnosis is not None
    assert r.diagnosis.code == "all_correct"


def test_kullama_not_required():
    """سلم 2023: ثابتة / تتناقص — pas كلما inventé."""
    p = _p()
    copy = (
        "تمثل الوثيقة منحنيين. الاستنساخ ثابتة عند 100. "
        "الترجمة تتناقص حتى تنعدم عند 5. نستنتج أن الدواء يثبط الترجمة."
    )
    r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
    rel = next(h for h in r.criteria if h.id == "relation")
    assert rel.status == "full"
    assert r.method_percent >= 85
    assert r.science_status == "ok"


def test_arabic_decimal_15_anchors():
    p = _p()
    copy = "تمثل المنحنى نسبة الترجمة عند ١٫٥ ثم تنعدم. نستنتج أن الدواء يثبط الترجمة."
    r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
    kp = next(h for h in r.criteria if h.id == "keypoint")
    assert kp.status == "full"


def test_inhibits_transcription_is_grave():
    p = _p()
    r = grade(
        student_answer=p.rubric.model_answer + " إذن يثبط الاستنساخ.",
        rubric=p.rubric,
        document=p.document,
    )
    assert r.science_status == "error"
    assert r.overall_training_percent <= 40
    assert "science" in r.caps_applied


def test_lian_is_verb_slip_not_bac_20():
    p = _p()
    copy = p.rubric.model_answer.replace(
        "نستنتج أن الدواء يثبط الترجمة.",
        "لأن الدواء يثبط الترجمة. نستنتج أن الدواء يثبط الترجمة.",
    )
    r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
    assert r.diagnosis is not None
    assert r.diagnosis.code == "verb_slip.interpret"
    no_cause = next(h for h in r.criteria if h.id == "no_cause")
    assert no_cause.status == "absent"


def test_not_a_bac_official_score():
    p = _p()
    r = grade(student_answer=p.rubric.model_answer, rubric=p.rubric, document=p.document)
    assert r.method_points_max == 4.0
    assert "بكالوريا" not in (r.phrase_ar or "")
