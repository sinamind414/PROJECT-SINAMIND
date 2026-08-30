"""S3 — verb + bac + DA v1 → grade(). Mort VERB_RULES / جاهز / JS diagnostic."""

from __future__ import annotations

import ast
from pathlib import Path

from services.grade_adapter import resolve_question_id, ungraded_http
from services.local_grader import UngradedError, grade_question
from services.rubric_store import list_question_ids

BACKEND = Path(__file__).resolve().parent.parent
ROOT = BACKEND.parent


def _banned_imports(path: Path, banned: set[str]) -> set[str]:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in banned or alias.name in banned:
                    found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod in banned or mod.split(".")[0] in banned:
                found.add(mod)
    return found


def test_bac_blanc_does_not_import_regex_or_methodo():
    found = _banned_imports(
        BACKEND / "routes" / "bac_blanc.py",
        {
            "services.document_analysis_service",
            "methodology.evaluator",
            "services.action_verbs_service",
        },
    )
    assert not found
    src = (BACKEND / "routes" / "bac_blanc.py").read_text(encoding="utf-8")
    assert "evaluate_answer" not in src
    assert "جاهز للبكالوريا" not in src
    assert "grade_or_none" in src
    assert "TRAINING_BANNER_AR" in src


def test_action_verbs_evaluate_does_not_call_regex():
    src = (BACKEND / "routes" / "action_verbs.py").read_text(encoding="utf-8")
    assert "evaluate_answer(" not in src
    assert "from services.action_verbs_service import evaluate_answer" not in src
    assert "grade_or_none" in src
    assert "ungraded_http" in src


def test_da_v1_evaluate_does_not_call_regex():
    src = (BACKEND / "routes" / "document_analysis.py").read_text(encoding="utf-8")
    assert "from services.document_analysis_service import evaluate_answer" not in src
    assert "evaluate_answer(" not in src
    assert "grade_or_none" in src


def test_diagnostic_page_does_not_import_js_grader():
    src = (
        ROOT
        / "khawarizmi-frontend"
        / "src"
        / "app"
        / "diagnostic"
        / "global"
        / "page.tsx"
    ).read_text(encoding="utf-8")
    assert "evaluateMethodologyAnswer" not in src
    # HON-2 (ARCHITECTURE-COACH-LOCAL §14.1) : le diagnostic sans grille L0
    # est un MUR تعذر — pas de carte, pas d'appel note locale.
    assert "NoLocalGradeWall" in src


def test_unknown_verb_id_is_ungraded():
    assert resolve_question_id("verb:analyse", "verb:interpret") is None
    try:
        grade_question("verb:analyse", "نلاحظ ارتفاع")
        raise AssertionError("devait lever UngradedError")
    except UngradedError as e:
        assert e.question_id == "verb:analyse"


def test_l0_still_resolves():
    qid = resolve_question_id("verb:analyse", "manhadjiya-yeast-analyse")
    assert qid == "manhadjiya-yeast-analyse"
    assert "manhadjiya-yeast-analyse" in list_question_ids()


def test_ungraded_http_payload():
    body = ungraded_http("bac:2023:ex1")
    assert body["code"] == "ungraded"
    assert body["status"] == 422
    assert "تدريبية" in body["banner_ar"]


def test_no_alias_enzyme_ph_to_temp():
    """Ne pas mapper un DA pH vers la grille 37°."""
    assert resolve_question_id("enzyme-activity-v1:analyse") is None
