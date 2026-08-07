# Architecture détaillée des moteurs — IA Khawarizmi Pro (niveau fonctionnel)

**Date :** 2026-08-07 — **Niveau :** fonctions, signatures, schémas DB, formats échangés, flux séquentiels.
**Principe :** chaque moteur a un mode **local déterministe (0 token)** actif par défaut, et un mode **LLM amélioré** (si `ENABLE_EXTERNAL_LLM=1` + clé).

---

# 1. Carte des fichiers (57 services + 21 modules méthodologie)

```
services/
├── chatbot_orchestrator.py      (439)  ← pilote la conversation
├── chat_classifier.py           (309)  ← 11 intents (regex arabe/français)
├── chat_prompt.py               (570+) ← 6 builders de prompts (socratique, explication…)
├── chat_service.py              (—)    ← legacy
├── chatbot_fallbacks.py         (48)   ← réponses 0 token (motivation, procrastination…)
├── chatbot_response.py          (133)  ← make_response, normalize, cartes, sources
├── semantic_cache.py            (189)  ← cache sémantique Redis (similarité cosinus)
├── rag_service.py               (246)  ← vector + keyword + merge + cache LRU
├── reranker.py                  (227)  ← BM25 + mots-clés (0 LLM)
├── embedder.py                  (148)  ← ONNX miniLM ou fallback déterministe
├── correction_v2.py             (700+) ← correcteur v2 (sanity → LLM → L2)
├── correction_v2_retry.py       (154)  ← retry transitoire
├── fallback_v2.py               (604)  ← évaluateur L2 composite
├── savoir_corrector.py          (665)  ← correcteur mots-clés/numériques (orphelin)
├── answer_sanity.py             (178)  ← anti-charabia
├── khawarizmi_engine.py         (777)  ← tutor (pré-analyse, prompts, Bloom)
├── data_loader.py               (106)  ← charge programme/annales/lexique
├── scheduler.py                 (411)  ← FSRS (intervalles, prédiction Bac)
├── fsrs_graph.py / fsrs_persistence.py / evaluation_fsrs.py  ← mémoire legacy
├── orientation_service.py       (471)  ← mission du jour, prédiction
├── aujourdhui.py                (—)    ← accueil (bac_essentials.json)
├── llm.py                       (242)  ← 7 providers + fallback
├── llm_helpers.py               (103)  ← call_llm + sanitize_response
├── llm_guard.py                 (359)  ← double opt-in + blackhole réseau
├── llm_parser.py / metrics.py / cost_logger.py / correction_audit.py
├── methodology_local_responses.py (199) ← 21 verbes, 0 token
├── lesson_explanation.py        (—)    ← 5 leçons structurées, 0 token
├── mindmap_service.py           (1067) ← mindmaps (LLM + fallbacks statiques arabes)
├── remediation_service.py       (—)    ← dominant_error_code → page du livre
├── socratic_tutor.py            (152)  ← mode indice (hint sans note)
└── ai_orchestrator.py + ai_modes/ (guided, free, evaluation) ← API /api/ai/*
```

---

# 2. Schémas de données (tables centrales)

## 2.1 `users` (auth + mémoire FSRS)
```
id INTEGER PK · email VARCHAR · password_hash VARCHAR · prenom VARCHAR ·
wilaya VARCHAR · filiere VARCHAR · plan VARCHAR('free'|'pro') ·
fsrs_config JSON · created_at · last_active
```

## 2.2 `da_scenarios` / `da_questions` (analyse de documents)
```
da_scenarios: id · slug · unit_key · title_ar · subtitle_ar · context_ar ·
              chapter_slug · dominant_skills JSON · difficulty
da_questions: id · scenario_id FK · verb_slug · level · n · title_ar ·
              skill_ar · doc_ref · prompt_ar · placeholder_ar ·
              model_answer_ar · learning_focus_ar
```

## 2.3 `da_answers` (historique des corrections — RGPD hash)
```
id · session_id · question_id · verb_slug · chapter_slug ·
answer_text = SHA-256 (jamais la copie) · score REAL · score_max REAL ·
percentage REAL · feedback_ar · success JSON · errors JSON ·
missing_markers JSON · forbidden_found JSON
```

