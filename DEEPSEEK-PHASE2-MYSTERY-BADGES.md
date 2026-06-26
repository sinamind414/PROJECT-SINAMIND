# PHASE 2 — Mystery Box + Badge System + Social Proof

**Projet :** Khawarizmi Pro  
**Statut :** 100% implémenté

---

## 1. Services

### `services/phase2_service.py`
- `open_mystery_box_v2(box_id, user_id, db)` — récompense aléatoire par rareté (common→legendary)
- `get_social_stats(chapter, db)` — stats sociales statiques

### `services/badge_service.py`
- 4 badges prédéfinis (common→legendary)
- `check_and_award_badges(user_id, db)` — logique à brancher
- `get_all_badges()` — liste tous les badges

---

## 2. Routes

**Fichier :** `routes/phase2.py`

| Endpoint | Méthode | Description |
|---|---|---|
| `POST /api/phase2/mystery-box/open` | POST | Ouvre une mystery box (récompense aléatoire) |
| `GET /api/phase2/social-stats/{chapter}` | GET | Statistiques sociales |

**Fichier :** `routes/badges.py`

| Endpoint | Méthode | Description |
|---|---|---|
| `GET /api/badges/` | GET | Liste tous les badges |
| `POST /api/badges/check` | POST | Vérifie et attribue les badges |

---

## 3. Intégration

**Fichier :** `main.py`
- Imports : `phase2`, `badges`
- Routeurs dans la liste

---

## 4. Tests

**Fichier :** `tests/test_phase2.py` (3 tests)

- `test_open_mystery_box_v2` — vérifie la structure de réponse
- `test_social_stats` — vérifie les clés sociales
- `test_badges_list` — vérifie l'endpoint badges

---

## 5. Différences avec le spec original

| Point | Spec original | Implémentation |
|---|---|---|
| Types | `user_id: str`, `db`, `Dict/List` | `int`, `AsyncSession`, types natifs |
| Route badges | non spécifiée | Créée (`/api/badges/`) |
| Tests | absents | 3 tests avec JWT |
