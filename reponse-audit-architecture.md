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
