# Audit technique — Moteur de correction (Correcteur IA)

**Date :** 2026-08-06 — **Périmètre :** `correction_v2.py` (686 l.), `correction_v2_retry.py` (154 l.), `correction_audit.py`, `answer_sanity.py`, `llm.py` (fallback multi-provider), `socratic_tutor.py`, `remediation_service.py`, prompts v1/v2, routes `document_analysis_v2`, `evaluate`, `ai_evaluate`, `dual_coding`, et les 158 tests associés.
**Méthode :** lecture intégrale + tests dynamiques (parsing tolérant, validation highlights, couverture) + vérification des contrats route/schéma/persistance.

---

# 1. Verdict synthèse

| Axe | Note | Constat |
|---|---|---|
| Architecture | 🟢 | pipeline hybride clair : sanity → prompt → LLM avec fallback → post-validation |
| Robustesse parsing | 🟢 | 4 stratégies d'extraction JSON, highlights clampés/validés |
| Résilience | 🟢 | retry ciblé transitoire (98 % couverture) + chaîne de 7 providers |
| Sécurité / RGPD | 🟠 | audit en hash uniquement ✅ mais **`da_answers.answer_text` stocke la réponse brute en clair** |
| Couverture tests | 🟠 | 75 % global ; `socratic_tutor` à 32 % |
| Cohérence | 🟠 | **2 moteurs coexistent** : `correction_v2` (nouveau) vs `call_gpt4o_evaluator` (legacy, encore branché sur `/api/ai/evaluate` et `routes/evaluate.py`) |
| Coût | 🟡 | prompt v2 (-68 % tokens) non activé par défaut |

**En une phrase :** le correcteur v2 est **bien conçu, bien testé et résilient** — mais il coexiste avec un moteur legacy toujours branché, stocke la copie de l'élève en clair (contrairement à sa propre charte d'audit), et son prompt optimisé n'est pas activé.

---

# 2. Points forts (vérifiés)

## 2.1 Pipeline hybride propre
`evaluate_answer_v2` : **1. Sanity check local** (0 LLM) → **2. Build prompt** (v1 ou v2, RAG enrichi) → **3. Appel LLM** (injectable, fallback multi-provider) → **4. Post-validation** (parse JSON tolérant, clamp score, validate highlights). Chaque étape a une sortie déterministe documentée (`sanity`, `llm`, `llm_recovered`, `llm_v2`, `llm_error`, `llm_retried`).

## 2.2 Parsing JSON très robuste (testé)
- JSON direct → fences ```json``` → premier `{`/dernier `}` → balayage par profondeur.
- Testé : JSON noyé dans du texte ✓, fence ✓, tronqué → `None` propre ✓, sans JSON → erreur contrôlée ✓.

## 2.3 Highlights validés
`_validate_highlights` : types inconnus → `irrelevant`, start/end clampés, `start >= end` rejeté, non-dict ignorés. Testé ✓.

## 2.4 Retry intelligent (98 % couverture)
`evaluate_answer_v2_with_retry` : ne retente **que** les erreurs transitoires (5xx, timeout, 429, quota…) via patterns ; jamais de retry sur charabia (sanity) ni sur erreurs permanentes (401, clé invalide, JSON illisible). Backoff exponentiel 1.5s ×2, `attempts` ajouté au contrat, `source="llm_retried"` après succès post-retry.

## 2.5 Chaîne de fallback multi-provider (7 niveaux)
`_call_with_fallback` : primaire (auto-détecté Groq/Gemini/OpenRouter) → Gemini 2.5 Flash → Cloudflare GLM-5.2 → Z.AI GLM-4.7 → ZenMux → NaraRouter → OpenAI gpt-4o-mini. Le validateur JSON déclenche le fallback même sur HTTP 200 inexploitable. Métadonnées provider/modèle taguées sur la réponse pour l'audit.

## 2.6 Sanity check local efficace (85 % couverture)
Vide, trop court (< 8 car.), ratio arabe < 30 %, bigrammes répétés > 60 %, < 4 caractères distincts, keyboard smash latin/arabe → rejet immédiat avec message pédagogique arabe, **sans dépenser un token**.

## 2.7 Audit RGPD bien pensé… dans `correction_audit.py`
`log_correction_audit` : uniquement des hash SHA256 (élève, prompt, erreur), jamais de contenu brut, insert async sans bloquer, échec silencieux (log seulement).