## 2.4 `da_fsrs` (mémoire FSRS du correcteur v2)
```
id · user_id · verb_slug · chapter_slug · last_score INT ·
attempts INT · stability REAL · difficulty REAL · interval_jours REAL ·
prochaine_revision DATETIME · fsrs_state JSON · last_review
```

## 2.5 `rag_chunks` (contexte RAG)
```
id · source (livre) · chapitre · content TEXT · embedding (pgvector) ·
tokens · chunk_index · importance (critique/haute/moyenne) · metadata_json
```

## 2.6 `lesson_blocks` (leçons actives)
```
id · chapter_slug · block_type (summary/mcq/…) · sort_order · title_ar ·
body_ar · visual_hint · quick_check JSON
```

## 2.7 Tables de l'ancien monde (legacy)
```
mastery_micro_concepts (due_date, state, pending_real_evaluation)
action_verb_progress (last_score, attempts, prochaine_revision)
action_verb_streaks · user_gems · user_badges · user_streaks · duels ·
chatbot_memory · chatbot_socratic_streaks · correction_audit (hash uniquement)
```

---

# 3. Le contrat central : le dict de résultat v2

Produit par `evaluate_answer_v2` → consommé par route/DB/FSRS/frontend/audit.

```python
{
  # Identité de l'évaluation
  "source": "local"|"llm"|"llm_recovered"|"llm_v2"|"llm_retried"|"sanity"|"llm_error",
  "provider": "primary"|"local"|"none", "model": str, "finish_reason": str,
  "attempts": int, "parse_status": "ok"|"recovered"|"failed"|"local_fallback",
  # Note
  "score": int, "score_max": int, "percentage": int, "confidence": float,
  # Erreurs localisées dans la copie
  "highlights": [{"start":int, "end":int, "type":str, "message_ar":str}],
  # Critères
  "matched_criteria": [str], "unmatched_criteria": [{"criterion","why_ar","from_model_answer"}],
  "missing": [{"expected","why_ar","from_model_answer"}],
  "success": [str], "errors": [str],
  # Diagnostic + remédiation
  "dominant_error_code": str, "remediation": {"page","lesson_title","advice_ar"}|None,
  # Retour pédagogique
  "feedback_ar": str, "advice_ar": str,
  "sanity_code": "ok"|"gibberish"|"too_short"|...,
  # RGPD (jamais la copie)
  "student_answer_hash": "sha256", "llm_raw_hash": "sha256"|None,
  "prompt_hash": "sha256",
  "llm_raw": str|None   # ABSENT du contrat public (retiré cette session) — gardé en llm_error
}
```

**Codes `dominant_error_code` (ordre de priorité) :**
`gibberish` > `scientific_error` > `off_topic` > `methodology_error` > `partial_correct` > `all_correct` > `insufficient` > `unknown`.

---

# 4. Flux séquentiel détaillé — 5 parcours types

## 4.1 Parcours CHATBOT (message élève)

