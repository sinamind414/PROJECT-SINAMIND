# Rapport d'architecture — SPECKIT (lecture seule)

**Date :** 2026-08-26
**Nature du document :** rapport **lecture seule**. Aucun code modifié, aucun commit, aucun merge, aucune recommandation ni jugement de qualité. Tous les chemins sont cités tels que constatés dans le checkout au moment de la lecture.

---

## Sommaire (accès direct)

- [1. Identité du dépôt](#1-identité-du-dépôt)
- [2. Arborescence globale](#2-arborescence-globale)
- [3. Frontend](#3-frontend)
- [4. Backend](#4-backend)
- [5. Contrats & données](#5-contrats--données)
- [6. Tests](#6-tests)
- [7. CI / CD](#7-ci--cd)
- [8. Configuration & secrets](#8-configuration--secrets)
- [9. Dette technique observable](#9-dette-technique-observable)
- [10. Flux de données](#10-flux-de-données)
- [11. Annexes](#11-annexes)

---

## 1. Identité du dépôt

| Élément | Valeur constatée |
|---|---|
| Chemin racine | `/home/user/PROJECT-SINAMIND` |
| Branche courante | `arena/01a035b2-project-sinamind` |
| Commit de la branche | `8ef5a8c972c4b5b1cb64fa31cae76934c8371e5c` (même SHA que `master`) |
| Commit `master` (origin) | `8ef5a8c972c4b5b1cb64fa31cae76934c8371e5c` |
| Message HEAD | `fix(ci): correct YAML indentation - run must be sibling of env, not child` |
| Branches locales | `master`, `arena/01a035b2-project-sinamind` |
| Branches distantes | `origin/master`, `origin/HEAD -> origin/master` |
| Nombre de dossiers | 56 |
| Nombre de fichiers (hors `.git`, `node_modules`, `.venv`, `.next`, `dist`, `build`) | 1170 |
| Un projet | Koums (rép), `khawarizmi-backend`, `khawarizmi-frontend`, `svt_course`, `scripts` |

> **Note d'état :** au moment de la lecture, `git status --short` liste une série de fichiers **untracked** en racine (`A...md`, `S1-sujet-type-bac-...md`, `audit-....md`, `INT-contrat-integration-S1-S4.md`, etc.). Aucune différence de la branche `arena/01a035b2-project-sinamind` par rapport à `master` (le SHA est identique).

---

## 2. Arborescence globale

Arborescence de premier niveau (hors fichiers cachés) :

```
PROJECT-SINAMIND/
├── khawarizmi-backend/        (backend FastAPI)
│   ├── config.py
│   ├── main.py
│   ├── database.py
│   ├── auth.py
│   ├── routes/                (61 fichiers .py)
│   ├── services/              (87 fichiers .py)
│   ├── grading/               (sous-package correcteur)
│   ├── methodology/           (sous-package méthodologie)
│   ├── schemas/
│   ├── models/minilm_onnx_int8/
│   ├── migrations/            (env.py, script.py.mako, versions/35 fichiers)
│   ├── prompts/
│   ├── templates/
│   ├── tests/                 (95 fichiers .py + tests/golden/)
│   ├── scripts/
│   ├── data/                  (ignoré par git)
│   └── requirements.txt
├── khawarizmi-frontend/       (frontend Next.js)
│   ├── package.json
│   ├── next.config.ts
│   ├── tsconfig.json
│   ├── vitest.config.ts
│   ├── netlify.toml
│   ├── src/                   (app/, components/, features/, hooks/, lib/, types/)
│   ├── public/                (pdfs/, lecons-sciences-experimentales/, figures/)
│   └── package-lock.json
├── svt_course/
├── scripts/
├── .github/workflows/ci.yml
├── README.md
├── .gitignore
└── vercel.json
```

Répartition par extension (hors `.git`, `node_modules`, `.venv`, `.next`, `dist`, `build`) :

| Extension | Nombre |
|---|---|
| `.py` | 461 |
| `.tsx` | 236 |
| `.ts` | 70 |
| `.md` | 95 |
| `.json` | 77 |
| `.html` | 48 |
| `.png` | 72 |
| `.svg` | 6 |
| `.pdf` | 12 |
| `.sql` | 14 |
| `.yml` / `.yaml` | 2 |

---

## 3. Frontend

**Dossier :** `khawarizmi-frontend`

### 3.1 Outillage

| Fichier | Contenu constaté |
|---|---|
| `khawarizmi-frontend/package.json` | `next` 16.2.10, `react` 19.2.4, `tailwindcss` 4, `vitest` 4.1.9 ; script `test: watch` ; ne possède pas de script `test`/`build` explicite pour le runner Deno |
| `khawarizmi-frontend/next.config.ts` | `turbopack` comme racine ; headers de sécurité (`X-Frame-Options: DENY`, CSP ajoutée uniquement en production) ; `rewrites` `/api/:path*` → `NEXT_PUBLIC_API_URL` ou fallback `localhost:8000` |
| `khawarizmi-frontend/tsconfig.json` | alias `@/*` → `./src/*` |
| `khawarizmi-frontend/vitest.config.ts` | environnement `node`, `include` `src/**/*.test.ts` |
| `khawarizmi-frontend/netlify.toml` | (présent, config Netlify) |
| racine `vercel.json` | `{}` (objet vide) |
| `package-lock.json` | présent |
| `deno.lock` | présent (dossier `khawarizmi-frontend`) |

### 3.2 `src/` (structure en 2 niveaux)

```
src/
├── app/                 (routes App Router)
│   ├── annales/  [slug]/ (page, exam/, guided/, read/, correction/)
│   ├── admin/analytics/
│   ├── dashboard/  diagnostic/  methodology/  mindmap/  chatbot/
│   ├── bac-blanc/  exercices/  exercises/  cours/  videos/  pulse/
│   ├── ... (plusieurs modules UI)
│   ├── layout.tsx  page.tsx  globals.css  loading.tsx  error.tsx
│   ├── global-error.tsx  not-found.tsx  favicon.ico
├── components/          (composants réutilisables)
│   ├── annales/  (ExamProgress.tsx, SubjectChoiceCard.tsx, SubmissionDialog.tsx)
│   ├── bac_blanc/ (BacBlancImmersif.tsx)
│   ├── dashboard/  diagnostic/  lessons/  methodology/  mindmap/
│   ├── layout/  ui/  auth/  features/  gamification/  programme/
│   └── providers.tsx
├── features/dashboard/
├── hooks/               (useDriveDashboard.ts, useGamification.ts, useLocalStreak.ts, useSocial.ts, useSound.ts)
├── lib/                 (annales-bac.ts, api-client.ts, types.ts, translations.ts, ...)
└── types/               (speech-recognition.d.ts)
```

### 3.3 Gestion d'état

`khawarizmi-frontend/src/components/providers.tsx` enveloppe l'application avec deux contextes :

- `AuthProvider` (`src/lib/auth-context.tsx`)
- `AchievementProvider` (`src/lib/achievement-context.tsx`)

Autres hooks/contextes d'état : `src/lib/auth-context.tsx`, `src/lib/achievement-context.tsx`, `src/hooks/*` (`useDriveDashboard`, `useGamification`, `useLocalStreak`, `useSocial`, `useSound`).

### 3.4 Client API

`src/lib/api-client.ts` : `const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://khawarizmi-backend.railway.app"`. Exporte des types `MindMapNode`, `MindMap`, `Flashcard`, `ChatMessage`.

### 3.5 Composants annales

Module `src/app/annales/` : `page.tsx` (liste), `[slug]/page.tsx`, `[slug]/exam/page.tsx`, `[slug]/exam/correction/page.tsx`, `[slug]/guided/page.tsx`, `[slug]/read/page.tsx`, `loading.tsx`. Composants : `src/components/annales/` (`ExamProgress.tsx`, `SubjectChoiceCard.tsx`, `SubmissionDialog.tsx`).

`src/app/annales/page.tsx` importe `getAllSujets` et `SujetBac` depuis `@/lib/annales-bac`, et le type `Annale` depuis `@/lib/types` ; il définit une fonction `annaleToSujet(a: Annale): SujetBac` de conversion.

### 3.6 Assets statiques

**PDF (12 fichiers)** dans `khawarizmi-frontend/public/pdfs/` :

```
public/pdfs/bac-svt-math/bac-svt-math-2023.pdf ... bac-svt-math-2026.pdf
public/pdfs/bac-svt/bac-svt-correction-2023.pdf ... bac-svt-correction-2026.pdf
public/pdfs/bac-svt/bac-svt-sujet-2023.pdf ... bac-svt-sujet-2026.pdf
```

> **Constat :** les 12 fichiers font chacun **131–132 octets** et commencent par `version https://git-lfs.github.com/spec/v1` — ce sont des **pointeurs Git LFS**, pas des PDF binaires.

### 3.7 Leçons SVT

`khawarizmi-frontend/public/lecons-sciences-experimentales/` contient **24 fichiers HTML** : `index.html`, `lecon_transcription.html`, `phase1_chapitres_1_2.html` … `phase22_chapitres_43_44.html`.

---

## 4. Backend

**Dossier :** `khawarizmi-backend`

### 4.1 Point d'entrée

`khawarizmi-backend/main.py` :

- Crée `app = FastAPI(**openapi_metadata, lifespan=lifespan, docs_url=None if _is_prod else "/docs", redoc_url=None if _is_prod else "/redoc", openapi_url=None if _is_prod else "/openapi.json")` — la doc est masquée en **production**.
- Middlewares : `SlowAPIMiddleware` (rate limiting) puis `CORSMiddleware` (`allow_origins` depuis `get_allowed_origins()` ; méthodes `GET/POST/PUT/DELETE/OPTIONS/PATCH` ; headers `Accept, Accept-Language, Authorization, Content-Type, X-Requested-With`).
- `app.include_router(admin_router)` (depuis `routes.admin_ingest`) puis boucle `for router in ALL_ROUTERS: app.include_router(router)`.
- Importe `setup_monitoring()` (`monitoring.py`), `limiter` (`rate_limit.py`), les handlers d'erreurs (`routes.errors`).

### 4.2 Registre de routes

`khawarizmi-backend/routes/__init__.py` :

- `ALL_ROUTERS` contient **48 routers** (comptés via `\w+\.router` dans le bloc).
- Le fichier importe les modules `(action_verbs, admin_analytics, ai_chat, annales, aujourdhui, auth, avatar, bac_blanc, badges, chatbot, chatbot_engagement, cities, cours, dashboard, diagnostic, document_analysis, document_analysis_v2, dual_coding, duels, exercices, flashcards, gamification, gems, health, kunz_tunnel, leaderboard, lessons, lexique, manhadjiya, methodology, methodology_flashcards, mindmap, mystery_box, observability, onboarding, orientation, payment, phase1, phase3, phase5, phase6, programme, progress, pulse, session, social, streaks, videos)`.
- Contient un **gel d'endpoints orphelins** : `FROZEN_ENDPOINTS: set[str]` (commentaire mentionnant un audit daté 2026-08-17). Liste :

  ```
  /api/cities/{city_id}/unlock
  /api/cities/leaderboard
  /api/gems/transactions
  /api/gems/leaderboard
  /api/leaderboard/refresh
  /api/onboarding/welcome-gems
  /api/phase6/events
  /api/phase6/session/start
  /api/phase6/funnels
  /api/streaks/me/activity
  /api/streaks/me/freeze
  /api/flashcards/methodology/
  /api/document-analysis/review
  /api/session/random
  ```

  Le fichier applique ensuite `_router.routes = [r for r in _router.routes if r.path not in FROZEN_ENDPOINTS]`.

### 4.3 Fichiers de routes présents

`khawarizmi-backend/routes/` contient **61 fichiers `.py`** dont des modules **non importés** dans `__init__.py` :

- **Présents sur disque mais non référencés dans `ALL_ROUTERS` / import block :** `admin_ingest`, `ai_evaluate`, `chapitres`, `errors`, `evaluate`, `lifespan`, `memory`, `mindmap_methodology`, `openapi_config`, `static_content`, `tutor`, `bac_blanc_intelligent`.
- `main.py` importe explicitement : `routes.admin_ingest` (→ `admin_router`), `routes.errors`, `routes.lifespan`, `routes.openapi_config`.

### 4.4 Comptage d'endpoints (versus README)

- **README.md** (`README.md:57`) : « `routes/` — 189 endpoints REST (voir `routes/__init__.py` pour le registre) ».
- **Mesure :** `grep -rEc "@router.*(get|post|put|delete|patch|api_route)" routes/*.py` → **total 205** décorateurs de route dans `routes/*.py`.
- Écart observé entre 205 décorateurs et les 189 endpoints annoncés — cohérent avec le fait que plusieurs modules (`evaluate.py`, `ai_evaluate.py`, `bac_blanc_intelligent.py`, `chapitres.py`, `memory.py`, `mindmap_methodology.py`, `static_content.py`, `tutor.py`) existent sur disque sans être montés dans `ALL_ROUTERS`.

### 4.5 Configuration

`khawarizmi-backend/config.py` (157 lignes) :

- `class Settings(BaseSettings)`.
- `VERSION: str = "2.0.0"` (ligne 14).
- `ENVIRONMENT: str = "development"` (ligne 15).
- `SECRET_KEY: str = ""` (ligne 18) avec un `@field_validator("SECRET_KEY")` (ligne 98) : exige ≥ 16 caractères ; en environnement `test`/`ci` il y a une rétention de fallback ; sinon `ValueError` si non défini.
- `DATABASE_URL` défaut : `postgresql+asyncpg://postgres:test@localhost/khawarizmi_test` (ligne 22).
- `ONNX_MODEL_PATH: str = ""` (ligne 90).
- Bloques de monitoring (lignes 134–135) : `environment=settings.ENVIRONMENT`, `release=f"khawarizmi-pro@{settings.VERSION}"`.

### 4.6 Services (87 fichiers `services/*.py`)

Le sous-dossier `services/` contient 87 fichiers Python. Points notables relevés :

- `services/fallback_v2.py` (24355 octets) : moteur de correction local.
- `services/fallback_programme_data.py` (2471 octets) : présent distinct de `fallback_v2` (pas un doublon).
- `services/llm_guard.py` : garde-fou contre les appels LLM externes. `is_llm_enabled()` retourne `False` par défaut ; `ENABLE_EXTERNAL_LLM=1` (ET le `ENVIRONMENT`/`DISABLE_LLM`) requis ; expose `GuardedOpenAIClient` (avec `_GuardedCompletions`, `_GuardedChat`, `_GuardedEmbeddings`, `_GuardedImages`, `_GuardedAudio`), `guard_proceed()`, `guarded_openai_client()`, `scrub_environment()`.
- `services/embedder.py` : service d'embeddings optimisé `onnxruntime` + `tokenizers`. **Constat LFS :** le chemin par défaut est `models/minilm_onnx_int8`, `onnx_file = .../model_quantized.onnx` ; le code détecte un pointeur LFS (`_is_lfs_pointer`) et bascule sur un **fallback TF-IDF déterministe** (`Activation du mode Fallback déterministe TF-IDF`).

### 4.7 Sous-package `grading/`

`khawarizmi-backend/grading/` contient `__init__.py, cache.py, cache_key.py, context.py, contracts.py, l2.py, mapping.py, metrics.py, observability.py, parser.py`.

### 4.8 Sous-package `methodology/`

`khawarizmi-backend/methodology/` contient `__init__.py, action_plan.py, bac_blanc_feedback.py, bac_blanc_guidance.py, chat_tutor.py, chat_tutor_prompts.py, diagnostic.py, document_usage_analyzer.py, evaluator.py, feedback_engine.py`.

### 4.9 Bases de données & accès

- `khawarizmi-backend/database.py` : sessions SQLAlchemy asynchrones. Docstring : la session est fournie aux dépendances FastAPI, la transaction est commitée uniquement via `db_transaction()` (écritures), lecture sans commit. En mode preview (SQLite) patch de compatibilité (JSONB/ARRAY → types SQLite), création automatique de toutes les tables sans FK.
- `khawarizmi-backend/auth.py` : `hash_password`/`verify_password` (bcrypt via `passlib`), `create_access_token` (JWT `jose`, `JWT_ALGORITHM`, `JWT_EXPIRE_HOURS`).
- `khawarizmi-backend/migrations/` : `env.py`, `script.py.mako`, `sql/`, `versions/` (35 fichiers de migrations).

### 4.10 Modèles

`khawarizmi-backend/models/minilm_onnx_int8/` : `config.json`, `model_quantized.onnx`, `ort_config.json`, `special_tokens_map.json`, `tokenizer.json`, `tokenizer_config.json`.

> **Constat :** `model_quantized.onnx` fait **134 octets** et commence par `version https://git-lfs.github.com/spec/v1` → **pointeur Git LFS**, pas un binaire ONNX réel. Le `.gitignore` racine a une ligne `khawarizmi-backend/models/*` avec `!khawarizmi-backend/models/minilm_onnx_int8/`.

---

## 5. Contrats & données

### 5.1 Contrat `SujetBac` (frontend)

`khawarizmi-frontend/src/lib/annales-bac.ts` (934 lignes, ~48292 octets) :

```ts
export interface SujetBac {
  slug: string
  annee: number
  session: "normale" | "rattrapage"
  matiere: string
  filiere: string
  titre: string
  titreAr: string
  difficulte: "facile" | "moyen" | "difficile"
  duree: number
  totalPages: number
  chapitres: string[]
  url_pdf: string
  url_corrige?: string
  exercices: Exercice[]
  subjects: BacSubSubject[]
}
```

Types de support :

```ts
export type ExerciceType = "qcm" | "analyse_document" | "raisonnement" | "schema" | "argumentation"
export interface DocumentRef { titre: string; nature: string; description: string }
export interface Question { id: string; texte: string; verb: string; points: number; indices?: string[] }
export interface Exercice { id: string; titre: string; type: ExerciceType; duree_minutes: number; points: number; documents: DocumentRef[]; questions: Question[] }
export interface BacSubSubject { ... }
```

Fonctions exportées : `getAllSujets(): SujetBac[]` (ligne 914), `getSujetBySlug(slug: string): SujetBac | undefined` (ligne 918), `getAnneeRange(): number[]` (ligne 931).

### 5.2 Contrat `Annale` (back ↔ front)

`khawarizmi-frontend/src/lib/types.ts` :

```ts
export interface Annale {
  id: number
  titre: string
  titre_ar?: string
  slug: string
  matiere: string
  niveau: string
  filiere: string
  annee: number
  type: "examen" | "concours"
  fichier_sujet: string | null
  fichier_correction: string | null
  tags: string[]
  difficulte: number
  created_at: string
}
export interface AnnalesResponse { ... }
```

### 5.3 Route annales (backend)

`khawarizmi-backend/routes/annales.py` — `router = APIRouter(prefix="/api/annales", tags=["Annales"])`. `GET /api/annales/` avec filtres ciblés (`page`, `taille`, `matiere`, `niveau`, `filiere`, `annee`, `type`, `recherche`) et tri `ORDER BY annee DESC, created_at DESC`.

### 5.4 Route exercices (backend)

`khawarizmi-backend/routes/exercices.py` — `router = APIRouter(prefix="/api/exercices", tags=["Exercices"])`. `GET /api/exercices/{chapitre}` interroge la table `rag_chunks` avec `source = "svt_bac_complet.md"` et filtre sur `content LIKE '%تمارين%'` / `'%التمرين%'` / `'%إجابة%'` (keywords via `chapter_mapping.json`).

### 5.5 Schémas Pydantic

`khawarizmi-backend/schemas/` contient : `__init__.py, action_verb.py, ai_request.py, ai_response.py, bac_blanc.py, chat.py, dashboard.py, document_analysis.py, evaluate.py, evaluation_v2.py`.

### 5.6 Données

- `khawarizmi-backend/data/` : présent (ignoré par git, cf. `.gitignore` `khawarizmi-backend/data/`).
- `source = "svt_bac_complet.md"` : cité dans `routes/exercices.py` comme **nom de source** en base, non un fichier du dépôt (introuvable en tant que fichier dans l'arborescence).

### 5.7 Contrat d'intégration Bac (document projet, hors code)

`INT-contrat-integration-S1-S4.md` (présent en racine, untracked) définit : pastilles `AuthenticiteSujet` (`officiel` / `reconstitue` / `entrainement`), `StatutValidation` (= `brouillon` | `relu_humain` | `publie`), `ScoringMode` (= `interdit` | `corrige_a_consulter` | `note_auto`), un contrat `SujetBacReconstitue` et un type `DocumentFigure` (`bytes_min: 500`, `sha256`), ainsi qu'une règle CI anti-pointeur-LFS sur `public/pdfs/`, `public/figures/bac/` et l'ONNX.

> Ce fichier est un document de **conception** ; il ne décrit pas un type `SujetBacReconstitue` présent dans le code réel (le seul `SujetBac` réel est dans `annales-bac.ts`).

---

## 6. Tests

### 6.1 Backend

- `khawarizmi-backend/pytest.ini` : `testpaths = tests`, `python_files = test_*.py`, `asyncio_mode = auto`, `norecursedirs = manual`, `markers = nightly` (test nécessitant un appel LLM réel, hors CI).
- `khawarizmi-backend/tests/` : **95 fichiers `*.py`**.

### 6.2 Harness golden (correcteur)

`khawarizmi-backend/tests/golden/` :

| Fichier | Rôle |
|---|---|
| `audit_correcteur_golden.py` | audit 56 copies (8 questions × 7 catégories) |
| `build_golden_annotated.py` | construction |
| `golden_annotated.json` | 166 Ko |
| `metrics.py` | métriques |
| `scoring.py` | barème |
| `test_golden_local.py` | tests locaux |
| `test_json_mode_quality.py` | qualité mode JSON |
| `test_regression.py` | régression |

**Résultat du harnais `audit_correcteur_golden.py`** (exécuté durant l'exploration, avec `ENVIRONMENT=ci`, `SECRET_KEY` de test, nettoyage de `.venv` puis réinstallation) :

- Échantillon : 56 copies (8 questions × 7 catégories).
- **Savoir (semantic) / L2 (fallback v2)** moyennes par catégorie :

  | catégorie | savoir % | l2 % |
  |---|---|---|
  | exacte | 100.0 | **83.4** |
  | reformulee | 68.8 | 33.8 |
  | hors_sujet | 3.1 | 9.4 |
  | contradictoire | 28.1 | 27.9 |
  | erreur_bac | 15.6 | 23.9 |

- **Faux positifs** (copie correcte notée < 60 %) : savoir 7, l2 18.
- **Faux négatifs** (copie fautive notée ≥ 60 %) : savoir 2 (`photo_1/erreur_bac` 75, `struct_1/contradictoire` 100), l2 **0**.
- **Conformité au barème** (nb copies dans la bande attendue) :

  | catégorie | bande attendue | savoir | l2 |
  |---|---|---|---|
  | exacte | 80.0–100 % | 8/8 | 5/8 |
  | reformulee | 70.0–100 % | 6/8 | 0/8 |
  | hors_sujet | 0.0–40.0 % | 8/8 | 8/8 |
  | contradictoire | 0.0–50.0 % | 7/8 | 8/8 |
  | erreur_bac | 0.0–50.0 % | 7/8 | 8/8 |

### 6.3 Frontend

- `vitest.config.ts` : `environment: node`, `include: ['src/**/*.test.ts']`.
- Fichiers de test `*.test.ts` présents, ex. `src/features/dashboard/orchestrator/fallback.test.ts`, `..../mappers.test.ts`, `src/lib/method/methodology-v2.test.ts`, `src/lib/manhadjia-lib.test.ts`, `src/lib/manhadjia-remediation.test.ts`.

---

## 7. CI / CD

**Fichier :** `.github/workflows/ci.yml` (racine du dépôt).

- **Déclencheurs :**
  - `push` vers `main` et `fabuleux/*`.
  - `pull_request` vers `main` **uniquement**.
- **Jobs :**
  - `backend-tests` : service Postgres 16, Python 3.12, smoke test + tests méthodologie.
  - `frontend-tests` : Node 20, `npm ci`, `lint` (continue-on-error), `vitest`, `next build`.
  - `deploy-railway` (sur `main` uniquement).

> **Observation :** le trigger n'écoute que `main`/`fabuleux/*`. Une PR de `master` ne déclenche pas les checks. (L'exploration ne révèle pas de `gh` PR #16 active au moment de la lecture — seule l'infra CI est documentée ici.)

**Autres fichiers de déploiement :**
- `khawarizmi-frontend/netlify.toml` (présent).
- `vercel.json` (racine, `{}`).
- `khawarizmi-frontend/next.config.ts` : `rewrites /api/:path*` vers `NEXT_PUBLIC_API_URL` ou fallback `localhost:8000`.

---

## 8. Configuration & secrets

### 8.1 Fichiers d'environnement

- `khawarizmi-backend/.env` : **absent** (non trouvé dans le checkout).
- `khawarizmi-backend/.env.example` : présent.
- `khawarizmi-backend/.env.example.groq` : présent.
- `.gitignore` racine : `**/.env`, `**/.env.*`, `!**/.env.example` (les `.env` réels sont exclus, les `.env.example` exceptionnés).

### 8.2 Variables de configuration (config.py)

- `VERSION` = `"2.0.0"`, `ENVIRONMENT` = `"development"` (défaut), `SECRET_KEY`, `DATABASE_URL`, `ONNX_MODEL_PATH`.
- Validateur `SECRET_KEY` : minimum 16 caractères, fallback auto en environnement `test`/`ci`, erreur sinon.

### 8.3 Secrets applicatifs

- `khawarizmi-backend/auth.py` : `SECRET_KEY` (JWT `jose`), `JWT_ALGORITHM`, `JWT_EXPIRE_HOURS` (via `get_settings()`).
- `README.md:79` : « les endpoints analytics élèves exigent `X-Admin-Token` = `ADMIN_SECRET` ».
- `services/llm_guard.py` : les clés API sont conservées **uniquement** si `ENABLE_EXTERNAL_LLM=1` (`scrub_environment`) ; sinon protection par défaut.

### 8.4 Python / Node

- Python du `.venv` : **3.11.2** (constaté via `khawarizmi-backend/.venv/bin/python --version`).
- Node : **v22.22.3** (constaté via `node --version`).
- `pyproject.toml` : **introuvable** dans tout le checkout (aucun résultat).

---

## 9. Dette technique observable

Constatations factuelles (sans préconisation ni jugement) :

- **Pointeurs Git LFS non téléchargés :**
  - `khawarizmi-frontend/public/pdfs/` : **12 fichiers** `.pdf` de 131–132 octets, contenu = `version https://git-lfs.github.com/spec/v1`.
  - `khawarizmi-backend/models/minilm_onnx_int8/model_quantized.onnx` : 134 octets, pointeur LFS (impacte `services/embedder.py`, qui bascule en fallback TF-IDF).
- **Écart de comptage d'endpoints :** README annonce 189, mesure brute 205 décorateurs dans `routes/*.py` ; plusieurs modules de routes existent hors de `ALL_ROUTERS`.
- **Modules de routes non montés :** `evaluate.py`, `ai_evaluate.py`, `bac_blanc_intelligent.py`, `chapitres.py`, `memory.py`, `mindmap_methodology.py`, `static_content.py`, `tutor.py` présents dans `routes/` mais non référencés dans le registre.
- **Gel d'endpoints :** `FROZEN_ENDPOINTS` (14 entrées) commenté comme « audit endpoints morts » (2026-08-17) ; commentaire mentionnant un endpoint dégelé (`/api/social/upload`).
- **Dépendances de tests :** le runner `nightly` (appel LLM réel) est marqué hors CI.
- **`.venv`** non versionné (exclu des snapshots de l'environnement de travail), `node_modules/`, `.next/`, `dist/` exclus.
- **`data/` backend** ignoré par git (données non versionnées).
- **Marqueurs de dette (`TODO`/`FIXME`/`HACK`/`XXX`) en MAJUSCULES :** **aucun** trouvé dans le code source projet (recherche casse exacte sur `khawarizmi-backend/services, grading, routes, methodology` et `khawarizmi-frontend/src`). Les occurrences rencontrées étaient soit le mot anglais « todo » (statut d'UI), soit des dépendances dans `.venv`.
- **`fallback_v2.py`** (24355 octets) est le moteur de correction local ; un fichier distinct `services/fallback_programme_data.py` existe (2471 octets). Le harnais golden n'appelle pas chercher un doublon — un seul `fallback_v2.py` (résultat de `find`).

---

## 10. Flux de données

### 10.1 Flux élève → annales (front → back)

1. `src/app/annales/page.tsx` appelle `getAllSujets()` (`src/lib/annales-bac.ts`) pour la liste statique, et `apiClient` (`src/lib/api-client.ts`) pour `Annale[]` depuis `https://khawarizmi-backend.railway.app` (ou `NEXT_PUBLIC_API_URL`).
2. `annaleToSujet(a: Annale)` convertit un `Annale` back en `SujetBac` front (mapping `difficulte`, `slug`, `titre`, …).
3. Le composant de détail (`src/app/annales/[slug]/...`) exploite `url_pdf`/`url_corrige` vers `public/pdfs/` (pointeurs LFS actuellement).

### 10.2 Flux API (front → back)

- `next.config.ts` réécrit `/api/:path*` vers `NEXT_PUBLIC_API_URL` (fallback `localhost:8000`).
- `src/lib/api-client.ts` définit `API_BASE_URL` vers l'URL de production Railway.
- Backend : `main.py` monte `admin_router` + `ALL_ROUTERS`, rate-limited par `SlowAPIMiddleware`, CORS restreint.

### 10.3 Flux de correction (back, 3 niveaux)

`khawarizmi-backend/routes/evaluate.py` (module présent, non monté dans `ALL_ROUTERS`) — `POST /api/evaluate` avec repli à 3 niveaux : `COMMON_MISTAKES` → `GPT4O` → `FALLBACK_L2` → `FALLBACK_L3`.

`khawarizmi-backend/services/fallback_v2.py` :

- `evaluate_l2` (ligne 440) : pondération `w_semantic=0.40`, `w_tfidf=0.25`, `w_structural=0.35`.
- Seuils : `≥ 0.85` → `correct` ; `≥ 0.35` → `partiel` ; sinon `insuffisant` ; `needs_l1_review` si `0.35 <= score < 0.70`.
- `concept_present_without_negation(text_normalized, pattern_normalized) -> bool` (ligne 67) avec marqueurs de négation FR/AR.
- `_normalize_ar_fr`, `NEGATION_MARKERS_FR/AR`, `compute_structural_score` (ligne 266), `L2Result`.

`khawarizmi-backend/routes/document_analysis_v2.py` — `POST /api/document-analysis/evaluate-v2` (analogue).

### 10.4 Flux d'embeddings

- `services/embedder.py` charge `model_quantized.onnx` (pointeur LFS). En l'absence de binaire, le service bascule en **fallback TF-IDF** (`Activation du mode Fallback déterministe TF-IDF`).

### 10.5 Flux données § `svt_bac_complet.md`

- `routes/exercices.py` requête `rag_chunks` filtré sur `source = 'svt_bac_complet.md'` et `content LIKE '%تمارين%' / '%التمرين%' / '%إجابة%'`.

---

## 11. Annexes

- **Contrat d'intégration :** `INT-contrat-integration-S1-S4.md` (racine, untracked) — pastilles `AuthenticiteSujet`/`ScoringMode`, `SujetBacReconstitue`, `DocumentFigure`, règles CI anti-LFS.
- **Sujets type Bac rédigés (racine, untracked) :** `S1-sujet-type-bac-D2-respiration.md`, `S2-sujet-type-bac-D3-tectonique.md`, `S3-sujet-type-bac-D2-photosynthese.md`, `S4-sujet-type-bac-D3-dorsale.md`, `ANALYSE-bac-svt-2025-officiel.md`.
- **Audits (racine) :** `audit-correcteur-svt-sinamind-v1.1.md`, `audit-correcteur-svt-sinamind.md`, `audit-pedagogique-svt-sinamind-v2-corrige.md`, `NOTE-ENVOI-audit-svt-sinamind.md`.
- **Modèle d'embeddings :** `khawarizmi-backend/models/minilm_onnx_int8/` (binaire ONNX = pointeur LFS, 134 octets).
- **PDF LFS :** `khawarizmi-frontend/public/pdfs/` (12 pointeurs LFS).
- **Leçons SVT :** `khawarizmi-frontend/public/lecons-sciences-experimentales/` (24 fichiers HTML).
- **Élément absent / non trouvé :**
  - `khawarizmi-backend/.env` — **absent**.
  - `pyproject.toml` — **introuvable** (sur l'ensemble du checkout).
  - Un type `SujetBacReconstitue` dans le code — **absent** (seul `SujetBac` réel dans `annales-bac.ts`).
  - La référence `svt_bac_complet.md` comme **fichier** — introuvable (apparaît seulement comme valeur `source` en base).

---

*Rapport généré en lecture seule. Les commandes d'exploration (`tree`, `grep`, `cat`, `find`, `git`) n'ont modifié aucun fichier du dépôt ; la seule écriture sur disque est ce rapport lui-même.*
