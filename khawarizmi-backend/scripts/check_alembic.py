import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import get_settings
from sqlalchemy import create_engine, text

s = get_settings()
engine = create_engine(s.DATABASE_URL)
with engine.connect() as conn:
    r = conn.execute(text("SELECT version_num FROM alembic_version"))
    print("Alembic version:", r.scalar())
