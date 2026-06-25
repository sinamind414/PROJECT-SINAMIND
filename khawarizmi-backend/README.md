# Khawarizmi Pro — Backend

API FastAPI de la plateforme éducative IA.

## Stack

- **Framework** : FastAPI (Python 3.12)
- **Base** : PostgreSQL 16 + pgvector
- **Cache** : Redis 7
- **Auth** : JWT (python-jose + bcrypt)
- **ORM** : SQLAlchemy 2.0 (async) + Alembic
- **IA** : Gemini 2.5 Flash / Groq Llama / OpenAI GPT

## Structure

```
main.py       ← Entrypoint (max 100 lignes)
config.py     ← Settings Pydantic
auth.py       ← JWT uniquement
database.py   ← Connexion DB
cache.py      ← Redis
routes/       ← Endpoints API
services/     ← Logique métier
models/       ← Modèles SQLAlchemy
schemas/      ← Schémas Pydantic
migrations/   ← Alembic
tests/        ← Pytest
```

## Sécurité

- JWT vérifié sur chaque endpoint protégé
- Rate limiting sur /api/chat et /api/evaluate (slowapi)
- SECRET_KEY requis en production
- Aucune clé API exposée dans le code

## Commandes

```bash
uvicorn main:app --reload --port 8000
alembic upgrade head          # Migrations
pytest tests/ -v --tb=short   # Tests
ruff check .                  # Lint
mypy .                        # Typecheck
```

## Documentation

Voir `AGENTS.md` pour les règles de contribution.
