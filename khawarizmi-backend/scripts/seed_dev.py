#!/usr/bin/env python3
"""seed_dev.py — Seed unifié Khawarizmi Pro.

Usage:
    python scripts/seed_dev.py [--force]

Insère les données de développement dans l'ordre :
  1. Verbes d'action    (action_verbs)
  2. Analyse doc        (da_scenarios, da_questions)
  3. Leçons             (lesson_blocks)
  4. Sujets Bac Blanc   (bac_subjects)
  5. Programme SVT      (domains, units, chapters, micro_concepts…)

Utilise asyncpg direct (pas de dépendance FastAPI / lifespan).
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"

sys.path.insert(0, str(ROOT))

import asyncpg

DB_DSN = "postgresql://khawarizmi_user:MOT_DE_PASSE_FORT_ICI@localhost:5432/khawarizmi"

DATA_FILES = {
    "action_verbs": ROOT / "data" / "action_verbs_seed.json",
    "document_analysis": SCRIPTS / "document_analysis_seed.json",
    "lessons": SCRIPTS / "lessons_seed.json",
    "bac_blanc": SCRIPTS / "bac_blanc_seed.json",
}


# ── helpers ─────────────────────────────────────────────────────────────


def load_json(path: Path) -> list | dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


async def table_count(conn: asyncpg.Connection, table: str) -> int:
    return await conn.fetchval(f"SELECT COUNT(*) FROM {table}")


# ── seeders ─────────────────────────────────────────────────────────────


async def seed_action_verbs(conn: asyncpg.Connection) -> int:
    data = load_json(DATA_FILES["action_verbs"])
    if isinstance(data, dict):
        verbs = data.get("action_verbs", [])
    else:
        verbs = data
    inserted = 0
    for v in verbs:
        slug = v["slug"]
        exists = await conn.fetchval("SELECT 1 FROM action_verbs WHERE slug = $1", slug)
        if exists:
            continue
        await conn.execute(
            """
            INSERT INTO action_verbs
                (slug, ar, fr, category, priority,
                 definition_ar, objective_ar, formula_ar,
                 steps, required_markers, forbidden_markers,
                 common_errors, scoring_rules,
                 bad_example, good_example, feedback_template_ar)
            VALUES
                ($1,$2,$3,$4,$5,
                 $6,$7,$8,
                 $9,$10,$11,
                 $12,$13,
                 $14,$15,$16)
            """,
            slug, v["ar"], v["fr"], v.get("category", "general"), v.get("priority", "medium"),
            v.get("definition_ar", ""), v.get("objective_ar", ""), v.get("formula_ar", ""),
            json.dumps(v.get("steps", []), ensure_ascii=False),
            json.dumps(v.get("required_markers", []), ensure_ascii=False),
            json.dumps(v.get("forbidden_markers", []), ensure_ascii=False),
            json.dumps(v.get("common_errors", []), ensure_ascii=False),
            json.dumps(v.get("scoring_rules", []), ensure_ascii=False),
            json.dumps(v.get("bad_example", {}), ensure_ascii=False),
            json.dumps(v.get("good_example", {}), ensure_ascii=False),
            v.get("feedback_template_ar", ""),
        )
        inserted += 1
    return inserted


async def seed_doc_analysis(conn: asyncpg.Connection) -> tuple[int, int]:
    data = load_json(DATA_FILES["document_analysis"])
    scenarios_ok = questions_ok = 0
    for sc in data:
        slug = sc["slug"]
        exists = await conn.fetchval("SELECT 1 FROM da_scenarios WHERE slug = $1", slug)
        if exists:
            continue
        unit_key = sc.get("unit_key", "")[:50]  # varchar(50) en base
        sc_id = await conn.fetchval(
            """
            INSERT INTO da_scenarios
                (slug, unit_key, title_ar, subtitle_ar, context_ar, dominant_skills)
            VALUES ($1,$2,$3,$4,$5,$6)
            RETURNING id
            """,
            slug, unit_key, sc["title_ar"], sc.get("subtitle_ar", ""),
            sc.get("context_ar", ""),
            json.dumps(sc.get("dominant_skills", []), ensure_ascii=False),
        )
        scenarios_ok += 1
        for q in sc.get("questions", []):
            await conn.execute(
                """
                INSERT INTO da_questions
                    (scenario_id, verb_slug, level, n, title_ar, skill_ar,
                     doc_ref, prompt_ar, placeholder_ar, model_answer_ar, learning_focus_ar)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
                """,
                sc_id, q["verb_slug"], q.get("level", 1), q.get("n", 0),
                q.get("title_ar", ""), q.get("skill_ar", ""),
                q.get("doc_ref", ""), q.get("prompt_ar", ""),
                q.get("placeholder_ar", ""), q.get("model_answer_ar", ""),
                q.get("learning_focus_ar", ""),
            )
            questions_ok += 1
    return scenarios_ok, questions_ok


async def seed_lessons(conn: asyncpg.Connection) -> int:
    data = load_json(DATA_FILES["lessons"])
    if isinstance(data, list):
        blocks = data
    else:
        blocks = data.get("lesson_blocks", data.get("lessons", []))
    inserted = 0
    for blk in blocks:
        chapter_slug = blk.get("chapter_slug", blk.get("chapitre_slug", ""))
        block_type = blk.get("block_type", blk.get("type", "content"))
        sort_order = blk.get("sort_order", blk.get("order", 0))
        title_ar = blk.get("title_ar", blk.get("titre_ar", ""))
        body_ar = blk.get("body_ar", blk.get("contenu_ar", ""))
        visual_hint = blk.get("visual_hint", blk.get("visuel", ""))
        quick_check = json.dumps(blk.get("quick_check", blk.get("verification_rapide", {})), ensure_ascii=False)
        exists = await conn.fetchval(
            "SELECT 1 FROM lesson_blocks WHERE chapter_slug = $1 AND sort_order = $2 AND block_type = $3",
            chapter_slug, sort_order, block_type,
        )
        if exists:
            continue
        await conn.execute(
            """
            INSERT INTO lesson_blocks
                (chapter_slug, block_type, sort_order, title_ar, body_ar, visual_hint, quick_check)
            VALUES ($1,$2,$3,$4,$5,$6,$7)
            """,
            chapter_slug, block_type, sort_order, title_ar, body_ar, visual_hint, quick_check,
        )
        inserted += 1
    return inserted


async def seed_bac_blanc(conn: asyncpg.Connection) -> int:
    data = load_json(DATA_FILES["bac_blanc"])
    if isinstance(data, dict):
        subjects = data.get("bac_subjects", data.get("subjects", []))
    else:
        subjects = data
    inserted = 0
    for subj in subjects:
        annale_slug = subj.get("annale_slug", subj.get("slug", ""))
        subject_number = subj.get("subject_number", subj.get("numero", 1))
        title_ar = subj.get("title_ar", subj.get("titre_ar", ""))
        themes_ar = json.dumps(subj.get("themes_ar", subj.get("themes", [])), ensure_ascii=False)
        estimated_minutes = subj.get("estimated_minutes", subj.get("duree", 120))
        exercises = json.dumps(subj.get("exercises", subj.get("exercices", [])), ensure_ascii=False)
        exists = await conn.fetchval(
            "SELECT 1 FROM bac_subjects WHERE annale_slug = $1 AND subject_number = $2",
            annale_slug, subject_number,
        )
        if exists:
            continue
        await conn.execute(
            """
            INSERT INTO bac_subjects
                (annale_slug, subject_number, title_ar, themes_ar, estimated_minutes, exercises)
            VALUES ($1,$2,$3,$4,$5,$6)
            """,
            annale_slug, subject_number, title_ar, themes_ar, estimated_minutes, exercises,
        )
        inserted += 1
    return inserted


# ── main ────────────────────────────────────────────────────────────────


async def main(force: bool = False) -> None:
    conn = await asyncpg.connect(DB_DSN)

    print("=" * 60)
    print("  SEED DEV — Khawarizmi Pro")
    print("=" * 60)

    # 1. Action verbs
    n = await seed_action_verbs(conn)
    c = await table_count(conn, "action_verbs")
    print(f"  [1/5] Verbes d'action      : {n} nouveaux — total {c}")

    # 2. Document analysis
    ns, nq = await seed_doc_analysis(conn)
    cs = await table_count(conn, "da_scenarios")
    cq = await table_count(conn, "da_questions")
    print(f"  [2/5] Analyse documentaire : {ns} scénarios, {nq} questions — total {cs} scénarios / {cq} questions")

    # 3. Lessons
    n = await seed_lessons(conn)
    c = await table_count(conn, "lesson_blocks")
    print(f"  [3/5] Leçons               : {n} nouveaux blocs — total {c}")

    # 4. Bac Blanc
    n = await seed_bac_blanc(conn)
    c = await table_count(conn, "bac_subjects")
    print(f"  [4/5] Sujets Bac Blanc     : {n} nouveaux sujets — total {c}")

    # 5. Programme SVT (via import_programme.py logique)
    print("  [5/5] Programme SVT…")
    from scripts.import_programme import import_programme
    programmes_dir = ROOT / "data" / "programmes"
    for fpath in sorted(programmes_dir.glob("*.json")):
        await import_programme(fpath)

    # — counts finaux —
    counts = {
        "action_verbs": await table_count(conn, "action_verbs"),
        "da_scenarios": await table_count(conn, "da_scenarios"),
        "da_questions": await table_count(conn, "da_questions"),
        "lesson_blocks": await table_count(conn, "lesson_blocks"),
        "bac_subjects": await table_count(conn, "bac_subjects"),
        "domains": await table_count(conn, "domains"),
        "units": await table_count(conn, "units"),
        "chapters": await table_count(conn, "chapters"),
        "micro_concepts": await table_count(conn, "micro_concepts"),
    }
    print("—" * 30)
    for k, v in counts.items():
        print(f"  {k:25s}: {v}")
    print("=" * 60)
    print("  [OK] Seed terminé")
    print("=" * 60)

    await conn.close()


if __name__ == "__main__":
    force = "--force" in sys.argv
    asyncio.run(main(force=force))
