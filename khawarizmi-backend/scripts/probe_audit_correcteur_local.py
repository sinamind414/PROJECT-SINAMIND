#!/usr/bin/env python3
"""scripts/probe_audit_correcteur_local.py — probes adversariales du correcteur local.

Reproduction des findings de AUDIT-CORRECTEUR-LOCAL-2026-08-30.md.
Lecture seule : ne modifie ni grille, ni moteur. Sortie = faits mesurés.

Usage :
  cd khawarizmi-backend
  python scripts/probe_audit_correcteur_local.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from services.arabic import normalize_arabic as n  # noqa: E402
from services.local_grader import UngradedError, _extract_numbers, _hit_pos, grade, grade_question  # noqa: E402
from services.rubric_store import load  # noqa: E402

OK, KO = "  ok ", "  !! "


def head(t: str) -> None:
    print(f"\n== {t}")


def main() -> int:
    yeast = load("yeast-glucose-interpret")
    assert yeast is not None
    R, D = yeast.rubric, yeast.document
    MODEL = R.model_answer

    def res(label: str, copy: str, rubric=R, doc=D):
        r = grade(student_answer=copy, rubric=rubric, document=doc)
        print(
            f"{label}: method={r.method_percent}% overall={r.overall_training_percent}% "
            f"science={r.science_status} sanity={r.sanity_code} "
            f"stuff={r.stuffing_suspected} caps={r.caps_applied} "
            f"diag={r.diagnosis.code if r.diagnosis else None}"
        )
        return r

    head("F1 — enclitiques : لانه/لانها/بسببها ne matchent pas «لان/بسبب»")
    for w in ("لأنها", "لانه"):
        r = res(f"{KO}{w}", MODEL.replace("لأن", w))
        assert next(c for c in r.criteria if c.id == "cause").status == "absent"
    res(f"{OK}لأن (réf)", MODEL)

    head("F2 — 36 ATP neutralisé par un «38 ATP» ajouté n'importe où")
    res(f"{KO}modèle + 36 ATP (réf cap 40)", MODEL + " وتنتج 36 ATP.")
    res(f"{KO}modèle + 36 ATP + 38 ATP", MODEL + " وتنتج 36 ATP لكن 38 ATP صحيح.")

    head("F3 — stuffing neutralisé par un chiffre du document (exemption kp_full)")
    stuff = " ".join(["الغلوكوز غلوكوز الخميرة خميرة تنفس تخمر طاقة مادة أيض نمو تكاثر"] * 3)
    res(f"{OK}bourrage sans chiffre (cap 50)", stuff)
    res(f"{KO}bourrage + «18»", stuff + " العدد يصل 18 ")

    head("F4 — hors-sujet avec 1 mot de thème : note 0 mais diagnostic faussé")
    off = (
        "تمثل الوثيقة منحنى تباعد الصفائح عند الأعراف المحيطية مثل الخميرة لا علاقة. "
        "كلما ابتعدت الصفيحة ازداد الخندق المحيطي. نستنتج غوص اللوح في الاندساس."
    )
    res(f"{KO}tectonique + «الخميرة» x1", off)

    head("F5 — autres comportements (référence saine)")
    res(f"{OK}modèle", MODEL)
    res(f"{OK}modèle + P/O NADH=2 (cap 40)", MODEL + " نسبة P/O لجزيء NADH تساوي 2 ")
    res(f"{OK}errata 10⁶ (jaune, pas de cap)", MODEL + " الوزن الجزيئي للريبوزوم 5S هو 3.6×10^6")
    res(f"{OK}vide", "   ")
    rev = (
        "نستنتج أن نمو الخميرة مرتبط بتوفر الغلوكوز لأن الغلوكوز مادة أيض وطاقة للتنفس. "
        "نلاحظ أن العدد 18 مع الغلوكوز مقابل 6 بدونه وتتكاثر الخلايا."
    )
    r = grade(student_answer=rev, rubric=R, document=D)
    print(f"{OK}ordre inversé: method={r.method_percent}% order_ok={r.order_ok} label={r.method_label_ar}")

    head("F6 — invariants bas niveau")
    print(f"{OK}idempotence normalize:", n(n("ﻧَﻼﺣِﻆ اﻟﻌﺪد ١٨")) == n("نلاحظ العدد 18"))
    print(f"{OK}لان ⊄ الانزيم:", _hit_pos(n("الانزيم"), n("لان")) is None)
    print(f"{OK}نمو ⊄ النموذج:", _hit_pos(n("النموذج"), n("نمو")) is None)
    print(f"{OK}séparateur décimal ٫:", _extract_numbers(n("3٫6")) == [(3.6, 0)])
    print(f"{OK}année 2018 ≠ keypoint 18:",
          grade(student_answer=MODEL.replace("18", "2018"), rubric=R, document=D).method_percent == 100)

    head("F7 — perf plafond (copie 20 000 car, limite route)")
    t0 = time.perf_counter()
    grade(student_answer=((MODEL + " ") * 250)[:20000], rubric=R, document=D)
    print(f"{OK}20k chars: {(time.perf_counter() - t0) * 1000:.0f} ms")

    head("F8 — id inconnu → ungraded (pas de fallback)")
    try:
        grade_question("question-inexistante", "نمو")
    except UngradedError as e:
        print(f"{OK}UngradedError: {e.question_id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
