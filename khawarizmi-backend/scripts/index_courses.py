# -*- coding: utf-8 -*-
"""
scripts/index_courses.py - Ingests SVT course documents into the PostgreSQL vector database (RAG).
"""

import os
import sys
import uuid
import asyncio
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Configurer the environment to avoid threads locks
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

# Add project root to python path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from config import get_settings
from services.embedder import embedder

COURSES_DIR = ROOT / "data" / "courses"


def chunk_text(text_content: str) -> list:
    """Chunks the text by double newline (paragraphs) for maximum semantic coherence."""
    paragraphs = [p.strip() for p in text_content.split("\n\n")]
    return [p for p in paragraphs if len(p) > 20]


async def index_chapter(file_path: Path, metadata: dict, engine):
    """Chunks a course file, generates vector embeddings, and inserts them into the DB."""
    if not file_path.exists():
        print(f"WARNING: File missing : {file_path.name}")
        return

    print(f"Reading course: {file_path.name}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = chunk_text(content)
    print(f"  -> {len(chunks)} chunks identified")

    # Generate embeddings in batch
    embeddings = embedder.encode(chunks)

    async with engine.begin() as conn:
        for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            chunk_id = uuid.uuid4()
            await conn.execute(
                text("""
                    INSERT INTO rag_chunks
                        (id, content, embedding, source, 
                         matiere, chapitre, importance,
                         chunk_index, created_at)
                    VALUES
                        (:id, :content, CAST(:embedding AS vector), :source,
                         :matiere, :chapitre, :importance,
                         :chunk_index, NOW())
                    ON CONFLICT (id) DO NOTHING
                """),
                {
                    "id": chunk_id,
                    "content": chunk,
                    "embedding": str(emb.tolist()),
                    "source": file_path.name,
                    "matiere": metadata["matiere"],
                    "chapitre": metadata["chapitre"],
                    "importance": metadata["importance"],
                    "chunk_index": idx
                }
            )

    print(f"  SUCCESS: {len(chunks)} chunks indexed.")


async def main():
    print("=" * 50)
    print("RAG Indexing - Khawarizmi Pro SVT")
    print("=" * 50)

    cfg = get_settings()
    db_url = cfg.DATABASE_URL
    if not db_url:
        db_url = os.getenv("DATABASE_URL")

    if not db_url:
        print("Error: DATABASE_URL not set in config or env.")
        return

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(db_url, echo=False)

    # Chapters to index corresponding to exact official titles in DB
    chapters_to_index = [
        {
            "file": "transcription_adn.txt",
            "metadata": {
                "matiere": "SVT",
                "chapitre": "Transcription de l'information genetique au niveau de l'ADN",
                "importance": "critique"
            }
        },
        {
            "file": "traduction_proteine.txt",
            "metadata": {
                "matiere": "SVT",
                "chapitre": "La traduction",
                "importance": "critique"
            }
        },
        {
            "file": "traduction_proteine.txt",
            "metadata": {
                "matiere": "SVT",
                "chapitre": "Les etapes de la traduction",
                "importance": "critique"
            }
        }
    ]

    for ch in chapters_to_index:
        file_path = COURSES_DIR / ch["file"]
        await index_chapter(file_path, ch["metadata"], engine)

    await engine.dispose()
    print("\nSUCCESS: All SVT RAG chapters indexed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
