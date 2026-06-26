# PHASE 1 — One More Click Loop + Combo System

**Projet :** Khawarizmi Pro  
**Statut :** 100% implémenté — conforme aux conventions du projet

---

## 1. MODÈLE SQLAlchemy

**Fichier :** `models/phase1.py`

| Modèle | Table | Colonnes |
|---|---|---|
| `ComboState` | `combo_states` | `user_id` (PK, FK→users.id), `current_combo`, `max_combo` |

Le combo est stocké en base : persistant entre les sessions, récupérable à la reconnexion.

---

## 2. SERVICE

**Fichier :** `services/phase1_service.py`

### `get_next_actions(user_id, last_action, db) → list[dict]`
Retourne 3 actions suggérées invariantes (Phase 1) :
1. **Continuer sur ce chapitre** (+15 pts) — `next_lesson`
2. **Faire un quiz rapide** (+25 pts) — `quick_quiz`
3. **Défi du jour** (+40 pts) — `daily_challenge`

### `calculate_combo(user_id, success, db) → dict`
Logique combo avec état DB :
- **Succès** : `current_combo++`, `multiplier = min(1 + current_combo // 3, 5)`, `points = 10 * multiplier`
- **Échec** : `current_combo = 0`, combo cassé

---

## 3. ROUTES

**Fichier :** `routes/phase1.py`

| Endpoint | Méthode | Body | Réponse |
|---|---|---|---|
| `POST /api/phase1/next-actions` | POST | `{"last_action": "..."}` | `{"actions": [...]}` |
| `POST /api/phase1/combo` | POST | `{"success": true/false}` | `{"multiplier", "points_earned", "combo_count", "message"}` |

Tous les endpoints sont protégés par JWT.

---

## 4. INTÉGRATION

**Fichier :** `main.py`
- Import : `phase1` dans le bloc `from routes import (...)`
- Routeur : `phase1.router` dans la liste `routers`

**Fichier :** `models/__init__.py`
- Export : `ComboState`

---

## 5. TESTS

**Fichier :** `tests/test_phase1.py` (5 tests)

- `test_next_actions_requires_auth` — vérifie la protection JWT
- `test_next_actions` — retourne 3 actions
- `test_combo_success` — combo incrementé
- `test_combo_failure` — combo reset à 0
- `test_combo_escalates_multiplier` — x2 après 3 succès consécutifs

---

## 6. DIFFÉRENCES AVEC LE SPEC ORIGINAL

| Point | Spec original | Implémentation |
|---|---|---|
| `user_id` type | `str` | `int` (convention projet) |
| `db` type hint | absent | `AsyncSession` |
| État combo | en mémoire, non utilisé | stocké en DB (`ComboState`) |
| `multiplier` calcul | constant x2 | `min(1 + count // 3, 5)` |
| `points_earned` | constant 20 | `10 * multiplier` |
| Tests | absents | 5 tests avec `auth_headers` |

---

**Migration DB requise :** `alembic revision --autogenerate -m "007_phase1_combo"`
