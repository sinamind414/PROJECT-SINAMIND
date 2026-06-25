import json
import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logger = logging.getLogger("khawarizmi.mindmap_service")


# ── Génération asynchrone (BackgroundTasks) ──────────────────────────────────
# Le flux asynchrone évite les timeouts HTTP sur la génération MindMap :
#   1. POST /generate  → crée une tâche, retourne task_id immédiatement
#   2. Background task → RAG + LLM + save + flashcards
#   3. GET /task/{id}  → polling côté frontend
#   4. POST /expand    → lazy loading des sous-nœuds à la demande


async def create_task(user_id: str, matiere: str, chapitre: str, filiere: str, db: AsyncSession) -> str:
    """Crée une entrée mindmap_tasks et retourne le task_id."""
    task_id = str(uuid.uuid4())
    await db.execute(
        text("""
            INSERT INTO mindmap_tasks
                (id, user_id, chapitre, matiere, filiere, status, progress, created_at, updated_at)
            VALUES
                (:id, :user_id, :chapitre, :matiere, :filiere, 'pending', 'init', NOW(), NOW())
        """),
        {"id": task_id, "user_id": int(user_id), "chapitre": chapitre, "matiere": matiere, "filiere": filiere},
    )
    await db.commit()
    return task_id


async def _update_task(
    task_id: str, status: str, progress: str = None, error: str = None, mindmap_id: str = None, db: AsyncSession = None
) -> None:
    """Met à jour le statut d'une tâche."""
    sets = ["status = :status", "updated_at = NOW()"]
    params = {"id": task_id, "status": status}
    if progress:
        sets.append("progress = :progress")
        params["progress"] = progress
    if error:
        sets.append("error = :error")
        params["error"] = error
    if mindmap_id:
        sets.append("mindmap_id = :mindmap_id")
        params["mindmap_id"] = mindmap_id
    await db.execute(text(f"UPDATE mindmap_tasks SET {', '.join(sets)} WHERE id = :id"), params)
    await db.commit()


async def get_task_status(task_id: str, user_id: str, db: AsyncSession) -> dict:
    """Récupère le statut d'une tâche pour le polling frontend."""
    result = await db.execute(
        text("""
            SELECT status, progress, error, mindmap_id, chapitre, created_at
            FROM mindmap_tasks
            WHERE id = :id AND user_id = :user_id
        """),
        {"id": task_id, "user_id": int(user_id)},
    )
    row = result.fetchone()
    if not row:
        return {"status": "not_found"}
    return {
        "status": row[0],
        "progress": row[1],
        "error": row[2],
        "mindmap_id": row[3],
        "chapitre": row[4],
        "created_at": str(row[5]) if row[5] else None,
    }


