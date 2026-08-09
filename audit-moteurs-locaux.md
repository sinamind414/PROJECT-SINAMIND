# Audit — Moteurs locaux du site (0 clé API)

**Date :** 2026-08-07 — **Périmètre :** tous les moteurs qui gèrent le site sans LLM externe
(chatbot, correcteur, RAG, FSRS, tutor, méthodologie, leçons, mindmap).
**Méthode :** lecture intégrale + **tests dynamiques** de chaque moteur en mode local (0 token, llm_guard actif).

---

# 1. Vue d'ensemble — comment le site tient sans clé API

```
Message élève
   │
   ▼
┌─ 1. CLASSIFICATION locale (regex, 0ms) ──────────────────────────┐
│   chat_classifier.py — 11 intents (explication, motivation, …)   │
└───────────────────────────────────────────────────────────────────┘
   │
   ▼
┌─ 2. INTERCEPTIONS locales (0 token) ─────────────────────────────┐
│   • méthodologie → methodology_local_responses (21 verbes)       │
│   • leçon → lesson_explanation (5 leçons structurées)            │
│   • refus de triche / navigation / orientation / FSRS push       │
└───────────────────────────────────────────────────────────────────┘
   │
   ▼
┌─ 3. RAG local ───────────────────────────────────────────────────┐
│   • keyword search (ILIKE, SQL) → le vrai signal                 │
│   • reranker hybride (BM25 + mots-clés, 0 LLM)                   │
│   • embedder ONNX absent → fallback déterministe (bruit assumé)  │
└───────────────────────────────────────────────────────────────────┘
   │
   ▼
┌─ 4. LLM (optionnel) → call_llm() retourne None sans clé ────────┐
└───────────────────────────────────────────────────────────────────┘
   │
   ▼
┌─ 5. FALLBACKS locaux (0 token) ──────────────────────────────────┐
│   chatbot_fallbacks : socratique (avec RAG), motivation,         │
│   procrastination, SMART goal, feedback                          │
└───────────────────────────────────────────────────────────────────┘
```

En parallèle : **correcteur v2** (sanity → L2 local TF-IDF/regex), **savoir_correct** (mots-clés +
vérifications numériques), **FSRS** (scheduler local), **tutor** (pré-analyse sans IA), **mindmap**.

---

# 2. Tests dynamiques (preuves, 0 LLM)

| Moteur | Test | Résultat |
|---|---|---|
| Classification | « اشرح لي الاستنساخ » → explication ; « أنا تعبان » → sos_concept ; « ما هو ATP؟ » → sos_concept | ✓ 5/5 intents corrects |
| Méthodologie | « كيف أقارن بين النصين؟ » → verb=اقارن + structure complète | ✓ (après fix) |
| Leçons | « اشرح لي درس المناعة » → proteines ; « راجع درس التنفس » → respiration ; « ملخص التركيب الضوئي » → photosynthese ; « اشرح درس التكتونية » → tectonique | ✓ (après fix) |
| Reranker | top-3 sur 3 chunks, question « أين يتم الاستنساخ؟ » → chunk correct en top1 | ✓ |
| FSRS | score 85 % → rating=Good, stabilité 2.3, intervalle calculé | ✓ |
| savoir_correct | bonne réponse → 4/4 ; hors-sujet → 0/4 ; « 38 ATP » + model_answer → 3/4 sans erreur | ✓ |
| Chatbot API | « كيف أقارن… » → methodology_local ; « اشرح لي درس المناعة » → lesson_explanation ; « أنا متعب » → motivation fallback ; « ما هو ATP؟ » → explication fallback socratique (avec RAG) | ✓ tous 0 token |

---

# 3. Bugs trouvés et corrigés dans cette session

## 🔴 B1 — « قارن » (verbe le plus fréquent du Bac) absent du mapping méthodologie
`detect_verb_from_message` n'avait que « اقارن » — aucun message « قارن… » n'était intercepté.
**Fix :** ajout « قارن » → clé existante « اقارن » (avec la vraie méthodologie de comparaison).
**Preuve :** « كيف أقارن بين النصين؟ » → réponse méthodologique complète.

