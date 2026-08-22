#!/usr/bin/env python3
"""Génère les modèles vides du dossier de validation humaine Lot 7."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATION_DIR = ROOT / "docs/pedagogie/validation-humaine"
TEMPLATES_DIR = VALIDATION_DIR / "templates"
GOLDEN = ROOT / "khawarizmi-backend/tests/golden/golden_annotated.json"
CONTRACTS = ROOT / "khawarizmi-frontend/data/chapter-learning-contracts.json"
EXERCISES = ROOT / "khawarizmi-frontend/data/chapter-exercise-bank.json"
FIGURES = ROOT / "docs/audit-contenu/iconography-manifest.json"

GOLDEN_FIELDS = [
    "item_id",
    "question_id",
    "answer_sha256",
    "score_max",
    "score",
    "dominant_error",
    "matched_criteria",
    "unmatched_criteria",
    "reviewer_id",
    "reviewed_at",
    "notes",
]


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _golden_rows() -> list[dict]:
    items = json.loads(GOLDEN.read_text(encoding="utf-8"))["items"]
    per_question: dict[str, int] = {}
    rows = []
    for item in items:
        question_id = str(item["question_id"])
        per_question[question_id] = per_question.get(question_id, 0) + 1
        item_id = f"{question_id}-copy-{per_question[question_id]:02d}"
        rows.append({
            "item_id": item_id,
            "question_id": question_id,
            "answer_sha256": _sha(str(item.get("student_answer") or "")),
            "score_max": item["bareme"],
            "score": "",
            "dominant_error": "",
            "matched_criteria": "",
            "unmatched_criteria": "",
            "reviewer_id": "",
            "reviewed_at": "",
            "notes": "",
        })
    return rows


def main() -> None:
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    golden_rows = _golden_rows()
    _write_csv(TEMPLATES_DIR / "golden-grader-a.csv", GOLDEN_FIELDS, golden_rows)
    _write_csv(TEMPLATES_DIR / "golden-grader-b.csv", GOLDEN_FIELDS, golden_rows)
    _write_csv(
        TEMPLATES_DIR / "golden-arbitration.csv",
        [
            "item_id", "question_id", "answer_sha256", "score_a", "score_b",
            "error_a", "error_b", "score_final", "dominant_error_final",
            "arbiter_id", "arbitrated_at", "rationale",
        ],
        [],
    )

    contracts = json.loads(CONTRACTS.read_text(encoding="utf-8"))["contracts"]
    _write_csv(
        TEMPLATES_DIR / "content-review.csv",
        ["chapter_slug", "title_ar", "title_fr", "decision", "reviewer_id", "reviewed_at", "evidence_reference", "notes"],
        [{
            "chapter_slug": item["chapterSlug"],
            "title_ar": item["titleAr"],
            "title_fr": item["titleFr"],
            "decision": "",
            "reviewer_id": "",
            "reviewed_at": "",
            "evidence_reference": "",
            "notes": "",
        } for item in contracts],
    )

    activities = [
        activity
        for chapter in json.loads(EXERCISES.read_text(encoding="utf-8"))["chapters"]
        for activity in chapter["activities"]
    ]
    _write_csv(
        TEMPLATES_DIR / "rubric-review.csv",
        ["activity_id", "kind", "score_max", "decision", "reviewer_id", "reviewed_at", "evidence_reference", "notes"],
        [{
            "activity_id": item["id"],
            "kind": item["kind"],
            "score_max": item["scoreMax"],
            "decision": "",
            "reviewer_id": "",
            "reviewed_at": "",
            "evidence_reference": "",
            "notes": "",
        } for item in activities],
    )

    figures = json.loads(FIGURES.read_text(encoding="utf-8"))["figures"]
    _write_csv(
        TEMPLATES_DIR / "figure-review.csv",
        [
            "figure_id", "file_sha256", "scientific_decision",
            "bilingual_labels_applied", "mobile_checked", "a4_print_checked",
            "reviewer_id", "reviewed_at", "evidence_reference", "notes",
        ],
        [{
            "figure_id": item["id"],
            "file_sha256": item["sha256"],
            "scientific_decision": "",
            "bilingual_labels_applied": "",
            "mobile_checked": "",
            "a4_print_checked": "",
            "reviewer_id": "",
            "reviewed_at": "",
            "evidence_reference": "",
            "notes": "",
        } for item in figures],
    )

    templates = {
        "primary-source-manifest-template.json": {
            "document_path": "",
            "sha256": "",
            "authority": "",
            "administrative_reference": "",
            "publication_date": "",
            "verified_by": "",
            "verified_at": "",
            "evidence_reference": "",
        },
        "reviewers-template.json": {
            "reviewers": [
                {"reviewer_id": "", "role": "teacher_or_inspector_svt", "organization": "", "declaration_reference": ""},
                {"reviewer_id": "", "role": "teacher_or_inspector_svt", "organization": "", "declaration_reference": ""},
            ],
            "arbiter": {"reviewer_id": "", "role": "teacher_or_inspector_svt", "declaration_reference": ""},
        },
        "human-metrics-template.json": {
            "consensus_sha256": "",
            "n": None,
            "mae_l2": None,
            "kappa_l2": None,
            "severe_error_rate_l2": None,
            "mae_savoir": None,
            "kappa_savoir": None,
            "severe_error_rate_savoir": None,
            "thresholds_passed": False,
            "computed_at": "",
            "computed_by": "",
        },
        "publication-signoff-template.json": {
            "decision": "",
            "scope": "contents_figures_rubrics",
            "signed_by": [],
            "signed_at": "",
            "signature_references": [],
            "release_commit": "",
            "notes": "",
        },
    }
    for name, payload in templates.items():
        (TEMPLATES_DIR / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print(
        "Generated validation templates: "
        f"golden={len(golden_rows)}, contents={len(contracts)}, "
        f"rubrics={len(activities)}, figures={len(figures)}"
    )


if __name__ == "__main__":
    main()