```
ÉLÈVE → POST /api/chatbot/ask (ou /ask/stream SSE)
   │
   ├─ 0. AUTH (JWT) + RATE LIMIT (20/h free, 100/h pro) + CACHE exact (15 min)
   │
   ├─ 1. CLASSIFICATION (chat_classifier, regex, ~0.1 ms)
   │     → intent ∈ {explication, socratique, orientation, procrastination,
   │        daily_plan, smart_goal, motivation, illusion, triche, feedback,
   │        navigation, sos_concept, init}
   │
   ├─ 2. INTERCEPTIONS LOCALES (0 token) — dans l'ordre :
   │     a. detect_verb_from_message() → méthodologie (21 verbes) → réponse locale
   │     b. detect_lesson_request()    → leçon structurée (5 leçons) → réponse locale
   │     c. triche → refus ferme
   │     d. navigation → cartes de liens
   │
   ├─ 3. CAS SPÉCIFIQUES (0 token) :
   │     orientation/init → calculer_orientation() + FSRS push (concept dû)
   │     procrastination  → prompt LLM SINON fallback_procrastination()
   │     illusion         → question de vérification (concept dû ou chapitre)
   │     smart_goal       → prompt LLM SINON fallback_smart_goal()
   │     motivation       → prompt LLM SINON fallback_motivation()
   │     feedback         → prompt LLM SINON message d'orientation
   │
   ├─ 4. CAS DÉFAUT (sos_concept / explication) :
   │     a. CACHE SÉMANTIQUE (Redis, similarité cosinus > seuil) → HIT = réponse immédiate
   │     b. RAG : _safe_rag_search()
   │          ├─ vector_rag_search (pgvector) — SKIPPÉ si embedder fallback
   │          ├─ keyword_rag_search (ILIKE ANY) — le vrai signal
   │          ├─ merge + rerank (BM25 + mots-clés) + cache LRU 5 min
   │     c. ORIENTATION contexte (prédiction Bac, dues)
   │     d. PROMPT adaptatif (chat_prompt) :
   │          explication si fsrs_stability < 3.0, sinon socratique
   │          + mode tutor (pas de réponse directe) / mode bac (points clés)
   │     e. call_llm() → SANITIZE (supprime mentions source/IA) → si None :
   │          fallback_socratique(message, rag_chunks) — cite le cours
   │     f. CACHE SÉMANTIQUE store (si pas fallback)
   │     g. ENGAGEMENT tracking (chatbot_memory, streaks)
   │     h. METRICS (classification/rag/llm/cache, latence par étape)
   │
   └─ Réponse TuteurResponse :
        { reponse, type, cartes[], sources[], question_suivante,
          flashcards_suggerees[], fallback_active, from_cache, tokens_utilises }
```

## 4.2 Parcours CORRECTION v2 (réponse d'élève notée)

```
ÉLÈVE → POST /api/document-analysis/evaluate-v2
   │
   ├─ 0. AUTH + RATE LIMIT (15/h free, 80/h pro)
   ├─ 1. ROUTE : charge scénario (da_scenarios) + documents + questions (da_questions)
   │         score_max = _compute_score_max_for_verb(verb)  (VERB_RULES, fallback 4)
   │
   ├─ 2. evaluate_answer_v2_with_retry (retry si 5xx/timeout/429)
   │     │
   │     ├─ 3. SANITY (answer_sanity, 0 token) :
   │     │      vide → empty · court → too_short · pas arabe → not_arabic ·
   │     │      répétitions → gibberish · < 4 caractères uniques → repeated_chars
   │     │      → REJET immédiat : score 0, code, message arabe, highlight rouge
   │     │
   │     ├─ 4. PROMPT v2 (correction_prompt_v2, -68% tokens) :
   │     │      scénario + docs (résumés) + consigne + verb + skill + model_answer
   │     │
   │     ├─ 5. LLM (call_llm via llm.py, 7 providers) :
   │     │      température 0.0 · max 4096 tokens · timeout 25 s
   │     │      validateur JSON (4 stratégies de parsing)
   │     │      └─ si échec / JSON illisible :
   │     │           _evaluate_local_fallback() → L2 (fallback_v2)
   │     │           TF-IDF 0.25 + structurel 0.35 + sémantique 0.40
   │     │           (si embedder fallback : sémantique redistribuée sur les 2 autres)
   │     │           → score clampé, concepts trouvés/manquants, verdict
   │     │
   │     ├─ 6. POST-VALIDATION :
   │     │      _extract_json_from_response (4 stratégies) ·
   │     │      _validate_highlights (types, clamps) ·
   │     │      _compute_dominant_error_code (priorité)
   │     │      remediation = get_remediation(verb, code) → page livre MANHADJIYA
   │     │
   │     └─ 7. RETOUR dict v2 (le contrat §3)
   │
   ├─ 8. ROUTE — consommateurs du dict :
   │     a. da_answers : INSERT (answer_text = hash SHA-256, success/errors JSON)
   │     b. da_fsrs : _update_fsrs_v2 (last_score, attempts+1) si source ≠ llm_error
   │     c. correction_audit : INSERT hash-only (jamais la copie)
   │     d. session : score_global = Σ scores / Σ max (pannes LLM exclues)
   │     e. frontend : feedback_ar + advice_ar + highlights + remediation
   │
   └─ Réponse : { session_id, score_global, evaluations[dict v2] }
```

