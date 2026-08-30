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
> corrections/h étaient **partagées par tous les élèves du site** et le plan `pro` n'était jamais
> reconnu ; **F12 (moyen)** le 429 de quota sortait hors contrat d'erreur et **écrasait toutes les
> notes du scénario** dans l'UI (crash 500 latent) ; **F15 (moyen)** le bac blanc appelle le
> correcteur local avec des ids qui ne peuvent **jamais** rencontrer une grille. F13 reste dû :
> trois surfaces de correction backend sans appelant frontend. **F12/F14/F15 corrigés (S38/S39),
> gardes ajoutées.**

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