async def run_generation_background(
    task_id: str,
    matiere: str,
    chapitre: str,
    filiere: str,
    niveau_detail: str,
    user_id: str,
    db_url: str,
    openai_api_key: str,
    openai_base_url: str,
    openai_model: str,
) -> None:
    """Tâche d'arrière-plan : génère le Mind Map hors de la requête HTTP.

    Crée sa propre session DB car la session de la requête est fermée
    après le retour de la réponse.
    """
    logger.info(f"MINDMAP_ASYNC | Tâche {task_id} démarrée pour '{chapitre}'")
    engine = create_async_engine(db_url, pool_size=5, max_overflow=10, pool_pre_ping=True)
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_maker() as db:
        try:
            await _update_task(task_id, "running", progress="rag", db=db)

            # 1. Recherche RAG + re-ranking hybride
            from services.embedder import embedder
            from services.reranker import rerank

            query_text = f"Chapitre: {chapitre} - Matiere: {matiere} - Filiere: {filiere}"
            query_vector = embedder.encode([query_text])[0]
            res_chunks = await db.execute(
                text("""
                    SELECT content, source,
                           1 - (embedding <=> CAST(:emb AS vector)) AS similarity
                    FROM rag_chunks
                    WHERE LOWER(matiere) = LOWER(:matiere)
                    AND (LOWER(chapitre) = LOWER(:chapitre)
                         OR LOWER(REPLACE(chapitre, 'é', 'e')) = LOWER(REPLACE(:chapitre, 'é', 'e')))
                    ORDER BY embedding <=> CAST(:emb AS vector)
                    LIMIT 20
                """),
                {"matiere": matiere, "chapitre": chapitre, "emb": str(query_vector.tolist())},
            )
            raw_chunks = [
                {
                    "content": r._mapping["content"],
                    "source": r._mapping["source"],
                    "similarity": float(r._mapping["similarity"]) if r._mapping["similarity"] else 0.0,
                }
                for r in res_chunks.fetchall()
            ]

            if not raw_chunks:
                await _update_task(task_id, "failed", error="no_context", db=db)
                logger.warning(f"MINDMAP_ASYNC | Aucun contexte RAG pour '{chapitre}'")
                return

            # Re-ranking : garder les 5 meilleurs chunks
            chunks = rerank(query_text, raw_chunks, top_k=5)
            context_text = "\n\n".join([f"Source: {c['source']}\n{c['content']}" for c in chunks])
            source_names = ", ".join(list(set([c["source"] for c in chunks])))

            # 2. Génération LLM (racine + niveau 1 seulement = lazy loading)
            await _update_task(task_id, "running", progress="llm", db=db)

            from openai import AsyncOpenAI

            from services.llm import extract_json_from_gemini

            openai_client = AsyncOpenAI(api_key=openai_api_key, base_url=openai_base_url)

            # Prompt pour génération superficielle (racine + niveau 1 uniquement)
            lazy_prompt = (
                MINDMAP_SYSTEM_PROMPT
                + """

GÉNÉRATION PROGRESSIVE (LAZY LOADING) :
- Génère UNIQUEMENT la racine (niveau 0) et ses enfants directs (niveau 1).
- NE génère PAS les niveaux 2 et 3 maintenant.
- Les enfants de niveau 1 auront leurs sous-nœuds générés à la demande.
- Chaque nœud de niveau 1 doit avoir un champ "has_children": true si des sous-nœuds existent.
"""
            )

            user_prompt = f"""
            CONTEXTE DES COURS OFFICIELS :
            {context_text}

            CHAPITRE : {chapitre}
            MATIERE : {matiere}
            FILIERE : {filiere}
            NIVEAU DE DETAIL : {niveau_detail}
            """

            try:
                response = await openai_client.chat.completions.create(
                    model=openai_model,
                    temperature=0.2,
                    max_tokens=1200,
                    timeout=20.0,
                    messages=[{"role": "system", "content": lazy_prompt}, {"role": "user", "content": user_prompt}],
                )
                content = response.choices[0].message.content or ""
                generated_data = extract_json_from_gemini(content)
            except Exception as e:
                logger.error(f"MINDMAP_ASYNC | Échec LLM: {e}")
                generated_data = {}

            if not generated_data or "racine" not in generated_data:
                generated_data = {"racine": _build_default_racine(chapitre, matiere), "liens_transversaux": []}

            # 3. Formatage + sauvegarde
            await _update_task(task_id, "running", progress="save", db=db)

            def format_node_lazy(node: dict, level=0):
                if "id" not in node or not node["id"] or len(node["id"]) < 5:
                    node["id"] = str(uuid.uuid4())
                node["niveau"] = level
                if "maitrise_eleve" not in node:
                    node["maitrise_eleve"] = 0
                importance = node.get("importance", "moyenne")
                if importance not in ["critique", "haute", "moyenne"]:
                    node["importance"] = "moyenne"
                    importance = "moyenne"
                node["couleur"] = {"critique": "#E74C3C", "haute": "#F39C12", "moyenne": "#3498DB"}[importance]
                if "flashcard_auto" not in node:
                    node["flashcard_auto"] = importance in ["critique", "haute"]
                node["enfants"] = node.get("enfants", [])
                node["expanded"] = False
                for child in node["enfants"]:
                    format_node_lazy(child, level + 1)

            format_node_lazy(generated_data["racine"], level=0)

            mindmap_id = str(uuid.uuid4())
            mindmap_data = {
                "id": mindmap_id,
                "titre": chapitre.upper(),
                "matiere": matiere,
                "filiere": filiere,
                "chapitre": chapitre,
                "racine": generated_data["racine"],
                "liens_transversaux": generated_data.get("liens_transversaux", []),
                "metadata": {
                    "genere_le": datetime.now(UTC).isoformat(),
                    "version": "2.0",
                    "source_rag": source_names,
                    "user_id": user_id,
                    "lazy_loading": True,
                },
            }

            await save_mindmap(mindmap_data, user_id, db)

            # 4. Flashcards FSRS
            await _update_task(task_id, "running", progress="flashcards", db=db)
            flashcards = await _generate_auto_flashcards(mindmap_data["racine"], matiere, chapitre, user_id, db)
            if flashcards:
                await persist_flashcards_to_fsrs(flashcards, matiere, chapitre, user_id, db)

            # 5. Tâche terminée
            await _update_task(task_id, "completed", progress="done", mindmap_id=mindmap_id, db=db)
            logger.info(f"MINDMAP_ASYNC | Tâche {task_id} terminée — mindmap={mindmap_id}")

        except Exception as e:
            logger.error(f"MINDMAP_ASYNC | Tâche {task_id} échouée: {e}", exc_info=True)
            await _update_task(task_id, "failed", error=str(e)[:500], db=db)

    await engine.dispose()


