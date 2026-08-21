# Audit backend + branchement runtime « point d'équilibre »

> Date : 2026-08-20 · Branche : `arena/01a01f52-project-sinamind`
> Mandat utilisateur : « Audit le backend et applique ta recommandation — le point d'équilibre »

## 1. Verdict de l'audit

| Élément | Statut |
|---|---|
| Route `routes/manhadjiya.py` (9 endpoints) | ✅ code propre, sync pur, 0 DB / 0 LLM / 0 Redis |
| `get_contextual_remediation_data` | ✅ pur en mémoire (keywords sur `ALL_UNITS`), latence mesurée **0,013 ms** |
| CORS | ✅ contourné : le frontend appelle en **relatif** `/api/...` via rewrites Next → même origine |
| `POST /contextual-remediation` | ✅ 200, **42 ms de bout en bout** (navigateur → Next → FastAPI), erreur `verb_slug requis` gérée |
| Backend complet | ❌ **ne démarrait PAS** : 2 bugs bloquants committés (voir §2) |
| Backend après correction | ✅ démarre (SQLite 81 tables, 0 LLM, Redis/ONNX en dégradation tolérée) |
| Tests backend manhadjiya | ✅ **99 passed** (après correction) |

## 2. Bloqueurs trouvés et corrigés (2 lignes, mécaniques)

1. **`services/chatbot_handlers.py:185`** — marqueur de conflit git orphelin
   `<<<<<<< HEAD` committé **sans** `=======` ni `>>>>>>>`. Résultat :
   `IndentationError` → **le backend entier ne démarre plus** (import chain),
   et la collecte de tous les tests backend échouait aussi.
   Correction : suppression de la ligne orpheline (le code présent est le côté
   HEAD complet et valide — vérifié par `ast.parse` + 99 tests verts).
2. **`routes/__init__.py`** — `pulse.router` référencé dans `ALL_ROUTERS`
   mais **jamais importé** (`NameError: name 'pulse' is not defined`).
   Correction : `pulse,` ajouté à la liste d'imports.

Ces deux bugs étaient committés dans la base de session (`f45018c`) :
**le backend de production était en panne avant cet audit**.

## 3. Ce qui a été appliqué (le point d'équilibre)

- **Un seul endpoint branché** : `POST /api/manhadjiya/contextual-remediation`.
- **Où** : phase ب des 22 ateliers (7 bootcamp + 15 satellites), via
  `RemediationHint` (debounce 1,2 s · timeout 2,5 s · AbortController ·
  garde anti-réponse obsolète · texte ≥ 12 caractères).
- **Repli silencieux** : toute erreur (réseau, timeout, HTTP ≠ 2xx, JSON
  invalide, payload vide) → `null` → **rien ne s'affiche**, la détection
  locale reste la seule source de vérité et s'affiche toujours.
  Prouvé en conditions réelles : backend coupé → proxy HTTP 500 → rien.
- **Jamais branché** (reste statique, injecté au build) : cartes, verb_ref,
  unites, exemples — `wire_satellite_official_data.py` inchangé.
- 22 JSON portent `verb_slug` (7 bootcamp : diff minimal +1 ligne chacun ;
  15 satellites via le script, idempotent) + invariant testé (slugs ∈ VERB_UNIT_MAP).

## 4. Fichiers

| Fichier | Changement |
|---|---|
| `khawarizmi-backend/services/chatbot_handlers.py` | −1 ligne (marker de conflit orphelin) |
| `khawarizmi-backend/routes/__init__.py` | +1 ligne (`pulse,` import manquant) |
| `khawarizmi-frontend/src/lib/manhadjia-remediation.ts` | nouveau — fetch timeout/abort + normalisation (11 tests) |
| `khawarizmi-frontend/src/components/manhadjia/RemediationHint.tsx` | nouveau — panneau « أخطاء شائعة — المرجع الرسمي » |
| 8 composants `Atelier*.tsx` | +1 import +1 ligne `<RemediationHint …/>` en phase ب |
| 22 JSON ateliers | + champ `verb_slug` |
| 23 pages `app/manhadjia/**` | commentaires de doctrine mis à jour (honnêteté : 1 appel API, repli silencieux) |
| `manhadjia-lib.ts` + tests | `verb_slug: string` dans `AtelierData`, +2 invariants |