## 4.3 Parcours ÉVALUATION LEGACY (`/api/ai/evaluate` — non appelé par le frontend)

```
   ├─ N0: check_common_mistakes() → erreur connue → verdict immédiat (0 token)
   ├─ N1: call_gpt4o_evaluator() → 7 providers + tenacity retry (3×)
   ├─ N2: evaluate_l2() → composite local
   │
   ├─ evaluation_mode :
   │     ├─ update_concept_graph()  (FSRS graph : concepts + prérequis + dépendances)
   │     ├─ save_concept_updates()  → prochaine révision
   │     ├─ needs_l1_review ? → enque_for_l1_review (worker asynchrone) :
   │     │      re-évalue avec LLM ; écart > 0.20 → correct_fsrs_scores()
   │     ├─ translate_feedback()  (feedback_translator : fr ↔ ar)
   │     └─ evaluate_methodology() (si include_methodology)
   │
   └─ normalize_result() : CORRECT→PARTIEL si manquant obligatoire, 0→FAUX
```

## 4.4 Parcours MISSION DU JOUR (`/api/aujourdhui*`)

```
GET /api/aujourdhui
   ├─ _load_mastered(user_id) → fichier JSON local (data/mastery/{id}.json)
   ├─ get_mission_du_jour() :
   │      bac_essentials.json (57 MC, 11 unités, 18 phrases clés du livre)
   │      → PREMIER MC non maîtrisé (progression linéaire) sinon MC du jour (graine hash)
   │      → QCM (phrase clé + erreurs fréquentes d'autres MC)
   │      → progress par unité (mc_total, mc_maitrise, pourcentage)
   └─ POST /api/aujourdhui/valider → met à jour le fichier mastery
```

## 4.5 Parcours MINDMAP (`/api/mindmap/*`)

```
POST /api/mindmap/generate (async) ou /generate (sync)
   ├─ LLM (si clé) : construit l'arbre JSON → validation → fallback si invalide
   ├─ fallback STATIQUE : _build_default_enfants(chapitre) → 3-5 nœuds arabes
   │      (adn, photosynthese, immuno, enzymes, respiration, tectonique…)
   │      alignés sur le programme officiel SVT 3AS
   └─ persiste mindmaps + mindmap_nodes (FSRS lié par bac_frequent)
```

---

# 5. Le moteur LLM — 7 providers et leur sélection

```
call_llm (llm_helpers) ──▶ _call_with_fallback (llm.py)
   │
   ├─ PRIMARY (config openai_base_url + OPENAI_API_KEY) :
   │     auto-détection du provider par préfixe de clé :
   │     gsk_* → Groq (llama-3.3-70b) · AIza* → Gemini (gemini-2.5-flash) ·
   │     sk-or-v1* → OpenRouter (gemini-2.5-flash) · sinon OpenAI
   │
   ├─ VALIDATEUR (response_validator) : si le JSON est illisible → fallback
   │
   └─ FALLBACKS dans l'ordre :
        1. Gemini 2.5 Flash (GEMINI_API_KEY)      — 15 req/min gratuites
        2. Cloudflare GLM-5.2 (CLOUDFLARE_API_TOKEN)
        3. Z.AI GLM-4.7 (ZAI_API_KEY)
        4. ZenMux GLM-5.2 (ZENMUX_API_KEY)
        5. NaraRouter (NARA_API_KEY)              — 5M tokens/jour gratuits
        6. OpenAI gpt-4o-mini (OPENAI_FALLBACK_API_KEY)
   └─ si TOUS échouent → RuntimeError → le moteur local prend le relais

llm_guard (défense en profondeur) :
   1. is_llm_enabled() = ENABLE_EXTERNAL_LLM=1 ET clé — sinon TOUT est bloqué
   2. scrub_environment() : vide les *_API_KEY au démarrage si pas de flag
   3. GuardedOpenAIClient : lève LLMDisabledError sur .create()
   4. patch openai module : AsyncOpenAI remplacé par la factory gardée
   5. blackhole httpx : les domaines LLM connus sont coupés au transport
```

---

# 6. Le cache — 4 niveaux

