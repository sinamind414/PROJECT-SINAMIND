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

---

## 12. F25 — le client Avalait n'importe quel 200 comme du JSON (corrigé), et trois faux positifs écartés

### 12.1 Ce que je cherchais, et ce que la mesure a refusé

À la suite de F20, j'ai traqué les autres lectures d'erreur `detail`-only. Quatre sites restaient :
`submitDrillAnswer` (l.609), `streamChatbotMessage` (l.790), `correctExercise` (l.1552) — et `grade`,
déjà conforme. Vérification des consommateurs dans `src/` : **zéro appel** pour les trois premiers
(grep des trois identifiants hors `api-client.ts` : rien). Les corriger n'aurait changé **aucune**
écran pour un élève : ce sont des méthodes mortes du client, documentées comme dette de surface et
laissées telles quelles — pas de patch de vitrine.

Contrôle utile sur le patch §10 : les 8 fichiers `pytest` cités par le job `backend-tests` **existent
tous** (`test_methodology*` ×3, `test_diagnostic`, `test_couche3`, `test_tutor`,
`test_bac_blanc_intelligent`, `test_mindmap_methodology`) — donc `patches/F24-ci-triggers-master.patch`
ne peut pas rougir la CI pour une cause triviale du type fichier manquant.

### 12.2 Le défaut vivant : `return response.json()` nu sur le chemin le plus emprunté

`request()` est appelé par **32 sites** du front. Son chemin de succès ne protégeait pas le parsing :
un `200` dont le corps n'est pas du JSON — page HTML d'une porte d'entrée, maintenance d'un proxy,
domaine mal routé — remontait `SyntaxError: Unexpected token 'O', "OK" is not valid JSON`, que les pages
affichent telles quelles (`setError(e.message)`), en pleine interface arabe RTL.

Et ce n'est pas un scénario d'école : **mesuré** dans cette session, l'hôte que la CSP Whitelistait
répond `200` avec le corps texte `OK` sur `/health` (rapport §11.1). Le front possède exactement l'appel
correspondant — `getHealth()` → `this.request<HealthCheck>("/health")` (`src/lib/api-client.ts:1611`,
non consommé aujourd'hui, mais c'est la forme du bug).

Correctif : `readJsonBody()` — corps vide (204/205) → `undefined` sans exception ; corps non parseable →
`apiError({}, status, UI_AR.reponse_illisible)` avec le texte élève :
`تعذر قراءة استجابة الخادم — ليست مشكلة في إجابتك. أعد المحاولة بعد قليل.`
La phrase dit explicitement à l'élève que **ce n'est pas sa réponse** qui est en cause — dans un site
dont la promesse est de corriger des copies, un « SyntaxError » technique se lit comme un échec scolaire.

Gardes : 4 tests dans `src/lib/api-client.error-contract.test.ts` (200 texte, 204 vide, 200 JSON, 404 HTML) ;
sans le correctif, **3 d'entre eux sont rouges**. Le 404 HTML ne régresse pas : les branches d'erreur
étaient déjà protégées par `.catch(() => ({}))`.

### 12.3 Batterie de cette passe

`vitest` **22 fichiers / 862 tests ✓** · `tsc --noEmit` **0** · `eslint src` **0 erreur** (12 warnings
gardés, §10.4) · `npm run pdfs:check` à jour · `next build` **✓ Compiled successfully** · HTTP 200 sans
marqueur d'erreur sur `/methodology`, `/annales/bac-svt-se-2026/read`, `/bac-blanc`.

---

## 13. F26 — la chaîne technique brute arrivait à l'écran de l'élève (8 pages corrigées)

`setError(e.message)` / `setError(String(e))` était le motif partout : depuis F20, le client
remonte enfin le message arabe du serveur, donc *quand il y en a un*. Dans les autres cas — panne
réseau, page HTML d'une porte d'entrée, `SyntaxError` de corps non JSON, vieux repli français —
l'élève arabe RTL lisait `Failed to fetch`, `Unexpected token 'O'…` ou `Erreur de chargement`.
Sur un site dont la promesse est « ta copie est corrigée », ce texte se lit comme un verdict sur
**sa** réponse. Le contre-sens est exactement le type de bug que le reste de ce rapport mesure.

Correctif : `src/lib/ui-error.ts` → `readableError(error, fallback)`, avec un ordre de priorité assumé :

1. **le message du serveur s'il est déjà en arabe** (lui seul sait quoi réparer), amputé du préfixe
   `Error:` et plafonné à 240 caractères ;
2. **le statut HTTP s'il est connu** : 401 fin de session, 403 compte, 404 contenu indisponible,
   429 limite (réutilise `UI_AR.limite_atteinte`), 5xx panne serveur — avec la mention
   « المشكلة ليست في إجابتك » ;
3. **les pannes locales reconnaissables** : réseau, délai dépassé, requête interrompue, corps illisible ;
4. **repli arabe de l'appelant**, sinon `UI_AR.erreur_chargement` — et jamais le texte brut, jamais
   du HTML, jamais une URL, jamais une chaîne française sur un écran arabe.

Branché sur : `auth/login`, `auth/register`, `drill/[unit_id]`, `annales/[slug]/exam/correction`,
`programme/ProgrammeView`, `admin/analytics` (la page est `dir="rtl"`, son repli français était donc
une fuite), `mindmap/chapter` (ses 4 cas sémantiques conservés, le repli délègue au helper),
`BacBlancImmersif` (×3, sur les chemins morts — cohérence). Dans `api-client`, le tuteur SSE garde
`message_fr` comme **trace technique** (journaux) et `message_ar` comme écran élève ; les trois autres
sites `detail`-only (`submitDrillAnswer`, `correctExercise`, `grade`) passent par `apiError`.

Garde : `src/lib/ui-error.test.ts` — 19 tests (table de correspondance + un scan source qui nomme
n'importe quelle page revenant à `setError(String(…))` ou `e.message`). Vérifié mordant : réinjecter
`setError(String(err))` dans `auth/login` passe la garde au rouge avec le fichier en cause.

## 14. F27 — le SQL d'écriture de la mémoire était PostgreSQL-only : la répétition n'enregistrait rien sur SQLite

Le plus rentable de cette passe, et il dormait derrière **22 tests rouges depuis des semaines**.

`services/fsrs_unified.py` écrivait les états FSRS avec `NOW()` (28 occurrences). SQLite ne connaît
pas `NOW()` — et ce dépôt **supporte SQLite** : `_sqlite_compat()`, `ensure_dialect_for_url()` et un
test dédié (`tests/test_dialect_guard.py`), sans parler des docstrings « preview SQLite » du module.
Sur SQLite, chaque `INSERT` levait, l'exception était avalée par un `except Exception: … return False`
qui **ne logguait même pas** (contrairement aux chemins de lecture, eux, loggés), et la progression
de l'élève ne s'enregistrait pas. Les 22 tests, eux, disaient vrai : le fixture créait bien les
tables, l'`assert await update_memory(...)` attendait `True`. **Le test n'était pas périmé, le code
oui.** Correction : `NOW()` → `CURRENT_TIMESTAMP` (SQL standard, strictement équivalent en
PostgreSQL — `timestamp with time zone`).

`tests/test_evaluate.py` : deux tests enveloppaient l'appel dans
`patch("services.ai_modes.evaluation_mode.get_question")`, symbole qui n'existe pas dans ce module
(`get_question` vit dans `services/questions.py`) — vestige du retrait de la route `/api/ai/evaluate`
(GEL 2026-08-17). L'`AttributeError` du patch partait **avant** toute assertion : rouge pour rien.
Patch retiré, assertions conservées et renforcées (le 404 doit être du JSON), docstring qui dit la
portée réelle du test maintenant qu'il ne teste plus la recherche de question.

**Ce que je n'ai PAS fait, et pourquoi** : `NOW()` subsiste dans 13 autres fichiers (`interleaving`,
`phase3/5/6`, `payment`, `mindmap_service`, `auth`, `bac_blanc`, `lessons`, `lifespan`, `social`,
`remediation`, `kunz_tunnel`), souvent dans de l'arithmétique de dates (`EXTRACT(EPOCH FROM …)`,
`NOW() - INTERVAL '7 days'`, casts `::text`) qui ne se traduit pas au mot à mot. Convertir à l'aveugle
casserait la production — et il n'y a pas de PostgreSQL dans ce sandbox pour vérifier. À la place,
`tests/test_sql_portability.py` : un module non exempté qui introduit `NOW()`/`ILIKE`/`::jsonb`/
`date_trunc` dans une chaîne passe la suite au rouge en nommant le fichier ; `fsrs_unified` est
verrouillé sans marque PG-only ; et une exemption périmée est elle-même une erreur. La dette est
**inventoriée avec la raison par fichier**, pas niée. 3 tests, vérifiés mordants avec une sonde
temporaire.

