"""032 : normalisation arabe partagée pour le RAG (audit O4)

- add_column rag_chunks.content_norm (texte normalisé par services/arabic.py)
- Backfill des chunks existants EN PYTHON (ar_normalize n'est pas exprimable
  en SQL pur) — batch UPDATE par lot.
- Index trigram GIN sur content_norm SI PostgreSQL + pg_trgm (skippé
  silencieusement en SQLite/preview — le fallback ILIKE reste fonctionnel).

Note : le keyword_rag_search utilise COALESCE(content_norm, content) → les
lignes non backfillées gardent le comportement préexistant (matching brut).
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "032"
down_revision = "031"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("rag_chunks", sa.Column("content_norm", sa.Text(), nullable=True))

    # ── Backfill (Python — ar_normalize n'est pas du SQL) ─────────
    conn = op.get_bind()
    from services.arabic import ar_normalize

    while True:
        rows = conn.execute(
            sa.text(
                "SELECT id, content FROM rag_chunks "
                "WHERE content_norm IS NULL LIMIT 500"
            )
        ).fetchall()
        if not rows:
            break
        for rid, content in rows:
            conn.execute(
                sa.text(
                    "UPDATE rag_chunks SET content_norm = :n WHERE id = :id"
                ),
                {"n": ar_normalize(content or ""), "id": rid},
            )

    # ── Index trigram (PostgreSQL uniquement) ─────────────────────
    if conn.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        op.execute(
            "CREATE INDEX IF NOT EXISTS ix_rag_chunks_content_norm_trgm "
            "ON rag_chunks USING gin (content_norm gin_trgm_ops)"
        )


def downgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute(
            "DROP INDEX IF EXISTS ix_rag_chunks_content_norm_trgm"
        )
    op.drop_column("rag_chunks", "content_norm")
