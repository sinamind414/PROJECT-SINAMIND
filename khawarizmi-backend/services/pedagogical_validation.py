"""État de validation humaine des moteurs de notation."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_GOLDEN_PATH = Path(__file__).parent.parent / "tests" / "golden" / "golden_annotated.json"


@lru_cache(maxsize=1)
def grading_validation_status() -> dict[str, object]:
    """Retourne un statut honnête : jamais de certification synthétique."""
    try:
        metadata = json.loads(_GOLDEN_PATH.read_text(encoding="utf-8")).get("metadata", {})
    except (OSError, json.JSONDecodeError):
        metadata = {}
    annotation_type = str(metadata.get("annotation_type") or "missing")
    annotator = str(metadata.get("annotator") or "")
    human_validated = annotation_type.startswith("human") and annotator.startswith("expert_svt")
    return {
        "human_validated": human_validated,
        "annotation_type": annotation_type,
        "annotator": annotator or None,
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
