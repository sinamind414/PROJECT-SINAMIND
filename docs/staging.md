# Staging Deployment — Khawarizmi Pro

## Architecture

```
┌──────────────────────┐     ┌──────────────────────┐
│   Vercel (Frontend)  │────▶│  Railway (Backend)   │
│                      │     │                      │
│  NEXT_PUBLIC_API_URL │     │  KHAWARIZMI-IA       │
│  ──────────────────▶ │     │  (FastAPI + PGVector) │
└──────────────────────┘     └──────────────────────┘
                                      │
                            ┌─────────┴─────────┐
                            │ Postgres + Redis   │
                            │ (managed addons)   │
                            └────────────────────┘
```

## Railway Backend

### 1. Create staging environment

```bash
railway login
railway link
railway environment create staging
```

### 2. Add addons

```bash
railway add --environment staging postgres
railway add --environment staging redis
```

### 3. Set environment variables

```bash
railway variables set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(64))")
railway variables set ENVIRONMENT=staging
railway variables set VERSION=2.0.0-rc.1
railway variables set GEMINI_API_KEY=<your-gemini-key>
railway variables set OPENAI_API_KEY=<your-openai-key>
railway variables set SENTRY_DSN=<your-sentry-dsn>
```

Railway auto-sets `DATABASE_URL` and `REDIS_URL` when addons are linked.

### 4. Deploy

```bash
railway up --environment staging
```

### 5. Verify

```bash
railway open --environment staging
# Opens browser → /health endpoint
# Should return: {"status": "healthy", "database": "connected", "redis": "connected"}
```

## Vercel Frontend

### 1. Create project

```bash
cd khawarizmi-frontend
vercel link
```

### 2. Set environment variable

```bash
vercel env add NEXT_PUBLIC_API_URL production
# Value: https://<your-backend-staging>.up.railway.app
```

### 3. Deploy

```bash
vercel --prod
```

### 4. Verify

```bash
vercel open
# Opens browser → check /auth/login renders
```

## Minimum Environment Variables

### Backend (Railway)

| Variable | Required | Example |
|----------|----------|---------|
| `SECRET_KEY` | YES | `python -c "import secrets; print(secrets.token_hex(64))"` |
| `DATABASE_URL` | YES | Auto-set by Railway addon |
| `REDIS_URL` | YES | Auto-set by Railway addon |
| `ENVIRONMENT` | YES | `staging` |
| `GEMINI_API_KEY` | YES | AI provider key |
| `OPENAI_API_KEY` | no | Fallback AI provider |
| `SENTRY_DSN` | no | Error monitoring |
| `ALLOWED_ORIGINS` | no | Comma-separated extra CORS origins |

### Frontend (Vercel)

| Variable | Required | Example |
|----------|----------|---------|
| `NEXT_PUBLIC_API_URL` | YES | `https://khawarizmi-ia-staging.up.railway.app` |

## Smoke Checklist

After deploy, verify:

- [ ] GET `/health` returns `{"status": "healthy", "database": "connected", "redis": "connected"}`
- [ ] POST `/api/auth/register` creates a user
- [ ] POST `/api/auth/login` returns a token
- [ ] GET `/api/auth/me` returns user data
- [ ] GET `/api/programme/SVT/Sciences%20Naturelles` returns programme
- [ ] POST `/api/chat` with a question returns an AI response
- [ ] Frontend `/auth/login` renders
- [ ] Frontend `/auth/register` creates user and redirects to `/dashboard`

## Local Staging (optional)

For local testing with staging-like config:

```bash
cd khawarizmi-backend
DATABASE_URL=postgresql+asyncpg://khawarizmi:khawarizmi_pass@localhost:5432/khawarizmi_test \
REDIS_URL=redis://localhost:6379/1 \
ENVIRONMENT=staging \
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(64))") \
uvicorn main:app --port 8000

cd khawarizmi-frontend
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```
