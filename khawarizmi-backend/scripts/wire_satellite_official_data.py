#!/usr/bin/env python3
"""Injection des données officielles (unités du programme + exemples pratiques)
dans les JSON des ateliers satellites — statique, au moment du build, sans API.

Source unique : prompts/scientific_knowledge.py (VERB_UNIT_MAP, ALL_UNITS,
PRACTICAL_EXAMPLES). Les 7 JSON du bootcamp ne sont PAS touchés (doctrine
0 API / 0 LLM : les données sont copiées dans le JSON, jamais appelées).

Usage (depuis khawarizmi-backend/) :
    python scripts/wire_satellite_official_data.py
"""
from __future__ import annotations

import json
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parent.parent
FRONTEND = BACKEND.parent / "khawarizmi-frontend"
DATA_DIR = FRONTEND / "data" / "ateliers"

sys.path.insert(0, str(BACKEND))
from prompts.scientific_knowledge import (  # noqa: E402
    ALL_UNITS,
    PRACTICAL_EXAMPLES,
    VERB_UNIT_MAP,
)

# slug satellite → (fichier JSON, verbes backend, catégories d'exemples)
SATELLITES = [
    ("saf", "manhadjia_s01_saf_taam.json", ["decrire"], []),
    ("arif", "manhadjia_s02_arif_taam.json", ["definir"], []),
    ("atbat", "manhadjia_s03_atbat_taam.json", ["prove", "prove-experimentally"], ["prouver-experimentalement"]),
    ("fardiya", "manhadjia_s04_fardiya_taam.json", ["hypothesis", "validate-hypothesis"], []),
    ("naqich", "manhadjia_s05_naqich_taam.json", ["discuss"], []),
    ("synapse", "manhadjia_s06_synapse_taam.json", ["deduce"], ["deduction-vs-extraction"]),
    ("taaraf", "manhadjia_s07_taaraf_taam.json", ["nommer"], []),
    ("oudkur", "manhadjia_s08_oudkur_taam.json", ["citer"], []),
    ("addid", "manhadjia_s09_addid_taam.json", ["enumerer"], []),
    ("sannif", "manhadjia_s10_sannif_taam.json", ["classer"], []),
    ("mayyiz", "manhadjia_s11_mayyiz_taam.json", ["distinguer"], []),
    ("istakhrij", "manhadjia_s12_istakhrij_taam.json", ["extract", "exploit-document"], ["deduction-vs-extraction"]),
    ("alliq", "manhadjia_s13_alliq_taam.json", ["comment"], []),
    ("anqid", "manhadjia_s14_anqid_taam.json", ["evaluate-critique"], []),
    ("mochkil", "manhadjia_s15_mochkil_taam.json", ["formulate-problem"], []),
]

# VERB_UNIT_MAP a « unite5-energie », ALL_UNITS a « unite5-energetique ».
UNIT_TITLES = {u["id"]: u.get("title_ar", "") for u in ALL_UNITS}
UNIT_TITLES.setdefault("unite5-energie", UNIT_TITLES.get("unite5-energetique", ""))

def units_for(verb_slugs: list[str]) -> list[dict[str, str]]:
    ids: list[str] = []
    for unit_id, verbs in VERB_UNIT_MAP.items():
        if any(v in verbs for v in verb_slugs) and unit_id not in ids:
            ids.append(unit_id)
    return [{"id": i, "titre_ar": UNIT_TITLES.get(i, i)} for i in ids if UNIT_TITLES.get(i)]

def exemples_for(categories: list[str]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for cat in categories:
        for ex in PRACTICAL_EXAMPLES.get(cat, []):
            item = {
                "title": ex.get("title", ""),
                "context": ex.get("context", ""),
                "content": ex.get("content", ""),
                "unit": ex.get("unit", ""),
            }
            if item not in out:
                out.append(item)
    return out

def main() -> None:
    total_units = 0
    total_exemples = 0
    for slug, filename, verb_slugs, categories in SATELLITES:
        path = DATA_DIR / filename
        if not path.exists():
            print(f"❌ {filename} introuvable — abort")
            sys.exit(1)
        data = json.loads(path.read_text(encoding="utf-8"))
        unites = units_for(verb_slugs)
        exemples = exemples_for(categories)
        data["unites"] = unites
        data["verb_slug"] = verb_slugs[0]
        if exemples:
            data["exemples"] = exemples
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        total_units += len(unites)
        total_exemples += len(exemples)
        print(f"✅ {filename} <- {len(unites)} unités · {len(exemples)} exemples · verb_slug={verb_slugs[0]} ({slug})")
    print(f"Total : {total_units} unités, {total_exemples} exemples sur 15 satellites — bootcamp intact.")

if __name__ == "__main__":
    main()
