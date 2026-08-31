# Audit — comment les exercices des rubriques sont corrigés sur le site (2026-08-30)

**Cible :** le chemin réel de l'élève — pages → composants → `api-client` → routes FastAPI → moteur
local `grade()` — et **non** le moteur seul (déjà audité dans `AUDIT-CORRECTEUR-LOCAL-2026-08-30.md`,
F1–F11, moteur **1.2.0**).

**Branche :** `arena/01a05476-project-sinamind`, base `9ffb1ab` (merge PR #17).

**Méthode :** lecture du code des deux côtés, exécution du chemin complet via `ASGITransport`
(TestClient sur l'app réelle, 0 LLM, 0 DB, 0 réseau), suites `pytest` / `vitest`, `tsc`, `ruff`,
`eslint`. Sonde reproductible : **`khawarizmi-backend/scripts/probe_audit_surfaces_site.py`**
(54 assertions, **54 OK · 0 échec** à la date de ce rapport).

> **Note de reprise.** Une session antérieure avait produit un compte rendu de cet audit et un
> commit local `1b4df85`. **Ce commit n'était pas dans le dépôt de cette session** (checkout
> revenu à `9ffb1ab`, ni rapport ni sonde sur le disque). Tout a donc été **re-dérivé et
> re-mesuré ici** ; deux affirmations du compte rendu antérieur ne résistent pas à la vérification
> et sont corrigées en §3 (F12 requalifié, bac blanc).

---

## 0. Verdict en une ligne

> **Les 13 grilles git sont bien branchées, et c'est le seul chemin qui note vraiment en local :
> `ScenarioRunner → POST /api/grade`. Tout le reste est soit muré (honnête), soit vivant mais
> structurellement non-noté, soit mort.** Trois défauts réels trouvés côté site : **F14 (haut)**
> le quota de correction était clé par **IP** et non par compte — derrière le proxy, les 15
> corrections/h étaient **partagés par tous les élèves du site** et le plan `pro` n'était jamais
> reconnu ; **F12 (moyen)** le 429 de quota sortait hors contrat d'erreur et **écrasait toutes les
> notes du scénario** dans l'UI (crash 500 latent) ; **F15 (moyen)** le bac blanc appelle le
> correcteur local avec des ids qui ne peuvent **jamais** rencontrer une grille. F13 reste dû :
> trois surfaces de correction backend sans appelant frontend. **F12/F14/F15 corrigés (S38/S39),
> gardes ajoutées.**
>
> Et **F18** : la CI ne se déclenchait **jamais** (filers sur `main`, branche inexistante ; base
> réelle `master`) et la suite `grade` n'était dans aucun gate — la PR #17 a été fusionnée sans
> un seul test exécuté. Correctif livré en patch (`patches/F18-ci-gate-fix.patch`), la permission
> `workflows` manquant au token de session.

---

## 1. Carte des surfaces qui demandent une correction

| Surface (page) | Composant / appel | Méthode `api-client` | Route | Moteur | Ce que reçoit l'élève |
|---|---|---|---|---|---|
| `/document-analysis/[scenarioId]`, `/document-analysis/chapters/[chapterSlug]`, `/diagnostic/chapters/[chapterSlug]` | `ScenarioRunner.submit()` | `grade()` | `POST /api/grade` | `grade()` 1.2.0, grille git | **Note locale réelle** (13 ids câblés = les 13 grilles) |
| id sans grille dans ces mêmes pages | `ScenarioRunner` → `ungradedEvaluation` | `grade()` | `POST /api/grade` → 422 | — | `ungraded` + `banner_ar`, **jamais un 0** |
| question sans `gradeQuestionId` du tout | `ScenarioRunner:351` | — (aucun appel) | — | — | mur `NoLocalGradeWall` |
| `/action-verbs/[slug]` (cartes exercices) | `NoLocalGradeWall:397` | — | — | — | mur `NoLocalGradeWall` |
| `/action-verbs/[slug]` (zone réponse) | `submitAnswer()` | `evaluateVerbAnswer()` | `POST /api/action-verbs/evaluate` | `grade_or_none` | **vivant mais toujours `ungraded`** : candidats `("verb:<slug>", …)`, aucune grille ne s'appelle `verb:*` |
| `/diagnostic/global` | `NoLocalGradeWall` | — | — | — | mur `NoLocalGradeWall` |
| `/annales/[slug]/exam/correction` (bac blanc) | `getBacCorrection()` | `getBacCorrection()` | `GET /api/bac-blanc/{sid}/correction` (notes calculées à `/submit`) | `grade_or_none` | **toujours `ungraded`** — voir F15 |
| `/drill/[unit_id]` | QCM local du navigateur | `submitDrillQcm()` | `/api/session/next`, `/api/drill/qcm…` | pas de correction de copie | le site ne soumet **jamais** de copie libre |
| `/exercices/[chapitre]` | liste seulement | `listExercices` (lecture) | — | — | **aucun point d'appel de correction** |
| *(backend)* `/api/exercices/{id}/correct` | — | `correctExercise()` | idem | `grade_or_none` | **mort côté site** (F13) |
| *(backend)* `/api/drill/submit` (copie libre) | — | `submitDrillAnswer()` | idem | `grade_or_none` | **mort côté site** (F13) |
| *(backend)* `/api/document-analysis/evaluate-v2` | — | `evaluateDaAnswersV2()` | idem | `grade()` | **mort côté site** (F13) |
| *(backend)* `/api/evaluate/methodology` | — | — (zéro appelant) | idem | `grade_or_none` | **mort côté site**, porteur du quota (S36) |

Mesures de câblage (probe S1, S11) : **13 `gradeQuestionId`** dans
`src/lib/methodology-documents.ts` = exactement les **13 grilles** de `data/rubrics/questions/`
aucune orpheline dans les deux sens ; `ScenarioRunner` monté sur **3 pages** ; **un seul** `fetch`
vers `/api/grade` dans tout le frontend.

---

## 2. Ce que reçoit l'élève, mesuré sur l'app réelle (probe, 12 sections)

| # | Contrôle | Résultat mesuré |
|---|---|---|
| S2 | copie modèle des 13 grilles, via HTTP | **13/13 → `method_percent=100`, `overall=100`, tous les critères `full`, `all_correct`** |
| S3 | `question_id` inconnu | **422** `code=ungraded`, **aucun** champ `score`/`percentage` fabriqué |
| S4 | copie vide | 200 + `« الإجابة فارغة… »` + bannière `ليست علامة بكالوريا رسمية` |
| S5 | deux axes, copie « 36 ATP » | `method=100` / `overall=40`, `caps_applied=['science']`, `science_status=error` |
| S5 | bourrage lexical + le 18 du document | `stuffing_suspected=true`, `overall=50` (cap), `method=75`, `diagnosis={code: stuffing}` |
| S6 | fix F1 de l'audit moteur, **vu depuis le site** | `لأن → لأنها` sur `yeast-glucose-interpret` → **100 %** (et non 75 %) |
| S7 | 2ᵉ soumission identique | `from_cache: false → true`, note identique, **quota non re-consommé** |
| S8 | fuite de secrets de grille | aucun `model_answer`, `variants`, `keypoints`, `counter_examples`, `advice_by_gap` dans la réponse ni dans `/api/grade/rubric/{id}` |
| S9 | budget 15/h épuisé | `200 ×15` puis **429 propre** (`code=quota_exceeded`, message arabe, `Retry-After: 3599`), **zéro 500** |
| S10 | sentier de crash d'origine | avec `limiter.enabled=False` : **200** (plus de 500) ; un 422 n'est plus capté par le handler 429 |
| S12 | qui paie le quota | clé = `user:<id>:<plan>` ; **free 15/h, pro 80/h** ; le compte B n'est pas pénalisé par le budget de A |
| S13 | bac blanc | **8/8 exercices du sujet seed `bac-svt-2025` non résolus** → `ungraded`, jamais une note inventée |

---

## 3. Findings

### F14 — BUG (haut) : le quota de correction était clé par IP, pas par compte — **CORRIGÉ (S39)**

**Fait.** `rate_limit._get_user_plan()` décodait le JWT sans `options={"verify_sub": False}`, alors
que les tokens de l'app portent `sub` en **int** (`deps.get_current_user`, lui, passe l'option — le
commentaire le dit). python-jose lève `JWTClaimsError: Subject must be a string.`, l'`except` avale,
et `get_user_key()` retombe sur `get_remote_address(request)`.

