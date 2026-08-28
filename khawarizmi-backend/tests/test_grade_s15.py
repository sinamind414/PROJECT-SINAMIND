"""S15 — chatbot explain-back / boss-fight gelés. 0 % jouet. 0 alias L0."""

from __future__ import annotations

import ast
from pathlib import Path

from services.local_grader import GRADER_VERSION, TRAINING_BANNER_AR

BACKEND = Path(__file__).resolve().parent.parent
ROOT = BACKEND.parent
ENGAGE = (BACKEND / "services" / "chatbot_engagement_service.py").read_text(encoding="utf-8")
ROUTE = (BACKEND / "routes" / "chatbot_engagement.py").read_text(encoding="utf-8")
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
CLIENT = (ROOT / "khawarizmi-frontend" / "src" / "lib" / "api-client.ts").read_text(
    encoding="utf-8"
)
CHAT_UI = (
    ROOT / "khawarizmi-frontend" / "src" / "components" / "dashboard" / "chatbot" / "useChatbot.ts"
).read_text(encoding="utf-8")


def _banned_imports(src: str, banned: set[str]) -> set[str]:
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
            root = mod.split(".")[0]
            if root in banned or mod in banned:
                found.add(mod)
    return found


def test_no_heuristic_judges_left():
    assert "def _score_clarity" not in ENGAGE
    assert "def _score_scientific_terms" not in ENGAGE
    assert "def _score_structure" not in ENGAGE
    assert "def _score_boss_answer" not in ENGAGE
    assert "overlap = len" not in ENGAGE


def test_explain_back_contract_ungraded():
    assert '"total_score": 0' in ENGAGE
    assert '"clarity_score": 0' in ENGAGE
    assert '"ungraded": True' in ENGAGE
    assert '"source": "ungraded"' in ENGAGE
    assert "TRAINING_BANNER_AR" in ENGAGE
    assert "answer[:1000]" not in ENGAGE


def test_boss_submit_ungraded_no_copy():
    assert '"score": 0' in ENGAGE
    assert '"passed": False' in ENGAGE
    assert '"details": []' in ENGAGE
    assert '"student_answer"' not in ENGAGE
    assert "AND user_id = :uid" in ENGAGE
    assert "S15" in ROUTE


def test_boss_questions_never_leak_model_answer():
    gen = ENGAGE.split("def _generate_boss_questions")[1].split("def ")[0]
    assert "model_answer" not in gen
    assert "_public_boss_questions" in ENGAGE


def test_no_alias_to_l0_rubrics():
    assert "proteine-adn-scientific-text" not in ENGAGE
    assert "manhadjiya-yeast-analyse" not in ENGAGE
    assert "grade_or_none" not in ENGAGE
    assert "grade_or_none" not in ROUTE


def test_engagement_does_not_import_llm():
    found = _banned_imports(
        ENGAGE,
        {"openai", "llm", "pipeline", "fallback_v2", "evaluate"},
    )
    assert not found, found
    found_r = _banned_imports(ROUTE, {"openai", "llm", "pipeline", "fallback_v2"})
    assert not found_r, found_r


def test_evaluate_still_not_mounted():
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT


def test_grader_version_unchanged():
    assert GRADER_VERSION == "1.1.6"
    assert "openai" not in GRADER
    assert "from services.chatbot_engagement_service" not in GRADER
    assert TRAINING_BANNER_AR.startswith("ملاحظة تدريبية")


def test_front_does_not_paint_boss_bac_percent():
    assert "Boss Bac!" not in CHAT_UI
    assert "ليست علامة بكالوريا رسمية" in CHAT_UI
    assert "% بكالوريا" not in CHAT_UI
    assert "/api/chatbot/explain-back" in CLIENT
    assert "/api/chatbot/boss-fight/" in CLIENT