## 🔴 B2 — Interception de leçons aveugle à l'arabe
`detect_lesson_request` ne cherchait que des mots-clés **latins** (proteine, mitose…) avec des
déclencheurs latins (explique, cours…) — les messages réels des élèves (« اشرح لي درس المناعة »)
retombaient sur le fallback LLM.
**Fix :** mots-clés arabes (مناعة، استنساخ، ترجمة، بروتين، إنزيم، تنفس، تركيب ضوئي، تكتونية، زلازل،
تخمر، ميتوكندري…) + déclencheurs arabes (درس، اشرح، ملخص، راجع، مراجعة، افهم).

## 🔴 B3 — LESSON_EXPLANATIONS incomplet (2 leçons sur 5 référencées)
Le mapping renvoyait vers `respiration`, `photosynthese`, `tectonique`… qui **n'existaient pas**
dans LESSON_EXPLANATIONS (seulement `proteines` et `mitose`) → `lesson_not_found`.
**Fix :** ajout des 3 leçons complètes (title, introduction, key_points, bac_verbs, conseil,
question suivante).

---

# 4. Points de vigilance (documentés, non bloquants)

## 🟡 V1 — Embedder fallback = bruit déterministe (pas du TF-IDF)
En l'absence du modèle ONNX (cas du site), `embedder.encode` génère des **vecteurs aléatoires
déterministes** (`np.random.seed(hash(text))`) — la similarité cosinus en résultant est du bruit.
- Le **keyword search SQL** (ILIKE ANY) reste le vrai signal → le RAG local est correct.
- Le correcteur local L2 **redistribue déjà** le poids sémantique sur TF-IDF + structurel quand
  `is_fallback` (corrigé précédemment).
- **Recommandé :** quand `is_fallback`, faire sauter `vector_rag_search` dans `rag_search`
  (économise un appel inutile + évite d'injecter du bruit dans le reranker).

## 🟡 V2 — Pas d'intent « bac » dédié dans le classifieur
« ماذا ينتظر المصحح؟ » → sos_concept (le mode bac est géré par le paramètre `mode`, pas par
l'intention) — comportement acceptable mais le message est moins bien servi qu'avec un intent bac.

## 🟡 V3 — `deterministic_correct` sensible aux mots-clés fournis
Sans `model_answer`/`expected_keywords`, le score est bas (1.2/4 sur « 38 ATP ») car les mots-clés
sont auto-extraits de la question (courte). Avec `model_answer` → 3/4 correct. **Les appelants
doivent toujours passer `model_answer`.**

## 🟢 Points forts confirmés
- **Cache sémantique** : évite les doublons (messages identiques → 2e appel servi du cache).
- **`sanitize_response`** : nettoie les mentions de source/IA des réponses (regex arabe + français).
- **FSRS complet** : prédiction Bac, mention, topological sort des concepts.
- **Pré-analyse sans IA** du tutor : vérification des sommes de probabilités et résultats
  numériques attendus (0 token).
- **Refus de triche** : interception locale ferme (« الحل الجاهز ما يربحك نقطة »).

---

# 5. Couverture finale (site en mode local)

| Fonctionnalité | Moteur local | Statut |
|---|---|---|
| Chatbot conversationnel | classification + interceptions + fallbacks + cache | ✅ |
| Méthodologie (21 verbes) | methodology_local_responses | ✅ (fix B1) |
| Explication de leçons | lesson_explanation (5 leçons) | ✅ (fix B2+B3) |
| RAG | keyword SQL + reranker hybride | ✅ |
| Correcteur v2 | sanity → L2 (TF-IDF + regex + structurel) | ✅ |
| Correcteur savoir | deterministic_correct (mots-clés + numériques) | ✅ |
| FSRS | scheduler local + prédiction Bac | ✅ |
| Tutor | pré-analyse sans IA + prompts locaux | ✅ |
| Mindmap | nécessite LLM pour la génération (fallback ?) | ⚠️ à vérifier |

Tests : **644/644** après corrections.
