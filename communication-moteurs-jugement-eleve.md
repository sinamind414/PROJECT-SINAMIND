# Comment les moteurs communiquent pour juger l'élève et ses erreurs

**Date :** 2026-08-07 — **Source :** traçage réel des appels dans le code (pas théorique).

---

# 1. Le point d'entrée : où l'élève est jugé

Il y a **2 pipelines d'évaluation** qui coexistent. Les deux jugent la même chose
(une réponse d'élève), mais avec des moteurs et des formats différents.

| Pipeline | Route | Moteur principal | Utilisé par le site actuel |
|---|---|---|---|
| **A — Correcteur v2** | `POST /api/document-analysis/evaluate-v2` | sanity → LLM optionnel → **L2 local** | ✅ le vrai (page document-analysis) |
| **B — Évaluation legacy** | `POST /api/ai/evaluate` | GPT-4o (LLM) → **L2 local** + common mistakes | ⚠️ route non appelée par le frontend, mais alimente FSRS legacy |

Le chatbot (`/api/chatbot/ask`) **ne note pas** : il explique, oriente, motive.

---

# 2. Pipeline A — le chemin complet d'une réponse d'élève (v2)

```
ÉLÈVE envoie sa réponse
        │
        ▼
┌─ ROUTE document_analysis_v2.py ────────────────────────────────────────┐
│ charge scénario + documents + question (DB da_*)                        │
│                                                                          │
│   → appelle evaluate_answer_v2_with_retry()                              │
│        │                                                                │
│        ▼                                                                │
┌─ correction_v2_retry.py ──┐      ┌─ correction_v2.py ──────────────────┐│
│ retry si erreur transitoire│────▶│ 1. SANITY check (answer_sanity.py)   ││
│ (5xx, timeout, 429)        │      │    → vide/court/charabia → rejet 0  ││
└───────────────────────────┘      │    token avec code + message arabe   ││
                                    │ 2. Prompt (v2, -68% tokens)          ││
                                    │ 3. LLM (call_llm) ── si None ──▶    ││
                                    │    _evaluate_local_fallback         ││
                                    │      → evaluate_l2 (fallback_v2.py) ││
                                    │      TF-IDF + regex + structurel    ││
                                    │ 4. Post-validation (parse, clamp)   ││
                                    │ 5. dominant_error_code + remediation││
                                    └─────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────────────┘
        │
        ▼  Le dict de résultat v2 circule ensuite vers 4 consommateurs :
        │
   ┌────┼────────────────┬───────────────────┬──────────────────────┐
   ▼    ▼                ▼                   ▼                      ▼
PERSISTANCE        FEEDBACK            REMÉDIATION             AUDIT
da_answers         feedback_ar         dominant_error_code     correction_audit
(success/errors/    + advice_ar        → get_remediation()     (hash uniquement,
 missing, hash de   renvoyés au        → page + conseil         jamais la copie)
 la réponse)        frontend           du livre MANHADJIYA
        │
        ▼
FSRS (da_fsrs)
score par verbe/chapitre
(last_score, attempts)
```

## Le dict de résultat v2 — le « contrat » échangé entre les moteurs

```python
{
  "source": "local" | "llm" | "llm_recovered" | "sanity" | "llm_error",
  "score": int, "score_max": int, "percentage": int,
  "highlights": [{"start", "end", "type", "message_ar"}],   # erreurs localisées dans le texte
  "matched_criteria": [...],          # ce que l'élève a réussi
  "unmatched_criteria": [{"criterion", "why_ar", "from_model_answer"}],  # ce qu'il a raté
  "feedback_ar": str, "advice_ar": str,
  "dominant_error_code": "scientific_error" | "methodology_error" | "off_topic"
                       | "partial_correct" | "all_correct" | "insufficient",
  "missing": [...], "success": [...], "errors": [...],
  "remediation": {"page", "lesson_title", "advice_ar"},   # → lien livre
  "student_answer_hash": "sha256..."   # RGPD
}
```

C'est **ce dict qui fait communiquer tous les moteurs** : chaque étape le remplit,
chaque consommateur (DB, FSRS, frontend, audit) le lit.

---

# 3. Pipeline B — le chemin legacy (encore branché sur FSRS graph)

```
ÉLÈVE → POST /api/ai/evaluate → ai_evaluate.py → evaluation_mode.py
        │
        ▼
routes/evaluate.py — evaluate_with_fallback()
   │
   ├─ N0: check_common_mistakes()          (fallback_v2) — erreurs connues, instantané, 0 token
   │       └─ si erreur connue → verdict immédiat (source=COMMON_MISTAKES)
   ├─ N1: call_gpt4o_evaluator()           (llm.py + 7 providers de fallback)
   │       └─ si échec →
   ├─ N2: evaluate_l2()                    (fallback_v2) — local composite
   │
   ▼
evaluation_mode.py
   ├─ update_concept_graph()    → FSRS graph (concepts + prérequis)
   ├─ save_concept_updates()    → prochaine révision FSRS
   ├─ needs_l1_review ? → enque_for_l1_review() → worker de réconciliation
   │       └─ re-évalue avec LLM en arrière-plan ; écart > 0.20 → correct_fsrs_scores()
   ├─ translate_feedback()      (feedback_translator) — français ↔ arabe
   └─ evaluate_methodology()    (methodology/evaluator) — juge la MÉTHODE, pas le fond
```

**Différence clé avec A :** le pipeline B met à jour le **graphe de concepts FSRS**
(et déclenche la réconciliation L1), le pipeline A met à jour **da_fsrs** (score par verbe).
Les deux coexistent sans se synchroniser — dette connue.

---

# 4. Les moteurs de jugement et ce qu'ils produisent

| Moteur | Fichier | Juge quoi | Sortie |
|---|---|---|---|
| **Sanity check** | answer_sanity.py | la forme (vide, court, charabia, pas arabe) | code + message arabe, 0 token |
| **L2 composite** | fallback_v2.py | le fond sans LLM | score 0-1 (sémantique 0.40 + TF-IDF 0.25 + structurel 0.35), concepts trouvés/manquants, verdict correct/partiel/insuffisant |
| **savoir_correct** | savoir_corrector.py | les mots-clés scientifiques + valeurs numériques (38 ATP…) | score/points, points forts, erreurs, conseils — **⚠️ orphelin : utilisé seulement par scripts/audit_correcteur.py** |
| **LLM** (optionnel) | llm.py + llm_helpers | le fond avec IA | score, highlights, critères matchés |
| **Common mistakes** | fallback_v2.py | les erreurs typiques connues | verdict instantané |
| **RAG** | rag_service.py + reranker | fournit le CONTEXTE au jugement | chunks + sources (alimente le prompt/fallback) |
| **FSRS** | scheduler.py + fsrs_graph | la mémoire de l'élève | intervalle de révision, prédiction Bac |

## Comment les ERREURS de l'élève sont jugées (le cœur de la question)

1. **Détection** : le moteur de jugement compare la réponse à la réponse modèle et aux
   concepts requis → `unmatched_criteria` (ce qui manque, avec `why_ar` et `from_model_answer`).
2. **Classification** : `dominant_error_code` — priorité :
   `sanity_code` (charabia) > `scientific_error` (erreur de science) > `off_topic` (hors sujet)
   > `methodology_error` (méthode ratée) > `partial_correct` > `all_correct`.
3. **Localisation** : `highlights` (start/end dans le texte de l'élève + type + message arabe).
4. **Remédiation** : `dominant_error_code` + verbe → `get_remediation()` → **page du livre
   MANHADJIYA** + conseil arabe (fallback générique si verbe non couvert).
5. **Mémorisation** : le score part dans **FSRS** (da_fsrs v2 / concept graph legacy) → la
   prochaine révision de l'élève est calculée selon cette erreur.
6. **Filet de sécurité** : si le score est ambigu (zone grise 0.35-0.70), la **réconciliation L1**
   ré-évalue avec LLM en arrière-plan et corrige les scores FSRS si écart > 0.20.

---

# 5. Schéma de communication simplifié (une réponse d'élève)

```
            ┌─────────────────────────────────────────────┐
            │              ROUTE /evaluate-v2              │
            └──────────────────┬──────────────────────────┘
                               │
         ┌─────────────────────┼──────────────────────┐
         ▼                     ▼                      ▼
   SANITY check          LLM (si clé)           L2 local (0 clé)
   (0 token)             │  │  │                 │  │  │
         │               │  └──┴──▶ fallback ◀───┘  │  │
         ▼               ▼                          ▼
   ┌─ rejet 0 ──▶ message arabe            score + concepts + verdict
         │                                     │
         └──────────▶ DICT DE RÉSULTAT ◀───────┘
                          │
        ┌─────────────────┼──────────────────────────────┐
        ▼                 ▼                              ▼
   dominant_error    unmatched_criteria             score/percentage
   → remediation     → missing/errors               → FSRS (da_fsrs)
   → page livre      → affiché à l'élève            → prochaine révision
```

---

# 6. Constats de l'audit de communication

| # | Constat | Impact |
|---|---|---|
| 1 | **Deux pipelines non synchronisés** (A → da_fsrs, B → concept graph) | un élève peut avoir 2 historiques FSRS différents selon la page |
| 2 | **savoir_correct orphelin** : excellent moteur de mots-clés/numériques, jamais branché sur une route | son potentiel (vérif 38 ATP, mots-clés) est perdu |
| 3 | **Le dict de résultat est le seul contrat** entre moteurs — il est stable (bon point) | la communication passe par un format commun documenté |
| 4 | **La réconciliation L1 ne tourne qu'avec LLM** (si `state.openai` absent → ré-enfile à l'infini) | en mode sans clé, la zone grise n'est jamais re-évaluée (acceptable : le L2 est honnête) |
| 5 | **Le chatbot ne note pas** : il oriente vers `/evaluate-v2` et les flashcards | cohérent produit (le chat explique, l'évaluation juge) |

---

# 7. Recommandations prioritaires

1. **Brancher `deterministic_correct` (savoir_corrector)** comme 1er étage du pipeline A
   (avant sanity ou après) pour les questions à mots-clés/nombre : il donne 4/4 vs 0/4
   avec 0 token — le juge le plus précis pour les questions fermées.
2. **Synchroniser FSRS** : faire écrire `da_fsrs` par le pipeline B (ou migrer le concept
   graph vers da_fsrs) — une seule source de vérité pour la mémoire de l'élève.
3. **Documenter le format commun** dans le code (déjà fait en partie — le dict v2).
