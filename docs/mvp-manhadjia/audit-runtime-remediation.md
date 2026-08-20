# Audit backend + branchement runtime « point d'équilibre »

> Date : 2026-08-20 · Branche : `arena/01a01f52-project-sinamind`
> Mandat utilisateur : « Audit le backend et applique ta recommandation — le point d'équilibre »

## 1. Verdict de l'audit

| Élément | Statut |
|---|---|
| Route `routes/manhadjiya.py` (9 endpoints) | ✅ code propre, sync pur, 0 DB / 0 LLM / 0 Redis |
| `get_contextual_remediation_data` | ✅ pur en mémoire (keywords sur `ALL_UNITS`), latence mesurée **0,013 ms** |
| CORS | ✅ contourné : le frontend appelle en **relatif** `/api/...` via rewrites Next → même origine |
| `POST /contextual-remediation` | ✅ 200, **42 ms de bout en bout** (navigateur → Next → FastAPI), erreur `verb_slug requis` gérée |
| Backend complet | ❌ **ne démarrait PAS** : 2 bugs bloquants committés (voir §2) |
| Backend après correction | ✅ démarre (SQLite 81 tables, 0 LLM, Redis/ONNX en dégradation tolérée) |
| Tests backend manhadjiya | ✅ **99 passed** (après correction) |

## 2. Bloqueurs trouvés et corrigés (2 lignes, mécaniques)

1. **`services/chatbot_handlers.py:185`** — marqueur de conflit git orphelin
   `<<<<<<< HEAD` committé **sans** `=======` ni `>>>>>>>`. Résultat :
   `IndentationError` → **le backend entier ne démarre plus** (import chain),
   et la collecte de tous les tests backend échouait aussi.
   Correction : suppression de la ligne orpheline (le code présent est le côté
   HEAD complet et valide — vérifié par `ast.parse` + 99 tests verts).
2. **`routes/__init__.py`** — `pulse.router` référencé dans `ALL_ROUTERS`
   mais **jamais importé** (`NameError: name 'pulse' is not defined`).
   Correction : `pulse,` ajouté à la liste d'imports.

Ces deux bugs étaient committés dans la base de session (`f45018c`) :
**le backend de production était en panne avant cet audit**.

## 3. Ce qui a été appliqué (le point d'équilibre)

- **Un seul endpoint branché** : `POST /api/manhadjiya/contextual-remediation`.
- **Où** : phase ب des 22 ateliers (7 bootcamp + 15 satellites), via
  `RemediationHint` (debounce 1,2 s · timeout 2,5 s · AbortController ·
  garde anti-réponse obsolète · texte ≥ 12 caractères).
- **Repli silencieux** : toute erreur (réseau, timeout, HTTP ≠ 2xx, JSON
  invalide, payload vide) → `null` → **rien ne s'affiche**, la détection
  locale reste la seule source de vérité et s'affiche toujours.
  Prouvé en conditions réelles : backend coupé → proxy HTTP 500 → rien.
- **Jamais branché** (reste statique, injecté au build) : cartes, verb_ref,
  unites, exemples — `wire_satellite_official_data.py` inchangé.
- 22 JSON portent `verb_slug` (7 bootcamp : diff minimal +1 ligne chacun ;
  15 satellites via le script, idempotent) + invariant testé (slugs ∈ VERB_UNIT_MAP).

## 4. Fichiers

| Fichier | Changement |
|---|---|
| `khawarizmi-backend/services/chatbot_handlers.py` | −1 ligne (marker de conflit orphelin) |
| `khawarizmi-backend/routes/__init__.py` | +1 ligne (`pulse,` import manquant) |
| `khawarizmi-frontend/src/lib/manhadjia-remediation.ts` | nouveau — fetch timeout/abort + normalisation (11 tests) |
| `khawarizmi-frontend/src/components/manhadjia/RemediationHint.tsx` | nouveau — panneau « أخطاء شائعة — المرجع الرسمي » |
| 8 composants `Atelier*.tsx` | +1 import +1 ligne `<RemediationHint …/>` en phase ب |
| 22 JSON ateliers | + champ `verb_slug` |
| 23 pages `app/manhadjia/**` | commentaires de doctrine mis à jour (honnêteté : 1 appel API, repli silencieux) |
| `manhadjia-lib.ts` + tests | `verb_slug: string` dans `AtelierData`, +2 invariants |