async def expand_node(
    node_id: str, node_label: str, chapitre: str, matiere: str, user_id: str, db: AsyncSession, openai_client
) -> dict:
    """Lazy loading : génère les sous-nœuds d'un nœud à la demande.

    Évite de générer l'arbre complet en une seule fois.
    """
    from config import get_settings
    from services.embedder import embedder
    from services.llm import extract_json_from_gemini
    from services.reranker import rerank

    # 1. RAG ciblé sur le nœud spécifique + re-ranking
    query_text = f"{matiere} {chapitre} {node_label}"
    try:
        query_vector = embedder.encode([query_text])[0]
        res_chunks = await db.execute(
            text("""
                SELECT content, source,
                       1 - (embedding <=> CAST(:emb AS vector)) AS similarity
                FROM rag_chunks
                WHERE LOWER(matiere) = LOWER(:matiere)
                AND (LOWER(chapitre) = LOWER(:chapitre)
                     OR LOWER(REPLACE(chapitre, 'é', 'e')) = LOWER(REPLACE(:chapitre, 'é', 'e')))
                AND content ILIKE :keyword
                ORDER BY embedding <=> CAST(:emb AS vector)
                LIMIT 10
            """),
            {
                "matiere": matiere,
                "chapitre": chapitre,
                "keyword": f"%{node_label[:30]}%",
                "emb": str(query_vector.tolist()),
            },
        )
        raw_chunks = [
            {
                "content": r._mapping["content"],
                "source": r._mapping["source"],
                "similarity": float(r._mapping["similarity"]) if r._mapping["similarity"] else 0.0,
            }
            for r in res_chunks.fetchall()
        ]
        chunks = rerank(query_text, raw_chunks, top_k=3) if raw_chunks else []
    except Exception as e:
        logger.error(f"MINDMAP_EXPAND | Erreur RAG: {e}")
        chunks = []

    context_text = "\n\n".join([f"Source: {c['source']}\n{c['content']}" for c in chunks]) if chunks else ""

    expand_prompt = f"""
    Tu es un expert pédagogique. Génère les sous-nœuds (niveau enfant) du nœud suivant.

    NŒUD PARENT : {node_label}
    CHAPITRE : {chapitre}
    MATIERE : {matiere}

    CONTEXTE RAG :
    {context_text}

    RÈGLES :
    1. Maximum 5 sous-nœuds
    2. Labels en ARABE (termes scientifiques en FR entre parenthèses)
    3. Maximum 5 mots par label
    4. Format JSON : {{"enfants": [{{"label": "...", "type": "...", "importance": "..."}}]}}

    Réponds UNIQUEMENT avec le JSON.
    """

    _model = get_settings().openai_model
    try:
        response = await openai_client.chat.completions.create(
            model=_model,
            temperature=0.2,
            max_tokens=800,
            timeout=15.0,
            messages=[
                {"role": "system", "content": "Tu génères des sous-nœuds pédagogiques en JSON."},
                {"role": "user", "content": expand_prompt},
            ],
        )
        content = response.choices[0].message.content or ""
        data = extract_json_from_gemini(content)
    except Exception as e:
        logger.error(f"MINDMAP_EXPAND | Échec LLM: {e}")
        data = {}

    enfants = data.get("enfants", []) if data else []

    # Formater les nouveaux nœuds
    for child in enfants:
        child["id"] = str(uuid.uuid4())
        child["niveau"] = 2
        child["maitrise_eleve"] = 0
        importance = child.get("importance", "moyenne")
        child["couleur"] = {"critique": "#E74C3C", "haute": "#F39C12", "moyenne": "#3498DB"}.get(importance, "#3498DB")
        child["flashcard_auto"] = importance in ["critique", "haute"]
        child["enfants"] = []
        child["expanded"] = False

    return {"node_id": node_id, "enfants": enfants}


