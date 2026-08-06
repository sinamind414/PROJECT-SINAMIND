# Rapport — Tests de toutes les routes + correspondance site ↔ backend

**Date :** 2026-08-06 — **Méthode :** serveur réellement booté (uvicorn, SQLite preview) + auth JWT complète (register → login → me) + analyse du contrat frontend↔backend + suites de tests.

---

# 1. Résultat des suites de tests

| Suite | Résultat | Détail |
|---|---|---|
| Backend `pytest tests/` (57 fichiers) | 🟢 **624 passed** / 4 failed / 1 skipped / 5 xfailed | les 4 échecs sont **pré-existants** (mocks obsolètes `pulse_service` ×3, attente `llm_recovered` ×1) — non liés aux routes |
| Frontend `vitest` | 🟢 **592/592 passed** (9 fichiers) | intact |
| Frontend `eslint` | 🟠 1 erreur + 21 warnings | inchangé (pré-existant) |
| Boot serveur | 🟢 startup complet, 189 routes API, 0 doublon | après corrections |

---

# 2. Bugs trouvés par le test des routes (et corrigés)

## 🔴 P0-1 — L'inscription et le login ne fonctionnaient pas (aucun commit)
**Symptôme :** `POST /api/auth/register` → 200 avec token, mais `GET /api/auth/me` → 401 « Token invalide ou expiré ».
**Cause :** `routes/auth.py` faisait `INSERT INTO users ... RETURNING` (register) et `UPDATE users SET last_active` (login) **sans jamais appeler `db.commit()`**. La session `get_db` est en lecture seule (rollback à la fermeture) → l'utilisateur était **annulé après chaque inscription** → token inutilisable. **Aucun élève ne pouvait s'inscrire.**
**Fix :** `await db.commit()` ajouté dans register et login. **Testé :** register → me → login → 200 OK, l'utilisateur persiste.

## 🔴 P0-2 — Page d'accueil (`/api/aujourdhui`) en 500
**Symptôme :** 500 `FileNotFoundError: data/essential/bac_essentials.json`.
**Cause :** fichier requis par la mission du jour (accueil post-login) **absent du dépôt** (data/ gitignoré, jamais commité).
**Fix :** générateur `scripts/generate_bac_essentials.py` + fichier généré (force-addé) :
- **57 micro-concepts** officiels (canonical ONEC) mappés aux **11 unités du livre** (u1–u11, ordre officiel)
- 11 unités aux **noms officiels du livre** (`units.py`)
- **18 phrases clés BAC** extraites des « 🎓 نصائح البكالوريا » du livre corrigé + erreurs graves
**Testé :** mission du jour (concept + unité + QCM), matrix (57 MC / 11 unités), fiche J-1 (18 phrases), valider (progression enregistrée) → **tous 200 OK**.

## 🟠 P1-1 — Mode preview SQLite inutilisable
- `aiosqlite` **absent de `requirements.txt`** → le mode preview (codé dans le lifespan) échouait à chaque boot → `aiosqlite==0.21.0` ajouté.
- `is_sqlite = db_url.startswith("sqlite://")` ne matchait pas `sqlite+aiosqlite://` → bloc de création automatique des tables sauté → fix → **80 tables créées automatiquement**.

## 🟠 P1-2 — Coquille dans le programme officiel
« آليات تحويل الطاقة **الكيمائية** الكامنة » → « **الكيميائية** » (fallback + JSON programmes).

---

# 3. Correspondance site ↔ backend (contrat)

Analyse automatique des **95 chemins API littéraux** de `api-client.ts` contre les **189 routes réelles** de l'app bootée :

| État | Nombre | Détail |
|---|---|---|
| ✅ Matchent | **85** | toutes les routes utilisées par des pages réelles |
| 🔀 Redirect 307 | 1 | `/api/flashcards/methodology` → `/api/flashcards/methodology/` (route avec slash final) |
| ⚪ Méthodes mortes | 9 | aucun composant/pages ne les appelle (vérifié par grep) |

**Les 9 méthodes mortes (aucun impact utilisateur) :** `/api/coach/*` ×4, `/api/tuteur`, `/api/social/blog/posts` + `/vote`, `/api/social/messenger/*` ×2.

## Réactivation des routeurs (4) — pages réelles réparées
Les fichiers de routes existaient mais n'étaient **plus enregistrés** dans `ALL_ROUTERS` :

