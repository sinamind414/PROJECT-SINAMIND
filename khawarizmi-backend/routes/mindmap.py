# routes/mindmap.py
# Khawarizmi Pro — Routes Mind Map Dynamique (Pilier 4)

import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel, Field
from typing import Literal

from deps import get_db, get_current_user, get_openai
from services.mindmap_service import (
    generate_mindmap,
    update_node_maitrise,
    get_weak_nodes
)

logger = logging.getLogger("khawarizmi.api")
router = APIRouter(prefix="/api/mindmap", tags=["Mind Map"])


class MindMapGenerateRequest(BaseModel):
    matiere: str = Field(..., min_length=2, max_length=50)
    chapitre: str = Field(..., min_length=2, max_length=100)
    filiere: str = Field(..., min_length=2, max_length=50)
    niveau_detail: Literal["standard", "détaillé"] = "standard"


class MaitriseUpdateRequest(BaseModel):
    maitrise: Literal[0, 1, 2]


@router.post("/generate")
async def generate_mindmap_endpoint(
    request: MindMapGenerateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    openai_client = Depends(get_openai)
):
    result = await generate_mindmap(
        matiere=request.matiere,
        chapitre=request.chapitre,
        filiere=request.filiere,
        niveau_detail=request.niveau_detail,
        user_id=str(current_user["id"]),
        db=db,
        openai_client=openai_client
    )

    if result.get("status") == "no_context":
        return {"status": "no_context", "message": result["message"]}

    return result


@router.get("/{mindmap_id}")
async def get_mindmap(
    mindmap_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        text("""
            SELECT data FROM mindmaps
            WHERE id = :id AND user_id = :user_id
        """),
        {"id": mindmap_id, "user_id": int(current_user["id"])}
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Mind Map non trouvé")

    return json.loads(row[0])


@router.patch("/{node_id}/maitrise")
async def update_maitrise(
    node_id: str,
    body: MaitriseUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await update_node_maitrise(
            node_id=node_id,
            maitrise=body.maitrise,
            user_id=str(current_user["id"]),
            db=db
        )
        return {
            "status": "success",
            "node_id": result["id"],
            "maitrise_eleve": result["maitrise_eleve"],
            "message": {
                0: "Nœud marqué comme non compris. Révision prioritaire activée.",
                1: "Nœud en cours d'apprentissage.",
                2: "Nœud maîtrisé. Révision espacée activée."
            }[body.maitrise]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{mindmap_id}/weak")
async def get_weak_nodes_endpoint(
    mindmap_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    nodes = await get_weak_nodes(
        mindmap_id=mindmap_id,
        user_id=str(current_user["id"]),
        db=db
    )

    return {
        "mindmap_id": mindmap_id,
        "weak_nodes": nodes,
        "total": len(nodes),
        "message": (
            f"{len(nodes)} nœud(s) à revoir en priorité."
            if nodes else
            "Excellent ! Tous les nœuds sont en cours ou maîtrisés."
        )
    }
