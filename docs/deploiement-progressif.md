# Déploiement progressif — IA Khawarizmi Pro

Checklist opérationnelle pour la mise en production SANS risque : chaque
fonctionnalité s'active progressivement, avec un rollback ciblé et des
métriques de validation.

---

## 1. Configuration (config.py)

| Variable | Défaut | Activation |
|---|---|---|
| `savoir_enabled_verbs` | `[]` | liste de verb_slug (analyse, extract, interpret…) |
| `json_mode_providers` | `[]` | noms canoniques (openai, groq, gemini, zai) |
| `ENABLE_EXTERNAL_LLM` | absent | `1` + clé API pour activer le LLM externe |

Les deux listes vides = comportement « pré-optimisation » : aucun étage
savoir, aucun JSON natif. La route fonctionne identiquement (LLM seul).

---

## 2. Séquence d'activation recommandée

### J0 — Déploiement initial (tout désactivé)
- `savoir_enabled_verbs=[]` · `json_mode_providers=[]`
- Vérifier : `/metrics/prometheus` répond, `/api/memory/summary` répond,
  les 935 tests CI passent.
- Objectif : baseline stable, 0 changement de comportement.

### J1 — Étage savoir (1 verbe)
- `savoir_enabled_verbs=["analyse"]` (verbe d'extraction — réponses courtes
  = le point fort du moteur).
- Métriques cibles :
  - `grading_source_total{source="local_savoir",verb="analyse"}` / total
    du verbe > 20 % ;
  - `grading_llm_latency_seconds` p95 en baisse (les corrections savoir
    sont 0 token) ;
  - scores moyens stables ±5 % vs J0 (pas de plaintes utilisateurs).
- Rollback : retirer "analyse" de la liste (instantané, sans déploiement).

### J3 — Étendre savoir (2e verbe)
- `savoir_enabled_verbs=["analyse", "extract"]` (ou un autre verbe
  d'extraction/identification).
- Ne PAS activer les verbes de rédaction (علّل/فسّر) avant le golden
  humain : les troncatures riches sont sur-notées (biais documenté).

### J7 — Bilan hebdo + JSON natif (1 provider)
- Bilan : coverage savoir, économie tokens, satisfaction. Décision
  d'étendre ou de rester.
- `json_mode_providers=["openai"]` (ou le provider principal réel).
- Métriques : `parse_strategy_total{strategy="native_json",provider=...}`
  doit dépasser 95 % ; si < 90 % → alerte (le provider ne respecte pas son
  contrat) → rollback en retirant de la liste.

### J14 — Étendre JSON natif
- `json_mode_providers=["openai", "groq"]` puis +gemini — chaque ajout
  validé par la même métrique parse_strategy.

---

## 3. Endpoints de contrôle

| Endpoint | Usage |
|---|---|
| `GET /metrics/prometheus` | métriques Prometheus (scrape) |
| `GET /api/memory/summary` | vue consolidée mémoire FSRS |
| `GET /api/memory/due?limit=50` | items dus |
| `GET /health` | santé |

---

## 4. Alertes recommandées (Prometheus)

```
# L'étage savoir est activé mais quasi-jamais appliqué
ALERT SavoirInactif
IF rate(grading_source_total{source="local_savoir"}[1h])
   / rate(grading_source_total[1h]) < 0.05
   AND savoir_enabled_verbs != []
THEN "savoir_corrector activé mais quasi-jamais appliqué — vérifier can_handle"

# Le JSON natif ne domine pas sur un provider activé
ALERT JsonModeFaible
IF rate(parse_strategy_total{strategy!="native_json"}[1h])
   / rate(parse_strategy_total[1h]) > 0.10
THEN "parse de rattrapage > 10 % — provider JSON mode suspect"

# Pire cas panne LLM
ALERT LLMDeadline
IF histogram_quantile(0.99, rate(grading_llm_latency_seconds_bucket[5m])) > 20
THEN "latence LLM p99 > 20 s — deadline global C3 approché"
```

---

## 5. Migration 033 (fusion FSRS) — ordre

1. `alembic upgrade head` (Postgres) — ajoute les colonnes de fusion +
   backfill da_fsrs/action_verb_progress (idempotent, WHERE NOT EXISTS).
2. Vérifier : `SELECT source, COUNT(*) FROM mastery_micro_concepts GROUP BY
   source;` → concept/verb_chapter/verb_action.
3. Les écritures passent déjà par fsrs_unified (aucun changement de code
   nécessaire). Les tables da_fsrs/action_verb_progress restent en lecture
   (analytics) — suppression possible plus tard si décidée.

---

## 6. Garde-fous intégrés (rappel)

- **Cache C2** : jamais de note dégradée cachée (source ∈ whitelist) ; TTL
  7 j ; single-flight (30 élèves → 1 appel LLM).
- **Étage savoir** : jamais généraliste (can_handle + ≥ 3 concepts dans la
  copie) ; remédiation désactivée tant que κ < 0.65.
- **JSON natif** : activation par provider ; parser fallback conservé ;
  kill-switch par liste vide.
- **LLM** : deadline global 20 s (C3) + circuit breaker par provider.
- **FSRS** : une seule porte d'écriture (fsrs_unified) ; tolérance table
  absente (preview).