## 5. Preuves

- Backend : **99/99 tests manhadjiya verts** · démarrage complet OK · 9/9 endpoints 200 via proxy Next.
- Frontend : **799 tests verts** (dont 11 remediation + 2 invariants) · ESLint clean · build OK · 23/23 routes 200.
- Bout en bout : `POST /api/manhadjiya/contextual-remediation` → **42 ms**, 12 erreurs officielles renvoyées pour `deduce`.
- Repli : backend arrêté → HTTP 500 → composant muet (testé).

## 6. Bugs résiduels — corrigés le 2026-08-20 (même session)

### 6.1 Modèle ONNX « corrompu » — cause racine : pointeur Git LFS
- Le fichier `model_quantized.onnx` (134 octets) est un **pointeur Git LFS**
  (oid sha256:fac7bbc8…, taille réelle 118 Mo) jamais téléchargé.
- Corrections livrées :
  - `services/embedder.py` : détection explicite du pointeur → message
    actionnable (« git lfs pull puis redémarrer ») au lieu de l'INVALID_PROTOBUF
    cryptique ; récupération depuis `model_quantized.zip` si présent (sans
    jamais supprimer le fichier tracké par git) ; fallback déterministe propre
    (les consommateurs sémantiques — rag_service, l2, semantic_cache — se
    désactivent déjà correctement quand `is_semantic` est False).
  - `scripts/check_onnx_asset.py` (nouveau) : diagnostic du statut
    (OK / LFS / CORROMPU / MANQUANT / ZIP) + commande de récupération exacte.
- **Action côté utilisateur** (réseau du sandbox bloqué pour les CDN de contenu
  GitHub — vérifié : media/objects/github-cloud.githubusercontent.com
  inaccessibles, seul api.github.com et le protocole git répondent) :
  sur une machine avec accès réseau :
  `git lfs pull --include 'khawarizmi-backend/models/minilm_onnx_int8/*'`
  puis redéployer. Alternative sans git-lfs : le batch API LFS
  (`POST https://github.com/sinamind414/PROJECT-SINAMIND.git/info/lfs/objects/batch`,
  en-têtes `application/vnd.git-lfs+json`, oid `fac7bbc8…`, size `118086323`)
  renvoie une URL de téléchargement signée valable 1 h — testé depuis le
  sandbox : le batch répond, seul le CDN de contenu est bloqué.
  En attendant, le RAG mot-clé reste fonctionnel.

### 6.2 Écart `unite5-energie` vs `unite5-energetique` — corrigé
- `prompts/scientific_knowledge.py` : helper `_canonical_unit_id()` (alias) appliqué
  à `get_unit_specific_errors`, `build_knowledge_block`, `get_practical_examples`.
- Les deux orthographes sont verrouillées par des tests existants → **aucune
  constante modifiée**. Résultat : les erreurs énergétiques (photosynthèse…)
  apparaissent maintenant dans la remédiation (15 erreurs pour « interpret »
  au lieu de 12). 4 tests de non-régression dans `tests/test_unit_id_alias.py`.

### 6.3 Redis absent en preview
- Toléré par design (warning, rate-limit/cache dégradés, zéro blocage) —
  pas un bug code, aucun changement.

## 7. Bugs supplémentaires découverts par la suite backend (jusqu'ici masqués : le backend ne démarrait pas)

