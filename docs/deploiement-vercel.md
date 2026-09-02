# Déploiement Vercel — Khawarizmi Pro (frontend Next.js)

Le frontend est un Next.js 16 standard, **déjà prêt pour Vercel** :
proxy de l'API dans `src/app/api/[...path]/route.ts` (route handler Node qui
lit l'origine **à chaque requête**), rewrite `/health` dans `next.config.ts`
(empreinte de vérification), analytics `@vercel/analytics` inclus. Aucun
`vercel.json` nécessaire.

> ⚠️ Depuis F32 (rapport §19), `/api/*` **n'est plus** un rewrite de
> `next.config.ts`. Une destination de rewrite est figée **au build**, alors
> que la CI ne re-déploie que Railway : chaque changement de domaine du
> backend recassait la production sans commit ni CI rouge. Le handler, lui,
> se reconfigure en éditant une variable d'environnement.

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

| Variable | Où | Valeur |
|---|---|---|
| `API_ORIGIN` | Vercel | l'origine publique du backend, sans `/api` (ex. `https://<service>.up.railway.app`). **Lue à la requête** → changer de domaine = éditer + redeployer, pas re-builder |
| `NEXT_PUBLIC_API_URL` | Vercel | même valeur ; sert encore la CSP (`connect-src`) et le rewrite `/health`. `API_ORIGIN` a la priorité |
| `LOCAL_RUBRIC_GRADER` | Railway | `true` — sinon `/api/grade` retombe sur un LLM, ou échoue si aucun provider n'est configuré (`config.py` : défaut `False`) |
| `SAVOIR_REMEDIATION_ENABLED` | Railway | `true` si tu assumes les seuils de remédiation par verbe (défaut `False`) |

Le navigateur n'appelle que le propre domaine du front (`/api/...`) : pas de
CORS à déclarer, `connect-src 'self'` suffit. Cross-origin direct n'est
nécessaire que si tu Pointes `NEXT_PUBLIC_API_URL` hors proxy — auquel cas
l'origine doit être dans `get_allowed_origins()` **et** dans la CSP.

⚠️ En l'absence des deux variables, le proxy retombe sur
`http://localhost:8000` — ce n'est correct qu'en dev. En prod le handler ne
tombe nulle part : il répond **501 `{"code":"api_origin_non_configuré",
"attendu":"… sans /api"}` avant tout fetch**, pour que la panne lisible soit
« variable manquante » et non « le backend est cassé » (un 502 réseau aurait
fait perdre deux jours, c'est exactement ce qui est arrivé à D1).

Tout est lu par **un seul résolveur**, `src/lib/api-origin.ts` : la CSP
(`connect-src`), le rewrite `/health` et le proxy runtime partagent la même
origine. Changer l'un des trois sans les autres ne peut plus arriver.

## 4. Vérifier après déploiement

```bash
# 0) tout d'un coup — verdict par empreinte, exit 1 si le branchement n'est pas bon :
python3 khawarizmi-backend/scripts/verify_prod_api.py \
    --front https://<votre-app>.vercel.app --back https://<service>.up.railway.app
#   A « amont ≠ ce dépôt » (le /health répond « OK » en texte brut, ou 404 {"message","requestId"})
#   B « le proxy du front ne suit pas » (501 = variable absente, 404 inconnu = rewrite fantôme)
#   C « drapeaux éteints » (LOCAL_RUBRIC_GRADER absent de /health → correction silencieusement hors service)
#   Le même script doit tourner en CI : voir docs/patches-todo/ — le job `prod-wiring` est écrit
#   mais PAS encore appliqué (le proxy Git de l'agent n'a pas la permission `workflows`, `git push`
#   est refusé sur .github/workflows/**). À appliquer à la main : sans lui, cette vérification reste
#   une faveur que tu te fais à toi-même, pas une garde.

# 1) le proxy du front atteint-il le bon backend ?
curl -s https://<votre-app>.vercel.app/health
#   → un OBJET JSON de diagnostic (routes/health.py). « OK » en texte brut = autre chose que ce dépôt.

# 2) la forme d'erreur prouve que c'est CE backend (routes/errors.py) :
curl -s https://<votre-app>.vercel.app/api/inexistant
#   → {"erreur":…,"status":404,"path":"/api/inexistant","method":"GET"}
#   → {"message","requestId"} = un autre projet (c'est ainsi que khawarizmi-backend.railway.app a été démasqué)

# 3) une page qui dépend de l'API doit répondre, sinon D1 est toujours là :
curl -s -o /dev/null -w '%{http_code}\n' https://<votre-app>.vercel.app/api/manhadjiya/verbs
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
