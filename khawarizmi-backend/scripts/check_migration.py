"""Check alembic migration status."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from sqlalchemy import create_engine, text

from config import get_settings

s = get_settings()
engine = create_engine(s.DATABASE_URL)

with engine.connect() as conn:
    r = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')"))
    exists = r.scalar()
    print(f"alembic_version table exists: {exists}")

    if exists:
        r2 = conn.execute(text("SELECT version_num FROM alembic_version"))
        row = r2.fetchone()
        print(f"Alembic version: {row[0] if row else 'NO ROWS (empty table)'}")
    else:
        print("Alembic version table does not exist - chain is broken")

    r3 = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'lexique_termes')"))
    print(f"lexique_termes table exists: {r3.scalar()}")

    r4 = conn.execute(text("SELECT COUNT(*) FROM lexique_termes"))
    print(f"Terms in lexique_termes: {r4.scalar()}")
