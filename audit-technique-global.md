# Audit technique global — IA Khawarizmi Pro

**Date :** 2026-08-06 — **Commit audité :** `cbe1a3a` (merge PR #9, main)
**Périmètre :** `khawarizmi-backend` (FastAPI), `khawarizmi-frontend` (Next.js 16), CI/CD, hygiène du dépôt.
**Méthode :** lecture statique + vérification runtime (import de l'app, listing OpenAPI, boot uvicorn, `pytest` backend, `vitest` + lint + build frontend).

---

# 1. Verdict synthèse

| Axe | Note | Constat clé |
|---|---|---|
| Démarrage backend | 🔴 **BLOQUÉ** | `ModuleNotFoundError: app_state` — corrigé dans cette session (voir §6) |
| Contrat frontend ↔ backend | 🔴 **18+ endpoints appelés par le frontend absents du backend** | pages principales en 404 |
| Tests backend | 🟠 624 pass / 4 fail (après fix) | la suite ne pouvait même pas se collecter avant |
| Tests frontend | 🟢 592/592 pass | sain |
| Lint frontend | 🟠 1 erreur + 21 warnings | CI en `continue-on-error` |
| Sécurité | 🟡 globalement saine | 1 endpoint admin sans rôle admin, 1 fragilité JWT |
| Hygiène dépôt | 🟡 49 Mo de `data/` trackés, artefacts de dev commités | |
| CI | 🔴 **ne protège pas la prod** | merge sans checks exécutés |

**En une phrase :** le code est de bonne qualité, mais le dépôt, tel que mergé sur `main`, **ne peut pas démarrer** et le frontend appelle **~19 endpoints qui n'existent pas** — l'application en production est très probablement en panne ou fortement dégradée.

---

# 2. Découvertes critiques (P0)

## P0-1 — `app_state.py` manquant → backend injoignable (CORRIGÉ, voir §6)

**Fait vérifié :**
- `database.py:25` et `routes/lifespan.py:19` font `from app_state import state` ; le fichier **n'existe ni dans l'arbre de travail ni dans tout l'historique git** (387 commits vérifiés).
- `python -c "from main import app"` → `ModuleNotFoundError: No module named 'app_state'`.
- La chaîne est totale : `alembic upgrade head` (CMD Docker) → `migrations/env.py` → `from models import Base` → `from database import Base` → **crash**. `uvicorn main:app` → **crash**. Les 57 fichiers de tests backend → **échec de collecte** (0 test exécutable).

**Cause racine (git-blame) :** le commit `bdad539` a déplacé le dataclass `AppState` (qui vivait dans `routes/lifespan.py`) vers un module `app_state.py`… **sans jamais committer le fichier**. Le PR #9 a été mergé sans que les checks CI ne soient exécutés (statut du commit de merge : `pending`, 0 check-run) → la régression est arrivée sur `main` silencieusement.

## P0-2 — Le frontend appelle 18+ endpoints absents du backend

Comparaison automatique des chemins littéraux de `src/lib/api-client.ts` + appels de pages contre les **176 routes réelles** de l'app (vérifié sur l'app bootée) :

| Endpoint appelé (frontend) | Endpoints exposés (backend) | Feature cassée |
|---|---|---|
| `GET /api/aujourdhui`, `/matrix`, `/fiche-j1`, `POST /valider`, `/dix-minutes` (×2) | **aucun** (`routes/aujourdhui.py` non enregistré) | **Page d'accueil post-login** (`/aujourdhui`, `page.tsx:32`), pages `dix-minutes`, `fiche-j1`, `progress` → 404 |
| `POST /api/chatbot/ask/stream` (SSE) | seul `/api/chatbot/ask` (JSON non-streaming) existe | **Conversation chatbot principale** → 404 (le frontend ne fait jamais appel à `/ask`) |
| `/api/bac-blanc/start`, `/choose`, `/save`, `/submit`, `/{id}/correction` | seulement `/api/bac-blanc/feedback` + `/action-plan` | **Bac Blanc immersif** (`BacBlancImmersif.tsx`) → 404 |
| `/api/document-analysis/evaluate`, `/progress`, `/weak-spots`, `/scenarios`, `/scenarios/{slug}`, `/{slug}/correction` | seulement `/api/document-analysis/evaluate-v2` | **Document Analysis** → 404 (hors éval v2) |
| `/api/lessons/{slug}`, `/{slug}/check` | **aucun** | **Leçons actives** (`ActiveLesson.tsx`) → 404 |
| `/api/coach/lois`, `/reflexes`, `/survival-cards`, `/validate` | **aucun** | **Coach méthodologique** (`CoachPanel.tsx`) → 404 |
| `/api/tuteur` | **aucun** (`tuteur.py` non enregistré) | `apiClient.tuteur()` → 404 |
| `/api/social/blog/posts`, `/posts/{id}/vote` | `/api/social/blog` (paths différents) | Blog social → 404 |
| `/api/social/messenger/conversations`, `/…/messages` | `/api/social/conversations` | Messenger → 404 |

**Cause racine :** un refactor a retiré de `ALL_ROUTERS` (`routes/__init__.py`) 13 fichiers de routes **complets et fonctionnels** (`aujourdhui`, `lessons`, `tuteur`, `chat`, `evaluate`, `bac_blanc`, `document_analysis`, `phase2`, `phase4`, `aujourdhui`…). `chat.py` ne peut pas être ré-enregistré tel quel : il définit `GET /api/chapitres/{matiere}`, en **conflit de route** avec `chapitres.py` (déjà enregistré) → le serveur ne démarrerait pas (assertion FastAPI). C'est probablement la raison du retrait.

---

# 3. Découvertes élevées (P1)

## P1-1 — CI inopérante : le merge s'est fait sans checks
- `.github/workflows/ci.yml` : le job backend ne lance qu'un **sous-ensemble** (methodology, diagnostic, couche3, tutor, bac_blanc_intelligent, mindmap_methodology) — pas la suite complète, et **avec `REDIS_URL` pointant sur localhost sans service Redis** dans le job.
- Lint frontend : `continue-on-error: true` (l'erreur `no-explicit-any` actuelle ne bloque pas).
- Statut du commit de merge `cbe1a3a` : `pending` / 0 check-run → **rien n'a détecté le P0-1**.

## P1-2 — `/api/admin/analytics/*` accessible à tout utilisateur authentifié
`admin_analytics.py` (`/global`, `/methodology-gaps`, `/students-at-risk` — données élèves) ne dépend que de `get_current_user`. Aucune vérification de rôle admin. Contraste : `admin_ingest.py` exige bien un `ADMIN_SECRET`.

## P1-3 — Build Next.js fragile hors réseau
`npm run build` échoue si `fonts.googleapis.com` est injoignable (`next/font` Google — police Cairo, `layout.tsx`). Échec reproduit dans le sandbox. En CI GitHub (réseau ouvert) cela passe ; sur un runner restreint ou en build offline, **build rouge**. Recommandation : self-hoster la police (ou `next/font/local`).

## P1-4 — README et réalité divergents
- README annonce « tests/ — Pytest (13 fichiers, couverture ≥ 50 %) » → il y a **57 fichiers** de tests ; aucune config de couverture n'existe (`pytest.ini` sans `--cov`).
- README annonce un `docker compose up --build` → **aucun `docker-compose.yml` à la racine** (il existe dans `khawarizmi-backend/`).

---

# 4. Découvertes moyennes (P2)

## P2-1 — 4 tests backend en échec (dérive tests ↔ code, non liés au P0-1)
Après correction du P0-1 : `624 passed, 4 failed, 1 skipped, 5 xfailed`.
- `test_pulse_service.py` ×3 : `AttributeError: Mock object has no attribute 'last_activity'` — les mocks des tests ne collent plus au service (`pulse_service` attend désormais `last_activity`).
- `test_correction_v2_retry.py` : attend `source == "llm_recovered"`, reçoit `"llm"`.

## P2-2 — Fragilité JWT dans `deps.get_current_user`
`jwt.decode(..., options={"verify_sub": False})` puis `int(payload.get("sub"))` : si le claim `sub` est absent, `int(None)` lève `TypeError` **non capturée** → 500 au lieu du 401 attendu. Retirer l'option et valider `sub` proprement.

## P2-3 — Fichiers référencés mais jamais créés (dégradation silencieuse)
- `worker/worker.py` (arq) — import dans le lifespan sous `try/except` : la file de jobs est **silencieusement désactivée** en production (log warning seulement).
- `routes/static_content.py` — idem pour le préchargement des contenus statiques.
- Conséquence : deux capacités « prévues » ne s'exécutent nulle part, sans erreur visible.

## P2-4 — Lint frontend : 1 erreur + 21 warnings
Erreur : `no-explicit-any` dans `src/app/aujourdhui/page.tsx:268`. 21 warnings de variables inutilisées (dont `Sidebar.tsx` : 4 imports morts).

---

# 5. Découvertes faibles / hygiène (P3)

- **`khawarizmi-backend/data/` (49 Mo, 3360 fichiers)** : dans `.gitignore` mais **déjà trackés** (PDF d'annales, OCR pages_txt, `run.state.json`…) → gonfle le clone et le déploiement. À retirer du suivi (`git rm -r --cached`) si le runtime ne dépend que du fallback JSON.
- **Artefacts de dev commités en racine** : 8 captures PNG (~7 Mo), `response-54.network-response`, `الكتاب_المصحح_v1.0 (1).md` (276 Ko), `LIVRE-MANHADJIYA.md` **dupliqué** (racine + `khawarizmi-backend/`, 356 Ko chacun).
- **Deux Dockerfiles identiques** (racine + backend) et deux `railway.toml` — risque de divergence ; le CI déploie depuis `khawarizmi-backend/`.
- **`CACHEBUST=20260704A` codé en dur** dans les Dockerfiles ; `.railway-cache-bust` / `.vercel-trigger` servent de cache-bust manuels — mécanique fragile mais fonctionnelle.
- **Modules legacy non enregistrés** : `bac_blanc.py` (entier, ~400 lignes) vs `bac_blanc_intelligent.py` ; `document_analysis.py` vs `v2` ; `chat.py` vs `ai_chat.py` ; `evaluate.py` vs `ai_evaluate.py` — code mort maintenu en double. `check_legacy_usage.py` existe mais rien ne le fait tourner en CI.
- `requirements.txt` épinglé précisément (bon point) ; `bcrypt==4.0.1` volontairement figé pour compatibilité passlib (assumé, mais à surveiller).

---

# 6. Ce qui va bien (vérifié)

1. **`llm_guard.py` — défense en profondeur exemplaire** : opt-in double (`ENABLE_EXTERNAL_LLM=1` + clé), scrub des variables d'env, blackhole httpx sur les domaines LLM connus, client « gardé » qui lève `LLMDisabledError`, fallback déterministe local. C'est le meilleur morceau du projet.
2. **Auth** : JWT uniquement, token **en mémoire** côté frontend (aucun `localStorage`), `SECRET_KEY` obligatoire ≥ 16 chars avec `ValueError` en production, cookies + Bearer supportés.
3. **Rate limiting** : SlowAPI par user/plan (`20/h` free vs `100/h` pro sur chat), storage Redis avec repli mémoire.
4. **CORS** : liste explicite d'origines, méthodes et headers restreints, `allow_origin_regex` supprimé (choix assumé).
5. **Aucun secret committé** : scan des patterns (`sk-`, `gsk_`, `AIza`, `sk-or-v1`, `AKIA`…) → seul un placeholder `gsk_xxx…` dans `.env.example.groq`. Les `.env*` sont ignorés avec exception pour les exemples.
6. **Zéro TODO/FIXME/HACK** dans le code Python.
7. **Tests** : après le fix, 624 tests backend passent (9 s) + 592 tests frontend passent (3 s).
8. **Architecture** : séparation routes/services/schemas/models propre, 30 migrations Alembic ordonnées et nommées, `main.py` de 60 lignes, config Pydantic centralisée.
9. **Graceful degradation systématique** : Redis absent, DB absente, embedder ONNX absent → chaque brique dégrade avec un log explicite (constaté au boot).
10. **Hygiène Docker** : `.dockerignore` bien construit (exclut le frontend et les gros data), healthcheck `/health` + retries sur Railway.

---

# 7. Correction appliquée dans cette session

**Fichier créé : `khawarizmi-backend/app_state.py`** — dataclass `AppState` + instance `state`, reconstitué à partir de la définition historique de `routes/lifespan.py` (commit `bdad539~1`) + champ `embedder_fallback` (utilisé par le lifespan actuel).

**Preuves (live-state-truth) :**
- `python -c "from main import app"` → OK, **176 routes** exposées (avant : `ModuleNotFoundError`).
- `pytest tests/` → **624 passed, 4 failed** (avant : 0 collecté).
- Boot réel `uvicorn main:app` → `Application startup complete`, `/health` répond, tutor + scheduler initialisés, 251 questions chargées.

**Non touché (scope-fence) :** les 13 routes non enregistrées, les 4 tests en échec, la CI, l'admin analytics, le lint frontend — tout est documenté ci-dessus avec la correction recommandée.

---

# 8. Plan d'action priorisé

| # | Action | Effort | Impact |
|---|---|---|---|
| 1 | ✔ `app_state.py` restauré (fait) | — | backend démarre |
| 2 | Ré-enregistrer dans `ALL_ROUTERS` : `aujourdhui`, `lessons`, `tuteur`, `bac_blanc`, `document_analysis`, `phase2`, `phase4`, `coach` (si le fichier existe), messenger/blog | 1 h | +10 features réparées |
| 3 | `chat.py` : retirer sa route `GET /api/chapitres/{matiere}` (conflit) puis l'enregistrer, ou supprimer le fichier (le frontend utilise `/api/ai/chat`) | 15 min | supprime l'ambiguïté |
| 4 | Ajouter `POST /api/chatbot/ask/stream` (SSE) ou basculer le frontend sur `/ask` JSON | 1-2 h | répare le chatbot |
| 5 | CI : suite pytest complète (avec PostgreSQL + Redis services), lint sans `continue-on-error`, protection de branche sur `main` | 1 h | empêche la récidive du P0 |
| 6 | `admin_analytics` : exiger un rôle admin (claim JWT ou table) | 30 min | ferme la fuite de données élèves |
| 7 | Réparer les 4 tests en dérive (mocks `pulse_service`, attente `llm_recovered`) | 1 h | suite verte |
| 8 | `deps.py` : retirer `verify_sub: False`, valider `sub` → 401 propre | 10 min | robustesse |
| 9 | Self-hoster la police Cairo (`next/font/local`) | 30 min | build hermétique |
| 10 | `git rm -r --cached` de `khawarizmi-backend/data/` + artefacts racine ; dédupliquer `LIVRE-MANHADJIYA.md` | 30 min | dépôt allégé |
| 11 | Supprimer le code mort : `chat.py`, `evaluate.py`, `bac_blanc.py` (si non ré-enregistré), `document_analysis.py` (si v2 suffit), `tuteur.py` ; faire tourner `check_legacy_usage.py` en CI | 2 h | dette réduite |
| 12 | Mettre à jour README (57 fichiers tests, coverage, compose) | 15 min | docs fidèles |

---

# 9. Limites de l'audit

- Le build Next.js n'a pas pu être validé de bout en bout : le sandbox bloque `fonts.googleapis.com` (échec reproduit et documenté, P1-3).
- Les tests backend ont été exécutés en **mode SQLite preview** (pas de PostgreSQL/Redis dans le sandbox) ; la suite CI officielle utilise PostgreSQL 16.
- Les endpoints « absents » l'ont été vérifiés sur l'app **réellement bootée** (liste OpenAPI), pas seulement par grep.
- Le comportement en production Railway (variables réelles, migrations appliquées) n'a pas pu être observé directement.
