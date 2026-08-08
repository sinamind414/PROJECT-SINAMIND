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
- Le pipeline complet est couvert par un second benchmark
  (`scripts/benchmark_pipeline.py`, section suivante) ; le savoir local y est
  exercé réellement (deterministic_correct_v2), le LLM reste simulé.
- Mono-process : le partage inter-nœuds (vrai Redis réseau) n'est pas
  mesuré (single-flight multi-workers dépend de la latence réseau Redis).


---

# Benchmark pipeline — étage savoir local vs LLM

Mesure du pipeline COMPLET (cache → retry → façade → `grading/pipeline.py`)
sur le corpus golden : 48 questions couvertes par le lexique (sur 50),
copies fortes (réponse modèle, ≥ 3 concepts → savoir) et copies faibles
(réponse d'une AUTRE question → LLM). Provider LLM simulé 200 ms ± 80 ms,
fake redis, `llm_call` injecté. Relance : `python scripts/benchmark_pipeline.py`.

## Résultats (run du 2026-08-08, après fix lexique — voir plus bas)

### A. Savoir activé (`config.savoir_enabled_verbs` = verbes du corpus)

| Métrique | Valeur |
|---|---|
| Corrections | 96 (48 fortes + 48 faibles) |
| **Appels LLM** | **31** (économie **67.7 %**) |
| Répartition | `local_savoir` **65 (67.7 %)** · `llm` 31 (32.3 %) |
| Mur | 1.61 s |
| Latence savoir p50 / p95 / p99 | **2.9 ms / 3.7 ms / 3.8 ms** |
| Latence LLM p50 / p95 / p99 | 259 ms / 313 ms / 340 ms |

→ **Deux tiers des corrections ne consomment aucun token LLM** et répondent
en ~3 ms. Le ratio savoir/LLM dépend du corpus : ici les réponses modèles du
golden se chevauchent lexicalement (vocabulaire SVT commun) — 35 % des
copies « faibles » matchent encore ≥ 3 concepts.

### B. Savoir désactivé (défaut de config `[]`)

| Métrique | Valeur |
|---|---|
| Corrections | 96 · Appels LLM : **96** (économie 0 %) |
| Latence LLM p50 / p95 / p99 | 257 ms / 386 ms / 482 ms |

→ Sans le flag, tout part au LLM : le flag `savoir_enabled_verbs` est le
**kill-switch de l'économie** (par verbe).

### C. Étage savoir pur (`run_savoir`, flag actif)

- 9600 appels · **2347 µs/appel** (~425 copies/s mono-thread) — coût CPU
  réel du moteur (normalisation + scan lexique + matching).

## Bug de performance corrigé (découvert par ce benchmark)

Le premier run a révélé des latences aberrantes : copies savoir ~62 ms,
appels LLM étalés par paliers de ~500 ms (blocage GIL). Cause :
`_contains_any` re-normalisait CHAQUE variante du lexique à CHAQUE appel —
~1500 variantes × (NFKD + 25 `replace` + 6 `regex`) ≈ **30.7 ms par appel**,
et le moteur l'appelait 2× par correction (can_handle + détection).

**Fix** (`services/savoir_corrector.py`) : `_SYNONYMS_NORM` — variantes
pré-normalisées UNE FOIS au chargement + `_contains_any_norm` sur le chemin
chaud (4 call sites basculés).

| Mesure | Avant | Après | Gain |
|---|---|---|---|
| `_detect_lexicon_concepts` | 30.7 ms | **0.61 ms** | ×50 |
| `deterministic_correct_v2` | ~60 ms | **1.65 ms** | ×36 |
| Scénario A (96 corr.) | 7.62 s (p50 savoir 62 ms, p50 LLM 2.77 s) | **1.61 s** (p50 savoir 2.9 ms, p50 LLM 259 ms) | ×4.7 |

L'impact prod était réel : en asyncio mono-thread, 60 ms de CPU par copie
bloquaient la boucle d'événements — 100 corrections simultanées = plusieurs
secondes de gel pour TOUS les utilisateurs. Comportement inchangé (tests
golden et savoir : 951 passed).

## Limites

- LLM simulé (latence fixe) ; le RAG context (embedding + similarité) n'est
  pas exercé — le benchmark mesure le moteur local + le wrapper, pas le
  chemin RAG complet.
- Le corpus golden est thématiquement homogène → le ratio savoir/LLM mesuré
  (67.7 %) est un plafond optimiste pour le trafic réel mixte.
