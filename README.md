# IA Khawarizmi Pro

Plateforme éducative IA destinée aux lycéens algériens préparant le Bac Sciences Naturelles.

## Mission

Transformer la préparation au Bac SVT grâce à l'intelligence artificielle :
diagnostic précis, feedback ultra-spécifique, répétition espacée (FSRS),
mind maps dynamiques et évaluation méthodologique intelligente.

## Architecture

```
PROJECT-SINAMIND/
├── khawarizmi-backend/     → FastAPI + PostgreSQL + Redis
├── khawarizmi-frontend/    → Next.js 16 + React 19 + TailwindCSS 4
└── docs/                   → Documentation technique
```

## Lancement

### Docker (recommandé)
```bash
docker compose up --build
```

### Local
```bash
# Backend
cd khawarizmi-backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd khawarizmi-frontend
npm install
npm run dev
```

## Structure des dossiers

### Backend (`khawarizmi-backend/`)
- `main.py` — Point d'entrée FastAPI (< 100 lignes)
- `config.py` — Configuration Pydantic centralisée
- `auth.py` — JWT uniquement
- `database.py` — PostgreSQL + asyncpg
- `cache.py` — Redis
- `models/` — Modèles SQLAlchemy
- `schemas/` — Schémas Pydantic
- `routes/` — Endpoints REST
- `services/` — Logique métier (RAG, FSRS, AI, Mindmap)
- `methodology/` — Moteur méthodologique (verbs, diagnostic, feedback)
- `bac_blanc/` — Couche 3 évaluation intelligente
- `migrations/` — Alembic
- `tests/` — Pytest (13 fichiers, couverture ≥ 50%)

### Frontend (`khawarizmi-frontend/`)
- `src/app/` — Pages Next.js App Router
- `src/components/` — Composants React
- `src/lib/` — Utilitaires, hooks, contextes
- `src/styles/` — Styles globaux

## Règles de sécurité

- **JWT uniquement** — Pas de localStorage token, pas de Supabase Auth
- **SECRET_KEY obligatoire** — ValueError si absent en production
- **Rate limiting** — SlowAPI sur `/api/chat` et `/api/evaluate`
- **CORS restreint** — Méthodes et headers limités
- **Clés API** — Jamais dans le code, toujours dans `.env`

## Scripts de test

```bash
# Backend
cd khawarizmi-backend
pytest tests/ -v

# Frontend
cd khawarizmi-frontend
npm run lint
```

## Références

- `AGENTS.md` — Règles absolues du projet (prompt développeur)
- `docs/` — Documentation technique détaillée
- `.env.example` — Template de configuration

---

**Projet :** IA Khawarizmi Pro — Bac Sciences Naturelles Algérie
