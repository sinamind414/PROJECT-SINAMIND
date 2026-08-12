"""Route Orientation — Système d'aide à la décision.

GET /api/orientation
Retourne les 3 recommandations priorisées pour l'élève,
basées sur l'agrégation de toutes les données FSRS.
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user
from services.orientation_roadmap import calculer_roadmap
from services.orientation_service import calculer_orientation

logger = logging.getLogger("khawarizmi.api")
router = APIRouter(prefix="/api/orientation", tags=["Orientation"])


@router.get("")
async def orienter_eleve(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne les recommandations pédagogiques priorisées pour l'élève.

    Agrège : flashcards FSRS + action-verbs + document-analysis + mindmap.
    0 appel IA. 100% SQL. Latence < 200ms.
    """
    orientation = await calculer_orientation(db, current_user["id"])

    logger.info(
        f"Orientation : user={current_user['id']} "
        f"pred_bac={orientation['prediction_bac']} "
        f"recs={len(orientation['recommendations'])}"
    )

    return orientation


@router.get("/roadmap")
async def roadmap_eleve(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """BOUSSOLE : parcours unité par unité (maîtrise + verrouillage).

    Retourne les 5 unités du programme SVT Bac Algérie avec leur niveau de
    maîtrise (depuis la mémoire FSRS), leur statut (done / active / locked),
    l'unité courante et le message du coach — « maîtrise d'abord l'unité N ».
    """
    roadmap = await calculer_roadmap(db, current_user["id"])

    logger.info(
        f"Roadmap : user={current_user['id']} "
        f"unite_active={roadmap['unite_active']} "
        f"done={sum(1 for u in roadmap['unites'] if u['statut'] == 'done')}/5"
    )

    return roadmap


@router.get("/roadmap")
async def roadmap_eleve(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne la boussole officielle : 3 domaines, 11 unités, 22 phases."""
    roadmap = await calculer_roadmap(db, current_user["id"])

    logger.info(
        "Roadmap : user=%s unite_active=%s done=%s/11",
        current_user["id"],
        roadmap["unite_active"],
        sum(1 for unit in roadmap["unites"] if unit["statut"] == "done"),
    )

    return roadmap
