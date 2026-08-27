#!/usr/bin/env python3
"""Valide les grilles L0 : sum(points) + grade(model_answer) ≥ 85 %.

Sortie ≠ 0 si une grille est sourde. Bloque le merge (G5).
"""
from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from services.local_grader import grade  # noqa: E402
from services.rubric_store import list_question_ids, load  # noqa: E402
from services.lexicon import in_file  # noqa: E402


def _unknown_lex(r) -> list[str]:
    unknown: list[str] = []
    blobs: list[str] = list(r.theme_variants)
    for c in r.criteria:
        blobs.extend(c.variants)
    for v in blobs:
        if v.startswith("$lex:"):
            key = v[5:].strip()
            if not in_file(key):
                unknown.append(v)
    return unknown


def main() -> int:
    ids = list_question_ids()
    if not ids:
        print("FAIL: aucune rubric dans index.json", file=sys.stderr)
        return 1
    errors = 0
    for qid in ids:
        packed = load(qid)
        if packed is None:
            print(f"FAIL {qid}: ungraded")
            errors += 1
            continue
        r = packed.rubric
        unknown = _unknown_lex(r)
        if unknown:
            print(f"FAIL {qid}: $lex: hors fichier {unknown}")
            errors += 1
        if r.verb_slug == "analyse" and packed.document is None:
            print(f"FAIL {qid}: analyse sans DocumentModel")
            errors += 1
        if not r.model_answer.strip():
            print(f"FAIL {qid}: model_answer vide")
            errors += 1
            continue
        result = grade(
            student_answer=r.model_answer,
            rubric=r,
            document=packed.document,
        )
        ok = result.method_percent >= 85
        status = "OK" if ok else "FAIL"
        print(
            f"{status} {qid} method={result.method_percent}% "
            f"({result.method_points}/{result.method_points_max}) "
            f"label={result.method_label_ar} science={result.science_status} "
            f"diag={result.diagnosis.code if result.diagnosis else '-'}"
        )
        if not ok:
            for h in result.criteria:
                print(f"    {h.id}: {h.status} {h.points_earned}/{h.points_max}")
            errors += 1
    if errors:
        print(f"\n{errors} grille(s) sourde(s) ou invalide(s).", file=sys.stderr)
        return 1
    print(f"\n{len(ids)} grilles valides.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
