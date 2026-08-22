"""scripts/golden_human_report.py — Rapport de qualité des annotations expert.

Compare les scores HUMANS (tests/golden/golden_annotated.json —
annotator=expert_svt de préférence) aux scores SYSTÈME des moteurs locaux
(L2 + savoir, chemins prod réels — mêmes helpers que le CI) et affiche :

  1. Métriques par moteur (MAE, exact_match, severe, bias, κ, coverage)
     avec VERDICT par rapport aux seuils CI ;
  2. Les items en désaccord sévère (|écart| ≥ 2 pts) — à réviser ;
  3. La liste des copies que le savoir ne couvre pas (périmètre LLM).

Fonctionne aussi sur le golden SYNTHÉTIQUE (baseline avant livraison
expert). Usage :
    python scripts/golden_human_report.py
    python scripts/golden_human_report.py --min-items 30   # seuil de confiance
    python scripts/golden_human_report.py --export data/golden_disagreements.csv
    python scripts/golden_human_report.py \
      --input ../docs/pedagogie/validation-humaine/evidence/golden-human-annotated.json \
      --consensus ../docs/pedagogie/validation-humaine/evidence/golden-consensus.json \
      --metrics-output ../docs/pedagogie/validation-humaine/evidence/human-metrics.json
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

BACKEND = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND))

from tests.golden.metrics import compute_golden_metrics, format_metrics
from tests.golden.scoring import l2_score, savoir_result

# Seuils CI (tests/golden/test_golden_local.py) — les mêmes, en absolu
THRESHOLDS = {
    "l2": {"mae": 0.85, "severe": 0.10, "kappa": 0.45},
    "savoir": {"mae": 0.35, "severe": 0.10, "kappa": 0.65},  # κ 0.65 = réactiver remédiation
}


def verdict(metric: str, value, threshold) -> str:
    if value is None:
        return "⚠️ n/a"
    ok = value <= threshold if metric in ("mae", "severe") else value >= threshold
    return "✅" if ok else "❌"


def report_line(m: dict, thresholds: dict) -> list[str]:
    return [
        f"  n={m['n']}  MAE={m['mae']} {verdict('mae', m['mae'], thresholds['mae'])}"
        f" (seuil ≤ {thresholds['mae']})",
        f"  exact={m['exact_match']}  severe={m['severe_error_rate']} "
        f"{verdict('severe', m['severe_error_rate'], thresholds['severe'])}"
        f" (seuil ≤ {thresholds['severe']})  bias={m['bias']}",
        f"  κ={m['kappa']} {verdict('kappa', m['kappa'], thresholds['kappa'])}"
        f" (seuil ≥ {thresholds['kappa']})  std_ratio={m['std_ratio']}",
    ]


def export_disagreements(rows: list[dict], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"  → désaccords exportés : {path}")


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", default="", help="export CSV des désaccords")
    parser.add_argument("--min-items", type=int, default=0,
                        help="n items minimum pour considérer le verdict fiable")
    parser.add_argument("--input", default="", help="golden humain JSON alternatif")
    parser.add_argument("--consensus", default="", help="golden-consensus.json pour lier le hash")
    parser.add_argument("--metrics-output", default="", help="écrit human-metrics.json")
    args = parser.parse_args()

    if args.input:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        items = payload.get("items", [])
    else:
        from tests.golden.metrics import load_golden_annotated
        items = load_golden_annotated()
    if not items:
        print("❌ golden_annotated.json absent ou vide")
        return 1

    annotators = {it.get("annotator") for it in items}
    non_empty = [i for i in items if i["human_dominant_error"] != "empty"]

    print(f"Golden : {len(items)} items · annotator(s) : {annotators}")
    print(f"  copies vides (empty) : {len(items) - len(non_empty)} (exclues du L2, "
          f"comme en prod — sanity les rejette)\n")

    # ── L2 ──────────────────────────────────────────────────────────
    human_scores, l2_scores, human_codes, l2_codes = [], [], [], []
    for item in non_empty:
        score, code = await l2_score(item)
        human_scores.append(item["human_score"])
        l2_scores.append(score)
        human_codes.append(item["human_dominant_error"])
        l2_codes.append(code)

    m_l2 = compute_golden_metrics(human_scores, l2_scores, human_codes, l2_codes)
    print("── L2 (fallback local) ──")
    print("\n".join(report_line(m_l2, THRESHOLDS["l2"])))

    # ── Savoir ──────────────────────────────────────────────────────
    from services.savoir_corrector import SAVOIR_HIGH_CONFIDENCE_MIN_CONCEPTS

    handled = []
    for item in items:
        r = savoir_result(item)
        if r["_savoir_can_handle"] and r["_savoir_n_concepts"] >= SAVOIR_HIGH_CONFIDENCE_MIN_CONCEPTS:
            handled.append((item, r))

    print(f"\n── Savoir (spécialiste local) — coverage {len(handled)}/{len(items)} "
          f"({len(handled) / len(items):.0%}) ──")
    if handled:
        h_scores = [it["human_score"] for it, _ in handled]
        s_scores = [r["score"] for it, r in handled]
        h_codes = [it["human_dominant_error"] for it, _ in handled]
        s_codes = [r["dominant_error_code"] for it, r in handled]
        m_savoir = compute_golden_metrics(h_scores, s_scores, h_codes, s_codes)
        print("\n".join(report_line(m_savoir, THRESHOLDS["savoir"])))
    else:
        print("  ⚠️ aucun item couvert — périmètre de branchement vide")

    # ── Désaccords sévères ──────────────────────────────────────────
    rows = []
    for item in non_empty:
        l2_score_val, _ = await l2_score(item)
        diff = abs(item["human_score"] - l2_score_val)
        if diff >= 2:
            rows.append({
                "question_id": item["question_id"],
                "chapitre": item.get("chapitre", ""),
                "verb_slug": item.get("verb_slug", ""),
                "human_score": item["human_score"],
                "l2_score": l2_score_val,
                "ecart": diff,
                "human_code": item["human_dominant_error"],
                "question": item["question"],
                "student_answer": item["student_answer"][:120],
                "reponse_attendue": item["reponse_attendue"][:120],
            })

    print(f"\n── Désaccords sévères L2 (|écart| ≥ 2) : {len(rows)} ──")
    for r in sorted(rows, key=lambda r: -r["ecart"])[:10]:
        print(f"  [{r['question_id']}] humain={r['human_score']} vs L2="
              f"{r['l2_score']} ({r['human_code']}) — {r['student_answer'][:60]}…")
    if len(rows) > 10:
        print(f"  … et {len(rows) - 10} autres (export CSV pour tout voir)")
    if args.export and rows:
        export_disagreements(sorted(rows, key=lambda r: -r["ecart"]),
                             BACKEND / args.export)

    if args.metrics_output:
        if not args.consensus:
            print("❌ --metrics-output exige --consensus")
            return 1
        consensus_payload = json.loads(Path(args.consensus).read_text(encoding="utf-8"))
        consensus_items = consensus_payload.get("items", [])
        consensus_hash = hashlib.sha256(
            json.dumps(consensus_items, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()
        l2_passed = (
            m_l2.get("mae") is not None
            and m_l2["mae"] <= THRESHOLDS["l2"]["mae"]
            and m_l2["severe_error_rate"] <= THRESHOLDS["l2"]["severe"]
            and (m_l2.get("kappa") is None or m_l2["kappa"] >= THRESHOLDS["l2"]["kappa"])
        )
        savoir_passed = bool(handled) and (
            m_savoir.get("mae") is not None
            and m_savoir["mae"] <= THRESHOLDS["savoir"]["mae"]
            and m_savoir["severe_error_rate"] <= THRESHOLDS["savoir"]["severe"]
            and (m_savoir.get("kappa") is None or m_savoir["kappa"] >= THRESHOLDS["savoir"]["kappa"])
        )
        metrics = {
            "consensus_sha256": consensus_hash,
            "n": len(consensus_items),
            "mae_l2": m_l2.get("mae"),
            "kappa_l2": m_l2.get("kappa"),
            "severe_error_rate_l2": m_l2.get("severe_error_rate"),
            "mae_savoir": m_savoir.get("mae") if handled else None,
            "kappa_savoir": m_savoir.get("kappa") if handled else None,
            "severe_error_rate_savoir": m_savoir.get("severe_error_rate") if handled else None,
            "thresholds_passed": l2_passed and savoir_passed,
            "computed_at": datetime.now(UTC).isoformat(),
            "computed_by": "golden_human_report.py",
        }
        Path(args.metrics_output).write_text(
            json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"  → métriques humaines exportées : {args.metrics_output}")

    # ── Verdict global ──────────────────────────────────────────────
    print("\n── Verdict ──")
    valid_human_annotators = {"expert_svt_double_blind"}
    n_human = sum(1 for it in items if it.get("annotator") in valid_human_annotators)
    if n_human == 0:
        print("  ⚠️ Aucune annotation humaine validante — ce rapport reflète "
              "une baseline synthétique ou mono-correcteur.")
    else:
        print(f"  ✅ {n_human}/{len(items)} items annotés par expert")
        if n_human < args.min_items:
            print(f"  ⚠️ {n_human} < {args.min_items} items — verdict partiel, "
                  "livrer plus d'annotations pour fiabiliser.")
    if handled:
        kappa = m_savoir.get("kappa")
        if kappa is not None and kappa >= THRESHOLDS["savoir"]["kappa"]:
            rem = "✅ RÉACTIVER la remédiation savoir"
        else:
            rem = f"⏳ garder la remédiation désactivée (κ={kappa})"
        print(f"  Remédiation savoir : seuil κ ≥ {THRESHOLDS['savoir']['kappa']} → {rem}")
    else:
        print("  Remédiation savoir : n/a (aucun item couvert)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
