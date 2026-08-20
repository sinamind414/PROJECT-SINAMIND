"""Garde-fou de portabilité SQL — v2 (2026-08-20).

Le garde historique test_fsrs_scheduler_no_in_tuple (test_config_critical.py)
pointe services/fsrs_scheduler.py, fichier supprimé par la fusion FSRS :
il skippait en silence et la règle AGENTS.md §1.5 n'était plus enforcée.
Ce nouveau fichier (aucun test existant modifié) encode la règle moderne,
compatible avec le preview SQLite ET PostgreSQL/asyncpg :

1. « IN :param » (texte SQL) exige bindparam("param", expanding=True) dans
   le même fichier — seule forme portable (asyncpg refuse les tuples IN
   sans expanding ; SQLite ne connaît pas ANY).
2. « col = ANY(:param) » (liste en paramètre) est interdit : non portable
   (SQLite : no such function ANY) — utiliser IN + expanding.
   « :param = ANY(col) » (colonne ARRAY) reste autorisé : réécrit en
   EXISTS json_each par le hook SQLite de database.py (recherche annales).
3. Le hook database.py doit rester présent (réécriture :param = ANY(col)
   + json_each) — sinon la recherche d'annales casse à nouveau en preview.
"""
from __future__ import annotations

import pathlib
import re

BACKEND = pathlib.Path(__file__).resolve().parent.parent
SQL_DIRS = ["services", "routes", "models", "grading"]

_IN_PARAM_RE = re.compile(r"\bIN\s+:(\w+)", re.IGNORECASE)
_ANY_PARAM_RE = re.compile(r"=\s*ANY\s*\(\s*:\w+", re.IGNORECASE)


def _sql_files() -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for d in SQL_DIRS:
        files.extend((BACKEND / d).glob("*.py"))
    return files


def test_in_param_exige_expanding() -> None:
    """Chaque « IN :name » doit avoir bindparam('name', expanding=True)."""
    for path in _sql_files():
        text = path.read_text(encoding="utf-8")
        for match in _IN_PARAM_RE.finditer(text):
            param = match.group(1)
            expanding_double = f'bindparam("{param}", expanding=True)' in text
            expanding_single = f"bindparam('{param}', expanding=True)" in text
            assert expanding_double or expanding_single, (
                f"{path.relative_to(BACKEND)}: 'IN :{param}' sans "
                f"bindparam('{param}', expanding=True) — bug asyncpg/SQLite "
                f"(règle AGENTS.md §1.5)"
            )


def test_any_sur_param_interdit() -> None:
    """« col = ANY(:param) » interdit (non portable SQLite) — IN + expanding."""
    for path in _sql_files():
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//"):
                continue  # commentaires (ex. note explicative scheduler.py)
            assert not _ANY_PARAM_RE.search(line), (
                f"{path.relative_to(BACKEND)}:{lineno}: '= ANY(:param)' non portable "
                f"sur SQLite — utiliser IN + bindparam(expanding=True)"
            )


def test_hook_sqlite_any_colonne_present() -> None:
    """Le hook :param = ANY(colonne) → json_each doit rester dans database.py."""
    text = (BACKEND / "database.py").read_text(encoding="utf-8")
    assert "_PARAM_EQ_ANY_COL_RE" in text, "hook SQLite ANY manquant dans database.py"
    assert "json_each" in text, "réécriture json_each manquante dans database.py"
    assert "_param_eq_any_col_sqlite" in text, "fonction de réécriture manquante"
