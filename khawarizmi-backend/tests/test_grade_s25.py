"""S25 — UI explique caps_applied (حشو 50 / science 40). Hors grade(). 1.1.5."""

from __future__ import annotations

from pathlib import Path

from services.local_grader import GRADER_VERSION

ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND = Path(__file__).resolve().parent.parent
FE = ROOT / "khawarizmi-frontend" / "src"
CARD = FE / "components" / "methodology" / "GradeResultCard.tsx"
SCENARIO = FE / "components" / "methodology" / "ScenarioRunner.tsx"
DIAG = FE / "app" / "diagnostic" / "global" / "page.tsx"
API = FE / "lib" / "api-client.ts"
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")


def test_card_shows_stuffing_and_science_caps():
    src = CARD.read_text(encoding="utf-8")
    assert "capsApplied" in src
    assert "سقف 50 · حشو" in src
    assert "سقف 40" in src
    assert "capHints" in src
    assert "بكالوريا" not in src.split("درجة التدريب")[1][:80]


def test_adapters_forward_caps():
    assert "capsApplied" in SCENARIO.read_text(encoding="utf-8")
    assert "capsApplied" in DIAG.read_text(encoding="utf-8")
    assert "caps_applied" in API.read_text(encoding="utf-8")
    assert "caps_applied" in CARD.read_text(encoding="utf-8")


def test_grader_untouched_no_version_bump():
    assert GRADER_VERSION == "1.1.7"
    assert "GradeResultCard" not in GRADER
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT
