# Benchmark cache correction C2 — résultats

Mesure de charge déterministe (sans réseau ni DB) sur les VRAIS chemins de
production : `grading/cache.py` + `app_state.redis`, provider LLM simulé à
latence contrôlée.

## Méthodologie

- **Provider LLM simulé** : `asyncio.sleep(200 ms ± 80 ms)` par appel —
  représente le coût d'un appel LLM réel (le pipeline complet est dominé par
  la latence du provider).
- **Redis simulé** : implémentation in-memory de l'API `redis.asyncio`
  utilisée par `grading/cache.py` (get/setex/set nx/ex/exists/delete/eval CAS)
  — les chemins de code sont identiques à la prod (single-flight Lua compris).
- **Réponses** : copies SVT réalistes en arabe (passent le sanity check →
  cacheables).
- **Machine** : sandbox CI (CPU partagé) — les valeurs absolues dépendent de
  la machine ; les RATIOS (économie d'appels, hit vs miss) sont
  représentatifs du comportement en prod.
- Relance : `python scripts/benchmark_cache.py` (variante rapide `--quick`,
  latence LLM réglable `--llm-ms 150`). Résultats détaillés →
  `data/benchmark_cache_results.json`.

## Résultats (run du 2026-08-08, LLM simulé 200 ms ± 80 ms)

### 1. Single-flight — 30 élèves concurrents, même copie

| Métrique | Valeur |
|---|---|
| Corrections | 30 |
| **Appels LLM** | **1** (économie **96.7 %**) |
| Hit rate | 96.7 % (29 hits / 1 miss) |
| Mur | 1.40 s |
| Latence ressentie p50 / p95 / p99 | 224 ms / 225 ms / 1.40 s |
| Latence HIT p50 / p99 | 224 ms / 225 ms |
| Latence MISS (1er élève) | 1.40 s |

→ Le pic de classe (30 élèves sur la même question en même temps) coûte
**1 seul appel LLM** ; les 29 autres élèves reçoivent la même note en ~224 ms
(même latence que le miss — ils attendent juste la fin de la correction).

### 2. Miss puis Hit — 50 copies uniques re-soumises (100 corrections)

| Métrique | Valeur |
|---|---|
| Corrections | 100 |
| **Appels LLM** | **50** (économie **50 %**) |
| Hit rate | 50 % (50 hits / 50 misses) |
| **Latence HIT p50 / p99** | **162 µs / 326 µs** |
| **Latence MISS p50 / p99** | **182 ms / 277 ms** |

→ Un hit est **~1 100× plus rapide** qu'un miss : la re-soumission d'une
copie déjà corrigée coûte des microsecondes (sanity + hash + lookup Redis),
pas un appel LLM.

### 3. Concurrence mixte — 10 questions × 10 élèves (100 corrections)

| Métrique | Valeur |
|---|---|
| Corrections | 100 |
| **Appels LLM** | **10** (économie **90 %**) |
| Hit rate | 90 % (90 hits / 10 misses) |
| Mur | 0.30 s |
| Latence ressentie p50 / p95 / p99 | 219 ms / 280 ms / 280 ms |

→ Le single-flight s'applique **par clé** (question × verbe × réponse) :
chaque question ne coûte qu'un appel LLM même si 10 élèves répondent
pareil en même temps.

## Interprétation

1. **Single-flight vérifié en conditions réalistes** : le verrou par clé
   (CAS Lua + double-check) fusionne bien les corrections concurrentes —
   c'est le mécanisme qui protège le budget LLM pendant les pics de classe.
2. **Le cache amortit la latence LLM** : p99 hit ≈ 300 µs contre ~200-280 ms
   miss. Pour un utilisateur qui réessaie ou corrige une copie déjà vue, la
   réponse est instantanée.
3. **Le sanity pré-check ne coûte rien** : les 30/50/100 corrections passent
   par `check_answer_sanity` (µs) avant le lookup — le rejet d'une copie
   invalide reste déterministe et gratuit (jamais de lookup ni d'appel LLM).
4. **Contrat Public respecté** : les résultats simulés (source `llm_v2`,
   `parse_status=ok`, `sanity_code=ok`) sont bien cacheables ; un résultat
   dégradé (source hors whitelist, sanity ≠ ok) est refusé au store
   (`skip_uncacheable`) — l'équité prime sur la perf.

## Limites

- Mono-process : le partage inter-nœuds (vrai Redis réseau) n'est pas
  mesuré ici — le comportement du single-flight multi-workers dépend de la
  latence réseau Redis (lock 30 s, double-check après attente).
- La latence LLM simulée est fixe ; en prod elle varie selon le provider
  (cf. alerte `LLMDeadline` p99 > 20 s).
- Le pipeline complet (sanity → savoir → prompt → LLM → parser → mapping →
  post-validation) n'est pas inclus : seul le wrapper cache + provider simulé
  sont exercés (le savoir local et le LLM réel sont couverts par les tests
  golden, pas par ce benchmark de charge).
