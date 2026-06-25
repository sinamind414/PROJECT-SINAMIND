# IA Khawarizmi Pro

Plateforme éducative IA pour les lycéens algériens préparant le Bac Sciences Naturelles.

## Architecture

```
khawarizmi-backend/    → FastAPI + PostgreSQL 16 + pgvector
khawarizmi-frontend/   → Next.js 16 + React 19 + TailwindCSS 4
```

## Stack technique

- **Backend** : FastAPI + Python 3.12
- **Base** : PostgreSQL 16 + pgvector
- **Cache** : Redis 7
- **IA** : Gemini 2.5 Flash (principal) / Groq Llama (failover)
- **Auth** : JWT (python-jose + bcrypt)
- **Répétition** : FSRS Graph
- **Frontend** : Next.js 16 + React 19 + TailwindCSS 4
- **Mobile** : React Native + Expo 56

## Lancement

### Docker (recommandé)

```bash
docker compose up --build
```

### Local — Backend

```bash
cd khawarizmi-backend
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Local — Frontend

```bash
cd khawarizmi-frontend
npm install
npm run dev
```

## Règles de sécurité

- JWT uniquement pour l'authentification
- Aucune clé API dans le code
- Rate limiting sur /api/chat et /api/evaluate
- SECRET_KEY requis en production (lève ValueError si absent)

## Documentation

- `AGENTS.md` — Prompt développeur et règles absolues
- `khawarizmi-backend/AGENTS.md` — Règles backend
- `khawarizmi-frontend/AGENTS.md` — Règles frontend

## Tests

```bash
cd khawarizmi-backend
pytest tests/ --asyncio-mode=auto -v
```
