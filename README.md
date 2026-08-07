# IA Khawarizmi Pro

Plateforme éducative IA destinée aux lycéens algériens préparant le Bac Sciences Naturelles.

## Mission

Transformer la préparation au Bac SVT grâce à l'intelligence artificielle :
diagnostic précis, feedback ultra-spécifique, répétition espacée (FSRS),
mind maps dynamiques et évaluation méthodologique intelligente.

> **Fonctionne sans clé API :** tout le moteur pédagogique (chatbot, correcteur,
> RAG) dispose d'un fallback local déterministe (TF-IDF + regex + embeddings locaux).
> Les providers externes (OpenAI/Groq/Gemini…) ne sont activés que si
> `ENABLE_EXTERNAL_LLM=1` **et** une clé sont configurés (`services/llm_guard.py`).

## Architecture

```
PROJECT-SINAMIND/
├── khawarizmi-backend/     → FastAPI + PostgreSQL + Redis (+ mode preview SQLite)
├── khawarizmi-frontend/    → Next.js 16 + React 19 + TailwindCSS 4
└── docs/                   → Documentation technique
```

## Lancement

### Docker (recommandé)
```bash
cd khawarizmi-backend
docker compose up --build
```

### Local
```bash
# Backend (mode preview SQLite : aucune base requise, tables auto-créées)
cd khawarizmi-backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
export SECRET_KEY=votre-cle-min-16-caracteres
uvicorn main:app --reload

# Frontend
cd khawarizmi-frontend
npm install
npm run dev
```

## Structure des dossiers

### Backend (`khawarizmi-backend/`)
- `main.py` — Point d'entrée FastAPI (< 100 lignes)
- `config.py` — Configuration Pydantic centralisée (SECRET_KEY obligatoire en prod)
- `auth.py` — JWT uniquement
- `database.py` — PostgreSQL + asyncpg (ou SQLite preview auto-alter)
- `cache.py` — Redis (avec repli silencieux)
- `routes/` — 189 endpoints REST (voir `routes/__init__.py` pour le registre)
- `services/` — Logique métier (RAG, FSRS, AI, Mindmap, correcteur…)
- `services/correction_v2.py` — Correcteur hybride : sanity → LLM → fallback local L2
- `services/llm_guard.py` — Garde-fou : 0 appel externe sans double opt-in
- `methodology/` — Moteur méthodologique (verbs, diagnostic, feedback)
- `migrations/` — Alembic (30 migrations)
- `tests/` — Pytest (57 fichiers, 632 tests)

### Frontend (`khawarizmi-frontend/`)
- `src/app/` — Pages Next.js App Router
- `src/components/` — Composants React
- `src/lib/` — Utilitaires, hooks, contextes
- `src/styles/` — Styles globaux

## Règles de sécurité

- **JWT uniquement** — Pas de localStorage token, pas de Supabase Auth
- **SECRET_KEY obligatoire** — ValueError si absent en production
- **Rate limiting** — SlowAPI sur `/api/chatbot/*` et `/api/*/evaluate` (Redis si dispo)
- **CORS restreint** — Méthodes et headers limités
- **Clés API** — Jamais dans le code, toujours dans `.env`
- **RGPD** — Les réponses élèves sont hachées (SHA-256) dans la base d'audit et `da_answers`
- **Admin** — Les endpoints analytics élèves exigent `X-Admin-Token` = `ADMIN_SECRET`

## Scripts de test

```bash
# Backend (632 tests)
cd khawarizmi-backend
export SECRET_KEY=ci-test-key-for-smoke-tests-only ENVIRONMENT=ci
export DATABASE_URL=sqlite+aiosqlite:///./ci_test.db
python -m pytest tests/ -q

# Frontend (592 tests)
cd khawarizmi-frontend
npm run lint
npm run test
npm run build   # build 100 % hermétique (police locale, aucune dépendance réseau)
```

## Références

- `AGENTS.md` — Règles absolues du projet (prompt développeur)
- `audit-technique-global.md` — Audit global (architecture, routes, sécurité)
- `audit-correcteur.md` — Audit du moteur de correction
- `audit-livre-corrige.md` — Audit + alignement du livre officiel SVT 3AS
- `rapport-tests-routes.md` — Tests bout-en-bout des routes
- `.env.example` — Template de configuration

---

**Projet :** IA Khawarizmi Pro — Bac Sciences Naturelles Algérie
