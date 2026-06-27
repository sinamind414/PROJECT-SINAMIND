import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user

logger = logging.getLogger("khawarizmi.chatbot")
router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])


@router.get("/state")
async def get_state(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from services.chatbot_engagement_service import get_chatbot_state
    state = await get_chatbot_state(db, current_user["id"])
    return {"status": "ok", **state}


@router.post("/feedback")
async def post_feedback(
    body: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feedback = body.get("feedback", "")
    chapter = body.get("chapitre") or None
    if feedback not in ("understood", "partial", "confused", "example", "quiz"):
        raise HTTPException(status_code=400, detail="Feedback invalide")

    from services.chatbot_engagement_service import record_chat_feedback
    await record_chat_feedback(db, current_user["id"], feedback, chapter)
    return {"status": "ok", "feedback": feedback}


@router.post("/daily-mission/complete")
async def complete_mission(
    body: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    mission_id = body.get("mission_id")
    if not mission_id:
        raise HTTPException(status_code=400, detail="mission_id requis")

    from services.chatbot_engagement_service import complete_daily_mission
    result = await complete_daily_mission(db, current_user["id"], mission_id)
    return result


@router.post("/confusion/detect")
async def detect_confusion_endpoint(
    body: dict,
    current_user: dict = Depends(get_current_user),
):
    text = (body.get("text") or "").strip()
    feedback_type = body.get("feedback_type", "confused")
    if not text:
        raise HTTPException(status_code=400, detail="text requis")

    from services.chatbot_engagement_service import detect_confusion
    result = await detect_confusion(text, feedback_type)
    return result


@router.post("/explain-back")
async def explain_back(
    body: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    concept = (body.get("concept") or "").strip()
    answer = (body.get("answer") or "").strip()
    if not concept or not answer:
        raise HTTPException(status_code=400, detail="concept et answer requis")

    from services.chatbot_engagement_service import evaluate_explain_back
    result = await evaluate_explain_back(db, current_user["id"], concept, answer)
    return result


@router.post("/boss-fight/start")
async def start_boss_fight_endpoint(
    body: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chapter = (body.get("chapter") or "").strip()
    if not chapter:
        raise HTTPException(status_code=400, detail="chapter requis")

    from services.chatbot_engagement_service import start_boss_fight
    result = await start_boss_fight(db, current_user["id"], chapter)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/boss-fight/{boss_fight_id}/submit")
async def submit_boss_fight_endpoint(
    boss_fight_id: str,
    body: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    answers = body.get("answers", {})
    if not answers:
        raise HTTPException(status_code=400, detail="answers requis")

    from services.chatbot_engagement_service import submit_boss_fight
    result = await submit_boss_fight(db, current_user["id"], boss_fight_id, answers)
    if "error" in result:
        raise HTTPException(status_code=404 if "non trouvé" in result["error"] else 400, detail=result["error"])
    return result


@router.post("/mystery-box/open")
async def open_mystery_box_endpoint(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from services.chatbot_engagement_service import open_chatbot_mystery_box
    result = await open_chatbot_mystery_box(db, current_user["id"])
    return result
