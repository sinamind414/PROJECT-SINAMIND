# Audit du rapport « Audit Technique PROJECT-SINAMIND » — vérifié pièce par pièce

> **Date** : 2026-08-18 · **Branche** : `arena/01a0066d-project-sinamind` (HEAD `fcd1b18`)
> **Objet** : le rapport technique collé dans le fil (78 problèmes : 9 CRITIQUE, 26 MAJEUR, 30 MINEUR, 13 INFO).
> **Méthode** : chaque affirmation vérifiée contre les fichiers réels, ligne par ligne. Faits ≠ avis. Ce document ne modifie rien.
> **Rapport audité sans commit déclaré** : les vérifications portent sur l'arbre courant ; une ligne fausse peut venir d'un autre instantané (comme le rapport 62/100 qui auditait `d6591c1`).

---

## 0. Verdict en une ligne

**Le meilleur audit technique de toute notre file** — précision de lignes remarquable (~35 affirmations vérifiées, une seule fausse) — mais sa **faute est paradoxalement son action prioritaire n°1** : le « SyntaxError critique de config.py:146 » **n'existe pas**. L'application démarre (prouvé des dizaines de fois cette session) et 965 tests passent sur ce même fichier. En revanche, l'IDOR de `social.py` est **réel et grave** — c'est le seul vrai CRITIQUE que nos 13 actes d'audit ont manqué.

---

## 1. La réfutation — le CRITIQUE qui n'existe pas

| Affirmation du rapport | Réalité du fichier |
|---|---|
| « config.py:146 : SyntaxError, parenthèse fermante manquante dans `list(set(base_origins + extra_origins)`, l'import du module est impossible, **l'application ne démarre pas** » | `config.py:146-148` : `all_origins = list(set(base_origins + extra_origins))` — **syntaxiquement correct, parenthèses complètes**. Preuve par l'exécution : le backend a démarré ~20 fois cette session, 965 tests passent, `import config` OK. |

**Conséquence** : l'action #1 du plan « immédiat 0-48 h » (« Corriger le SyntaxError, 5 min ») n'a **rien à corriger**. Le rapport s'est probablement basé sur un instantané antérieur ou une lecture tronquée. C'est le seul point factuellement faux sur ~40 vérifiés — mais il est en tête de son plan d'action, ce qui fausse la priorisation.

---

## 2. Les confirmations — tout le reste, avec preuves

### 2.1 Le vrai CRITIQUE (celui que notre chaîne a manqué)

| # | Affirmation | Preuve (fichier réel) |
|---|---|---|
| **IDOR** | `GET /conversations/{cid}/messages` lit les messages **sans vérifier que l'utilisateur est membre de la conversation** | `routes/social.py:109-115` — `SELECT m.* … WHERE m.conversation_id = :cid` + `Depends(get_current_user)` seul. **Tout élève connecté peut lire toute conversation en itérant les ids.** CRITIQUE justifié — c'est la vraie découverte du rapport. |

### 2.2 Confirmations exactes (avec lignes)

| Affirmation | Vérification |
|---|---|
| Upload sans whitelist/taille/MIME (`social.py:45-52`) | ✅ `upload_file` : extension du nom de fichier prise telle quelle, écriture directe disque, 0 limite |
| `users/search` expose l'email (`55-61`) | ✅ `SELECT id, nom, email FROM users …` |
| Pepper `dev-only-key` si SECRET_KEY vide (`services/hashing.py:17`) | ✅ ligne 17 exacte : `key = cfg.SECRET_KEY or "dev-only-key"` |
| Comparaison admin non-constante (`admin_ingest.py:15`) | ✅ `x_admin_token != secret` — comparaison standard, pas `hmac.compare_digest` |
| Pas de claim `jti` (`auth.py`) | ✅ 0 occurrence |
| Breaker global non verrouillé (`services/llm.py:39`) | ✅ `_breaker_state: dict = {}` en module, read-modify-write sans lock |
| Clé de test en dur (`llm.py:100`) | ✅ `!= "test-gemini-key"` en production |
| Cache RAG global (`rag_service.py:15`) | ✅ `_rag_cache: OrderedDict` module-scope |
| UNIQUE NULL (`models/session.py:47`) | ✅ `UniqueConstraint("user_id", "concept_id")` + `concept_id` nullable → doublons possibles en PostgreSQL (NULL ≠ NULL) |
| 34 migrations Alembic | ✅ 34 fichiers dans `migrations/versions/` |
| `conftest.py` mock par sous-chaîne | ✅ `if "user_streaks" in sql: …` (l.102-116) |
| `test_auth.py` assertions multi-statuts | ✅ 5 occurrences, dont `in [200, 201, 409]` **et `in [401, 500]`** — un 500 passe le test |
| Fixture `event_loop` obsolète (`conftest.py:220`) | ✅ présente |
| `aiofiles==25.1.0` en double | ✅ 2 occurrences dans requirements.txt |
| Aucun security header (`next.config.ts`) | ✅ 0 bloc `headers()` |
| Aucun `error.tsx` / `loading.tsx` / `not-found.tsx` / `middleware.ts` | ✅ 0 fichier (vérifié par `ls`) |
| `HardestVerbPoll` + `OnboardingOverlay` en `fetch()` natif | ✅ (`HardestVerbPoll.tsx:25` ; OnboardingOverlay vérifié dans nos actes précédents) |
| `Content-Type: application/json` sur les GET (`api-client.ts:107`) | ✅ header inconditionnel |
| `get()`/`post()` sans timeout/retry/refresh (`203-222`) | ✅ `fetch` nu, pas les mécanismes de `request()` |
| Progression en localStorage falsifiable | ✅ (nos propres constats, actes 3-4 : `getStoredAnswers`) |
| `rehype-raw` présent et inutilisé | ✅ dans package.json, 0 import — risque XSS si importé |
| Duplication CSS `.glass` ↔ `.svt-glass` | ✅ 9 classes `svt-*` en double dans globals.css |
| Icône PWA `/icon.svg` absente | ✅ fichier introuvable dans `public/` |
| Vitest : 0 `.test.tsx`, environnement `node` | ✅ pattern `src/**/*.test.ts` seulement |
| `ES2017` dans tsconfig | ✅ ligne 3 |
| Règles ESLint `react-compiler` / `set-state-in-effect` désactivées | ✅ lignes 16 et 21 `"off"` |
| PDFs = pointeurs LFS de 132 octets | ✅ vérifié indépendamment (tour précédent) — sujets/corrections 2023-2026 |
| Modèle ONNX = pointeur LFS de 134 octets | ✅ vérifié dès notre première session |
| CI actif : ~5-6 fichiers de tests + `continue-on-error: true` | ✅ ligne 78 exacte |
| Chemin Windows personnel (`docker-compose.yml:54`) | ✅ **ligne 54 exacte** : `C:/Users/zakaria/Documents/RESSOURCES_KHAWARIZMI/…` |
| `startup.sh` : fix de migration inline au lieu d'Alembic | ✅ `python3 -c "…"` en dur |
| Double Dockerfile (racine + backend) | ✅ les deux existent |
| `netlify.toml` + `vercel.json` (vide) coexistent | ✅ |
| `lib/api-client.ts` obsolète, **273 lignes**, URL en dur | ✅ **exactement 273 lignes**, `https://khawarizmi-backend.railway.app` |
| BOM UTF-8 dans `.gitignore` | ✅ `b'\xef\xbb\xbf'` |
| `AGENT_RULES.md` + `AGENTS.md` coexistent | ✅ |
| ~7 Mo de non-code à la racine | ✅ ~4,6 Mo comptés (txt/md/png) + PDFs |

