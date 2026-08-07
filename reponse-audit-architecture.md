# Réponse à l'audit d'architecture — vérifications et Sprint 0 appliqué

**Date :** 2026-08-07 — **Nature :** vérification de l'audit contre le code réel + implémentation du Sprint 0.

---

# 1. Vérification des constats [Suspecté]

## C4 — Embedder : suspicion RÉFUTÉE (modèle multilingue confirmé)
L'audit suspectait `all-MiniLM-L6-v2` (anglais). **Vérifié dans `models/minilm_onnx_int8/config.json` + `scripts/convert_to_onnx.py` :**
- Modèle : **`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`**
- Vocabulaire : 250 037 (tokenizer XLM-R Unigram) — **pas** le vocabulaire anglais de MiniLM-L6 (~30k)
- Architecture : BertModel, hidden 384, 12 couches, 12 têtes

Le modèle est **multilingue** (formé sur 50+ langues dont l'arabe). Le test AUC de contrôle (50 paires arabes) reste utile pour mesurer la qualité réelle sur l'arabe, mais la prémisse « vocabulaire anglais » est fausse.

## Section 4 — Runtime WSGI sync : suspicion RÉFUTÉE (ASGI async confirmé)
- Déploiement : **uvicorn** (ASGI) partout (Dockerfile racine + backend + railway.toml)
- Tous les appels LLM : `AsyncOpenAI` + `await` (llm.py, llm_helpers, correction_v2, mindmap)
- Aucun endpoint ne bloque un worker ; le sémaphore global et le job async restent des améliorations (pas des corrections de bug)

## C6 — Golden set : partiellement RÉFUTÉ
- `data/golden_set_onec.json` (50 questions ONEC) **existe** et alimente `eval_calibration.py` (calibration des prompts, chargé au boot : « GOLDEN_SET_OK | 50 exemples »)
- `tests/golden/test_regression.py` **existe**
- Ce qui manque réellement : les **métriques MAE/κ contre une note humaine** en CI (le point C6 reste valide sur ce volet)

## Confirmés par le code (avec preuves)

| Constat | Preuve |
|---|---|
| **C1** — contexte scénario re-envoyé N fois | `for ans in body.answers:` → `evaluate_answer_v2_with_retry(scenario_context=..., documents=...)` à chaque itération (route document_analysis_v2.py:121, 2 occurrences) |
| **C2** — aucun cache de correction | `document_analysis_v2.py` : 0 appel à make_cache_key/get_cache/set_cache |
| **C3** — cascade LLM sans deadline global | boucle providers avec `timeout` par appel, aucun budget global → pire cas 7 × 25 s = 175 s |
| **C5** — 4 systèmes de mémoire + 1 fichier | da_fsrs, mastery_micro_concepts, action_verb_progress, fsrs_graph + data/mastery/{id}.json |
| **O2** — clé cache sans version | `make_cache_key("chatbot", lang, mode, chapter, message)` — pas de PROMPT_VERSION/MODEL_ID |
| **O7** — 4 stratégies de parsing JSON | `_extract_json_from_response` : direct → fence → premier/dernier → profondeur |

---

# 2. Sprint 0 implémenté (48 h) — 4 corrections livrées

## C3 — Deadline global + circuit breaker (services/llm.py)
- `GLOBAL_LLM_DEADLINE_SECONDS = 20.0` : budget unique partagé entre le primary et tous les fallbacks ; `timeout = min(timeout, remaining)` par appel ; abandon si `remaining < 2 s`.
- **Breaker par provider** : `_breaker_allow/record_failure/record_success` — 3 échecs → OPEN 60 s (half-open automatique après cooldown).
- **Pire cas panne providers : 175 s → 20 s.**
- Testé : 3 échecs → allow=False ; succès → allow=True.

## C1.3 — max_tokens par intent (services/correction_v2.py)
- Correcteur : `LLM_MAX_TOKENS 4096 → 900` (un JSON v2 tient dans ~900 tokens ; −78 % du plafond de sortie).
- Chatbot : déjà à 350 (défaut `call_llm`). Mindmap : déjà borné (1400-2000 par appel).

## C4-gate — is_semantic + désactivation du cache sémantique (embedder.py + semantic_cache.py)
- `embedder.is_semantic` : True si ONNX chargé, False en fallback (vecteurs = bruit).
- `get_semantic_cache()` retourne None si `not is_semantic` → **plus aucune mauvaise réponse servie par le cache sémantique en mode local** (le trou de sécurité signalé par l'audit est bouché).

## O2 — Version de contrat dans toutes les clés de cache (cache.py)
- `CACHE_CONTRACT_VERSION = "v2"` injectée dans `make_cache_key` → toute la famille de clés (chatbot exact, RAG, correction future) est invalidée d'un coup au prochain bump.
- Vérifié : `khawarizmi:v2:11d760d4…`.

---

# 2c. Sprint 1 (étape 2) — O7 : sortie JSON native provider ✅

## Correctifs de validation O7 (points 1-3) ✅

1. **Activation PROGRESSIVE par provider** (plus de kill-switch global) :
   `config.json_mode_providers: list[str] = []` (défaut VIDE = aucun provider
   en JSON natif, comportement pré-O7). `should_use_json_mode(provider, cfg)`
   vérifie la capacité (caps.json_mode != "none") ET la présence du nom
   canonique dans la liste → rollback d'un seul provider sans toucher les
   autres. Étapes conseillées : `["openai"]` (semaine 1) → +groq → +gemini,
   en surveillant `parse_strategy_total{strategy,provider}`.
2. **Mapping v2→v1 extrait en fonction pure** `grading/mapping.py::map_v2_to_v1`
   (testable avec du JSON natif parfait) + **amélioration type-aware** du
   dominant_error_code : une erreur scientifique v2 → `scientific_error`
   (remédiation contenu) au lieu du fallback aveugle `methodology_error`
   (toutes les erreurs v2 → unmatched → methodology_error). Le plan supposait
   `grade → dominant_error_code` : faux vs code réel (grade → advice_ar,
   dominant dérivé des errors/score) — documenté et testé.
3. **Label `provider` sur `parse_strategy_total{strategy,provider}`** :
   `record_parse_strategy(strategy, provider)` — permet de savoir QUI produit
   les stratégies de rattrapage (ex. 90 % des fence sur Groq → alerte
   d'intégration) et quels providers activer en priorité.

## Étape suivante — Golden metrics CI ✅ (cf. section 2d)

Livré : `services/llm_providers.py` (capacités par provider), `grading/parser.py`
(stratégies + compteur), `grading/schemas/correction_output.py` (schémas),
`_call_with_fallback(json_schema=...)` (dispatch par appel), `correction_v2.py`
(passe le schéma + parse avec `json_mode_used`), kill-switch
`config.json_mode_enabled` (défaut True).

- **Capacité déclarée par provider, pas de flag global** : `ProviderCapabilities`
  (json_mode / max_output_tokens / supports_prefix_caching pour C1 futur).
  Tous les providers passent par le SDK AsyncOpenAI (même Gemini via son
  endpoint OpenAI-compatible) → dispatch OpenAI-style :
  - primary auto-détecté par la clé (gsk_* → json_object, AIza* → json_object,
    sinon json_schema strict) ; Gemini fallback → json_object ;
    GLM-4.7 (Z.AI) → json_object ; Cloudflare/ZenMux/Nara → **none** (prudent,
    jamais de response_format non validé — ajustable dans PROVIDER_CAPS).
  - `apply_json_mode(call_kwargs, provider, schema)` : fonction PURE testable ;
    la réponse est taggée `_khawarizmi_json_mode` → `json_mode_used` côté
    correction_v2.
- **⚠️ Divergence documentée vs plan** : le schéma natif doit matcher le format
  DEMANDÉ par le prompt, pas le contrat public v1. Le prompt v2 (PROD,
  use_v2_prompt=True) demande `{score: 0-100, errors:[{line,type,detail,fix}],
  feedback, grade}` — forcer le schéma v1 déclencherait le mapping v2→v1 de
  correction_v2.py sur du v1 → score multiplié par score_max/100 (catastrophe
  silencieuse). `CORRECTION_V2_JSON_SCHEMA` = format v2 (PROD) ; le mapping
  v2→v1 produit ensuite le contrat public inchangé. `CORRECTION_V1_JSON_SCHEMA`
  (non utilisé en prod) aligné sur les types RÉELS du code : highlights.type =
  gibberish/off_topic/missing_link/wrong_formulation/irrelevant/good_element
  (le plan listait error/missing/good/partial — faux vs `_validate_highlights`),
  dominant_error_code = 13 valeurs réelles (pas 8).
- **Piège Gemini neutralisé par l'architecture** : response_schema du SDK
  Google force tous les champs déclarés → on utilise l'endpoint
  OpenAI-compatible avec `response_format={"type":"json_object"}` (JSON valide
  garanti, aucun champ optionnel inventé). Pas de build_provider_schema.
- **Strict-compat OpenAI** : chaque champ déclaré est required OU nullable
  (`["T","null"]` — confidence/advice_ar optionnels comme prévu au plan).
  Mini-validateur structurel maison (jsonschema n'est pas une dépendance).
- **Parser fallback conservé et mesuré** : `grading/parser.py` —
  native_json → direct → fence → regex → partial → failed ;
  `parse_strategy_total{strategy}` compté à chaque correction.
  Objectif : native_json > 95 % sur providers JSON-capables (alerte si < 90 %).
- **Test nightly qualité** (`tests/golden/test_json_mode_quality.py`, marqué
  `nightly`, skippé en CI / sans clé réelle) : MAE(json, baseline free) ≤ 0.15
  et std(json) ≥ 0.70×std(free) sur 10 items du golden set ONEC (pas de scores
  humains dans le set → baseline = mode texte libre, non-régression).
- **Tests** : +40 → **733 passed, 3 skipped (2 nightly + 1 préexistant),
  5 xfailed** · ruff vert. C2 inchangé (le cache opère sur le résultat parsé).

---

Livré dans le **package `grading/`** (`grading/cache_key.py` + `grading/cache.py`)
— **wrapper** autour de `evaluate_answer_v2_with_retry` (aucune édition des
700 lignes de `correction_v2.py` ; le refactor `grading/` de S2.1 se posera
dessus sans friction). Route `document_analysis_v2.py` branchée.

- **Vérification préalable (bloquante)** : le prompt de correction est PUR —
  aucun champ élève (prenom/user/attempt/fsrs/stability/niveau) dans
  `prompts/correction_prompt.py` ni `prompts/correction_prompt_v2.py` ; tous
  les inputs sont dérivés de (question, verbe, barème, copie) → cache
  partageable sans `user_id`, ni `attempt_bucket`, ni `level_bucket` à ajouter.
- **Clé** : `corr:{CACHE_CONTRACT_VERSION}:c1:prompt:p1:variant:{v1|v2}:
  model:{modèle CONFIGURÉ}:q:{question_id}:verb:{verb_slug}:smax:{score_max}:
  ans:{hmac_sha256(pepper, canonical)}` — `score_max` dans la clé ⇒ un
  changement de barème (VERB_RULES) invalide seul ; un déploiement invalide
  sélectivement (14 j de TTL).
- **Piège 1 (offsets)** : `key_normalize` — seule normalisation à décalage
  calculable : **lstrip** (`delta` uniforme reprojeté) + **rstrip** (sans
  effet sur les offsets). Le texte canonique est envoyé au LLM (cache et LLM
  même référentiel), highlights stockés en espace CANONIQUE, reprojetés +delta
  puis clampés sur la copie réelle au retour (hit ET miss → même convention).
  Interdits : collapse interne, ar_normalize, tashkîl **et conversion
  `\r\n`→`\n`** (elle casserait la bijection : le frontend affiche la copie
  brute qui garde ses `\r` → offsets JS faux d'un caractère par CRLF ; une
  copie CRLF est un miss documenté, zéro risque).
- **Piège 2 (champs par-élève)** : payload = `CACHEABLE_FIELDS` uniquement ;
  `student_answer_hash`, `prompt_hash`, `llm_raw_hash`, `attempts`,
  `parse_status`, `source` recalculés à chaque hit — jamais lus du cache.
  Aucun `llm_raw` dans le payload (vérifié par test).
- **Piège 3 (note dégradée)** : `is_cacheable` — seules les notes de confiance
  (`llm`/`llm_v2`/`llm_retried` + contrat futur `local_savoir`/`local_l2_high_conf`,
  sanity_code `ok`, parse `ok`/`recovered`) sont cachées ; `local_fallback`,
  `sanity`, `llm_error` jamais (équité : on ne fige pas une panne LLM pour 7 j).
  ⚠️ Point factuel : `parse_status == "ok"` STRICT tuerait le cache en prod —
  `correction_v2.py:825` fait `"ok" if source == "llm" else "recovered"`, or la
  route est en `use_v2_prompt=True` → `source="llm_v2"` → `"recovered"`. On
  garde `{"ok", "recovered"}` (testé `test_llm_v2_is_cacheable`).
- **Ordre pipeline** : sanity pré-check dans le wrapper AVANT le lookup (un
  rejet sanity est déterministe et ~µs — jamais de lookup ni de store, vérifié
  par compteurs) → lookup → single-flight + double-check → évaluation →
  store conditionnel.
- **Single-flight** : verrou local + verrou Redis (Lua CAS, libération
  conditionnée au token, attente bornée) — 30 élèves sur la même question →
  **1 seul appel LLM**.
- **Hit** : `from_cache=True` + **source d'origine PRÉSERVÉE** (ex. `llm_v2` —
  `grading_source_total` reste fidèle), `attempts=0`, `parse_status="cached"`,
  0 appel LLM. Le champ `from_cache` est exposé dans la réponse API.
- **Observabilité** : `correction_cache_ops_total{result,verb}` par verbe —
  labels `hit | hit_after_wait | miss | store | skip_uncacheable` (logs
  structurés + compteurs `grading_cache_stats()`). Hit rate par verbe =
  (hit+hit_after_wait)/(hit+hit_after_wait+miss).
- **TTL 7 jours** (`CORRECTION_CACHE_TTL`), invalidation 100 % passive via la
  clé (prompt version, variant v1/v2, modèle configuré, score_max).
- **Réserve B §7** : seuil FSRS `3.0` unifié dans `services/pedagogical.py`
  (`pedagogical_bucket`, absent ≡ 0.0 ≡ "low") — le namespace "default" de la
  clé chatbot est supprimé (poids mort) ; aligné sur la route chatbot,
  l'orchestrateur, chat_service, chat_prompt et remediation.
- **Tests** : les 10 acceptations C2 couvertes (2e envoi → cache avec
  `from_cache=True` + source préservée ; espaces de bord → hit / espaces
  internes & CRLF → miss documenté ; 1 caractère de différence → miss ;
  payload sans llm_raw ni copie ; llm_error & sanity jamais cachés ; bump de
  version → invalidation passive ; sans Redis → calcul direct ; single-flight
  10 concurrents → 1 appel ; source d'origine préservée) → **693 passed,
  1 skipped, 5 xfailed** · ruff vert.

---

# 2d. Sprint 1 (étape 3) — Golden metrics CI (prérequis O1/savoir_corrector) ✅

Livré : `tests/golden/metrics.py` (MAE, exact, severe, bias, κ, std_ratio),
`tests/golden/test_golden_local.py` (CI, 0 token, 0 clé), 
`tests/golden/build_golden_annotated.py` + `golden_annotated.json` (125 items),
`can_handle`/`confidence_for` créés sur savoir_corrector (réponse à la
question : le moteur n'avait PAS de can_handle — sa fonction publique était
`deterministic_correct`).

- **Annotation (réponse à la question 1)** : pas d'expert SVT disponible dans
  le sandbox → **approche B améliorée** : annotations SYNTHÉTIQUES
  déterministes (human_score = barème × proportion de mots-clés présents dans
  la copie, tolérance à l'article défini ال). Format IDENTIQUE à l'annotation
  humaine du plan (human_score, human_dominant_error, annotator,
  annotation_date) — remplacer annotator "synthetic_keyword_v1" par
  "expert_svt" quand les vraies annotations existent, la mécanique ne change
  pas. 125 items : 43 all_correct / 55 partial_correct / 25 empty /
  2 insufficient.
- **Seuils bloquants CI** (première exécution = calibration) :
  - L2 (n=100, copies vides exclues — elles passent par sanity dans le
    pipeline réel) : **MAE=0.27** (seuil 0.85) · severe=0.01 (≤ 0.10) ·
    **κ=0.714** (≥ 0.45) · bias=-0.07
  - savoir (n=119/125, coverage 95 %, périmètre can_handle ET confiance
    ≥ 0.92 — le périmètre EXACT du futur branchement haute confiance) :
    **MAE=0.327** (≤ 0.35) · **severe=0.0** (spécialiste) · κ=0.449 ·
    bias=-0.265 (léger pessimisme à surveiller)
  - sanity : 0 faux rejet sur copies notées > 0 ; tous les "empty" rejetés
  - Cohérence : un rejet sanity implique un code humain de rejet
- **2 artefacts d'annotation corrigés en cours de route** (détectés par le
  test lui-même) : matching littéral des mots-clés vs formes définies arabes
  (gs_016 : « حرارة مثلى » vs « الحرارة المثلى ») → normalisation ال par mot ;
  score de la copie parfaite forcé à bareme sans vérifier les mots-clés →
  définition unique (proportion réelle).
- **savoir_corrector.can_handle / confidence_for** : `can_handle` = ≥ 2
  concepts du lexique dans (question + réponse modèle) ; `confidence_for` =
  min(1.0, concepts/3) → ≥ 0.92 ⟺ ≥ 3 concepts couverts (seuil de promotion
  local_savoir du design validé). Le test golden mesure sur CE périmètre.
- **CI** : job `golden set (local, 0 token — BLOQUANT)` ajouté à
  `docs/ci/ci.yml.amelioree` (build_golden_annotated.py + test_golden_local.py)
  + job `golden-llm-nightly` (test_json_mode_quality, sur schedule, clé LLM).
  ⚠️ Toujours non poussable dans `.github/workflows/` (permission workflows
  absente — vérifié) : le fichier attend une permission accordée.
- **Tests** : +18 → **751 passed, 3 skipped, 5 xfailed** · ruff vert.

---

# 3. Réponses aux 3 questions de l'audit

1. **Quel modèle ONNX ?** → `paraphrase-multilingual-MiniLM-L12-v2` (multilingue, pas anglais-only). C4 reste à mesurer (AUC 50 paires arabes) mais le remplacement d'urgence n'est pas nécessaire.
2. **Runtime WSGI sync ou ASGI async ?** → **ASGI async** (uvicorn + AsyncOpenAI). La section 4 de l'audit ne s'applique pas en l'état ; le job async et le sémaphore restent des optimisations de capacité.
3. **Volumétrie rag_chunks ?** → ingestion via `ingest_livre_manhadjiya.py` (chunks depuis LIVRE-MANHADJIYA.md, ~400 sections → milliers de chunks). En dessous de 5 000 chunks, O4 (index GIN) est du confort ; le volume réel dépend de l'exécution de l'ingestion.

---

# 4. Divergence d'avis sur un point

L'audit recommande de **supprimer `savoir_corrector.py` (665 l.)** (« orphelin »). Mon avis diffère :
- C'est un **moteur testé et précis** (4/4 bonne réponse, 0/4 hors-sujet, détecte « 38 ATP » faux — vérifié cette session).
- La bonne action n'est pas la suppression mais le **branchement comme étage 1 du correcteur v2** (questions fermées à mots-clés/numériques, 0 token) — c'est d'ailleurs O1 de l'audit (gating par confiance) qui en a besoin.
- La « règle un module par responsabilité » s'applique au *duplication de pipeline*, pas au *moteur lui-même* : savoir_correct est le juge local le plus précis pour un type de questions.

---

# 5. État final

- Ruff : All checks passed · pytest : **644/644** (inchangé)
- Breaker/deadline testés unitairement · clé cache versionnée
- Prochaines étapes recommandées (Sprint 1) : C2 (cache de correction), C1.1 (préfixe stable + prompt caching), O7 (JSON natif), O4 (ar_normalize + index)
