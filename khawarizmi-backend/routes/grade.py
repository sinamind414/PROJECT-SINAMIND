"""POST /api/grade — S2. 0 LLM. Sans Rubric → 422 ungraded. Jamais VERB_RULES / L2."""

from __future__ import annotations

import time
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from deps import get_current_user
from rate_limit import evaluate_limit, get_user_key, limiter
from services.grade_adapter import may_write_fsrs
from services.grade_cache import cache_get_async, cache_set_async, make_key
from services.grade_metrics import record_cache, record_result, record_ungraded, snapshot
from services.grade_quota import should_count_quota
from services.local_grader import TRAINING_BANNER_AR, grade
from services.rubric_store import list_question_ids, load

router = APIRouter(prefix="/api/grade", tags=["Grade"])


class GradeIn(BaseModel):
    question_id: str = Field(min_length=1, max_length=200)
    answer: str = Field(default="", max_length=20000)
    surface: Literal["da", "verb", "bac"] = "da"


def _public_grade_dict(result) -> dict:
    """Jamais model_answer, jamais variants."""
    diag = result.diagnosis
    return {
        "grader_version": result.grader_version,
        "rubric_id": result.rubric_id,
        "rubric_version": result.rubric_version,
        "verb_slug": result.verb_slug,
        "method_points": result.method_points,
        "method_points_max": result.method_points_max,
        "method_percent": result.method_percent,
        "method_label_ar": result.method_label_ar,
        "order_ok": result.order_ok,
        "science_status": result.science_status,
        "science_flags": result.science_flags,
        "science_capped": result.science_capped,
        "caps_applied": list(getattr(result, "caps_applied", []) or []),
        "sanity_code": result.sanity_code,
        "stuffing_suspected": result.stuffing_suspected,
        "diagnosis": {"code": diag.code, "label_ar": diag.label_ar} if diag else None,
        "praise_ar": result.praise_ar,
        "next_step_ar": result.next_step_ar,
        "phrase_ar": result.phrase_ar,
        "criteria": [
            {
                "id": c.id,
                "status": c.status,
                "points_earned": c.points_earned,
                "points_max": c.points_max,
                "label_ar": c.label_ar,
            }
            for c in result.criteria
        ],
        "overall_training_percent": result.overall_training_percent,
        "source": "local_rubric",
        "banner_ar": TRAINING_BANNER_AR,
        "ungraded": False,
        "from_cache": bool(getattr(result, "from_cache", False)),
    }


def _enforce_evaluate_quota(request: Request) -> None:
    """15/h free, 80/h pro. Seulement si should_count_quota. Fail-open si limiter down."""
    key = get_user_key(request)
    limit_str = evaluate_limit(key)
    try:
        inner = getattr(limiter, "limiter", None)
        if inner is None:
            return
        from limits import parse

        item = parse(limit_str)
        allowed = inner.hit(item, key)
        if allowed is False:
            raise HTTPException(
                status_code=429,
                detail="تم بلوغ حد التصحيح. ليست علامة بكالوريا رسمية.",
            )
    except HTTPException:
        raise
    except Exception:
        return


async def _maybe_write_fsrs(user: dict, result, chapter_slug: str) -> None:
    """FSRS hors grade(). Pas de copie. DB absente → silence."""
    if not may_write_fsrs(result):
        return
    try:
        from app_state import state
        from services.fsrs_unified import update_memory

        if not getattr(state, "db_session", None):
            return
        async with state.db_session() as db:
            await update_memory(
                db,
                user["id"],
                "verb_chapter",
                item_id=f"{result.verb_slug}::{chapter_slug}" if chapter_slug else result.rubric_id,
                chapter=chapter_slug or "",
                last_score=int(result.overall_training_percent),
                attempts_delta=1,
            )
            await db.commit()
    except Exception:
        return


@router.post("")
async def post_grade(
    request: Request,
    body: GradeIn,
    current_user: dict = Depends(get_current_user),
):
    """Note une copie. ENABLE_EXTERNAL_LLM ignoré. user_id hors clé (équité)."""
    t0 = time.perf_counter()
    packed = load(body.question_id)
    if packed is None:
        record_ungraded(body.question_id, (time.perf_counter() - t0) * 1000)
        return JSONResponse(
            status_code=422,
            content={
                "code": "ungraded",
                "erreur": "ungraded",
                "question_id": body.question_id,
                "status": 422,
                "banner_ar": TRAINING_BANNER_AR,
            },
        )
    chapter = packed.rubric.chapter_slug
    key = make_key(packed, body.answer)
    hit = await cache_get_async(key)
    if hit is not None:
        record_cache(True)
        record_result(hit, (time.perf_counter() - t0) * 1000)
        await _maybe_write_fsrs(current_user, hit, chapter)
        return _public_grade_dict(hit)
    result = grade(
        student_answer=body.answer,
        rubric=packed.rubric,
        document=packed.document,
    )
    if should_count_quota(sanity_code=result.sanity_code, from_cache=False):
        _enforce_evaluate_quota(request)
    if result.cacheable:
        await cache_set_async(key, result)
    record_cache(False)
    record_result(result, (time.perf_counter() - t0) * 1000)
    await _maybe_write_fsrs(current_user, result, chapter)
    return _public_grade_dict(result)


@router.get("/questions")
async def list_gradable(
    current_user: dict = Depends(get_current_user),
):
    _ = current_user
    return {"question_ids": list_question_ids(), "banner_ar": TRAINING_BANNER_AR}


@router.get("/rubric/{question_id}")
async def get_rubric_public(
    question_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Labels + steps. JAMAIS variants, model_answer, keypoints.values."""
    _ = current_user
    packed = load(question_id)
    if packed is None:
        return JSONResponse(
            status_code=422,
            content={
                "code": "ungraded",
                "erreur": "ungraded",
                "question_id": question_id,
                "status": 422,
            },
        )
    r = packed.rubric
    return {
        "rubric_id": r.rubric_id,
        "version": r.version,
        "verb_slug": r.verb_slug,
        "total_points": r.total_points,
        "criteria": [{"id": c.id, "label_ar": c.label_ar, "points": c.points} for c in r.criteria],
        "method_graph_steps": list(r.method_graph.steps) if r.method_graph else [],
        "banner_ar": TRAINING_BANNER_AR,
    }


@router.get("/metrics")
async def grade_metrics(
    current_user: dict = Depends(get_current_user),
):
    """S12 §7.1 — compteurs. Jamais la copie, jamais user_id dans le snapshot."""
    _ = current_user
    return snapshot()
