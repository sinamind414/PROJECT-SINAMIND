"""Seed Bac Blanc — 1 annale avec 2 sujets au choix.

Usage: python scripts/seed_bac_blanc.py
"""

import asyncio
import json
import logging
import pathlib

from sqlalchemy import text

from database import get_db

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("seed_bac")

SEED_FILE = pathlib.Path(__file__).parent / "bac_blanc_seed.json"


async def seed():
    if not SEED_FILE.exists():
        logger.error(f"Fichier seed introuvable : {SEED_FILE}")
        return

    data = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    logger.info(f"Seed bac blanc : {len(data)} sujets a inserer")

    async for db in get_db():
        for subject in data:
            existing = await db.execute(
                text("SELECT COUNT(*) FROM bac_subjects WHERE annale_slug = :slug AND subject_number = :num"),
                {"slug": subject["annale_slug"], "num": subject["subject_number"]},
            )
            if existing.scalar() > 0:
                logger.info(f"  SKIP : {subject['annale_slug']} sujet {subject['subject_number']}")
                continue

            await db.execute(
                text("""
                    INSERT INTO bac_subjects
                        (annale_slug, subject_number, title_ar, themes_ar,
                         estimated_minutes, exercises)
                    VALUES
                        (:slug, :num, :title, :themes, :minutes, :exercises)
                """),
                {
                    "slug": subject["annale_slug"],
                    "num": subject["subject_number"],
                    "title": subject["title_ar"],
                    "themes": json.dumps(subject.get("themes_ar", []), ensure_ascii=False),
                    "minutes": subject.get("estimated_minutes", 120),
                    "exercises": json.dumps(subject["exercises"], ensure_ascii=False),
                },
            )
            logger.info(
                f"  INSERT : {subject['annale_slug']} sujet {subject['subject_number']} ({len(subject['exercises'])} exercices)"
            )

        await db.commit()
        logger.info("Seed bac blanc termine")
        break


if __name__ == "__main__":
    asyncio.run(seed())