Effet de bord trouvé au passage : `cost_log.jsonl` est **suivi par git à la racine** et `pytest` y
append → lancer la suite salit l'arbre de travail (mesuré : +2 lignes). Corrigé dans
`tests/conftest.py` (`COST_LOG_PATH` dévié vers le dossier temporaire, `setdefault` → l'override
reste possible). Le vrai débat — une journal de coûts illimité versionné dans le dépôt — reste ouvert,
§14.1.

**Batterie backend après correctif** : `pytest tests` → **1378 passed, 10 skipped, 5 xfailed, 0 failed**
(après 1344 ✓ / 24 ✗). Bruit résiduel non bloquant : un `ValueError: I/O operation on closed file` du
`BatchSpanProcessor` OpenTelemetry au shutdown des tests — traceur exporter sur stdout fermé par
pytest ; cosmétique, exit code 0.

### 14.1 Dettes ouvertes par un choix, pas par oubli

- `cost_log.jsonl` à la racine, suivi, à croissance non bornée : à sortir du versionnement (ou
  basculer dans `data/` ignoré + rotation). Décision de dépôt, pas un patch de plus.
- Les 13 fichiers `NOW()` exemptés : à convertir **avec** une base PostgreSQL en CI — donc après
  l'application de `patches/F24-ci-triggers-master.patch`, qui fournit cette base (`services: postgres:16`).
- Le `except Exception: return False` silencieux des écritures FSRS : désormais sans effet sur SQLite,
  mais il avale encore n'importe quelle erreur côté Postgres (migration ratée = plus de répétition,
  aucun signal). Le rendre bavard (un `logger.warning` comme les lectures) est une ligne ; je ne l'ai
  pas faite sans test de prod, parce qu'un log d'erreur sur ce chemin peut devenir du bruit en continu.

---

## 15. La rubrique Manhadjia passée au crible : quatre soupçons réfutés, un panneau mort réanimé (F28)

Directive : « continue de régler les bugs du site, **surtout la rubrique manhadjia** ». J'ai donc traité
`/manhadjia/*` comme une surface à mesurer, pas à réputer. Verdict : **le module est structurellement
sain** — et le seul vrai défaut de la rubrique n'est pas dans la rubrique.

### 15.1 Ce qui tient (mesures, pas impressions)

