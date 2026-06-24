"""
Script d'import du programme officiel.
Usage : python scripts/import_programme.py
"""

import asyncio
import json
import os
import sys
import unicodedata
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DB_URL = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://khawarizmi_user:MOT_DE_PASSE_FORT_ICI@localhost:5432/khawarizmi"
)


def get_session():
    engine = create_async_engine(DB_URL, pool_size=2)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return session_factory


PROGRAMMES_DIR = ROOT / "data" / "programmes"


def normalize_text(text: str) -> str:
    """Normalise le texte en préservant les accents UTF-8."""
    if not text:
        return text
    return unicodedata.normalize("NFC", text).strip()


async def import_programme(file_path: Path):
    print(f"\nImport : {file_path.name}")

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    matiere = normalize_text(data["matiere"])
    filiere = normalize_text(data["filiere"])

    session_factory = get_session()
    async with session_factory() as db:
        await db.execute(
            text("""
                DELETE FROM chapters
                WHERE unit_id IN (
                    SELECT id FROM units
                    WHERE domain_id IN (
                        SELECT id FROM domains
                        WHERE matiere = :matiere
                        AND filiere = :filiere
                    )
                )
            """),
            {"matiere": matiere, "filiere": filiere},
        )

        await db.execute(
            text("""
                DELETE FROM units
                WHERE domain_id IN (
                    SELECT id FROM domains
                    WHERE matiere = :matiere
                    AND filiere = :filiere
                )
            """),
            {"matiere": matiere, "filiere": filiere},
        )

        await db.execute(
            text("""
                DELETE FROM domains
                WHERE matiere = :matiere
                AND filiere = :filiere
            """),
            {"matiere": matiere, "filiere": filiere},
        )

        domain_count = 0
        unit_count = 0
        chapter_count = 0

        for domain_data in data["domains"]:
            domain_id = uuid4()

            await db.execute(
                text("""
                    INSERT INTO domains
                        (id, matiere, filiere, numero,
                         titre_fr, titre_ar)
                    VALUES
                        (:id, :matiere, :filiere, :numero,
                         :titre_fr, :titre_ar)
                """),
                {
                    "id": domain_id,
                    "matiere": matiere,
                    "filiere": filiere,
                    "numero": domain_data["numero"],
                    "titre_fr": normalize_text(domain_data["titre_fr"]),
                    "titre_ar": normalize_text(domain_data.get("titre_ar")) if domain_data.get("titre_ar") else None,
                },
            )
            domain_count += 1

            for unit_data in domain_data["units"]:
                unit_id = uuid4()

                await db.execute(
                    text("""
                        INSERT INTO units
                            (id, domain_id, numero,
                             titre_fr, titre_ar, page)
                        VALUES
                            (:id, :domain_id, :numero,
                             :titre_fr, :titre_ar, :page)
                    """),
                    {
                        "id": unit_id,
                        "domain_id": domain_id,
                        "numero": unit_data["numero"],
                        "titre_fr": normalize_text(unit_data["titre_fr"]),
                        "titre_ar": normalize_text(unit_data.get("titre_ar")) if unit_data.get("titre_ar") else None,
                        "page": unit_data.get("page"),
                    },
                )
                unit_count += 1

                for chap_data in unit_data.get("chapters", []):
                    await db.execute(
                        text("""
                            INSERT INTO chapters
                                (id, unit_id, numero,
                                 titre_fr, titre_ar, page,
                                 type, importance)
                            VALUES
                                (:id, :unit_id, :numero,
                                 :titre_fr, :titre_ar, :page,
                                 :type, :importance)
                        """),
                        {
                            "id": uuid4(),
                            "unit_id": unit_id,
                            "numero": chap_data["numero"],
                            "titre_fr": normalize_text(chap_data["titre_fr"]),
                            "titre_ar": normalize_text(chap_data.get("titre_ar"))
                            if chap_data.get("titre_ar")
                            else None,
                            "page": chap_data.get("page"),
                            "type": chap_data.get("type"),
                            "importance": chap_data.get("importance", "moyenne"),
                        },
                    )
                    chapter_count += 1

        await db.commit()

    print(f"  {domain_count} domaines")
    print(f"  {unit_count} unites")
    print(f"  {chapter_count} chapitres")


async def main():
    print("=" * 50)
    print("Import des programmes officiels Khawarizmi Pro")
    print("=" * 50)

    if not PROGRAMMES_DIR.exists():
        print(f"Dossier introuvable : {PROGRAMMES_DIR}")
        return

    json_files = list(PROGRAMMES_DIR.glob("*.json"))

    if not json_files:
        print(f"Aucun fichier JSON dans {PROGRAMMES_DIR}")
        return

    for file_path in json_files:
        await import_programme(file_path)

    print("\nImport termine.")


if __name__ == "__main__":
    asyncio.run(main())
