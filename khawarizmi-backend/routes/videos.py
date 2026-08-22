"""Routes pour les vidéos YouTube."""

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user

router = APIRouter(prefix="/api/videos", tags=["Videos"])
SEED_PATH = Path(__file__).parent.parent / "data" / "videos_seed.json"


def _seed_videos() -> list[dict]:
    if not SEED_PATH.exists():
        return []
    with open(SEED_PATH, encoding="utf-8") as file:
        videos = json.load(file)
    return [{"id": index + 1, **video} for index, video in enumerate(videos)]


@router.get("/all")
async def get_all_videos(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM videos ORDER BY chapitre, id"))
    rows = result.fetchall()
    if rows:
        return [dict(r._mapping) for r in rows]
    return _seed_videos()


@router.get("/by-chapter/{chapitre}")
async def get_videos_by_chapter(
    chapitre: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        text("""
            SELECT * FROM videos
            WHERE LOWER(chapitre) LIKE LOWER(:pattern)
            ORDER BY id
            LIMIT 10
        """),
        {"pattern": f"%{chapitre}%"},
    )
    rows = result.fetchall()
    if rows:
        return [dict(r._mapping) for r in rows]
    needle = chapitre.casefold()
    return [
        video for video in _seed_videos()
        if needle in video.get("chapitre", "").casefold()
        or video.get("chapitre", "").casefold() in needle
    ][:10]


@router.post("/seed")
async def seed_videos(db: AsyncSession = Depends(get_db)):
    if not SEED_PATH.exists():
        raise HTTPException(404, "Fichier seed introuvable")

    with open(SEED_PATH, encoding="utf-8") as f:
        videos = json.load(f)

    count = 0
    for video in videos:
        await db.execute(
            text("""
                INSERT INTO videos (youtube_id, titre, chaine, duree, chapitre, description)
                VALUES (:youtube_id, :titre, :chaine, :duree, :chapitre, :description)
            """),
            video,
        )
        count += 1

    await db.commit()
    return {"message": f"{count} vidéos importées"}
