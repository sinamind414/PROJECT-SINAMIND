"""Seed Document Analysis — insère les 11 scénarios et 55 questions en DB.

Usage:
    python scripts/seed_document_analysis.py

Lit scripts/document_analysis_seed.json (généré par extract_scenarios.js)
et insère les scénarios + questions dans da_scenarios et da_questions.
"""

import asyncio
import json
import logging
import pathlib

from sqlalchemy import text

from database import get_db

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("seed_da")

SEED_FILE = pathlib.Path(__file__).parent / "document_analysis_seed.json"


async def seed():
    if not SEED_FILE.exists():
        logger.error(f"Fichier seed introuvable : {SEED_FILE}")
        logger.error("Lance d'abord : node scripts/extract_scenarios.js")
        return

    data = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    logger.info(f"Seed : {len(data)} scénarios à insérer")

    async for db in get_db():
        for scenario in data:
            slug = scenario["slug"]

            existing = await db.execute(
                text("SELECT id FROM da_scenarios WHERE slug = :slug"),
                {"slug": slug},
            )
            if existing.fetchone():
                logger.info(f"  SKIP (existe) : {slug}")
                continue

            result = await db.execute(
                text("""
                    INSERT INTO da_scenarios
                        (slug, unit_key, title_ar, subtitle_ar, context_ar, dominant_skills)
                    VALUES
                        (:slug, :unit_key, :title_ar, :subtitle_ar, :context_ar, :dominant_skills)
                    RETURNING id
                """),
                {
                    "slug": slug,
                    "unit_key": scenario["unit_key"],
                    "title_ar": scenario["title_ar"],
                    "subtitle_ar": scenario["subtitle_ar"],
                    "context_ar": scenario["context_ar"],
                    "dominant_skills": json.dumps(scenario.get("dominant_skills", []), ensure_ascii=False),
                },
            )
            scenario_id = result.fetchone()._mapping["id"]

            for q in scenario["questions"]:
                await db.execute(
                    text("""
                        INSERT INTO da_questions
                            (scenario_id, verb_slug, level, n, title_ar, skill_ar,
                             doc_ref, prompt_ar, placeholder_ar, model_answer_ar, learning_focus_ar)
                        VALUES
                            (:scenario_id, :verb_slug, :level, :n, :title_ar, :skill_ar,
                             :doc_ref, :prompt_ar, :placeholder_ar, :model_answer_ar, :learning_focus_ar)
                    """),
                    {
                        "scenario_id": scenario_id,
                        "verb_slug": q["verb_slug"],
                        "level": q["level"],
                        "n": q["n"],
                        "title_ar": q["title_ar"],
                        "skill_ar": q["skill_ar"],
                        "doc_ref": q["doc_ref"],
                        "prompt_ar": q["prompt_ar"],
                        "placeholder_ar": q["placeholder_ar"],
                        "model_answer_ar": q["model_answer_ar"],
                        "learning_focus_ar": q["learning_focus_ar"],
                    },
                )

            logger.info(f"  INSERT : {slug} ({len(scenario['questions'])} questions)")

        await db.commit()
        logger.info("Seed terminé avec succès")
        break


if __name__ == "__main__":
    asyncio.run(seed())
