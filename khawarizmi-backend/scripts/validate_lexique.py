"""Validate the generated lexique JSON."""

import json

path = "data/lexique_svt_terminale_complet.json"
with open(path, encoding="utf-8") as f:
    raw = f.read()

print("=== ENCODING ===")
print(f"File size: {len(raw.encode('utf-8'))} bytes")
ar_check = "البروتينات" in raw
print(f"Arabic preserved: {ar_check}")

d = json.loads(raw)
all_terms = [t for dom in d["domaines"] for cat in dom["categories"] for t in cat["termes"]]

print("\n=== STRUCTURE ===")
print(f"Metadata total_entrees: {d['metadata']['total_entrees']}")
print(f"Domaines: {len(d['domaines'])}")

errors = []
for _di, dom in enumerate(d["domaines"]):
    for _ci, cat in enumerate(dom["categories"]):
        for _ti, t in enumerate(cat["termes"]):
            for field in [
                "id",
                "terme_fr",
                "terme_ar",
                "type",
                "definition_fr",
                "definition_ar",
                "importance",
                "chapitre_principal",
            ]:
                if not t.get(field):
                    errors.append(f"{t.get('id', '?')} missing {field}")
            if t.get("type") not in [
                "molecule",
                "enzyme",
                "concept",
                "processus",
                "cellule",
                "organite",
                "structure",
                "mecanisme",
            ]:
                errors.append(f"{t.get('id')} invalid type: {t.get('type')}")
            if t.get("importance") not in ["critique", "haute", "moyenne"]:
                errors.append(f"{t.get('id')} invalid importance: {t.get('importance')}")

print("\n=== VALIDATION ===")
print(f"Total terms: {len(all_terms)}")
print(f"Errors: {len(errors)}")
for e in errors[:10]:
    print(f"  - {e}")

print("\n=== STATS ===")
c = sum(1 for t in all_terms if t["importance"] == "critique")
h = sum(1 for t in all_terms if t["importance"] == "haute")
m = sum(1 for t in all_terms if t["importance"] == "moyenne")
print(f"Critique: {c} | Haute: {h} | Moyenne: {m}")
print(f"Bac_frequent: {sum(1 for t in all_terms if t['bac_frequent'])}")
types = {}
for t in all_terms:
    types[t["type"]] = types.get(t["type"], 0) + 1
print(f"Types: {dict(sorted(types.items()))}")
print(f"Cross-links: {len(d['liens_transversaux'])}")

# Sample
import random

print("\n=== SAMPLE ===")
for t in random.sample(all_terms, min(5, len(all_terms))):
    print(f"  {t['id']}: {t['terme_fr']} ({t['terme_ar']}) [{t['importance']}]")
