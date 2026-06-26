# PHASE 0 — Finalisation (Streak + Points + Mystery Box + Avatar)

**Projet :** Khawarizmi Pro  
**Statut :** 100% implémenté — conforme aux conventions du projet

---

## 1. MODÈLES SQLAlchemy

**Fichier :** `khawarizmi-backend/models/gamification.py`

| Modèle | Table | Clé |
|---|---|---|
| `UserStreak` | `user_streaks` | `user_id` (FK → users.id) |
| `UserPoints` | `user_points` | `user_id` (FK → users.id) |
| `UserAvatar` | `user_avatars` | `user_id` (FK → users.id) |
| `Badge` | `badges` | `id` (UUID) |
| `UserBadge` | `user_badges` | `user_id` + `badge_id` (composite FK) |
| `MysteryBox` | `mystery_boxes` | `id` (UUID) |

**Conventions respectées :**
- `user_id` en `Integer` avec `ForeignKey("users.id", ondelete="CASCADE")` (aligné sur le PK de `User`)
- Types : `Date` pour les dates, `Boolean` pour les flags, `JSONB` pour `content_value`
- `nullable=False` sur les colonnes critiques

---

## 2. SERVICES

### 2.1 Gamification Service
**Fichier :** `services/gamification_service.py`
- `get_or_create_streak(user_id, db)` → crée ou retourne le streak
- `update_streak(user_id, db)` → incrémente/réinitialise selon `last_activity`
- `add_points(user_id, points, db)` → cumul points total + hebdo

### 2.2 Avatar Service
**Fichier :** `services/avatar_service.py`
- Niveaux : `[0, 200, 600, 1200, 2500, 4500]` XP
- `get_user_avatar(user_id, db)` → création auto si inexistant
- `add_xp(user_id, xp, db)` → ajoute XP, calcule le level, signale `leveled_up`

### 2.3 Mystery Box Service
**Fichier :** `services/mystery_box_service.py`
- `open_mystery_box(box_id, user_id, db)` → retourne récompense
- `create_mystery_box(user_id, rarity, db)` → crée une nouvelle box
- `get_available_boxes(user_id, db)` → liste des boxes disponibles

---

## 3. ROUTES

### 3.1 Gamification — `routes/gamification.py`

| Endpoint | Méthode | Description |
|---|---|---|
| `/api/gamification/streak/update` | POST | Met à jour le streak quotidien |
| `/api/gamification/streak` | GET | Récupère le streak actuel |
| `/api/gamification/points/add?points=N` | POST | Ajoute N points |

### 3.2 Mystery Box — `routes/mystery_box.py`

| Endpoint | Méthode | Description |
|---|---|---|
| `/api/mystery-box/open` | POST | Ouvre une boîte (body: `{"box_id": "..."}`) |
| `/api/mystery-box/create?rarity=X` | POST | Crée une boîte |
| `/api/mystery-box/available` | GET | Liste les boîtes disponibles |

### 3.3 Avatar — `routes/avatar.py`

| Endpoint | Méthode | Description |
|---|---|---|
| `/api/avatar/` | GET | Récupère l'avatar (level, xp) |
| `/api/avatar/add-xp?xp=N` | POST | Ajoute N XP |

---

## 4. AUTH

Tous les endpoints sont protégés par JWT via `get_current_user` (Bearer token).

---

## 5. TESTS

**Fichier :** `tests/test_gamification.py` (8 tests)
**Fichier :** `tests/test_gamification_phase0.py` (8 tests)

- Utilisation des fixtures `client` + `auth_headers` du projet
- Tests : streak update, points, XP, avatar, mystery box (open/create/available)

---

## 6. INTÉGRATION

**Fichier :** `main.py`
- Imports : `gamification`, `mystery_box`, `avatar`
- Routeurs enregistrés dans la liste `routers`

**Fichier :** `models/__init__.py`
- Export : `UserStreak`, `UserPoints`, `UserAvatar`, `Badge`, `UserBadge`, `MysteryBox`

---

## 7. ENDPOINTS FINAUX

| Endpoint | Méthode | Auth |
|---|---|---|
| `POST /api/gamification/streak/update` | POST | JWT |
| `GET /api/gamification/streak` | GET | JWT |
| `POST /api/gamification/points/add?points=N` | POST | JWT |
| `POST /api/mystery-box/open` | POST | JWT |
| `POST /api/mystery-box/create?rarity=X` | POST | JWT |
| `GET /api/mystery-box/available` | GET | JWT |
| `GET /api/avatar/` | GET | JWT |
| `POST /api/avatar/add-xp?xp=N` | POST | JWT |

---

**Migration DB requise :** `alembic revision --autogenerate -m "006_gamification_phase0"`
