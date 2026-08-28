"""S20 — counter_examples manuscrits L0. Gate négatif auteur. Jamais GET rubric."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from services.local_grader import GRADER_VERSION
from services.rubric_store import data_dir, list_question_ids, load

BACKEND = Path(__file__).resolve().parent.parent
ROUTE = (BACKEND / "routes" / "grade.py").read_text(encoding="utf-8")
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
VAL = (BACKEND / "scripts" / "validate_rubrics.py").read_text(encoding="utf-8")
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")
SCHEMA = (BACKEND / "schemas" / "rubric.py").read_text(encoding="utf-8")


def _mod():
    spec = importlib.util.spec_from_file_location(
        "validate_rubrics_s20", BACKEND / "scripts" / "validate_rubrics.py"
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_each_l0_has_two_counters_including_off_topic():
    ids = list_question_ids()
    assert len(ids) >= 10
    for qid in ids:
        packed = load(qid)
        assert packed is not None
        raw = json.loads((data_dir() / packed.rubric_path).read_text(encoding="utf-8"))
        ex = raw.get("counter_examples")
        assert isinstance(ex, list) and len(ex) >= 2, qid
        assert any(x.get("id") == "off_topic" for x in ex), qid
        assert all(x.get("axis") in ("overall", "method") for x in ex), qid


def test_counters_not_on_rubric_model_or_get():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    assert not hasattr(packed.rubric, "counter_examples") or not getattr(
        packed.rubric, "counter_examples", None
    )
    assert "counter_examples" not in packed.rubric.model_dump()
    assert '"counter_examples"' not in ROUTE.split("return {")[-1]
    public_keys = (
        "rubric_id",
        "version",
        "verb_slug",
        "total_points",
        "criteria",
        "method_graph_steps",
        "banner_ar",
    )
    for k in public_keys:
        assert k in ROUTE
    assert "model_answer" not in ROUTE.split("return {")[-1]


def test_validate_runs_counters():
    assert "_check_counter_examples" in VAL
    assert "off_topic" in VAL
    assert "model+atp36" in VAL
    mod = _mod()
    for qid in list_question_ids():
        fails = mod.check_question(qid)
        assert fails == [], fails


def test_grader_and_schema_untouched():
    assert "counter_examples" not in GRADER
    assert "counter_examples" not in SCHEMA
    assert GRADER_VERSION == "1.1.5"
    assert "openai" not in GRADER
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT
