#!/usr/bin/env python3
"""
Modèle de coût LLM — EXÉCUTABLE (audit 100k §5.4 / grille §B et G0-3)

« coût/élève/mois = f(évaluations/jour, % cache hit, % étage local) »
— pas un tableau d'opinions : la formule tourne ici.

Formule :
    coût_élève_mois = éval/j × (1 − hit_cache) × (1 − %_local)
                      × [(tok_in × p_in + tok_out × p_out) / 1 000 000] × 30

  - hit_cache   : part des évaluations servies par le cache single-flight
                  (grading/cache.py — R2) : copies répétées, retry.
  - %_local     : part résolue sans LLM externe (sanity, savoir, fallback —
                  le « mode déterministe local » du backend, 0 token).
  - tok_in/out  : tokens moyens par appel LLM (réel si --from-log, sinon
                  hypothèse à mesurer sur les logs de prod).

Tarifs (daté 2026-08-21) — Gemini 2.5 Flash, modèle primaire du backend
(services/llm.py) ; source : page tarifaire Google AI Studio + agrégateur
OpenRouter (recherches web du jour) :
    direct (Google AI Studio) : 0,15 $/Mtok in · 1,25 $/Mtok out
    agrégateur (OpenRouter)   : 0,30 $/Mtok in · 2,50 $/Mtok out
  → le scénario « haut » prend les tarifs agrégateur (pire cas raisonnable,
    pas une spéculation).

Usage :
    python scripts/llm_cost_model.py
    python scripts/llm_cost_model.py --from-log /path/cost_log.jsonl
    python scripts/llm_cost_model.py --evals 3 5 8 --cache 0.2 0.3 0.5 \
        --local 0.1 0.2 0.4 --students 10000 100000 --markdown
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

PRICE_GOOGLE = (0.15, 1.25)        # $/Mtok (in, out) — direct, daté 2026-08-21
PRICE_AGGREGATOR = (0.30, 2.50)    # $/Mtok (in, out) — agrégateur, daté 2026-08-21


def load_cost_log(path: str) -> dict | None:
    """Tokens moyens RÉELS mesurés depuis cost_log.jsonl (cost_logger.py)."""
    p = Path(path)
    if not p.exists():
        print(f"⚠️  log introuvable : {path}", file=sys.stderr)
        return None
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    if not rows:
        return None
    return {
        "n": len(rows),
        "avg_in": statistics.mean(r["input_tokens"] for r in rows),
        "avg_out": statistics.mean(r["output_tokens"] for r in rows),
        "avg_cost_usd": statistics.mean(r["cost_usd"] for r in rows),
    }


def monthly_cost(
    evals_day: float,
    cache_hit: float,
    local_pct: float,
    tok_in: float,
    tok_out: float,
    price: tuple[float, float],
) -> float:
    p_in, p_out = price
    per_eval = (tok_in * p_in + tok_out * p_out) / 1_000_000
    return evals_day * (1 - cache_hit) * (1 - local_pct) * per_eval * 30


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--from-log", default=None,
                    help="cost_log.jsonl pour calibrer les tokens moyens réels")
    ap.add_argument("--evals", type=float, nargs=3, default=[2, 5, 10],
                    metavar=("BAS", "MED", "HAUT"),
                    help="évaluations LLM / élève / jour (défaut 2 5 10)")
    ap.add_argument("--cache", type=float, nargs=3, default=[0.5, 0.3, 0.0],
                    metavar=("BAS", "MED", "HAUT"),
                    help="taux de hit cache (défaut 0.5 0.3 0.0)")
    ap.add_argument("--local", type=float, nargs=3, default=[0.4, 0.2, 0.0],
                    metavar=("BAS", "MED", "HAUT"),
                    help="%% résolu par les étages locaux (défaut 0.4 0.2 0.0)")
    ap.add_argument("--tok-in", type=float, default=None,
                    help="tokens d'entrée moyens / appel (défaut : log si --from-log, sinon 150)")
    ap.add_argument("--tok-out", type=float, default=None,
                    help="tokens de sortie moyens / appel (défaut : log si --from-log, sinon 80)")
    ap.add_argument("--students", type=int, nargs="+", default=[10000, 100000],
                    help="tailles de population actives (défaut 10000 100000)")
    ap.add_argument("--markdown", action="store_true",
                    help="émettre le bloc §B au format tableau markdown")
    args = ap.parse_args()

    log = load_cost_log(args.from_log) if args.from_log else None
    tok_in = args.tok_in or (log["avg_in"] if log else 150)
    tok_out = args.tok_out or (log["avg_out"] if log else 80)
    tok_src = (f"mésurés cost_log.jsonl (n={log['n']})" if log
               else "hypothèse — à mesurer sur les logs de prod")

    # 3 scénarios : (libellé, éval/j, cache, local, tarif)
    (e_lo, e_md, e_hi) = args.evals
    (c_lo, c_md, c_hi) = args.cache
    (l_lo, l_md, l_hi) = args.local
    scenarios = [
        ("Bas", e_lo, c_lo, l_lo, PRICE_GOOGLE),
        ("Médian", e_md, c_md, l_md, PRICE_GOOGLE),
        ("Haut", e_hi, c_hi, l_hi, PRICE_AGGREGATOR),
    ]

    lines: list[str] = []
    if args.markdown:
        lines.append("## §B — Modèle de coût (exécutable, `scripts/llm_cost_model.py`)")
        lines.append("")
        lines.append("Formule : `coût/élève/mois = éval/j × (1−cache) × (1−local) × [(tok_in×p_in + tok_out×p_out)/1M] × 30`")
        lines.append("")
    else:
        print(f"Tokens moyens / appel : {tok_in:.0f} in / {tok_out:.0f} out  [{tok_src}]")
        print(f"Tarifs Gemini 2.5 Flash (daté 2026-08-21) : Google {PRICE_GOOGLE[0]}/{PRICE_GOOGLE[1]} $/M · "
              f"agrégateur {PRICE_AGGREGATOR[0]}/{PRICE_AGGREGATOR[1]} $/M")
        print()

    header = (f"{'Scénario':<9} {'éval/j':>7} {'cache':>6} {'local':>6} {'tarif':<10} "
              f"{'$ /élève/mois':>13}" + "".join(f"{'  ' + str(s).replace(' ', '') + ' élèves':>15}" for s in args.students))
    if args.markdown:
        lines.append("| Scénario | éval/j | cache | local | tarif | $ /élève/mois |"
                     + "".join(f" {s} élèves |" for s in args.students) + "|")
        lines.append("|---" * (5 + len(args.students)) + "|")
    else:
        print(header)
        print("-" * len(header))

    for name, e, c, l, price in scenarios:
        cost = monthly_cost(e, c, l, tok_in, tok_out, price)
        totals = [cost * s for s in args.students]
        price_lbl = "Google" if price == PRICE_GOOGLE else "agrégateur"
        if args.markdown:
            lines.append(
                f"| {name} | {e:g} | {c:.0%} | {l:.0%} | {price_lbl} | **{cost:.4f}** "
                + "".join(f"| **{t:,.0f} $/mois**" for t in totals)
                + " |"
            )
        else:
            print(f"{name:<9} {e:>7.0f} {c:>6.0%} {l:>6.0%} {price_lbl:<10} "
                  f"{cost:>13.4f}" + "".join(f"{t:>15,.0f}" for t in totals))

    if args.markdown:
        lines.append("")
        lines.append(f"Sources : tokens [{tok_src}] · tarifs Gemini 2.5 Flash datés 2026-08-21 "
                     f"(Google AI Studio {PRICE_GOOGLE[0]}/{PRICE_GOOGLE[1]} $/M ; OpenRouter "
                     f"{PRICE_AGGREGATOR[0]}/{PRICE_AGGREGATOR[1]} $/M). Garde-fous déjà en place : "
                     f"quota 15 éval/h/élève (R1) · cache single-flight (R2) · circuit breaker par provider (R13).")
        print("\n".join(lines))
    else:
        print(f"\nTotal = coût/élève/mois × élèves actifs. Le vrai chiffre dépend des 5 cases "
              f"« à mesurer » du §B — ce script les remplace par des fourchettes.")


if __name__ == "__main__":
    main()
