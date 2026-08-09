# Architecture détaillée des moteurs — IA Khawarizmi Pro

**Date :** 2026-08-07 — **Base :** code réel lu et testé (pas de théorie).
**Périmètre :** les 12 moteurs du backend, leurs entrées/sorties, leurs communications, et un avis d'expert sur chacun.

---

# 1. Vue d'ensemble — les 5 couches

```
┌────────────────────────────────────────────────────────────────────────┐
│  COUCHE ROUTES (FastAPI, 189 endpoints)                                │
│  /api/chatbot* · /api/ai/chat · /api/ai/evaluate · /api/document-      │
│  analysis* · /api/mindmap* · /api/programme · /api/aujourdhui* · …     │
└───────────────┬────────────────────────────────────────────────────────┘
                │
┌───────────────▼────────────────────────────────────────────────────────┐
│  COUCHE ORCHESTRATION                                                   │
│  AIOrchestrator (guided/free/methodology/evaluation) ·                  │
│  chatbot_orchestrator (11 intents) · evaluate_answer_v2_with_retry ·    │
│  KhawarizmiTutor (tutor pédagogique)                                    │
└───────────────┬────────────────────────────────────────────────────────┘
                │
┌───────────────▼────────────────────────────────────────────────────────┐
│  COUCHE MOTEURS DE JUGEMENT                                             │
│  answer_sanity · fallback_v2 (L2) · savoir_correct · correction_v2 ·   │
│  methodology/evaluator · chat_classifier · fsrs_graph                  │
└───────────────┬────────────────────────────────────────────────────────┘
                │
┌───────────────▼────────────────────────────────────────────────────────┐
│  COUCHE CONNAISSANCE                                                   │
│  rag_service + reranker + embedder · data_loader (canonical ONEC) ·    │
│  fallback_programme_data · lesson_explanation · methodology_local_     │
│  responses · mindmap_service (_fallbacks statiques)                    │
└───────────────┬────────────────────────────────────────────────────────┘
                │
┌───────────────▼────────────────────────────────────────────────────────┐
│  COUCHE LLM + INFRA                                                     │
│  llm_guard (double opt-in) · llm.py (7 providers) · llm_helpers ·      │
│  cache (Redis/None) · SQLite/PostgreSQL · scheduler FSRS · worker L1   │
└────────────────────────────────────────────────────────────────────────┘
```

**Principe directeur :** chaque moteur a un mode **local déterministe (0 token)** et un mode **LLM amélioré** — le premier est actif par défaut (site sans clé API), le second seulement si `ENABLE_EXTERNAL_LLM=1` + clé.

---

# 2. Fiches détaillées des 12 moteurs

## M1 — Chatbot orchestrator (`services/chatbot_orchestrator.py`, 439 l.)
| | |
|---|---|
| **Rôle** | Pilote toute la conversation : classification → interceptions locales → RAG → LLM → fallbacks |
| **Entrées** | message, contexte (chapitre, history, fsrs), user_id, db, openai_client |
| **Sorties** | `TuteurResponse` (reponse, type, cartes, sources, question_suivante, fallback_active…) |
| **11 intents** | explication, socratique, orientation, procrastination, daily_plan, smart_goal, motivation, illusion, triche, feedback, navigation, sos_concept |
| **Dépendances** | chat_classifier, methodology_local_responses, lesson_explanation, rag_service, llm_helpers, chatbot_fallbacks, orientation_service, semantic_cache, metrics |
| **Mode local** | ✅ interceptions + fallbacks spécifiques par intent (motivation, procrastination, SMART…) |
| **Mode LLM** | prompts adaptatifs par intent (explication vs socratique, mode tutor/bac) |
| **Avis** | 🟢 **Bien conçu** — défense en profondeur : 3 étages (local → LLM → fallback) + cache sémantique. Points faibles : la détection des verbes arabes était incomplète (corrigé : قارن), et `call_llm` sans clé retombe proprement sur les fallbacks. |

## M2 — Classificateur d'intention (`services/chat_classifier.py`, 309 l.)
| | |
|---|---|
| **Rôle** | Détecte l'intention d'un message AVANT tout traitement (regex + normalisation arabe) |
| **Entrées** | message brut |
| **Sorties** | `{intent, type, is_init}` — priorité du plus spécifique au plus général |
| **Mode local** | ✅ 100 % regex, 0 ms, 0 token |
| **Avis** | 🟢 Solide et rapide. Limite : pas d'intent « bac » dédié (« ماذا ينتظر المصحح؟ » → sos_concept) — le mode bac est passé par paramètre, pas par intention. |

