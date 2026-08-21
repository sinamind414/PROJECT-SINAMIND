# Audit « prêt pour 100 000 élèves ? » — v2 (après contre-audit)

> Réécrit le 2026-08-21 après le retour adversarial (5 lentilles). Chaque
> affirmation est étiquetée : **[vérifié]** (commande + sortie dans l'annexe
> Reçus), **[inféré]** (déduit du code, non mesuré), **[supposé]** (hypothèse
> à confirmer). Pas de pourcentage de « readiness » : il ne serait pas dérivable.

## 1. Ce qui est vrai aujourd'hui (3 faits vérifiés, 3 inférences)

1. **[vérifié]** Le produit fonctionne de bout en bout sur un backend SQLite
   local : 1015 tests backend verts, 799 tests frontend, 176 opérations HTTP
   sans 500 (Reçus R3–R5).
2. **[vérifié]** Manhadjia (le contenu le plus poussé) coûte ~0 à l'échelle :
   statique + 1 endpoint pur-mémoire de 42 ms (Reçu R6).
3. **[vérifié]** L'évaluation LLM est plafonnée par utilisateur :
   **15/heure** (80/heure si abonnement « pro ») — `rate_limit.py:38`
   (Reçu R1). Un abonné gratuit ne peut pas générer plus de ~360 évaluations
   LLM/jour, même en attaquant volontairement.
4. **[inféré]** Le cache de correction (single-flight + TTL, Reçu R2) réduit
   le coût LLM des copies répétées (copier-coller entre élèves) — ampleur
   réelle inconnue, jamais mesurée sur du trafic réel.
5. **[inféré]** Le pool de connexions (10 + 20 overflow, Reçu R2) suffit pour
   un trafic modéré ; personne ne sait ce qu'il encaisse à 500 req/s.
6. **[inféré]** Le rate limit par utilisateur ne couvre que **6 fichiers de
   routes** (Reçu R7) : les autres endpoints publics (waitlist, seed, feedback…)
   ne sont pas plafonnés — un scraper peut les marteler. Gravité faible
   (coût proche de zéro) mais déni de service possible.

## 2. Ce que je ne sais pas (et que le rapport v1 aurait dû dire)

