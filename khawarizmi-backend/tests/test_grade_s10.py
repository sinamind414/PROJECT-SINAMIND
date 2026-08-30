"""S10 — drill/submit + exercices/correct gelés. 0 GPT / 0 L2. QCM local intact."""

from __future__ import annotations

import ast
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
ROOT = BACKEND.parent
FLASH = (BACKEND / "routes" / "flashcards.py").read_text(encoding="utf-8")
EXO = (BACKEND / "routes" / "exercices.py").read_text(encoding="utf-8")
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")
CLIENT = (
    ROOT / "khawarizmi-frontend" / "src" / "lib" / "api-client.ts"
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


def test_drill_submit_does_not_import_llm_or_evaluate():
    found = _banned_imports(
        FLASH,
        {"openai", "llm", "pipeline", "fallback_v2", "correction_v2", "evaluate"},
    )
    assert not found, found
    assert "evaluate_with_fallback" not in FLASH
    assert "from routes.evaluate import" not in FLASH
    assert "grade_or_none" in FLASH
    assert "ungraded_http" in FLASH


def test_exercices_correct_does_not_call_gpt():
    found = _banned_imports(EXO, {"openai", "correction_service", "llm"})
    assert not found, found
    assert "correct_student_answer" not in EXO
    assert "grade_or_none" in EXO
    assert "ungraded_http" in EXO
    assert "UserExerciseResponse" not in EXO


def test_qcm_drill_stays_local():
    assert "soumettre_qcm_drill" in FLASH
    assert "QCM_LOCAL" in FLASH
    assert "get_qcm" in FLASH


def test_evaluate_py_still_not_mounted():
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT


def test_front_handles_ungraded_422():
    assert "submitDrillAnswer" in CLIENT
    assert "/api/drill/submit" in CLIENT
    assert 'data.code === "ungraded"' in CLIENT
    assert "source: \"ungraded\"" in CLIENT
