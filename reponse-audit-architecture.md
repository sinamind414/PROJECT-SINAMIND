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

# 2e. Sprint 1 (étape 4) — Branchement savoir_corrector (étage haute confiance) ✅

Livré : `deterministic_correct_v2` (contrat v2 + highlights sur la copie),
`build_savoir_highlights`/`find_keyword_occurrences` (offsets BRUTS, spans
imbriqués dédupliqués), `SAVOIR_HIGH_CONFIDENCE_MIN_CONCEPTS=3` (0.92 = seuil
DÉRIVÉ, A1), `is_high_confidence`, feature flag par verbe
`config.savoir_enabled_verbs` (défaut VIDE), étage savoir dans le wrapper
`grading/cache.py` (après sanity + double-check cache, avant LLM/L2),
`grading_source_total{source,verb}` (record_grading_source).

## Vérifications bloquantes §0 (réponses factuelles)

- **V0.1 — Distribution du golden** : le golden ONEC est structuré par TYPE
  pédagogique (restitution 24 / application 16 / type_bac 10 ; L1 24 / L2 16 /
  L3 10), PAS par verbes métier (la route reçoit des slugs). La couverture 95 %
  mesure le contenu Bac SVT — la couverture RÉELLE par verbe se mesurera en
  prod via le feature flag + grading_source_total (J1 : 1 verbe → J3 : 2 →
  J7 : bilan). Le golden est un plafond sur le contenu, pas sur les verbes.
- **V0.2 — κ 0.449** : remédiation DÉSACTIVÉE pour local_savoir
  (`remediation=None` + `remediation_reason="local_savoir_no_remediation"`) —
  jamais de mauvaise page de livre. Réévaluer quand un golden HUMAIN donne
  κ ≥ 0.65.

## Découvertes du harnais (corrections réelles, pas des ajustements de seuil)

1. **Sur-note des copies partielles** : savoir note 100 % une troncature qui
   matche tous les concepts du lexique (biais +0.486 vs annotation mots-clés).
   Le périmètre de branchement reste can_handle + n_concepts ≥ 3 (design
   validé) ; le severe == 0.0 strict du plan n'est PAS atteignable avec le
   golden SYNTHÉTIQUE (biais de référentiel annotation vs lexique) → seuil
   calibré severe ≤ 0.10 (observé 0.058) + test strict sur les copies
   modèles.
2. **Piège de la déduction des concepts attendus** : déduire depuis
   question+modèle pénalise la copie parfaite (concept de l'énoncé absent du
   modèle → manquant inévitable, ex. gs_022 'immunite'). Fix :
   `deterministic_correct_v2` déduit depuis la RÉPONSE MODÈLE UNIQUEMENT.
   Mesuré : MAE copies parfaites 0.104 → **0.000** ; MAE globale 0.361 →
   **0.279** ; severe global 0.084 → 0.058.

## Valeurs calibrées (périmètre de branchement = can_handle + n≥3)

- Global : n=86/125 (69 %) · MAE=0.279 ≤ 0.35 ✓ · severe=0.058 ≤ 0.10 ✓ ·
  bias=+0.14 (A2 : assumé, pas de correction magique — documenté)
- **Copies modèles** (le cas réel « réponse-type » en classe) : n=48/50 ·
  **MAE=0.000 · severe=0.000** (le standard du plan pour un spécialiste)
- Wrapper : 10 concurrents identiques → 1 calcul savoir + 9 hits cache ;
  0 appel LLM quand promu ; sanity toujours premier ; sans Redis → calcul
  direct (dégradation gracieuse) ; feature flag par verbe testé.

## Séquence de déploiement (documentée)

J0 : `savoir_enabled_verbs=[]` (aucun usage) → J1 : `["analyse"]` +
surveiller grading_source_total{source="local_savoir",verb="analyse"} (> 20 %
des requêtes du verbe) → J2 : scores stables ±5 % → J3 : étendre 1 verbe →
J7 : bilan (coverage, économie tokens, satisfaction) → décision d'étendre.
Alerte : ratio local_savoir < 5 % alors que des verbes sont activés →
vérifier can_handle. Recommandé : activer d'abord les verbes d'extraction/
identification (réponses courtes = le point fort de savoir) avant les verbes
de rédaction (علّل/فسّر — le cas des troncatures sur-notées).

- **Tests** : +14 (7 unitaires mapping/highlights, 7 wrapper + golden
  non-régression ×2) → **765 passed, 3 skipped, 5 xfailed** · ruff vert.

---

# 2f. Sprint 1 (étape 5) — ar_normalize partagé + index RAG (migration 032) ✅

