# Patchs d'infrastructure à appliquer à la main

Ce dossier n'est pas une salle d'attente de confort : **la CI de ce dépôt n'a
pas été modifiée depuis des mois**, et `LOCAL_RUBRIC_GRADER` n'a jamais été
posé sur Railway pour cette raison. Le blocage est administratif, pas
technique.

## `ci-prod-wiring.patch` — `.github/workflows/ci.yml`

**Pourquoi ce fichier n'est pas commité sur la branche** : le proxy Git utilisé
par l'agent (GitHub App) n'a pas la permission `workflows`. `git push` est
**refusé en entier** dès qu'un commit touche `.github/workflows/**` :

> refusing to allow a GitHub App to create or update workflow
> `.github/workflows/ci.yml` without `workflows` permission

Laisser le commit en local rendrait la branche impushable indéfiniment (chaque
push rejouerait l'historique). Le correctif est donc livré ici, à appliquer par
quelqu'un qui a le droit — toi, depuis l'interface GitHub ou ton `gh` personnel.

**Ce qu'il change, et pourquoi chacun des trois points compte :**

| Changement | Effet mesuré avant |
|---|---|
| `on.push/pull_request: branches: [main]` → `[master]` + `workflow_dispatch` | `main` n'existe pas dans ce dépôt (`git ls-remote`) → **le workflow ne tournait jamais**. Un `next build` rouge a pu atterrir sur `master` et y rester (rapport §10, patch F24 écrit le 2026-08-30, jamais appliqué). |
| `deploy-railway` : `if: github.ref == 'refs/heads/main'` → `if: github.event_name == 'workflow_dispatch'` | Le déploiement de prod ne peut plus être l'**effet de bord** d'un push. Il devient un geste délibéré, déclenché depuis Actions → CI/CD Khawarizmi Pro → *Run workflow*. |
| Nouveau job `prod-wiring`, `if: vars.PROD_API_ORIGIN` qui lance `khawarizmi-backend/scripts/verify_prod_api.py --front vars.PROD_FRONT_ORIGIN --back vars.PROD_API_ORIGIN` | La question « le front est-il branché sur un backend qui sert **ce** dépôt, et la correction est-elle allumée ? » devient une **constante rouge/verte** au lieu d'une opération artisanale. Job **sauté** tant que `vars.PROD_API_ORIGIN` / `vars.PROD_FRONT_ORIGIN` ne sont pas renseignés (Settings → Secrets and variables → Actions → Variables) — pas de vert mensonger par absence de test. |

## Appliquer

```bash
git apply docs/patches-todo/ci-prod-wiring.patch && git add .github/workflows/ci.yml
git commit -m "ci(workflows): triggers sur master, deploy-railway manuel, job prod-wiring"
git push origin arena/01a05476-project-sinamind
```

Ou, sans clone : éditer `.github/workflows/ci.yml` dans l'interface GitHub en
reprenant le contenu du patch (les trois hunks sont autonomes), et commiter.

Après application, contrôler que le fichier du dépôt est bien identique au
patch appliqué :

```bash
git apply --check --reverse docs/patches-todo/ci-prod-wiring.patch && echo "appliqué"
```

Une fois ce patch appliqué **sur la branche**, le supprimer d'ici.
