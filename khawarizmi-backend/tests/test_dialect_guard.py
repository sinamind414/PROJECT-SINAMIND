"""Garde du dialect SQLAlchemy — bug production 503 (fix 2026-08-21).

Historique : _sqlite_compat() était appliqué INCONDITIONNELLEMENT à l'import
et empoisonnait sqlalchemy.dialects.postgresql via sys.modules.setdefault.
Résultat en production (DATABASE_URL postgres) : create_async_engine levait
« module 'sqlalchemy.dialects' has no attribute 'postgresql' », le lifespan
dégradait TOUTE l'API en 503.

Fix : shim conditionnel (uniquement SQLite ou URL inconnue) +
ensure_dialect_for_url() appelé par le lifespan avant la création du moteur
+ retrait possible du module factice si la cible devient PostgreSQL.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys

BACKEND = pathlib.Path(__file__).resolve().parent.parent

PG_URL = "postgresql+asyncpg://postgres:test@localhost/khawarizmi_test"
SQLITE_URL = "sqlite+aiosqlite:///./_dialect_guard_test.db"

_ENGINE_CHECK = """
from sqlalchemy.ext.asyncio import create_async_engine
e = create_async_engine(%r)
print('ENGINE OK')
"""


def _fresh_process(python_code: str, database_url: str) -> subprocess.CompletedProcess:
    env = {
        **{k: v for k, v in os.environ.items() if k not in ("DATABASE_URL",)},
        "DATABASE_URL": database_url,
        "SECRET_KEY": "dialect-guard-secret-key-16c",
        "ENVIRONMENT": "ci",
        "REDIS_URL": "",
        "PYTHONPATH": str(BACKEND),
    }
    return subprocess.run(
        [sys.executable, "-c", python_code],
        capture_output=True, text=True, env=env, cwd=str(BACKEND), timeout=120,
    )


def test_fresh_process_postgres_construit_engine() -> None:
    """Le cas production : env postgres dès l'import → dialect réel intact."""
    code = "import database\n" + (_ENGINE_CHECK % PG_URL)
    result = _fresh_process(code, PG_URL)
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr[-800:]}"
    assert "ENGINE OK" in result.stdout


def test_fresh_process_sqlite_construit_engine() -> None:
    """Le cas preview : env sqlite → patch compat + moteur OK."""
    code = "import database\n" + (_ENGINE_CHECK % SQLITE_URL)
    result = _fresh_process(code, SQLITE_URL)
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr[-800:]}"
    assert "ENGINE OK" in result.stdout
    try:
        (BACKEND / "_dialect_guard_test.db").unlink(missing_ok=True)
    except OSError:
        pass


def test_ensure_dialect_poste_import_restaure_postgres() -> None:
    """Cas env tardif : import sans URL (shim appliqué) puis cible postgres."""
    code = (
        "import os\n"
        "os.environ.pop('DATABASE_URL', None)\n"
        "import database\n"
        "from database import ensure_dialect_for_url\n"
        f"ensure_dialect_for_url({PG_URL!r})\n"
    ) + (_ENGINE_CHECK % PG_URL)
    result = _fresh_process(code, PG_URL)
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr[-800:]}"
    assert "ENGINE OK" in result.stdout


def test_ensure_dialect_retour_sqlite_apres_postgres() -> None:
    """Idempotence : repasser en SQLite après un passage postgres."""
    code = (
        "import database\n"
        "from database import ensure_dialect_for_url\n"
        f"ensure_dialect_for_url({PG_URL!r})\n"
        f"ensure_dialect_for_url({SQLITE_URL!r})\n"
    ) + (_ENGINE_CHECK % SQLITE_URL)
    result = _fresh_process(code, SQLITE_URL)
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr[-800:]}"
    assert "ENGINE OK" in result.stdout
    try:
        (BACKEND / "_dialect_guard_test.db").unlink(missing_ok=True)
    except OSError:
        pass
