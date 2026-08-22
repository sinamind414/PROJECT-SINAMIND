"""Garde-fous Lot 7 : les templates ne doivent jamais fabriquer un GO."""
from __future__ import annotations

import csv
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "khawarizmi-backend"))
VALIDATION = ROOT / "docs/pedagogie/validation-humaine"
TEMPLATES = VALIDATION / "templates"


def _load_gate_module():
    path = ROOT / "scripts/check_publication_gate.py"
    spec = importlib.util.spec_from_file_location("publication_gate", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _csv_rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def test_templates_cover_all_objects_but_keep_human_fields_blank():
    grader_a = _csv_rows(TEMPLATES / "golden-grader-a.csv")
    grader_b = _csv_rows(TEMPLATES / "golden-grader-b.csv")
    contents = _csv_rows(TEMPLATES / "content-review.csv")
    rubrics = _csv_rows(TEMPLATES / "rubric-review.csv")
    figures = _csv_rows(TEMPLATES / "figure-review.csv")

    assert len(grader_a) == len(grader_b) == 125
    assert len(contents) == 55
    assert len(rubrics) == 110
    assert len(figures) == 35
    assert all(not row["score"] and not row["reviewer_id"] for row in grader_a + grader_b)
    assert all(not row["decision"] and not row["reviewer_id"] for row in contents + rubrics)
    assert all(not row["scientific_decision"] and not row["reviewer_id"] for row in figures)
    assert "student_answer" not in grader_a[0]
    assert "answer" not in grader_a[0]


def test_current_publication_gate_is_explicit_no_go():
    gate = _load_gate_module()
    result = gate.evaluate_gate()

    assert result["decision"] == "NO_GO"
    assert result["mechanical_gate_passed"] is False
    assert set(result["criteria"]) == {
        "primary_ministerial_source",
        "golden_double_blind",
        "golden_arbitration",
        "human_metrics",
        "contents_55",
        "rubrics_110",
        "figures_35",
        "publication_signoff",
    }
    assert all(item["passed"] is False for item in result["criteria"].values())

    persisted = json.loads((VALIDATION / "validation-status.json").read_text(encoding="utf-8"))
    assert persisted["decision"] == "NO_GO"
    assert persisted["mechanical_gate_passed"] is False


def test_copying_blank_templates_into_evidence_still_cannot_pass():
    gate = _load_gate_module()
    original_evidence = gate.EVIDENCE_DIR
    with tempfile.TemporaryDirectory() as temp_dir:
        evidence = Path(temp_dir)
        copies = {
            "golden-grader-a.csv": "golden-grader-a.csv",
            "golden-grader-b.csv": "golden-grader-b.csv",
            "golden-arbitration.csv": "golden-arbitration.csv",
            "content-review.csv": "content-review.csv",
            "rubric-review.csv": "rubric-review.csv",
            "figure-review.csv": "figure-review.csv",
            "primary-source-manifest-template.json": "primary-source.json",
            "reviewers-template.json": "reviewers.json",
            "human-metrics-template.json": "human-metrics.json",
            "publication-signoff-template.json": "publication-signoff.json",
        }
        for source, destination in copies.items():
            shutil.copy(TEMPLATES / source, evidence / destination)
        gate.EVIDENCE_DIR = evidence
        try:
            result = gate.evaluate_gate()
        finally:
            gate.EVIDENCE_DIR = original_evidence
    assert result["decision"] == "NO_GO"
    assert all(item["passed"] is False for item in result["criteria"].values())


def test_consensus_builder_refuses_missing_human_evidence():
    path = ROOT / "scripts/build_double_blind_consensus.py"
    spec = importlib.util.spec_from_file_location("consensus_builder", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert module.main() == 1
    assert not (VALIDATION / "evidence/golden-consensus.json").exists()
    assert not (VALIDATION / "evidence/golden-human-annotated.json").exists()


def test_synthetic_golden_cannot_report_human_validation():
    from services.pedagogical_validation import grading_validation_status

    grading_validation_status.cache_clear()
    status = grading_validation_status()
    assert status["annotation_type"] == "synthetic_keyword_based"
    assert status["annotator"] == "synthetic_keyword_v1"
    assert status["double_blind_evidence_complete"] is False
    assert status["human_validated"] is False
    assert status["scope"] == "formative_only"