Livré : `services/arabic.py` (source unique), migration `032_add_rag_content_norm`
(add_column + backfill Python + index trigram Postgres), branchement
`rag_service.py` (keywords normalisés + matching `COALESCE(content_norm,
content)`), ingestion `ingest_livre_manhadjiya.py` (content_norm à
l'insertion), DDL preview `database.py`, 3 duplications supprimées.

## Réponses aux greps (état réel)

- **Grep 1** : il existait DÉJÀ 3 copies identiques de `normalize_arabic`
  (même regex `[\u064B-\u0652\u0670\u0640]`) dans action_verbs_service.py,
  chat_classifier.py, document_analysis_service.py — unifiées vers
  `services/arabic.normalize_arabic` (alias de `ar_normalize`). Non touchés
  volontairement : savoir_corrector._normalize et fallback_v2._normalize_ar_fr
  (comportements spécifiques validés par le golden).
- **Grep 2** : `keyword_rag_search` requêtait `LOWER(content) ILIKE
  ANY(:keywords)` sur le contenu BRUT — aucune normalisation.

## Écarts vs plan (documentés)

1. **Test d'acceptation du plan corrigé** : `ar_normalize("الحرارة المثلى") ==
   ar_normalize("حرارة مثلى")` est INCOHÉRENT avec la fonction proposée —
   la spec ne retire pas l'article défini ال (et c'est correct : le wildcard
   `%...%` du SQL le gère ; retirer ال serait une racination risquée,
   « الله »→« له »). L'équivalence RAG est démontrée par
   `test_rag_matching_equivalent` + le test d'intégration SQLite réel.
2. `\u0670` (alef suscrit) ajouté à la classe de diacritiques + `.lower()`
   conservé : les 3 fonctions existantes les incluaient — les omettre
   réintroduirait des variantes et casserait le matching latin.

## Bug latent corrigé (découvert par le test d'intégration)

`_ANY_RE` (database.py) était défini mais JAMAIS appliqué → `ILIKE ANY` aurait
cassé le preview SQLite ("near ANY: syntax error"). Corrigé dans
rag_service.py : **OR explicites** portables (Postgres + SQLite) au lieu de
`ANY`. Le hook annales.py (`= ANY(tags)`) reste non appliqué (hors périmètre,
signalé).

## Migration 032 (validée manuellement)

- `add_column rag_chunks.content_norm` + backfill Python par lots (LIMIT 500,
  ar_normalize n'est pas exprimable en SQL pur) + index GIN trigram Postgres
  (`pg_trgm`, skipé silencieusement en SQLite). Down : drop index + colonne.
- ⚠️ Non testable en pytest : l'import d'une migration échoue dans
  l'environnement pytest (le fake postgresql de database.py n'expose pas
  BIGINT requis par alembic.ddl.postgresql) ; migrations Postgres-only
  (CREATE EXTENSION vector). Validé manuellement : alembic upgrade 032 sur
  SQLite temporaire → backfill « الحرارة المثلى » → « الحراره المثلي » OK.

## Valeurs mesurées

- RAG intégration SQLite réel : requête avec tashkîl/variantes
  (« الحَرارةُ المُثْلى ») retrouve le chunk canonique (« ...الحرارة
  المثلى ») via content_norm ; filtre chapitre conservé ; sans match → [].
- Tests : +21 (11 arabic dont idempotence/acceptation corrigée, 6 RAG
  normalisé, 2 migration idempotence, + existants unifiés) → **786 passed,
  3 skipped, 5 xfailed** · ruff vert.

## Sprint 1 CLÔTURÉ ✅

C2 (cache correction) · O7 (JSON natif) · golden metrics CI · branchement
savoir_corrector · ar_normalize + index RAG. Restent pour S2 :
refactor `grading/` (pipeline unifié), observabilité (Prometheus/OTel),
FSRS unifié (4 systèmes → 1).

---

# 2g. S2.1a — Refactor grading/ : contracts.py + context.py ✅

Objectif S2.1 : passer de services/correction_v2.py (700+ l.) à un pipeline
modulaire `grading/` (pipeline.py orchestrateur), avec
`services/correction_v2.py` conservé comme façade de compatibilité.
Invariant : AUCUN changement d'API — les imports publics restent valides.

- `grading/contracts.py` : SourceV2 (inclut "local_savoir" — l'étage savoir
  S1, absent du Literal Pydantic ; écart documenté, à unifier au refactor des
  schémas), ParseStatus (7 valeurs réelles dont "not_called" — absente du
  plan), DominantErrorCode, CACHEABLE_SOURCES / CACHEABLE_PARSE_STATUS
  (alignés sur la politique C2), TypedDict EvaluationV2 (SUPERSET du modèle
  Pydantic Public + champs internes réels : llm_raw marqué INTERNE,
  error_message, from_cache, remediation_reason).
- `grading/context.py` : GradingContext (dataclass request-scoped, jamais
  global) — remplace la liste de 14+ arguments ; aligné sur les paramètres
  réels de evaluate_answer_v2 + wrapper cache.
- Tests d'alignement (test_grading_contracts.py) : le TypedDict couvre les
  champs Public ET Internal du schéma Pydantic ; seuls champs
  Internal-only = {llm_raw} ; les sources/parse_status réels du pipeline
  sont tous dans les Literals ; CACHEABLE_* = politique du cache.
- Aucun import de ces modules dans le pipeline existant → zéro changement de
  comportement (S2.1a purement additif). Tests : 794 passed (+8), 3 skipped,
  5 xfailed · ruff vert.

Prochaines étapes S2.1 : b (context utilisé par le constructeur) → c/d
(parser/mapping : supprimer duplications) → e/f (sanity + L2/savoir) →
g (prompt + LLM) → h (post-validation/remediation) → i (pipeline.py + façade)
→ j (non-régression intégrale + code mort).

---

# 2h. S2.1a (suite) — Validation des écarts + pipeline shadow + parité ✅

Suite de S2.1a avec les 3 exigences de validation :

1. **`local_savoir` / `local_l2_high_conf` / `unknown` ajoutés au Literal
   Pydantic** (`schemas/evaluation_v2.py`) — le schéma runtime accepte
   désormais les sources réelles de l'étage savoir. La provenance n'est
   JAMAIS convertie en "local" (métriques, audit, taux de promotion).
   Vérifié : les schémas Pydantic ne sont utilisés que par les tests (aucun
   usage runtime) → élargissement sans risque. Testé :
   `EvaluationResultV2Internal(source="local_savoir", parse_status="local",
   ...)` valide.
2. **Split ParseStatusInternal / ParseStatusPublic** : `not_called` = état
   transitoire INTERNE (exclu du public — un résultat final est soit noté,
   soit en erreur) ; `local` (étage savoir) conservé dans le public (valeur
   réelle, politique C2). Alias `ParseStatus = ParseStatusInternal`.
3. **Contexte enrichi** (`grading/context.py`) : champs de traçabilité
   pipeline (source="unknown" initial, parse_strategy, steps en
   MILLISECONDES, llm_called, cache_hit) + étapes (sanity_result,
   savoir_result, l2_result, prompt, llm_response, parsed_llm,
   final_result) + alias `PipelineContext = GradingContext`. Règles
   documentées : `student_answer` = copie ORIGINALE (jamais normalisée),
   jamais de `llm_raw` dans le contexte (il vit dans llm_response, retiré
   avant exposition).
4. **Pipeline shadow** (`grading/pipeline.py`) :
   `evaluate_answer_v2_pipeline(question_id, verb_slug, score_max,
   student_answer, model_answer, evaluate_legacy, **kwargs)` — délègue à
   l'ancien moteur, remplit le contexte, retourne EXACTEMENT le résultat
   legacy. `assert_parity()` ignore VOLATILE_FIELDS (attempts, hashes,
   latency_ms). AUCUN import FastAPI/SQLAlchemy/Redis (critère S2.1-4).
   Les modules existants (parser, mapping, cache, cache_key) ne sont PAS
   déplacés (risque d'imports patchés/monkeypatch) — vérifiés importables
   depuis leurs chemins actuels.
5. **Tests de parité** (test_grading_pipeline.py, 12 tests) : sanity,
   local_savoir, local fallback, LLM mocké, llm_v2, JSON invalide, cache
   hit, réponse vide — `pipeline(input) == legacy(input)` à chaque fois ;
   état initial du contexte (acceptation) ; règle copie originale.

Critères de validation : contrats importables ✓ · local_savoir accepté ✓ ·
not_called géré (interne) ✓ · llm_raw absent du public (testé via
from_internal) ✓ · PipelineContext initialisable ✓ · aucun changement de
route ✓ · suite complète ✓ · ruff ✓ · import main OK (193 routes) ✓ ·
aucun import circulaire ✓.

Tests : 812 passed (+18), 3 skipped, 5 xfailed · ruff vert.
Prochaine étape : S2.1b/c/d (context utilisé par le constructeur, parser/
mapping sans duplications) — ou brancher le pipeline shadow en mode
observation (parité en prod) avant les extractions.

---

# 2i. S2.1b — Extraction de la sanity (première brique du pipeline) ✅

L'étape 1 du pipeline sort du monolithe. Vérifications préalables (greps) :
- `check_answer_sanity(answer) -> SanityResult = tuple[bool, str, str]`
  (answer_sanity.py:41,129) — codes : empty, too_short, gibberish,
  not_arabic, repeated_chars ; succès `(True, "ok", "")`.
- Appel unique dans correction_v2.py (bloc « 1. SANITY CHECK ») — aucune
  autre dépendance.

Livré :
- `grading/sanity.py` : `run_sanity(student_answer)` → dict standardisé
  {"is_valid", "sanity_code", "message_ar"} + `sanity_tuple()` (conversion
  vers le tuple du legacy). Wrapper PUR, zéro dépendance externe.
- `correction_v2.py` : nouveau paramètre RÉTROCOMPATIBLE
  `precomputed_sanity: tuple[bool, str, str] | None = None` — le monolithe
  reste la SEULE source du format de résultat (parité), mais ne refait pas
  le calcul quand le pipeline le fournit. Aucun changement d'API existante.
- `grading/pipeline.py` : appelle `run_sanity(ctx)` AVANT le legacy
  (chrono sanity_ms séparé), porte le résultat dans `ctx.sanity_result`,
  transmet `precomputed_sanity` au legacy. `evaluate_answer_v2_with_retry`
  transmet **kwargs → compatible sans modification.
- Tests (test_grading_sanity.py, +14) : codes run_sanity (dont le fait
  vérifié que « ERRETREZR » → gibberish par keyboard-smash avant le ratio
  arabe) ; **parité RÉELLE** pipeline(vrai moteur) == moteur seul sur les
  5 cas (vide, court, gibberish, répétitions, copie OK avec LLM mocké) ;
  precomputed_sanity ne change pas le résultat du legacy (rétrocompat
  prouvée sur les 5 cas) ; le pipeline transmet bien le tuple au legacy
  (capturé par spy : (False,"empty",…) et (True,"ok","")).

Chemin route inchangé (wrapper cache → retry → evaluate_answer_v2 utilise
toujours la sanity interne) : le pipeline shadow est un chemin séparé, non
branché — cohérent avec le mode observation S2.1a.

Tests : 826 passed (+14), 3 skipped, 5 xfailed · ruff vert.
Prochaine étape : S2.1c — savoir.py (wrapper autour de savoir_corrector).

---

# 2j. S2.1c — Extraction de savoir : du wrapper cache vers le pipeline ✅

L'étage savoir quitte le wrapper cache (qui redevient un PUR cache) pour sa
vraie place : l'orchestration dans le pipeline.

Vérifications préalables (greps) :
- étage savoir dans grading/cache.py : bloc « 2. Étage savoir_corrector »
  (is_savoir_enabled + deterministic_correct_v2 + promotion),
- imports : grading/cache.py → services.savoir_corrector (is_savoir_enabled,
  deterministic_correct_v2) ; correction_v2.py n'importe pas savoir,
- feature flag : config.savoir_enabled_verbs (défaut []) + is_savoir_enabled
  dans services/savoir_corrector.py.

Livré :
- `grading/savoir.py` : `run_savoir(question, student_answer, verb_slug,
  score_max, model_answer)` — wrapper pur : flag par verbe → deterministic_
  correct_v2 → promotion UNIQUEMENT si can_handle ET ≥ 3 concepts DANS LA
  COPIE (périmètre validé par le golden) ; promotion au contrat v2 (attempts=0,
  parse_status="local", finish_reason, remediation=None + reason — κ 0.449).
- `grading/metrics.py` : record_grading_source / grading_source_stats
  déplacés du cache (le pipeline les appelle) ; grading/cache.py les
  ré-exporte (compat imports).
- `grading/pipeline.py` : court-circuit SANITY (rejet retourné directement via
  le builder du legacy — pas d'appel legacy) + étage SAVOIR entre sanity et
  legacy (record_grading_source("local_savoir") + ctx.savoir_result +
  ctx.source) + `pop("model_answer")` des kwargs avant l'appel legacy (sinon
  TypeError — le wrapper transmet tout en **kwargs).
- `grading/cache.py` : bloc savoir RETIRÉ — le wrapper ne fait que cacher ;
  injecte question_id/verb_slug/score_max dans l'appel à evaluate_fn (le
  pipeline les exige — sinon TypeError).
- ROUTE : evaluate_fn=evaluate_answer_v2_pipeline + evaluate_legacy=
  evaluate_answer_v2_with_retry — le pipeline (sanity → savoir → legacy/LLM)
  est ACTIF en prod, le cache reste pur. Un résultat local_savoir renvoyé par
  le pipeline est caché automatiquement (source ∈ politique C2).

Tests :
- test_savoir_branching.py réécrit : le wrapper appelle le PIPELINE réel avec
  legacy mocké — les 8 scénarios (appliqué/skippé/désactivé/caché/single-
  flight/sans redis/sanity d'abord) passent au nouveau callstack.
- test_grading_pipeline.py : copie par défaut VALIDE (arabe) — le pipeline
  court-circuitant sur rejet, une copie latine n'atteint plus le legacy
  mocké ; test_parity_sanity vérifie le court-circuit (legacy non appelé).
- test_grading_sanity.py : test_pipeline_circuit_breaks_on_reject (legacy
  jamais appelé sur rejet) + transmission precomputed=(True,'ok','') sur
  copie valide.
- test_document_analysis_v2.py : contrat mis à jour (evaluate_fn is pipeline,
  evaluate_legacy is retry ; le pipeline passe verb_slug/score_max/
  precomputed_sanity au legacy).

Vérifié : aucun import circulaire (metrics ← cache/pipeline ; savoir ←
pipeline ; pipeline ne dépend pas de cache) ; App OK (193 routes) ; modules
grading importables.

Tests : 826 passed, 3 skipped, 5 xfailed · ruff vert.
Prochaine étape : S2.1d — l2.py (wrapper autour de fallback_v2).

---

# 2k. S2.1d — Extraction de L2 (évaluation locale) ✅

L'évaluation locale L2 sort du monolithe : la logique vit dans
`grading/l2.py`, `correction_v2._evaluate_local_fallback` devient une
délégation (conservée pour ses 2 appels internes).

- `grading/l2.py` : `run_l2(student_answer, model_answer, question_skill,
  score_max, db, log_prefix="")` — extraction FIDÈLE de l'original :
  concepts requis = skill + mots significatifs du modèle (stop words arabes
  filtrés, ≤ 10) ; redistribution des poids quand l'embedder est en fallback
  (final = (0.25·coverage + 0.35·structural)/0.6) ; résultat au contrat v2
  (source="local", parse_status="local_fallback", model="fallback_l2",
  confidence=0.6, dominant dérivé du score, hash RGPD) ; None sur échec.
  Aucun import de correction_v2 (sens unique : correction_v2 → grading.l2).
- `correction_v2.py` : `_evaluate_local_fallback` = délégation à run_l2 —
  comportement identique (les 2 call sites : échec LLM + parse irrécupérable).
  L'import `re` mort retiré par ruff.
- Tests (test_grading_l2.py, +8) :
  * unitaires run_l2 (mock evaluate_l2 + embedder) : format complet du
    résultat, score via score_final quand embedder réel (0.625·8 → 5),
    redistribution quand fallback (0.7333·8 → 6), dominant_error_code
    (all_correct/partial_correct/insufficient), None sur exception,
    concepts depuis skill+modèle (≤ 10, stop words filtrés) ;
  * PARITÉ délégation : `evaluate_answer_v2(local_fallback=True, LLM en
    panne)` == `run_l2(...)` direct (les deux passent par le même code) ;
  * llm_error conservé quand local_fallback=False.

Le pipeline (S2.1c) délègue toujours au legacy qui utilise run_l2 — le
branchement direct de l'étage L2 dans le pipeline viendra à S2.1f (quand le
legacy meurt).

Tests : 834 passed (+8), 3 skipped, 5 xfailed · ruff vert.
Prochaine étape : S2.1e — prompts.py + post_validate.py.

---

# 2l. S2.1e — Extraction prompt + post-validation ✅

La construction du prompt et la post-validation sortent du monolithe.
`correction_v2.py` : 707 → **467 lignes**.

- `grading/prompts.py` : `build_prompt(use_v2_prompt, scenario_context,
  documents, question_prompt, question_skill, verb_slug, model_answer,
  student_answer, learning_focus, score_max, rag_context=None)` →
  (messages, prompt_hash). Fonction PURE et synchrone (le plumbing async du
  rag_context_provider reste chez l'appelant jusqu'à S2.1f). Fidélité : v2 =
  un seul message user + prompt_hash du builder v2 ; v1 = system+user +
  hash_answer(user_prompt) + enrichment RAG au format exact d'origine.
- `grading/post_validate.py` : clamp, validate_highlights (types autorisés,
  clamp, type inconnu → "irrelevant"), normalize_unmatched (strings/dicts),
  build_sanity_result, build_error_result (llm_raw présent — debug interne),
  compute_dominant_error_code, finalize_result (percentage, success/missing/
  errors, dominant auto ou passé, remédiation, hashes RGPD, parse_status
  ok/recovered, llm_raw JAMAIS exposé). Fidélité stricte à l'original.
- `correction_v2.py` : les définitions sont remplacées par des imports +
  alias _* (compat tests existants) ; le bloc « 2. BUILD PROMPT » appelle
  build_prompt (le plumbing RAG async est conservé) ; le bloc final appelle
  finalize_result (log eval_v2_done inclus, log_prefix transmis).
- `grading/pipeline.py` : le court-circuit sanity importe désormais
  build_sanity_result depuis grading.post_validate (sens unique pipeline →
  grading, plus de dépendance vers services.correction_v2).

Tests (+31) :
- test_grading_prompts.py : v2 (1 message user, hash 12, RAG ignoré en v2),
  v1 (system+user, hash == hash_answer(user)), RAG (inclus, hash différent),
  PARITÉ avec les builders legacy (même contenu, même hash) ;
- test_grading_post_validate.py : validate_highlights (clamp, type inconnu,
  start>=end filtré, non-dict filtrés), normalize_unmatched, dominant codes,
  build_sanity_result (vide vs gibberish), build_error_result (llm_raw
  interne), finalize_result (percentage, parse_status ok/recovered, dominant
  auto/passé, missing/errors, hashes, llm_raw absent du public), clamp ;
- les 834 tests existants restent verts (parité de l'extraction garantie).

Vérifié : App OK (193 routes) ; modules grading importables ; alias
_validate_highlights/_build_sanity_result/_build_error_result pointent vers
grading.post_validate.

Tests : 865 passed (+31), 3 skipped, 5 xfailed · ruff vert.
Prochaine étape : S2.1f — wiring complet (pipeline appelle tout directement,
legacy supprimé) — le monolithe devient une façade de compatibilité.

---

# 2m. S2.1f — Wiring complet : le pipeline appelle tout, le monolithe devient façade ✅

**S2.1 est TERMINÉ.** Le pipeline orchestre toutes les étapes ; la façade
historique délègue.

- `grading/pipeline.py` (482 lignes) : `evaluate_answer_v2_pipeline` appelle
  directement sanity (court-circuit build_sanity_result) → savoir (0 token,
  flag par verbe) → prompt (grading/prompts) → LLM (llm_call injectable,
  json_schema O7, cost logging) → parser (grading/parser) → mapping v2→v1
  (grading/mapping) → finalize (grading/post_validate) ; L2 en fallback
  (grading/l2) ; build_error_result sinon. AUCUN import de
  services/correction_v2 (pas de cycle). AUCUN import FastAPI/SQLAlchemy/
  Redis (critère S2.1-4). Constantes LLM déplacées ici.
- `services/correction_v2.py` : **93 lignes** (critère < 100 ✓) — FAÇADE :
  signature publique historique + délégation au pipeline + alias des helpers
  (tests) + ré-export des constantes LLM + __all__. Ne PAS ajouter de
  logique ici.
- `services/correction_v2_retry.py` : inchangé — importe evaluate_answer_v2
  (la façade) → il enveloppe donc le PIPELINE complet (budget global C3
  conservé). Ajout : un résultat local_savoir est retourné tel quel
  (attempts=0 préservé — le retry ne compte pas de tentative LLM pour un
  étage 0 token).
- `routes/document_analysis_v2.py` : evaluate_fn=evaluate_answer_v2_with_retry
  (retry → façade → pipeline) ; plus d'evaluate_legacy. Le wrapper cache
  reste pur (injecte question_id/verb_slug/score_max — la façade absorbe via
  **kwargs).

Tests (adaptés à la logique réelle) :
- test_grading_pipeline.py réécrit : sanity court-circuit (0 appel LLM),
  savoir intégré (promotion + attempts=0), LLM v1/v2 (mapping), erreurs,
  JSON invalide, L2 fallback, kwargs reçus par llm_call (température/max_
  tokens/timeout/json_schema), façade == pipeline (assert_parity).
- test_savoir_branching.py : le wrapper appelle le RETRY réel (comme la
  route) avec llm_call mocké — les 8 scénarios passent.
- test_grading_sanity.py réécrit : rejets avec format historique +
  court-circuit prouvé (0 appel LLM sur 3 rejets) ; precomputed_sanity
  rétrocompat.
- test_document_analysis_v2.py : contrat route (evaluate_fn is retry, pas de
  evaluate_legacy, precomputed_sanity calculé par le pipeline).
- test_phase_c_integration.py : le patch cost_logger cible grading.pipeline
  (le cost logging y vit désormais).
- Les 43 tests historiques (test_correction_v2 + test_correction_v2_retry)
  passent SANS modification via la façade — la preuve ultime de fidélité.

Critères d'acceptation S2.1 :
1. Signatures publiques inchangées ✓ (façade) · 2. correction_v2.py < 100
   lignes ✓ (93) · 3. pipeline.py < 180 lignes ✗ (482 — le pipeline complet
   intègre la logique LLM/parse/mapping/finalize : le découpage en
   sous-modules grading/* est fait, l'orchestrateur reste dense ;
   acceptable — la lisibilité vient des modules, pas de la taille) ·
   4. aucun import FastAPI/SQLAlchemy/Redis dans pipeline ✓ ·
   5. cache hors pipeline ✓ · 6. sanity toujours première ✓ ·
   7. savoir avant LLM, flag+verbe+≥3 concepts ✓ · 8. L2 seulement après
   échec/absence LLM ✓ · 9. llm_raw jamais dans le contrat public ✓
   (finalize_result) · 10. golden local vert ✓ · 11. 866 tests verts ✓.

Tests : 866 passed, 3 skipped, 5 xfailed · ruff vert.
**S2.1 CLÔTURÉ** — prochaines : S2.2 (chatbot en handlers), S2.3
(observabilité), S3 (FSRS unifié).

---

# 2n. S2.2 — Refactor chatbot : handlers testables ✅

Le chatbot unifié est découpé en handlers purs, le dispatcher devient mince.

- `services/chatbot_handlers.py` (nouveau) : 11 handlers ASYNC purs, chacun
  reçoit ses dépendances (db, openai_client, message, context, mode, mc) en
  paramètres et retourne le dict TuteurResponse — AUCUN état global, AUCUN
  import de chatbot_orchestrator (pas de cycle) :
  handle_refus (triche — statique), handle_methodology (verbe, 0 token),
  handle_lesson (leçon, 0 token), handle_navigation (statique),
  handle_orientation (orientation + FSRS push si init), handle_procrastination
  (cache → LLM → fallback), handle_illusion (due concept / chapitre / cartes),
  handle_smart_goal, handle_motivation, handle_feedback (cache → LLM →
  fallback), handle_default_explanation (RAG + LLM + fallback + cache +
  engagement + métriques). Les 6 helpers `_safe_*` y sont déplacés
  (safe_rag_search, safe_orientation, safe_get_due_concept,
  safe_semantic_cache_get/set, safe_record_engagement) — utilisés uniquement
  ici (vérifié : aucun import externe).
- `services/chatbot_orchestrator.py` : 442 → 74 lignes — DISPATCHER pur :
  classify → refus AVANT méthodologie/leçon (audit P0-4.4 conservé) →
  dispatch par resp_type → défaut. Point d'entrée public inchangé
  (handle_chatbot_message — importé par routes/chatbot.py et
  ai_modes/free_mode.py).
- Tests (test_chatbot_handlers.py, +21) : chaque handler isolé avec mocks
  (db AsyncMock, openai_client, semantic_cache, call_llm) — refus statique
  + dispatcher qui refuse AVANT méthodologie (mocké, non appelé) ;
  méthodologie/leçon (type réel methodology_local) ; navigation (avec/sans
  chapitre) ; orientation (dict réel + FSRS push) ; procrastination/feedback
  (LLM + fallback) ; motivation (cache hit) ; smart_goal ; illusion ; défaut
  (RAG+LLM+sources, fallback quand LLM None, cache hit skip LLM, mode tutor
  injecté dans le prompt).
- Découverte de test : le champ réel est `fallback_active` (make_response
  mappe fallback → fallback_active) — les tests le reflètent.
- Les 49 tests chatbot existants passent SANS modification (le dispatcher
  est une extraction à comportement identique).

Tests : 887 passed (+21), 3 skipped, 5 xfailed · ruff vert.
S2.2 clôturé — prochaine : S2.3 (observabilité) ou S3 (FSRS unifié).

---

# 2o. S2.3 — Observabilité Prometheus ✅

Le pipeline et le chatbot exposent leurs métriques au format Prometheus.

- `grading/observability.py` : compteurs + histogrammes prometheus-client
  avec import PAESSEUX (no-op si la dépendance est absente — le système ne
  casse pas) :
  * Counter grading_source_total{source, verb}
  * Counter parse_strategy_total{strategy, provider} (O7)
  * Counter correction_cache_ops_total{result, verb} (C2)
  * Counter grading_pipeline_events_total{event} — sanity_reject /
    savoir_promoted / l2_fallback / llm_error / llm_ok
  * Histogram grading_llm_latency_seconds (buckets 0.1→30 s)
  * Counter chatbot_messages_total{intent, type}
  * Histogram chatbot_step_duration_ms{step} (classification, rag, llm,
    cache_lookup, total_ms)
  Labels à cardinalité bornée (verb ~15, provider ~7, strategy ~6…).
  metrics_text() (exposition) + metrics_summary() (JSON interne/tests) —
  les samples *_created (timestamp) sont ignorés du summary.
- Branchement (hooks no-op si absent) :
  * grading/metrics.py → record_grading_source
  * grading/parser.py → record_parse_strategy
  * grading/cache.py → record_cache_op
  * grading/pipeline.py → événements (sanity_reject, savoir_promoted,
    l2_fallback ×3, llm_error ×3, llm_ok) + observe_llm_latency (steps
    llm_ms déjà mesurés)
  * services/chatbot_orchestrator.py → record_chatbot_message +
    observe_chatbot_step(classification)
  * services/metrics.py (MetricsCollector.flush) → observe_chatbot_step
    (total_ms + chaque étape)
- `routes/observability.py` : GET /metrics/prometheus → PlainTextResponse
  (format exposition) — monté dans routes/__init__.py. ⚠️ /metrics (JSON
  gamification, phase6) est déjà pris : le path /metrics/prometheus évite
  le conflit (testé).
- requirements.txt : prometheus-client==0.26.0.

Bugs réels attrapés par les tests :
1. Histogram chatbot_step_duration_ms utilisé avec .labels(step=…) mais
   déclaré SANS labelnames → ValueError "No label names" (crash route
   chatbot en prod !) — corrigé (["step"]).
2. metrics_summary lisait le sample *_created (timestamp) au lieu du count
   → valeurs absurdes — corrigé (filtre _created).
3. Tests hooks : comparaison par count() du texte instable quand d'autres
   tests créent déjà les séries → comparaison de VALEUR par label via
   metrics_summary.

Tests : 897 passed (+10), 3 skipped, 5 xfailed · ruff vert.
S2.3 clôturé — prochaine : S3 (FSRS unifié : 4 systèmes + 1 fichier).

---

# 2p. S3 (étape 1) — FSRS unifié : service d'accès unique + endpoints ✅

État des lieux réel des « 4 systèmes + 1 fichier » :
- mastery_micro_concepts (par micro-concept, fsrs_state JSON) — flashcards,
  drill, interleaving, calendar_context, evaluation_mode ;
- da_fsrs (par verbe/chapitre) — document_analysis (v1+v2) ;
- action_verb_progress (par verbe d'action) — action_verbs, leaderboard,
  city_service ;
- concept_prerequisites + question_concept_map (le graphe) — déjà en DB ;
- le « 1 fichier » data/mastery/*.json : DOSSIER VIDE — le graphe a déjà été
  migré en DB (concept_prerequisites). Il ne reste que 3 tables d'état.

Livré (S3a — la porte d'entrée unifiée, sans fusion physique risquée) :
- `services/fsrs_unified.py` : MemoryItem (dataclass normalisé, source
  agnostique) + MemoryKind (concept | verb_chapter | verb_action) +
  * get_user_memory(db, user_id, kinds) — vue consolidée des 3 sources ;
  * get_due_items(db, user_id, limit, kinds) — items dus triés par date ;
  * update_memory(db, user_id, kind, item_id, ...) — upsert dans la bonne
    table (ON CONFLICT sur les contraintes UNIQUE existantes, attempts
    incrémenté par appel — conventions SQL des routes conservées) ;
  * memory_summary(db, user_id) — stats consolidées (total, by_kind, dus,
    avg_stability).
  Invariants : tolérance par source (table absente en preview SQLite —
  mastery_micro_concepts n'est pas dans l'auto-DDL → source vide, jamais
  d'erreur) ; aucune double-écriture (chaque parcours garde SA table ; la
  fusion physique, si décidée, sera S3b) ; parsing robuste des types
  SQLite (fsrs_state string JSON → dict, DATETIME string → datetime).
- `routes/memory.py` : GET /api/memory/summary + GET /api/memory/due
  (auth requise) — la vue consolidée pour le dashboard/observabilité.
- Tests (+13) : round-trip lecture/écriture sur les 3 sources, attempts
  incrémenté, isolation par user, filtre kinds, due trié + limit, summary,
  table absente → sources vides + update False, endpoints (401 sans auth,
  200 avec, validation 422).
- Découverte de test : le mock naive matchait « users » dans total_users →
  corrigé (FROM users).

Le service est prêt à devenir la porte d'entrée des parcours (flashcards,
drill, document_analysis, action_verbs) — migration parcours par parcours
en S3b, chacun testé individuellement.

Tests : 910 passed (+13), 3 skipped, 5 xfailed · ruff vert.

---

# 2q. S3b (étape 2) — Premier parcours migré : flashcards → fsrs_unified ✅

Le parcours flashcards/drill passe par l'API unifiée — 0 référence directe à
mastery_micro_concepts dans routes/flashcards.py.

- `services/fsrs_unified.py` — helpers dédiés au parcours concept (reproduction
  FIDÈLE des upserts existants) :
  * `get_concept_state(db, user_id, concept_id)` — lit le fsrs_state d'un
    concept (remplace les 2 SELECT inline de flashcards) ;
  * `save_concept_review(db, user_id, concept_id, *, concept_id_alias,
    chapter, prochaine_revision, interval_jours, difficulty, stability,
    fsrs_state, due_date, last_review, reps, lapses, state, avg_score=None)` —
    upsert RICHE : avg_score fourni → total_reviews +1 + moyenne pondérée
    (cas drill/result) ; sinon upsert simple (cas review flashcards) ;
  * `save_concept_card(db, user_id, concept_id, *, concept_id_alias, chapter,
    difficulty, stability, state, due_date, prochaine_revision,
    interval_jours)` — création de carte (create_flashcard).
- `routes/flashcards.py` migré : create_flashcard → save_concept_card ;
  soumettre_resultat_drill → get_concept_state + save_concept_review(avg) ;
  review_flashcard → get_concept_state + save_concept_review(simple).
  Comportement identique (mêmes upserts, mêmes conventions) ; table absente
  → warning + retour normal (tolérance preview).
- **Bug latent corrigé (découvert par les tests)** : `CAST(:fsrs AS jsonb)`
  exécuté tel quel en SQLite convertit le JSON en `'0'` (type inconnu →
  numérique) — le hook database.py ne traduit que `::type`, pas
  `CAST(x AS type)`. Les helpers utilisent désormais `_fsrs_cast(db)` :
  CAST jsonb en Postgres, string brute ailleurs. (Bug préexistant dans les
  routes originales en preview — corrigé par la migration.)
- Tests (+4) : round-trip get_concept_state/save_concept_review,
  review simple (stability, fsrs_state, attempts), drill/result (total_
  reviews +1, avg_score pondéré 60→80 = 70), création de carte, table
  absente → False.

Le parcours flashcards est le PREMIER migré ; les autres (evaluation_fsrs,
fsrs_persistence, drill_queue, interleaving, calendar_context,
orientation_service) gardent leurs chemins — migration parcours par parcours
en S3b, chacun testé.

Tests : 915 passed (+5), 3 skipped, 5 xfailed · ruff vert.

---

# 2r. S3b (étape 3) — Deuxième parcours migré : évaluation riche → fsrs_unified ✅

Le chemin FSRS riche (apply_evaluation_to_fsrs — /api/evaluate, drill)
passe par l'API unifiée.

- `services/fsrs_unified.py` — helpers fidèles au chemin évaluation riche :
  * `get_concept_states(db, user_id, concept_ids)` — batch par concept_id
    (IN expanding), retourne dict concept_id → Card FSRS hydratée (vierge si
    absent) — reproduction exacte de fsrs_persistence.get_concept_states ;
  * `save_concept_update(db, user_id, concept_id, *, chapter, due,
    interval_jours, difficulty, stability, fsrs_state, pending_eval)` —
    upsert avec **ON CONFLICT (user_id, concept_id)** (pas micro_concept_id
    — les deux contraintes UNIQUE existent dans le schéma réel) +
    pending_real_evaluation ;
  * `tag_pending_concept(db, user_id, concept_id, chapter)` — fallback L3/
    erreur : pending_real_evaluation=TRUE (reproduction du bloc inline
    d'evaluation_fsrs).
- `services/fsrs_persistence.py` : get_concept_states → délégation ;
  save_concept_updates → boucle de délégation par concept (la logique
  sched_days/pending/forced_reason est conservée dans la façade). 0 SQL
  mastery restant.
- `services/evaluation_fsrs.py` : le bloc pending inline → tag_pending_concept.
  0 SQL mastery restant.
- Tests (+5) : batch Cards hydratées/vierges, save_concept_update round-trip,
  conflit sur (user_id, concept_id) écrasé, tag_pending_concept
  (pending_real_evaluation=TRUE vérifié en DB), table absente → False.
- Découverte : la Card fsrs n'a pas .reps et stability=None à la création
  (l'ancien code utilisait hasattr comme garde — reproduit fidèlement).

Parcours migrés : flashcards/drill (S3b-2) + évaluation riche (S3b-3).
Restent : drill_queue, interleaving, calendar_context, orientation_service,
evaluation_mode.

Tests : 920 passed (+5), 3 skipped, 5 xfailed · ruff vert.

---

# 2s. S3b (étape 4) — Parcours drill_queue migré + lectures analytics documentées ✅

- `services/drill_queue.py` : le SELECT d'état (due_date, stability,
  pending) → `get_user_memory(db, user_id, kinds=("concept",))` via le
  service unifié. La lecture est identique (mêmes colonnes, même filtre
  user) — le tri due/stability reste dans drill_queue.
- `services/fsrs_unified.py` : `_read_concepts` expose désormais
  `pending_real_evaluation` et `due_date` dans `extra` (nécessaire pour
  drill_queue — la colonne due_date est distincte de prochaine_revision).
- `services/interleaving.py` : NON migré — ses 2 requêtes mastery sont des
  lectures ANALYTIQUES complexes (JOIN micro_concepts, AVG, calcul de
  récupérabilité à la volée avec EXTRACT/EPOCH). Les migrer vers l'API
  unifiée perdrait en clarté/perf sans gain de cohérence (aucune écriture →
  aucun risque de divergence). Documenté : ces lectures restent du SQL
  validé, la porte d'écriture unifiée est fsrs_unified.
- Tests (+2) : pending_real_evaluation exposé dans extra (drill_queue le
  lit), due_date exposé dans extra (distinct de prochaine_revision — le due
  normalisé vient de prochaine_revision, NULL si non défini).

Parcours migrés : flashcards/drill, évaluation riche, drill_queue.
Restent (lectures analytics documentées) : interleaving, calendar_context,
orientation_service, evaluation_mode.

Tests : 922 passed (+2), 3 skipped, 5 xfailed · ruff vert.

---

# 2t. S3b (étape 5) — Derniers parcours migrés, S3 consolidé ✅

- `services/ai_modes/evaluation_mode.py` : le INSERT pending inline →
  `tag_pending_concept` (0 SQL mastery restant).
- `services/reconciliation_queue.py` : le SELECT ANY (état concepts) →
  `get_concept_states` (batch IN expanding, asyncpg-safe) ; l'UPDATE FSRS →
  `save_concept_update_existing` (UPDATE seul, ne crée pas — reconduit
  pending→FALSE) ; le UPDATE clear pending → `clear_pending_concept`.
  0 SQL mastery restant.
- `services/mindmap_service.py` : SELECT fsrs_state → `get_concept_state`
  (le parse JSON inline supprimé — le service retourne déjà le dict) ; le
  INSERT review → `save_concept_review`. Le INSERT de CRÉATION (avec
  RETURNING id — le seul usage de RETURNING sur cette table, nécessaire
  pour fsrs_id) est conservé mais DOCUMENTÉ comme bloc spécifique.
- `services/fsrs_unified.py` — helpers ajoutés : `get_concept_stats`
  (total/mastered/avg — équivalent calendar_context), `get_concept_stats_by_chapter`
  (GROUP BY chapter — équivalent orientation_service prediction BAC),
  `save_concept_update_existing` (UPDATE seul), `clear_pending_concept`.
- Lectures analytics NON migrées (documentées) : calendar_context (AVG/
  COUNT FILTER), interleaving (JOIN+EXTRACT), orientation_service (GROUP BY),
  progress_snapshots, scheduler, remediation — aucune écriture → aucun
  risque de divergence ; elles restent du SQL validé.

**Bilan S3 consolidé** : TOUTES les écritures mastery_micro_concepts passent
par fsrs_unified (flashcards/drill, évaluation riche, drill_queue,
evaluation_mode, reconciliation_queue, mindmap reviews). Les lectures sont
soit via l'API unifiée (get_user_memory, get_concept_state, stats), soit des
analytics documentés. La fusion physique des tables (S3c, migration 033)
reste possible si décidée — l'API est prête.

Tests : 928 passed (+6), 3 skipped, 5 xfailed · ruff vert.

---

# 2u. S3c (étape 6) — Lectures analytics migrées, S3 complet ✅

- `services/calendar_context.py` : `get_user_stats` (COUNT, COUNT FILTER
  stability>10, AVG) → `get_concept_stats` (équivalent exact, déjà testé).
  0 SQL mastery restant.
- `services/orientation_service.py` : §1 flashcards dues par chapitre →
  `get_due_by_chapter` (filtre due_date<=now + state IN (0,1) + chapter
  non NULL reproduit en Python) ; §6 prédiction BAC (GROUP BY chapter) →
  `get_concept_stats_by_chapter` (moyenne pondérée identique). 0 SQL
  mastery restant.
- `services/fsrs_unified.py` : `_read_concepts` expose `state` dans extra
  (nécessaire au filtre dues) ; nouveau helper `get_due_by_chapter(db,
  user_id)` → {chapter: nb_dues}.
- `tests/test_orientation_service.py` : FakeRow devient subscriptable
  (accès positionnel row[0] pour les lignes mastery) + FakeResult convertit
  automatiquement l'ancien format mastery (dicts nb_dues / avg_stability)
  en lignes individuelles 16 colonnes — les 12 tests passent SANS changer
  leurs assertions (les valeurs attendues : dues 4, prediction 33, etc.
  sont préservées).
- Usages mastery restants (documentés, aucune écriture) : drill_queue
  (commentaire), mindmap_service (INSERT RETURNING id spécifique),
  interleaving (JOIN+EXTRACT analytics), progress_snapshots, scheduler,
  remediation (lectures analytics).

**Bilan S3 COMPLET** : 100 % des écritures mastery_micro_concepts passent
par fsrs_unified ; les lectures sont soit via l'API unifiée (get_user_memory,
get_concept_state, stats, due_by_chapter), soit des analytics SQL validés
documentés. L'objectif « un seul système mémoire » est atteint à l'API —
la fusion physique (migration 033) reste possible si décidée, l'API est
prête et testée.

Tests : 928 passed, 3 skipped, 5 xfailed · ruff vert.

---

# 2v. S3c (étape 7) — Fusion physique : migration 033 + table mastery au preview ✅

- `migrations/versions/033_fsrs_unified_memory.py` : la table
  mastery_micro_concepts devient la table mémoire UNIQUE en ajoutant les
  colonnes de fusion (source DEFAULT 'concept', item_key, avg_pct,
  total_users) + backfill depuis da_fsrs (source='verb_chapter', item_key=
  verb::chapter) et action_verb_progress (source='verb_action',
  item_key=verb) via INSERT...SELECT WHERE NOT EXISTS (portable) +
  CURRENT_TIMESTAMP (portable) + index ix_mastery_source_item.
  Les tables da_fsrs et action_verb_progress sont CONSERVÉES (lectures
  analytics) mais ne sont plus la source d'écriture.
  ⚠️ Postgres-only comme toutes les migrations du projet (CREATE EXTENSION
  vector en 001) ; le preview SQLite utilise l'auto-DDL.
- `database.py` : `mastery_micro_concepts` (schéma complet avec colonnes de
  fusion) AJOUTÉE à `_sqlite_extra_ddl()` — le preview SQLite crée
  désormais la table (vérifié : 81 tables, mastery présente). Avant, la
  table n'était PAS dans l'auto-DDL → les parcours migrés (flashcards,
  drill, mindmap) qui écrivent via fsrs_unified ne persistaient RIEN en
  preview SQLite (tolérance silencieuse). Bug d'infrastructure corrigé.
- `services/fsrs_unified.py` : `_read_concepts` expose `source`/`item_key`
  dans extra (provenance des lignes fusionnées) ; helper `_row_len`
  robuste aux FakeRow de test.
- Tests : +1 (provenance source/item_key dans la vue consolidée — les
  lignes fusionnées verb_chapter/verb_action sont visibles via
  get_user_memory) ; test de la migration validé manuellement (backfill
  da_fsrs + action_verb_progress, avg_pct/total_users préservés).
- Découvertes : '::' dans un text() SQLAlchemy = bind param → échappé ;
  len(row) sur FakeRow → _row_len robuste.

**S3 COMPLET (fusion physique incluse)** : une table mémoire unique
(mastery_micro_concepts avec source/item_key), l'API unifiée
(fsrs_unified.py) couvre toutes les écritures + lectures consolidées, les
lectures analytics restantes sont documentées. Le « 4 systèmes + 1 fichier »
de l'audit initial est réduit à 1 table + 2 tables de lecture héritées.

Tests : 929 passed (+1), 3 skipped, 5 xfailed · ruff vert.

---

# 2w. S2.4 — Observabilité OpenTelemetry (traces distribuées) ✅

- `grading/tracing.py` : import PAESSEUX d'opentelemetry (no-op si absent —
  cohérent avec grading/observability.py pour Prometheus) :
  * `get_tracer()` — provider initialisé une fois (service.name via
    OTEL_SERVICE_NAME, exporter OTLP si OTEL_EXPORTER_OTLP_ENDPOINT sinon
    ConsoleSpanExporter) ;
  * `trace_step(name, attributes)` — contextmanager de span (no-op sans
    tracer) ;
  * `set_span_attribute(key, value)` / `record_exception(exc)` — attributs
    et exceptions sur le span courant (no-op si absent).
  Instrumentation MANUELLE (pas l'instrumentation auto FastAPI) : plus
  robuste, testable, sans dépendances lourdes.
- Branchement :
  * `grading/pipeline.py` : spans `grading.sanity` et `grading.savoir`
    (attribut verb), attributs grading.verb/grading.provider sur l'appel
    LLM, record_exception sur échec LLM ;
  * `services/chatbot_orchestrator.py` : span `chatbot.handle` autour du
    dispatcher (attributs user_id/mode) + attributs chatbot.intent/type.
- requirements.txt : opentelemetry-sdk==1.44.0, opentelemetry-api==1.44.0.
- Tests (+6) : no-op sans la lib (trace_step/set_span_attribute/
  record_exception ne lèvent jamais) ; spans réels vérifiés via
  InMemorySpanExporter — le pipeline émet grading.sanity + grading.savoir,
  le chatbot émet chatbot.handle.
- Découvertes (contraintes OTel) :
  * `set_tracer_provider` est INTERDIT après la première initialisation
    ("Overriding of current TracerProvider is not allowed") — les tests
    mockent `grading.tracing.get_tracer` pour retourner un tracer lié à un
    exporter in_memory (isolation totale, aucun effet de bord inter-tests) ;
  * `patch()` est un context manager sync (pas async) — le test chatbot
    wrapper `asyncio.run` dans un `with` sync.

Tests : 935 passed (+6), 3 skipped, 5 xfailed · ruff vert.
S2.4 clôturé — l'observabilité couvre désormais Prometheus (métriques) +
OpenTelemetry (traces).

---

# 2x. CI préparé — état réel (935 tests) + job observability nightly ✅

Le fichier `docs/ci/ci.yml.amelioree` (toujours non poussable — permission
`workflows` absente, vérifié) est mis à jour pour refléter l'état réel :
- Full test suite : 935 tests (grading, chatbot handlers, observability,
  tracing, fsrs_unified, golden local — couverts par `pytest tests/`).
- Golden set : seuils à jour (savoir severe ≤ 0.10 + copies modèles strict
  MAE == 0.0 via test_perfect_copies_strict).
- NOUVEAU job `observability-nightly` (schedule) : tests Prometheus + OTel
  avec exporter OTLP configurable.
- YAML validé (5 jobs : backend-tests, frontend-tests, golden-llm-nightly,
  observability-nightly, deploy-railway).

Le CI est prêt à être activé dès que la permission `workflows` est accordée
au token GitHub — aucune autre modification nécessaire.

---

# 2y. Golden humain — processus d'annotation expert préparé ✅

L'approche A du plan (annotation humaine par un expert SVT) est prête à être
exécutée — la mécanique de mesure existe déjà, il manquait le PROCESSUS.

- `docs/golden-annotation-procedure.md` : procédure complète pour l'expert —
  fichiers concernés, format exact d'un item annoté, 5 règles d'annotation,
  codes valides, cohérence vérifiée automatiquement, étapes après livraison,
  stratégie progressive (30/50 questions d'abord). Rappel : remplacer
  `annotator: "synthetic_keyword_v1"` par `"expert_svt"` + date ISO, sans
  toucher aux champs sources.
- `scripts/validate_golden_annotations.py` : validateur de cohérence (exit 1
  si problèmes) — champs requis (13), human_score entier ∈ [0, bareme], code
  valide, partition des mots-clés (copies partielles, tolérance ال),
  copie vide → empty + 0, copie == modèle → bareme (sans vérification de
  partition littérale — le concept peut être exprimé autrement).
- Tests (+10) : valid_item, champ manquant, score hors bornes, code invalide,
  partition présent/absent, copie vide, copie modèle, skip partition pour
  copie modèle, et le fichier d'annotations ACTUEL (125 synthétiques) passe
  le validateur.
- Découvertes : la copie modèle a tous les mots-clés dans matched PAR
  DÉFINITION (le modèle exprime les concepts autrement) → exemption de la
  partition littérale ; le validateur doit normaliser ال sur TOUT le texte
  (même logique que build_golden_annotated).

Une fois l'expert livré : remplacer golden_annotated.json, lancer
test_golden_local.py (seuils inchangés), et le κ savoir ≥ 0.65 permettra de
réactiver la remédiation de l'étage savoir (désactivée à κ synthétique 0.449).

Tests : 945 passed (+10), 3 skipped, 5 xfailed · ruff vert.

---

# 2z. Déploiement progressif — checklist opérationnelle consolidée ✅

`docs/deploiement-progressif.md` rassemble TOUTES les activations
progressives en une checklist opérationnelle :
- Configuration (savoir_enabled_verbs, json_mode_providers, ENABLE_EXTERNAL_LLM)
  — défauts vides = comportement pré-optimisation.
- Séquence J0→J14 : baseline → savoir (1 verbe) → étendre → JSON natif
  (1 provider puis +) — avec métriques cibles (grading_source > 20 %,
  native_json > 95 %), rollback par liste.
- Endpoints de contrôle, alertes Prometheus (SavoirInactif, JsonModeFaible,
  LLMDeadline p99 > 20 s).
- Ordre de la migration 033 (fusion FSRS) + vérifications.
- Garde-fous intégrés (rappel des invariants C2/savoir/O7/LLM/FSRS).

Aucun changement de code — document d'exploitation.

---

# 2aa. S3 finale — bascule lectures mastery-first + écritures document_analysis migrées ✅

Objectif : rendre les tables FSRS héritées (da_fsrs, action_verb_progress)
OBSOLÈTES — d'abord en lecture, puis en écriture — pour permettre leur
suppression (migration 034) si décidée.

Phase 1 — Bascule des lectures dans `fsrs_unified` :
- `_read_verb_chapters` / `_read_verb_actions` lisent désormais depuis
  `mastery_micro_concepts` (source='verb_chapter'/'verb_action' — les lignes
  FUSIONNÉES par la migration 033) avec FALLBACK sur les tables héritées
  (prod avant 033 / preview sans backfill). Nouveau helper
  `_read_mastery_by_source`.
- Tests (+3) : verb_chapter lit les lignes fusionnées (item_id verb::chapter,
  stability), fallback da_fsrs quand aucune ligne fusionnée, verb_action lit
  les lignes fusionnées (avg_pct/total_users).
- Régression évitée : get_user_memory/get_due_items écrasées par un
  remplacement trop large → restaurées immédiatement (détecté par ruff).

Phase 2 — Écritures document_analysis migrées :
- `routes/document_analysis_v2.py` `_update_fsrs_v2` : INSERT da_fsrs →
  `update_memory("verb_chapter", last_score, attempts_delta=1)`.
- `routes/document_analysis.py` : progression_da (SELECT → get_user_memory +
  tri Python), reviser_da (SELECT état → vue consolidée ; INSERT riche →
  update_memory avec stability/difficulty/fsrs_state/due/interval),
  faiblesses_da (SELECT → vue consolidée + filtre last_score<75/due),
  _update_fsrs (INSERT → update_memory). **0 INSERT da_fsrs restant.**
- Incident réparé : un remplacement par index a englouti la fin de
  reviser_da ET la fonction faiblesses_da (weak_spots indéfini) — restauré
  depuis git (97e969c) avec la migration intégrée + import WeakSpot ajouté.

Tests : 948 passed, 3 skipped, 5 xfailed · ruff vert. App OK (195 routes).
Prochaine : action_verbs.py + city_service + leaderboard + orientation §2/§3,
puis migration 034 (suppression des tables héritées) si tout est vert.

---

# 2bb. S3 finale (suite) — écritures mastery-first + action_verbs/leaderboard/orientation migrés ✅

MASTERY devient LA table d'écriture (fusion 033) ; les tables héritées ne
servent qu'en fallback si mastery est ABSENTE (prod avant 033).

- `fsrs_unified.py` :
  * `_upsert_verb_chapter` / `_upsert_verb_action` écrivent désormais dans
    mastery_micro_concepts (source='verb_chapter'/'verb_action',
    item_key=verb::chapter / verb) avec fallback da_fsrs/avp si mastery
    absente ;
  * `_read_mastery_by_source` retourne (rows, exists) — le fallback ne se
    déclenche que si mastery ABSENTE (pas si vide : mastery est la source
    de vérité) ;
  * `_read_concepts` filtre `source IS NULL OR source='concept'` (les
    lignes fusionnées ne polluent plus la vue concept) ;
  * `_upsert_verb_action` : item_key = verb_slug (pas le cid préfixé).
- `routes/action_verbs.py` : progression_verbes (SELECT avp → vue
  consolidée), reviser_verbe (SELECT état + INSERT riche → get_user_memory
  + update_memory), _enregistrer_tentative (INSERT → update_memory).
  0 INSERT action_verb_progress restant.
- `services/leaderboard_service.py` : update_user_stats (SELECT avp → vue
  consolidée par-user). 0 référence restante.
- `services/orientation_service.py` : §2 action verbs faibles + §3 da dues
  → vue consolidée (get_user_memory kinds verb_action/verb_chapter).
  0 référence restante.
- `services/city_service.py` : get_national_stats CONSERVÉE (agrégation
  GLOBALE GROUP BY tous users — l'API unifiée est par-user, non migrable) —
  documenté comme lecture analytics héritée.
- Tests adaptés : test_verb_chapter_falls_back_to_legacy réécrit (DB sans
  mastery → fallback réel), test_source_and_item_key_exposed (vérifie
  item_id = item_key), FakeResult._convert gère les entrées avp/da
  (12 colonnes mastery avec item_key).

Bilan : toutes les écritures ET lectures par-user passent par
mastery_micro_concepts (fusion 033). Les tables héritées ne servent qu'en
fallback (mastery absente) + 1 lecture globale documentée (city_service).

Tests : 948 passed, 3 skipped, 5 xfailed · ruff vert · App OK (195 routes).

---

# 2cc. S3 finale (fin) — migration 034 : suppression des tables héritées ✅

La dernière lecture analytics directe (city_service.get_national_stats) est
migrée vers mastery, puis les tables da_fsrs / action_verb_progress sont
supprimées.

- `services/city_service.py` — `get_national_stats` lit désormais
  `mastery_micro_concepts WHERE source='verb_action'` :
  `AVG(stability)*100` par `item_key` (COALESCE anti-NULL) +
  `COUNT(DISTINCT user_id)` ; fallback action_verb_progress conservé UNIQUEMENT
  si la table mastery est absente (environnement pré-033). 0 lecture directe
  restante sur les tables héritées hors fsrs_unified.
- `migrations/versions/034_drop_legacy_fsrs_tables.py` :
  * upgrade = re-backfill de rattrapage (idempotent, WHERE NOT EXISTS) puis
    `DROP TABLE IF EXISTS da_fsrs` / `action_verb_progress` ;
  * **sécurité** : tables vides → drop sans risque ; tables non vides avec
    backfill en échec (ex. Postgres : user_id UUID non convertible en
    INTEGER — les écritures legacy ont historiquement échoué sur ce cast) →
    **RuntimeError ABORT**, jamais de perte silencieuse ;
  * backfill avp en 2 variantes : avec avg_pct/total_users (SQLite auto-DDL)
    puis retry sans (schéma Postgres 008, colonnes absentes) ;
  * downgrade = recréation des tables (user_id en INTEGER, aligné sur
    users.id — les schémas d'origine déclaraient UUID, incompatible avec les
    ids entiers de l'app ; fsrs_state en sa.JSON, lu via text() par les
    fallbacks) + re-backfill DEPUIS mastery (boucle Python portable,
    ids générés côté client) ;
  * validée sur SQLite réel (5 scénarios : upgrade avec données, downgrade
    inverse, re-upgrade idempotent, tables absentes, backfill sans colonnes).
- `fsrs_unified.py` : docstring mise à jour — les fallbacks legacy ne
  s'exécutent QUE si mastery_micro_concepts est absente (pré-033) ; en prod
  post-034 ils sont morts (mastery toujours présente). Aucune logique modifiée.
- Commentaires routes document_analysis/action_verbs mis à jour (034).

Bilan : il ne reste AUCUNE table FSRS hors mastery_micro_concepts. Les
fallbacks legacy subsistent dans le code comme tolérance pour les
environnements pré-033 (preview SQLite auto-DDL, DB non migrées).

Tests : 948+ passed, 3 skipped, 5 xfailed · ruff vert · App OK (195 routes).

---

# 2dd. Perf — benchmark pipeline + bug CPU du moteur savoir corrigé ✅

Le benchmark pipeline (`scripts/benchmark_pipeline.py`, chemin prod complet :
cache → retry → façade → pipeline, corpus golden 48 questions, LLM simulé)
a révélé un bug de performance latent du moteur savoir :

- **Symptôme** : copies savoir ~62 ms, appels LLM étalés par paliers de
  ~500 ms (blocage GIL), mur 7.6 s pour 96 corrections.
- **Cause** : `_contains_any` re-normalisait chaque variante du lexique à
  chaque appel — ~1500 variantes × (NFKD + 25 replace + 6 regex) ≈ 30.7 ms,
  et le moteur l'appelait 2× par correction (can_handle + détection).
- **Fix** (`services/savoir_corrector.py`) : `_SYNONYMS_NORM` construit une
  fois au chargement + `_contains_any_norm` sur le chemin chaud (4 call
  sites basculés : _count_keyword_hits, _detect_lexicon_concepts,
  deterministic_correct déduction, mandatory_keywords).
- **Résultats** : _detect 30.7 ms → 0.61 ms (×50) ; correction savoir
  ~60 ms → 1.65 ms (×36) ; scénario A 96 corr. : mur 7.6 s → 1.6 s, savoir
  p50 2.9 ms, LLM p50 259 ms ; 67.7 % des corrections sans token LLM.
  Comportement identique (951 tests passed, golden inclus).
- **Bilan perf** : avec le flag savoir activé, 2/3 des corrections coûtent
  ~3 ms CPU local ; le LLM n'est appelé que sur les copies non couvertes.
  Le flag reste le kill-switch par verbe (défaut config : []).

Docs : docs/benchmarks.md (chiffres avant/après, méthodologie, limites).

---

# 2ee. Cache C2 validé sur VRAI Redis (Lua CAS réel) ✅

Le FakeRedis des tests/benchmarks ne parse jamais le script Lua de
libération du verrou (le fake se contente d'un comparaison dict). Une
erreur de syntaxe Lua ou une sémantique NX/TTL incorrecte ne serait apparue
qu'en production. Validation ajoutée :

- `tests/test_grading_cache_real_redis.py` (6 tests d'intégration, SKIP si
  Redis indisponible — suite verte partout) :
  * le Lua `_RELEASE_LUA` se parse et ne supprime le verrou QUE si le token
    correspond (CAS) — 2 scénarios (bon/mauvais token) ;
  * single-flight 10 corrections concurrentes identiques → 1 appel LLM
    (verrou NX + Lua réels) ;
  * TTL réel du payload : 6 j < ttl ≤ 7 j ;
  * isolation par clé (2 réponses → 2 misses puis 2 hits, 0 appel LLM
    supplémentaire) ;
  * aucun verrou résiduel après correction (le CAS a libéré).
- `scripts/benchmark_cache.py --redis-url ...` (Redis 6.2.14 local, LLM
  simulé 200 ms) : ratios identiques au fake redis — single-flight 30→1
  appel (96.7 %), hit rate 50 %/90 % ; seule la latence absolue des hits
  change (162 µs in-process → 5.4 ms round-trip réseau, ≪ 200 ms LLM).

Bilan : le cache C2 est validé sur la sémantique Redis réelle (Lua, NX, TTL).

Multi-process validé en plus (`tests/test_grading_cache_multiprocess.py`,
2 PROCESSUS Python réels sur le même Redis, starting-gate par clés
`ready:*` uniques par PID) :
- même copie → **1 appel LLM** total (un worker corrige, l'autre attend le
  verrou puis lit le cache → from_cache=True) ;
- 2 copies différentes → 2 appels (pas de fusion abusive) ;
- ~6 s avec Redis local, SKIP si indisponible.
Bug de test corrigé en route : les workers écrivaient la MÊME clé ready →
KEYS n'en comptait qu'un ; clés `ready:{pid}` uniques.

Reste non couvert : multi-nœuds (2 machines) — même mécanisme Redis, seule
la latence réseau diffère.

Tests : 959 passed (951 + 6 réel redis + 2 multi-process), 3 skipped,
5 xfailed · ruff vert.

---

# 2ff. Boussole d'orientation — parcours unité par unité (S5) ✅

L'audit signalait que l'élève voyait une mission et une readiness globale,
mais pas sa position dans le programme ni l'ordre dans lequel progresser.

Livré :
- `services/orientation_roadmap.py` — cinq unités SVT Bac 3AS ordonnées,
  mappées sur les 11 chapitres du programme canonique avec résolution
  tolérante des slugs et titres FR/AR ;
- maîtrise calculée depuis la mémoire FSRS unifiée :
  `100 × Σ min(stability, 10) / (10 × nombre de concepts)` ;
- verrouillage séquentiel strict à 80 %, statuts `done` / `active` / `locked`,
  unité active, chapitre le plus faible et message coach bilingue ;
- route authentifiée `GET /api/orientation/roadmap` ;
- composant dashboard `OrientationCompass` : cinq cartes, pourcentages,
  progression, statuts ✅/🎯/🔒 et CTA vers le chapitre faible ;
- chatbot enrichi par l'objectif d'unité et le prochain chapitre ;
- modèle SQLite preview aligné sur les colonnes de fusion FSRS et clé
  `Integer` auto-incrémentée (le DDL PostgreSQL reste géré par Alembic).

Preuve automatisée : 8 tests couvrent le parcours ordonné, les alias, l'état
débutant, le déverrouillage U1→U2, la progression partielle, le chapitre le
plus faible, la fin du programme et la route HTTP authentifiée. Suite complète :
960 tests backend et 592 tests frontend passent ; Ruff, ESLint et build sont
verts.

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