| Fichier | Bug | Correction |
|---|---|---|
| `services/chatbot_handlers.py` | `handle_orientation` levait `NameError: greeting` sur **chaque message d'orientation** (moitié perdue du conflit git) | `greeting` reconstruit (salutation si `is_init`) + `prediction_bac` inclus dans la réponse (contrat de test) |
| `services/chatbot_handlers.py` | `make_response()` appelé avec `prochain_objectif` inconnu → `TypeError` | paramètre optionnel ajouté dans `chatbot_response.py` (rétro-compatible) |
| `services/pulse_service.py` | carte déjà complétée → streak renvoyé faux (0 au lieu du streak réel) | requête streak inline dans la branche idempotente + helper `_streak_summary_from_row` partagé |

**Preuves finales backend** : `pytest -q` → **1000 passed, 10 skipped, 5 xfailed, 0 failed**
(997 + 3 du garde portabilité SQL v2). Boot uvicorn propre,
`/api/manhadjiya/*` 200, `/api/pulse/*` montées (401 sans JWT, normal).

## 8. Suite — garde-fou mort + bugs asyncpg/SQLite (2026-08-20)

### 8.1 Garde-fou mort (skip silencieux) → ressuscité en v2
`tests/test_config_critical.py::test_fsrs_scheduler_no_in_tuple` pointe
`services/fsrs_scheduler.py`, fichier **supprimé** par la fusion FSRS
(le code vit dans `fsrs_unified.py`) → le test skippe en silence et la
règle AGENTS.md §1.5 (`IN :tuple` interdit sur asyncpg) n'était plus
enforcée nulle part. Tests gelés par AGENT_RULES → **nouveau fichier**
`tests/test_sql_portability_guard.py` (aucun test existant modifié) qui
encode la règle moderne :
- chaque « IN :param » exige `bindparam(param, expanding=True)` dans le
  même fichier (seule forme portable SQLite/asyncpg) ;
- « col = ANY(:param) » interdit (non portable SQLite) ;
- le hook `database.py` (`:param = ANY(col)` → json_each) doit rester présent.
Vérifié adversariellement : un fichier scratch violant la règle fait
échouer le test avec un message précis ; 3 tests verts en conditions réelles.
Balayage complet des skips « Fichier introuvable » : c'est le SEUL garde mort
(mindmap_service.py, llm.py, rag_service.py existent tous ; les skips
golden_annotated ne se déclenchent jamais — fichier committé).

