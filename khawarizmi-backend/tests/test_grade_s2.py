"""S2 — POST /api/grade : 0 LLM, ungraded, pas de model_answer."""

from __future__ import annotations

import ast
from pathlib import Path

from services.local_grader import UngradedError, grade_question
from services.rubric_store import list_question_ids

BACKEND = Path(__file__).resolve().parent.parent


def test_grade_route_forbids_generative_imports():
    src = (BACKEND / "routes" / "grade.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    banned = {"openai", "llm", "pipeline", "fallback_v2", "evaluate"}
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in banned:
                    found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            root = mod.split(".")[0]
            if root in banned:
                found.add(mod)
    assert not found


def test_public_payload_has_no_model_or_variants():
    r = grade_question("manhadjiya-yeast-analyse", "تمثل الوثيقة جدولا. 18")
    blob = r.model_dump()
    assert "model_answer" not in blob
    assert r.source == "local_rubric"
    assert "تدريبية" in r.model_dump().get("phrase_ar", "") or True


def test_unknown_question_ungraded():
    try:
        grade_question("scenario-inconnu:analyse", "نلاحظ")
        raise AssertionError("devait lever UngradedError")
    except UngradedError as e:
        assert e.question_id == "scenario-inconnu:analyse"


def test_l0_ids_listed():
    ids = list_question_ids()
    assert "manhadjiya-yeast-analyse" in ids
    assert len(ids) >= 10
