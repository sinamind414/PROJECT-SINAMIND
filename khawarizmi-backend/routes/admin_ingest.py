# routes/admin_ingest.py — Temporaire : ingestion RAG livre manhadjiya
import os
from pathlib import Path

from fastapi import APIRouter, Header, HTTPException

router = APIRouter(tags=["admin"])


@router.get("/api/admin/ingest-rag")
async def ingest_rag(x_admin_token: str = Header("")):
    secret = os.environ.get("ADMIN_SECRET", "")
    if not secret or x_admin_token != secret:
        raise HTTPException(status_code=404, detail="Not found")
    from scripts.ingest_livre_manhadjiya import (
        ingest_chunks_to_db,
        parse_markdown_sections,
        sections_to_chunks,
    )
    md_path = Path(__file__).resolve().parent.parent / "LIVRE-MANHADJIYA.md"
    if not md_path.exists():
        raise HTTPException(status_code=400, detail="LIVRE-MANHADJIYA.md not found")
    md = md_path.read_text(encoding="utf-8")
    sections = parse_markdown_sections(md)
    chunks = sections_to_chunks(sections)
    db_url = os.environ.get("DATABASE_URL", "")
    inserted = await ingest_chunks_to_db(chunks, db_url=db_url)
    return {"status": "ok", "sections": len(sections), "chunks": len(chunks), "inserted": inserted}
