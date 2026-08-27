# Architecture du correcteur — pour audit

**Date :** 2026-08-26 · **Source :** arbre réel (`khawarizmi-backend/grading/` + routes)
**Règle :** un seul pipeline « prof » (v2) ; **cinq moteurs de note coexistent**. Les auditer comme un système, pas comme un fichier.

---

## 0. Carte des moteurs (le fait le plus important)

Il n’y a **pas un** correcteur. Il y a **5 notes possibles** selon l’écran.

```
ÉCRAN ÉLÈVE                         MOTEUR RÉEL                         MONTÉ ?
─────────────────────────────────────────────────────────────────────────────
ScenarioRunner / DA immersif        Pipeline v2 (grading/)              OUI
                                    POST /api/document-analysis/evaluate-v2

Ancienne DA / Bac Blanc immersif    Regex VERB_RULES                    OUI
                                    POST /api/document-analysis/evaluate
                                    services/document_analysis_service.py
                                    bac_blanc.py appelle evaluate_answer() v1

Page /action-verbs/[slug]           Regex action_verbs_service          OUI
                                    POST /api/action-verbs/evaluate

File méthodologie (checklists)      Front local (methodology-v2.ts,     OUI (0 API)
                                    methodology-evaluator.ts)

Drill / questions bank (legacy)     evaluate.py : GPT-4o → L2           NON
                                    ai_evaluate.py orchestrateur        NON
```

**Pour un audit « le correcteur Bac » : le cœur est le pipeline v2.**  
Les autres sont des **barèmes parallèles** (même verbe, note différente).

---

## 1. Cœur v2 — couches

```
┌─────────────────────────────────────────────────────────────────┐
│  ROUTE  POST /api/document-analysis/evaluate-v2                 │
│  routes/document_analysis_v2.py                                 │
│  JWT + SlowAPI evaluate_limit (15/h free, 80/h pro)             │
│  charge scénario + docs + questions (model_answer inclus)       │
│  score_max = somme(VERB_RULES[verbe].points)  ← barème v1 !     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  CACHE C2   grading/cache.py :: evaluate_with_cache             │
│  • sanity pré-check (rejet → pas de lookup)                     │
│  • clé = question + verbe + score_max + copie normalisée        │
│            + model_id + prompt v1|v2     (PAS user_id)          │
│  • single-flight local + Redis Lua CAS                          │
│  • TTL 7 j · n’écrit que llm / llm_v2 / llm_retried /           │
│    local_savoir  (jamais sanity, jamais L2, jamais llm_error)   │
│  • highlights reprojetés (lstrip delta)                         │
│  • payload SANS copie claire, SANS llm_raw                      │
└────────────────────────────┬────────────────────────────────────┘
                             │ miss
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  RETRY   services/correction_v2_retry.py                        │
│  max 2 tentatives · budget global 20 s                          │
│  retry seulement llm_error TRANSITOIRE (5xx, timeout, 429)      │
│  jamais retry sanity / savoir / JSON invalide / 401             │
│  succès après retry → source = llm_retried  (si source==llm)    │
│  ⚠ use_v2_prompt=True produit souvent source=llm_v2 →           │
│    le tag llm_retried NE S’APPLIQUE PAS                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  FAÇADE   services/correction_v2.py  (93 lignes, 0 logique)     │
│  délègue → grading/pipeline.py                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    PIPELINE (ci-dessous)
```

`correction_v2.py` est une **façade**. Toute logique nouvelle dans ce fichier = dette.

---

## 2. Pipeline `grading/pipeline.py` — 7 étages

```
copie élève
    │
    ▼
[1] SANITY          grading/sanity.py
                    → services/answer_sanity.check_answer_sanity
                    0 token · ~µs
                    rejet → score 0, source=sanity, STOP
                    codes : empty | too_short | not_arabic | gibberish | repeated_chars
                    seuils : ≥8 car. utiles · ≥30 % arabe · ≤60 % bigrammes répétés · ≥4 glyphes
    │ ok
    ▼
[2] SAVOIR          grading/savoir.py
                    → services/savoir_corrector.deterministic_correct_v2
                    0 token · lexique FR/AR + erreurs graves + règles numériques DZ
                    PROMU seulement si :
                      • verb_slug ∈ config.savoir_enabled_verbs   (DÉFAUT = [])
                      • can_handle : ≥2 concepts lexique dans (énoncé+modèle)
                      • ≥3 concepts trouvés DANS LA COPIE
                    sinon → None, on continue
                    remédiation : SAVOIR_REMEDIATION_ENABLED (défaut False)
    │ None
    ▼
[3] PROMPT          grading/prompts.py
                    v2 (prod DA) : court, ~900 tokens max
                    v1 : + RAG Manhadjiya (rag_search, 3 chunks, verbe)
                    temperature 0.0 · max_tokens 900 · timeout 25 s
    │
    ▼
[4] LLM             llm_call injecté = services.llm._call_with_fallback
                    llm_guard : SANS ENABLE_EXTERNAL_LLM=1 + clé
                    → LLMDisabledError → étage 4 échoue
                    JSON natif : seulement si provider ∈ json_mode_providers
                    (DÉFAUT = [] → parse texte)
    │ fail / JSON mort
    ▼
[5] PARSER          grading/parser.py
                    native_json → direct → fence ```json → regex → partial
    │
    ▼
