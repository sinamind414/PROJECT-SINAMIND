#!/usr/bin/env python3
"""Noter une copie d'entraînement (0 LLM).

Usage:
  python scripts/grade_copy.py manhadjiya-yeast-analyse
  python scripts/grade_copy.py manhadjiya-yeast-analyse --file copie.txt
  echo '...' | python scripts/grade_copy.py greffe-ltc-interpret

Note d'entraînement — ليست علامة بكالوريا رسمية.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from services.local_grader import (  # noqa: E402
    TRAINING_BANNER_AR,
    UngradedError,
    grade_question,
)
from services.rubric_store import list_question_ids  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Correcteur local 0 LLM (entraînement)")
    p.add_argument("question_id", nargs="?", help="id dans data/rubrics/index.json")
    p.add_argument("--file", "-f", help="fichier de la copie (sinon stdin)")
    p.add_argument("--list", action="store_true", help="liste les questions")
    p.add_argument("--json", action="store_true", dest="as_json", help="sortie JSON")
    args = p.parse_args()

    if args.list or not args.question_id:
        print("questions:")
        for qid in list_question_ids():
            print(f"  {qid}")
        if not args.question_id:
            return 0 if args.list else 2

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    else:
        if sys.stdin.isatty():
            print("Colle la copie, puis Ctrl-D :", file=sys.stderr)
        text = sys.stdin.read()

    try:
        result = grade_question(args.question_id, text)
    except UngradedError:
        print(f"ungraded: pas de grille pour {args.question_id}", file=sys.stderr)
        return 2

    if args.as_json:
        print(result.model_dump_json(indent=2, ensure_ascii=False))
        return 0

    print(TRAINING_BANNER_AR)
    print(f"منهج: {result.method_points}/{result.method_points_max}  {result.method_percent}%  {result.method_label_ar}")
    if result.order_ok is False:
        print("ordre: لا (متقن interdit)")
    print(f"محتوى: {result.science_status}" + (f" — {', '.join(result.science_flags)}" if result.science_flags else ""))
    print(f"درجة التدريب: {result.overall_training_percent}%")
    if result.diagnosis:
        print(f"تشخيص: {result.diagnosis.code} — {result.diagnosis.label_ar}")
    if result.phrase_ar:
        print(result.phrase_ar)
    print("---")
    for h in result.criteria:
        mark = "✓" if h.status == "full" else ("~" if h.status == "partial" else "✗")
        print(f"  {mark} {h.label_ar}  {h.points_earned}/{h.points_max}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
