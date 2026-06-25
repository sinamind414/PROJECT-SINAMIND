# Khawarizmi Backend

API REST de la plateforme IA Khawarizmi Pro — Bac SVT Algérie.

## Stack technique

- **Framework** : FastAPI (Python 3.12)
- **Base de données** : PostgreSQL 16 + pgvector
- **Cache** : Redis 7
- **IA** : Gemini 2.5 Flash / OpenAI GPT (fallback)
- **Auth** : JWT (python-jose + bcrypt)
- **Répétition** : FSRS Graph
- **Deploy** : Railway (Docker)

## Structure

```
khawarizmi-backend/
├── main.py            → Entrypoint (< 100 lignes)
├── config.py           → Settings Pydantic
├── auth.py             → JWT uniquement
├── database.py         → PostgreSQL asyncpg
├── cache.py            → Redis
├── models/             → SQLAlchemy ORM
├── schemas/            → Pydantic validation
├── routes/             → Endpoints REST
├── services/           → Logique métier
├── methodology/        → Moteur méthodologique
├── bac_blanc/          → Évaluation intelligente
├── migrations/         → Alembic
└── tests/              → Pytest (≥ 50% coverage)
```

## Règles de sécurité

- **JWT uniquement** — Pas de double système d'auth
- **SECRET_KEY** — Obligatoire (ValueError si absent en prod)
- **Rate limiting** — SlowAPI sur les endpoints IA
- **CORS restreint** — Méthodes et headers limités

## Commandes

```bash
uvicorn main:app --reload        # Développement
pytest tests/ -v                  # Tests
alembic upgrade head              # Migrations
```

## Références

- `AGENTS.md` — Règles absolues du projet

---

**Projet :** IA Khawarizmi Pro — Bac Sciences Naturelles Algérie
