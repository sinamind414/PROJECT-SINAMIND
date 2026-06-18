# Khawarizmi Pro — Configuration
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://khawarizmi:khawarizmi@localhost:5432/khawarizmi_pro",
)

ALEMBIC_DATABASE_URL = DATABASE_URL
