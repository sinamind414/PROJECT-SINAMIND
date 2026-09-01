# ARCHITECTURE GLOBALE — Site SVT BAC (Khawarizmi Pro)

Document **mesuré**, pas recopié d'un design rêvé. Chaque chiffre a été relevé le 2026-08-31 sur la branche
`arena/01a05476-project-sinamind` (commit `71fccfb`). Les commandes de relevé sont en §11 : redemande-moi le
doc après modification, je regénère les chiffres au lieu de les supposer.

---

## 1. Vue d'ensemble : deux déploiements, un contrat

```
  navigateur élève (arabe, RTL)
      │
      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│ FRONT — khawarizmi-frontend · Next.js 16.2.10 (App Router, Turbopack)         │
│ 81 pages (19 avec paramètre dynamique) · 148 composants · 42 modules de lib  │
│ 27 fichiers de test · data/ local 332 Ko                                      │
│                                                                               │
│  Contenu LOCAL (aucune latence, survit à la panne d'API) :                    │
│   · 55 leçons (active-lessons)   · 55 clés de chapitres méthodo              │
│   · 68 documents/scénarios       · 30 fiches d'annales                        │
│   · 22 pages « أفعال الأداء »    · 5 simulateurs, mindmaps, fiches J-1        │
│  Contenu DISTANT (via api-client, 122 méthodes / 71 chemins) :                │
│   · correction + quota   · sessions de drill   · chatbot/tuteur               │
│   · progression synchronisée · XP, gems, streaks, duels, classement           │
└───────────────────────────────┬───────────────────────────────────────────────┘
                                │ fetch("/api/…")  ← même origine, TOUJOURS
                                │ proxy runtime : src/app/api/[...path]/route.ts lit
                                │ API_ORIGIN || NEXT_PUBLIC_API_URL || localhost:8000, PAR REQUÊTE 
┌───────────────────────────────▼───────────────────────────────────────────────┐
│ BACK — khawarizmi-backend · FastAPI sur python:3.12-slim (Dockerfile)         │
│ 62 fichiers de routes · 49 routers branchés · 209 endpoints déclarés          │
│ 95 services (21 657 lignes) · 139 fichiers de test · prompts 2 777 lignes    │
│                                                                               │
│  MOTEURS DÉTERMINISTES (sans LLM)                                             │
│   local_grader 844 l. · savoir_corrector 953 l. · fsrs_unified 1 048 l.       │
│   document_analysis_service 551 l. · mindmap_service 1 053 l.                 │
│   scheduler 413 l. · remediation_service 396 l. · llm_guard 359 l.            │
│  LLM optionnels (5 providers configurés) : OpenAI gpt-4o-mini · Z.ai glm-4.7  │
│   · ZenMux · Nara · vision gpt-4o-mini — repli si LOCAL_RUBRIC_GRADER=false   │
│  EMBEDDINGS LOCAUX : models/minilm_onnx_int8/ (ONNX int8, tokenizer 1 M lignes)│
└──────────┬──────────────────────────────────────────────┬─────────────────────┘
           ▼                                              ▼
  PostgreSQL (prod, DATABASE_URL)              data/*.json — 4,5 Mo · 68 fichiers
  SQLite (dev, compat shim dans database.py)   annales OCR · programme 3AS · lexique
  alembic upgrade head au démarrage (Railway)  QCM · golden_set_onec · rubrics/ (32 f.)
```

**Chaîne de déploiement** : front sur Vercel (`khawarizmi-ia-two.vercel.app`), back sur Railway
(`railway.toml` → `startCommand = "sh -c 'alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port
${PORT:-8000}'"`, healthcheck `/health`, grace 180 s, restart `ON_FAILURE` ×3). CI GitHub Actions
`.github/workflows/ci.yml` : `backend-tests` (smoke + tests Methodology) → `frontend-tests`
(`npm run lint` → `npm run test` → `npm run build`) → `deploy-railway`.

**Le maillon cassé est entre les deux** : `NEXT_PUBLIC_API_URL` configuré sur Vercel pointe vers un domaine
Railway qui ne sert pas ce dépôt → tous les appels API de la production échouent (rapport §11, question sans
réponse depuis 14 tours).

---

## 2. Frontend : l'empilement réel

### 2.1 Les quatre couches

