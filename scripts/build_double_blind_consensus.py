#!/usr/bin/env python3
"""Fusionne A/B + arbitrage en consensus humain, sans modifier le golden CI."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/pedagogie/validation-humaine/evidence"
GOLDEN = ROOT / "khawarizmi-backend/tests/golden/golden_annotated.json"
CONSENSUS = EVIDENCE / "golden-consensus.json"
HUMAN_ANNOTATED = EVIDENCE / "golden-human-annotated.json"


def _gate_module():
    path = ROOT / "scripts/check_publication_gate.py"
    spec = importlib.util.spec_from_file_location("publication_gate_for_consensus", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    gate = _gate_module()
    double_ok, double_problems, double_data = gate._validate_double_blind()
    if not double_ok:
        print("NO-GO: annotations A/B invalides")
        for problem in double_problems[:20]:
            print(f"- {problem}")
        return 1
    arbitration_ok, arbitration_problems, consensus = gate._validate_arbitration(double_data)
    if not arbitration_ok:
        print("NO-GO: arbitrage incomplet")
        for problem in arbitration_problems[:20]:
            print(f"- {problem}")
        return 1

    canonical = json.dumps(consensus, sort_keys=True, ensure_ascii=False).encode()
    consensus_hash = hashlib.sha256(canonical).hexdigest()
    now = datetime.now(UTC).isoformat()
    CONSENSUS.write_text(json.dumps({
        "metadata": {
            "annotation_type": "human_double_blind_consensus",
            "reviewer_a": double_data["reviewer_a"],
            "reviewer_b": double_data["reviewer_b"],
            "items": len(consensus),
            "consensus_sha256": consensus_hash,
            "created_at": now,
        },
        "items": consensus,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    source = json.loads(GOLDEN.read_text(encoding="utf-8"))
    by_item = {item["item_id"]: item for item in consensus}
    per_question: dict[str, int] = {}
    merged = []
    for item in source["items"]:
        question_id = str(item["question_id"])
        per_question[question_id] = per_question.get(question_id, 0) + 1
        item_id = f"{question_id}-copy-{per_question[question_id]:02d}"
        decision = by_item[item_id]
        updated = dict(item)
        updated["human_score"] = decision["score"]
        updated["human_score_max"] = item["bareme"]
        updated["human_dominant_error"] = decision["dominant_error"]
        updated["human_matched_criteria"] = []
        updated["human_unmatched_criteria"] = []
        updated["annotator"] = "expert_svt_double_blind"
        updated["annotation_date"] = now[:10]
        updated["validation_item_id"] = item_id
        merged.append(updated)

    HUMAN_ANNOTATED.write_text(json.dumps({
        "metadata": {
            "source": "jeu candidat interne — provenance primaire à valider séparément",
            "annotation_type": "human_double_blind_consensus",
            "annotator": "expert_svt_double_blind",
            "consensus_sha256": consensus_hash,
            "reviewer_ids": [double_data["reviewer_a"], double_data["reviewer_b"]],
            "date": now[:10],
        },
        "items": merged,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Consensus humain construit: {len(consensus)} items, sha256={consensus_hash}")
    print(f"- {CONSENSUS}")
    print(f"- {HUMAN_ANNOTATED}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
