"""Seed Active Lessons — charge les blocs depuis JSON.

Usage: python scripts/seed_lessons.py
"""

import asyncio
import json
import logging
import pathlib

from sqlalchemy import text
from database import get_db

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("seed_lessons")

SEED_FILE = pathlib.Path(__file__).parent / "lessons_seed.json"


async def seed():
    if not SEED_FILE.exists():
        logger.error(f"Fichier seed introuvable : {SEED_FILE}")
        return

    data = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    logger.info(f"Seed : {len(data)} lecons a inserer")

    async for db in get_db():
        for lesson in data:
            slug = lesson["chapter_slug"]

            existing = await db.execute(
                text("SELECT COUNT(*) FROM lesson_blocks WHERE chapter_slug = :slug"),
                {"slug": slug},
            )
            if existing.scalar() > 0:
                logger.info(f"  SKIP (existe) : {slug}")
                continue

            for i, block in enumerate(lesson["blocks"]):
                await db.execute(
                    text("""
                        INSERT INTO lesson_blocks
                            (chapter_slug, block_type, sort_order, title_ar,
                             body_ar, visual_hint, quick_check)
                        VALUES
                            (:slug, :btype, :order, :title, :body, :hint, :qc)
                    """),
                    {
                        "slug": slug,
                        "btype": block["block_type"],
                        "order": i,
                        "title": block["title_ar"],
                        "body": block["body_ar"],
                        "hint": block.get("visual_hint"),
                        "qc": json.dumps(block["quick_check"], ensure_ascii=False),
                    },
                )

            logger.info(f"  INSERT : {slug} ({len(lesson['blocks'])} blocs)")

        await db.commit()
        logger.info("Seed termine")
        break


if __name__ == "__main__":
    asyncio.run(seed())
