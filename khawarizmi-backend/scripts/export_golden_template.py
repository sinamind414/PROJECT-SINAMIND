"""scripts/export_golden_template.py — Template historique mono-correcteur.

Ne débloque jamais la publication Lot 7 (double aveugle requis). Exporte
depuis tests/golden/golden_annotated.json un template PRÊT À
REMPLIR par l'expert (champs human_* vidés) en 2 formats :
  - data/golden_annotation_template.json  : structure JSON finale
  - data/golden_annotation_template.csv   : tableur (Excel/Sheets/LibreOffice)

L'expert remplit UNIQUEMENT les colonnes human_* du CSV (voir
docs/golden-annotation-procedure.md §3) puis livre le CSV ; l'import
(scripts/import_golden_annotations.py) regénère le JSON validé.

Usage : python scripts/export_golden_template.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).parent.parent
GOLDEN_ANNOTATED = BACKEND / "tests" / "golden" / "golden_annotated.json"
OUT_JSON = BACKEND / "data" / "golden_annotation_template.json"
OUT_CSV = BACKEND / "data" / "golden_annotation_template.csv"

# Ordre stable des colonnes CSV (l'expert remplit les 4 dernières)
CSV_FIELDS = [
    "question_id", "chapitre", "verb_slug", "bareme",
    "question", "student_answer", "reponse_attendue", "mots_cles_attendus",
    "human_score", "human_dominant_error",
    "human_matched_criteria", "human_unmatched_criteria",
]

HUMAN_FIELDS = ["human_score", "human_score_max", "human_dominant_error",
                "human_matched_criteria", "human_unmatched_criteria",
                "annotator", "annotation_date"]


def blank_item(item: dict) -> dict:
    """Copie de l'item avec les champs humains VIDÉS (l'expert remplit)."""
    out = {k: v for k, v in item.items() if k not in HUMAN_FIELDS}
    out.update({
        "human_score": None,
        "human_score_max": None,
        "human_dominant_error": "",
        "human_matched_criteria": [],
        "human_unmatched_criteria": [],
        "annotator": "",
        "annotation_date": "",
    })
    return out


def _kw_list(value) -> str:
    if not value:
        return ""
    if isinstance(value, str):
        value = json.loads(value)
    return "; ".join(value)


def write_csv(items: list[dict], path: Path) -> None:
    """Écrit le CSV. Les copies VIDES sont pré-remplies (human_score=0,
    human_dominant_error=empty) : trivial et vérifié automatiquement —
    l'expert ne voit que les 100 vraies copies à noter."""
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for it in items:
            is_empty = not (it.get("student_answer") or "").strip()
            writer.writerow({
                "question_id": it["question_id"],
                "chapitre": it.get("chapitre", ""),
                "verb_slug": it.get("verb_slug", ""),
                "bareme": it["bareme"],
                "question": it["question"],
                "student_answer": it["student_answer"],
                "reponse_attendue": it["reponse_attendue"],
                "mots_cles_attendus": _kw_list(it.get("mots_cles_attendus") or []),
                "human_score": "0" if is_empty else "",
                "human_dominant_error": "empty" if is_empty else "",
                "human_matched_criteria": "",
                "human_unmatched_criteria": "",
            })


def main() -> int:
    if not GOLDEN_ANNOTATED.exists():
        print(f"❌ {GOLDEN_ANNOTATED} absent — lancez d'abord "
              "tests/golden/build_golden_annotated.py")
        return 1

    data = json.loads(GOLDEN_ANNOTATED.read_text(encoding="utf-8"))
    items = data.get("items", [])
    if not items:
        print("❌ golden_annotated.json vide")
        return 1

    template_items = [blank_item(it) for it in items]

    OUT_JSON.parent.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps({
        "metadata": {
            "source": "golden_annotated.json — jeu candidat interne, provenance primaire non établie",
            "annotation_type": "human_single_reviewer_template",
            "note": "Template mono-correcteur historique : ne débloque pas la publication. Utiliser docs/pedagogie/validation-humaine/templates pour le double aveugle.",
        },
        "items": template_items,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    write_csv(template_items, OUT_CSV)

    n_empty = sum(1 for it in items if (it.get("student_answer") or "").strip() == "")
    print(f"✅ Template exporté : {len(template_items)} items "
          f"({len(items) - n_empty} copies à noter, {n_empty} copies vides → "
          f"empty + 0 automatiques)")
    print(f"   JSON : {OUT_JSON}")
    print(f"   CSV  : {OUT_CSV} (Excel/Sheets — encodage UTF-8 BOM)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