## 2.8 Remédiation automatique
`dominant_error_code` (Spec §3.1) mappé via `REMEDIATION_MATRIX` (21 verbes du livre MANHADJIYA × codes d'erreur) → page + conseil arabe. Fallback générique si verbe non couvert.

---

# 3. Problèmes trouvés

## 🔴 P0-1 — La copie de l'élève est stockée en clair (contradiction RGPD interne)
`routes/document_analysis_v2.py` insère `answer_text = ans.answer` (texte brut complet) dans `da_answers` — **alors que la charte du projet** (AGENTS.md §1.2 + `correction_audit.py`) impose « contenu élève = hash uniquement ». Le hash est pourtant déjà calculé (`student_answer_hash`) et stocké dans l'audit. **La colonne `answer_text` est la seule trace en clair de la copie.**
→ Recommandation : stocker uniquement le hash dans `da_answers` (la colonne existe en migration 009) ou supprimer la colonne ; garder la copie seulement en session volatile.

## 🟠 P1-1 — Deux moteurs de correction coexistent (dette + risque d'incohérence)
| Moteur | Route | Statut |
|---|---|---|
| `evaluate_answer_v2_with_retry` (nouveau, hybride) | `/api/document-analysis/evaluate-v2` | **le bon** |
| `call_gpt4o_evaluator` (legacy, `llm.py`) | `/api/evaluate` (routes/evaluate.py) **et `/api/ai/evaluate`** (orchestrateur → `evaluation_mode.py` → `evaluate_with_fallback`) | **toujours branché** |

Conséquences : deux formats de sortie, deux notations (`score/10` avec seuils 0.85/0.35 vs `score/score_max`), deux politiques de fallback (double retry tenacity + fallback provider empilés). L'élève peut recevoir deux notes différentes selon la page.

## 🟠 P1-2 — Prompt v2 optimisé (-68 % tokens) non activé par défaut
`use_v2_prompt: bool = False` — la route `document_analysis_v2` **ne passe jamais** `use_v2_prompt=True`. Le gain mesuré (3742 → ~918 tokens) documenté dans `correction_prompt_v2.py` n'est donc **pas exploité en production**. → Recommandation : activer `use_v2_prompt=True` sur la route (le mapping v2→v1 est déjà écrit et testé).

## 🟡 P2-1 — Score max par verbe : couverture large mais fallback silencieux
`_compute_score_max_for_verb` s'appuie sur `VERB_RULES` (**26 verbes couverts** : analyse, interpret, deduce, justify, hypothesis, compare, explainer, critiquer, determiner, nommer, definir…). Vérifié : un verbe **absent** de la table retombe sur `4` **sans log** — une question mal typée donnerait une note sur 4 sans avertissement. → Recommandation : logger le fallback (1 ligne).

## 🟡 P2-2 — Couverture de tests inégale
- `correction_v2` : 71 % (le mapping v2→v1 et `_compute_dominant_error_code` partiellement couverts)
- `socratic_tutor` : **32 %** (le mode indice — pourtant une fonctionnalité visible)
- `answer_sanity` : 85 %, `correction_audit` : 100 %, `retry` : 98 %

## 🟡 P2-3 — `llm_raw` / `llm_raw_hash` exposés dans le résultat API
La route ne renvoie pas `llm_raw` au frontend (bien vu) mais il **reste dans le dict** retourné par `evaluate_answer_v2` — risque de fuite si une autre route l'expose par `**result`. → Recommandation : le retirer du contrat de retour ou le documenter « interne ».

## 🟡 P2-4 — Mode socratique : `remediation` = `{"hint": ...}` non standard
Dans la route, le mode indice met `remediation: {"hint": hint}` alors que le format standard de `remediation_service` est `{page, lesson_title, advice_ar}` — le frontend qui consomme `remediation.page` peut casser sur ce format hybride.

## 🟢 P3 — Points mineurs
- `_build_retry_result` (fallback final du retry) construit un dict sans `student_answer_hash` ni `provider`/`model` — contrat incomplet (chemin quasi inatteignable).
- Log `llm_response_fr` au niveau WARNING pour un succès (bruit).
- `logger.exception` dans `correction_audit` pourrait exposer l'erreur SQL complète (acceptable en dev, à filtrer en prod).

---

# 4. Vérifications dynamiques (preuves)

| Test | Résultat |
|---|---|
| Extraction JSON : direct / fence / noyé / tronqué / absent | ✓ / ✓ / ✓ / `None` propre / `None` propre |
| `_validate_highlights` : type invalide → `irrelevant`, clamp, inversion rejetée | ✓ (2 highlights valides sur 5) |
| `score string` ("cinq") → géré par `llm_recovered` + `int()` | ✓ (0 + source récupérée) |
| Tests correcteur (5 fichiers) | **158 passed** |
| Couverture (5 modules) | **75 %** (correction_v2 71 %, retry 98 %, audit 100 %, sanity 85 %, socratic 32 %) |
| `VERB_RULES` — couverture des verbes | **26 verbes** couverts, fallback silencieux à 4 pts |

---

# 5. Plan d'action priorisé

| # | Action | Effort | Impact |
|---|---|---|---|
| 1 | **RGPD** : `da_answers` → stocker `student_answer_hash` au lieu d'`answer_text` (ou chiffrer) | 30 min | conformité charte |
| 2 | **Unifier** : faire converger `/api/ai/evaluate` et `routes/evaluate.py` vers `evaluate_answer_v2_with_retry` (ou documenter l'abandon du legacy) | 1-2 h | une seule note possible |
| 3 | **Activer** `use_v2_prompt=True` sur la route evaluate-v2 | 5 min | -68 % tokens |
| 4 | Compléter `VERB_RULES` pour tous les verbes du livre (21) + test de couverture | 1 h | notes cohérentes |
| 5 | Tests `socratic_tutor` (32 % → ≥ 70 %) | 1 h | filet sur le mode indice |
| 6 | Retirer `llm_raw`/`llm_raw_hash` du contrat de retour public | 15 min | pas de fuite |
| 7 | Normaliser `remediation` du mode socratique (format standard) | 15 min | frontend robuste |

---

# 7. Corrections appliquées (session du 2026-08-06)

| # | Action | État | Preuve |
|---|---|---|---|
| 1 | **RGPD** : `da_answers.answer_text` stocke désormais `_sha256_text(ans.answer)` (hash SHA-256), plus jamais la copie en clair — aligné sur `correction_audit` et AGENTS.md §1.2 | ✅ fait | `answer_text` n'était lu par aucune route (vérifié) → aucun impact fonctionnel |
| 2 | **Legacy documenté** (pas de refonte risquée) : `call_gpt4o_evaluator` marqué « MOTEUR LEGACY — maintenu uniquement pour la réconciliation L1/L2 » ; `evaluation_mode` note que `/api/ai/evaluate` n'est appelé par aucun frontend | ✅ fait | docstrings ajoutés ; `/api/evaluate` reste non exposé |
| 3 | **`use_v2_prompt=True`** activé sur la route evaluate-v2 → prompt optimisé -68 % tokens (3742 → ~918) avec mapping v2→v1 testé | ✅ fait | paramètre passé dans l'appel retry |
| 4 | **Fallback score_max loggé** : verbe absent de VERB_RULES ou sans points → `logger.warning` au lieu du silence | ✅ fait | 26 verbes couverts, 2 warnings possibles |
| 5 | **Couverture socratic_tutor** : faux positif de mesure — les 6 tests existants donnent en réalité **92 %** (la mesure initiale de 32 % excluait le fichier de test) | ✅ documenté | `--cov` avec test_socratic_tutor : 92 % |
| 6 | **`llm_raw` retiré du contrat public** (retours sanity + succès) — conservé uniquement dans `llm_error` (debug interne, jamais exposé) ; `llm_raw_hash` reste pour l'audit | ✅ fait | test `llm_error` (l.249) inchangé, 59 tests correcteur verts |
| 7 | **`remediation` mode socratique** : faux positif — le type frontend `remediation` accepte les deux formes (`{page, lesson_title, advice_ar}` **et** `{hint: {hint_ar, focus_area, methodology_step}}`) et `ScenarioRunner.tsx` gère les deux (l.142-159) | ✅ documenté | aucun changement nécessaire |

**Vérifications :** pytest complet **628 passed / 0 failed** · boot serveur OK · aucun fichier frontend modifié.

---

# 6. Limites de l'audit

- Pas d'appel LLM réel (mode local) : le comportement des providers n'est vérifié que par mocks/tests unitaires et lecture.
- La route `evaluate-v2` n'a pas pu être testée de bout en bout (tables `da_*` absentes du mode SQLite preview — nécessite PostgreSQL seedé).
- Le legacy (`evaluate_with_fallback`, `normalize_result` dans routes/evaluate.py) n'a pas été audité ligne à ligne ; seuls ses points d'entrée et sa coexistence avec v2 ont été vérifiés.
