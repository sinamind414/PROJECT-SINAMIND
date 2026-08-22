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
| 3 | **Coût LLM cadré + plafond actif** | §B rempli + budget alert + kill-switch | ⬜ §B rempli (R17) + **compteur journalier + alerte budget + kill-switch livrés et testés** (R18 : 8 tests, suite 1032 verts) ; reste à définir le budget prod dans Railway (défaut 2,00 $/jour) | **Moi** (code) ✅ + **Toi** (décision budget) | R17 ✅ + R18 ✅ + LLM_DAILY_BUDGET_USD choisi |
| 4 | **Charge mesurée sur le trajet critique** | p95 + taux 5xx sous les SLO (§C) | ⬜ **premier run locust mesuré** (R16 : p95 11 ms / 0 échec à 10 users, p99 700 ms à 30 users — mode local, LLM hors circuit) ; re-mesure LLM réel sur Railway requise | **Moi** (locust, scénarios métier) | rapport locust ✅ (R16) + run LLM réel sur Railway |
| 5 | **Rate limits partagés + testés** | Redis en prod + 1 test de rate limit | ❌ partiel : **9 tests verts + BUG clé-IP trouvé et corrigé** (R15) ; compteurs toujours par instance sans Redis (R7) | **Moi** (tests) + **Toi** (Redis prod) | test vert ✅ (R15) + Redis connecté au /health |
| 6 | **Code prod à jour** | dernier fix déployé sur Railway | ✅/⬜ : tout est sur master (`8f1481f`) mais le redéploiement Railway n'est pas confirmé | **Toi** | version affichée par `/health` |

## G1 — Requis avant le pic (pré-bac)

| # | Critère | Seuil binaire | État (reçu) | Owner | Preuve à fournir |
|---|---|---|---|---|---|
| 7 | **ONNX récupéré** | RAG sémantique actif (`is_semantic=true`) | ❌ pointeur LFS non téléchargé (R8) | **Toi** (`git lfs pull`) | log « Embedder ONNX initialisé » |
| 8 | **LLM async/queue** | si et seulement si #4 l'impose | ⬜ conditionnel à #4 | **Moi** | décision chiffrée + impl |
| 9 | **Rollout progressif + critères d'abort** | §D rempli et validé | ⬜ | **Toi** | §D daté |
| 10 | **Revue légale 18-07** | avis écrit (mineurs, LLM tiers, rétention) | ⬜ | **Toi + juriste** | avis daté |
| 11 | **Multi-tenant (établissements/classes)** | isolation vérifiée OU renonciation écrite (B2C pur) | ❌ absent du schéma — seul `wilaya` existe (R12) | **Toi** (décision de besoin) | schéma ou renonciation |
| 12 | **Données élèves hachées partout** | aucune copie en clair, logs revus | ✅ partiel : hachage présent (R10) ; **revue des logs datée FAITE** (R19 : 0 fuite dans les logs applicatifs, 1 point mineur corrigé) ; F1/F2/F4 → revue légale (G1-10) | **Moi + Toi** | revue des logs ✅ (R19) + revue légale 18-07 |

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

**Premiers chiffres mesurés (R16, 2026-08-21 — mode local, 1 worker sandbox)** :
trajet critique p50 **10 ms** / p95 **11 ms** à 10 users (3,3 req/s) ·
**10,4 req/s soutenus, 0 échec** à 30 users · p99 monte à 700 ms à 30 users
(contention CPU sandbox, pas encore le goulot de prod). Rapport :
`docs/loadtest/rapport-premier-run-2026-08-21.md`.

## §B — Modèle de coût (exécutable — R17)

La formule tourne : `scripts/llm_cost_model.py` (re-exécutable à chaque
calibration, `--from-log cost_log.jsonl` pour les tokens réels).

Formule : `coût/élève/mois = éval/j × (1−cache) × (1−local) × [(tok_in×p_in + tok_out×p_out)/1M] × 30`

| Paramètre | Bas | Médian | Haut | Source |
|---|---|---|---|---|
| Évaluations LLM / élève / jour | 2 | 5 | 10 | fourchette hypothétique — **à mesurer** (usage réel) |
| Taux de hit cache | 50 % | 30 % | 0 % | fourchette hypothétique — **à mesurer** (single-flight R2 aide) |
| % résolu par étages locaux | 40 % | 20 % | 0 % | fourchette hypothétique — **à mesurer** |
| Tokens moyens (in + out) | 150 + 80 | 150 + 80 | 150 + 80 | **mésurés** `cost_log.jsonl` (n=18) (R17) |
| Prix Gemini 2.5 Flash / M tokens | 0,15 / 1,25 $ | 0,15 / 1,25 $ | 0,30 / 2,50 $ | **daté 2026-08-21** : Google AI Studio / agrégateur OpenRouter (R17) |
| **Coût / élève / mois** | **0,0022 $** | **0,0103 $** | **0,0735 $** | calcul (R17) |

| Scénario | $ /élève/mois | 10 000 élèves actifs | 100 000 élèves actifs |
|---|---|---|---|
| Bas | 0,0022 $ | **22 $/mois** | **220 $/mois** |
| Médian | 0,0103 $ | **103 $/mois** | **1 029 $/mois** |
| Haut | 0,0735 $ | **735 $/mois** | **7 350 $/mois** |

