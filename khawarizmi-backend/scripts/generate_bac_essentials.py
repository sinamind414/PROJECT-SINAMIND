"""Génère data/essential/bac_essentials.json (requis par /api/aujourdhui).

Sources :
- programme_svt_3as_canonical.json  → 57 micro-concepts officiels
- fallback_programme_data.py       → structure unités/chapitres (mapping MC → unité)
- الكتاب_المصحح_v1.0.md            → phrases clés BAC réelles (« نصائح البكالوريا »)
- lexique_svt_terminale_complet.json → définitions arabes pour phrase_cle

Le fichier est ensuite ajouté au dépôt (force-add) car requis au runtime.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
DATA = BACKEND / "data"
OUT = DATA / "essential" / "bac_essentials.json"


def load_canonical() -> list[dict]:
    d = json.load(open(DATA / "official" / "programme_svt_3as_canonical.json", encoding="utf-8"))
    mcs = []
    # Les 11 chapitres du canonical = les 11 unités du programme, dans l'ordre officiel.
    unit_index = 0
    for dom in d["domaines"]:
        for ch in dom.get("chapitres", []):
            unit_index += 1
            for mc in ch.get("micro_concepts", []):
                mcs.append({**mc, "unit_id": f"u{unit_index}"})
    return mcs


def load_units() -> list[dict]:
    sys.path.insert(0, str(BACKEND))
    from services.units import UNITS_CATALOG
    return UNITS_CATALOG  # id, domain_ar, unit_ar, keywords


def map_mc_to_unit(mc: dict, units: list[dict]) -> str:
    """Associe un MC à son unité (injectée par load_canonical, ordre officiel)."""
    return mc.get("unit_id", units[0]["id"])


def load_lexique() -> list[dict]:
    try:
        d = json.load(open(DATA / "lexique_svt_terminale_complet.json", encoding="utf-8"))
        termes = []
        for dom in d.get("domaines", []):
            for cat in dom.get("categories", []):
                termes.extend(cat.get("termes", []))
        return termes
    except Exception:
        return []


def load_livre_tips() -> tuple[list[str], list[str]]:
    """Extrait les « نصائح البكالوريا » (bullets ✦) et les erreurs (bullets contenant خطأ)."""
    livre = BACKEND / ".." / "الكتاب_المصحح_v1.0.md"
    if not livre.exists():
        return [], []
    text = livre.read_text(encoding="utf-8")
    phrases, erreurs = [], []
    in_tips = False
    for line in text.splitlines():
        if "نصائح البكالوريا" in line:
            in_tips = True
            continue
        if in_tips:
            if line.startswith("#") or line.startswith("---"):
                in_tips = False
                continue
            m = re.search(r"✦\s*(.+)", line)
            if m:
                tip = m.group(1).strip()
                phrases.append(tip)
                if re.search(r"خطأ|خلط|لا تخلط|لا تنس", tip):
                    erreurs.append(tip)
    return phrases, erreurs


def build_micro_concepts(mcs: list[dict], units: list[dict], lexique: list[dict]) -> list[dict]:
    lex_terms = [(e.get("terme_ar", ""), e.get("definition_ar", "")) for e in lexique if e.get("terme_ar")]
    out = []
    for i, mc in enumerate(mcs, 1):
        unit_id = map_mc_to_unit(mc, units)
        titre = mc.get("nom_ar") or mc.get("nom_fr", "Concept")
        # phrase clé : définition du lexique si trouvée, sinon le concept
        phrase = titre
        for term, definition in lex_terms:
            if term and (term in titre or titre in term):
                phrase = definition.strip()
                break
        out.append({
            "id": mc.get("id") or f"mc_{i:03d}",
            "titre": titre,
            "phrase_cle": phrase[:280],
            "erreur_frequente": f"خلط {titre} بمفهوم مشابه أو نسيان الشروط — خطأ شائع في البكالوريا",
            "mnemo": f"راجع: {mc.get('nom_fr', titre)[:60]}",
            "points_bac": 0.5 if mc.get("importance") != "critique" else 1.0,
            "niveau": "critique" if mc.get("importance") == "critique" else "moyen",
            "unit_id": unit_id,
            "bac_frequent": bool(mc.get("bac_frequent", True)),
        })
    return out


def main() -> None:
    mcs = load_canonical()
    units = load_units()
    lexique = load_lexique()
    phrases, erreurs = load_livre_tips()

    micro = build_micro_concepts(mcs, units, lexique)
    from collections import Counter
    counts = Counter(m["unit_id"] for m in micro)

    unites = []
    for u in units:
        unites.append({
            "unit_id": u["id"],
            "titre_fr": u["unit_ar"],
            "titre_ar": u["unit_ar"],
            "position": int(u["id"][1:]),
            "mc_count": counts.get(u["id"], 0),
        })

    payload = {
        "generated_from": ["programme_svt_3as_canonical.json", "services/units.py", "الكتاب_المصحح_v1.0.md", "lexique_svt_terminale_complet.json"],
        "micro_concepts": micro,
        "unites": unites,
        "phrases_bac_clefs": phrases or ["الاستنساخ في النواة، الترجمة في الهيولى"],
        "erreurs_graves": erreurs or ["خلط الاستنساخ بالترجمة"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Écrit {OUT}")
    print(f"  micro_concepts: {len(micro)} | unites: {len(unites)} | phrases: {len(phrases)} | erreurs: {len(erreurs)}")
    print(f"  répartition: {dict(counts)}")


if __name__ == "__main__":
    main()
