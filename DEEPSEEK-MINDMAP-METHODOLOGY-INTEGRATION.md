# Mind Map — Intégration Méthodologique

**Projet :** Khawarizmi Pro  
**Statut :** 100% implémenté

---

## 1. Service

**Fichier :** `services/mindmap_methodology_service.py`

| Fonction | Rôle |
|---|---|
| `enrich_mindmap_with_methodology(mindmap_data)` | Enrichit chaque nœud avec le verbe d'action détecté |
| `generate_methodological_mindmap(matiere, chapitre, filiere, user_id, db, openai)` | Génère un Mind Map + enrichissement méthodologique |
| `award_mindmap_methodology_points(user_id, mindmap_data, db)` | Calcule les points (15/verbe, +30 si 2 verbes complexes) |

**Logique d'enrichissement :**
- Parcourt récursivement les nœuds du Mind Map
- Pour chaque label, détecte le verbe via `methodology.verb_database.get_verb()`
- Ajoute les métadonnées : verbe, type, max_score, conseil
- Calcule le score méthodologique total

---

## 2. Routes

**Fichier :** `routes/mindmap.py` (ajout)

| Endpoint | Méthode | Auth | Description |
|---|---|---|---|
| `POST /api/mindmap/generate-methodological` | POST | JWT | Génère Mind Map enrichi |

Body : `{matiere, chapitre, filiere}`

---

## 3. Tests

**Fichier :** `tests/test_mindmap_methodology_integration.py` (3 tests)

- Auth requis
- Enrichissement avec verbes détectés
- Calcul des points
