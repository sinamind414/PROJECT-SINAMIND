# Synthèse Globale — IA Khawarizmi Pro (Bac SVT Algérie)

**Branche** : `arena/019fd78d-project-sinamind` · **Dernier commit** : `981dc96`
**Suite de tests** : 929 passed · 3 skipped · 5 xfailed · ruff vert

---

## 1. Ce qui a été livré (par phase)

### Sprint 1 — Corrections d'architecture (audit réconcilié)
| Élément | Livraison | Preuve |
|---|---|---|
| **C2** cache de correction exact | `grading/cache.py` + `grading/cache_key.py` — wrapper pur, single-flight, 3 pièges couverts (offsets, champs par-élève, notes dégradées) | 2e envoi identique → 0 appel LLM, source préservée + `from_cache` |
| **O7** JSON natif provider | `services/llm_providers.py` (capacités par provider), `grading/parser.py` (native_json → fallback), schémas strict-compat | `parse_strategy_total{strategy,provider}` ; activation progressive `json_mode_providers` |
| **Golden metrics CI** | `tests/golden/` (metrics, test_golden_local, build_golden_annotated — 125 items) | L2 MAE 0.27, savoir MAE 0.279, copies modèles MAE 0.000 |
| **savoir_corrector branché** | `grading/savoir.py` — étage 0 token, feature flag par verbe, remédiation désactivée (κ 0.449) | `can_handle` + ≥3 concepts dans la copie |
| **ar_normalize + index RAG** | `services/arabic.py` (source unique), migration 032, keywords normalisés | idempotent ; bug `ILIKE ANY` SQLite corrigé |

### S2.1 — Refactor grading (pipeline unifié)
`services/correction_v2.py` : **707 → 93 lignes** (façade de compatibilité).
Pipeline complet dans `grading/pipeline.py` : sanity → savoir → prompt → LLM → parser → mapping → post-validation → L2 fallback.
- 16 modules `grading/` (cache, cache_key, context, contracts, l2, mapping, metrics, observability, parser, pipeline, post_validate, prompts, sanity, savoir, schemas/)
- Aucun import FastAPI/SQLAlchemy/Redis dans le pipeline ; cache hors pipeline
- Les 43 tests historiques passent sans modification via la façade

### S2.2 — Chatbot en handlers testables
`services/chatbot_orchestrator.py` : **442 → 74 lignes** (dispatcher pur).
11 handlers async purs dans `services/chatbot_handlers.py` — refus/triche AVANT méthodologie (P0-4.4), 0 état global.

### S2.3 — Observabilité Prometheus
`grading/observability.py` (import paresseux, no-op si absent) + route `/metrics/prometheus` :
- `grading_source_total{source,verb}` · `parse_strategy_total{strategy,provider}` · `correction_cache_ops_total{result,verb}`
- `grading_pipeline_events_total{event}` (sanity_reject, savoir_promoted, l2_fallback, llm_error, llm_ok)
- Histogrammes : latence LLM, étapes chatbot

### S3 — FSRS unifié (4 systèmes → 1)
- **API** : `services/fsrs_unified.py` — `get_user_memory`, `get_due_items`, `update_memory`, `save_concept_review/update/card`, `tag_pending_concept`, `clear_pending_concept`, `get_concept_states`, stats par chapitre
- **Fusion physique** : migration `033_fsrs_unified_memory` — colonnes `source`/`item_key`/`avg_pct`/`total_users` + backfill depuis da_fsrs et action_verb_progress
- **100 % des écritures** mastery passent par l'API unifiée (flashcards, drill, évaluation riche, drill_queue, evaluation_mode, reconciliation_queue, mindmap)
- Table mastery ajoutée à l'auto-DDL SQLite (bug d'infrastructure corrigé — avant, le preview ne persistait rien)

## 2. Chiffres clés
- **51 commits** poussés sur la branche de session
- **929 tests verts** (+~290 depuis le début de la session), ruff 0 erreur
- **correction_v2.py** : 707 → 93 lignes · **chatbot_orchestrator.py** : 442 → 74 lignes
- **3 migrations** créées (032 ar_normalize, 033 fusion FSRS)
- **2 routes** ajoutées (`/metrics/prometheus`, `/api/memory/*`)
- **3 bugs d'infrastructure latents** corrigés (ILIKE ANY SQLite, CAST jsonb → '0', table mastery absente du preview)

## 3. Prochaines étapes possibles
1. **S2.4** — observabilité OpenTelemetry (traces distribuées)
2. **CI** — débloquer la permission `workflows` (le fichier `docs/ci/ci.yml.amelioree` est prêt : golden bloquant + nightly LLM)
3. **Golden humain** — remplacer les annotations synthétiques par un expert SVT (même format, la mécanique est prête)
4. **Déploiement** — activation progressive documentée (savoir par verbe, JSON mode par provider)
