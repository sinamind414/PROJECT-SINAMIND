"""Routes Flashcards Méthodologiques — Semaine 5"""

from fastapi import APIRouter
from methodology.methodology_flashcards import (
    get_all_methodology_flashcards,
    get_flashcards_by_category,
)

router = APIRouter(prefix="/api/flashcards/methodology", tags=["Flashcards Méthodologiques"])


@router.get("/")
async def get_methodology_flashcards():
    return get_all_methodology_flashcards()


@router.get("/category/{category}")
async def get_by_category(category: str):
    return get_flashcards_by_category(category)