### 2.3 Confirmations partielles / nuances

| Affirmation | Nuance |
|---|---|
| `GamificationPanel.tsx:36` « code mort setLastAction jamais utilisé » | **Semi-faux** : le setter est appelé ligne 50 (`setLastAction(action.action)`) — la **valeur** n'est jamais lue. Code inutile, pas mort. |
| `DocumentRenderer.tsx:307` `<img>` | Exact, mais à la **ligne 308** (décalage de 1) |
| « 9 fichiers de tests frontend » | **10** dans notre arbre (le nôtre s'est ajouté depuis l'instantané audité) |
| « 632 tests Python · 592 tests frontend · 189 endpoints » | Ce sont les **revendications du projet** citées par le rapport. Nos mesures : **951 fonctions de test / 965 tests passés** backend, **142 assertions** frontend (10 fichiers), **194 endpoints** (avant notre gel) |
| `useChatbot.ts` dépendances instables | ✅ confirmé (`[input, loading, …]`, `[sendMessage]`, `[messages, …]`) |

---

## 3. Ce que le rapport apporte que notre chaîne n'avait pas

1. **L'IDOR de `social.py`** — le vrai trou. Nos 13 actes ont traqué `students-at-risk` (faux positif) et raté celui-là. C'est le premier P0 sécurité **réel et vérifié** du dossier : tout élève connecté lit les messages privés de n'importe quelle conversation.
2. **Les PDFs LFS cassés en prod** — nous les avons trouvés au tour précédent ; le rapport y arrive par une autre voie (l'angle Vercel/Railway ne supporte pas LFS). Preuve croisée indépendante.
3. **Le détail fin** (pepper, jti, BOM, chemin Windows ligne 54, 273 lignes exactes) — niveau de précision que nos audits n'avaient pas.

---

## 4. Le plan d'action du rapport — verdict

| Phase | Verdict |
|---|---|
| Action #1 « Corriger le SyntaxError config.py:146 » | **À rayer** — rien à corriger |
| Action #2 « Corriger l'IDOR social.py » | **À faire en premier** — c'est le vrai CRITIQUE |
| Actions #3-6 (upload, email, compare_digest, pepper) | Justes, ordre correct |
| Actions #7-8 (chemin Windows, rehype-raw) | Justes |
| Court terme (LFS, ONNX, error/loading, headers, middleware…) | Juste — et aligné avec nos propres constats (middleware = notre « flash de contenu » ; LFS = nos PDFs/ONNX) |
| Moyen terme | Raisonnable |

---

## 5. Notation du rapport

| Axe | Note | Commentaire |
|---|---|---|
| Précision factuelle (~40 affirmations vérifiées) | **17/20** | Une seule fausse (le SyntaxError) — mais c'est une CRITIQUE et l'action n°1 du plan ; le reste est remarquablement juste, lignes incluses |
| Découverte de vrais risques | **18/20** | IDOR réel + LFS + pepper + upload — du concret exploitable |
| Priorisation | **13/20** | Le plan est bon sauf que sa tête (SyntaxError) n'existe pas ; l'IDOR réel est #2 derrière un fantôme |
| Couverture | 14/20 | Audit technique volontairement — 0 pédagogie, 0 file /manhadjia (hors périmètre assumé) |
| Utilité opérationnelle | **17/20** | Le backlog sécurité le plus actionnable du dossier |

**En tant qu'audit technique : 88/100.**
**En tant que plan d'action tel quel : 78/100** (il faut juste permuter l'action 1 et l'action 2, et supprimer la 1).
