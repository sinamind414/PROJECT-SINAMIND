"""État de validation humaine des moteurs de notation."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_BACKEND = Path(__file__).parent.parent
_ROOT = _BACKEND.parent
_GOLDEN_PATH = _BACKEND / "tests" / "golden" / "golden_annotated.json"
_GATE_PATH = _ROOT / "docs" / "pedagogie" / "validation-humaine" / "validation-status.json"


@lru_cache(maxsize=1)
def grading_validation_status() -> dict[str, object]:
    """Retourne un statut honnête : jamais de certification synthétique."""
    try:
        metadata = json.loads(_GOLDEN_PATH.read_text(encoding="utf-8")).get("metadata", {})
    except (OSError, json.JSONDecodeError):
        metadata = {}
    try:
        gate_criteria = json.loads(_GATE_PATH.read_text(encoding="utf-8")).get("criteria", {})
    except (OSError, json.JSONDecodeError):
        gate_criteria = {}
    annotation_type = str(metadata.get("annotation_type") or "missing")
    annotator = str(metadata.get("annotator") or "")
    required_gate = ("golden_double_blind", "golden_arbitration", "human_metrics")
    evidence_complete = all(
        gate_criteria.get(name, {}).get("passed") is True
        for name in required_gate
    )
    human_validated = (
        annotation_type == "human_double_blind_consensus"
        and annotator == "expert_svt_double_blind"
        and evidence_complete
    )
    return {
        "human_validated": human_validated,
        "annotation_type": annotation_type,
        "annotator": annotator or None,
        "double_blind_evidence_complete": evidence_complete,
        "scope": "validated" if human_validated else "formative_only",
        "message_fr": (
            "Notation validée par expert SVT."
            if human_validated
            else "Annotations humaines absentes : notes formatives, non certificatives."
        ),
        "message_ar": (
            "تم اعتماد سلم التصحيح من خبير علوم."
            if human_validated
            else "لم يعتمد خبير علوم سلم التصحيح بعد: العلامات تكوينية وليست رسمية."
        ),
    }