- Le trafic réel que Railway/ton conteneur encaisse (aucun test de charge
  n'existe — Reçu R4).
- Les limites réelles de ton plan Railway (CPU, connexions, régions) :
  **[supposé]** standard.
- Le plafond global Gemini de ta clé API : **[supposé]** jamais atteint à ce
  jour.
- **Ta date de lancement** — le v1 parlait de « avant le bac » sans calendrier.
  Donne-moi la date (ou la semaine visée) et je dérive le planning en
  semaines avec marges.
- Le nombre d'évaluations LLM par élève actif et par jour : indispensable
  au modèle de coût, je n'ai aucun chiffre d'usage réel.

## 3. Registre des risques (pre-mortem intégré)

| # | Risque | Statut |
|---|---|---|
| 1 | CI cassé sur master (workflow invalide, runs 0 s) | **[vérifié]** — le run du merge échoue au parse (Reçu R9) |
| 2 | Fix production du dialect PostgreSQL absent de la prod déployée ? | **[vérifié]** le fix est sur master depuis le merge (`8f1481f`) ; **[supposé]** que Railway redéploie master |
| 3 | Modèle ONNX manquant → RAG sémantique en fallback dégradé | **[vérifié]** (pointeur LFS, Reçu R8) |
| 4 | Coût LLM non modélisé | **[vérifié]** aucun budget/usage dans le repo ; **[inféré]** 12 fichiers de services appellent le LLM (Reçu R5) |
| 5 | Attaque de coût sur les évaluations | **[vérifié]** parée partiellement (15/h/élève) mais **aucun test** du rate limit (Reçu R7) |
| 6 | Railway = SPOF | **[supposé]** — aucune multi-région/plan de sortie dans le repo |
| 7 | Données de mineurs | **[vérifié]** les copies sont hachées avant stockage (README, architecture-moteurs-audit) ; **[supposé]** la conformité à la loi algérienne 18-07 (équivalent RGPD DZ) et l'envoi de textes de mineurs à un LLM tiers n'ont jamais été revus par un juriste |
| 8 | Une correction aberrante qui circule sur les réseaux | **[supposé]** — aucun plan de communication/correction publique prévu |
| 9 | Burnout du développeur solo | **[supposé]** — c'est toi, et le v1 empilait 6 chantiers sans ordre |
| 10 | Redis absent → rate limits par instance (non partagés) | **[vérifié]** code : sans Redis, stockage en mémoire par process (`rate_limit.py:41-46`) |

## 4. TA prochaine action — une seule

**Corriger le workflow CI sur master, via l'interface GitHub (aucun PAT requis).**

1. Ouvre https://github.com/sinamind414/PROJECT-SINAMIND/blob/master/.github/workflows/ci.yml
2. Bouton crayon (Edit) → supprime tout → colle le contenu de
   `docs/ci/ci.yml.corrigee` (il est dans ton repo, validé YAML).
3. Commit direct sur `master` (« ci: workflow valide + schedule nightly »).

C'est le point le plus rentable : tout le reste (tests, smokes, garde-fous)
ne protège personne tant que le CI ne tourne pas sur master. (J'ai vérifié
que ni `git push` ni l'API REST ne passent avec mon token — permission
`workflows` refusée, Reçu R9 — l'UI de TON compte la contourne.)

## 5. Ordre d'exécution après ça (pas de choix artificiel)

1. **Toi (5 min)** : workflow CI via l'UI (§4) → vérifier un run vert sur master.
2. **Toi (2 min)** : `git lfs pull --include 'khawarizmi-backend/models/minilm_onnx_int8/*'` (Reçu R8).
3. **Moi (code)** : test de charge locust sur `/api/manhadjiya/*` + `/api/evaluate` →
   le premier chiffre mesuré du système (remplace toute inférence).
4. **Moi (code)** : modèle de coût LLM — `coût/élève/mois = f(évaluations/jour,
   % cache hit, % étage local)`, exécutable, pas un tableau d'opinions.
5. **Toi** : me donner la date de lancement + le plan Railway (je dérive le
   calendrier et les marges).
6. **Toi + juriste** : revue 18-07 (mineurs, LLM tiers, rétention) — c'est le
   seul chantier que ni moi ni un test ne peut clore.

## 6. Ce que j'accepte du contre-audit, et ce que je conteste (avec reçus)

**Accepté** — « ~80 % » (non dérivable), « 500–2000 req/s » (inventé),
« tu étais mort avant le premier élève » (dramatisation), le choix (a)/(b)
(engagement, pas conseil), « Moi (je peux tout écrire) » (propriété fictive —
corrigé en « Moi = exécution code, Toi = décision »), l'ouverture
sycophantique, le calendrier absent, les risques 5–10 du §3.

**Contesté** — deux affirmations de la critique étaient vérifiables et fausses :
- « le rapport ignore le RGPD » : le hachage des copies est **dans le code**
  (Reçu R10) — le manque réel est la revue 18-07/LLM tiers (§3 #7).
- « 12 services » traité comme fausse précision : c'était un **grep**
  (Reçu R5), pas un chiffre inventé.

## Annexe — Reçus (commandes réellement exécutées le 2026-08-21)

- **R1** `grep -n "def evaluate_limit" khawarizmi-backend/rate_limit.py` →
  `return "80/hour" if (key and ":pro" in key) else "15/hour"` (ligne 38)
- **R2** `grep pool_size …/lifespan.py` → `{"pool_size": 10, "max_overflow": 20}`
  · `grading/cache.py` → `_single_flight(key, ttl=30)` + `CORRECTION_CACHE_TTL`
- **R3** `pytest tests/ -q` → `1015 passed, 10 skipped, 5 xfailed`
- **R4** `ls tests/*load* tests/*perf*` → rien · `npx vitest run` frontend → `799 passed`
- **R5** `grep -rln "call_gpt4o|chat.completions|gemini|call_llm" services/` → **12 fichiers**
- **R6** `POST /api/manhadjiya/contextual-remediation` via proxy → 42 ms, 15 erreurs officielles
- **R7** `grep -c "@limiter.limit" routes/*.py` → 6 fichiers seulement ·
  `ls tests/*rate*` → aucun test de rate limit
- **R8** `check_onnx_asset.py` → `STATUT : LFS — pointeur non téléchargé (134 octets, réel ≈ 118 Mo)` ·
  batch API LFS répond, CDN de contenu bloqué du sandbox (HTTP 000)
- **R9** `gh api PUT …/contents/.github/workflows/ci.yml` → `403 Resource not accessible by integration` ·
  `gh run list --branch master` → `failure … workflow file issue … 0s`
- **R10** `grep -rni "rgpd" README.md` → « Les réponses élèves sont hachées (SHA-256)… jamais stockée en clair »