## M3 — Correcteur v2 (`services/correction_v2.py`, 700+ l.)
| | |
|---|---|
| **Rôle** | Pipeline complet de correction : sanity → prompt → LLM → post-validation → remediation |
| **Entrées** | scénario, documents, question, skill, verb, model_answer, score_max, copie élève, llm_call injectable |
| **Sorties** | dict v2 (score, highlights, matched/unmatched, feedback_ar, dominant_error_code, remediation, hashes RGPD) |
| **Mode local** | ✅ sanity (0 token) + **L2 local** (`_evaluate_local_fallback` → evaluate_l2) quand le LLM est bloqué |
| **Mode LLM** | prompt v2 optimisé (-68 % tokens), retry transitoire, mapping v2→v1 |
| **Avis** | 🟢 **Le meilleur moteur du projet** : parsing JSON tolérant (4 stratégies), highlights clampés, source `llm_recovered`, RGPD par hash. Points faibles : `use_v2_prompt` non activé avant cette session (corrigé), embedder fallback = bruit (compensé par redistribution des poids). |

## M4 — Évaluateur local L2 (`services/fallback_v2.py`, 604 l.)
| | |
|---|---|
| **Rôle** | Juge le fond d'une réponse SANS LLM : 3 signaux pondérés |
| **Entrées** | reponse_eleve, question_data (réponses ref, concepts requis, points clés), db |
| **Sorties** | `L2Result` (score 0-1, semantic/TFIDF/structural, concepts trouvés/manquants, verdict, needs_l1_review) |
| **Pondération** | sémantique 0.40 + TF-IDF 0.25 + structurel (regex) 0.35 |
| **Mode local** | ✅ intégral (scikit-learn, numpy) |
| **Avis** | 🟢 Robuste et calibré (seuils 0.85/0.35). **Découverte :** quand l'embedder est en fallback, le signal sémantique devient du bruit → la correction v2 redistribue déjà les poids. Recommandation : faire de même dans les appels legacy. |

## M5 — Correcteur savoir (`services/savoir_corrector.py`, 665 l.)
| | |
|---|---|
| **Rôle** | Correction déterministe par mots-clés scientifiques + valeurs numériques attendues (38 ATP…) + erreurs conceptuelles typiques |
| **Entrées** | question, réponse, points, expected_keywords, mandatory_keywords, expected_numeric, model_answer |
| **Sorties** | score/points, points_forts, erreurs (arabes), conseils |
| **Mode local** | ✅ intégral — 0 token, instantané |
| **Avis** | 🟠 **Excellent mais ORPHELIN** : aucune route ne l'appelle (seulement `scripts/audit_correcteur.py`). Tests réels : 4/4 bonne réponse, 0/4 hors-sujet, 3/4 avec model_answer, détecte « 38 ATP » faux. **C'est le meilleur juge pour les questions fermées — à brancher comme 1er étage du pipeline v2.** |

## M6 — Sanity check (`services/answer_sanity.py`, 178 l.)
| | |
|---|---|
| **Rôle** | Filtre anti-charabia AVANT tout LLM : vide, trop court (< 8), ratio arabe < 30 %, bigrammes répétés, keyboard smash |
| **Entrées** | réponse brute |
| **Sorties** | `(is_valid, code, message_ar)` — codes: empty/too_short/not_arabic/gibberish/repeated_chars |
| **Mode local** | ✅ intégral |
| **Avis** | 🟢 Essentiel et efficace (85 % couverture). Protège le budget token et la crédibilité. |

## M7 — RAG (`services/rag_service.py` + `reranker.py` + `embedder.py`)
| | |
|---|---|
| **Rôle** | Fournit le CONTEXTE pédagogique (chunks du livre) au chatbot et au correcteur |
| **Entrées** | message, chapitre, db |
| **Sorties** | chunks fusionnés (vector + keyword), rerankés (BM25 + mots-clés), formatés, sources |
| **Mode local** | ✅ keyword search SQL (ILIKE) + reranker hybride (0 LLM) ; vector search **skippé** quand embedder en fallback (corrigé cette session) |
| **Mode LLM** | embedder ONNX (miniLM) quand disponible |
| **Avis** | 🟢 Le keyword + reranker tiennent le RAG sans ONNX. Points faibles : la table `rag_chunks` est vide en preview (seeds RAG absents) → le RAG ne ramène rien en local pur ; le `ILIKE ANY` n'est pas compatible SQLite (fallback silencieux OK). |

