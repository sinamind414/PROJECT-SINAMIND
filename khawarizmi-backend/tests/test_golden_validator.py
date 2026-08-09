"""tests/test_golden_validator.py — Validation des annotations golden (S2.4).

Le validateur (scripts/validate_golden_annotations.py) garantit que les
annotations humaines livrées par un expert SVT respectent le contrat :
- champs requis, score dans [0, bareme], code valide
- partition des mots-clés (copies partielles), copie vide → empty, copie
  modèle → bareme
"""

# NB : scripts/ n'est pas un package — import via le chemin fichier
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from scripts.validate_golden_annotations import validate_item

_SCRIPT = Path(__file__).parent.parent / "scripts" / "validate_golden_annotations.py"
_spec = importlib.util.spec_from_file_location("validate_golden_annotations", _SCRIPT)
validate_mod = importlib.util.module_from_spec(_spec)
sys.modules["validate_golden_annotations"] = validate_mod
_spec.loader.exec_module(validate_mod)


def _item(**over):
    base = {
        "question_id": "gs_x",
        "verb_slug": "restitution",
        "chapitre": "ch1",
        "question": "q",
        "student_answer": "réponse avec النواة",
        "bareme": 4,
        "reponse_attendue": "réponse modèle",
        "mots_cles_attendus": ["النواة"],
        "human_score": 4,
        "human_score_max": 4,
        "human_dominant_error": "all_correct",
        "human_matched_criteria": ["النواة"],
        "human_unmatched_criteria": [],
        "annotator": "expert_svt",
        "annotation_date": "2026-08-15",
    }
    base.update(over)
    return base


class TestValidateItem:
    def test_valid_item(self):
        assert validate_item(_item(), 0) == []

    def test_missing_field(self):
        item = _item()
        del item["annotator"]
        problems = validate_item(item, 0)
        assert any("champ requis absent: annotator" in p for p in problems)

    def test_score_out_of_range(self):
        problems = validate_item(_item(human_score=5), 0)
        assert any("hors [0, 4]" in p for p in problems)

    def test_invalid_code(self):
        problems = validate_item(_item(human_dominant_error="nimporte"), 0)
        assert any("code invalide" in p for p in problems)

    def test_partition_keyword_present_in_matched(self):
        item = _item(
            human_score=2,
            human_dominant_error="partial_correct",
            human_matched_criteria=[],
            human_unmatched_criteria=["النواة"],
        )
        problems = validate_item(item, 0)
        assert any("présent" in p and "unmatched" in p for p in problems)

    def test_partition_keyword_absent_from_unmatched(self):
        item = _item(
            student_answer="réponse sans concept",
            human_score=0,
            human_dominant_error="insufficient",
            human_matched_criteria=[],
            human_unmatched_criteria=[],
        )
        problems = validate_item(item, 0)
        assert any("ni dans unmatched" in p for p in problems)

    def test_empty_copy_requires_empty_code(self):
        problems = validate_item(
            _item(student_answer="", human_score=0, human_dominant_error="gibberish"),
            0,
        )
        assert any("copie vide mais code" in p for p in problems)

    def test_model_copy_requires_full_score(self):
        problems = validate_item(
            _item(student_answer="réponse modèle", human_score=2,
                  human_dominant_error="partial_correct"),
            0,
        )
        assert any("copie == modèle mais score" in p for p in problems)

    def test_model_copy_skips_partition_check(self):
        """Copie modèle : pas de vérification de partition littérale (le
        concept peut être exprimé autrement)."""
        problems = validate_item(
            _item(student_answer="réponse modèle",
                  human_matched_criteria=[]),  # vide volontairement
            0,
        )
        assert problems == []

    def test_real_golden_file_valid(self):
        """Le fichier d'annotations actuel (synthétique) passe le validateur."""
        golden = Path(__file__).parent / "golden" / "golden_annotated.json"
        if not golden.exists():
            pytest.skip("golden_annotated.json absent")
        data = json.loads(golden.read_text(encoding="utf-8"))
        items = data.get("items", [])
        all_problems = []
        for i, item in enumerate(items):
            all_problems.extend(validate_item(item, i))
        assert all_problems == []