[6] MAPPING         grading/mapping.py   (si prompt v2 : errors[] → v1)
                    sinon clamp score, validate_highlights, normalize_unmatched
                    champs cassés → source=llm_recovered
    │
    ▼
[7] FINALIZE        grading/post_validate.py
                    dominant_error_code, hashes HMAC(SECRET_KEY), remediation
                    contrat EvaluationV2
```

**Fallback L2** (`grading/l2.py` → `fallback_v2.evaluate_l2`) si :
`llm_call` absent **ou** exception LLM **ou** JSON irrécupérable, **et** `local_fallback=True`.

La route v2 passe **`local_fallback=True`**. Donc en prod sans clé cloud :

```
sanity → savoir (off) → LLM bloqué par llm_guard → L2
```

Le « correcteur souverain » runtime **n’est pas Savoir**. C’est **L2**.

---

## 3. L2 — ce que c’est vraiment

`services/fallback_v2.py` · score composite 0–1 :

| Signal | Poids | Mécanisme |
|---|---|---|
| s1 sémantique | 0.40 | cosine MiniLM ONNX **ou** bruit hash si LFS |
| s2 TF-IDF | 0.25 | char n-grammes 3–5 (sklearn) |
| s3 structurel | 0.35 | regex synonymes + **anti-négation** |

Si `embedder.is_fallback` : s1 est **jeté**, poids reportés sur TF-IDF + structurel  
`(0.25 s2 + 0.35 s3) / 0.60`.

Concepts L2 ≠ lexique Savoir : extraits du `skill` + 10 mots ≥4 lettres du **modèle**. Table `SYNONYMES` L2 beaucoup plus petite.

`question_id` n’est **pas** passé par `run_l2` → pas de lookup `reference_embeddings` pgvector sur le chemin v2. Cosine **local** uniquement.

---

## 4. Savoir — ce que c’est vraiment

`savoir_corrector.py` (~900 lignes) :

- Lexique `_SYNONYMS` / `_SYNONYMS_NORM` (concepts SVT 3AS, FR+AR+darija)
- Erreurs graves (`_GRAVE_ERRORS`) : 36 ATP, ADN dans le cytoplasme, CO₂ produit en photosynthèse…
- Règles numériques ONEC : 38 ATP, P/O 3/2
- Score = couverture mots-clés − pénalités
- **Concepts attendus déduits du modèle, pas de l’énoncé** (copie modèle = 20/20)

**Off en prod** tant que `SAVOIR_ENABLED_VERBS` est vide.  
L’activer trop tôt = noter avec le lexique sur des verbes méthodo (حلّل / فسّر) où le lexique est un mauvais juge.

---

## 5. Contrat de sortie v2 (ce que le front consomme)

`grading/contracts.py` + `schemas/evaluation_v2.py`

```
source          sanity | local_savoir | local | llm | llm_v2 | llm_recovered
                | llm_retried | llm_error | cached_evaluation | socratic