**Pourquoi c'est grave ici.** `uvicorn main:app` est lancé **sans `--proxy-headers`**
(`Dockerfile`, `railway.toml`) et l'app n'a pas de `ProxyHeadersMiddleware` : `request.client.host`
est l'IP du proxy. Donc, derrière le déploiement réel :

1. **un seul seau de 15 corrections/h pour tout le site** — le 16ᵉ élève de l'heure est bloqué,
   quel que soit son compteur personnel ;
2. **le plan `pro` n'est jamais lu** → `evaluate_limit()` = 15/h au lieu de 80/h et `chat_limit()`
   = 20/h au lieu de 100/h : les élèves payants étaient bridés au tarif gratuit, sur
   `/api/grade`, `/api/evaluate`, `/api/ai/chat`, `/api/ai/evaluate`, `/api/document-analysis/evaluate-v2`,
   `/api/dual-coding/evaluate` (même fonction de clé) ;
3. un token sans `sub` fabriquait la clé mutualisée `user:None:free`.

**Preuve.** 6 des 8 tests de `tests/test_grade_s39.py` **échouent sur le code d'origine** et passent
après le correctif. Probe S12 : `clé=user:991012:free`, `free → 15/hour`, `pro → 80/hour`,
compte B `200` pendant que compte A est à `429`.

**Fix.** `verify_sub: False` + refus explicite d'un `sub` manquant (repli IP), dans `rate_limit.py`.
Les compteurs deviennent par élève, et le tarif payant est respecté.

---

### F12 — BUG (moyen) : le 429 de quota cassait le scénario entier, et crashait en 500 sous condition — **CORRIGÉ (S38)**

**Fait.** `enforce_evaluate_quota` **levait** `HTTPException(429)` depuis `/api/grade` (route non
décorée), et `main.py` enregistrait le handler slowapi **sur le statut 429** :
`app.add_exception_handler(429, _rate_limit_exceeded_handler)`. Or ce handler lit
`request.state.view_rate_limit`, que **seul** le chemin décorateur/middleware de limitation pose.

**Ce qui se passait vraiment** (mesuré, et cela corrige le compte rendu antérieur) :

* **par défaut** : pas de 500 — `SlowAPIMiddleware` (auto-check) pose `view_rate_limit = None` pour
  toute route non exemptée, donc le handler aboutit… en un 429 **hors contrat** :
  `{"error": "Rate limit exceeded: تم بلوغ حد التصحيح…"}`, **sans** `erreur`, **sans** `Retry-After` ;
* **dès que l'auto-check ne passe pas** (`limiter.enabled = False`, middleware court-circuité,
  route exemptée, `SlowAPIMiddleware` retirée au profit des seuls décorateurs) : l'état n'existe pas →
  `AttributeError: 'State' object has no attribute 'view_rate_limit'` → **HTTP 500**. Reproduit
  dans ce dépôt, traceback complet à l'appui (sentier : `routes/grade.py:132 → rate_limit.py:85`).

**Impact élève, dans les deux cas.** C'est le plus sévère, et il était manqué :
`apiClient.grade()` **levait** sur ce 429 non conforme (`data.erreur` absent), et
`ScenarioRunner.submit()` fait `Promise.all(...)` dans un `try { } catch { }` qui marque
**toutes** les questions du scénario `تعذر التصحيح`. Un élève à quota épuisé voyait donc
**ses copies déjà notées jetées**, sans jamais comprendre qu'il s'agissait du budget horaire.

**Fix (S38), des deux côtés.**

* Backend : `enforce_evaluate_quota` **retourne** une `JSONResponse(429)` (contrat `erreur` +
  `code=quota_exceeded` + `banner_ar` arabe + `retry_after_s`/`Retry-After`), et ne lève plus rien ;
  `main.py` branche le handler sur la **classe** `RateLimitExceeded` avec un handler maison
  **None-safe** (`routes/errors.py`) ; `Limiter(swallow_errors=True, in_memory_fallback_enabled=True)`
  pour qu'une panne de storage des limites dégrade au lieu de mettre le site en 500.
* Frontend : `grade()` mappe un 429 en **`ungraded` honnête** avec le message serveur + `quota: true`
  et `retry_after_s` ; `Promise.all` → **`Promise.allSettled`**, une question qui échoue ne supprime
  plus les autres. Un 5xx reste une panne (throw).
* Gardes : 12 tests dans `tests/test_grade_s38.py` (dont « le handler survit à l'absence de
  `view_rate_limit` », « plus de `raise HTTPException` dans `rate_limit.py` », « le handler est branché
  sur la classe, pas sur 429 ») et **5 tests** `src/lib/api-client.grade-quota.test.ts` — **3 des 5
  échouent sur l'`api-client.ts` d'origine**.

---

### F15 — BUG (moyen) : le bac blanc ne peut rencontrer aucune grille — **CORRIGÉ (S39, pont)** + **F16 (faible) : « 0 % » affiché sur un non-noté**

**Fait.** `/api/bac-blanc/submit` corrige bien avec le moteur local
(`grade_or_none(resolve_question_id(ex_id, f"bac:{annale}:{ex_id}"), …)`), mais le seed
(`scripts/bac_blanc_seed.json`, `bac-svt-2025`) utilise `s1-e1…s2-e4` alors que les grilles git
s'appellent `bac2023-s1-ex2-analyse-traduction`, `enzyme-temp-analyse`, etc. **Aucun recouvrement
d'ids** → les 8 exercices du sujet sont systématiquement `ungraded`. La grille 2023 existante
n'est atteignable d'**aucune** surface du site (seulement par
`tests/test_grade_bac2023_ml901.py`, au niveau moteur) — et, contrairement au compte rendu
antérieur, le bac blanc n'affiche **pas** `NoLocalGradeWall` : il affiche le retour `ungraded` de
cette route.

