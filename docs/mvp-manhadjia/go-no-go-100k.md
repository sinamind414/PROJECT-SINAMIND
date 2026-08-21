# GO / NO-GO — Lancement 100 000 élèves (grille binaire)

> Livrable demandé par le dernier contre-audit : « une page go/no-go chiffrée,
> pas un nouveau narratif ». Règles d'usage :
> - Chaque ligne est **binaire** : ✅ GO · ❌ NO-GO · ⬜ NON VÉRIFIÉ.
> - ⬜ compte comme NO-GO jusqu'à preuve fournie.
> - Verdict global = **ET logique** de toutes les lignes de G0. Pas de note
>   chiffrée, pas de pourcentage.
> - Colonne « État » toujours sourcée par un reçu (annexe R1–R13). Une case
>   vide = à remplir par son owner, pas une opinion de l'auteur.

---

## G0 — Bloquants absolus (avant le premier élève externe)

| # | Critère | Seuil binaire | État (reçu) | Owner | Preuve à fournir |
|---|---|---|---|---|---|
| 1 | **CI vert sur master** | 1 run vert sur le dernier push | ❌ workflow invalide, runs 0 s (R9) | **Toi** (UI GitHub, pas de PAT requis) | lien du run vert |
| 2 | **Backup + restore drill** | restore réellement testé, RPO/RTO écrits | ⬜ aucune trace dans le repo (R14) | **Toi + Railway** | capture du restore + RPO/RTO choisis |
| 3 | **Coût LLM cadré + plafond actif** | §B rempli + budget alert + kill-switch | ⬜ modèle absent, alerte budgétaire absente | **Moi** (code) + **Toi** (décision budget) | §B rempli + config de quota |
| 4 | **Charge mesurée sur le trajet critique** | p95 + taux 5xx sous les SLO (§C) | ⬜ benchmarks.md existe mais **LLM simulé** (R11) | **Moi** (locust, scénarios métier) | rapport locust réel (login, soumission, correction) |
| 5 | **Rate limits partagés + testés** | Redis en prod + 1 test de rate limit | ❌ partiel : 15/h/élève vérifié (R1), mais **0 test** (R7) et compteurs par instance sans Redis (R7) | **Moi** (tests) + **Toi** (Redis prod) | test vert + Redis connecté au /health |
| 6 | **Code prod à jour** | dernier fix déployé sur Railway | ✅/⬜ : tout est sur master (`8f1481f`) mais le redéploiement Railway n'est pas confirmé | **Toi** | version affichée par `/health` |

## G1 — Requis avant le pic (pré-bac)

| # | Critère | Seuil binaire | État (reçu) | Owner | Preuve à fournir |
|---|---|---|---|---|---|
| 7 | **ONNX récupéré** | RAG sémantique actif (`is_semantic=true`) | ❌ pointeur LFS non téléchargé (R8) | **Toi** (`git lfs pull`) | log « Embedder ONNX initialisé » |
| 8 | **LLM async/queue** | si et seulement si #4 l'impose | ⬜ conditionnel à #4 | **Moi** | décision chiffrée + impl |
| 9 | **Rollout progressif + critères d'abort** | §D rempli et validé | ⬜ | **Toi** | §D daté |
| 10 | **Revue légale 18-07** | avis écrit (mineurs, LLM tiers, rétention) | ⬜ | **Toi + juriste** | avis daté |
| 11 | **Multi-tenant (établissements/classes)** | isolation vérifiée OU renonciation écrite (B2C pur) | ❌ absent du schéma — seul `wilaya` existe (R12) | **Toi** (décision de besoin) | schéma ou renonciation |
| 12 | **Données élèves hachées partout** | aucune copie en clair, logs revus | ✅ partiel : hachage présent (R10) ; logs Sentry non revus | **Moi + Toi** | revue des logs datée |

---

## §A — Modèle de charge (à remplir, pas à deviner)

Formule : `req/s_pic = (DAU × %_actifs_au_pic × req_par_élève) / (fenêtre_pic_h × 3600)`

| Paramètre | Valeur | Source |
|---|---|---|
| Élèves inscrits | ___ | Toi |
| DAU (actifs/jour) | ___ | analytics (absent ? à brancher) |
| % actifs au pic (19h–21h) | ___ | à mesurer |
| Req par élève et par session | ___ | à mesurer (benchmarks.md = 1 trajet simulé, R11) |
| Fenêtre de pic | ___ h | Toi |
| **req/s attendu au pic** | **= calcul ci-dessus** | — |
| Marge de sécurité | **× 3** | règle standard |
| **req/s cible pour le test de charge** | **= req/s × 3** | — |

Contraintes déjà mesurées : pool DB `10 + 20` (R2) · cache single-flight (R2) ·
latence d'un trajet avec LLM simulé p50 224 ms / p99 1,40 s (R11 — LLM réel :
à re-mesurer, c'est la variable dominante).

## §B — Modèle de coût (à remplir, fourchettes obligatoires)

Formule : `coût/élève/mois = éval/j × (1 − hit_cache) × (1 − %_local) × (tok_in + tok_out) × prix_par_Mtok × 30`