score / score_max / percentage / confidence
highlights[]    {start, end, type, message_ar}   offsets sur la copie
matched_criteria[] / unmatched_criteria[] / missing[]
success[] / errors[]
dominant_error_code
feedback_ar / advice_ar
remediation     {page, lesson_title, advice_ar} | hint socratique
from_cache
student_answer_hash   HMAC-SHA256(SECRET_KEY)   jamais la copie
```

**Socratique** (`request_hint=true`) : court-circuit **avant** le pipeline.  
`source=socratic`, score 0, **pas** de persist, **pas** de FSRS.

---

## 6. Persistance (route v2 seulement)

| Table | Quoi |
|---|---|
| `da_sessions` | score_global = somme notes **hors** `llm_error` |
| `da_answers` | **hash** de la copie (`hash_answer`) — ici RGPD tenu |
| | skip si `source=llm_error` (ne pas pourrir l’historique) |
| FSRS unifié | `update_memory(verb_chapter, verb::chapter)` si pas llm_error |
| audit | `log_correction_audit` hashes only |

**Attention :** la route **v1** (`document_analysis.py`) écrit encore `answer_text` **en clair**. Deux politiques sur la même table.

---

## 7. Feature flags (le levier d’audit n°1)

| Variable | Défaut | Effet |
|---|---|---|
| `ENABLE_EXTERNAL_LLM` | off | sans ça, étage 4 n’existe pas |
| `savoir_enabled_verbs` | `[]` | Savoir jamais promu |
| `savoir_remediation_enabled` | `false` | même si promu, `remediation=None` |
| `json_mode_providers` | `[]` | parse texte, pas JSON natif |
| `local_fallback` | `True` sur la route v2 | L2 après échec LLM |
| `use_v2_prompt` | `True` sur la route v2 | mapping v2→v1 |

Mesurer `grading_source_total{source,verb}` **avant** de toucher un flag.

---

## 8. Observabilité

- Prometheus `/metrics/prometheus` : `grading_source_total`, `parse_strategy_total`, `correction_cache_ops_total`, `grading_pipeline_events_total`, latence LLM
- OTel `grading/tracing.py` : spans sanity / savoir / handle (no-op si SDK absent)
- `cost_logger` si usage tokens
- Cache : hit / hit_after_wait / miss / store / skip_uncacheable

---

## 9. Contraintes d’archi (à ne pas casser)

1. `grading/` **n’importe pas** FastAPI / SQLAlchemy / Redis. Cache hors pipeline.
2. Pas de cycle : `correction_v2` → `pipeline` ; jamais l’inverse.
3. Cache **sans** `user_id` : deux élèves, même copie, même note. **Voulu** (équité).  
   Conséquence : une note Savoir/LLM devient la vérité pour tout le lycée 7 jours.
4. `llm_raw` et la copie **interdits** dans le payload cache (`assert`).
5. Température **0.0** — ne pas « améliorer » en 0.3.

---

## 10. Surfaces d’audit (checklist)

### Intégrité de la note
- [ ] Même copie, 3 moteurs (v2 / v1 regex / action-verbs) → 3 notes. Acceptable ?
- [ ] `score_max` v2 dérivé de `VERB_RULES` v1 — le LLM n’invente pas le barème, mais le barème est celui du **regex**, pas du سلم ONEC.
- [ ] Savoir off : en local sans LLM, **L2** note. Qualité L2 ≠ qualité Savoir.
- [ ] ONNX LFS = s1 L2 = bruit ; redistribution OK **si** `is_fallback` détecté.

### Équité / cache
- [ ] Cache cross-élèves : voulu. Une hallucination LLM cachée 7 j = **toutes** les copies identiques faussées.
- [ ] L2 / sanity **non** cachés. OK.
- [ ] `llm_retried` rarement posé (source `llm_v2`). Métrique retry trompeuse.

### Sécu / RGPD
- [ ] v2 hashe la copie. **v1 ne le fait pas.**
- [ ] Highlights renvoyés au front : offsets sur texte élève (OK) ; contenu visible (normal).
- [ ] `model_answer` chargé serveur, **pas** renvoyé dans evaluate-v2. Mais `GET .../correction` le livre à tout JWT (hors pipeline, trou voisin).

### Gouvernance LLM
- [ ] `get_openai` sur la route : 503 si client absent ? Vérifier deps — si 503, L2 n’est jamais atteint.
- [ ] `llm_guard` + `local_fallback=True` = chemin nominal local. Documenter ça, pas « hybride LLM ».

### Pédagogie
- [ ] Sanity `not_arabic` : copie 100 % chiffres/formules (38 ATP, O₂) peut être rejetée.
- [ ] Savoir juge le **contenu** ; le Bac juge aussi la **méthode** (حلّل / نص علمي). Promouvoir Savoir sur ces verbes = mauvaise note « scientifique » pour une tâche méthodo.
- [ ] File front (checklists) **ne passe pas** par ce pipeline. n/6 ≠ score v2.

### Code mort / double
- [ ] `evaluate.py` / `ai_evaluate.py` hors registre — ne pas « réparer » en les montant.
- [ ] `correction_service.py` (legacy) encore importé ? À grepper avant suppression.

---

## 11. Fichiers canoniques (ordre de lecture)

```
routes/document_analysis_v2.py     entrée HTTP + persist + FSRS
grading/cache.py                   C2
services/correction_v2_retry.py    retry
services/correction_v2.py          façade
grading/pipeline.py                orchestrateur
grading/sanity.py  + answer_sanity.py
grading/savoir.py  + savoir_corrector.py
grading/prompts.py
grading/parser.py
grading/mapping.py
grading/l2.py      + fallback_v2.py
grading/post_validate.py
grading/contracts.py
services/llm.py + llm_guard.py     étage 4 réel
services/document_analysis_service.py   v1 parallèle (Bac Blanc)
```

---

## 12. Schéma mental pour l’auditeur

```
                    ┌──────────── sanity ────────────┐
                    │ rejet → 0                      │
                    └──────────────┬─────────────────┘
                                   │
                    ┌──────────── savoir ────────────┐
                    │ flag verbe + ≥3 concepts       │
                    │ défaut OFF ────────────────────┼──► (saute)
                    └──────────────┬─────────────────┘
                                   │
              ENABLE_EXTERNAL_LLM=1 ?────non────┐
                       oui                      │
                        ▼                       ▼
                   LLM + parse               L2 (TF-IDF+regex
                   + mapping                 + embed / hash)
                        │                       │
                        └───────────┬───────────┘
                                    ▼
                              contrat v2
                         cache si source « noble »
                         persist hash + FSRS
```

**Phrase d’audit :** le dépôt *vend* un correcteur hybride sanity → savoir → LLM → L2.  
Le *runtime par défaut* est **sanity → L2**, barème `VERB_RULES`, cache partagé, et **deux autres correcteurs regex** encore en prod sur d’autres écrans.