**F16.** L'en-tête de la page de correction est honnête (`allUngraded` → `—` + bannière), mais
**chaque ligne d'exercice affichait `{ex.percentage}%`, donc « 0 % »** pour une copie non notée.

**Fix.** `BacExercise.grade_question_id` (champ explicite, premier candidat de
`resolve_question_id`) — aucun contenu d'épreuve inventé, la donnée reste à la main de l'auteur :
il renseigne le `rubric_id` du sujet et la correction locale s'active. UI : la ligne d'exercice passe
par `formatTrainingPercent` (`—` comme l'en-tête). Sondes : probe S13 + 4 tests dans
`tests/test_grade_s39.py`.

---

### F13 — DETTE (moyen) : trois surfaces de correction backend sans aucun appelant frontend — **CONSTATTÉ, à trancher**

Mesuré (probe S11) : `apiClient.submitDrillAnswer` (→ `/api/drill/submit`, copie libre, S10),
`apiClient.correctExercise` (→ `/api/exercices/{id}/correct`) et `apiClient.evaluateDaAnswersV2`
(→ `/api/document-analysis/evaluate-v2`) sont **appelés par zéro page, zéro composant**.
`/drill` ne fait que du QCM local ; `/exercices/[chapitre]` ne liste que des exercices. S'y ajoute
`/api/evaluate/methodology` : route vivante (auth + quota partagés, S36) sans **aucun** appelant.

Conséquence de mesure, pas seulement d'hygiène : ces routes tournent sur `grade_or_none`, donc
répondent `ungraded` pour les exercices DB (aucune grille `exercice-{id}` n'existe) — les brancher
tel quel n'apporterait aucune note. **Décision produit** : soit alimenter les grilles et brancher,
soit supprimer les routes et les méthodes mortes. Le rapport ne tranche pas.

### F18 — PROCESSUS (haut, silencieusement le plus coûteux) : la CI ne se déclenche jamais, et le suite grade n'était dans aucun gate — **CORRIGÉ (S39)**

**Fait.** `.github/workflows/ci.yml` se déclenche sur `push: [main, fabuleux/*]` et
`pull_request: [main]`. Or `origin/HEAD → origin/master` et **`main` n'existe pas** dans le dépôt
(unique branche distante : `master`). Aucune des trois conditions n'est jamais remplie :
`backend-tests`, `frontend-tests` **ne tournent pas**, et `deploy-railway` (gardé
`if: github.ref == 'refs/heads/main'`) non plus. La PR #17 — qui a livré le moteur 1.2.0 — a donc
été fusionnée **sans aucun test exécuté**. Le compte rendu d'audit précédent indiquait
« gate CI actif » : c'était faux (le gate ne pouvait pas se déclencher).

**Second trou.** Même quand elle tourne, l'étape backend ne sélectionnait que
`test_methodology*.py`, `test_diagnostic.py`, `test_couche3.py`, `test_tutor.py`,
`test_bac_blanc_intelligent.py`, `test_mindmap_methodology.py` — **pas `tests/test_grade_s*.py`**,
alors que `grade()` est le seul chemin qui note des copies d'élèves sur le site, et pas
`scripts/validate_rubrics.py` (le gate auteur des 13 grilles). Les 16 gardes de ce correctif
seraient restées hors CI.

**Fix proposé — livré en patch, pas en commit.** `pull_request.branches` reçoit `master`
(+ garde `main` conservée) ; deux étapes supplémentaires : `pytest tests/test_grade_s*.py
tests/test_local_grader.py tests/test_grading_sanity.py tests/test_answer_sanity.py`
(**278 ✓ en 1 s**, 0 DB, 0 Redis) et `python scripts/validate_rubrics.py`.
Le token de la session d'agent **n'a pas la permission `workflows`** (`! remote rejecting:
refusing to allow a GitHub App to create or update workflow … without 'workflows' permission`),
donc le correctif est applicable par un humain :

```bash
git apply patches/F18-ci-gate-fix.patch     # dry-run vérifié : git apply --check → OK
```

**Le déclencheur `push` est volontairement laissé tel quel** : l'y élargir à `master` activerait
`deploy-railway` en production sur chaque push — décision d'exploitation à prendre séparément,
pas par effet de bord d'un audit.

### F17 — OBSERVATION (faible) : le quota ne couvre qu'un tiers des corrections

`enforce_evaluate_quota` n'est appelé que par `/api/grade` et `/api/evaluate/methodology` (morte).
`/api/action-verbs/evaluate`, `/api/exercices/{id}/correct`, `/api/drill/submit`,
`/api/document-analysis/evaluate*` et `/api/bac-blanc/submit` corrigent localement **hors budget**.
Tant que `/api/grade` est la seule surface vivante, l'effet est nul ; si F13 est tranché par le
branchement, il faudra étendre l'appel (une ligne par route).

---

## 4. Ce qui est confirmé sain (à ne pas « réparer »)

* **Un seul juge.** 13/13 grilles passent par `grade()` 1.2.0 ; `scripts/validate_rubrics.py`
  **13 grilles OK** (modèle ≥ 85 %, hors-sujet, 36 ATP, vide, contre-exemples).
* **Aucun 0 volé, aucun % inventé** : 422 `ungraded` côté `/api/grade`, `grade_or_none` partout
  ailleurs, `ungradedEvaluation` côté UI, `allowSecondAttempt` et XP verrouillés par le contrat
  (`mayAwardXp`).
* **Les deux axes** (méthode / global) remontent jusqu'à l'UI, caps et diagnostic nommés compris.
* **Pas de fuite** de `model_answer`, `variants`, `keypoints`, contre-exemples ou conseils par gap.
* **Le cache ne rejoue pas le quota** (S7) et n'écrit pas FSRS (S28).

---

## 5. État des suites et rejeu

| Contrôle | Résultat |
|---|---|
| `pytest tests/` (backend) | **1344 ✓ / 24 ✗ / 13 skipped / 5 xfailed** — les **24 ✗ sont préexistants** sur `9ffb1ab` (22 `test_fsrs_unified.py`, 2 `test_evaluate.py`, dépendants d'une DB), **identiques avant/après** |
| `-k grade` | **254 ✓** (234 sur la base + 20 nouvelles gardes S38/S39) |
| `-k methodology` | **82 ✓** |
| `scripts/validate_rubrics.py` | **13 grilles valides** |
| `ruff check` (fichiers touchés) | **All checks passed** (19 alertes préexistantes ailleurs dans le dépôt, non touchées) |
| `vitest run` (frontend) | **804 ✓** (799 base + 5 nouveaux) |
| `tsc --noEmit` | **9 erreurs, avant = après** (préexistantes : `manhadjia-*.test.ts`, un cast `api-client.ts`) — **0 introduite** |
| `eslint` (fichiers touchés) | propre (1 warning préexistant `setRequestingHint`, non lié) |
| `scripts/probe_audit_surfaces_site.py` | **54 OK · 0 échec** |
| sélection exacte du nouveau gate CI | **278 ✓ en 1 s** (0 DB, 0 Redis) + `validate_rubrics.py` **13 ✓** |

**Rejouer la sonde** (aucun service requis) :

```bash
cd khawarizmi-backend
pip install -r requirements.txt        # ou a minima : fastapi slowapi limits pydantic-settings httpx jose fsrs numpy onnxruntime
python scripts/probe_audit_surfaces_site.py
```

---

## 6. Diffusion du correctif (S38 + S39)

| Fichier | Changement |
|---|---|
| `khawarizmi-backend/rate_limit.py` | `verify_sub: False` + sub obligatoire (**F14**) ; `enforce_evaluate_quota` **retourne** `JSONResponse(429)` au lieu de lever ; fail-open `enabled=False` ; `Limiter(swallow_errors, in_memory_fallback_enabled)` |
| `khawarizmi-backend/routes/errors.py` | `rate_limit_exceeded_handler` None-safe, corps conforme au contrat `erreur`, `Retry-After` (**F12**) |
| `khawarizmi-backend/main.py` | handler branché sur la **classe** `RateLimitExceeded`, plus sur le statut 429 |
| `khawarizmi-backend/routes/grade.py`, `routes/methodology.py` | `over_quota = enforce_evaluate_quota(request)` → `return` |
| `khawarizmi-backend/schemas/bac_blanc.py`, `routes/bac_blanc.py` | pont `grade_question_id` en premier candidat de `resolve_question_id` (**F15**) |
| `khawarizmi-frontend/src/lib/api-client.ts` | 429 → `ungraded + quota + banner_ar + retry_after_s`, plus de throw (**F12**) |
| `khawarizmi-frontend/src/components/methodology/ScenarioRunner.tsx` | `Promise.all` → `Promise.allSettled` : une question en échec ne jette pas le scénario |
| `khawarizmi-frontend/src/app/annales/[slug]/exam/correction/page.tsx` | ligne d'exercice : `—` au lieu de `0 %` sur un non-noté (**F16**) |
| tests | `tests/test_grade_s38.py` (12), `tests/test_grade_s39.py` (8), `src/lib/api-client.grade-quota.test.ts` (5), sonde 54 assertions |
| `patches/F18-ci-gate-fix.patch` | à appliquer par un humain : `pull_request` élargi à `master` (la CI ne se déclenchait **jamais**) + suite `grade` et `validate_rubrics.py` dans le gate ; `push` **non touché** (déploiement Railway) |

---

## 7. Complément (même date) — couverture, et deux recommandations **retirées**

### 7.1 Couverture mesurée, surface par surface

`methodologyScenarios` = **18 scénarios / 68 questions**, dont **13 questions portant une
`gradeQuestionId`** (19 %) — les 13 grilles git.

| Surface | Notée localement ? | Mesure |
|---|---|---|
| `/document-analysis/<l0-*>` (7 scénarios) | **oui** | 13/13 questions branchées, auto-note 100 % |
| `/document-analysis/chapters/*`, `/diagnostic/chapters/*` (66 liens → 11 scénarios `*-v1`) | **non** | 55 questions sur `NoLocalGradeWall` |
| `/annales/*` (23 sujets, 27 exercices) | **jamais** | l'appel `/api/grade` est absent ; seule `getBacCorrection` (PDF) |
| `/bac-blanc` (sujet seed, 8 exercices) | **non** | `grade_question_id` vide partout → `ungraded` (**F15**, pont prêt) |
| `/action-verbs/*` (13 verbes) | **non** | 0 grille taguée `verb:<slug>` |

Le hub `/document-analysis` ne liste que les 7 scénarios notables
(`scenarioHasLocalGrade`, `src/app/document-analysis/page.tsx:25`) : le trou est donc
**une dette de rédaction de grilles, pas un lien cassé**. Note d'exploitation : quota free
15 évaluations/h (**F17**) — si les 55 questions étaient branchées, ~3 scénarios de 5
questions/h seulement.

### 7.2 Deux recommandations de la section 5 que j'avais tort de présenter comme rapides

1. « **brancher les 13 grilles existantes sur les scénarios `*-v1` = simple câblage** » — **FAUX**.
   Aucun des 10 scénarios `*-v1` mesurables ne partage un seul nombre avec le document d'une
   grille (0 recouvrement). Exemple concret : la question `analyse` d'`enzyme-activity-v1`
   porte sur *الوثيقة 1* = **la courbe de pH** (optimum 7), alors que `enzyme-temp-analyse`
   exige 37 / 80 / 100 °م ; la copie modèle de la question y obtient **method=0 overall=0**.
   Les 13 grilles sont soudées à leur propre scénario mono-document (le `contextAr` de
   `l0EnzymeTempScenario` le dit noir sur blanc : « ليست وثيقة pH »).
2. « **remplir `grade_question_id` du bac blanc avec la grille bac 2023** » — **FAUX**.
   `scripts/bac_blanc_seed.json` ex. `s1-e2` = « تفسير الإشباع الضوئي » (saturation lumineuse) ;
   `bac2023-s1-ex2-analyse-traduction` = traduction de l'expérience ML901. Mesuré : overall
   **0 %** sur l'exercice. Dans les deux cas l'élève aurait reçu une **note fausse**, ce que le
   repo interdit plus gravement qu'une absence de note.

### 7.3 Ce qui a été fait à la place

* **Gate de branchement** `khawarizmi-backend/tests/test_grade_s40.py` (7 tests) :
  * pour toute question branchée, **la copie modèle montrée à l'élève doit obtenir 100 % sous
    sa grille** (extension au niveau surface du G5 de `validate_rubrics.py`) ;
  * aucune grille indexée sans `model_answer` (sinon elle noterait n'importe quoi) ;
  * branchement injectif (une grille = une question) ; version moteur épinglée ;
  * pont bac blanc : `grade_question_id` déclaré ⇒ `model_answer_ar` doit saturer la grille,
    et un test verrouille l'absence de raccourci sur le seed actuel ;
  * **méta-test** qui vérifie que la garde attrape précisément l'erreur du 7.2 (pH → grille
    chaleur) — vérifié par expérimentation directe : injecter le raccourci bac blanc rend le test
    rouge (`overall=0`), le retirer le rend vert. Sur l'arbre actuel : **0 câblage
    non conforme**, donc la garde atterrit verte.
* **Accélérateur d'auteur** `khawarizmi-backend/scripts/gen_rubric_skeletons.py` : produit des
  paires `rubric`/`document` **valides au schéma** pour les 55 questions, en recopiant
  uniquement ce que le scénario contient déjà, avec **un keypoint seulement s'il est à la fois
  cité par l'exemple de l'UI et présent dans le document** (c'est le contrôle qui manque quand
  on câble à la main). Sortie **hors `index.json`** → ne corrige aucune copie. `--check`
  auto-note chaque squelette : 55 se chargent, **3 s'auto-valident à 100 %** —
  `gene-expression-protein-disorder-v1-analyse`, `nervous-communication-v1-analyse`,
  `photosynthesis-v1-analyse` → les trois seules questions où l'on peut espérer un branchement
  court, les 52 autres exigent de relire le sujet. Exemple déposé pour 5 questions de
  `enzyme-activity-v1` sous `data/rubrics/drafts/` (+ `README.md` expliquant la publication en
  5 étapes).

### 7.4 Finding mineur découvert par la garde (F19)

`l0-greffe-ltc` questions `justify` et `compare` sont **notées** (grilles
`greffe-ltc-justify` / `greffe-ltc-compare`) mais leur `modelAnswer` est vide (`""`) dans
`methodology-documents.ts:1879` s. — 11 autres questions du même scénario en affichent un.
Un élève qui reprend la formulation attendue n'a donc aucun exemple à comparer, alors que la
grille, elle, exige « rappel + لأن + نعلم أن ». Rien de cassé côté moteur ; c'est un contenu à
rédiger (et la garde ne peut rien contrôler tant que l'exemple est absent — elle le signale).

---

## 8. Deuxième complément (31/08) — `/methodology`, annales, et trois correctifs ciblés

### 8.1 « La rubrique des annales est-elle gérée par notre correcteur ? » — non, et voici où ça casse

Le chemin *existe* : `/annales/[slug]/exam` monte `BacBlancImmersif` → `POST /api/bac-blanc/{sid}/submit`
→ `grade_or_none()` → `services/local_grader` (0 LLM, `services/grade_adapter.py:26-32`).
Mais trois verrous le rendent inatteignable :

| Verrou | Mesure |
|---|---|
| `bac_subjects` n'est écrit que par `scripts/seed_bac_blanc.py` (unique `INSERT` du repo) | 1 slug seedé `bac-svt-2025` ; **intersection avec les 23 slugs d'annales = ∅** |
| `/api/bac-blanc/start` | `if not rows: raise HTTPException(404, "Sujets introuvables pour : …")` → **404 pour les 23 sujets**, avant toute saisie d'élève |
| Le seul sujet seedé | 0/8 exercices avec `grade_question_id` → tout `ungraded` (verrouillé par `tests/test_grade_s40.py`) |

Et les deux boutons `/exam` d'une page de sujet (`src/app/annales/[slug]/page.tsx:80` et `:98`,
« امتحان كامل مع مؤقت زمني ») ne sont conditionnés par rien. Correction de ma section 7 :
j'avais écrit « `/annales` n'appelle jamais `/api/grade` » — vrai au sens strict, trompeur :
le correcteur est bien branché au flux, c'est **l'absence de sujets en base** qui coupe avant
la note. `GET /{sid}/correction` ne corrige d'ailleurs rien : il rejoue `bac_answers.score`.

### 8.2 F20 — contrat d'erreur front/back rompu (toutes les 4xx)

`http_exception_handler` renvoie le contrat `{"erreur", "status", "path", "method"}`
(`routes/errors.py:23-32`, enregistré pour 400/401/403/404 dans `main.py:61`) alors que
`api-client.request()` ne lit que `error.detail` (`src/lib/api-client.ts:175,183`) →
**tout message du backend est jeté** et l'élève voit « خطأ HTTP 404 ». Les voies `grade()`
(lignes 562, 1022) lisent bien `data.erreur` : l'incohérence est localement corrigée, jamais
globalement. Réparation minimale : `error.erreur || error.detail`.

### 8.3 F21 — `next build` est rouge sur l'arbre de base (indépendant de ce travail)

`npx next build` échoue au type-check sur `src/lib/api-client.ts:1189` (TS2352, ligne du
commit de base `9ffb1ab`, blâmée telle quelle), et `next.config.ts` ne pose aucun
`typescript.ignoreBuildErrors`. Total `tsc --noEmit` : **9 erreurs**, toutes préexistantes
(1 dans `api-client.ts`, 8 dans `manhadjia-lib.test.ts` / `manhadjia-remediation.test.ts`).
Conséquence à trancher par le mainteneur : soit le déploiement ignore les erreurs TS, soit le
build servi est périmé. Je n'ai pas corrigé : le point 1 est hors du périmètre autorisé et les
8 autres touchent la stratégie de type-check des tests — décision de repo, pas de session.
Mes fichiers : 0 erreur ajoutée (9 avant / 9 après).

### 8.4 F22 — le portail `/methodology` ne permettait pas le geste qu'il enseigne (corrigé)

Le laboratoire de méthodologie, hors session, était **décoratif** : `toggleStep` défini mais
jamais appelé (aucun `onClick`, aucun `<input>`), `localChecked` en `useState` pur (un F5
effaçait tout), et `doneCount` exigeait une auto-évaluation impossible à obtenir dans ce mode
→ compteur bloqué à `0/5`, ruban à 0 %, et le bloc « المنهجية جاهزة — يمكنك الكتابة الآن »
inatteignable. Trois correctifs, tous gardés par tests :

1. `src/lib/method/checklistUiStore.ts` (nouveau) — cochages persistés par bucket
   `mode[:checklistId]`, SSR-safe (repli mémoire comme `evidenceService`), + helpers purs
   `isStepDone` / `countDoneSteps` ;
2. `MethodChecklistLab.tsx` — bouton de cochage `aria-pressed` **uniquement** en mode hors
   session (le mode session garde la preuve écrite + l'auto-vérification comme seules voies),
   compteur branché sur les helpers, `reset()` purge le bucket ;
3. `practiceOutcome.applyMethodRunOutcome()` — une **preuve « méthode »** n'est enregistrée que
   si le verdict objectif du run est `passed` et que le score (étapes à preuve solide / total)
   atteint le **seuil ≥ 70 % déjà exigé partout ailleurs** (`src/app/progress/page.tsx:354` :
   « لا إثبات بعد — أنهِ محاولة ≥ 70٪ »). Idempotent, et **sans ouverture de porte FSRS** : le
   rappel espacé se mérite sur une copie notée par le moteur, pas sur un exercice de structure.

Ce que je me suis refusé : créer une `evidence` à la fin d'un run de Lab par simple
auto-déclaration (« هل يتوافق جوابك مع النموذج ؟ »). Le compteur `BAC` était mort, l'inflater
de preuve fabriquée l'aurait rendu faux — et une `score: 0` serait apparue en « 0 % » dans
« إثباتات حديثة ». La philosophie du site (l'élève d'abord *fait* la méthodologie) commande le
geste réel (point 1-2), pas la note décorative.

### 8.5 F23 — la tuile « FSRS » est une jauge monotone (documentée, non corrigée)

`ContractPulse` affiche `openRecallCount = recallGates.filter(g => g.allowed)`
(`src/lib/lesson/evidenceService.ts:306`) ; `allowed` est posé `true` à l'ouverture
(l.237) et **aucun chemin ne le repasse à `false`** (grep `allowed: false` dans `src/lib/lesson`
→ 0). Le chiffre étiqueté « FSRS » ne peut donc que monter : il compte des portes ouvertes, pas
des révisions dues. Décision de produit nécessaire (le refermer à la révision faite, ou le
renommer) — hors du périmètre que j'ai reçu.

### 8.6 Suites après ces changements

`npx vitest run` : **828 tests passés** (18 fichiers ; +24 nouveaux dont les gardes de câblage,
qui sont **8/9 rouges sur le code pré-correctif** — vérifié par `git stash`).
`npx eslint` sur les 7 fichiers : 0 erreur, 3 warnings préexistants (`proofs`, `canEdit`
inutilisés avant comme après ; `toggleStep` n'est plus mort). `tsc` : 9 = 9.
`next dev` : `/methodology` et `/methodology/exercices/analyse-gene-expression` en HTTP 200,
aucun marqueur d'erreur runtime dans le HTML rendu.

---

## 9. Pass « corrige les bugs » — ce qui a été touché, et ce qui est resté ouvert (2026-08-31)

**Règle de périmètre appliquée** : seuls les bugs démontrés dans ce rapport sont corrigés ; la
correction suit la mesure du §8.6 (**0 % de rubriques réellement servies par un moteur** → aucun
câblage de nouvelle question n'a été ajouté, sous peine de murs « تعذر التصحيح »).

| # | Bug | Correction | Preuve |
|---|---|---|---|
| F20 | `api-client` lisait `data.detail` ; le contrat backend est `{"erreur",…}` → **tout** message 4× serveur était jeté (« خطأ HTTP 404 ») | `httpErrorMessage(payload, status, fallback)` lit `erreur` puis `detail` ; `apiError()` attache `status` ; utilisé sur la branche 429, la branche `!ok` et `evaluateVerbAnswer` | 11 tests nouveaux ; **10/10 rouges** sur le code d'avant (contrôle par stash) |
| F21 | `next build` **rouge au commit de base** (`api-client.ts:1189` TS2352 + 8 erreurs dans deux fichiers de test) | normalisation validée à la place du cast « make-auditable » ; corrections de typage dans `manhadjia-lib.test.ts` / `manhadjia-remediation.test.ts` (sans relâcher le typage par des `any`) | `✓ Compiled successfully in 15.4s`, 65 pages statiques, `tsc --noEmit` = **0** (après 9) |
| F22 | cases de `MethodChecklistLab` décoratives, ruban bloqué à 0 % | bouton accessible + `checklistUiStore` + règle de cohérence selon le mode | §8.2 (commit `dc05e19`) |
| P3 | tuile BAC de `/methodology` s'ouvrait sur une auto-déclaration | `applyMethodRunOutcome` : la clé = preuve écrite **jugée ≥ seuil (70 %)** dans le moteur de verdict ; 0 sinon ; idempotent ; aucun effet sur erreurs/rappels | 19 tests (+24 au total sur le store/verdict/câblage) |
| F23 | tuile « FSRS » = compteurs de portes ouvertes (`allowed` jamais remis à `false`) → jauge monotone | **étiquetée honnêtement** (« بوابات FSRS — أبواب مفتوحة بعد إثبات، ليست مراجعات معلّقة »). Un vrai compteur de révisions dues demanderait un champ `dueRecallCount` **inexistant** : refusé de l'inventer | texte seul |
| §8.5 | `/annales/[slug]` promettait « ابدأ هذا الموضوع » + « امتحان كامل مع مؤقت زمني » alors qu'aucun sujet annale n'est chargé et qu'aucune grille ne correspond ; `/bac-blanc` promettait « مؤقت حقيقية » | textes alignés sur l'état réel (« حالة هذا الموضوع في الموقع », « قاعة الاختبار بمؤقّت غير مفتوحة بعد — لا موضوع مُدخَل في القاعدة ولا شبكة تقييم محلية مطابِقة ») ; la carte « قراءة » n'affiche « ملف PDF متاح » qu'après `isAnnalePdfAvailable(url_pdf)` (avant : « غير متاح » affiché **à tort** pour les vrais liens) | HTTP 200 + aucune marque d'erreur sur `/annales/el_mojtahid_3as`, `/annales/bac-svt-2025`, `/bac-blanc`, `/methodology` |

**Deux décisions refusées, à connaître si on reprend le dossier :**

1. **Câbler le bouton « ابدأ » de `/bac-blanc`** → non. `enterExam` n'est appelé nulle part
   (`grep -rn enterExam src` : 1 résultat, sa définition) : le hall, `startBac`, `chooseBacSubject`,
   `saveBacAnswer`, `submitBac` sont morts. Rendre le bouton actif produirait une salle sans grille
   de correction — exactement ce que l'intro du site interdit (« لن نفتح قاعة وهمية »).
2. **Inventer une métrique `dueRecallCount`** pour rendre la tuile FSRS utile → non, c'est un champ
   qui n'existe nulle part dans `RecallSnapshot`.

**Reste ouvert (non corrigé, par conception ou par manque de données) :**

- **Zéro rubrique réellement servie par un moteur** : 13 câblages existent mais la page verbe (la
  plus exposée) appelle `/api/verbs/{slug}/evaluate`, endpoint sans réseau de grilles. C'est du
  contenu-auteur, pas du code.
- Les 4 défauts methodology §7.7 (dont `BAC_PROOF_SYSTEM_NOT_LIVE`) — le n°3 est traité en P3.
- `npm run lint` est **mort** (`next lint` supprimé en Next 16) et masque donc ces erreurs ; eslint
  sur `src` trouve 2 `no-html-link-for-pages` **préexistants** (`BacBlancImmersif.tsx:168`,
  `VerbLessonFlow.tsx:535`) → hors périmètre, non touchés.
- `seed_bac_blanc.py` n'est lancé ni par `startup.sh` ni par le `Dockerfile` (§8.5).

**Honnêteté sur ma propre méthode** : une première passe de patch sur `api-client.ts` a avalé la
signature de `evaluateVerbAnswer` (273 erreurs de typage). Repère utile : c'est `tsc` qui l'a crié,
pas l'œil — d'où la règle appliquée ici, *patch → tsc → tests → build*, dans cet ordre.

### 9.1 Précision mesurée après coup — la salle existe, elle est juste **condamnée à l'accueil**

En rédigeant les gardes de texte (`src/lib/truthful-promises.test.ts`), une de mes affirmations a
été prise en défaut par la machine : j'avais écrit « la salle n'est pas branchée ». En réalité :

- `src/app/annales/[slug]/exam/page.tsx` **existe** et monte `BacBlancImmersif annaleSlug={slug}` ;
  `src/app/bac-blanc/page.tsx` le monte aussi dès qu'un sujet est sélectionné ;
- `src/app/annales/[slug]/exam/correction/page.tsx` existe également (le lien de débrief n'est pas
  un 404) ;
- **mais** l'écran `phase === "intro"` du composant (lignes 153-174) ne rend **aucun bouton** :
  seule `enterExam()` fait passer de `intro` à `choix`, et `grep -rn enterExam src` ne renvoie que
  sa définition. Le flux `choix → épreuve (minuterie 2 h, autosave 30 s, rendu auto à 0) →
  soumission → débrief` est donc **implémenté et inatteignable** — d'où l'avertissement eslint
  préexistant `'enterExam' is defined but never used`, qui est la trace du bug, pas un détail.

Conséquence sur le correctif : les textes posés sur `/annales/[slug]` et `/bac-blanc` restent vrais
(« قاعة الامتحان غير مفتوحة بعد لهذا الموضوع »), et l'écran d'accueil affichait `SVT · 2026` + un
format (2 h / 2 sujets / 4 exercices) **comme s'ils décrivaient le fichier demandé** — pour
`/annales/el_mojtahid_3as/exam` c'est faux. Corrigé : le slug demandé est affiché, et le bloc est
réétiqueté « نموذج عام للشكل — لا أوصف هذا الملف تحديدا » (les chiffres restent, leur statut
change). Le disclaimer du composant (« لا شبكة تقييم محلية … لن نفتح قاعة وهمية ») est conservé.

**Ce que je ne fais toujours pas, et pourquoi** : brancher le bouton d'entrée. Ouvrir la salle sans
grille = une épreuve de 2 h dont la correction renvoie « تعذر التصحيح » pour les 8 exercices ;
c'est précisément ce que le texte de l'intro s'interdit. Le travail qui débloque la salle est
§8.5 : importer les 23 sujets en base (`bac:<annee>:<exercice>`), puis authored les grilles.

Petit effet de bord supprimé au passage : l'ancre `<a href="/document-analysis">` (rechargement
complet de page) est passée en `<Link>` — `eslint src/components/bac_blanc/BacBlancImmersif.tsx`
passe de 1 erreur à 0 ; le `warning enterExam unused` est **laissé volontairement** (il documente
la porte manquante ; le renommer `_enterExam` ferait disparaître la trace).

**Gardes ajoutées** : `src/lib/truthful-promises.test.ts` (7 tests, niveau source, style du repo) —
interdisent de ré-infler les promesses annales/bac-blanc, imposent `isAnnalePdfAvailable` sur la
carte « قراءة », et verrouillent l'étiquetage honnête de la tuile بوابات FSRS et de l'intro de salle.

**Batterie finale de ce pass** : vitest **20 fichiers / 846 tests ✓** (839 → +7 gardes, dont 10 du
contrat d'erreur, rouges 10/10 avant le correctif) · `tsc --noEmit` **0** (après 9) ·
`next build` **✓ Compiled successfully** (rouge au commit de base) · HTTP 200 sans marqueur
d'erreur sur `/annales/{slug}`, `/annales/{slug}/exam`, `/bac-blanc`, `/methodology`.

---

## 10. La chaîne de validation est débranchée — et deux de mes affirmations étaient fausses (2026-08-31)

### 10.1 Le garde-fou ne peut pas se déclencher (bug d'infrastructure, le plus rentable du dossier)

```
ci.yml (master, 9ffb1ab) :  on: push: branches [main, fabuleux/*] ; pull_request: branches [main]
git ls-remote --heads origin :  arena/01a03f4f…  arena/01a05476…  master        ← « main » n'existe pas
gh run list --branch master  :  dernière exécution 7 jours, toutes en « 0s · failure »
gh run list --branch arena/01a05476-project-sinamind  :  (vide — 5 commits, 0 exécution)
```

Conséquences mesurées, pas supposées :

1. **aucun push sur `master`, aucune PR vers `master` ne lance les tests ni le build** — c'est
   exactement la fenêtre par laquelle F21 est passé : `next build` rouge depuis le merge de PR #17
   (2026-08-30) sur `master`, sans qu'aucune checking ne le signale ;
2. `deploy-railway` est conditionné à `github.ref == 'refs/heads/main'` → **GitHub Actions n'a
   jamais déployé le backend**. Le frontend, lui, est bâti par Netlify (`khawarizmi-frontend/netlify.toml`,
   `command = "npm run build"`) : si Netlify déploie `master`, sa construction **échoue** depuis le
   2026-08-30 et le site servi est figé à la dernière image valide. À vérifier dans le tableau de
   bord Netlify — c'est la seule affirmation de ce rapport que le sandbox ne peut pas trancher ;
3. l'étape Lint portait `continue-on-error: true` : même déclenchée, elle n'aurait rien bloqué.

**Correctif proposé (commit séparé, à valider par toi)** : triggers sur `master` + PR vers `master`,
étape `Typecheck` (`npm run typecheck`), Lint **sans** `continue-on-error` (il passe : 0 erreur),
`npm run pdfs:check`. **`deploy-railway` reste inerte volontairement** — activer un déploiement de
production n'est pas un effet de bord tolérable d'un fix de CI ; c'est une décision à poser à part
(secrets, stratégie de rollback).

### 10.2 « PDF disponible » n'a jamais été vérifié : 25 des 36 fichiers sont absents, 11 sont des pointeurs LFS

`khawarizmi-frontend/public/pdfs/` contient **12 fichiers de 131-132 octets** dont le préambule est
`version https://git-lfs.github.com/spec/v1` : ce sont des **pointeurs Git LFS non restaurés**, pas
des sujets. Le catalogue `src/lib/annales-bac.ts` déclare 30 sujets et **36 URL PDF distinctes :
11 existent (en pointeur), 25 sont totalement absentes** — y compris `bac-svt-sujet-2022.pdf` et
tout ce qui précède 2023.

Le codefront rendait un verdict honnête **par accident** : `isAnnalePdfAvailable()` renvoyait `false`
en dur. Correctif : `scripts/pdf-availability.mjs` régénère `src/lib/pdf-availability.ts`
(URL utilisables / pointeurs LFS / trop petits) à partir du disque ; la fonction devient un prédicat
sur cet inventaire ; la raison technique (`pointeur-lfs`, `fichier-absent`, `aucune-url`) est exposée
en `title` sur les deux surfaces qui affichent « الملف ناقص » — l'élève garde un libellé simple, le
développeur sait quoi réparer. Garde de fraîcheur `npm run pdfs:check` + 7 tests dont un qui **relève
un manifeste volontairement menteur (5/7 rouges)**.

Réparation réelle (hors code) : `git lfs install && git lfs pull`, récupérer les 25 fichiers manquants,
puis `npm run pdfs:gen`.

### 10.3 Rétractations — mes deux affirmations fausses de la session

| Affirmation | Verdict | Ce que la mesure dit |
|---|---|---|
| « `npm run lint` est mort (`next lint` supprimé en Next 16) et masque donc ces erreurs » | **FAUX** | le script est `"lint": "eslint"`, il tourne et sort **1** ; ce qui masque, c'est `continue-on-error: true` sur l'étape CI. J'ai failli écrire « sort 0 » à cause d'un `$?` lu après un pipe (`tail`) — le code de sortie du pipeline, pas celui d'eslint. Corrigé dans la méthode : `npx eslint src; echo $?`. |
| §9 : « la carte قراءة n'affiche « ملف PDF متاح » qu'après `isAnnalePdfAvailable(url_pdf)` (avant : « غير متاح » affiché **à tort** pour les vrais liens) » | **SANS EFFET** | la fonction était constante → le rendu ne changeait pas d'un cheveu, et « les vrais liens » n'existaient pas (11 pointeurs LFS + 25 absents). Le correctif utile est §10.2. |

### 10.4 Warnings eslint laissés exprès (dette de produit, pas de style)

`eslint src` = **0 erreur, 12 warnings**. Neuf sont des identifiants déclarés et jamais utilisés
(`enterExam`, `markReviewed`, `reviewBlocked`, `exercises`, `canEdit`, `setRequestingHint`,
`ArrowLeft`, `onRetry`, `proofs`) — dont **6 à occurrence unique** dans leur fichier : la trace
matérielle de fonctionnalités écrites et non branchées. Les renommer en `_x` ou les supprimer ferait
disparaître l'indicateur ; la dette est ici, pas dans le lint.

### 10.5 Le correctif de CI est livré en patch, pas en commit

GitHub refuse qu'une GitHub App crée ou modifie `.github/workflows/*` sans la permission
`workflows` :

```
 ! [remote rejected] arena/01a05476-project-sinamind (refusing to allow a GitHub App to create
   or update workflow `.github/workflows/ci.yml` without `workflows` permission)
```

Le correctif tient donc dans **`patches/F24-ci-triggers-master.patch`** (50 lignes, vérifié
applicable : `git apply --check` passe sur l'état courant de cette branche). Deux façons de l'activer :

1. `git apply patches/F24-ci-triggers-master.patch && git commit -am "ci: valider master" && git push`
   — depuis un compte qui a la main sur les workflows ;
2. accorder *Workflows : write* à l'application — préférable à terme, parce que la CI doit aussi
   pouvoir écrire ses badges de statut et ses règles de branchement.

**Rappel important** : le patch ne touche pas la condition `deploy-railway: if: github.ref ==
'refs/heads/main'`. Appliquer ce patch **n'active aucun déploiement de production** ; il ajoute
seulement `Typecheck`, `Lint` (sans `continue-on-error`) et `pdfs:check` au job `frontend-tests`.
Si tu veux que CI déploie le backend, c'est une décision séparée : secrets `RAILWAY_TOKEN`, stratégie
de rollback, et surtout un `next build` vert — ce qui, pour le coup, l'est de nouveau.

---

## 11. Panne de production mesurée : le site en ligne n'atteint **aucune** API (2026-08-31)

Trouvé en cherchant à vérifier moi-même ce que je t'avais demandé de regarder dans Netlify.
Le frontend servi est **`https://khawarizmi-ia-two.vercel.app`** (PR #10 « Deploy Vercel — code actuel »),
et non Netlify — `netlify.toml` est là, mais c'est Vercel qui répond.

### 11.1 Trois sondes, trois réponses qui se recoupent

| Sonde | Réponse | Lecture |
|---|---|---|
| `GET https://khawarizmi-ia-two.vercel.app/health` | page Railway « **The train has not arrived at the station** » (404, `Request ID: …`) | le rewrite `/health` du frontend (destination = `NEXT_PUBLIC_API_URL`) pointe vers un **domaine Railway non provisionné** — `khawarizmi-production.up.railway.app`, le seul que le dépôt documente (`docs/deploiement-vercel.md:15,35`) |
| `GET https://khawarizmi-ia-two.vercel.app/api/lessons/inexistant` | **même** page Railway | donc **toutes** les routes `/api/*` sont mortes : connexion, correction, quota, rappels. L'application publique ne peut rien appeler |
| `GET https://khawarizmi-backend.railway.app/health` → `OK` · `GET …/api/bac-blanc/zz/correction` → `{"message":"Not Found","requestId":"…"}` | un **autre** service | ce domaine — celui que la CSP Whitelistait — ne court pas ce dépôt : ici `/health` renvoie un objet de diagnostic (`routes/health.py:28`) et un 404 a la forme `{"erreur","status","path","method"}` (`routes/errors.py`) ; la clé `requestId` **n'existe dans aucun `.py`** du repo |

Cumul : le site servi aujourd'hui ne peut ni authentifier un élève ni corriger une copie. **Tant que
ce point n'est pas réparé, aucun de mes correctifs n'est visible par un utilisateur** — y compris
ceux des §8, 9 et 10. Et si Vercel construit depuis `master`, la casse n'est pas double mais triple :
F21 (build rouge, 30/08 → 31/08) bloquait aussi le déploiement du frontend.

### 11.2 Ce que le dépôt peut absorber tout de suite (fait)

1. **`next.config.ts`** : `connect-src` n'héberge plus d'hôte en dur. L'origine est dérivée de
   `apiOrigin(process.env.NEXT_PUBLIC_API_URL)`, la **variable déjà utilisée par les rewrites**.
   Sans ça, le moindre changement d'URL côté env produit un site qui reste cassé pour une autre
   raison : l'appel cross-origin est bloqué par la CSP, silencieusement, côté navigateur.
2. **`khawarizmi-frontend/lib/api-client.ts`** (273 lignes, importé par **personne**, URL en dur
   vers l'hôte fantôme) : bandeau `⚠️ DEAD + DANGEREUX` + mesure des trois faits. Il n'est pas
   supprimé — la dette de surface se signale — mais il ne peut plus être importé par ignorance.
3. **`src/lib/deploy-config.test.ts`** (5 gardes) : interdit un domaine en dur dans le bloc CSP,
   exige que CSP et rewrites lisent la même variable, et vérifie que le client mort reste (a) marqué
   mort, (b) non importé dans `src/`. Contrôle : ré-infecter la CSP avec l'ancien texte passe **2/5 au rouge**.

### 11.3 Ce qui est à toi, dans l'ordre

1. **Railway** : donner au service backend un domaine provisionné (ou réutiliser celui qui existe),
   puis vérifier sans rien toucher au code :
   `curl -i https://<domaine-railway>/health` → doit renvoyer **l'objet JSON** de `routes/health.py`,
   pas `OK` ; `curl -i https://<domaine-railway>/api/bac-blanc/zz/correction` → doit renvoyer
   `{"erreur":…}`, pas `{"message":…,"requestId":…}`.
2. **Vercel** : `NEXT_PUBLIC_API_URL` = exactement ce domaine (sans `/api`). La CSP se régénère
   depuis ce commit, donc tu n'as plus rien à y déclarer.
3. Fumer la chaîne en prod après déploiement : `/auth/login` doit passer, et `/api/lessons/x` doit
   répondre le 404 de **l'app** (plus la page Railway).
4. Option structurelle que je recommande mais n'ai pas imposée : vider `API_BASE_URL` en production
   (le client n'utiliserait que le proxy same-origin `/api`) — une origine, zéro CORS, zéro CSP à
   maintenir. Ce n'est pas un détail cosmétique : c'est ce qui rend la classe de panne de §11
   impossible au lieu de la rendre vérifiable.

### 11.4 Note de méthode (pour ne pas refaire l'erreur)

Le sandbox a, en cours de tour, **supprimé `node_modules` et ré-initialisé HEAD** au commit de base
(reflog : `clone: from https://github.com/…`), laissant mes fichiers en *untracked*. Symptôme :
`next build` échouait sur « Could not find the Next.js package ». Récupération appliquée :
sauvegarde des deux fichiers en cours d'édition → `git fetch origin <branche>` →
`git reset --hard FETCH_HEAD` → re-déposition → `npm ci` (17 s, cache npm) → batterie complète
rejouée. Deux règles en sortir : (a) **toujours vérifier `git log --oneline -1` avant de conclure**
qu'un commit est perdu ou gagné ; (b) un build qui échoue sur un *paquet manquant* n'est pas un échec
de code — distinguer les deux avant d'accuser le patch.
