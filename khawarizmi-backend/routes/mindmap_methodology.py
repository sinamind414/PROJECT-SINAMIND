"""Routes Mindmap Methodologique — Semaine 7"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from methodology.mindmap_methodology import (
    get_static_mindmap,
    get_all_static_mindmaps,
    generate_dynamic_mindmap
)

router = APIRouter(prefix="/api/mindmap/methodology", tags=["Mindmap Methodologique"])


@router.get("/static")
async def list_static_mindmaps():
    return get_all_static_mindmaps()


@router.get("/static/{mindmap_id}")
async def get_static(mindmap_id: str):
    mindmap = get_static_mindmap(mindmap_id)
    if not mindmap:
        raise HTTPException(status_code=404, detail="Mindmap non trouvee")
    return mindmap


class DynamicRequest(BaseModel):
    verb: str


@router.post("/dynamic")
async def get_dynamic_mindmap(request: DynamicRequest):
    try:
        mindmap = generate_dynamic_mindmap(request.verb)
        return mindmap
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
