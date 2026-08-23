# Loadtest — trajets métier (locust)

Premier test de charge du système (audit 100k §5.3 / grille G0-4 + §A).
Objectif : **remplacer les inférences par des chiffres mesurés** (« le premier
chiffre mesuré du système »).

## Contenu

- `locustfile.py` — profil « un élève » :
  - inscription **une seule fois** (compte unique, pas de login par requête)
  - navigation légère : `GET /api/manhadjiya/verbs`, `GET /api/manhadjiya/verb/{slug}`
  - remédiation contextuelle : `POST /api/manhadjiya/contextual-remediation` (pur mémoire, R6)
  - **trajet critique** : `POST /api/document-analysis/evaluate-v2` (soumission + correction)

Pondération du mix : 3 navigation + 3 remédiation + 1 correction (par défaut,
`LT_EVAL_WEIGHT`). Attente entre requêtes : 2–6 s (rythme élève).

## Prérequis

Un backend démarré avec une base seeded (les 11 scénarios) :

```bash
# 1) serveur local (SQLite, mode déterministe — 0 LLM externe)
cd khawarizmi-backend
DATABASE_URL="sqlite+aiosqlite:///./lt.db" SECRET_KEY=loadtest-secret-key-at-least-32-bytes GEMINI_API_KEY=test \
  ENVIRONMENT=ci .venv/bin/uvicorn main:app --port 8100

# 2) seed des scénarios (PYTHONPATH requis — le seed passe par l'état de l'app)
PYTHONPATH=. DATABASE_URL="sqlite+aiosqlite:///./lt.db" \
  .venv/bin/python -c "import asyncio; from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession; from app_state import state; from database import ensure_dialect_for_url; url='sqlite+aiosqlite:///./lt.db'; ensure_dialect_for_url(url); state.db_engine=create_async_engine(url); state.db_session=async_sessionmaker(state.db_engine, class_=AsyncSession, expire_on_commit=False); import scripts.seed_document_analysis as s; asyncio.run(s.seed())"
```

## Lancer le run (headless, rapport HTML + JSON)

```bash
cd khawarizmi-backend
LT_PLAN=pro LT_SECRET=<SECRET_KEY du serveur> \
.venv/bin/locust -f loadtest/locustfile.py --headless \
    --host http://127.0.0.1:8100 -u 10 -r 1 -t 90s \
    --only-summary --json-file /tmp/lt-run --html /tmp/lt.html
```

| Variable | Rôle |
|---|---|
| `LT_PLAN` | `free` (défaut) = les 15 éval/h font **partie** de la mesure (rate limit = objet de charge) · `pro` = 80/h, mesure le trajet seul |
| `LT_SECRET` | requis si `LT_PLAN=pro` (forge un JWT pro pour l'user créé) |
| `LT_SCENARIO_ID` | slug du scénario seeded (défaut `gene-expression-protein-disorder-v1`) |
| `LT_EVAL_WEIGHT` | poids du trajet critique dans le mix (défaut 1) |

> ⚠️ `--json-file X` écrit `X.json` (locust ajoute l'extension).

## Interprétation (SLO §C de la grille)

- **p95 correction (sync) ≤ 8 s** : les runs de 2026-08-21 (mode local)
  mesurent p95 = 11 ms à 10 users et p99 = 700 ms à 30 users — **le LLM
  externe est la variable dominante** (R11 : p99 1,40 s avec LLM simulé
  200 ms ± 80 ms). Un run avec clés réelles sur une instance contrôlée est
  nécessaire pour valider le SLO en conditions réelles.
- **Taux 5xx < 0,5 %** : les runs de référence sont à **0 %** — surveiller à
  l'échelle (pool DB 10+20, R2).
- Le run 30 users sature partiellement le CPU **du sandbox** (1 worker
  uvicorn) — à refaire sur Railway (la cible réelle) avant de conclure.

Rapport de référence : `docs/loadtest/rapport-premier-run-2026-08-21.md`.
