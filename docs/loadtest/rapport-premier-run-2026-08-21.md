# Premier run de charge — chiffres mesurés (2026-08-21)

> Audit 100k §5.3 : « test de charge locust sur `/api/manhadjiya/*` +
> évaluation → **le premier chiffre mesuré du système** (remplace toute
> inférence) ». Ce rapport est ce premier chiffre. Grille G0-4 + §A.

## Conditions du run

| Paramètre | Valeur |
|---|---|
| Date | 2026-08-21 (20:53–20:56 UTC) |
| Cible | backend uvicorn, **1 worker**, CPU sandbox (≈ 2 cœurs) |
| Base | SQLite locale, 11 scénarios / 55 questions seedés |
| Mode IA | **déterministe local** (`ENVIRONMENT=ci`) — 0 appel LLM externe |
| Redis | absent (cache C2 inopérant, rate limit en mémoire) |
| ONNX | fallback bag-of-ngrams (modèle LFS non téléchargé — R8) |
| Comptes | `pro` (JWT forgé) — le rate limit est isolé de la mesure |
| Mix | 3 navigation manhadjiya + 3 remédiation + 1 correction (trajet critique) |

**Limite majeure (à ne pas oublier)** : le LLM externe est désactivé. Les
latences ci-dessous mesurent l'ossature (routes, DB SQLite, pipeline local,
sanity/fallback) — **pas la latence Gemini**, variable dominante (R11).

## Run 1 — 10 users / 90 s (ramp 1/s)

**297 requêtes, 0 échec, 3,3 req/s.**

| Endpoint | N | avg (ms) | p50 | p95 | p99 | max |
|---|---|---|---|---|---|---|
| **POST /api/document-analysis/evaluate-v2** (trajet critique) | 24 | 10 | **10** | **11** | 15 | 15 |
| POST /api/manhadjiya/contextual-remediation | 103 | 3 | 3 | 4 | 5 | 6 |
| GET /api/manhadjiya/verbs | 85 | 5 | 4 | 6 | 9 | 9 |
| GET /api/manhadjiya/verb/{slug} (5 verbes) | 85 | 2 | 2 | 3 | 4 | 4 |

## Run 2 — 30 users / 60 s (ramp 3/s)

**623 requêtes, 0 échec, 10,4 req/s.**

| Endpoint | N | avg (ms) | p50 | p95 | p99 | max |
|---|---|---|---|---|---|---|
| **POST /api/document-analysis/evaluate-v2** | 43 | 35 | **10** | **20** | 700 | 703 |
| GET /api/manhadjiya/verbs | 196 | 14 | 4 | 13 | 520 | 523 |
| POST /api/manhadjiya/contextual-remediation | 188 | 11 | 3 | 7 | 480 | 611 |
| GET /api/manhadjiya/verb/{slug} | 196 | 2–18 | 2 | 3–5 | 4–520 | 523 |

À 3× la charge, **p50 inchangé** (10 ms sur le trajet critique) mais **p99
monte à 700 ms** — contention de l'événement loop sur un CPU sandbox avec
1 worker. C'est le premier signal de saturation du système testé (pas encore
le goulot de prod).

## Lecture par rapport aux SLO §C (propositions)

| SLO | Mesure (mode local) | Verdict |
|---|---|---|
| p95 correction (sync) ≤ 8 s | **11 ms** (10u) / 20 ms (30u) | ✅ à 100× — **mais** avec LLM réel : p99 1,40 s mesuré LLM simulé (R11) + latence Gemini → **à re-mesurer avec clés réelles** avant validation |
| Taux 5xx < 0,5 % / 24 h | **0 %** sur 920 requêtes | ✅ (échantillon petit) |
| Disponibilité 99,5 % | non mesurable ici | ⬜ (besoin d'un run long sur Railway) |

## Prochaine mesure (la seule qui vaille pour le pic)

1. Instance Railway (cible réelle, pas le sandbox) + clés LLM réelles.
2. `LT_PLAN=free` pour mesurer le comportement du rate limit **sous charge**
   (15/h par user — R15 : la clé par user fonctionne désormais).
3. Monter la charge par paliers (30 → 100 → 300 users) jusqu'au premier
   dépassement de p95 = 8 s → ce point **est** le goulot (pool DB 10+20 ?
   1 worker uvicorn ? LLM ?).
4. Remplir le §A de la grille avec `req/s_pic` réel → dimensionner.

## Fichiers

- `khawarizmi-backend/loadtest/locustfile.py` — le scenario
- `khawarizmi-backend/loadtest/README.md` — mode d'emploi
- Rapports bruts (non versionnés, ~1 Mo) : `locust-10u-90s.{json,html}`,
  `locust-30u-60s.json`
