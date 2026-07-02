# Tâche B — Ingestion RAG du LIVRE MANHADJIYA + branchement dans le correcteur v2

> Instructions pour Deepseek dans OpenCode.
> À exécuter session par session. Attendre validation utilisateur entre chaque session.

**Prérequis** : le correcteur v2 est déjà en place et fonctionne
(Q7 → source=llm, score 4/5 constaté). Cette tâche l'enrichit avec
la méthodologie officielle du LIVRE MANHADJIYA.md.

**Fichiers concernés** :
- Existants (déjà commités) : `scripts/ingest_livre_manhadjiya.py`,
  `services/correction_v2.py`, `services/rag_service.py`,
  `routes/document_analysis_v2.py`
- Fichier de données : `LIVRE MANHADJIYA.md` (que l'utilisateur va fournir)

**Interdit** : modifier `services/answer_sanity.py`, `prompts/correction_prompt.py`,
`services/rag_service.py`, `services/document_analysis_service.py`. Les extensions
autorisées portent uniquement sur `routes/document_analysis_v2.py`.

---

## Session 1 — Vérifier l'infra RAG existante (10 min)

Avant d'ingérer, s'assurer que la stack RAG répond.

```bash
cd khawarizmi-backend
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM rag_chunks;"
psql "$DATABASE_URL" -c "SELECT source, COUNT(*) FROM rag_chunks GROUP BY source;"
```

**Critères de sortie** :
- La table `rag_chunks` existe (créée par migration 004).
- L'extension `pgvector` est active (colonne `embedding vector(384)`).
- Rapporter à l'utilisateur : nombre total de chunks, sources actuelles.

Si erreur `relation "rag_chunks" does not exist` → **s'arrêter et demander**
à l'utilisateur : la migration Alembic doit être appliquée d'abord.

---

## Session 2 — Ingestion du LIVRE MANHADJIYA (15 min)

L'utilisateur doit avoir placé `LIVRE MANHADJIYA.md` dans un chemin accessible.

**Étape A — Dry-run pour vérifier le parsing** :

```bash
cd khawarizmi-backend
python -m scripts.ingest_livre_manhadjiya \
  --path /chemin/absolu/vers/LIVRE\ MANHADJIYA.md \
  --dry-run --sample 3
```

**Attendu** (référence : dry-run sur le vrai livre a produit) :
- `Sections trouvées : 296`
- `Chunks produits : 258`
- Répartition par verbe : `analyse ~43, explain ~44, interpret ~25, ...`

Si le nombre de chunks < 100 ou > 500, quelque chose cloche dans le
découpage. Signaler à l'utilisateur avant de continuer.

**Étape B — Ingestion réelle** :

```bash
python -m scripts.ingest_livre_manhadjiya \
  --path /chemin/absolu/vers/LIVRE\ MANHADJIYA.md
```

Le script est idempotent : il fait d'abord un DELETE des chunks
`source='livre_manhadjiya'` avant de réinsérer.

**Attendu** : `✅ Ingestion terminée : ~258 chunks` en 30-60 s
(temps dominé par le calcul d'embeddings ONNX).

**Étape C — Vérification post-ingestion** :

```bash
psql "$DATABASE_URL" <<SQL
SELECT chapitre, COUNT(*) as n
FROM rag_chunks
WHERE source = 'livre_manhadjiya'
GROUP BY chapitre
ORDER BY n DESC;
SQL
```

Rapporter à l'utilisateur la ventilation par verbe. Points de vigilance :
- Si `methodologie_generale` > 50 % du total, la détection de verbe est trop
  large — pas bloquant mais à noter.
- Si `deduce` a < 3 chunks, la méthodologie du verbe "استنتج" sera peu
  enrichie — pas bloquant mais à signaler.

**Critère de sortie** : au moins 200 chunks dans `rag_chunks` avec
`source='livre_manhadjiya'`, ventilés sur au moins 5 verbes.

---

## Session 3 — Brancher le RAG dans la route v2 (30 min)

**Fichier à modifier** : `khawarizmi-backend/routes/document_analysis_v2.py`
(seul fichier autorisé à cette étape).

**Étape A — Ajouter la fonction `_make_rag_provider`** en haut du fichier,
après les imports :

```python
from services.rag_service import rag_search, format_rag_context


async def _make_rag_provider(db):
    """Fabrique un provider RAG qui filtre les chunks du LIVRE MANHADJIYA
    par slug de verbe. Passé à evaluate_answer_v2 pour enrichir le prompt.

    Si aucun chunk n'est trouvé (ingestion pas encore faite ou verbe non
    couvert), retourne "" — le correcteur dégrade proprement vers la
    méthodologie codée en dur dans prompts/correction_prompt.py.
    """

    async def _provider(*, verb_slug: str, question_prompt: str, student_answer: str) -> str:
        # Requête combinant verbe + début de la consigne pour cibler
        # les chunks les plus pertinents.
        query = f"{verb_slug} {question_prompt[:200]}"
        try:
            chunks = await rag_search(db, message=query, chapter=verb_slug)
        except Exception:
            return ""  # Dégradation silencieuse : le correcteur v2 gère l'absence de RAG
        # Top 3 seulement — le prompt reste raisonnable en taille
        return format_rag_context(chunks[:3])

    return _provider
```

**Étape B — Passer le provider à `evaluate_answer_v2`** dans la boucle
qui traite `body.answers`. Trouver l'appel existant :

```python
result = await evaluate_answer_v2(
    scenario_context=...,
    documents=...,
    ...
    llm_call=_call_with_fallback,
    primary_client=openai_client,
    primary_model=cfg.openai_model,
)
```

Le modifier en ajoutant **une seule ligne** :

```python
rag_provider = await _make_rag_provider(db)   # ← à créer une fois avant la boucle si preferé

result = await evaluate_answer_v2(
    scenario_context=...,
    documents=...,
    ...
    llm_call=_call_with_fallback,
    primary_client=openai_client,
    primary_model=cfg.openai_model,
    rag_context_provider=rag_provider,          # ← nouveau
)
```

**Optimisation** : `_make_rag_provider(db)` peut être appelé **une seule
fois** avant la boucle, pas une fois par question. Le provider retourné
est réutilisable.

**Étape C — Vérifier que rien ne casse** :

```bash
cd khawarizmi-backend
pytest tests/test_document_analysis_v2.py -v
pytest tests/test_correction_v2.py -v
```

**Attendu** : tous les tests passent (les tests mockent `_call_with_fallback`,
donc RAG ou pas RAG ne change pas leur comportement — sauf si les tests
d'intégration font des assertions sur le prompt user).

Si un test échoue parce qu'il vérifie l'absence de bloc RAG dans le prompt,
ajuster le test en injectant un `rag_provider=None` explicite.

**Étape D — Test réel avec l'utilisateur** :

L'utilisateur relance :

```bash
API_URL="..." TOKEN="..." SCENARIO="..." \
  ./scripts/verify_corrector_v2.sh
```

**Attendu** :
- Q1-Q5 : toujours ✅ `source=sanity`, 0/n (RAG non appelé sur sanity).
- Q7 : ✅ `source=llm`, score `>=80%`. Le prompt user contient maintenant
  un bloc `═══ مقتطفات من الكتاب المنهجي (RAG) ═══` avec les extraits
  du livre pour le verbe `hypothesis`.
- Q8 : ✅ `source=llm`. Feedback devrait être plus riche (référence à la
  méthodologie officielle du livre).

**Critère de sortie** : Q7 et Q8 continuent à donner `source=llm` avec un
score cohérent. Aucun test ne casse.

---

## Session 4 — Commit propre

```bash
cd PROJECT-SINAMIND
git status
# Doit montrer : modifié khawarizmi-backend/routes/document_analysis_v2.py
# Peut-être : modifié tests/test_document_analysis_v2.py

git add khawarizmi-backend/routes/document_analysis_v2.py
# Éventuellement : git add khawarizmi-backend/tests/test_document_analysis_v2.py

git commit -m "feat(correcteur-v2): brancher RAG LIVRE MANHADJIYA dans la route v2

Ajoute _make_rag_provider() dans routes/document_analysis_v2.py qui
appelle rag_search filtré par verbe. Le contexte du livre est injecté
en supplément de la méthodologie codée en dur (jamais en remplacement).

Dégradation silencieuse si l'ingestion RAG n'a pas été faite : le
correcteur retombe sur la méthodologie hardcoded sans erreur.

Ingestion préalable :
  python -m scripts.ingest_livre_manhadjiya --path .../LIVRE\\ MANHADJIYA.md
Produit ~258 chunks tagués source='livre_manhadjiya'.
"

git push
```

---

## Ce qui doit rester intact après cette tâche

- `services/answer_sanity.py` (md5 doit être `c4cf6216db85c31eb01a4ac51e788064`)
- `prompts/correction_prompt.py` (md5 `e0efd2535dd1ace64e0d0e9a47d29a12`)
- `services/document_analysis_service.py` (md5 `983667de9c2bb87ebabc76ca9e7ff4f0`)
- `services/rag_service.py` (aucune modification)

## Cas d'arrêt — demander à l'utilisateur

1. Si la table `rag_chunks` n'existe pas.
2. Si l'ingestion produit < 100 chunks (parsing cassé).
3. Si Q7/Q8 régressent (score baisse par rapport à avant le branchement).
4. Si les tests existants échouent après ajout du provider.
