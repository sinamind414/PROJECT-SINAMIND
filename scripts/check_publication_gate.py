#!/usr/bin/env python3
"""Garde de publication Lot 7 : NO-GO tant que les preuves humaines manquent."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VALIDATION_DIR = ROOT / "docs/pedagogie/validation-humaine"
EVIDENCE_DIR = VALIDATION_DIR / "evidence"
STATUS_PATH = VALIDATION_DIR / "validation-status.json"
GOLDEN = ROOT / "khawarizmi-backend/tests/golden/golden_annotated.json"
CONTRACTS = ROOT / "khawarizmi-frontend/data/chapter-learning-contracts.json"
EXERCISES = ROOT / "khawarizmi-frontend/data/chapter-exercise-bank.json"
FIGURES = ROOT / "docs/audit-contenu/iconography-manifest.json"

VALID_ERRORS = {
    "scientific_error", "methodology_error", "off_topic", "partial_correct",
    "all_correct", "insufficient", "gibberish", "too_short", "empty",
    "not_arabic", "repeated_chars", "server_error", "unknown",
}


def _sha_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha_file(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            return list(reader.fieldnames or []), list(reader)
    except OSError:
        return [], []


def _expected_golden() -> dict[str, dict[str, Any]]:
    items = _json(GOLDEN)["items"]
    per_question: dict[str, int] = {}
    expected = {}
    for item in items:
        question_id = str(item["question_id"])
        per_question[question_id] = per_question.get(question_id, 0) + 1
        item_id = f"{question_id}-copy-{per_question[question_id]:02d}"
        expected[item_id] = {
            "question_id": question_id,
            "answer_sha256": _sha_bytes(str(item.get("student_answer") or "").encode()),
            "score_max": int(item["bareme"]),
        }
    return expected


def _validate_grader(path: Path, expected: dict[str, dict]) -> tuple[bool, list[str], str | None, dict[str, dict]]:
    fields, rows = _csv(path)
    problems: list[str] = []
    forbidden = {"student_answer", "answer", "reponse_eleve"} & set(fields)
    if forbidden:
        problems.append(f"colonnes de copie en clair interdites: {sorted(forbidden)}")
    by_id = {row.get("item_id", ""): row for row in rows}
    if set(by_id) != set(expected):
        problems.append(f"couverture attendue {len(expected)}, reçue {len(by_id)}")
    reviewer_ids = {row.get("reviewer_id", "").strip() for row in rows if row.get("reviewer_id", "").strip()}
    if len(reviewer_ids) != 1:
        problems.append("un reviewer_id unique et non vide est requis par fichier")
    for item_id in sorted(expected):
        spec = expected[item_id]
        row = by_id.get(item_id)
        if not row:
            continue
        if row.get("question_id") != spec["question_id"]:
            problems.append(f"{item_id}: question_id incohérent")
        if row.get("answer_sha256") != spec["answer_sha256"]:
            problems.append(f"{item_id}: hash copie incohérent")
        try:
            score = int(row.get("score", ""))
        except ValueError:
            problems.append(f"{item_id}: score manquant/invalide")
            continue
        if not 0 <= score <= spec["score_max"]:
            problems.append(f"{item_id}: score hors barème")
        if row.get("dominant_error", "") not in VALID_ERRORS:
            problems.append(f"{item_id}: dominant_error invalide")
        if not row.get("reviewed_at", "").strip():
            problems.append(f"{item_id}: reviewed_at absent")
    reviewer = next(iter(reviewer_ids), None)
    return not problems, problems, reviewer, by_id


def _validate_primary_source() -> tuple[bool, list[str]]:
    manifest = _json(EVIDENCE_DIR / "primary-source.json")
    if not isinstance(manifest, dict):
        return False, ["evidence/primary-source.json absent"]
    required = ["document_path", "sha256", "authority", "administrative_reference", "verified_by", "verified_at", "evidence_reference"]
    missing = [field for field in required if not str(manifest.get(field) or "").strip()]
    if missing:
        return False, [f"champs source primaire absents: {missing}"]
    document = (ROOT / str(manifest["document_path"])).resolve()
    allowed_root = (EVIDENCE_DIR / "primary").resolve()
    if not document.is_relative_to(allowed_root):
        return False, ["document primaire hors evidence/primary"]
    if not document.is_file():
        return False, ["document primaire archivé introuvable"]
    if _sha_file(document) != manifest["sha256"]:
        return False, ["hash du document primaire invalide"]
    return True, []


def _validate_reviewers(reviewer_a: str | None, reviewer_b: str | None) -> tuple[bool, list[str]]:
    payload = _json(EVIDENCE_DIR / "reviewers.json")
    if not isinstance(payload, dict):
        return False, ["evidence/reviewers.json absent"]
    reviewers = payload.get("reviewers") or []
    by_id = {str(item.get("reviewer_id") or ""): item for item in reviewers}
    if not reviewer_a or not reviewer_b or reviewer_a == reviewer_b:
        return False, ["deux reviewer_id distincts sont requis"]
    problems = []
    for reviewer_id in (reviewer_a, reviewer_b):
        item = by_id.get(reviewer_id, {})
        if item.get("role") != "teacher_or_inspector_svt":
            problems.append(f"{reviewer_id}: rôle SVT non attesté")
        if not str(item.get("declaration_reference") or "").strip():
            problems.append(f"{reviewer_id}: déclaration externe absente")
    return not problems, problems


def _validate_double_blind() -> tuple[bool, list[str], dict[str, Any]]:
    expected = _expected_golden()
    ok_a, problems_a, reviewer_a, rows_a = _validate_grader(EVIDENCE_DIR / "golden-grader-a.csv", expected)
    ok_b, problems_b, reviewer_b, rows_b = _validate_grader(EVIDENCE_DIR / "golden-grader-b.csv", expected)
    ok_reviewers, reviewer_problems = _validate_reviewers(reviewer_a, reviewer_b)
    valid = ok_a and ok_b and ok_reviewers
    details = {"reviewer_a": reviewer_a, "reviewer_b": reviewer_b, "items": len(expected)}
    return valid, problems_a + problems_b + reviewer_problems, {
        **details, "valid": valid, "expected": expected, "rows_a": rows_a, "rows_b": rows_b,
    }


def _validate_arbitration(double_data: dict[str, Any]) -> tuple[bool, list[str], list[dict]]:
    expected = double_data.get("expected") or {}
    rows_a = double_data.get("rows_a") or {}
    rows_b = double_data.get("rows_b") or {}
    if not double_data.get("valid") or not expected or not rows_a or not rows_b:
        return False, ["annotations double aveugle incomplètes"], []
    disputes = [
        item_id for item_id in sorted(expected)
        if rows_a[item_id].get("score") != rows_b[item_id].get("score")
        or rows_a[item_id].get("dominant_error") != rows_b[item_id].get("dominant_error")
    ]
    _, arbitration_rows = _csv(EVIDENCE_DIR / "golden-arbitration.csv")
    by_id = {row.get("item_id", ""): row for row in arbitration_rows}
    if set(by_id) != set(disputes):
        return False, [f"arbitrage attendu pour {len(disputes)} désaccords, reçu {len(by_id)}"], []
    problems = []
    consensus = []
    reviewer_ids = {double_data.get("reviewer_a"), double_data.get("reviewer_b")}
    for item_id in sorted(expected):
        spec = expected[item_id]
        row_a, row_b = rows_a[item_id], rows_b[item_id]
        if item_id in disputes:
            row = by_id[item_id]
            try:
                score = int(row.get("score_final", ""))
            except ValueError:
                problems.append(f"{item_id}: score_final invalide")
                continue
            error = row.get("dominant_error_final", "")
            arbiter = row.get("arbiter_id", "").strip()
            if arbiter in reviewer_ids or not arbiter:
                problems.append(f"{item_id}: arbitre distinct requis")
            if not row.get("arbitrated_at", "").strip() or not row.get("rationale", "").strip():
                problems.append(f"{item_id}: trace d'arbitrage incomplète")
        else:
            score = int(row_a["score"])
            error = row_a["dominant_error"]
        if not 0 <= score <= spec["score_max"] or error not in VALID_ERRORS:
            problems.append(f"{item_id}: consensus invalide")
        consensus.append({"item_id": item_id, "score": score, "dominant_error": error})
    return not problems, problems, consensus


def _validate_metrics(consensus: list[dict]) -> tuple[bool, list[str]]:
    payload = _json(EVIDENCE_DIR / "human-metrics.json")
    if not isinstance(payload, dict) or not consensus:
        return False, ["evidence/human-metrics.json ou consensus absent"]
    consensus_hash = _sha_bytes(json.dumps(consensus, sort_keys=True, ensure_ascii=False).encode())
    required_numeric = ["mae_l2", "kappa_l2", "severe_error_rate_l2", "mae_savoir", "kappa_savoir", "severe_error_rate_savoir"]
    problems = []
    if payload.get("consensus_sha256") != consensus_hash:
        problems.append("hash consensus des métriques invalide")
    if payload.get("n") != len(consensus):
        problems.append("taille métriques incohérente")
    for field in required_numeric:
        if not isinstance(payload.get(field), (int, float)):
            problems.append(f"{field} absent")
    if payload.get("thresholds_passed") is not True:
        problems.append("seuils humains non atteints ou non attestés")
    if not payload.get("computed_at") or not payload.get("computed_by"):
        problems.append("trace de calcul métriques absente")
    return not problems, problems


def _validate_approval_csv(path: Path, id_field: str, expected_ids: set[str], *, figures: bool = False) -> tuple[bool, list[str]]:
    _, rows = _csv(path)
    if not rows:
        return False, [f"evidence/{path.name} absent"]
    by_id = {row.get(id_field, ""): row for row in rows}
    problems = []
    if set(by_id) != expected_ids:
        problems.append(f"{path.name}: couverture {len(by_id)}/{len(expected_ids)}")
    for item_id in sorted(expected_ids):
        row = by_id.get(item_id, {})
        decision_field = "scientific_decision" if figures else "decision"
        if row.get(decision_field) != "APPROVE":
            problems.append(f"{item_id}: décision APPROVE absente")
        for field in ("reviewer_id", "reviewed_at", "evidence_reference"):
            if not row.get(field, "").strip():
                problems.append(f"{item_id}: {field} absent")
        if figures:
            for field in ("bilingual_labels_applied", "mobile_checked", "a4_print_checked"):
                if row.get(field) != "true":
                    problems.append(f"{item_id}: {field} non confirmé")
    return not problems, problems


def _validate_publication_signoff() -> tuple[bool, list[str]]:
    payload = _json(EVIDENCE_DIR / "publication-signoff.json")
    if not isinstance(payload, dict):
        return False, ["evidence/publication-signoff.json absent"]
    signers = payload.get("signed_by") or []
    refs = payload.get("signature_references") or []
    problems = []
    if payload.get("decision") != "GO":
        problems.append("décision GO absente")
    if len(set(signers)) < 2 or len(refs) < 2:
        problems.append("deux signataires et deux références de signature sont requis")
    for field in ("signed_at", "release_commit"):
        if not str(payload.get(field) or "").strip():
            problems.append(f"{field} absent")
    return not problems, problems


def evaluate_gate() -> dict[str, Any]:
    criteria: dict[str, dict[str, Any]] = {}

    primary_ok, primary_problems = _validate_primary_source()
    criteria["primary_ministerial_source"] = {"passed": primary_ok, "problems": primary_problems}

    double_ok, double_problems, double_data = _validate_double_blind()
    criteria["golden_double_blind"] = {"passed": double_ok, "problems": double_problems[:20]}

    arbitration_ok, arbitration_problems, consensus = _validate_arbitration(double_data)
    criteria["golden_arbitration"] = {"passed": arbitration_ok, "problems": arbitration_problems[:20]}

    metrics_ok, metrics_problems = _validate_metrics(consensus)
    criteria["human_metrics"] = {"passed": metrics_ok, "problems": metrics_problems}

    chapter_ids = {item["chapterSlug"] for item in _json(CONTRACTS)["contracts"]}
    content_ok, content_problems = _validate_approval_csv(EVIDENCE_DIR / "content-review.csv", "chapter_slug", chapter_ids)
    criteria["contents_55"] = {"passed": content_ok, "problems": content_problems[:20]}

    activity_ids = {activity["id"] for chapter in _json(EXERCISES)["chapters"] for activity in chapter["activities"]}
    rubric_ok, rubric_problems = _validate_approval_csv(EVIDENCE_DIR / "rubric-review.csv", "activity_id", activity_ids)
    criteria["rubrics_110"] = {"passed": rubric_ok, "problems": rubric_problems[:20]}

    figure_ids = {item["id"] for item in _json(FIGURES)["figures"]}
    figure_ok, figure_problems = _validate_approval_csv(EVIDENCE_DIR / "figure-review.csv", "figure_id", figure_ids, figures=True)
    criteria["figures_35"] = {"passed": figure_ok, "problems": figure_problems[:20]}

    signoff_ok, signoff_problems = _validate_publication_signoff()
    criteria["publication_signoff"] = {"passed": signoff_ok, "problems": signoff_problems}

    passed = all(item["passed"] for item in criteria.values())
    return {
        "evaluated_at": datetime.now(UTC).date().isoformat(),
        "decision": "GO" if passed else "NO_GO",
        "mechanical_gate_passed": passed,
        "human_authenticity_note": "Le logiciel contrôle présence, cohérence et hashes; l'authenticité des identités/signatures reste une responsabilité humaine externe.",
        "criteria": criteria,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="écrit validation-status.json")
    parser.add_argument("--allow-no-go", action="store_true", help="retour 0 même si NO_GO (génération de statut)")
    args = parser.parse_args()
    result = evaluate_gate()
    if args.write:
        STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATUS_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["decision"] == "GO" or args.allow_no_go:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
