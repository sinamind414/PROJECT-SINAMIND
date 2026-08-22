#!/usr/bin/env python3
"""
scripts/normalize_arabic_pres_forms.py — Normalisation des extraits PDF en
« formes de présentation » arabes (action 2 du plan de correction OCR).

Problème : certains documents extraits de PDF (ex. methodologie doc n°1,
eddirasa.com) sont encodés en caractères U+FB50-U+FDFF (formes contextuelles)
plutôt qu'en lettres arabes standard U+0621-U+064A — illisibles sans
normalisation. La transformation est DETERMINISTE et réversible vers le
standard : unicodedata NFKC (décomposition de compatibilité Unicode).

Transformations appliquées (conservatrices) :
  1. NFKC : formes de présentation → lettres standard (ﻮ → و, ﻻ → لا)
  2. suppression des caractères de contrôle C0 (sauf \\n et \\t)
  3. 3+ sauts de ligne consécutifs → 2
  4. numéro de page erratique en tête de champ « contenu » (1-3 chiffres
     isolés avant la vraie entrée) — suppression
Le script ne touche QUE les champs contenant des formes de présentation ou
des contrôleurs (idempotent : une 2e exécution ne change rien).

Sortie :
  - fichier JSON normalisé (in place)
  - rapport before/after pour la relecture humaine (docs/audit-contenu/)

Usage :
    python scripts/normalize_arabic_pres_forms.py \
        --file data/methodologie_sciences_3as.json \
        --report ../docs/audit-contenu/normalisation-2026-08-22.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PRES = re.compile(r"[\uFB50-\uFDFF\uFE70-\uFEFF]")
CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
LEADING_PAGENUM = re.compile(r"^\s*\d{1,3}\s*\n?")
MULTI_NL = re.compile(r"\n{3,}")


def normalize_text(text: str) -> tuple[str, list[str]]:
    """Applique les transformations ; retourne (texte, transformations faites).

    La suppression du numéro de tête n'est tentée QUE sur un champ qui
    contenait des formes de présentation (extraction corrompue) — jamais sur
    un texte sain (garde anti-régression)."""
    if not text:
        return text, []
    before = text
    done = []
    had_pres = bool(PRES.search(text))
    if had_pres:
        text = unicodedata.normalize("NFKC", text)
        done.append("NFKC (formes de présentation → lettres standard)")
    if CTRL.search(text):
        text = CTRL.sub("", text)
        done.append("suppression contrôleurs C0")
    if "\n" in text and MULTI_NL.search(text):
        text = MULTI_NL.sub("\n\n", text)
        done.append("3+ sauts de ligne → 2")
    if had_pres:
        m = LEADING_PAGENUM.match(text)
        if m and m.group().strip().isdigit() and 0 < len(m.group().strip()) <= 3:
            # numéro erratique en tête (ex. numéro de page du PDF)
            text = text[m.end():]
            done.append(f"numéro de tête retiré ({m.group().strip()!r})")
    return text, done


def walk_and_fix(o, path=""):
    """Yield (chemin, avant, après, transformations) pour chaque champ modifié."""
    if isinstance(o, str):
        after, done = normalize_text(o)
        if after != o:
            yield path or "(racine)", o, after, done
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from walk_and_fix(v, f"{path}/{k}" if path else str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk_and_fix(v, f"{path}[{i}]")


def apply_in_place(o):
    """Réécrit l'objet en place ; retourne la liste des chemins modifiés."""
    changed = []

    def rec(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str):
                    nv, _ = normalize_text(v)
                    if nv != v:
                        o[k] = nv
                        changed.append(k)
                else:
                    rec(v)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                if isinstance(v, str):
                    nv, _ = normalize_text(v)
                    if nv != v:
                        o[i] = nv
                        changed.append(f"[{i}]")
                else:
                    rec(v)

    rec(o)
    return changed


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--file", required=True)
    ap.add_argument("--report", required=True)
    args = ap.parse_args()

    f = Path(args.file)
    data = json.load(open(f, encoding="utf-8"))

    diffs = list(walk_and_fix(data))
    if not diffs:
        print(f"{f.name} : aucun champ à normaliser (déjà propre ou idempotent).")
        return

    apply_in_place(data)
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rep = Path(args.report)
    rep.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Rapport de normalisation — {f.name} (2026-08-22)",
        "",
        f"Champs transformés : **{len(diffs)}** · Transformations appliquées :",
    ]
    all_done = set()
    for _, _, _, done in diffs:
        all_done.update(done)
    lines += [f"- {d}" for d in sorted(all_done)]
    lines += [
        "",
        "## Avant / après (relecture humaine requise — action 2 du plan)",
        "",
    ]
    for path, before, after, done in diffs:
        lines.append(f"### `{path[:90]}`")
        lines.append(f"Transformations : {', '.join(done)}")
        lines.append("")
        lines.append("**AVANT** (brut) :")
        lines.append("```")
        lines.append((before[:400] + "…") if len(before) > 400 else before)
        lines.append("```")
        lines.append("")
        lines.append("**APRÈS** :")
        lines.append("```")
        lines.append((after[:400] + "…") if len(after) > 400 else after)
        lines.append("```")
        lines.append("")
    rep.write_text("\n".join(lines), encoding="utf-8")
    print(f"{f.name} : {len(diffs)} champs normalisés, écrit in place.")
    print(f"Rapport before/after : {rep}")


if __name__ == "__main__":
    main()