MINDMAP_SYSTEM_PROMPT = """
INSTRUCTIONS LANGUE OBLIGATOIRES :

1. TOUS les labels en ARABE.
2. Termes scientifiques universels en FR entre parenthèses :
   ADN, ARN, ATP, polymérase, ribosome.
3. Exemples corrects :
   "تركيب البروتين"
   "الانزيم بوليمراز (ARN polymérase)"
4. INTERDIT : labels entièrement en français.

═══════════════════════════════════════════

Tu es un expert pédagogique spécialisé dans le Bac algérien.
Ta tâche est de générer un Mind Map JSON structuré.

RÈGLES OBLIGATOIRES :
1. Maximum 3 niveaux de profondeur
2. Maximum 7 enfants par nœud
3. Maximum 5 mots par label
4. flashcard_auto = true si importance = critique ou haute
5. Couleurs : critique=#E74C3C haute=#F39C12 moyenne=#3498DB

FORMAT JSON OBLIGATOIRE :
{
  "racine": {
    "id": "uuid",
    "label": "string max 5 mots — EN ARABE OBLIGATOIREMENT",
    "type": "concept|definition|formule|processus|exception",
    "niveau": 0,
    "importance": "critique|haute|moyenne",
    "bac_frequent": boolean,
    "flashcard_auto": boolean,
    "maitrise_eleve": 0,
    "couleur": "#hex",
    "enfants": [],
    "liens": []
  },
  "liens_transversaux": []
}

Réponds UNIQUEMENT avec le JSON. Aucun texte autour.
"""