| Routeur | Endpoints | Pages réparées |
|---|---|---|
| `aujourdhui` | `/api/aujourdhui` + `/matrix` + `/fiche-j1` + `/valider` + `/dix-minutes` | **Page d'accueil post-login**, « 10 minutes », « Fiche J-1 », « Progress » |
| `lessons` | `/api/lessons/{slug}` + `/{slug}/check` | **Leçons actives** (`ActiveLesson.tsx`) |
| `bac_blanc` | `/api/bac-blanc/start|choose|save|submit|{id}/correction` | **Bac Blanc immersif** (`BacBlancImmersif.tsx`) |
| `document_analysis` | `/api/document-analysis/scenarios`, `/progress`, `/weak-spots` | **Document Analysis** (page + v1 scenarios) |

Vérifié : **189 routes, 0 doublon** (le doublon potentiel de `chat.py` n'est pas ré-enregistré — `/api/chat` n'est utilisé par aucune page).

---

# 4. Tests de routes en conditions réelles (serveur booté + JWT)

| Route | Méthode | Résultat |
|---|---|---|
| `/health` | GET | 🟢 200 (degraded sans Redis — comportement attendu) |
| `/api/auth/register` | POST | 🟢 200 + token |
| `/api/auth/me` | GET | 🟢 200 (id, email, plan) |
| `/api/auth/login` | POST | 🟢 200 + token |
| `/api/programme/SVT/Sciences Experimentales` | GET | 🟢 200 — **3 domaines, 11 unités, 55 chapitres** (noms officiels du livre, arabe correct) |
| `/api/programme/_debug/status` | GET | 🟢 200 |
| `/api/cours/list` | GET | 🟢 200 (55 chapitres) |
| `/api/cours/{titre}` | GET | 🟢 200 (contenu du cours) |
| `/api/exercices/{chapitre}` | GET | 🟠 404 propre (aucune donnée seedée en preview) |
| `/api/lexique/search?q=ADN` | GET | 🟠 200 vide (DB non seedée en preview) |
| `/api/flashcards/due` | GET | 🟢 200 |
| `/api/videos/all` | GET | 🟢 200 |
| `/api/progress` | GET | 🟢 200 |
| `/api/chatbot/ask` | POST | 🟢 200 (réponse déterministe, fallback local, 0 token) |
| `/api/chatbot/health` | GET | 🟢 200 |
| `/api/aujourdhui` | GET | 🟢 200 (mission du jour) |
| `/api/aujourdhui/matrix` | GET | 🟢 200 (57 MC, 11 unités) |
| `/api/aujourdhui/fiche-j1` | GET | 🟢 200 (18 phrases clés du livre) |
| `/api/aujourdhui/valider` | POST | 🟢 200 (progression enregistrée) |
| `/api/lessons/{slug}` | GET | 🟠 404 propre (leçon absente de la DB preview) |
| `/api/bac-blanc/start` | POST | 🟠 404 propre (sujets non seedés en preview) |
| `/api/document-analysis/progress` | GET | 🟢 200 |
| `/api/document-analysis/scenarios` | GET | 🟠 500 en preview (table `da_scenarios` de migration, schéma absent en SQLite) |
| `/api/flashcards/methodology` | GET | 🟢 307 → route avec slash |

**Note :** les 500 restants en preview sont dus aux tables de migrations absentes du mode SQLite (schéma minimal) — **non reproductibles en production** (PostgreSQL + `alembic upgrade head` applique le schéma complet ; les scripts `seed_lessons.py`, `seed_bac_blanc.py` existent pour les données).

---

# 5. Ce qui reste (documenté, hors périmètre)

1. **4 tests backend en dérive** : `test_pulse_service.py` ×3 (mock `last_activity`), `test_correction_v2_retry.py` (attente `llm_recovered`) — à réparer.
2. **Méthodes mortes de l'api-client** (coach ×4, tuteur, blog/messenger ×4) : soit créer les endpoints backend, soit supprimer les méthodes — aucun impact utilisateur actuellement.
3. **`routes/static_content.py` et `worker/worker.py` manquants** (imports optionnels) — dégradation silencieuse au boot (déjà documenté à l'audit global).
4. **`configure_limiter_storage` inexistant** dans `rate_limit.py` → le rate limiting reste en mémoire même quand Redis est dispo (warning au boot).
5. **Embedder ONNX corrompu** : `model_quantized.onnx` → `INVALID_PROTOBUF` → fallback déterministe actif (le RAG sémantique est en mode dégradé).