### 8.2 Bugs réels trouvés par cette vérification — corrigés
| Fichier | Bug | Correction |
|---|---|---|
| `routes/social.py` | `WHERE v.verb_slug IN :verbs` + `tuple()` **sans** expanding → crash asyncpg en production (PostgreSQL) | `bindparam("verbs", expanding=True)` + `list()` — portable SQLite/asyncpg |
| `services/scheduler.py` | `micro_concept = ANY(:cids)` → **« no such function: ANY » sur SQLite** (preview/CI) | `IN :cids` + `expanding=True` + `list()` |
| `services/fsrs_unified.py` | `tuple(...) if len>1 else (x[0],)` inutile (expanding accepte list) | `list(concept_ids)` |
| `database.py` | `:recherche2 = ANY(tags)` (recherche d'annales) plantait sur SQLite ; `_ANY_RE` était défini mais **jamais utilisé** (dead code) | Hook SQLite : `:param = ANY(colonne)` → `EXISTS (SELECT 1 FROM json_each(col) WHERE json_each.value = param)` — gère les binds `%(nom)s`/`:nom`/`?` ; toute la recherche d'annales fonctionne désormais en preview |

Vérifications : démo SQLite réelle (tag + titre + expanding) ✓ · ruff 0 ✓ ·
1000 tests verts ✓ · PostgreSQL inchangé (le hook ne compile que pour sqlite).

## 9. Gate de remédiation savoir — verdict golden appliqué (2026-08-20)

- Le processus golden (`scripts/golden_human_report.py`) dit : κ savoir ≥ 0.65
  → « RÉACTIVER la remédiation savoir ». Les commentaires de code affirmaient
  κ = 0.449 (périmé). **Mesure réelle sur le golden set actuel : κ = 0.858**
  (MAE 0.279, exact 0.791, severe 0.058) → verdict RÉACTIVER confirmé.
- Implémentation : `config.savoir_remediation_enabled` (défaut **False** =
  comportement historique, verrouillé par le test gelé `test_savoir_branching`).
  À True, la remédiation savoir réutilise la MÊME matrice que le chemin LLM
  (`services/remediation_service` : verbe-spécifique puis générique).
  Activation production : `SAVOIR_REMEDIATION_ENABLED=true` (progressive).
- Preuves : `tests/test_savoir_remediation_gate.py` (4 tests : défaut inerte,
  wiring matrice, fallback silencieux, chaîne réelle scientific_error → page
  spécifique au verbe) ; suite complète 1004 passed / 0 failed.

## 10. Smoke test GET sur SQLite — 99 routes vérifiées (2026-08-21)

- Nouveau `scripts/smoke_api_get.py` : énumère les 99 routes GET `/api/*`
  depuis l'app FastAPI, les appelle sans auth (lifespan réel, SQLite preview)
  et remonte uniquement les 500. Résultat après corrections : **0 erreur**
  (200 publics · 401/403 attendus · 404 dummy-id · 422 validation).
- Bug attrapé et corrigé : `GET /api/social/blog` → 500 « near "(": syntax
  error ». Cause : `AVG(rating)::numeric(3,2)` — le hook SQLite supprimait
  `::numeric` mais laissait la précision `(3,2)` orpheline. Fix général dans
  `database.py` : `_CAST_RE` engloutit aussi la précision optionnelle
  (`::type`, `::type(3,2)`, `::type[]`). Vérifié : blog → 200, rating → 404
  propre, aucune autre route en 500.

## 11. Clôture de session

- Branche : `arena/01a01f52-project-sinamind` (16 commits) — **PR #12 ouverte
  vers master, statut MERGEABLE / CLEAN** (vérifié via API GitHub 2026-08-21).
- Infra vérifiée : `startup.sh` cohérent avec railway.toml (fix migration 017
  héritée + alembic + uvicorn), main.py 60 ≤ 110 lignes (hook pre-commit),
  35 migrations + alembic.ini présents. Pre-commit corrigé : `no-commit-to-branch`
  protégeait `main` (mort) → `master` (branche par défaut + deploy).
- Actions utilisateur restantes : (1) copier `docs/ci/ci.yml.corrigee` vers
  `.github/workflows/ci.yml` (permission workflows) puis merger sur master ;
  (2) `git lfs pull` pour le modèle ONNX ; (3) activer
  `SAVOIR_REMEDIATION_ENABLED` quand le feedback élève le justifie.
## 13. Bug production critique — dialect PostgreSQL empoisonné (2026-08-21)

- **Symptôme** : avec `DATABASE_URL` postgres (configuration Railway), le
  lifespan échouait `DB init error: module 'sqlalchemy.dialects' has no
  attribute 'postgresql'` → **toute l'API partait en 503 dégradé** en
  production. Reproduit en process frais.
- **Cause racine** : `_sqlite_compat()` (database.py) était appliqué
  **inconditionnellement** à l'import et installait un module factice
  `sqlalchemy.dialects.postgresql` via `sys.modules.setdefault` ; quand le
  vrai dialect n'avait pas encore été importé (cas standard), le moteur
  asyncpg ne pouvait plus se construire.
- **Fix** : shim conditionnel (uniquement SQLite ou URL inconnue) ;
  `ensure_dialect_for_url(url)` appelé par le lifespan AVANT la création du
  moteur (l'ordre d'import ne compte plus) ; le module factice est marqué
  (`_KHARIZMI_FAKE`) et retiré si la cible devient PostgreSQL ; ARRAY réel
  restauré.
- **Preuves** : `tests/test_dialect_guard.py` (4 tests : process frais
  postgres, process frais sqlite, env tardif restauré, aller-retour
  postgres→sqlite) ; suite complète **1008 passed / 0 failed** ; smoke
  99 routes GET sans 500 ; boot SQLite inchangé (75+ tables).

## 14. Endpoint frontend orphelin — sondage « verbe le plus difficile » (2026-08-21)

- Audit de couverture endpoints : 131 chemins appelés par le frontend
  (littéraux + template literals normalisés) comparés aux 172 chemins /api
  montés. Un seul orphelin réel : `POST /api/action-verbs/feedback/hardest`
  (HardestVerbPoll, page /action-verbs) — l'endpoint **n'existait pas** au
  backend : 404 avalé par le catch silencieux du composant → aucun vote
  jamais collecté depuis la mise en ligne du sondage.
- Fix : endpoint public ajouté dans routes/action_verbs.py (pas de JWT —
  sondage anonyme), validation verb_slug (requis, ≤ 80), compteur Redis
  `khawarizmi:hardest_verb_feedback:{slug}` quand Redis est disponible
  (production), sinon log structuré seul (preview) — dégradation gracieuse.
- Preuves : tests/test_action_verbs_feedback.py (5 tests : vote valide
  anonyme, 400 sans slug/corps vide/trop long, votes répétables) · suite
  complète **1013 passed / 0 failed** · ruff 0.

## 15. Smoke toutes méthodes HTTP + drift d'auto-DDL vidéos (2026-08-21)

- Nouveau `scripts/smoke_api_all.py` : 176 opérations HTTP sous /api (GET +
  POST/PUT/PATCH/DELETE, corps vide {}, sans auth, denylist des routes à
  effet de bord coûteux). Attendu : 401/403/422/404/405 — seuls les 500
  comptent. Résultat après corrections : **0 échec**.
- Bug attrapé : `POST /api/videos/seed` → 500 `NOT NULL constraint failed:
  videos.url`. Cause : l'auto-DDL SQLite exigeait `url TEXT NOT NULL` alors
  que la migration 006 (production PostgreSQL) n'a PAS cette colonne —
  le seed fonctionnait en prod mais plantait en preview. Fix : auto-DDL
  alignée sur la migration (colonne retirée) ; vérifié seed ×2 → 200,
  10 vidéos importées.
- Tests : tests/test_videos_seed.py (garde DDL + e2e en sous-processus —
  le lifespan ne se ré-entre pas sous pytest-asyncio, queue liée au premier
  loop : artefact de test, pas un bug prod) · tests/test_action_verbs_feedback.py
  simplifié sur le fixture `client` du conftest (l'endpoint n'utilise pas la DB).
- Job nightly CI validé : `pytest -m nightly --collect-only` → 2 tests
  collectés (le marker existe, le job ne mourra pas à la collecte).
- Preuves : **1015 tests backend verts / 0 erreur** · ruff 0 · smoke GET 99
  routes + smoke all 176 opérations sans 500.

## 12. CI — découverte et blocage de permission

- Les 9 derniers runs CI échouaient au **parse du workflow** (un `: ` dans un
  block scalar YAML → « workflow file issue », 0 s).
- Le token de session peut *déclencher* des runs mais pas *écrire*
  `.github/workflows/ci.yml` (push refusé par GitHub : permission `workflows`
  manquante). Version corrigée livrée : `docs/ci/ci.yml.corrigee`
  (triggers master/arena/*, **schedule ajouté** — les jobs nightly étaient
  morts sans lui, deploy sur master, ruff bloquant, Redis service).
- À appliquer par l'utilisateur : copier `docs/ci/ci.yml.corrigee` vers
  `.github/workflows/ci.yml` + merger sur master (le schedule ne se
  déclenche que depuis la branche par défaut).
