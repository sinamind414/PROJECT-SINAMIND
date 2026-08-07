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

# 2b. Sprint 1 (étape 1) — C2 : cache de correction exact (corr_full_exact) ✅

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
