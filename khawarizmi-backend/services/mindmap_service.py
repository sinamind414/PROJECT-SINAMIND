import os
import uuid
import json
import re
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger("khawarizmi.mindmap_service")


MINDMAP_SYSTEM_PROMPT = """
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
    "label": "string max 5 mots",
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
    matiere: str,
    chapitre: str,
    filiere: str,
    niveau_detail: str,
    user_id: str,
    db: AsyncSession,
    openai_client
) -> dict:
    u_id = int(user_id)
    
    # 1. Vérifier si un Mind Map existe déjà pour ce chapitre/utilisateur
    result = await db.execute(
        text("""
            SELECT data FROM mindmaps
            WHERE user_id = :user_id AND LOWER(chapitre) = LOWER(:chapitre)
        """),
        {"user_id": u_id, "chapitre": chapitre}
    )
    row = result.fetchone()
    if row:
        logger.info(f"Mind Map existant trouve pour le chapitre : {chapitre}")
        mindmap_data = json.loads(row[0])
        flashcards = await _generate_auto_flashcards(
            mindmap_data["racine"],
            matiere,
            chapitre,
            user_id,
            db
        )
        return {
            "status": "success",
            "mindmap": mindmap_data,
            "flashcards_generees": flashcards,
            "source_rag": mindmap_data.get("metadata", {}).get("source_rag", "")
        }

    # 2. Recherche vectorielle dans rag_chunks pour collecter le contexte RAG
    from services.embedder import embedder
    query_text = f"Chapitre: {chapitre} - Matiere: {matiere} - Filiere: {filiere}"
    try:
        query_vector = embedder.encode([query_text])[0]
        logger.info(f"Recherche RAG: {len(embedder.encode([query_text])[0])} dim")
        res_chunks = await db.execute(
            text("""
                SELECT content, source
                FROM rag_chunks
                WHERE LOWER(matiere) = LOWER(:matiere)
                AND (LOWER(chapitre) = LOWER(:chapitre) 
                     OR LOWER(REPLACE(chapitre, 'é', 'e')) = LOWER(REPLACE(:chapitre, 'é', 'e')))
                ORDER BY embedding <=> CAST(:emb AS vector)
                LIMIT 5
            """),
            {
                "matiere": matiere,
                "chapitre": chapitre,
                "emb": str(query_vector.tolist())
            }
        )
        chunks = res_chunks.fetchall()
        logger.info(f"Chunks RAG trouvés: {len(chunks)}")
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
            "message": "Je n'ai pas trouve cette information dans la base. Consulte ton manuel officiel."
        }

    context_text = "\n\n".join([f"Source: {c.source}\n{c.content}" for c in chunks])
    source_names = ", ".join(list(set([c.source for c in chunks])))

    # 3. Interroger le LLM pour générer l'arborescence JSON
    user_prompt = f"""
    CONTEXTE DES COURS OFFICIELS :
    {context_text}
    
    CHAPITRE : {chapitre}
    MATIERE : {matiere}
    FILIERE : {filiere}
    NIVEAU DE DETAIL : {niveau_detail}
    """

    from services.llm import extract_json_from_gemini

    from config import get_settings
    _model = get_settings().openai_model
    logger.info(f"Generation du Mind Map via le modele {_model}...")
    try:
        response = await openai_client.chat.completions.create(
            model=_model,
            temperature=0.2,
            max_tokens=2000,
            timeout=25.0,
            messages=[
                {"role": "system", "content": MINDMAP_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )
        content = response.choices[0].message.content or ""
        generated_data = extract_json_from_gemini(content)
    except Exception as e:
        logger.error(f"Echec de generation LLM du Mind Map : {e}")
        generated_data = {}

    # Structure de fallback si le JSON LLM est invalide
    if not generated_data or "racine" not in generated_data:
        logger.warning("Structure JSON générée invalide. Utilisation du fallback statique.")
        generated_data = {
            "racine": _build_default_racine(chapitre, matiere),
            "liens_transversaux": []
        }

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
            
        node["couleur"] = {
            "critique": "#E74C3C",
            "haute": "#F39C12",
            "moyenne": "#3498DB"
        }[importance]
        
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
            "genere_le": datetime.utcnow().isoformat(),
            "version": "2.0",
            "source_rag": source_names,
            "user_id": user_id
        }
    }

    # 6. Enregistrer dans la base de données
    await save_mindmap(mindmap_data, user_id, db)

    # 7. Générer les flashcards
    flashcards = await _generate_auto_flashcards(
        mindmap_data["racine"],
        matiere,
        chapitre,
        user_id,
        db
    )

    return {
        "status": "success",
        "mindmap": mindmap_data,
        "flashcards_generees": flashcards,
        "source_rag": source_names
    }


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
        "liens": []
    }


async def _generate_auto_flashcards(
    node: dict,
    matiere: str,
    chapitre: str,
    user_id: str,
    db: AsyncSession,
    flashcards: list = None
) -> list:
    if flashcards is None:
        flashcards = []

    if node.get("flashcard_auto") and node.get("label"):
        card = {
            "recto": node["label"],
            "verso": f"Voir chapitre : {chapitre}",
            "type": node.get("type", "concept"),
            "importance": node.get("importance", "moyenne"),
            "node_id": node["id"]
        }
        flashcards.append(card)

    for child in node.get("enfants", []):
        await _generate_auto_flashcards(
            child, matiere, chapitre, user_id, db, flashcards
        )

    return flashcards


async def save_mindmap(
    mindmap: dict,
    user_id: str,
    db: AsyncSession
) -> None:
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
            "created_at": datetime.utcnow()
        }
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
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        )
        for child in node.get("enfants", []):
            await save_node_recursive(child)

    await save_node_recursive(mindmap["racine"])
    await db.commit()


async def update_node_maitrise(
    node_id: str,
    maitrise: int,
    user_id: str,
    db: AsyncSession
) -> dict:
    if maitrise not in [0, 1, 2]:
        raise ValueError("maitrise doit être 0, 1 ou 2")

    u_id = int(user_id)
    result = await db.execute(
        text("""
            UPDATE mindmap_nodes
            SET maitrise_eleve = :maitrise,
                updated_at = :updated_at
            WHERE id = :node_id
            AND user_id = :user_id
            RETURNING id, maitrise_eleve
        """),
        {
            "node_id": node_id,
            "maitrise": maitrise,
            "user_id": u_id,
            "updated_at": datetime.utcnow()
        }
    )
    await db.commit()
    row = result.fetchone()

    if not row:
        raise ValueError(f"Nœud {node_id} non trouvé")

    return {"id": row[0], "maitrise_eleve": row[1]}


async def get_weak_nodes(
    mindmap_id: str,
    user_id: str,
    db: AsyncSession
) -> list:
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
        {"mindmap_id": mindmap_id, "user_id": u_id}
    )
    rows = result.fetchall()
    return [dict(r._mapping) for r in rows]
