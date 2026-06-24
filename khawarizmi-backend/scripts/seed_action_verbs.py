"""Seed des 13 verbes d'action depuis les fichiers JSON.

Usage: python scripts/seed_action_verbs.py
"""

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from config import get_settings

SEED_FILES = [
    ROOT / "data" / "action_verbs_seed.json",
    ROOT / "data" / "action_verbs_seed2.json",
    ROOT / "data" / "action_verbs_seed3.json",
]


async def seed():
    print("=" * 60)
    print("Seed Action Verbs — 13 verbes")
    print("=" * 60)

    verbs = []
    for f in SEED_FILES:
        if not f.exists():
            print(f"ATTENTION: {f} introuvable — skip")
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        verbs.extend(data)

    print(f"Verbes a inserer : {len(verbs)}")

    cfg = get_settings()
    db_url = cfg.DATABASE_URL
    if not db_url:
        print("ERREUR: DATABASE_URL non configuree")
        return

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(db_url, echo=False)

    inserted = 0
    async with engine.begin() as conn:
        for v in verbs:
            await conn.execute(
                text("""
                    INSERT INTO action_verbs
                        (slug, ar, fr, category, priority,
                         definition_ar, objective_ar, formula_ar,
                         steps, required_markers, forbidden_markers,
                         common_errors, scoring_rules,
                         bad_example, good_example, feedback_template_ar)
                    VALUES
                        (:slug, :ar, :fr, :category, :priority,
                         :definition_ar, :objective_ar, :formula_ar,
                         :steps, :required_markers, :forbidden_markers,
                         :common_errors, :scoring_rules,
                         :bad_example, :good_example, :feedback_template_ar)
                    ON CONFLICT (slug) DO UPDATE SET
                        ar = EXCLUDED.ar,
                        fr = EXCLUDED.fr,
                        category = EXCLUDED.category,
                        priority = EXCLUDED.priority,
                        definition_ar = EXCLUDED.definition_ar,
                        objective_ar = EXCLUDED.objective_ar,
                        formula_ar = EXCLUDED.formula_ar,
                        steps = EXCLUDED.steps,
                        required_markers = EXCLUDED.required_markers,
                        forbidden_markers = EXCLUDED.forbidden_markers,
                        common_errors = EXCLUDED.common_errors,
                        scoring_rules = EXCLUDED.scoring_rules,
                        bad_example = EXCLUDED.bad_example,
                        good_example = EXCLUDED.good_example,
                        feedback_template_ar = EXCLUDED.feedback_template_ar
                """),
                {
                    "slug": v["slug"],
                    "ar": v["ar"],
                    "fr": v["fr"],
                    "category": v["category"],
                    "priority": v["priority"],
                    "definition_ar": v["definition_ar"],
                    "objective_ar": v["objective_ar"],
                    "formula_ar": v.get("formula_ar"),
                    "steps": json.dumps(v.get("steps", []), ensure_ascii=False),
                    "required_markers": json.dumps(v.get("required_markers", []), ensure_ascii=False),
                    "forbidden_markers": json.dumps(v.get("forbidden_markers", []), ensure_ascii=False),
                    "common_errors": json.dumps(v.get("common_errors", []), ensure_ascii=False),
                    "scoring_rules": json.dumps(v.get("scoring_rules", []), ensure_ascii=False),
                    "bad_example": json.dumps(v.get("bad_example"), ensure_ascii=False)
                    if v.get("bad_example")
                    else None,
                    "good_example": json.dumps(v.get("good_example"), ensure_ascii=False)
                    if v.get("good_example")
                    else None,
                    "feedback_template_ar": v.get("feedback_template_ar"),
                },
            )
            inserted += 1
            print(f"  [{inserted:02d}] {v['slug']}: {v['ar']} ({v['fr']})")

    await engine.dispose()
    print(f"\n{'=' * 60}")
    print(f"[OK] {inserted} verbes inseres/mis a jour")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(seed())
