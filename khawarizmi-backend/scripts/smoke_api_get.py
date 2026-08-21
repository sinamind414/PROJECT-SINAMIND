#!/usr/bin/env python3
"""Smoke test GET : toutes les routes /api/* sur le backend SQLite (preview).

Sans auth : classe les réponses (200 public · 401/403 attendu · 422 validation
· 404 dummy id) et remonte uniquement les 500 — bugs réels de preview
(incompatibilité SQL, table absente de l'auto-DDL, erreur de code).
Usage : .venv/bin/python scripts/smoke_api_get.py
"""
from __future__ import annotations

import asyncio
import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

os.environ.setdefault("SECRET_KEY", "smoke-test-secret-key-16chars")
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./smoke_api.db"
os.environ["ENVIRONMENT"] = "development"

import httpx  # noqa: E402

from main import app  # noqa: E402
from routes.lifespan import lifespan  # noqa: E402

_PATH_PARAM = re.compile(r"\{[^}]*\}")


def to_url(path: str) -> str:
    sluggy = ("slug", "chapter", "domain", "verb", "code", "type")
    return _PATH_PARAM.sub(lambda m: "test" if any(s in m.group(0) for s in sluggy) else "1", path)


async def main() -> int:
    routes = sorted(
        {
            (getattr(r, "path", ""), tuple(sorted(getattr(r, "methods", set()) or set())))
            for r in app.routes
            if getattr(r, "path", "").startswith("/api") and "GET" in (getattr(r, "methods", set()) or set())
        }
    )
    print(f"{len(routes)} routes GET sous /api")

    failed: list[tuple[str, int, str]] = []
    async with lifespan(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://smoke", timeout=8.0) as client:
            for path, _ in routes:
                url = to_url(path)
                try:
                    resp = await client.get(url)
                except Exception as exc:  # noqa: BLE001
                    failed.append((url, 0, f"EXC {type(exc).__name__}: {str(exc)[:120]}"))
                    continue
                code = resp.status_code
                if code == 500:
                    body = resp.text[:160].replace("\n", " ")
                    failed.append((url, code, body))
    if failed:
        print(f"\n❌ {len(failed)} route(s) en 500 :")
        for url, code, body in failed:
            print(f"  {code}  GET {url}\n       {body}")
        return 1
    print("✅ Aucune route GET en 500 (hors timeout/exceptions ci-dessus)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