## M8 — FSRS (`services/scheduler.py` + `fsrs_graph.py` + `evaluation_fsrs.py`)
| | |
|---|---|
| **Rôle** | Mémoire de l'élève : intervalle de révision, prédiction Bac, graphe de concepts |
| **Entrées** | Card, score_percent, historique concept |
| **Sorties** | prochain intervalle, rating (Again/Hard/Good/Easy), prédiction Bac, mention |
| **Mode local** | ✅ bibliothèque `fsrs` v4 (prouvé : score 85 % → Good, stabilité 2.3) |
| **Avis** | 🟠 **Deux sources de vérité non synchronisées** : pipeline v2 écrit `da_fsrs` (score par verbe), pipeline legacy écrit le graphe de concepts. Un élève peut avoir 2 historiques FSRS selon la page. Recommandation : migrer vers une seule table. |

## M9 — Tutor pédagogique (`services/khawarizmi_engine.py`, 777 l. + `data_loader.py`)
| | |
|---|---|
| **Rôle** | Pré-analyse sans IA (probabilités, résultats numériques), routage par niveau Bloom, prompts système, calendrier |
| **Entrées** | sujet, question, réponse élève, niveau, score, mode |
| **Sorties** | pré-analyse structurée, prompt, traitement socratique des erreurs |
| **Mode local** | ✅ pré-analyse 0 token (somme de probas, résultat numérique attendu) |
| **Mode LLM** | `interroger_ia` avec fallback providers |
| **Avis** | 🟢 Bonne idée (vérifications déterministes avant LLM). Limite : `pre_analyser_sans_ia` ne couvre que 2 types de questions (probas + numériques) — le reste dépend du LLM. |

## M10 — Moteur méthodologie (`methodology/`, 2407 l. — 21 modules)
| | |
|---|---|
| **Rôle** | Juge la MÉTHODE (pas le fond) : verbes, structure du texte, utilisation des docs, feedback, flashcards |
| **Entrées** | instruction (verbe), réponse élève |
| **Sorties** | score méthodologique, feedback, action plan |
| **Mode local** | ✅ `methodology_local_responses` (21 verbes), `evaluator.py`, `text_structure_analyzer` |
| **Avis** | 🟠 **Gros moteur sous-exploité** : `evaluate_methodology` n'est appelé que si `include_methodology=True` (optionnel). Le chatbot l'utilise via les interceptions locales (verbes), mais le correcteur v2 ne croise pas son verdict avec le fond. |

## M11 — Mindmap (`services/mindmap_service.py`, 1067 l.)
| | |
|---|---|
| **Rôle** | Génère des cartes mentales du programme |
| **Entrées** | matiere, chapitre, filiere, niveau, user, db, openai_client |
| **Sorties** | arbre de nœuds (label, type, importance) |
| **Mode local** | ✅ `_fallbacks` statiques ARABES alignés sur le programme (adn, photosynthese, immuno, enzymes, respiration, tectonique…) — 3-5 enfants par défaut |
| **Mode LLM** | génération enrichie si clé |
| **Avis** | 🟢 Le fallback statique est **scientifiquement aligné** (vérifié : labels du programme officiel). Limite : seulement ~6 chapitres couverts en local ; le reste renvoie un fallback générique. |

## M12 — Orientation / Aujourd'hui (`services/orientation_service.py` + `services/aujourdhui.py`)
| | |
|---|---|
| **Rôle** | Mission du jour, prédiction Bac, thermomètre 57 MC, fiche J-1 |
| **Entrées** | user_id, mastered (fichier JSON local), db |
| **Sorties** | mission (1 MC), quiz, progress par unité, prédiction |
| **Mode local** | ✅ 100 % déterministe (fichier JSON par user, pas de DB requise) |
| **Avis** | 🟢 Fiable et testé. Le `bac_essentials.json` généré est aligné sur le livre corrigé (57 MC, 11 unités). |

---

# 3. Matrice de communication entre moteurs

```
                    │ chat_   corr_   fallback savoir_ sanity  rag   fsrs   tutor  method  mindmap  orient
                    │ orchestr  v2      L2      correct  check              ology
┌───────────────────┼──────────────────────────────────────────────────────────────────────────
│ chatbot_orchestr  │   ●      —       —       —       ●      ●     ●      —      ●       —       ●
│ correction_v2     │   —      ●       ●       —       ●      ●(ctx) —      —      —       —       —
│ fallback_v2 (L2)  │   —      ●       ●       —       —      —     —      —      —       —       —
│ savoir_correct    │   —      (1)     —       ●       —      —     —      —      —       —       —
│ sanity check      │   ●      ●       —       —       ●      —     —      —      —       —       —
│ RAG               │   ●      ●(ctx)  —       —       —      ●     —      —      —       —       —
│ FSRS scheduler    │   —      ●(score)—       —       —      —     ●      —      —       —       —
│ KhawarizmiTutor   │   —      —       —       —       —      —     —      ●      —       —       ●
│ methodology/      │   ●(21v) ●(opt)  —       —       —      —     —      —      ●       —       —
│ mindmap_service   │   —      —       —       —       —      —     —      —      —       ●       —
│ orientation       │   ●      —       —       —       —      —     —      —      —       —       ●
```
**(1) = recommandé mais non branché** (savoir_correct orphelin).