| Contrôlé | Méthode | Résultat |
|---|---|---|
| 23 routes vs 22 jours du lib | extraction mécanique des `slug:`/`href:` de `manhadjia-lib.ts` vs répertoires | 22 ↔ 22, **aucune route orpheline, aucun href mort** |
| Import des 22 ateliers JSON | chemins `../../../data/ateliers/*.json` résolus sur disque | 22 présents, 0 cassé (piège : `../data/ateliers` n'existe pas) |
| Liens issus des **données** | `lien_suivant` + `lien_juge` des 22 fichiers contre la table des routes | 22/22 résolvent ; les 3 `lien_juge` visent `l0-greffe-ltc`, la seule page à **5/5 grilles câblées** |
| Contrat remédiation | `manhadjia-remediation.ts` ↔ `routes/manhadjiya.py:110` ↔ `get_contextual_remediation_data` | enveloppe `data`, clés `verb/units/relevant_errors`, erreurs en chaînes, sans auth — **conforme dans les deux sens** |
| Moteur de détection local | pavage exact du texte par `highlightSpans` sur 120 motifs réels × 9 textes (tashkīl, tatwīl, hits collés) | **1080 combinaisons, 0 rupture**, 0 index hors bornes ; les 120 regex compilent |
| Références officielles | `verb_ref` des 11 ateliers vs `methodology/verb_database.json` (arabe, français, définition, critères, erreurs) | **0 dérive sur 11** — les cartes « المرجع الرسمي » sont des copies fidèles |
| Preuves / progression | grep `evidence\|progress-store\|achievement` sur composants + pages + lib | **0 émission de preuve, 0 écriture de progression** — donc pas de faux badge, pas de jumeau de P3 ici |
| Rendu | smoke HTTP dev | `/manhadjia`, `/manhadjia/atwal`, 4 pages de verbe → 200 sans marqueur d'erreur |

### 15.2 Quatre hypothèses que j'ai émises, et que la mesure a tuées

1. **« la remédiation est morte »** : `get_contextual_remediation_data("hallil", …)` renvoyait `units: []`.
   Faux : **le slug de répertoire n'est pas la clé d'API**. Le front envoie `data.verb_slug` (le verbe
   officiel), et **22/22 ateliers résolvent au moins une unité**. Piège consigné pour ne pas y retomber.
2. **« `persistSessionSnapshot` n'est jamais appelé → la reprise de session est morte »** : artifact de mon
   propre grep (l'appel est dans le module lui-même). `reduceSession` émet bien `persistSession` /
   `clearSession`, `runSessionEffects` les exécute (le `default: never` prouve l'exhaustivité), et
   `dispatchSessionEvent` — le passage obligé des vues — persiste. **Rien à réparer** ; l'exercice
   `analyse-gene-expression` reprend bien sa session.
3. **« un regex `g` + `.test()` en boucle fausse la détection »** : chaque motif est reconstruit à chaque
   appel (donc `lastIndex` repart de 0), et la seule boucle (`re.exec`) garde la garde `length === 0` →
   `lastIndex++`. Correct.
4. **« le hub `hallil` est une route morte »** : `/manhadjia/hallil` renvoie 404 (mesuré), mais ce n'était
   pas un lien cassé — la page vit sur `/manhadjia` et **zéro lien ne cible `/manhadjia/hallil`**.

Quatre soupçons réfutés, ça veut dire une chose : je n'ai rien « corrigé » dans `src/app/manhadjia` ni dans
`data/ateliers`, parce qu'il n'y avait rien à y corriger.

### 15.3 Le seul défaut mesuré de la rubrique : une remédiation « contextuelle » aveugle au verbe

Les 22 ateliers produisent **21 verbes officiels distincts**. Branchés sur `VERB_UNIT_MAP`, ils ne donnent
que **2 jeux d'unités différents** : 18 verbes → les 5 unités du programme, 3 verbes → 1 seule unité. Le
conseil affiché en phase ب (`أخطاء شائعة — المرجع الرسمي`) est donc **quasi identique d'un atelier à l'autre** :
la contextualisation est un nom, pas un comportement.

Je ne le corrige pas, et il faut lire pourquoi : rendre la remédiation par-verbe exige de rédiger le
`VERB_UNIT_MAP` fin — c'est-à-dire **décider quels items du programme pèsent sur chaque verbe**. C'est de
la pédagogie d'examen, et ce n'est pas ma main qui doit l'écrire (mêmes raisons que §9 et que le refus de
fabriquer les grilles). Le correctif honnête est un **fichier de données à valider par toi**, pas un patch de
plus. Ajouté à cela, l'état de la prod (§11) rend le débat académique : l'appel part vers un domaine non
provisionné, donc le panneau retombe sur son repli silencieux quel que soit son contenu.

Le contrat d'échec silencieux reste, lui, **volontaire** : `RemediationHint` affiche la détection locale
dans tous les cas, et le composant est propre (debounce 1,2 s, timeout 2,5 s, garde de requête obsolète).

### 15.4 F28 — le panneau de données officielles était orphelin (et faux) : `ManhadjiyaTips`

Le gisement n'était pas dans les ateliers manhadjia mais dans sa voisine immédiade, la rubrique **المنهجية**
(`/methodology`). `src/components/methodology/ManhadjiyaTips.tsx` : 266 lignes, trois onglets (نصائح المراجعة
· الأخطاء الشائعة · مستويات بلوم), branchés sur trois endpoints qui répondent **200 avec du contenu arabe
réel** (`REVISION_TIPS_AR` = 51 conseils, `COMMON_BAC_ERRORS` = 37 erreurs, `VERB_COGNITIVE_LEVELS` = 74 verbes).
Références dans le dépôt, tous fichiers confondus, hors le fichier lui-même : **0**. Le panneau n'était
monté par aucune page. Deux bugs le rendaient de toute façon inutilisable :

- **réseau** : trois `fetch` dans un `Promise.all`, **sans contrôle de `resp.ok`**, sans timeout, sans
  annulation, `catch` → `console.error` seul. Un seul endpoint en panne (le 404 HTML de la prod §11, par
  exemple) faisait lever `.json()`, rejetait le `Promise.all` **en entier**, et laissait l'élève devant
  trois onglets à `(0)` — un « pas de donnée » qui se lit comme « rien à apprendre », avec aucun bouton
  pour réessayer. Une requête pendante figeait l'écran « جاري التحميل... » indéfiniment.
- **contrat de données** : les tables de libellés, d'icônes et de couleurs étaient indexées sur des **clés
  arabes** (`"في القسم"`, `"تذكّر"` …) alors que le backend envoie des **clés anglaises** (`in_class`,
  `remember`, `compare_and_analyse` …). Mesure : **10/10 catégories de conseils perdaient leur icône et
  affichaient la clé technique en titre**, et **5/5 niveaux de Bloom prenaient la couleur du premier** —
  l'échelle que ce panneau existe pour enseigner. (Seul l'onglet erreurs était aligné : `methodology`,
  `knowledge`, `form`.)

Correctif (commit ci-dessous) :

- nouvelle couche **`src/lib/manhadjiya-tips.ts`** : endpoints, timeout 4 s avec `AbortController`, contrôle
  de statut, `normalizeCategoryMap` (ne garde que les listes de chaînes non vides ; distingue
  « `data: {}` » = répondu-vide **de** « null » = en panne), et **dégradation par onglet** — la panne d'un
  endpoint ne vide plus les deux autres ; libelliers indexés sur les clés **réelles** du backend ;
- `ManhadjiyaTips.tsx` réécrit sur ce lib : plus de `console.error` qui avale, un bandeau
  « تعذّر تحميل … لم تُخترع بيانات بديلة » + **إعادة المحاولة** par onglet en échec, et `غير متاح` dans
  l'onglet touché au lieu d'un `(0)` mensonger. Visuel et classes inchangés par ailleurs ;
- **monté dans `/methodology`** en section `#official-tips` (« 4. المرجع الرسمي »), avant la règle d'or.
  Cinq libellés d'en-tête sont neufs (`official_recommendations`, `cognitive_levels`, `correction_criteria`
  + deux icônes) : ce sont des **traductions de clés**, pas du contenu d'examen — mais ce sont les seuls
  mots que j'ai écrits ici, donc tu peux les reprendre ;
- **`src/lib/manhadjiya-tips.test.ts` (26 tests)** dont une **garde transversale** : le test relit
  `khawarizmi-backend/prompts/correction_prompt.py`, en extrait les clés de premier niveau, et interdit
  toute clé sans libellé côté UI. Si le backend ajoute une catégorie demain, le frontend passe au rouge
  au lieu d'afficher `new_category_name` à un élève arabophone. Plus une garde anti-orphan : si on détache
  le panneau, le test le dit.

Morsure vérifiée par trois régressions contrôlées (chaque mutation a fait rougir exactement ce qu'il
fallait, 1 / 2 / 1 échecs, puis revert) : retirer un libellé de Bloom, réintroduire le rejet global du
`Promise.all`, détacher `<ManhadjiyaTips />` de la page.

