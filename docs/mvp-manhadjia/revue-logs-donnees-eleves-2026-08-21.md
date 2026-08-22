# Revue des logs — données élèves en clair (2026-08-21)

> G1-12 de la grille go-no-go-100k : « aucune copie en clair, **logs revus** ».
> Cette revue est la partie « logs revus » (côté Moi). Périmètre : backend
> (logs applicatifs, exceptions/Sentry, stores d'audit). Datée, re-runnable.

## Verdict

**Aucune fuite de contenu élève dans les logs applicatifs** — balayage
systématique (grep `services/`, `routes/`, `grading/`) : aucun `logger.*`
n'interpole le contenu d'une réponse élève, aucun `str(req)`/`repr(req)`,
aucune exception portant le contenu brut. Un point mineur corrigé (F3).

## Ce qui est VÉRIFIÉ propre (avec preuves)

| # | Point | Preuve |
|---|---|---|
| 1 | **Hachage des réponses** : HMAC-SHA256 avec pepper serveur (`SECRET_KEY`), refusa explicit si pas de pepper (pas de fallback public) | `services/hashing.py` (`hash_answer`) |
| 2 | **Audit trail corrections** : stocke UNIQUEMENT des hash (`student_answer_hash`, `prompt_hash`, `error_message_hash`) — jamais le contenu brut | `services/correction_audit.py` (INSERT + docstring « jamais le contenu brut ») |
| 3 | **Logs applicatifs** : seuls des identifiants transitent (user_id, question_id, verb_slug, scores, provider) — ex. `eval_v2 \| user=30 scenario=… score=0/0`, `FALLBACK_L2 \| user=… q=… reason=…` | balayage grep `logger.*` services/ routes/ grading/ |
| 4 | **Pas de body de requête dans les logs** : aucun `str(req)` / `repr(req)` / `{req}` | balayage grep |
| 5 | **Exceptions** : aucun `raise` n'embarque de contenu élève → rien à capturer automatiquement par Sentry via les tracebacks | balayage grep `raise …(reponse\|answer)` |
| 6 | **Sentry** : seul usage manuel = `capture_message` BUDGET_KILL (R18, sans PII) ; SDK avec défauts protecteurs (`send_default_pii=False`, `data_scrubbing=True` — aucun override dans `config.py`) | `services/llm_budget.py`, `config.py:init_sentry` |
| 7 | **Chatbot** : `logger.exception("ask_stream_failed")` — traceback seul, pas le message | `routes/chatbot.py:261` |

## Points signalés (périmètre de la revue légale G1-10 — pas des bugs)

- **F1 — Les prompts LLM portent la réponse élève en clair** vers des
  providers externes (Gemini/GLM/OpenAI) — c'est le cœur du produit.
  C'est L'objet de la revue 18-07 (mineurs + LLM tiers), déjà listée
  (audit §3 #7). Aucun changement code possible sans changer le produit.
- **F2 — `tunnel_events.payload` (jsonb) stocke le payload client tel quel**
  (`services/kunz_tunnel_service.py:70`) — le contenu dépend des événements
  envoyés par le front. Store de données fonctionnel (recall), pas un log :
  à inventorier dans la revue légale.
- **F4 — Chat historique / données d'apprentissage en base** : stockage
  fonctionnel (rappel, progression) — périmètre revue légale, hors logs.

## Corrigé dans cette revue

- **F3 — Sortie LLM loguée en entier** sur échec de parse JSON
  (`services/llm.py:313`) : le modèle peut citer la réponse de l'élève ;
  le message d'exception transitait le contenu complet (logs/Sentry).
  → **tronqué à 200 caractères** (fix dans ce commit, R19).

## Recommandations

- **R-A** (fait, F3) : troncature du contenu LLM dans les messages
  d'exception/erreur.
- **R-B** : en prod, vérifier que le DSN Sentry conserve les défauts SDK
  (`send_default_pii=False`) — à noter dans le runbook de la revue 18-07.
- **R-C** : si de nouveaux endpoints loguent des requêtes, ajouter un test
  de non-révélation (pattern : envoyer une réponse marquée, asserter
  qu'elle n'apparaît pas dans les logs capturés).

## Reçu (R19)

- Balayage : `grep -rnE "logger\.\w+\(f?…\{(reponse|answer|…)" services/ routes/ grading/` → 0 occurrence de contenu élève
- `grep -rn "raise …(reponse|answer)"` → 0 occurrence
- `grep -n "send_default_pii|data_scrubbing|before_send" config.py` → 0 (défauts SDK protecteurs)
- Fix F3 appliqué : `services/llm.py` (troncature 200 car.)
- Suite backend : 1036 passed / 10 skipped / 5 xfailed (après fix)