| Paramètre | Bas | Médian | Haut | Source |
|---|---|---|---|---|
| Évaluations LLM / élève / jour | ___ | ___ | ___ | à mesurer (usage réel) |
| Taux de hit cache | ___ | ___ | ___ | à mesurer (single-flight R2 aide) |
| % résolu par étages locaux (savoir/manhadjia) | ___ | ___ | ___ | à mesurer |
| Tokens moyens (in + out) | ___ | ___ | ___ | à mesurer (logs) |
| Prix Gemini / M tokens | ___ | ___ | ___ | **à relever sur la page tarifaire Gemini, daté** |
| **Coût / élève / mois** | **=** | **=** | **=** | calcul |

Exemple **fictif** (à remplacer, ne pas citer) : 5 éval/j, 0 % cache, 0 % local,
2 000 tokens, 1 $/M → 0,30 $/élève/mois → **3 000 $/mois à 10k élèves actifs**,
30 000 $/mois à 100k actifs. Le chiffre réel dépend des 5 cases vides.

**Garde-fous déjà présents [vérifié]** : quota 15 éval/h/élève (R1) ·
cache single-flight + TTL (R2) · **circuit breaker par provider LLM** (R13) ·
étage savoir 0 token (R5). **Absents [vérifié]** : alerte budgétaire globale,
kill-switch par feature, compteurs de coût par jour.

## §C — SLO proposés (à ajuster — ce sont des propositions, pas des faits)

| SLO | Valeur proposée | Statut |
|---|---|---|
| p95 correction d'évaluation (sync) | ≤ 8 s | proposition |
| p95 correction (async) | ≤ 60 s | proposition |
| Taux d'erreur 5xx | < 0,5 % sur 24 h | proposition |
| Disponibilité (hors maintenance annoncée) | 99,5 % | proposition |
| Délai d'annonce de maintenance | ≥ 24 h | proposition |

## §D — Plan de rollout (à remplir)

| Phase | Seuil | Critères d'abort (⚠️ un seul suffit) | Date | Owner |
|---|---|---|---|---|
| Pilote | 1 % (~1 000 élèves) | 5xx > 1 % · coût/jour > budget · 1 correction aberrante virale | ___ | Toi |
| Région | 10 % | idem + plaintes enseignants > seuil | ___ | Toi |
| Moitié | 50 % | idem + SLO §C violés 2 jours consécutifs | ___ | Toi |
| Complet | 100 % | idem | ___ | Toi |

## §E — Ordre d'exécution (adopté du dernier contre-audit)

| Ordre | Action | Owner concret |
|---|---|---|
| 1 | CI vert sur master (UI GitHub, 5 clics) | **Toi** |
| 2 | Backup + restore drill | **Toi + Railway** |
| 3 | Modèle de coût + plafonds (code : compteurs, alertes) | **Moi** (code), **Toi** (budget) |
| 4 | Test de charge sur trajets métier | **Moi** (locust) |
| 5 | Async/queue **si** #4 l'impose | **Moi** |
| 6 | Scale horizontal **après** identification du goulot | **Toi + Moi** |

---

## Annexe — Reçus (commandes exécutées)

- **R1** `grep "def evaluate_limit" rate_limit.py` → `"80/hour" if ":pro" else "15/hour"` (l.38)
- **R2** `grep pool_size lifespan.py` → `10 + 20` · `grading/cache.py` → `_single_flight(ttl=30)` + `CORRECTION_CACHE_TTL`
- **R5** `grep -rln "call_gpt4o|chat.completions|gemini|call_llm" services/` → 12 fichiers
- **R7** `grep -c "@limiter.limit" routes/*.py` → 6 fichiers · `ls tests/*rate*` → aucun
- **R8** `check_onnx_asset.py` → `STATUT : LFS (134 o, réel ≈ 118 Mo)` · CDN sandbox bloqué
- **R9** `gh run list --branch master` → `failure … workflow file issue … 0s` · API REST → 403 permission
- **R10** `grep -rni "rgpd" README.md` → « réponses élèves hachées (SHA-256)… jamais en clair »
- **R11** `docs/benchmarks.md` → p50 224 ms / p95 225 ms / p99 1,40 s — **LLM simulé 200 ms ± 80 ms** (run 2026-08-08)
- **R12** `grep -rn "etablissement|classe" models/ migrations/` → **rien** (seul `wilaya` dans `schemas/user.py`)
- **R13** `services/llm.py:32-39` → « Budget global + circuit breaker (audit C3)… un breaker par provider » · `tenacity==9.1.4` dans requirements
- **R14** `grep -rn "backup" lifespan.py config.py` → aucune trace

## Verdict (forme binaire, pas narrative)

- **G0 compteur** : 2 ❌ (CI, rate limits testés) + 3 ⬜ (backup/restore, coût, charge) + 1 ✅/⬜ (déploiement) → **NO-GO en l'état**.
- **G1 compteur** : 2 ❌ (ONNX, multi-tenant) + 1 ✅ partiel (hachage) + 3 ⬜ (async, rollout, légal).
- **La seule ligne qui débloque tout le reste : G0-1 (CI)** — owner : toi, 5 minutes, UI GitHub.
