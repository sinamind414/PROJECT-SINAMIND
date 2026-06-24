# scripts/ingest_claude_opus.py
# Ingeste le fichier PROGRAMME NATIONAL SVT généré par Claude Opus
# dans la table rag_chunks pour le RAG.

import asyncio
import os
import re
import sys
import uuid
from pathlib import Path

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from config import get_settings
from services.embedder import embedder

COURSE_FILE = ROOT / "data" / "courses" / "programme_national_svt_claude_opus.md"

UNIT_RE = re.compile(r"^# [^\s] الوحدة (\d+): (.+)$", re.MULTILINE)
DOMAINE_RE = re.compile(r"^# [^\s] المجال (.+?): (.+)$", re.MULTILINE)
SECTION_RE = re.compile(r"^## ", re.MULTILINE)

MATIERE = "SVT"
FILIERE = "Sciences Experimentales"


def parse_units(content: str):
    lines = content.split("\n")
    units = []
    current_domaine = ""
    current_unit = None
    current_lines = []

    for line in lines:
        dm = DOMAINE_RE.match(line)
        if dm:
            current_domaine = dm.group(2).strip()

        um = UNIT_RE.match(line)
        if um:
            if current_unit and current_lines:
                units.append((current_domaine, current_unit, "\n".join(current_lines)))
            current_unit = f"Unite {um.group(1)}: {um.group(2).strip()}"
            current_lines = [line]
        else:
            if current_unit is not None:
                current_lines.append(line)

    if current_unit and current_lines:
        units.append((current_domaine, current_unit, "\n".join(current_lines)))

    return units


def chunk_section(content: str, min_chars: int = 100):
    parts = SECTION_RE.split(content)
    chunks = []
    for p in parts:
        p = p.strip()
        if len(p) < min_chars:
            continue
        if len(p) > 2000:
            sub = [p[i : i + 1500] for i in range(0, len(p), 1500)]
            chunks.extend(sub)
        else:
            chunks.append(p)
    return chunks


async def ingest():
    print("=" * 60)
    print("Ingestion RAG - Programme National SVT Claude Opus")
    print("=" * 60)

    if not COURSE_FILE.exists():
        print(f"ERREUR: Fichier introuvable : {COURSE_FILE}")
        return

    with open(COURSE_FILE, encoding="utf-8") as f:
        content = f.read()

    units = parse_units(content)
    print(f"Unites detectees : {len(units)}")

    cfg = get_settings()
    db_url = cfg.DATABASE_URL or os.getenv("DATABASE_URL")
    if not db_url:
        print("ERREUR: DATABASE_URL non configurée")
        return

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(db_url, echo=False)

    total_chunks = 0
    count = [0]
    for _domaine, chapitre, unit_content in units:
        chunks = chunk_section(unit_content)
        if not chunks:
            continue

        count[0] += 1
        print(f"\n[Unite {count[0]:02d}] ({len(chunks)} chunks)")
        sys.stdout.flush()

        embeddings = embedder.encode(chunks)

        async with engine.begin() as conn:
            for idx, (chunk, emb) in enumerate(zip(chunks, embeddings, strict=False)):
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
                        "source": "programme_national_svt_claude_opus.md",
                        "matiere": MATIERE,
                        "chapitre": chapitre,
                        "importance": "critique",
                        "chunk_index": idx,
                    },
                )
            total_chunks += len(chunks)
        print(f"   -> {len(chunks)} inseres")

    await engine.dispose()
    print(f"\n{'=' * 60}")
    print(f"[OK] Ingestion terminee : {total_chunks} chunks inseres")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(ingest())