| Couche | Volume mesuré | Détail |
|---|---|---|
| `src/app/` | 81 `page.tsx` (19 dynamiques) | une page = une surface de travail, **toutes en `"use client"`** |
| `src/components/` | 148 fichiers, 18 dossiers | `methodology` 4 712 l. · `dashboard` 3 728 l. · `manhadjia` 3 352 l. · `lessons` 1 874 l. · `simulation` 1 399 l. · `gamification` 1 141 l. · `drive-design` 568 l. · `programme` 517 l. · `layout` 489 l. · `ui` 370 l. |
| `src/lib/` | 42 modules + 27 fichiers de test | voir §2.3 |
| `data/` (racine front) | 332 Ko | `chapitres-fiches-map.json`, `fiches-resume.json`, `ateliers/` |

Top des modules de `lib` par taille : `methodology-documents.ts` 2 207 · `api-client.ts` 1 705 ·
`manhadjia-lib.ts` 1 172 · `types.ts` 1 171 · `methodology-v2.ts` 1 116 · `annales-bac.ts` 979 ·
`methodology-chapters.ts` 749 · `progress-store.ts` 595 · `methodology-v1.ts` 586 ·
`lesson/evidenceService.ts` 456 · `lesson/coachService.ts` 395 · `lesson/practiceOutcome.ts` 393 ·
`methodology-checklists.ts` 373 · `lesson/sessionStateMachine.ts` 331.

### 2.2 Le gabarit de page — le même partout

```tsx
"use client"
export default function Page() {
  return (
    <AppShell>            // sidebar + header mobile + thème + RTL
      <AuthGuard>         // ← sans session : l'élève ne voit RIEN (le SSR rend un squelette)
        <main className="flex-1 p-6 overflow-auto">…</main>
      </AuthGuard>
    </AppShell>
  )
}
```

Conséquence, mesurée et non négociable (rapport §16.4) : sur une page gardée, le HTML reçu par le
navigateur **ne contient pas le contenu**. Un `curl` renvoie 200 + coquille vide. La preuve du rendu se fait
par `renderToStaticMarkup` ou par le module de données, jamais par un code HTTP.

### 2.3 Carte `page → module de données → moteur`

| Page(s) | Module de données | Moteur / API appelée | État mesuré |
|---|---|---|---|
| `/cours/[domaine]/[unite]/[chapitre]` | `active-lessons.ts` (55 leçons, type `ActiveLesson`) | repli `apiClient.getCours(chapitre)` si pas de leçon locale | **327 caractères de cours en moyenne** (223-376), 2-3 blocs, `visualHint` rempli **0 fois sur 160 blocs** |
| `/methodology` | `methodology-v1/v2.ts`, `methodology-checklists.ts` | `/api/methodology`, `/api/diagnostic/methodology` | composants sains ; le gate `method_percent == 100` conditionne l'accès à la salle |
| `/document-analysis/[scenarioId]` | `methodology-documents.ts` (68 documents, 6 types) | `/api/document-analysis/*` (+ `evaluate-v2`) | 13 documents sur 68 ont une grille ; `DocumentRenderer` + `ScenarioReadingMode` + `chart-scale.ts` (échelle mesurée, testée) |
| `/manhadjia/{verbe}` (22 pages) | `manhadjia-lib.ts`, `manhadjiya-tips.ts` | `/api/manhadjiya/*` (9 endpoints) | cohérent avec le livre ; remédiation pilotée par verbe |
| `/action-verbs/[slug]` | `methodology-verb-labels.ts`, table backend | `/api/action-verbs/{slug}/exercises` | le seul `reduce` de points restant est légitime (règles de score) |
| `/annales`, `/annales/[slug]`, `/read`, `/guided`, `/exam`, `/exam/correction` | `annales-bac.ts` (30 fiches) + `pdf-available.ts` | `/api/grade`, `/api/annales` | barème = échelle officielle 20 (F31) ; **0 `وضعية`**, 80/80 questions en français, 0 PDF utilisable sur 12 pointeurs LFS |
| `/drill`, `/exercises`, `/exercices/[chapitre]`, `/dix-minutes` | `lesson/*`, `recall/*`, `progress-store.ts` | `/api/session/next`, `/api/drill/*`, `/api/exercices/*` | 429 + quota testés ; muets en prod si API morte |
| `/bac-blanc` | `components/bac_blanc/BacBlancImmersif.tsx` (354 l.) | `/api/bac-blanc/{start,choose,save,submit,{id}/correction}` | 5 endpoints, schéma `schemas/bac_blanc.py` |
| `/simulation/*` (6 pages, 5 simulateurs) | composants autonomes | aucun | **les seules pages sans API ni garde de session** : elles marchent hors ligne |
| `/duel`, `/leaderboard`, `/achievements`, `/shop`, `/chatbot`, `/scanner`, `/feynman`, `/videos`, `/pulse`, `/map` | divers | `/api/social`, `/api/duels`, `/api/chatbot*`, `/api/gems`… | dépendance API totale → morts en prod tant que D1 n'est pas tranché |
| `/diagnostic/{global,units,chapter}` | `methodology-chapters.ts` | `/api/diagnostic/*` | 55 clés de chapitre, bijection vérifiée 13↔13 |
| `/admin/analytics` | — | `/api/admin/analytics/{global,methodology-gaps,students-at-risk}` | visible mais non listé dans la nav |