**Batterie après F28** : `vitest run` → **907 passed** (881 → +26) · `tsc --noEmit` → 0 · `eslint src` →
0 erreur, 12 warnings (les mêmes, gardés à dessein) · `next build` → ✓, `/methodology` prerender ✓ ·
smoke dev : `/methodology` 200 sans marqueur d'erreur, et `GET /api/manhadjiya/{revision-tips,common-errors,
cognitive-levels}` via le proxy → 200 sur les clés attendues.

### 15.5 PDF des annales : re-mesure, et la limite du sandbox

Le mécanisme d'honnêteté existe déjà et fonctionne : `scripts/pdf-availability.mjs` génère
`src/lib/pdf-availability.ts` (`0 utilisable · 12 pointeurs LFS`, et le fichier est à jour au `--check`),
`src/lib/pdf-available.ts` sert `isAnnalePdfAvailable` + le motif de indisponibilité, et `/annales/[slug]`
comme `/annales/[slug]/read` le consomment. Mesure : **36 URL déclarées dans `annales-bac.ts`, 12 fichiers
sur disque — tous des pointeurs de 131/132 octets — et 25 absentes**. Donc le site ne ment pas sur les PDF ;
il sont simplement **absents du dépôt** (LFS non restauré + avant-2023 jamais rapatriés). Réparation
impossible ici, et ce n'est pas un choix : le sandbox n'a ni egress (`media.githubusercontent.com`,
`mena.edu.dz` → `HTTP 000`) ni `git lfs` (`git: 'lfs' is not a git command`). À faire chez toi :
`git lfs install && git lfs pull`, récupérer les 25 manquants, puis `npm run pdfs:gen`.

---

## 16. Scan de « استغلال الوثائق » (`/document-analysis`) : où sont les exercices, et ce qu'ils contiennent vraiment

Question posée telle quelle : « où est le dossier, il contient des exercices, scanne le repo ». Réponse
littérale d'abord, verdict de scan ensuite.

### 16.1 La surface n'est pas un dossier d'exercices, c'est un routage de 92 lignes

| Where | Contenu |
|---|---|
| `khawarizmi-frontend/src/app/document-analysis/` | **3 fichiers** : `page.tsx` (94 l., le hub), `[scenarioId]/page.tsx` (25 l.), `chapters/[chapterSlug]/page.tsx` (33 l.) |
| `khawarizmi-frontend/src/lib/methodology-documents.ts` | **2 207 lignes = les exercices eux-mêmes** : 18 scénarios, leurs documents (SVG inline en data-URI), leurs questions, leurs `modelAnswer`, et le champ `gradeQuestionId` qui branche la grille |
| `khawarizmi-frontend/src/lib/methodology-chapters.ts` | 749 lignes : `methodologyChapterLinks` (**55 liens de chapitre**) + `UNITS_CONFIG` |
| `khawarizmi-frontend/src/components/methodology/ScenarioRunner.tsx` | 721 lignes : le lecteur d'exercice, l'appel `apiClient.grade`, le mur `NoLocalGradeWall` |
| `khawarizmi-backend/routes/document_analysis.py` | 7 endpoints `/api/document-analysis/*` (liste, détail, `evaluate`, `{slug}/correction`, `progress`, `review`, `weak-spots`) — **tous sous `get_current_user`** |
| `khawarizmi-backend/data/rubrics/` | `index.json` : **13 grilles** = 56 critères, versions 1.0.x |

Donc : les exercices **ne sont pas dans le dossier `document-analysis`**, ils sont dans deux libs de données
statiques ; le dossier d'routes ne fait que résoudre un id puis monter `ScenarioRunner`.

### 16.2 L'inventaire mesuré

- **18 scénarios.** 7 ont `gradeQuestionId` sur **toutes** leurs questions (13 questions = 13 grilles du
  dépôt) et sont **les seuls affichés par le hub** ; 11 n'ont **aucune** grille et sont **hors hub**, atteignables
  uniquement par les 55 liens de chapitre (`/document-analysis/chapters/<slug>`, et `/diagnostic`).
- Les 11 cachés ne sont **pas vides** : 44 documents, **55 questions, 54 corrigés-types (`modelAnswer`) déjà
  rédigés** — ce qui manque, c'est la grille (critères + points), pas l'exercice. C'est la formulation exacte
  de la dette « 19 % de correcteur branché » (§8.5, §9) : 13 questions outillées sur 68.
- Zéro défaut de structure : 0 scenario injoignable (hub ∪ chapitres = 18/18) · 0 lien de chapitre cassé ·
  55 slugs uniques · bijection **stricte** questions câblées ↔ `index.json` dans les deux sens (aucune carte
  morte, aucune grille orpheline) · 0 scénario à câblage mixte (le cas qui enverrait l'alias
  `${scenario.id}:${q.id}` et récolterait un 422 déguisé en zéro) · **13/13 : le `verb_slug` de la grille est
  bien le `verbSlug` affiché** (sans ça, la progression FSRS serait consignée sous le mauvais verbe).
- `ScenarioRunner.submit()` est propre : `Promise.allSettled` (une question en échec n'annule pas les copies
  notées), `ungradedEvaluation("تعذر التصحيح")` par question en échec, XP gated par `contract.mayAwardXp`.
- Les deux appels du hub (`getDaProgress`, `getDaWeakSpots`) with `.catch(() => {})` : **pas** un bug — les
  endpoints existent et répondent 401 sans token ; la bande FSRS n'apparaît simplement pas. Vérifié en direct :
  `GET /api/document-analysis/{progress,weak-spots,scenarios}` → 401 `{"erreur":"Token invalide ou expiré"}`.

### 16.3 Ce que j'ai corrigé (F29) et ce que j'ai verrouillé

- **Libellé mensonger mesuré** : la carte `l0-proteine-adn` affichait « 📄 **0** وثائق » — le scénario est un
  *texte scientifique sans document* (`contextAr` le dit : « لا وثيقة رقمية »). Une fiche « 0 document » se lit
  comme une fiche vide. La carte affiche maintenant « **نص علمي — بلا وثيقة** » quand `documents.length === 0`.
- **`src/lib/methodology-documents.inventory.test.ts` (9 tests)** : premier verrou de cet inventaire (18/7/13/55,
  bijection avec `data/rubrics/index.json`, concordance verbe↔grille, homogénéité du câblage, accessibilité,
  garde de libellé, garde « le hub ne liste que des cartes à grille »). Morsure vérifiée : retirer une grille
  câblée → 3 échecs ; retirer le nouveau libellé → 1 échec.
- Batterie : `vitest` **916 ✓** (907 → +9) · `tsc` 0 · `eslint` 0 erreur / 12 warnings · `next build` ✓
  (les trois routes de la surface compilées).

### 16.4 Rétractation de méthode (compte à rebours de mes propres smokes)

Sur cette surface, **un HTTP 200 ne prouve rien** : `PageShell` et les pages scénario enveloppent tout dans
`AuthGuard`, qui ne rend qu'un chargeur côté serveur. Mesure : `/document-analysis`, `/methodology`,
`/progress`, `/dashboard` → 224 caractères arabes dans le HTML (le shell d'authentification) ;
`/manhadjia`, lui, n'est pas gardé → 575 caractères, contenu réel. Un slug inventé
(`/document-analysis/inexistant-x`) renvoie donc 200 aussi : `notFound()` ne se déclenche qu'après hydratation.
Conséquence : mes « routes 200 » des tours précédents ne valaient preuve que pour les pages **non gardées** ;
pour les autres, la preuve tient de `vitest` + `tsc` + `next build`, pas du curl. À faire soi-même pour un contrôle
visuel : ouvrir la page connecté, ou brancher un token dans le navigateur.

### 16.5 La décision qui t'appartient, maintenant chiffrée

Brancher les 11 scénarios cachés = rédiger 55 grilles. La matière première existe déjà dans le dépôt (54
corrigés-types) et le modèle de fichier existe (56 critères sur 13 grilles, `GRADER_VERSION 1.2.0`). Ce que je
ne peux pas faire à ta place : décider **ce qui vaut un point** dans un barème officiel algérien. Deux voies
honnêtes : soit tu me donnes les barèmes (texte officiel), soit tu valides des squelettes produits par
`scripts/gen_rubric_skeletons.py` — dans les deux cas la rédaction reste tenue par toi, et le hub restera
honnête par construction puisqu'il filtre sur `scenarioHasLocalGrade`.

---

## 17. F30 — afficher les exercices de « استغلال الوثائق » et rendre les graphes justes

Demande : afficher les exercices de la rubrique et les rendre lisibles avec le graphe et les
tableaux. En mesurant, la demande est tombée sur **deux défauts réels**, dont un qui faisait mentir
les figures.

### 17.1 Premièrement : l'exercice était caché par le mur de correction

`ScenarioRunner`, ligne de garde :

```tsx
if (!hasLocal) return <NoLocalGradeWall titleAr={scenario.title} … />
```

Le mur dit une vérité (aucune grille ⇒ personne ne corrige ici), mais il **remplaçait tout**. Bilan
mesuré : **11 scénarios sur 18 — 44 documents, 55 consignes, 17 tableaux, 7 graphes, 11 schémas de
flux, 10 images annotées — étaient invisibles**, y compris par URL directe. Un exercice qu'on ne peut
pas lire n'est pas protégé de la fausse note : il est perdu.

Réparé par `src/components/methodology/ScenarioReadingMode.tsx` : le mur devient une **bannière** et
l'exercice est rendu en lecture seule — en-tête + contexte, badges de composition (📊 2 رسم · 📋 1 جدول…),
documents, puis par question : verbe, `docRef`, consigne, **zone de brouillon locale** (avec le rappel
« لا تُرسَل، ولا تُصحَّح، ولا تُحتسب في تقدّمك »), et le `modelAnswer` + `learningFocus` dans un
`<details>` **fermé**, intitulé « افتحه بعد أن تكتب إجابتك » — la règle d'or du site (« لا تصحيح كامل
قبل محاولة التلميذ ») est tenue par la structure, pas par une promesse.

Sur le hub `/document-analysis`, une seconde section `#lecture-seule` liste ces 11 cartes avec le badge
« قراءة وتصحيح ذاتي », **sans** le badge `مصحح محلي`, et la ligne de pied dit les deux compteurs
(« 7 بطاقة بشبكة git · 11 بطاقة قراءة »). Les cartes déjà corrigibles restent filtrées sur
`scenarioHasLocalGrade` : aucune promesse d'État n'est prêtée à une page sans grille.

### 17.2 Deuxièmement : trois courbes sur sept étaient fausses

`DocumentRenderer` plaçait les points **par index** (`padding + index * stepX`). Sur les 7 graphes
structurés du dépôt, 3 ont des abscisses inégales — donc dessinées avec des mensonges :

| Document | Abscisses | Pas réels | Effet mesuré sur le rendu |
|---|---|---|---|
| `photosynthesis-v1` — كمية O₂ حسب شدة الإضاءة | 0 · 50 · 100 · 200 · 400 · 600 | 50, 50, 100, 200, 200 | **le plateau de saturation disparaissait**, la courbe paraissait linéaire |
| `enzyme-activity-v1` — تأثير درجة الحرارة | 0 · 20 · 30 · 37 · 50 · 70 | 20, 10, 7, 13, 20 | l'optimum (37) tombait à la mauvaise place |
| `enzyme-activity-v1` — تأثير pH | 2 · 4 · 6 · 7 · 8 · 10 | 2, 2, 1, 1, 2 | idem, sur un pH échelle 2→10 |

Sur un site dont la compétence enseignée est « حلّل المنحنى », un axe faux n'est pas un détail de style :
l'élève entraîne son œil sur une figure qui contredit la وثيقة. Ajouté `src/components/methodology/chart-scale.ts` :
`buildXAxis` (axe **numérique proportionnel** quand toutes les étiquettes portent un nombre croissant,
catégoriel sinon — et le motif du repli est renvoyé, pas deviné), `niceDomain` (borne 0 seulement si elle
n'écrase pas la variation : une série 88→100 ne s'écrase plus sous une baseline à zéro ; une série qui
change de signe garde son zéro), `ticksOf`/`niceNum` (graduations rondes), `formatAxisNumber` (2 décimales
max, pas de « -0 », « — » si non fini), `chartNumbersTable` (mêmes abscisses, mêmes valeurs, unité reprise
du document — aucune valeur ajoutée ni arrondie ailleurs).

Et la lisibilité demandée, côté chiffre : **un tableau « أرقام الوثيقة » sous chaque courbe**, construit sur
les `points` déjà présents. C'est ce qui manquait pour la compétence évaluée : en analyse de document,
l'élève doit **citer** les valeurs. Rendu vérifié par `react-dom/server` (pas par un 200) :
`2 → 10 %`, `4 → 40 %`, `6 → 85 %`, `7 → 100 %`, `8 → 70 %`, `10 → 15 %` pour la courbe de pH ;
`0 · 0 وحدة, 50 · 5 وحدة … 600 · 45 وحدة` pour celle de photosynthèse ; `x` des points à 42 · 80 · 118 · 194 · 346 · 498,
soit des écarts 38/38/76/152/152 — exactement les proportions des abscisses.

Un bug que j'ai **moi-même introduit puis corrigé** dans la foulée : ma première version du tableau
passait chaque cellule dans `Number(cell)` pour détecter un NaN — « 5 وحدة » devenait donc « — ».
L'assertion de rendu l'a attrapé ; la garde est supprimée (`formatAxisNumber` pose déjà le tiret).

### 17.3 Ce qui est verrouillé

`src/components/methodology/chart-scale.test.ts` — **43 tests** :
proportions d'axe (dont le ratio 4× du segment 400→600), plateau visible, replis catégorielles **nommés**
(`etiquettes-non-numeriques`, `moins-de-3-points`, `abscisses-non-croissantes`), axe partagé entre séries de
longueurs différentes, domaines d'ordonnées (ancrage 0 conditionnel, série constante, point unique, tableau
vide), graduations régulières, formatage, table à une/trois séries avec tiret si une série est plus courte,
`DocumentRenderer` branché sur `buildXAxis`/`niceDomain`/`ChartNumbersTable` et **sans** `index * stepX` ni
`computeChartBounds`, garde du mode lecture (documents rendus, corrigé dans `<details>`, **aucun**
`apiClient`/`awardXP`/`grade(`/`saveMethodologyEvaluations` dans ce composant), garde du hub (deux familles,
pas de badge « مصحح محلي » sur les cartes de lecture), et complétude de `VERB_LABELS_AR` vs l'union
`MethodologyVerbSlug` (les libellés de verbe ont été **extraits** dans `src/lib/methodology-verb-labels.ts`
pour que le mode noté et le mode lecture partagent la même table, typée par l'union).

Morsure vérifiée par mutation : forcer un espagement régulier → `expected 1.0 to be close to 4` ; rétablir
la garde NaN du tableau → 1 échec ; retirer `<ScenarioReadingMode>` du runner → 1 échec. (Une première
mutation était **invalide** — `parseAxisNumber` lit le nombre où qu'il soit dans l'étiquette, donc
`"x0"` restait numérique ; le comportement sur les libellés d'intervalle « 0-50 » est maintenant épinglé
par un test qui le **choisit** au lieu de le subir.)

Batterie : `vitest` **959 ✓** (916 → +43) · `tsc --noEmit` 0 · `eslint src` 0 erreur / **12 warnings**
(inchangés ; le 13ᵉ que j'avais créé — `computeChartBounds` devenu mort — a été supprimé, pas consigné) ·
`next build` ✓. Le rendu visuel des pages gardées par `AuthGuard` reste invérifiable par curl (§16.4) :
les preuves ci-dessus viennent du rendu `react-dom/server` et des tests, pas d'un code HTTP.

---

## 18. La هيكلة officielle du sujet confrontée aux données d'annales — F31

### 18.0 Ce qui a été lu, et ce qui ne l'a pas été

Ton message annonçait `هيكلة موضوع البكالوريا.pdf`. **Ce fichier n'est jamais arrivé dans le sandbox** :
`/home/user/uploads` n'existe pas et `find / -xdev -iname '*.pdf' -newermt …` ne remonte rien. Je n'ai donc
**pas lu ton document**, et je ne fais pas semblant. J'ai confronté le site au chapitre équivalent déjà
versionné dans le dépôt — `LIVRE-MANHADJIYA.md`, l. 344-470, « 2- هيكلة موضوع البكالوريا » (p. 15-16) —
qui est la même autorité locale. Si ton PDF dit autre chose, envoie-le en texte dans le repo et je reprends
la confrontation.

**Réponse à la question que tu posais en filigrane (§14) : ce chapitre ne débloque pas les grilles.** C'est
un chapitre de *structure et d'économie d'épreuve* (bloc, points, durée, verbes attendus), pas un
`سلم تنقيط` par critère. Les 55 grilles manquent toujours ; les 42 squelettes de `data/rubrics/drafts/`
attendent ta validation, rien n'a changé de ce côté.

### 18.1 Ce que le chapitre fixe (علوم تجريبية, معامل 6)

| Bloc | Points | Temps conseillé dans le livre | Nature |
|---|---|---|---|
| التمرين الأول | **5** | ≈ 45 د | استرجاع + تنظيم وهيكلة ; تعليمات مباشرة |
| التمرين الثاني | **7** | ≈ 1 س 15 د | استدلال علمي ; تحليل مقارن, مناقشة الفرضيات |
| التمرين الثالث | **8** | ≈ 2 س | استدلال ضمن مسعى علمي ; 3 parties, III = حصيلة تركيبية |
| **المجموع** | **20** | 4 س conseillées (contre 3 س d'épreuve) | |

Variante رياضيات : تمرين 6-8 ن + تمرين 12-14 ن, معامل 2. La table des verbes du correcteur
(`VERB_COGNITIVE_LEVELS`) couvre déjà exactement les verbes de ces trois blocs — c'est le bon côté.

### 18.2 Ce que le site enseigne est juste — et je n'y ai pas touché

`khawarizmi-backend/prompts/correction_prompt.py`, `REVISION_TIPS_AR["bac_exam_structure"]` :
« التمرين الأول: 5 نقاط … الثاني: 7 نقاط … الثالث: 8 نقاط … المجموع: 20 نقطة ». **Aligné sur le livre.**
Un test verrouille cette cohérence inter-langages (§18.5) pour que personne ne « modernise » l'un sans l'autre.

### 18.3 Défaut n° 1 — le barème affiché était une somme, pas le mètre officiel (corrigé, F31)

`/annales/[slug]` affichait `🏆 {sujet.exercices.reduce((a, e) => a + e.points, 0)} نقاط`. Or `sujet.exercices`
**concatène les deux options au choix** (`subject-1` **et** `subject-2`), alors qu'un candidat n'en traite
qu'une. Mesure sur les 30 sujets du module :

| année / sujet | total affiché avant | total d'une option |
|---|---|---|
| 2025 | **36** | 18 / 18 |
| 2024 | **36** | 17 / 18 |
| 2022 | **37** | 19 / 18 |
| 2021 | **29** | 14 / 15 |
| 2016 | **32** | 16 / 16 |
| filière Math + 2026 + 2008-2011 (20 sujets) | **0** | — (aucune structure chargée) |

Une épreuve notée sur 20 était annoncée « 36 نقاط » sur 10 sujets et « 0 نقاط » sur 20 autres. Les mêmes
comptes fusionnés apparaissaient sur les cartes de `/annales` (`📄 4 تمارين · 💡 8 أسئلة` pour une épreuve
qui en compte 2 et 4 par option).

**Corrigé** (`src/lib/annales-bac.ts` : `BAC_NOTE_SCALE_POINTS = 20`, `attachedPointsByOption()`,
`optionStats()` ; les deux pages) : le hero affiche l'échelle officielle `🏆 20 نقاط` (titre d'infobulle :
« هيكلة موضوع البكالوريا: 5 + 7 + 8 نقاط »), les comptes sont **par option** (« تمارين لكل خيار »), et quand
le mètre joint ne fait pas 20 une ligne ambre le dit : « 18 نقطة مرفقة — ينقصها 2 نقطة (التمرين الثالث غير
مرفق بعد) ». Les sujets vides disent « لا تمارين مرفقة بعد » au lieu de « 0 نقاط ».

Ce que je n'ai **pas** fait, délibérément : je n'ai réécrit aucun `points:` d'exercice (chiffres scrapés,
pas les miens), je n'ai pas inventé le bloc manquant, et je n'ai pas touché `duree: 180`.

### 18.4 Défaut n° 2 — le tiers le plus lourd de l'épreuve n'existe pas dans les données (non corrigé : il exige une source)

Deux mesures, reproductibles sur `getAllSujets()` :

1. **20 options structurées, 0 qui contiennent une وضعية.** Le mot `وضعية` n'apparaît **nulle part** dans
   `src/lib/annales-bac.ts` (0 occurrence). Les `type` d'exercice réellement présents :
   `analyse_document=18 · raisonnement=12 · argumentation=4 · schema=4 · qcm=2` — soit uniquement les blocs
   1 et 2. **Le التمرين الثالث (8 ن = 40 % de la note, ~2 h de travail) est absent de toute la rubrique**,
   ce qui explique mécaniquement qu'aucune option n'atteigne 20 (plafond mesuré : 19).
2. **80 questions d'annales structurées, 80 sans un seul caractère arabe.** Exemple typique
   (`bac-svt-se-2023`) : `titre: "Réponse humorale"`, `texte: "Décrivez le rôle des plasmocytes."`,
   ids `ex2-2023`, documents « Cinétique de production d'anticorps ». Autrement dit : les fiches
   étiquetées BAC 2016-2025 sont des **exercices fabriqués en français**, pas des sujets ONEC.
   Le site ne ment pas — le bandeau `نماذج تدريبية غير رسمية … لا تحسبها مواضيع رسمية` existe (liste, l. 119-129)
   et chaque carte porte le badge (l. 316), le hero aussi — mais un élève qui vient « travailler les annales
   du bac » dans une épreuve rédigée **en arabe** ne travaille pas l'épreuve.

Conséquence hiérarchique : **la rubrique annales ne peut pas devenir un outil de préparation tant que le
bloc de 8 points et la langue de l'épreuve ne sont pas là.** Ce n'est pas un bug de code, c'est une dette de
données qui suppose les vrais sujets (un PDF ONEC par année, puis `سلم التنقيط` officiel → qui alimenterait
en passant les 55 grilles manquantes). Je ne fabrique ni l'un ni l'autre.

### 18.5 Défaut n° 3 — le budget temps du livre dépasse l'épreuve d'une heure

Le chapitre conseille 45 د + 1 س 15 د + 2 س = **240 minutes**, alors que son propre en-tête (et toutes les
fiches du site : `duree: 180` pour les 30 sujets) fixent l'épreuve à **180 minutes**. Un élève qui suit le
conseil à la lettre dépasse d'1 h, soit 33 % — et c'est précisément dans le bloc qu'il n'a pas (2 س).
Le site n'offre **aucun** repère de temps par bloc pour corriger ça. Deux issues possibles, **c'est ton
arbitrage** : soit tu décides d'un repère cohérent avec 180 min (par exemple proportionnel 40/60/80, à toi
de l'assumer pédagogiquement), soit on retire les conseils de temps du module. Je ne publie pas de chiffres
de gestion du temps sous mon nom sans que tu les valides.

### 18.6 Ce qui verrouille, et ce qui reste ouvert

`src/lib/annales-bareme.test.ts` — **11 tests** : échelle = 5+7+8 ; cohérence avec
`REVISION_TIPS_AR["bac_exam_structure"]` (lecture du fichier backend) ; fixture à deux options de tailles
différentes (le max, pas la somme) ; `null` pour un sujet non structuré, jamais un 0 déguisé ; **la somme
fusionnée est épinglée comme le piège** (`max > 20`) ; aucun total d'option ne dépasse 20 ; la source des
deux pages ne doit plus contenir le `reduce` mensonger et doit porter les libellés « لكل خيار » / « ينقصها ».
Morsure vérifiée par mutation : rétablir `{sujet.exercices.reduce((a, e) => a + e.points, 0)} نقاط` →
1 échec. Une de mes propres affirmations de fixture était fausse (`questions: 2` au lieu de 3 — le code
était juste, mon calcul non) : corrigée dans le test, pas dans le helper.

Batterie : `vitest` **970 ✓** (959 → +11) · `tsc --noEmit` 0 · `eslint src` 0 erreur / 12 warnings (inchangés)
· `next build` ✓ · `/annales` et `/annales/[slug]` en 200 sans erreur de rendu. **Rappel §16.4 : ces pages
sont sous `AuthGuard`, un curl ne prouve pas le contenu** — les chiffres d'avant/après ci-dessus viennent du
module réellement chargé (`tsx`), pas d'un HTML.

**Décisions qui t'appartiennent, dans l'ordre de rendement :** (1) me redonner le PDF (ou sa copie texte)
si ta copie de la هيكلة diffère du livre ; (2) la dette des annales (bloc de 8 ن + arabe) — sans elle la
rubrique reste un entraînement hors format ; (3) le repère de temps (§18.5) ; (4) `API_BASE_URL = ""` en
production, question sans réponse depuis **treize tours** (§11) — aucun appel API élève n'aboutit en prod
tant que ce n'est pas tranché.

---

## 19. F32 — le proxy d'API ne servait à rien : le rewrite le masquait (et D1 devient réglable sans rebuild)

### 19.1 Ce que la question de l'utilisateur a révélé

Question posée : « as-tu identifié la nouvelle URL Railway pour mettre à jour `NEXT_PUBLIC_API_URL` ? ».
Non — et le point n'est plus là. Trois constats : le dépôt ne documente qu'un seul domaine
(`docs/deploiement-vercel.md:15,35` → `khawarizmi-production.up.railway.app`, précisément celui qui ne répond
plus), le sandbox n'avait plus d'egress pendant ce tour (contrôle : `api.github.com` → 200, `example.com`,
`*.vercel.app`, `*.up.railway.app` → **000**), et `gh api …/actions/secrets` → `403 Resource not accessible
by integration`. **Aucun de ces trois obstacles n'a d'importance si l'origine est lue à la requête.**

Le défaut de fond : `next.config.ts` construit ses `rewrites` **au build**, alors que
`.github/workflows/ci.yml` ne re-déploie que Railway (job `deploy-railway`, l. 92-95). Un changement de
domaine côté Railway recasse donc la prod **sans commit, sans CI rouge, sans trace**. C'est la raison pour
laquelle D1 survit à huit audits : elle se régénère seule.

### 19.2 L'implémentation que j'ai écrite, et la mesure qui l'a invalidée avant d'être livrée

Premier essai : `src/app/api/[...path]/route.ts`, handler Node « force-dynamic » qui lit
`API_ORIGIN || NEXT_PUBLIC_API_URL || http://localhost:8000` **par requête**, reconstruit
`${origine}/api/${path}` avec la query, transmet cookie + Authorization + corps, passe le flux HTTP de la
réponse (SSE de `/api/chatbot/ask/stream`), et en cas d'amont injoignable renvoie la **forme d'erreur du
backend** (`{erreur, status, path, method, requestId}` — `routes/errors.py`) en 502, la cause technique
restant dans les logs. **10 tests unitaires, tous verts.**

Puis la mesure qui compte, parce que des tests verts ne prouvent pas le câblage : `API_ORIGIN` pointé sur
un **port mort** (127.0.0.1:8999) avec un amont vivant sur :8000 → la requête `/api/manhadjiya/verbs`
répondait **quand même** le JSON de :8000. Autrement dit **mon handler n'était jamais appelé** : la
documentation de Next place les rewrites du panier `afterFiles` **avant** les routes dynamiques, donc le
`source: "/api/:path*"` de `next.config.ts` absorbait tout. Un proxy mort + 10 tests verts = exactement le
type de correctif qui ferait re-chuter la prod dans six semaines.

### 19.3 Correction appliquée

- `next.config.ts` : le rewrite `/api/:path*` est **retiré** (commentaire qui dit pourquoi, avec la mesure).
  `/health` est conservé — c'est l'empreinte par laquelle on vérifie qu'un domaine sert bien *ce* dépôt.
- Le handler devient le seul chemin pour `/api/*`. `src/app/api` ne contient que lui (vérifié : aucune autre
  route à masquer).
- `deploy-config.test.ts` : la garde qui exigeait « les deux rewrites lisent la même variable » est
  **remplacée** (le contrat a changé, ce n'est pas un test qu'on effile pour être vert) par deux assertions :
  aucun `source: "/api/:path*"` dans la config, et le handler partage bien le repli de dev.

### 19.4 Vérification, en dev et dans le manifest de build

| Sonde | Résultat |
|---|---|
| `API_ORIGIN=http://127.0.0.1:8999` (mort) → `GET /api/manhadjiya/verbs?page=2` via :3000 | `{"erreur":"Le serveur de correction est injoignable. Réessaie dans un instant.","status":502,"path":"/api/manhadjiya/verbs","method":"GET","requestId":"proxy-…"}` — **c'est bien mon handler** |
| `API_ORIGIN=http://127.0.0.1:8000` (vivant) → GET avec cookie | amont reçoit `cookie: sid=eleve-9`, `host: 127.0.0.1:8000`, query préservée |
| POST `/api/grade` avec `authorization: Bearer t` et corps JSON | méthode, corps, en-tête d'autorisation traversent intacts |
| amont qui renvoie 500 (`/api/boom`) | **500 propagé tel quel**, pas mangé en 500 générique ni réécrit |
| `GET /health` via :3000 | passe toujours (rewrite conservé) |
| `/`, `/annales`, `/annales/bac-svt-se-2025`, `/document-analysis`, `/cours` | 200, `err=0` |
| `.next/routes-manifest.json` (build avec `NEXT_PUBLIC_API_URL` posé) | `afterFiles = [{/health → …}]`, **aucun** `/api/:path*` ; `/api/[...path]` bien présent dans `app-path-routes-manifest.json` |

Batterie : `vitest` **981 ✓** (970 → +11) · `tsc --noEmit` 0 · `eslint src` **0 erreur / 12 warnings**
(une 13ᵉ que j'avais créée — `NextRequest` importé pour rien — supprimée, pas consignée) · `next build` ✓.
Remarque de méthode : ma première lecture du manifest (`rm.get("beforeFiles")` au niveau racine) affichait
« aucun rewrite, nulle part » — **faux**, les rewrites vivent sous `rm["rewrites"]["afterFiles"]`. Le
« /health a dispari du build » que j'allais consigner n'existe pas ; corrigé avant d'être écrit.

### 19.5 Ce qu'il te reste à faire (une variable, plus deux drapeaux)

1. **Vercel** → Settings → Environment Variables → ajouter `API_ORIGIN` = l'origine du service Railway
   (sans `/api`). Tu peux garder `NEXT_PUBLIC_API_URL` telle quelle : elle sert encore la CSP et `/health`,
   et `API_ORIGIN` a la priorité sur elle.
2. **Railway** → variables du backend : `LOCAL_RUBRIC_GRADER=true` (sinon `/api/grade` retombe sur le LLM,
   ou échoue si aucun provider n'est configuré) et, si tu assumes les seuils, `SAVOIR_REMEDIATION_ENABLED=true`.
   Ces deux drapeaux valent `False` par défaut dans `config.py` : une URL correcte sans eux laisse la
   correction locale éteinte.
3. **Empreinte de vérification** (à faire depuis ta machine, le sandbox n'ayant pas d'egress ce tour) :
   `curl https://<domaine-railway>/health` doit renvoyer **un objet JSON de diagnostic** (forme de
   `routes/health.py`) et `curl https://<domaine-railway>/api/inexistant` doit renvoyer
   `{"erreur":…,"status":404,"path":…,"method":…}` (forme de `routes/errors.py`). Si tu obtiens `OK` en
   texte brut ou `{"message","requestId"}`, **ce n'est pas ce dépôt** — c'est exactement comme ça que
   `khawarizmi-backend.railway.app` a été démasqué.
4. Un avantage de cette configuration : la CSP reste `connect-src 'self'` (le front n'appelle plus que son
   propre domaine), donc un changement de domaine ne demande plus de retoucher deux endroits.

---

## 20. F34 — l'audit du correcteur mesurait l'audit, pas le correcteur (et un plan de 10 jours dessus)

**Déclencheur.** Un rapport d'audit circule le 2026-09-01 : « 69/100, robustesse adversariale 100/100,
couverture sémantique 55/100, Géologie et Génétique à reconstruire → ~10 jours d'enrichissement de mots-clés
pour atteindre 80/100 ». Les chiffres ont été **re-courus ici, à l'unité près** (`python3
scripts/audit_correcteur.py`, HEAD `c38bf2b`) : 50 items, moyenne 57,6 %, 214 concepts / 1495 variantes,
11 règles graves, 4 règles numériques, 9/9 adversariaux, latence 0,30 ms, `robustesse_score` 0,694.
Le problème n'est donc pas la fabrique des nombres. C'est **ce qu'ils comptent**.

### Ce qui a été mesuré ce tour (pas inféré)

| # | Fait | Comment |
|---|---|---|
| 1 | L'audit **écrit dans l'objet qu'il mesure** : 83 concepts sont ajoutés à `_SYNONYMS` pendant la notation (`_SYNONYMS[cid] = [kw]`, `scripts/audit_correcteur.py` l. 299 et 324), parce que le raccordement mot-clé→concept échoue sur 83 des mots-clés du corpus | compteur `concepts_injectes_par_l_audit` ajouté au rapport ; valeur affichée en tête du markdown |
| 2 | L'entrée évaluée **n'est pas une copie d'élève** : `evaluate_one(q)` retombe sur `reponse_attendue` (l. 202), et `data/golden_set_onec.json` n'a aucun champ `student_answer` (clés : `bareme, chapitre, chapitre_id, id, mots_cles_attendus, niveau, question, reponse_attendue, type`) | lecture des clés du JSON |
| 3 | La « couverture KWD » est calculée en testant la présence du mot-clé **dans la réponse attendue** (`if kw_norm in ans_norm`, l. 186) : c'est de la cohérence interne du corpus, pas de la couverture du programme | relecture de `score_against_expected` |
| 4 | 10 points du score étaient **auto-attribués** (`+ 0.10 * 1.0  # 0 LLM (toujours vrai dans ce script)`) ; retirés et poids renormalisés sur 0,90, l'indice passe de 69,4 à **66,0** | modification + re-run |
| 5 | Les six « garanties 0 LLM » du rapport étaient **du texte codé en dur**, aucune n'était exercée — c'est ce bloc qui a produit la mention « architecture irréprochable » | `grep` du bloc `render_markdown` ; remplacé par `verify_llm_guarantees()` |
| 6 | Le moteur audité est **orphelin** : `deterministic_correct` (v1) n'est appelé par aucune route. `routes/grade.py` → `services/local_grader.grade` (rubriques, `GRADER_VERSION = "1.2.0"`) ; le chemin mots-clés vivant est `deterministic_correct_v2` (`grading/savoir.py`, `tests/golden/scoring.py`, qui dit lui-même « chemin prod réel »). Déjà écrit dans `architecture-moteurs-audit.md` l. 98 : « aucune route ne l'appelle (seulement scripts/audit_correcteur.py) » | `grep -rn "deterministic_correct" --include=*.py` |
| 7 | Sur la même entrée (réponse modèle) : v1 **sans** épinglage de concepts = 97,7 % de moyenne, **0 item à 0 %** ; v2 (chemin servi) = 100,0 % par construction, ses concepts étant déduits de la réponse modèle. Donc le « 0 % Génétique Q6 » n'est pas un trou de l'élève : c'est l'échec du raccordement de l'audit | script ad hoc dans `/tmp`, imports directs de `services.savoir_corrector` |
| 8 | Le nombre de domaines bloqués est **17**, pas 16 ; `tokens_utilises == 0` ✅ ; `LLMDisabledError` sur `chat.completions.create` ✅ ; clés API vidées ✅ ; `is_llm_enabled()` False sous `DISABLE_LLM=1` ✅ ; blocage réseau : **non vérifiable ici** (httpx absent de l'environnement de CI — marqué tel, pas coché) | sortie de `verify_llm_guarantees()` |
| 9 | `tests/golden/metrics.py` (MAE, accord exact, erreurs graves, biais, Cohen κ) **ne tourne pas dans ce sandbox** : `ModuleNotFoundError: No module named 'numpy'` (et `pydantic` absent aussi). Les seuils y sont déjà écrits et bloquants : savoir MAE ≤ 0,35/4 et 0 erreur grave ; L2 MAE ≤ 0,85/4, κ ≥ 0,45 | tentative d'import |

### Jugement

Le plan « +70 mots-clés en Génétique, +80 en Géologie → +11,5 points » est **refusé** pour une raison
simple : *le levier qu'il actionne et la jauge qu'il regarde sont la même chose*. Enrichir `_SYNONYMS`
fait monter « couverture KWD » mécaniquement, parce que l'audit remplit cette table lui-même avant de
noter. Une mesure qui répond à sa propre correction n'est pas une mesure, c'est un bouton. Deuxième
raison : 10 jours dans la seule fenêtre de rentrée (2→6 septembre), pour ne consulter **aucune copie**.

Ce qui est gardé de l'audit, parce que vérifié : les 9 cas adversariaux. C'est le seul endroit du rapport
où une réponse écrite à la main entre dans la machine et où l'on attend un **échec** de notation
(charabia → 0 %, recopie de la question → ≤ 30 %, 36 ATP → 0 %). Une négative-control list de 9 items,
c'est peu, mais c'est non circulaire : c'est un test de précision, pas de rappel.

### Ce qui a changé dans le code (`scripts/audit_correcteur.py`)

- **Déclarations en tête de rapport** : moteur audité vs chemin servi, nature de l'entrée, nombre de
  concepts injectés pendant la mesure. Sans ces trois lignes, les tableaux se lisent comme une qualité de
  notation ; avec, ils se lisent pour ce qu'ils sont.
- **L'indice n'est plus un verdict** : « Score de robustesse 69/100 » → « Alignement interne de l'audit »,
  avec une phrase disant ce qu'il ne mesure pas et la grandeur qui compte à la place.
- **Garanties 0 LLM exercées** (`verify_llm_guarantees()`) : `vérifié` / `échec` / `non vérifiable ici`,
  avec le détail. Le statut « non vérifiable » est écrit tel quel — pas de ✅ de complaisance.
- **`--answers <json|jsonl>`** : évalue de vraies copies, et, dès 5 items portant `human_score`, sort
  MAE, accord exact, biais signé, taux d'erreurs graves et κ (pur Python, sans numpy — pour que ça tourne
  là où `tests/golden/metrics.py` ne tourne pas). Sous 5 items, il **refuse** de calculer un accord.
- **Code de sortie** : plus indexé sur l'indice (auto-attribué) ; `exit 2` si un adversarial échoue ou si
  une garantie 0-LLM tombe. Une ligne stderr rappelle, à chaque exécution sans copie, que le rapport ne
  vaut pas preuve.
- Rendu : « Couverture mots-clés » → « Alignement mots-clés→concepts », avec la mention qu'un 0 % est
  d'abord un échec du raccordement de l'audit.

### La seule chose qui manque encore (et ce n'est pas du code)

`--answers` est écrit, harnais de métriques écrit, seuils écrits, `TRAINING_BANNER_AR` posé : **il n'y a
aucune copie d'élève dans le dépôt** (0 réelle, et les 125 « copies » de `tests/golden/golden_annotated.json`
sont annotées par `synthetic_keyword_v1`, dont ~40 % de réponses attendues recopiées). Les 12 copies de
juin, triées et notées à la main, sont la seule matière qui transforme ce rapport en mesure. C'est le
geste qui ouvre la semaine du 2 septembre, pas l'enrichissement de table.
