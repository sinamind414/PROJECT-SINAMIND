"""
Script d'import des questions taggees et des micro-concepts.
Usage : python scripts/import_questions_taggees.py

Effectue :
1. Insertion des 42 micro-concepts depuis micro_concepts_reference.json
   dans la table micro_concepts (avec mapping chapitre_id).
2. Insertion des 234 mappings question -> micro_concept dans
   question_concept_map (concept principal + concepts secondaires).
"""

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from config import get_settings

# Mapping domaine -> chapitre_id (depuis programme_svt_3as_canonical.json)
DOMAIN_TO_CHAPITRE = {
    "prot": "ch1_proteines",
    "struc": "ch_structure_proteines",
    "enz": "ch2_enzymes",
    "imm": "ch3_immunite",
    "nerv": "ch4_nerveux",
    "photo": "ch_photosynthese",
    "resp": "ch_respiration",
    "tec": "ch_tectonique_plaques",
}

DATA_DIR = ROOT / "data"
OFFICIAL_DIR = DATA_DIR / "official"
MICRO_CONCEPTS_PATH = OFFICIAL_DIR / "micro_concepts_reference.json"
QUESTIONS_TAGGEES_PATH = DATA_DIR / "questions_taggees.json"


def get_domain_from_mc_id(mc_id: str) -> str:
    """Extrait le domaine d'un micro_concept_id (ex: mc_prot_01 -> prot)."""
    parts = mc_id.split("_")
    if len(parts) >= 2:
        return parts[1]
    return ""


async def import_micro_concepts(db: AsyncSession, concepts: list) -> int:
    """Insere ou met a jour les 42 micro-concepts dans la table micro_concepts."""
    count = 0
    for mc in concepts:
        mc_id = mc["id"]
        domain = get_domain_from_mc_id(mc_id)
        chapitre_id = DOMAIN_TO_CHAPITRE.get(domain, "ch_inconnu")

        await db.execute(
            text("""
                INSERT INTO micro_concepts
                    (id, chapitre_id, matiere, nom, code,
                     label_fr, label_ar)
                VALUES
                    (:id, :chapitre_id, :matiere, :nom, :code,
                     :label_fr, :label_ar)
                ON CONFLICT (id) DO UPDATE SET
                    chapitre_id = EXCLUDED.chapitre_id,
                    matiere     = EXCLUDED.matiere,
                    nom         = EXCLUDED.nom,
                    code        = EXCLUDED.code,
                    label_fr    = EXCLUDED.label_fr,
                    label_ar    = EXCLUDED.label_ar
            """),
            {
                "id": mc_id,
                "chapitre_id": chapitre_id,
                "matiere": "SVT",
                "nom": mc["nom_fr"],
                "code": mc_id,
                "label_fr": mc["nom_fr"],
                "label_ar": mc["nom_ar"],
            },
        )
        count += 1

    return count


async def import_question_concept_map(db: AsyncSession, questions: list) -> int:
    """Insere les mappings question -> micro_concept dans question_concept_map."""
    count = 0

    for q in questions:
        question_id = q["id"]
        primary_mc = q["micro_concept_id"]

        # Concept principal (weight = 1.0)
        await db.execute(
            text("""
                INSERT INTO question_concept_map
                    (question_id, micro_concept, weight)
                VALUES
                    (:qid, :mc, :weight)
                ON CONFLICT (question_id, micro_concept) DO UPDATE SET
                    weight = EXCLUDED.weight
            """),
            {"qid": question_id, "mc": primary_mc, "weight": 1.0},
        )
        count += 1

        # Concepts secondaires (weight = 0.5)
        for sec_mc in q.get("secondary_concepts", []):
            await db.execute(
                text("""
                    INSERT INTO question_concept_map
                        (question_id, micro_concept, weight)
                    VALUES
                        (:qid, :mc, :weight)
                    ON CONFLICT (question_id, micro_concept) DO UPDATE SET
                        weight = EXCLUDED.weight
                """),
                {"qid": question_id, "mc": sec_mc, "weight": 0.5},
            )
            count += 1

    return count


async def main():
    print("=" * 60)
    print("Import des micro-concepts et questions taggees")
    print("=" * 60)

    # Chargement des fichiers JSON
    with open(MICRO_CONCEPTS_PATH, "r", encoding="utf-8") as f:
        mc_data = json.load(f)

    with open(QUESTIONS_TAGGEES_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"\n  Micro-concepts a importer : {len(mc_data['micro_concepts'])}")
    print(f"  Questions taggees         : {len(questions)}")

    # Connexion a la DB (conversion vers asyncpg comme dans main.py)
    settings = get_settings()
    db_url = (
        settings.DATABASE_URL
        .replace("postgresql://", "postgresql+asyncpg://", 1)
        .replace("postgres://", "postgresql+asyncpg://", 1)
    )
    engine = create_async_engine(db_url, pool_size=2)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as db:
        print("\n[1/2] Insertion des micro-concepts...")
        mc_count = await import_micro_concepts(db, mc_data["micro_concepts"])
        await db.commit()
        print(f"  {mc_count} micro-concepts inseres/mis a jour")

        print("\n[2/2] Insertion des mappings question -> micro_concept...")
        map_count = await import_question_concept_map(db, questions)
        await db.commit()
        print(f"  {map_count} mappings inseres/mis a jour")

    await engine.dispose()

    # Verification
    print("\n" + "=" * 60)
    print("Verification")
    print("=" * 60)

    async with session_factory() as db:
        result = await db.execute(
            text("SELECT COUNT(*) FROM micro_concepts")
        )
        print(f"  Total micro_concepts en DB : {result.scalar()}")

        result = await db.execute(
            text("SELECT COUNT(*) FROM question_concept_map")
        )
        print(f"  Total mappings en DB       : {result.scalar()}")

        result = await db.execute(
            text("""
                SELECT COUNT(DISTINCT question_id)
                FROM question_concept_map
            """)
        )
        print(f"  Questions distinctes       : {result.scalar()}")

    print("\nImport termine avec succes.")


if __name__ == "__main__":
    asyncio.run(main())