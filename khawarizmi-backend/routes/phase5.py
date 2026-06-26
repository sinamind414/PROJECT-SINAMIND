from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db
from services.phase5_service import (
    create_challenge,
    create_challenge_for_user,
    get_challenge_results,
    get_friend_activity,
    get_live_classroom_stats,
    list_friend_requests,
    list_friends,
    respond_friend_request,
    search_users,
    send_friend_request,
    send_friend_request_to_user,
    submit_challenge_result,
)

router = APIRouter(prefix="/api/phase5", tags=["Phase 5 - Social & Live"])


class FriendRequestResponse(BaseModel):
    accept: bool


class ChallengeResultRequest(BaseModel):
    score: int = Field(ge=0)
    correct_answers: int = Field(default=0, ge=0)
    total_questions: int = Field(default=0, ge=0)
    duration_seconds: int = Field(default=0, ge=0)


@router.get("/live-stats/{chapter}")
async def live_stats(
    chapter: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_live_classroom_stats(chapter, db)


@router.get("/friends-activity")
async def friends_activity(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_friend_activity(current_user["id"], db)


@router.get("/users/search")
async def users_search(
    q: str = Query(..., min_length=1),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {"users": await search_users(current_user["id"], q, db)}


@router.get("/friends")
async def friends(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {"friends": await list_friends(current_user["id"], db)}


@router.post("/friend-requests/user/{friend_user_id}")
async def create_friend_request_to_user(
    friend_user_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await send_friend_request_to_user(current_user["id"], friend_user_id, db)


@router.post("/friend-requests/{friend_id}")
async def create_friend_request(
    friend_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await send_friend_request(current_user["id"], friend_id, db)


@router.get("/friend-requests")
async def get_friend_requests(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {"requests": await list_friend_requests(current_user["id"], db)}


@router.post("/friend-requests/{request_id}/respond")
async def respond_to_friend_request(
    request_id: str,
    body: FriendRequestResponse,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await respond_friend_request(current_user["id"], request_id, body.accept, db)


@router.post("/challenge/user/{friend_user_id}")
async def send_challenge_to_user(
    friend_user_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_challenge_for_user(current_user["id"], friend_user_id, db)


@router.post("/challenge/{friend_id}")
async def send_challenge(
    friend_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_challenge(current_user["id"], friend_id, db)


@router.post("/challenge/{challenge_id}/result")
async def challenge_result(
    challenge_id: str,
    body: ChallengeResultRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await submit_challenge_result(
        user_id=current_user["id"],
        challenge_id=challenge_id,
        score=body.score,
        correct_answers=body.correct_answers,
        total_questions=body.total_questions,
        duration_seconds=body.duration_seconds,
        db=db,
    )


@router.get("/challenge/{challenge_id}/results")
async def challenge_results(
    challenge_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_challenge_results(challenge_id, db)
