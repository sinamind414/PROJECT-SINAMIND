"""tests/test_migration_032.py — Migration 032 : rag_chunks.content_norm.

⚠️ Le backfill complet (add_column + UPDATE par lots) est validé MANUELLEMENT
(hors pytest) : l'import d'une migration Alembic échoue dans l'environnement
pytest — le fake module postgresql de database.py (compat SQLite) n'expose
pas les types requis par alembic.ddl.postgresql (BIGINT…). Les migrations
Alembic sont Postgres-only (CREATE EXTENSION vector des migrations
antérieures) ; le preview/CI utilise l'auto-DDL de database.py.

Validation manuelle exécutée (voir rapport) :
    alembic upgrade 032 sur SQLite temporaire (backfill normalisé OK,
    index trigram skippé en SQLite).

Ce test couvre l'invariant clé : le backfill est IDEMPOTENT (ar_normalize).
"""

from services.arabic import ar_normalize


def test_backfill_is_idempotent():
    """Re-normaliser une valeur déjà normalisée ne change rien."""
    once = ar_normalize("الحرارة المثلى للإنزيم")
    assert once == "الحراره المثلي للانزيم"
    assert ar_normalize(once) == once