### 2.4 Navigation : 81 pages, 19 entrées

`src/components/layout/Sidebar.tsx` déclare **19 entrées** groupées en sections (اليوم · باك · نراجع · نتدرب ·
نسقسي / الدروس النشطة · الخريطة الذهنية · التجارب المقررة / 10 دقائق · محاكاة · إصلاح الأخطاء / الوضعية
الإدماجية · منهجية البكالوريا · أفعال الأداء · استغلال الوثائق / التشخيص · ورقة J-1 / التقدم · نظرة عامة),
plus une variante mobile de 5 entrées. Sur les 61 routes sans paramètre, **42 ne sont dans aucune
navigation** (dont 22 pages `/manhadjia/*`, `/bac-blanc`, `/duel`, `/feynman`, `/achievements`, `/videos`,
`/admin/analytics`, `/exercises` vs `/exercices/[chapitre]` qui se disputent le même usage).

**Et la landing `src/app/page.tsx` ne propose que deux liens : `/auth/register` et `/auth/login`.** Aucun
chemin « ouvre ton chapitre » avant la création de compte, alors que le contenu de cours est local.

### 2.5 Quatre systèmes parallèles de « leçon »

C'est le trait le plus structurant de l'architecture, et le moins assumé :

1. `/cours/…` → `active-lessons.ts` — par **chapitre** (55)
2. `/lecons-sciences-experimentales/[slug]` → `experimental-lessons-data.ts` — par **leçon science**
3. `/manhadjia/{verbe}` (22 pages) → `manhadjia-lib.ts` — par **verbe d'action**
4. `/methodology` + `/document-analysis` → `methodology-documents.ts` (68) — par **scénario**

Les quatre sont branchés ; un seul est relié programmatiquement (1↔4 via `methodology-chapters.ts` et
`getLessonForChapter`). `getChapterSlugByTitle` existe mais ne sert pas à fusionner 2 et 3.

---

## 3. Le contrat entre les deux moitiés

```
khawarizmi-frontend/src/lib/api-client.ts — 1 705 lignes
  l. 56   const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || ""
  l. 223  fetch(`${API_BASE_URL}${endpoint}`)           // en-t communs + session
  l. 385  POST ${API_BASE_URL}/api/auth/refresh         // refresh silencieux
  l. 646  POST /api/drill/submit      ·  l. 836  POST /api/chatbot/ask/stream (SSE)
  l. 1092 POST /api/grade             ·  l. 1255 POST /api/action-verbs/evaluate
  l. 1575 POST /api/exercices/{id}/correct
  → 122 méthodes, 71 chemins /api/… distincts
```

- **Un seul mode d'adressage depuis F32 : same-origin.** `API_BASE_URL = NEXT_PUBLIC_API_URL || ""` reste
  en place pour les clients qui voudraient partir en cross-origin (l'origine doit alors être dans
  `get_allowed_origins()` **et** dans la CSP). Mais le chemin de production est le **proxy runtime**
  `src/app/api/[...path]/route.ts`, qui **délègue** la résolution à `src/lib/api-origin.ts` :
  `API_ORIGIN || NEXT_PUBLIC_API_URL || http://localhost:8000` **lu à chaque requête**, par un seul
  résolveur partagé avec la CSP et le rewrite `/health` (depuis F33 — avant, trois endroits lisaient la
  variable et pouvaient diverger). Le handler reconstruit `${origine}/api/${path}` avec la query, transmet cookie et
  `Authorization`, passe le corps et le flux de la réponse (SSE), propage les statuts de l'amont, et renvoie
  la forme d'erreur du backend (`{erreur, status, path, method, requestId}`, `routes/errors.py`) en **502**
  si l'amont est injoignable — la cause technique part dans les logs serveur.
