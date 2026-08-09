# Déploiement Vercel — Khawarizmi Pro (frontend Next.js)

Le frontend est un Next.js 16 standard, **déjà prêt pour Vercel** :
rewrites API dans `next.config.ts` (proxy `/api/*` et `/health` vers le
backend), analytics `@vercel/analytics` inclus. Aucun `vercel.json`
nécessaire (les rewrites Next sont appliqués nativement par Vercel).

## 1. Prérequis — le backend doit être déployé et public

Le frontend ne fait que du proxy : il faut une URL publique du backend
FastAPI. Options :

- **Railway** (déjà prévu : job `deploy-railway` dans
  `docs/ci/ci.yml.amelioree` avec `RAILWAY_TOKEN`) — l'URL finale ressemble
  à `https://khawarizmi-production.up.railway.app` ;
- **Render / Fly.io / serveur VPS** — n'importe quel hébergement uvicorn ;
- ⚠️ Vercel ne peut PAS héberger le backend seul (FastAPI ≠ serverless Next,
  et les workers de réconciliation + FSRS ont besoin d'un process long).

## 2. Import sur Vercel (1 clic, sans CLI)

1. Aller sur https://vercel.com/new
2. **Import Git Repository** → sélectionner `sinamind414/PROJECT-SINAMIND`
   (le dépôt est déjà sur GitHub — Vercel demande l'autorisation GitHub,
   c'est VOUS qui la donnez, aucune clé à coller ici).
3. Framework preset : **Next.js** (détecté automatiquement).
4. Root directory : **`khawarizmi-frontend`** ← important (le dépôt est un
   monorepo backend + frontend).
5. Build command : `npm run build` · Output : `next start` (défauts).

## 3. Variables d'environnement (Project Settings → Environment Variables)

| Variable | Valeur |
|---|---|
| `NEXT_PUBLIC_API_URL` | l'URL publique du backend, ex. `https://khawarizmi-production.up.railway.app` (sans `/api`) |

Les rewrites de `next.config.ts` deviennent alors :
`/api/:path*` → `https://<backend>/api/:path*` (proxy serveur — le
navigateur ne voit jamais l'URL du backend).

⚠️ En l'absence de `NEXT_PUBLIC_API_URL`, le rewrite retombe sur
`http://localhost:8000` — valable en dev local UNIQUEMENT.

## 4. Vérifier après déploiement

```bash
curl -s https://<votre-app>.vercel.app/health   # → JSON du backend (proxy OK)
```

- Le déploiement échoue au build si le frontend n'est pas dans la root
  directory configurée (monorepo).
- `npm run build` est hermétique (pas de Google Fonts runtime).

## 5. Notes

- Le backend en preview/demo tourne avec SQLite + mode local déterministe
  (0 LLM). En production : Postgres (migrations Alembic 001→034) + Redis
  (cache C2) + `ENABLE_EXTERNAL_LLM=1` + clé OpenAI.
- Le preview Arena (sandbox) démarre déjà le site complet : backend
  `uvicorn` + frontend `next dev`, proxy `/api` inclus — voir la réponse
  du sandbox (LIVE PREVIEW).
