"""scripts/import_golden_annotations.py — Import historique mono-correcteur.

Ne débloque jamais la publication Lot 7. Lit le CSV complété par un relecteur
(data/golden_annotation_template.csv ou
tout CSV au même format), fusionne avec les items sources (champs
non-humains préservés), VALIDE avec validate_golden_annotations puis écrit
tests/golden/golden_annotated.json (backup .bak conservé).

Colonnes humaines attendues (les seules que l'expert modifie) :
  human_score, human_dominant_error,
  human_matched_criteria, human_unmatched_criteria   (listes séparées par ";")
La colonne human_score_max est facultative (défaut = bareme).

Usage :
    python scripts/import_golden_annotations.py --csv data/golden_annotation_template.csv
    python scripts/import_golden_annotations.py --csv chemin/vers/expert.csv --dry-run
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

BACKEND = Path(__file__).parent.parent
GOLDEN_ANNOTATED = BACKEND / "tests" / "golden" / "golden_annotated.json"
VALID_CODES = {
    "scientific_error", "methodology_error", "off_topic", "partial_correct",
    "all_correct", "insufficient", "gibberish", "too_short", "empty",
    "not_arabic", "repeated_chars", "server_error", "unknown",
}


def _parse_list(value: str) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(";") if part.strip()]


def _load_items(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("items", data if isinstance(data, list) else [])


def merge_csv(csv_path: Path, source_items: list[dict]) -> list[dict]:
    """Fusionne les annotations du CSV sur les items sources (par question_id
    + student_answer — une copie peut apparaître sous 2 questions)."""
    by_qid: dict[str, dict] = {}
    for it in source_items:
        by_qid[(it["question_id"], it["student_answer"])] = it

    rows = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))
    merged: list[dict] = []
    missing: list[str] = []
    unfilled: list[str] = []
    for row in rows:
        key = (row.get("question_id", ""), row.get("student_answer", ""))
        src = by_qid.get(key)
        if src is None:
            missing.append(f"{key[0]} — copie introuvable dans le golden source")
            continue
        item = dict(src)
        raw_score = row.get("human_score")
        human_fields = [
            row.get("human_dominant_error") or "",
            row.get("human_matched_criteria") or "",
            row.get("human_unmatched_criteria") or "",
        ]
        if raw_score in (None, ""):
            if not any(human_fields):
                # Ligne TOTALEMENT vide → item non annoté, conservé tel quel
                # (livraison progressive : l'expert ne remplit qu'une partie)
                continue
            # Ligne PARTIELLEMENT remplie → erreur de l'expert (bloquant)
            unfilled.append(f"{key[0]} — ligne CSV partiellement remplie "
                            "sans human_score")
            continue
        item["human_score"] = int(raw_score)
        item["human_score_max"] = int(row["human_score_max"]) if row.get("human_score_max") not in (None, "") else item["bareme"]
        item["human_dominant_error"] = (row.get("human_dominant_error") or "").strip()
        item["human_matched_criteria"] = _parse_list(row.get("human_matched_criteria") or "")
        item["human_unmatched_criteria"] = _parse_list(row.get("human_unmatched_criteria") or "")
        item["annotator"] = "human_single_reviewer_unverified"
        item["annotation_date"] = (row.get("annotation_date") or "").strip()
        merged.append(item)

    if missing:
        print(f"⚠️ {len(missing)} lignes CSV sans correspondance (ignorées) :")
        for m in missing[:10]:
            print(f"   - {m}")
    if unfilled:
        print(f"⚠️ {len(unfilled)} lignes CSV présentes SANS human_score :")
        for m in unfilled[:10]:
            print(f"   - {m}")
    return merged, unfilled


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, help="CSV complété par l'expert")
    parser.add_argument("--dry-run", action="store_true",
                        help="valide sans écrire golden_annotated.json")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"❌ {csv_path} absent")
        return 1

    source_items = _load_items(GOLDEN_ANNOTATED)
    merged, unfilled = merge_csv(csv_path, source_items)

    # Validation (réutilise validate_golden_annotations en mémoire)
    sys.path.insert(0, str(BACKEND))
    from scripts.validate_golden_annotations import validate_item

    problems: list[str] = []
    for i, item in enumerate(merged):
        problems.extend(validate_item(item, i))
    if unfilled:
        problems.append(f"{len(unfilled)} lignes CSV présentes sans human_score "
                        "(remplir ou retirer la ligne)")

    if problems:
        print(f"❌ {len(problems)} problème(s) de cohérence sur {len(merged)} items :")
        for p in problems[:20]:
            print(f"   - {p}")
        return 1

    kept = len(source_items) - len(merged)
    print(f"✅ {len(merged)} items mono-annotés cohérents (non validants pour publication)"
          + (f" · {kept} items non annotés conservés tels quels" if kept else ""))

    if args.dry_run:
        print("(dry-run — golden_annotated.json non modifié)")
        return 0

    shutil.copy(GOLDEN_ANNOTATED, str(GOLDEN_ANNOTATED) + ".bak")
    GOLDEN_ANNOTATED.write_text(json.dumps({
        "metadata": {
            "source": "golden_set_onec.json (nom historique) — jeu candidat interne, provenance primaire non établie",
            "annotation_type": "human_single_reviewer",
            "annotator": "human_single_reviewer_unverified",
            "date": max((it.get("annotation_date") or "") for it in merged) or "",
            "note": "Annotation humaine mono-correcteur non vérifiée : reste formative et ne remplace pas le double aveugle Lot 7.",
        },
        "items": merged,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ écrit dans {GOLDEN_ANNOTATED} (backup .bak conservé)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