- **En prod, aucune variable posée ≠ « on tente localhost »** : le handler répond **501
  `{"code":"api_origin_non_configuré","attendu":"… sans /api"}` avant tout fetch** (F33). Le fallback
  `localhost:8000` reste en dev seulement. C'est ce qui manquait à D1 pour être visible depuis l'extérieur :
  un 502 réseau se lit « le backend est mort », un 501 nommé se lit « je n'ai rien configuré ».
- **Le rewrite `/api/:path*` n'existe plus** (et c'est le correctif, pas un nettoyage) : les rewrites du
  panier `afterFiles` de Next passent **avant** les routes dynamiques, donc il masquait entièrement le
  handler. Mesure : `API_ORIGIN` sur un port mort + amont vivant sur :8000 → la requête répondait le JSON
  de :8000, tests unitaires verts compris (rapport §19.2). `/health` garde son rewrite : c'est l'empreinte
  qui prouve qu'un domaine sert *ce* dépôt (objet JSON de `routes/health.py`, et 404 au format
  `{"erreur","status","path","method"}` — jamais `{"message","requestId"}`).
- **Conséquence opérationnelle** : changer de domaine Railway = éditer `API_ORIGIN` dans Vercel, **zéro
  rebuild**. L'ancien mécanisme (destination figée au build, CI qui ne re-déploie que Railway,
  `.github/workflows/ci.yml` l. 92-95) rendait la panne invisible et récurrente.
