#!/usr/bin/env python3
"""
scripts/audit_iconography_inventory.py — Inventaire des schémas décrits dans le cours.

Le cours intégral (data/courses/programme_national_svt_claude_opus.md) contient
pour chaque unité une section « 🗺️ وصف الرسوم التوضيحية » qui DÉCRIT les schémas
à produire (contenu, couleurs, étiquettes) — les images elles-mêmes n'existent
pas (réserves de l'audit pédagogique 2026-08-22).

Ce script extract l'inventaire (unité → figures) pour alimenter le plan de
production iconographique. Ré-exécutable à chaque évolution du cours.

Usage :
    python scripts/audit_iconography_inventory.py            # rapport stdout
    python scripts/audit_iconography_inventory.py --json out.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

COURS = Path(__file__).resolve().parent.parent / "data/courses/programme_national_svt_claude_opus.md"

# En-têtes d'unité : emoji variable selon le domaine (🧬  ⚡ 🌍 🌋)
UNIT_HDR = re.compile(r"^# [\U0001F300-\U0001FAFF\u2600-\u27BF]?\s*(?:الوحدة|الوحدة) (\d+): (.+?)\s*$", re.M)
FIG_RE = re.compile(r"> 🎨 \*\*الرسم (\d+) — ([^:*]+):\*\*\s*\n((?:> .+\n?)+)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", metavar="FICHIER")
    args = ap.parse_args()

    txt = COURS.read_text(encoding="utf-8")

    # localiser les en-têtes d'unité
    units = []
    for m in UNIT_HDR.finditer(txt):
        units.append({"num": int(m.group(1)), "titre": m.group(2).strip(), "start": m.start()})
    units.sort(key=lambda u: u["start"])
    for i, u in enumerate(units):
        end = units[i + 1]["start"] if i + 1 < len(units) else len(txt)
        body = txt[u["start"]:end]
        figs = []
        for fm in FIG_RE.finditer(body):
            desc = re.sub(r"^>\s?", "", fm.group(3), flags=re.M).strip()
            desc = re.sub(r"\s+", " ", desc)
            figs.append({"num": int(fm.group(1)), "titre": fm.group(2).strip(),
                         "description": desc, "longueur_desc": len(desc)})
        u["figures"] = figs
        del u["start"]

    tot = sum(len(u["figures"]) for u in units)
    print(f"=== INVENTAIRE ICONOGRAPHIE — {len(units)} unités, {tot} figures décrites ===\n")
    for u in units:
        n = len(u["figures"])
        flag = "" if n else "   ⚠️ AUCUNE FIGURE DÉCRITE"
        print(f"U{u['num']:>2} — {u['titre'][:75]} → {n} figure(s){flag}")
        for f in u["figures"]:
            print(f"      {f['num']}. {f['titre'][:60]}  (desc. {f['longueur_desc']} car.)")
    print(f"\nTOTAL : {tot} figures décrites + figures manquantes pour les unités sans section 🗺️")

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(units, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"JSON écrit : {out}")


if __name__ == "__main__":
    main()