async def generate_mindmap(
    matiere: str, chapitre: str, filiere: str, niveau_detail: str, user_id: str, db: AsyncSession, openai_client
) -> dict:
    u_id = int(user_id)

    # 1. Vérifier si un Mind Map existe déjà pour ce chapitre/utilisateur
    result = await db.execute(
        text("""
            SELECT data FROM mindmaps
            WHERE user_id = :user_id AND LOWER(chapitre) = LOWER(:chapitre)
        """),
        {"user_id": u_id, "chapitre": chapitre},
    )
    row = result.fetchone()
    if row:
        logger.info(f"Mind Map existant trouve pour le chapitre : {chapitre}")
        mindmap_data = json.loads(row[0])
        flashcards = await _generate_auto_flashcards(mindmap_data["racine"], matiere, chapitre, user_id, db)
        if flashcards:
            await persist_flashcards_to_fsrs(flashcards, matiere, chapitre, user_id, db)
        return {
            "status": "success",
            "mindmap": mindmap_data,
            "flashcards_generees": flashcards,
            "source_rag": mindmap_data.get("metadata", {}).get("source_rag", ""),
        }

    # 2. Recherche vectorielle dans rag_chunks + re-ranking
    from services.embedder import embedder
    from services.reranker import rerank

    query_text = f"Chapitre: {chapitre} - Matiere: {matiere} - Filiere: {filiere}"
    try:
        query_vector = embedder.encode([query_text])[0]
        res_chunks = await db.execute(
            text("""
                SELECT content, source,
                       1 - (embedding <=> CAST(:emb AS vector)) AS similarity
                FROM rag_chunks
                WHERE LOWER(matiere) = LOWER(:matiere)
                AND (LOWER(chapitre) = LOWER(:chapitre)
                     OR LOWER(REPLACE(chapitre, 'é', 'e')) = LOWER(REPLACE(:chapitre, 'é', 'e')))
                ORDER BY embedding <=> CAST(:emb AS vector)
                LIMIT 20
            """),
            {"matiere": matiere, "chapitre": chapitre, "emb": str(query_vector.tolist())},
        )
        raw_chunks = [
            {
                "content": r._mapping["content"],
                "source": r._mapping["source"],
                "similarity": float(r._mapping["similarity"]) if r._mapping["similarity"] else 0.0,
            }
            for r in res_chunks.fetchall()
        ]
        chunks = rerank(query_text, raw_chunks, top_k=5) if raw_chunks else []
        logger.info(f"Chunks RAG trouvés: {len(raw_chunks)} → re-rankés: {len(chunks)}")
    except Exception as e:
        logger.error(f"Erreur recherche RAG: {type(e).__name__}: {e}")
        import traceback

        logger.error(traceback.format_exc())
        chunks = []

    # Pilier RAG Strict : si aucun contexte n'est trouvé, renvoyer l'erreur configurée
    if not chunks:
        logger.warning(f"RAG STRICT: Aucun contexte trouve pour le chapitre '{chapitre}'")
        return {
            "status": "no_context",
            "message": "Je n'ai pas trouve cette information dans la base. Consulte ton manuel officiel.",
        }

    context_text = "\n\n".join([f"Source: {c['source']}\n{c['content']}" for c in chunks])
    source_names = ", ".join(list(set([c["source"] for c in chunks])))

    # 3. Interroger le LLM pour générer l'arborescence JSON
    user_prompt = f"""
    CONTEXTE DES COURS OFFICIELS :
    {context_text}
    
    CHAPITRE : {chapitre}
    MATIERE : {matiere}
    FILIERE : {filiere}
    NIVEAU DE DETAIL : {niveau_detail}
    """

    from config import get_settings
    from services.llm import extract_json_from_gemini

    _model = get_settings().openai_model
    logger.info(f"Generation du Mind Map via le modele {_model}...")
    try:
        response = await openai_client.chat.completions.create(
            model=_model,
            temperature=0.2,
            max_tokens=2000,
            timeout=25.0,
            messages=[{"role": "system", "content": MINDMAP_SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
        )
        content = response.choices[0].message.content or ""
        generated_data = extract_json_from_gemini(content)
    except Exception as e:
        logger.error(f"Echec de generation LLM du Mind Map : {e}")
        generated_data = {}

    # Structure de fallback si le JSON LLM est invalide
    if not generated_data or "racine" not in generated_data:
        logger.warning("Structure JSON générée invalide. Utilisation du fallback statique.")
        generated_data = {"racine": _build_default_racine(chapitre, matiere), "liens_transversaux": []}

    # 4. Formater récursivement l'arbre généré pour typage et clés uniques
    def format_node_recursive(node: dict, level=0):
        if "id" not in node or not node["id"] or len(node["id"]) < 5:
            node["id"] = str(uuid.uuid4())
        node["niveau"] = level
        if "maitrise_eleve" not in node:
            node["maitrise_eleve"] = 0

        importance = node.get("importance", "moyenne")
        if importance not in ["critique", "haute", "moyenne"]:
            node["importance"] = "moyenne"
            importance = "moyenne"

        node["couleur"] = {"critique": "#E74C3C", "haute": "#F39C12", "moyenne": "#3498DB"}[importance]

        if "flashcard_auto" not in node:
            node["flashcard_auto"] = node["importance"] in ["critique", "haute"]

        node["enfants"] = node.get("enfants", [])
        for child in node["enfants"]:
            format_node_recursive(child, level + 1)

    format_node_recursive(generated_data["racine"], level=0)

    # 5. Composer l'objet final
    mindmap_id = str(uuid.uuid4())
    mindmap_data = {
        "id": mindmap_id,
        "titre": chapitre.upper(),
        "matiere": matiere,
        "filiere": filiere,
        "chapitre": chapitre,
        "racine": generated_data["racine"],
        "liens_transversaux": generated_data.get("liens_transversaux", []),
        "metadata": {
            "genere_le": datetime.now(UTC).isoformat(),
            "version": "2.0",
            "source_rag": source_names,
            "user_id": user_id,
        },
    }

    # 6. Enregistrer dans la base de données
    await save_mindmap(mindmap_data, user_id, db)

    # 7. Générer les flashcards
    flashcards = await _generate_auto_flashcards(mindmap_data["racine"], matiere, chapitre, user_id, db)

    # 8. Persister les flashcards dans FSRS (Mind Map ↔ FSRS)
    if flashcards:
        await persist_flashcards_to_fsrs(flashcards, matiere, chapitre, user_id, db)

    return {"status": "success", "mindmap": mindmap_data, "flashcards_generees": flashcards, "source_rag": source_names}


def _build_default_racine(chapitre: str, matiere: str) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "label": chapitre,
        "type": "concept",
        "niveau": 0,
        "importance": "critique",
        "bac_frequent": True,
        "flashcard_auto": True,
        "maitrise_eleve": 0,
        "couleur": "#E74C3C",
        "enfants": [],
        "liens": [],
    }


async def _generate_auto_flashcards(
    node: dict, matiere: str, chapitre: str, user_id: str, db: AsyncSession, flashcards: list = None
) -> list:
    if flashcards is None:
        flashcards = []

    if node.get("flashcard_auto") and node.get("label"):
        card = {
            "recto": node["label"],
            "verso": f"Voir chapitre : {chapitre}",
            "type": node.get("type", "concept"),
            "importance": node.get("importance", "moyenne"),
            "node_id": node["id"],
        }
        flashcards.append(card)

    for child in node.get("enfants", []):
        await _generate_auto_flashcards(child, matiere, chapitre, user_id, db, flashcards)

    return flashcards


async def persist_flashcards_to_fsrs(
    flashcards: list, matiere: str, chapitre: str, user_id: str, db: AsyncSession
) -> list:
    u_id = int(user_id)
    saved = []

    import json as _json

    from fsrs import Card, Rating

    from services.fsrs_config import get_fsrs_scheduler
    from services.fsrs_graph import run_fsrs_step

    scheduler_inst = get_fsrs_scheduler()
    now = datetime.now(UTC)
    default_card = Card()

    for card in flashcards:
        card_id = f"mm_{card['node_id']}"
        updated_card = run_fsrs_step(default_card, Rating.Good, now, scheduler_inst)

        due_date = updated_card.due if hasattr(updated_card, "due") else now + timedelta(days=1)
        interval = updated_card.scheduled_days if hasattr(updated_card, "scheduled_days") else 1

        fsrs_json = _json.dumps(
            {
                "stability": updated_card.stability,
                "difficulty": updated_card.difficulty,
                "scheduled_days": interval,
                "reps": getattr(updated_card, "reps", 0),
                "lapses": getattr(updated_card, "lapses", 0),
                "state": str(updated_card.state),
                "last_review": now.isoformat(),
                "review_history": [
                    {
                        "rating": Rating.Good.value,
                        "reviewed_at": now.isoformat(),
                        "elapsed_days": 0,
                        "scheduled_days": interval,
                        "state_before": str(default_card.state),
                    }
                ],
            }
        )

        result = await db.execute(
            text("""
                INSERT INTO mastery_micro_concepts
                    (user_id, micro_concept_id, concept_id, chapter,
                     difficulty, stability, state, due_date,
                     prochaine_revision, interval_jours, fsrs_state, last_review)
                VALUES
                    (:user_id, :mc_id, :concept_id, :chapter,
                     :difficulty, :stability, :state, :due_date,
                     :next_rev, :interval, :fsrs_state::jsonb, :last_review)
                ON CONFLICT (user_id, micro_concept_id)
                DO UPDATE SET
                    chapter = EXCLUDED.chapter
                RETURNING id
            """),
            {
                "user_id": u_id,
                "mc_id": card_id,
                "concept_id": card["node_id"],
                "chapter": chapitre,
                "difficulty": updated_card.difficulty,
                "stability": updated_card.stability,
                "state": 1,
                "due_date": due_date,
                "next_rev": due_date,
                "interval": interval,
                "fsrs_state": fsrs_json,
                "last_review": now,
            },
        )
        row = result.fetchone()
        saved.append({**card, "fsrs_id": row[0] if row else None})

        await db.execute(
            text("""
                UPDATE mindmap_nodes
                SET fsrs_card_id = :fsrs_id,
                    updated_at = :updated_at
                WHERE id = :node_id AND user_id = :user_id
            """),
            {
                "fsrs_id": card_id,
                "node_id": card["node_id"],
                "user_id": u_id,
                "updated_at": now,
            },
        )

    await db.commit()
    logger.info(f"FSRS: {len(saved)} flashcards persistees pour user={user_id} chapitre={chapitre}")
    return saved


async def save_mindmap(mindmap: dict, user_id: str, db: AsyncSession) -> None:
    u_id = int(user_id)
    await db.execute(
        text("""
            INSERT INTO mindmaps
                (id, user_id, titre, matiere, filiere,
                 chapitre, data, created_at)
            VALUES
                (:id, :user_id, :titre, :matiere, :filiere,
                 :chapitre, :data, :created_at)
            ON CONFLICT (id) DO UPDATE
            SET data = EXCLUDED.data
        """),
        {
            "id": mindmap["id"],
            "user_id": u_id,
            "titre": mindmap["titre"],
            "matiere": mindmap["matiere"],
            "filiere": mindmap["filiere"],
            "chapitre": mindmap["chapitre"],
            "data": json.dumps(mindmap, ensure_ascii=False),
            "created_at": datetime.now(UTC),
        },
    )

    async def save_node_recursive(node: dict):
        await db.execute(
            text("""
                INSERT INTO mindmap_nodes
                    (id, mindmap_id, user_id, label, type, importance,
                     bac_frequent, fsrs_card_id, maitrise_eleve, created_at, updated_at)
                VALUES
                    (:id, :mindmap_id, :user_id, :label, :type, :importance,
                     :bac_frequent, :fsrs_card_id, :maitrise_eleve, :created_at, :updated_at)
                ON CONFLICT (id) DO UPDATE
                SET label = EXCLUDED.label,
                    type = EXCLUDED.type,
                    importance = EXCLUDED.importance,
                    bac_frequent = EXCLUDED.bac_frequent,
                    updated_at = EXCLUDED.updated_at
            """),
            {
                "id": node["id"],
                "mindmap_id": mindmap["id"],
                "user_id": u_id,
                "label": node.get("label", ""),
                "type": node.get("type", "concept"),
                "importance": node.get("importance", "moyenne"),
                "bac_frequent": node.get("bac_frequent", False),
                "fsrs_card_id": node.get("fsrs_card_id"),
                "maitrise_eleve": node.get("maitrise_eleve", 0),
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            },
        )
        for child in node.get("enfants", []):
            await save_node_recursive(child)

    await save_node_recursive(mindmap["racine"])
    await db.commit()


async def update_node_maitrise(node_id: str, maitrise: int, user_id: str, db: AsyncSession) -> dict:
    if maitrise not in [0, 1, 2]:
        raise ValueError("maitrise doit être 0, 1 ou 2")

    u_id = int(user_id)

    # Récupérer le fsrs_card_id avant mise à jour
    node_result = await db.execute(
        text(
            "SELECT id, fsrs_card_id, chapitre FROM mindmap_nodes mn "
            "JOIN mindmaps m ON m.id = mn.mindmap_id "
            "WHERE mn.id = :node_id AND mn.user_id = :user_id"
        ),
        {"node_id": node_id, "user_id": u_id},
    )
    node_row = node_result.fetchone()

    # Mettre à jour le niveau de maîtrise
    result = await db.execute(
        text("""
            UPDATE mindmap_nodes
            SET maitrise_eleve = :maitrise,
                updated_at = :updated_at
            WHERE id = :node_id
            AND user_id = :user_id
            RETURNING id, maitrise_eleve
        """),
        {"node_id": node_id, "maitrise": maitrise, "user_id": u_id, "updated_at": datetime.now(UTC)},
    )
    row = result.fetchone()

    if not row:
        raise ValueError(f"Nœud {node_id} non trouvé")

    # Mettre à jour l'état FSRS via le vrai scheduler calibré
    import json

    from fsrs import Card, Rating

    from services.fsrs_config import get_fsrs_scheduler
    from services.fsrs_graph import run_fsrs_step

    fsrs_card_id = f"mm_{node_id}"

    # Charger l'état actuel de la carte si elle existe
    mc_result = await db.execute(
        text("SELECT fsrs_state FROM mastery_micro_concepts WHERE micro_concept_id = :mc_id AND user_id = :uid"),
        {"mc_id": fsrs_card_id, "uid": u_id},
    )
    mc_row = mc_result.fetchone()

    card = Card()
    review_history = []
    if mc_row and mc_row[0]:
        try:
            state_data = mc_row[0]
            if isinstance(state_data, str):
                state_data = json.loads(state_data)
            card.stability = state_data.get("stability", card.stability)
            card.difficulty = state_data.get("difficulty", card.difficulty)
            card.reps = state_data.get("reps", card.reps)
            card.lapses = state_data.get("lapses", card.lapses)
            card.scheduled_days = state_data.get("scheduled_days", card.scheduled_days)
            review_history = state_data.get("review_history", [])
        except Exception as e:
            logger.warning(f"Impossible de parser fsrs_state pour {fsrs_card_id}: {e}")

    # Mapper la maîtrise sur le rating FSRS (Again → Hard → Good)
    rating_map = {0: Rating.Again, 1: Rating.Hard, 2: Rating.Good}
    fsrs_rating = rating_map[maitrise]

    # Récupérer la configuration FSRS de l'élève
    res_config = await db.execute(text("SELECT fsrs_config FROM users WHERE id = :uid"), {"uid": u_id})
    config_row = res_config.fetchone()
    user_fsrs_config = config_row[0] if config_row else None

    # Appliquer le scheduler calibré
    scheduler_inst = get_fsrs_scheduler(user_fsrs_config)
    now_utc = datetime.now(UTC)
    updated_card = run_fsrs_step(card, fsrs_rating, now_utc, scheduler_inst)

    due_date = updated_card.due if hasattr(updated_card, "due") else now_utc + timedelta(days=1)
    interval = updated_card.scheduled_days if hasattr(updated_card, "scheduled_days") else 1

    # Préserver l'historique des révisions
    review_history.append(
        {
            "rating": fsrs_rating.value if hasattr(fsrs_rating, "value") else maitrise,
            "reviewed_at": now_utc.isoformat(),
            "elapsed_days": 0,
            "scheduled_days": interval,
            "state_before": str(card.state),
        }
    )

    fsrs_json = json.dumps(
        {
            "stability": updated_card.stability,
            "difficulty": updated_card.difficulty,
            "scheduled_days": interval,
            "reps": getattr(updated_card, "reps", 0),
            "lapses": getattr(updated_card, "lapses", 0),
            "state": str(updated_card.state),
            "last_review": now_utc.isoformat(),
            "review_history": review_history,
        }
    )

    await db.execute(
        text("""
            INSERT INTO mastery_micro_concepts
                (user_id, micro_concept_id, concept_id, chapter,
                 difficulty, stability, fsrs_state, due_date,
                 prochaine_revision, interval_jours, state, last_review, updated_at)
            VALUES
                (:user_id, :mc_id, :concept_id, :chapter,
                 :difficulty, :stability, :fsrs_state::jsonb, :due_date,
                 :next_rev, :interval, :state, :last_review, :updated_at)
            ON CONFLICT (user_id, micro_concept_id)
            DO UPDATE SET
                difficulty = EXCLUDED.difficulty,
                stability = EXCLUDED.stability,
                fsrs_state = EXCLUDED.fsrs_state,
                due_date = EXCLUDED.due_date,
                prochaine_revision = EXCLUDED.prochaine_revision,
                interval_jours = EXCLUDED.interval_jours,
                state = EXCLUDED.state,
                last_review = EXCLUDED.last_review,
                updated_at = EXCLUDED.updated_at
        """),
        {
            "user_id": u_id,
            "mc_id": fsrs_card_id,
            "concept_id": node_id,
            "chapter": node_row[2] if node_row else "",
            "difficulty": updated_card.difficulty,
            "stability": updated_card.stability,
            "fsrs_state": fsrs_json,
            "due_date": due_date,
            "next_rev": due_date,
            "interval": interval,
            "state": updated_card.state.value if hasattr(updated_card.state, "value") else int(updated_card.state),
            "last_review": now_utc,
            "updated_at": now_utc,
        },
    )

    await db.commit()
    return {"id": row[0], "maitrise_eleve": row[1]}


async def get_weak_nodes(mindmap_id: str, user_id: str, db: AsyncSession) -> list:
    u_id = int(user_id)
    result = await db.execute(
        text("""
            SELECT id, label, type, importance,
                   bac_frequent, fsrs_card_id
            FROM mindmap_nodes
            WHERE mindmap_id = :mindmap_id
            AND user_id = :user_id
            AND maitrise_eleve = 0
            ORDER BY
                CASE importance
                    WHEN 'critique' THEN 1
                    WHEN 'haute' THEN 2
                    WHEN 'moyenne' THEN 3
                END
        """),
        {"mindmap_id": mindmap_id, "user_id": u_id},
    )
    rows = result.fetchall()
    return [dict(r._mapping) for r in rows]