- **Erreurs normalisées côté back** : `routes/errors.py` renvoie un message arabe élève + `requestId` ;
  handlers branchés sur 400/401/403/404 (http), 422 (validation), 500 (générique), et sur la **classe**
  `RateLimitExceeded` (pas sur le code 429 — correction S38 : brancher le handler sur le code faisait planter
  les 429 manuels en 500, car `request.state.view_rate_limit` n'existe que pour le décorateur).
- **Sécurité de rendu** : `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` caméra/micro/géolocation coupées,
  CSP en production seulement (Turbopack en dev injecte de l'inline).

---

## 4. Backend : comment 209 endpoints sont branchés

```
main.py — 69 lignes, point d'entrée unique
 ├─ setup_monitoring()                       → Prometheus (routes/observability.py: GET /metrics/prometheus)
 ├─ FastAPI(**openapi_metadata, lifespan=routes/lifespan.lifespan)
 │    docs_url/redoc_url/openapi_url = None si ENVIRONMENT == "production"
 ├─ app.state.limiter = limiter (slowapi) + SlowAPIMiddleware   → quotas de correction
 ├─ CORSMiddleware(allow_origins=get_allowed_origins(), allow_credentials=True)
 ├─ app.include_router(admin_router)         → /api/admin/ingest-rag
 ├─ for router in ALL_ROUTERS: include       → 49 routers (routes/__init__.py)
 └─ handlers 400/401/403/404/422/500 + RateLimitExceeded
```

`routes/__init__.py` documente lui-même les retraits : « *phase2, phase4, badges retirés : doublons ou non
utilisés* » — alors que `routes/badges.py` (1 endpoint) existe toujours. **Une surface morte n'est pas
supprimée, elle est injoignable** : une page qui appelle `/api/badges/me` reçoit un 404 bien réel.

### 4.1 Répartition des endpoints (209 déclarés, mesurés par AST sur `routes/`)

| Domaine | Fichiers · endpoints | Points notables |
|---|---|---|
| Correction | `grade` 4 · `ai_evaluate` 1 · `evaluate` 1 · `exercices` 3 · `document_analysis_v2` 1 | `GET /api/grade/rubric/{question_id}` = porte d'entrée des grilles ; `GET /api/grade/metrics` |
| Méthodologie | `manhadjiya` 9 · `methodology` 1 · `methodology_flashcards` 2 · `diagnostic` 3 · `tutor` 1 | `/api/manhadjiya/{revision-tips,common-errors,cognitive-levels,verbs,verb/{slug},verb-units,contextual-remediation,practical-examples,analysis-terms}` — cœur qui fonctionne |
| Documents | `document_analysis` 7 · `document_analysis_v2` 1 | `scenarios`, `scenarios/{slug}`, `evaluate`, `…/correction`, `progress`, `review`, `weak-spots` |
| Annales & examen | `annales` 3 · `bac_blanc` 5 · `bac_blanc_intelligent` 2 · `programme` 3 | `POST /api/annales/seed` alimente `bac_subjects` (1 seul sujet en base aujourd'hui) |
| Leçons | `lessons` 2 · `cours` 2 · `chapitres` 1 · `lexique` 4 · `videos` 3 · `dual_coding` 3 | `GET /api/lessons/{chapter_slug}` sert le repli du §2.3 |
| Sessions & mémorisation | `session` 4 · `flashcards` 7 · `kunz_tunnel` 3 · `memory` 2 | `GET /api/recall/due` (FSRS), `POST /api/drill/submit` |
| Progression & pilotage | `aujourdhui` 7 · `progress` 2 · `dashboard` 1 · `pulse` 3 · `retry-errors` (front only) | `GET /api/aujourdhui/matrix`, `POST /api/aujourdhui/valider` |
| Tuteur & IA | `chatbot` 3 · `ai_chat` 2 · `chatbot_engagement` 8 | `ask/stream` en SSE ; boss-fight, mystery box, détection de confusion |
| Cartes mentales | `mindmap` 7 · `mindmap_methodology` 3 | génération asynchrone par `task_id` |
| Ludique & social | `gamification` 3 · `streaks` 3 · `gems` 5 · `avatar` 2 · `cities` 5 · `mystery_box` 3 · `leaderboard` 3 · `onboarding` 3 · `social` 13 · `duels` 6 · `phase5` 12 · `phase1` 2 · `phase3` 3 · `phase6` 6 | **≈ 83 endpoints sur 209 (40 %) pour l'engagement**, contre 16 pour la méthodologie |
| Infra & divers | `health` 5 · `observability` 1 · `auth` 6 · `admin_analytics` 3 · `admin_ingest` 1 · `orientation` 2 · `payment` 1 · `badges` 1 (non branché) | Chargily (`POST /api/payment/webhook/chargily`) |

### 4.2 Configuration (`config.py`, pydantic Settings)

```
debug · cache_ttl=3600 · data_dir
openai_base_url / openai_model="gpt-4o-mini" · ia_temperature=0.3 · ia_max_tokens=600
vision_base_url / vision_model (OCR & schémas)
zai_* · zenmux_* · nara_*        → 4 fournisseurs LLM interchangeables + json_mode_providers[]
savoir_enabled_verbs[] · savoir_remediation_enabled=False · savoir_veto=True
local_rubric_grader=False        ← DRAPEAU DÉCISIF : sans lui, la correction retombe sur le LLM
chargily_secret_key · ENVIRONMENT · DATABASE_URL
```

---

## 5. La machine à corriger — cœur pédagogique

```
copie d'un élève (une question, en arabe)
  │
  ├─ POST /api/grade (routes/grade.py)         quota slowapi → 429 + message arabe (testé côté front)
  │
  ├─ services/local_grader.py (844 l.)         GRADER_VERSION = "1.2.0"
  │     critères chargés depuis data/rubrics/questions/{id}.v1.json
  │     scoring par critère, aucun appel réseau, déterministe
  │        ⚠ 13 questions équipées pour ~68 documents + ~55 exercices d'annales
  │
  ├─ services/savoir_corrector.py (953 l.)     verbes d'action (الأفعال) → niveau cognitif
  │     VERB_COGNITIVE_LEVELS couvre les 3 niveaux de la هيكلة (استرجاع / استدلال / مسعى علمي)
  │     remédiation par verbe · veto si le verbe exigé n'est pas respecté
  │
  ├─ prompts/correction_prompt.py (1 128 l.)  REVISION_TIPS_AR["bac_exam_structure"]
  │     التمرين الأول 5 · الثاني 7 · الثالث 8 · المجموع 20  ← conforme au livre (rapport §18)
  │     + correction_prompt_v2 (112 l.) · evaluation_prompt (200 l.) · free_chat_prompt (290 l.)
  │     · scientific_knowledge (1 047 l.) — 2 777 lignes de prompts au total
  │
  ├─ si local_rubric_grader=false → LLM + services/llm_guard.py (359 l.)
  │
  └─ score → services/fsrs_unified.py (1 048 l.)  → prochaine révision
             → /api/progress, progress-store.ts (front, localStorage) → /progress, /aujourdhui
```

**Deux verrous à connaître** : (1) la salle d'examen n'est pas accessible au premier venu —
`method_percent == 100 AND overall_training_percent == 100` ; (2) sans grille dans `data/rubrics/questions/`,
le score par critère n'existe pas. `data/rubrics/` = **32 fichiers** : `index.json` **13 rubriques validées**,
`questions/` 13, `templates/` 6, `mixins/` 1, `drafts/` **10 squelettes à valider** (5 questions +
5 documents, README à part), régénérables par `scripts/gen_rubric_skeletons.py`.

---

## 6. Données de contenu : qui détient quoi

| Emplacement | Contenu | Volume mesuré | État |
|---|---|---|---|
| front `src/lib/active-lessons.ts` | 55 leçons × 7 composants | 189 lignes, **327 car. de texte par leçon** | 55/55 ont résumé, concepts (+erreur fréquente), 2-3 blocs, ≥3 auto-vérifs, erreurs, `bacLinkAr`, verbes liés, scénario, prompt de révision. **0 visuel** |
| front `src/lib/methodology-chapters.ts` | 55 chapitres ↔ méthodo | 749 l. | bijection saine, testée |
| front `src/lib/methodology-documents.ts` | 68 documents, 6 types | 2 207 l. | 13 avec grille ; 11 exposés comme « استغلال الوثائق » |
| front `src/lib/annales-bac.ts` | 30 fiches d'annales | 979 l. | 10 structurées (2 options chacun) ; **0 `وضعية`** dans tout le fichier ; 80/80 questions sans caractère arabe ; `duree: 180` partout |
| front `src/lib/manhadjia-lib.ts` + `manhadjiya-tips.ts` | 22 verbes, règles, exemples | 1 172 + 224 l. | cohérent avec le livre |
| front `data/` + `src/lib/pdf-availability.ts` | fiches J-1, ateliers, PDF | 332 Ko · 12 pointeurs LFS | **0 PDF utilisable** |
| back `data/*.json` | 68 fichiers | **4,5 Mo** | `qcm_items`, `annales_sciences_3as` (OCR corrompu), `programme_sciences_3as`, `lexique_svt_terminale_complet`, `golden_set_onec`, `manhadjiya_v1_seed`, `sciences_methodologie`, `methodologie_sciences_3as`, `micro_concepts`, `questions_taggees` |
| back `data/rubrics/` | grilles | 32 fichiers | goulot n°1 pédagogique |
| racine du dépôt | livres sources | `LIVRE-MANHADJIYA.md` 5 397 l. · `504601676-كتاب-العلوم…txt` 218 386 car. · `BAREME-L0.md` · `FINALBAC_VOLUME_1/2.txt` | **la seule matière première réelle pour écrire les 55 leçons** |

---

## 7. État élève et persistance

- `src/lib/auth-context.tsx` : session + refresh ; `AuthGuard` (`src/components/auth/`, 49 l.) masque le rendu.
- `src/lib/progress-store.ts` (595 l.) : progression en localStorage + synchro API ; snapshots de session.
- `src/lib/lesson/` : `sessionStateMachine.ts` (331 l.) + `sessionReduce.ts` (292 l.) +
  `practiceOutcome.ts` (393 l.) + `evidenceService.ts` (456 l.) + `coachService.ts` (395 l.) — machine à états
  **pure et testée**, c'est la partie la plus solide du front.
- `src/lib/recall/` : machine à états du rappel espacé (315 l. de test), branchée sur `/api/recall/due`.
- `src/lib/method/checklistUiStore.ts` : état des checklists de méthode (persisté).
- Gamification : XP, gems, streaks, badges côté backend (`models/gamification.py`, `services/`),
  composants dans `src/components/gamification/` (15 fichiers, 1 141 l.).

---

## 8. Qualité : ce qui est verrouillé

| Côté | Mesure du 2026-08-31 |
|---|---|
| Front | **970 tests vitest** dans 27 fichiers · `tsc --noEmit` 0 erreur · `eslint src` 0 erreur / **12 warnings** (surfaces mortes volontairement conservées) · `next build` ✓ |
| Back | **139 fichiers de test**, 23 986 lignes · CI : smoke + tests Methodology |

Style de test adopté (et à maintenir) : **génératif, pas de snapshot figé**. Les tests énumèrent la source —
« toute clé de `chapitres-fiches-map.json` a une page », `5 + 7 + 8 == BAC_NOTE_SCALE_POINTS`,
« aucune leçon ne sort sous 1 500 caractères », « `VERB_LABELS_AR` couvre toute l'union
`MethodologyVerbSlug` » — et **échouent quand on ajoute une surface sans la brancher**. Les gardes de source
(`readFileSync` + `toContain`) verrouillent le câblage côté rendu, là où DOM Testing n'apporte rien.

---

## 9. Le parcours élève que l'architecture autorise réellement

```
  /  ──(2 liens : s'inscrire / se connecter)──▶  /aujourdhui
        │
        ├─▶ /cours/… ── 327 caractères, 0 schéma ──▶ /drill · /dix-minutes   ← questions via API (morte en prod)
        ├─▶ /annales  ── 2 options fusionnées, 0 وضعية, tout en français
        ├─▶ /methodology · /document-analysis · /manhadjia/*   ← LE VRAI POINT FORT : 68 scénarios,
        │      verbes, auto-vérifs, échelles de graphes mesurées   13 grilles sur 68
        └─▶ /diagnostic ── note de méthode ──▶ GATE 100 % ──▶ /bac-blanc
                                                  └── butée : sans les 55 grilles, pas de score par critère
```

Lecture d'architecte : la couche **données locales** est robuste (pas de latence, survit à la panne API, 7
composants sur 55/55 leçons) ; la couche **orchestration** (garde, gate, quota, machine à états) est couverte
par des tests ; **les deux étages manquants sont le contenu de cours (8,24 % du volume du livre de référence)
et les grilles de correction (13 sur 68 + 10 brouillons).** Ajouter des pages n'augmente le rendement
d'aucun des deux ; et 42 routes hors navigation dégradent la compréhension du chemin.

---

## 10. Dettes structurelles, classées par rendement pédagogique

| # | Dette | Preuve | Effet tant que c'est là |
|---|---|---|---|
| D1 | Origine de l'API mal branchée en prod (le front appelle un domaine qui ne sert pas ce dépôt) | rapport §11, §19 ; `verify_prod_api.py` | **25 pages sur 81 (31 %) dépendent de l'API** : correction, drill, tuteur, progression. Côté code, clos (F32+F33 : proxy lu à la requête, résolveur unique, 501 nommé, `/health` qui expose les drapeaux ; le job CI `prod-wiring` est écrit mais attend `docs/patches-todo/`, faute de permission `workflows`). **Reste deux gestes hors dépôt**, à ma main : `API_ORIGIN` dans Vercel (sans `/api`) puis Redeploy ; `LOCAL_RUBRIC_GRADER=true` dans Railway. Tant qu'ils manquent, D1 reste mesuré négatif — et le dit |
| D2 | 55 leçons fabriquées par gabarit, contenu scientifique non écrit | `lessonCorpusStats()` : focus 4 899 car. · gabarit 9 396 · substitution-de-nom 24 779 · duplication ×6,71 | **présentation corrigée (F35)**, pas le contenu : la page s'appelle « الإطار المنهجي للدرس », elle affiche un bandeau « محتوى هذا الدرس لم يُكتب بعد », les paragraphes partagés portent « نص مشترك مع 16 درسًا », et le générateur ne distribue plus aucun verdict (l'auto-notation arabe-contre-français est retirée). Écrire les 55 leçons reste à ta main ; le point d'entrée est `registerAuthoredLesson(slug, blocs)` |
| D3 | Grilles de correction : 13 validées sur ~68, 10 brouillons non validés | `data/rubrics/index.json` | le correcteur local ne peut pas noter critère par critère ; la salle reste fermée |
| D4 | Annales sans التمرين الثالث (8 ن) et intégralement en français | §18.4 : 0 `وضعية`, 80/80 questions | la rubrique « BAC » n'entraîne pas à l'épreuve réelle |
| D5 | 42/61 routes hors navigation, 4 systèmes de leçons parallèles | `Sidebar.tsx` (19 href) | l'élève ne sait pas par où commencer |
| D6 | `AuthGuard` posé avant la lecture d'un contenu 100 % local | `page.tsx` de `/cours/…` | friction maximale pour 327 caractères ; abandon avant d'avoir vu une leçon |
| D7 | `duree: 180` min vs 240 min de budget conseillé par le livre | §18.5 | l'élève sort du sujet avec le bloc de 8 ن entamé |
| D8 | 0 PDF sur 12 pointeurs Git LFS ; `bac_subjects` = 1 sujet | `pdf-availability.ts`, `/api/annales` | aucun énoncé officiel à montrer, donc aucun barème officiel à scorer |

**Ordre de traitement recommandé** : D1 (une variable, `API_ORIGIN`, plus deux drapeaux — débloque les 25 pages interactives) → D2 (extraire du
livre déjà dans le dépôt, 55 chapitres, validation éditoriale par toi) → D3 (valider les 10 brouillons, puis
générer à partir des vrais barèmes) → D4/D8 (mêmes sources : ONEC) → D5/D6 (une nav et un chemin d'entrée) →
D7 (un arbitrage de chiffres).

---

## 11. Reproduire ces chiffres

```bash
# FRONT
cd khawarizmi-frontend
find src/app -name 'page.tsx' | wc -l                              # 81 pages
find src/app -name 'page.tsx' | grep -c '\['                        # 19 dynamiques
find src/components -name '*.tsx' | wc -l                            # 148 composants
grep -c 'href: "/' src/components/layout/Sidebar.tsx                 # 19 entrées de nav
npx vitest run 2>&1 | grep -E "Tests |Test Files"                    # 970 / 27

cat > _cov.ts <<'TS'                                                 # volume des leçons (⚠ dans khawarizmi-frontend)
import { activeLessons } from "@/lib/active-lessons"
const c = activeLessons.map(l => (l.lessonBlocks ?? []).reduce((a, b) => a + b.contentAr.length, 0))
console.log({ lecons: c.length, min: Math.min(...c), max: Math.max(...c),
  moyenne: Math.round(c.reduce((a, b) => a + b, 0) / c.length),
  visuels: activeLessons.filter(l => l.lessonBlocks.some(b => !!b.visualHint)).length })
TS
npx tsx _cov.ts && rm -f _cov.ts                                    # 55 · 223 · 376 · 327 · 0

# BACK
cd ../khawarizmi-backend
ls routes/*.py | wc -l                                              # 62 fichiers de routes
grep -c '\.router,' routes/__init__.py                              # 49 routers branchés
python3 - <<'PY'                                                     # 209 endpoints (AST, sans exécuter)
import ast, pathlib
n = 0
for p in sorted(pathlib.Path('routes').glob('*.py')):
    t = ast.parse(p.read_text(encoding='utf-8'))
    n += sum(1 for x in ast.walk(t) if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))
             for d in x.decorator_list if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
             and d.func.attr in ('get', 'post', 'put', 'patch', 'delete'))
print("endpoints déclarés :", n)
PY
ls services/*.py | wc -l                                            # 95 · find tests -name 'test_*.py' | wc -l → 139
python3 -c "import json;print(len(json.load(open('data/rubrics/index.json'))))"   # 13 grilles validées
find data/rubrics -type f | wc -l                                   # 32

# CÂBLAGE PROD : vérifier que le proxy runtime n'est pas masqué par un rewrite (rapport §19.4)
cd ../khawarizmi-frontend && npm run build >/dev/null 2>&1
python3 -c "
import json,pathlib
rm = json.load(open('.next/routes-manifest.json'))
after = [{k: r[k] for k in ('source','destination')} for r in rm['rewrites']['afterFiles']]
print('rewrites afterFiles :', after)      # attendu : /health seulement, JAMAIS /api/:path*
print('route proxy :', '/api/[...path]' in json.load(open('.next/app-path-routes-manifest.json')))
"                                            # attendu : True
# puis, en dev : API_ORIGIN=http://127.0.0.1:8999 (port mort) → /api/... doit répondre un 502
# {"erreur":"Le serveur de correction est injoignable…","requestId":"proxy-…"}. Un JSON d'amont vivant
# à cette place prouverait qu'un rewrite absorbe encore les appels.
# puis, sans aucune variable en prod : /api/... doit répondre 501 {"code":"api_origin_non_configuré"}
# (NODE_ENV=production). Un 502 ici prouverait que le fallback localhost est encore tenté en prod.

# Et sur la production réelle, le verdict en une commande (aucune dépendance, urllib seul) :
python3 khawarizmi-backend/scripts/verify_prod_api.py --front https://<app>.vercel.app --back https://<svc>.up.railway.app
# exit 1 + trois familles : A amont ≠ ce dépôt · B proxy du front ne suit pas · C drapeaux de correction éteints
# `/health` expose désormais correction.{local_rubric_grader, savoir_remediation_enabled, savoir_veto,
# grader_version} : la panne « domaine bon mais correction éteinte » est devenue lisible sans lire les logs.
```

*Règle de lecture* : ce document décrit **ce qui est**. Ce qui devrait être — la liste des défauts par priorité
pédagogique et les correctifs appliqués (F1→F31) — est dans `AUDIT-SURFACES-CORRECTION-SITE-2026-08-30.md`
(§0→§18).