Lecture : même au pire scénario raisonnable, le coût LLM n'est **pas**
contraignant à 100k — ce qui le devient, c'est la **latence** (R11) et le
plafonnement par quota (R1/R15). Le vrai chiffre viendra des 3 cases
« à mesurer » (usage réel, cache, local) — les remplacez par des chiffres
mesurés dans le script, pas dans ce tableau.

**Garde-fous présents [vérifié]** : quota 15 éval/h/élève (R1) ·
cache single-flight + TTL (R2) · **circuit breaker par provider LLM** (R13) ·
étage savoir 0 token (R5) · **compteur de coût journalier + alerte budget +
kill-switch** (R18). **Reste** : canal d'alerte sortant (email/Sentry) sur
BUDGET_KILL, compteurs multi-instances (nécessite Redis).

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
- **R15** `pytest tests/test_rate_limit.py` → 9 passed · suite complète : 1024 passed / 10 skipped / 5 xfailed · **bug trouvé puis corrigé** : `_get_user_plan` (rate_limit.py) échouait sur tous les tokens réels (sub int → `JWTClaimsError: Subject must be a string`) → clé rate-limit retombait sur l'IP (compteur unique 15/h par IP, tier pro 80/h jamais appliqué) → fix `options={"verify_sub": False}` (pattern déjà documenté dans deps.get_current_user) · contresens du grep R7 corrigé : 7 décorateurs dans le code dont 2 sur des modules non montés (gel 2026-08-17) → 5 plafonds vivants au runtime
- **R16** locust 2.46.3 headless (`loadtest/locustfile.py`, 10 users/90 s puis 30 users/60 s, uvicorn 1 worker sandbox, SQLite seedé 11 scénarios, mode déterministe local 0 LLM) → run 1 : 297 req / 0 échec / trajet critique p50 10 ms · p95 11 ms · p99 15 ms · run 2 : 623 req / 10,4 req/s / 0 échec / p50 10 ms · p95 20 ms · p99 700 ms (saturation CPU sandbox) · rapport : `docs/loadtest/rapport-premier-run-2026-08-21.md`
- **R17** `python scripts/llm_cost_model.py --from-log cost_log.jsonl` → tokens moyens **mésurés** 150 in / 80 out (n=18) · tarifs Gemini 2.5 Flash datés 2026-08-21 (Google AI Studio 0,15/1,25 $/M · OpenRouter 0,30/2,50 $/M, recherches web du jour) · sortie : 0,0022 / 0,0103 / 0,0735 $/élève/mois (bas/médian/haut) → 22–735 $/mois à 10k actifs, 220–7 350 $/mois à 100k
- **R18** `pytest tests/test_llm_budget.py` → 8 passed · suite complète : 1032 passed / 10 skipped / 5 xfailed · **`services/llm_budget.py`** : compteur de coût par jour UTC + dépassement → coupure auto du LLM externe jusqu'à minuit + alerte `BUDGET_KILL` (CRITICAL, greppable) · kill-switch manuels `LLM_KILL` (global) / `LLM_KILL_FEATURES` (par feature, sans redémarrage) · intégration dans `_call_with_fallback` (porte d'entrée unique) + 4 call sites (evaluate/tutor/engine) + garde `call_llm` · **l'usage réel (tokens) est désormais enregistré EN PRODUCTION** (cost_log.jsonl + compteur — avant, le logger n'avait aucun appelant) · état exposé dans `/health` (`business.llm_budget`) · effet de bord tests corrigé (COST_LOG_PATH isolé dans conftest + gitignore) · **alertes sortantes (ce turn)** : Sentry `capture_message` fatal (no-op si DSN absent) + webhook `BUDGET_ALERT_WEBHOOK` (POST JSON, thread fond, 3 s, 1×/jour de coupure) + métriques Prometheus (`llm_budget_day_cost_usd` / `_auto_killed` / `_kills_total`) · `pytest tests/test_llm_budget.py` → 12 passed, suite 1036 verts
- **R19** Revue des logs données élèves (G1-12, rapport `docs/mvp-manhadjia/revue-logs-donnees-eleves-2026-08-21.md`) : balayage `logger.*`/`raise`/`str(req)` sur services+routes+grading → **0 fuite de contenu élève dans les logs** · audit trail corrections = hash uniquement · Sentry = défauts SDK protecteurs + capture BUDGET_KILL sans PII · 1 point mineur corrigé (sortie LLM loguée en entier sur échec de parse → troncature 200 car., services/llm.py:313) · signalé à la revue légale (G1-10) : F1 prompts LLM en clair (cœur du produit), F2 tunnel_events.payload jsonb client, F4 données fonctionnelles en base · suite 1036 verts après fix

## Verdict (forme binaire, pas narrative)

- **G0 compteur** : 2 ❌ (CI, rate limits testés) + 3 ⬜ (backup/restore, coût, charge) + 1 ✅/⬜ (déploiement) → **NO-GO en l'état**.
- **G1 compteur** : 2 ❌ (ONNX, multi-tenant) + 1 ✅ partiel (hachage) + 3 ⬜ (async, rollout, légal).
- **La seule ligne qui débloque tout le reste : G0-1 (CI)** — owner : toi, 5 minutes, UI GitHub.