**Contrat central :** le **dict de résultat v2** (score, dominant_error_code, unmatched_criteria, remediation, hashes) — produit par correction_v2, consommé par la route (persistance), FSRS (da_fsrs), le frontend (feedback) et l'audit RGPD.

---

# 4. Avis d'expert par axe

## 4.1 Ce qui est excellent
- **Défense en profondeur** : chaque fonctionnalité a local → LLM → fallback (chatbot, correcteur, RAG, mindmap).
- **Sanity check avant LLM** : 0 token dépensé sur du charabia.
- **RGPD** : hash systématiques (student_answer_hash), copie jamais stockée en clair.
- **Cache sémantique + RAG cache** : pas de double coût.
- **Reranker hybride 0 LLM** : le RAG tient sans ONNX ni clé.
- **Fallbacks pédagogiquement alignés** : mindmap statique arabe sur le programme, remediation → pages du livre.

## 4.2 Ce qui doit être corrigé (priorité)
| # | Problème | Impact | Effort |
|---|---|---|---|
| 1 | **savoir_correct orphelin** (meilleur juge pour questions fermées, 0 token) | notes fermées imprécises | 30 min |
| 2 | **Double FSRS non synchronisé** (da_fsrs vs concept graph) | 2 historiques élèves | 1-2 h |
| 3 | **`rag_chunks` vide en local** (aucun seed RAG) | chatbot sans sources RAG en preview | 1 h |
| 4 | **`evaluate_methodology` optionnel** | la méthode et le fond ne sont pas croisés | 30 min |
| 5 | **Intent « bac » absent** du classifieur | messages bac mal routés | 15 min |
| 6 | **`ILIKE ANY` non-SQLite** (keyword RAG) | RAG keyword cassé en preview | 30 min |

## 4.3 Verdict global
**8/10** — Architecture exemplaire pour un produit éducatif sans infrastructure LLM :
la redondance locale/LLM est la bonne décision, le contrat de résultat est stable,
le RGPD est respecté. Les faiblesses sont des **dettes d'intégration** (moteurs
excellents non branchés, double FSRS), pas des défauts de conception.

---

# 5. Architecture cible recommandée (à 6 mois)

```
                 ┌──────────────────────────────────────┐
                 │         ORCHESTRATEUR UNIQUE          │
                 │  (fusionner chatbot + correcteur +    │
                 │   evaluation_mode en 1 pipeline)      │
                 └───────────────┬──────────────────────┘
                                 │
        ┌────────────────────────┼───────────────────────────┐
        ▼                        ▼                           ▼
┌─ JUGEMENT FOND ──┐      ┌─ JUGEMENT MÉTHODE ──┐      ┌─ MÉMOIRE ──┐
│ 1. savoir_correct│      │ methodology/evaluator│      │ da_fsrs    │
│    (questions    │      │ (verbes, structure,  │      │ (UNIQUE,   │
│    fermées)      │      │  docs)               │      │  migré)    │
│ 2. L2 local      │      └───────────┬──────────┘      └─────┬──────┘
│ 3. LLM (opt)     │                  │                       │
│ 4. sanity avant  │                  ▼                       ▼
└────────┬─────────┘        ┌─ REMÉDIATION ──┐        ┌─ RÉCONCILIATION ─┐
         │                  │ page livre +   │        │ worker L1 (LLM  │
         ▼                  │ conseil arabe  │        │ opt) + correct  │
┌─ CONTRAT COMMUN ──┐       └────────────────┘        └──────────────────┘
│ dict de résultat  │
│ (score, dominant_ │
│  error, missing,  │
│  remediation,     │
│  hashes RGPD)     │
└───────────────────┘
```
**Changements clés :** (1) savoir_correct devient l'étage 1 du jugement fond ;
(2) da_fsrs unique pour la mémoire ; (3) evaluate_methodology branché en parallèle
du fond (verdict croisé) ; (4) seed RAG pour le local ; (5) un seul format de sortie
partout (le dict v2).