| Niveau | Techno | Clé | TTL | But |
|---|---|---|---|---|
| Cache exact chatbot | Redis (ou None) | md5(message+lang+mode+chapitre) | 15 min | questions identiques |
| Cache sémantique | Redis | similarité cosinus vs entrées `sem_cache:{chapitre}:*` | 24 h | questions similaires |
| Cache RAG | mémoire LRU | (message, chapitre, limit) | 5 min / 256 entrées | éviter 2× le même RAG |
| Cache programme/cours | mémoire module | — | ∞ | programme + cours markdown |

**Mode local sans Redis :** tous les caches Redis sont silencieusement désactivés
(`get_cache` retourne None) — le site fonctionne, sans économie de coût.

---

# 7. Metrics et observabilité

```
MetricsCollector (par requête) :
   { endpoint, user_id, steps: {classification_ms, cache_lookup_ms, rag_ms,
     llm_ms, total_ms}, intent, resp_type, cache_hit, fallback_active,
     rag_chunks_count, tokens_utilises }

record_request(endpoint, cache_hit, fallback) → statistiques globales en mémoire
rag_cache_stats() → hit_rate du cache RAG
cost_logger (JSONL append) : model, tokens, cost_usd, prompt_hash, verb, latency
correction_audit (DB) : hash-only, attempts, source, score, parse_status
```

---

# 8. Matrice détaillée des dépendances (qui appelle qui)

| Appelant → Appelé | Quand |
|---|---|
| chatbot_orchestrator → chat_classifier | chaque message (étape 1) |
| chatbot_orchestrator → methodology_local_responses | si verbe détecté |
| chatbot_orchestrator → lesson_explanation | si leçon détectée |
| chatbot_orchestrator → rag_service | défaut (sos/explication) |
| chatbot_orchestrator → semantic_cache | défaut (avant/après RAG) |
| chatbot_orchestrator → orientation_service | init/motivation/procrastination |
| chatbot_orchestrator → scheduler.get_due_concepts | FSRS push (init/illusion) |
| chatbot_orchestrator → llm_helpers.call_llm | tous les cas LLM (None sans clé) |
| correction_v2 → answer_sanity | avant tout |
| correction_v2 → correction_prompt_v2 | construction du prompt |
| correction_v2 → llm (via llm_call injectable) | étape 5 |
| correction_v2 → fallback_v2.evaluate_l2 | si LLM None (local_fallback) |
| correction_v2 → remediation_service | après dominant_error_code |
| document_analysis_v2 → correction_audit | après chaque évaluation |
| document_analysis_v2 → da_fsrs (_update_fsrs_v2) | après chaque évaluation |
| evaluation_mode → fsrs_graph | legacy (concept graph) |
| evaluation_mode → reconciliation_queue | si needs_l1_review |
| evaluation_mode → feedback_translator | si lang == ar |
| evaluation_mode → methodology.evaluator | si include_methodology |
| guided_mode → khawarizmi_engine (tutor) | pre_analyse + interroger_ia |
| mindmap_service → mindmap fallbacks statiques | si LLM None/invalide |

---

# 9. Cycle de vie complet d'une REQUÊTE (vue temporelle)

```
t=0      AUTH (JWT, cookie/Bearer) + RATE LIMIT
t=0.1ms  CLASSIFICATION (regex)
t=0.2ms  INTERCEPTION locale ? (verbe/leçon/triche/navigation) → réponse immédiate
t=1ms    CAS SPÉCIFIQUE ? (orientation/procrastination/…) → réponse locale
t=2ms    CACHE EXACT ? → réponse cachée
t=3ms    CACHE SÉMANTIQUE ? → réponse similaire cachée
t=5ms    RAG : keyword (SQL) + reranker → chunks
t=7ms    PROMPT construit (ou fallback direct sur les chunks)
t=10ms   LLM (si clé) — sinon None → FALLBACK LOCAL
t=11ms   RÉPONSE normalisée (TuteurResponse)
t=12ms   ENGAGEMENT + METRICS + CACHE STORE
```

**En mode local pur (0 clé API) :** la chaîne complète tient en ~10-15 ms par
message (mesuré sur les logs : `total_ms ≈ 12`), sans aucun appel externe.
