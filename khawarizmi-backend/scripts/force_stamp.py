import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from sqlalchemy import create_engine, text

from config import get_settings

s = get_settings()
engine = create_engine(s.DATABASE_URL)

with engine.connect() as conn:
    trans = conn.begin()
    try:
        conn.execute(
            text("UPDATE alembic_version SET version_num = '005'")
        )
        trans.commit()
        print("Stamped alembic to 005 (via SQL UPDATE)")
    except Exception as e:
        trans.rollback()
        print(f"UPDATE failed: {e}, trying INSERT...")
        try:
            with engine.connect() as conn2:
                conn2.execute(
                    text("DELETE FROM alembic_version")
                )
                conn2.execute(
                    text("INSERT INTO alembic_version (version_num) VALUES ('005')")
                )
                conn2.commit()
                print("Stamped alembic to 005 (via DELETE+INSERT)")
        except Exception as e2:
            print(f"Both failed: {e2}")

# Verify
with engine.connect() as conn:
    r = conn.execute(text("SELECT version_num FROM alembic_version"))
    print("Alembic version now:", r.scalar())
