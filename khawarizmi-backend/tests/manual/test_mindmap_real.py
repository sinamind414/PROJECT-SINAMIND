# test_mindmap_real.py
# Test manuel E2E — Validation chaîne RAG → LLM → Mind Map
# Usage : python tests/manual/test_mindmap_real.py
# Nécessite : backend sur localhost:8000, utilisateur demo-mindmap@khawarizmi.dz

import json
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

print("=" * 60)
print("VALIDATION CHAINE COMPLETE — KHAWARIZMI PRO")
print("=" * 60)

# Étape 1 — Login
print("\n[1/3] Login...")
login_data = json.dumps({"email": "demo-mindmap@khawarizmi.dz", "password": "Demo1234!"}).encode("utf-8")

req = urllib.request.Request(
    "http://localhost:8000/api/auth/login", data=login_data, headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req) as f:
        res = json.loads(f.read().decode("utf-8"))
        token = res["access_token"]
        print(f"  OK Token recu: {token[:30]}...")
except Exception as e:
    print(f"  ECHEC Login: {e}")
    sys.exit(1)

# Étape 2 — Génération Mind Map
print("\n[2/3] Generation Mind Map (Transcription ADN)...")
mindmap_data = json.dumps(
    {
        "matiere": "SVT",
        "chapitre": "Transcription de l'information genetique au niveau de l'ADN",
        "filiere": "Sciences Experimentales",
        "niveau_detail": "standard",
    }
).encode("utf-8")

req = urllib.request.Request(
    "http://localhost:8000/api/mindmap/generate",
    data=mindmap_data,
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
)

try:
    with urllib.request.urlopen(req, timeout=60) as f:
        res = json.loads(f.read().decode("utf-8"))
        print(f"  OK Reponse recue (status: {res.get('status', '?')})")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"  ECHEC HTTP {e.code}: {body[:500]}")
    sys.exit(1)
except Exception as e:
    print(f"  ECHEC: {e}")
    sys.exit(1)

# Étape 3 — Validation du contenu
print("\n[3/3] Validation du contenu...")

mindmap = res.get("mindmap", {})
racine = mindmap.get("racine", {})

print(f"\n  Titre: {mindmap.get('titre', 'N/A')}")
print(f"  Racine: {racine.get('label', 'N/A')}")
print(f"  Nb enfants: {len(racine.get('enfants', []))}")

if racine.get("enfants"):
    print("\n  Enfants generes:")
    for child in racine["enfants"]:
        label = child.get("label", "?")
        importance = child.get("importance", "?")
        nb_sub = len(child.get("enfants", []))
        couleur = child.get("couleur", "?")
        bac = "BAC" if child.get("bac_frequent") else ""
        print(f"    - {label} [{importance}] ({nb_sub} sous-enfants) {bac} {couleur}")
else:
    print("\n  ATTENTION: Aucun enfant genere")

# Vérification présence de vrais termes scientifiques
contenu_str = json.dumps(mindmap).lower()
termes_attendus = ["polymerase", "promoteur", "initiation", "elongation", "transcription", "arn", "adn"]
termes_trouves = [t for t in termes_attendus if t in contenu_str]

print(f"\n  Termes scientifiques trouves: {len(termes_trouves)}/{len(termes_attendus)}")
for t in termes_trouves:
    print(f"    OK {t}")
for t in termes_attendus:
    if t not in termes_trouves:
        print(f"    MANQUE {t}")

# Structure JSON détaillée
print("\n  Structure complete:")
print(json.dumps(mindmap, indent=2, ensure_ascii=False)[:2000])

# Vérification flashcards
flashcards = res.get("flashcards_generees", [])
print(f"\n  Flashcards generees: {len(flashcards)}")
for fc in flashcards:
    print(f"    Recto: {fc.get('recto', '?')}")

# Vérification source RAG
source = res.get("source_rag", "")
print(f"\n  Source RAG: {source}")

# Verdict
print("\n" + "=" * 60)
nb_enfants = len(racine.get("enfants", []))
if nb_enfants >= 2 and len(termes_trouves) >= 3:
    print("VICTOIRE TOTALE - Mind Map genere avec vrai contenu!")
    print(f"  {nb_enfants} enfants, {len(termes_trouves)} termes, {len(flashcards)} flashcards")
elif nb_enfants >= 1:
    print("PARTIEL - Mind Map genere mais contenu a verifier")
else:
    print("ECHEC - Mind Map vide ou mal genere")
print("=" * 60)