## 5. Preuves

- Backend : **99/99 tests manhadjiya verts** · démarrage complet OK · 9/9 endpoints 200 via proxy Next.
- Frontend : **799 tests verts** (dont 11 remediation + 2 invariants) · ESLint clean · build OK · 23/23 routes 200.
- Bout en bout : `POST /api/manhadjiya/contextual-remediation` → **42 ms**, 12 erreurs officielles renvoyées pour `deduce`.
- Repli : backend arrêté → HTTP 500 → composant muet (testé).

## 6. Bugs résiduels — corrigés le 2026-08-20 (même session)

### 6.1 Modèle ONNX « corrompu » — cause racine : pointeur Git LFS
- Le fichier `model_quantized.onnx` (134 octets) est un **pointeur Git LFS**
  (oid sha256:fac7bbc8…, taille réelle 118 Mo) jamais téléchargé.
- Corrections livrées :
  - `services/embedder.py` : détection explicite du pointeur → message
    actionnable (« git lfs pull puis redémarrer ») au lieu de l'INVALID_PROTOBUF
    cryptique ; récupération depuis `model_quantized.zip` si présent (sans
    jamais supprimer le fichier tracké par git) ; fallback déterministe propre
    (les consommateurs sémantiques — rag_service, l2, semantic_cache — se
    désactivent déjà correctement quand `is_semantic` est False).
  - `scripts/check_onnx_asset.py` (nouveau) : diagnostic du statut
    (OK / LFS / CORROMPU / MANQUANT / ZIP) + commande de récupération exacte.
- **Action côté utilisateur** (réseau du sandbox bloqué pour media.githubusercontent.com) :
  sur une machine avec git-lfs : `git lfs pull --include 'khawarizmi-backend/models/minilm_onnx_int8/*'`
  puis redéployer. En attendant, le RAG mot-clé reste fonctionnel.

### 6.2 Écart `unite5-energie` vs `unite5-energetique` — corrigé
- `prompts/scientific_knowledge.py` : helper `_canonical_unit_id()` (alias) appliqué
  à `get_unit_specific_errors`, `build_knowledge_block`, `get_practical_examples`.
- Les deux orthographes sont verrouillées par des tests existants → **aucune
  constante modifiée**. Résultat : les erreurs énergétiques (photosynthèse…)
  apparaissent maintenant dans la remédiation (15 erreurs pour « interpret »
  au lieu de 12). 4 tests de non-régression dans `tests/test_unit_id_alias.py`.

### 6.3 Redis absent en preview
- Toléré par design (warning, rate-limit/cache dégradés, zéro blocage) —
  pas un bug code, aucun changement.

## 7. Bugs supplémentaires découverts par la suite backend (jusqu'ici masqués : le backend ne démarrait pas)

| Fichier | Bug | Correction |
|---|---|---|
| `services/chatbot_handlers.py` | `handle_orientation` levait `NameError: greeting` sur **chaque message d'orientation** (moitié perdue du conflit git) | `greeting` reconstruit (salutation si `is_init`) + `prediction_bac` inclus dans la réponse (contrat de test) |
| `services/chatbot_handlers.py` | `make_response()` appelé avec `prochain_objectif` inconnu → `TypeError` | paramètre optionnel ajouté dans `chatbot_response.py` (rétro-compatible) |
| `services/pulse_service.py` | carte déjà complétée → streak renvoyé faux (0 au lieu du streak réel) | requête streak inline dans la branche idempotente + helper `_streak_summary_from_row` partagé |

**Preuves finales backend** : `pytest -q` → **997 passed, 10 skipped, 5 xfailed, 0 failed**
(contre : suite impossible à collecter avant la session). Boot uvicorn propre,
`/api/manhadjiya/*` 200, `/api/pulse/*` montées (401 sans JWT, normal).
