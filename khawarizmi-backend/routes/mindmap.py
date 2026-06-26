# routes/mindmap.py
# Khawarizmi Pro — Routes Mind Map Dynamique (Pilier 4)
# Génération asynchrone + lazy loading

import json
import logging
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from deps import get_current_user, get_db, get_openai
from services.mindmap_methodology_service import generate_methodological_mindmap
from services.mindmap_service import (
    create_task,
    expand_node,
    get_task_status,
    get_weak_nodes,
    run_generation_background,
    update_node_maitrise,
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


class ExpandNodeRequest(BaseModel):
    node_id: str = Field(..., min_length=5)
    node_label: str = Field(..., min_length=1, max_length=200)
    chapitre: str = Field(..., min_length=2, max_length=100)
    matiere: str = Field(..., min_length=2, max_length=50)


# ── Génération asynchrone (non-bloquante) ────────────────────────────────────


class MethodologyMindMapRequest(BaseModel):
    matiere: str = Field(..., min_length=2, max_length=50)
    chapitre: str = Field(..., min_length=2, max_length=100)
    filiere: str = Field(..., min_length=2, max_length=50)


@router.post("/generate-methodological")
async def generate_methodological_endpoint(
    request: MethodologyMindMapRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        openai_client = get_openai()
    except HTTPException:
        openai_client = None
    mindmap = await generate_methodological_mindmap(
        matiere=request.matiere,
        chapitre=request.chapitre,
        filiere=request.filiere,
        user_id=current_user["id"],
        db=db,
        openai_client=openai_client,
    )
    return mindmap


@router.post("/generate")
async def generate_mindmap_endpoint(
    request: MindMapGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    openai_client=Depends(get_openai),
):
    """Démarre la génération asynchrone d'un Mind Map.

    Retourne immédiatement un task_id. Le frontend poll /task/{task_id}
    jusqu'à status=completed, puis récupère le Mind Map via /{mindmap_id}.
    """
    user_id = str(current_user["id"])

    # Vérifier si un Mind Map existe déjà (cache)
    result = await db.execute(
        text("""
            SELECT id, data FROM mindmaps
            WHERE user_id = :user_id AND LOWER(chapitre) = LOWER(:chapitre)
        """),
        {"user_id": int(user_id), "chapitre": request.chapitre},
    )
    row = result.fetchone()
    if row:
        # Mind Map déjà généré → retour direct
        return {"status": "success", "mindmap": json.loads(row[1]), "mindmap_id": row[0], "cached": True}

    # Créer la tâche asynchrone
    task_id = await create_task(
        user_id=user_id, matiere=request.matiere, chapitre=request.chapitre, filiere=request.filiere, db=db
    )

    # Lancer la génération en arrière-plan
    cfg = get_settings()
    db_url = cfg.DATABASE_URL or ""
    if db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1).replace(
            "postgres://", "postgresql+asyncpg://", 1
        )

    background_tasks.add_task(
        run_generation_background,
        task_id=task_id,
        matiere=request.matiere,
        chapitre=request.chapitre,
        filiere=request.filiere,
        niveau_detail=request.niveau_detail,
        user_id=user_id,
        db_url=db_url,
        openai_api_key=cfg.OPENAI_API_KEY,
        openai_base_url=cfg.openai_base_url,
        openai_model=cfg.openai_model,
    )

    return {
        "status": "pending",
        "task_id": task_id,
        "message": "Génération du Mind Map en cours. Poll /task/{task_id} pour suivre.",
    }


@router.get("/task/{task_id}")
async def get_task_status_endpoint(
    task_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Polling : récupère le statut d'une tâche de génération."""
    result = await get_task_status(task_id=task_id, user_id=str(current_user["id"]), db=db)

    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Tâche non trouvée")

    # Si terminé, récupérer le Mind Map complet
    if result["status"] == "completed" and result.get("mindmap_id"):
        mm_result = await db.execute(
            text("SELECT data FROM mindmaps WHERE id = :id AND user_id = :user_id"),
            {"id": result["mindmap_id"], "user_id": int(current_user["id"])},
        )
        mm_row = mm_result.fetchone()
        if mm_row:
            result["mindmap"] = json.loads(mm_row[0])

    return result


@router.post("/expand")
async def expand_node_endpoint(
    request: ExpandNodeRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    openai_client=Depends(get_openai),
):
    """Lazy loading : génère les sous-nœuds d'un nœud à la demande."""
    result = await expand_node(
        node_id=request.node_id,
        node_label=request.node_label,
        chapitre=request.chapitre,
        matiere=request.matiere,
        user_id=str(current_user["id"]),
        db=db,
        openai_client=openai_client,
    )
    return {"status": "success", "enfants": result["enfants"]}


# ── Endpoints existants (compatibilité) ──────────────────────────────────────


@router.get("/{mindmap_id}")
async def get_mindmap(
    mindmap_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        text("""
            SELECT data FROM mindmaps
            WHERE id = :id AND user_id = :user_id
        """),
        {"id": mindmap_id, "user_id": int(current_user["id"])},
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
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await update_node_maitrise(
            node_id=node_id, maitrise=body.maitrise, user_id=str(current_user["id"]), db=db
        )
        return {
            "status": "success",
            "node_id": result["id"],
            "maitrise_eleve": result["maitrise_eleve"],
            "message": {
                0: "Nœud marqué comme non compris. Révision prioritaire activée.",
                1: "Nœud en cours d'apprentissage.",
                2: "Nœud maîtrisé. Révision espacée activée.",
            }[body.maitrise],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{mindmap_id}/weak")
async def get_weak_nodes_endpoint(
    mindmap_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    nodes = await get_weak_nodes(mindmap_id=mindmap_id, user_id=str(current_user["id"]), db=db)

    return {
        "mindmap_id": mindmap_id,
        "weak_nodes": nodes,
        "total": len(nodes),
        "message": (
            f"{len(nodes)} nœud(s) à revoir en priorité."
            if nodes
            else "Excellent ! Tous les nœuds sont en cours ou maîtrisés."
        ),
    }
