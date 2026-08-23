#!/usr/bin/env python3
"""Smoke test TOUTES méthodes : routes /api/* sur le backend SQLite (preview).

Complément de smoke_api_get.py : couvre POST/PUT/PATCH/DELETE avec corps vide
{} (sans auth) — les 401/403/422/404/405 sont attendus, seuls les 500 et
exceptions comptent (bugs réels : accès body avant validation, SQL invalide,
table absente de l'auto-DDL).

Denylist volontaire : routes à effet de bord coûteux qui ne doivent pas être
frappées sans auth (aucune ne devrait répondre autrement que 401, mais on ne
prend pas le risque d'un LLM/écriture).
Usage : .venv/bin/python scripts/smoke_api_all.py
"""
from __future__ import annotations

import asyncio
import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

os.environ.setdefault("SECRET_KEY", "smoke-test-secret-key-at-least-32-bytes")
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./smoke_api_all.db"
os.environ["ENVIRONMENT"] = "development"

import httpx

from main import app
from routes.lifespan import lifespan

_PATH_PARAM = re.compile(r"\{[^}]*\}")
# Routes à effet de bord coûteux : on n'envoie JAMAIS de requête réelle.
DENYLIST = {
    "/api/chatbot/ask", "/api/chatbot/ask/stream",
    "/api/ai/chat", "/api/ai/chat/stream",
    "/api/evaluate", "/api/ai-evaluate",
    "/api/document-analysis/evaluate", "/api/document-analysis/evaluate-v2",
}


def to_url(path: str) -> str:
    sluggy = ("slug", "chapter", "domain", "verb", "code", "type", "term")
    return _PATH_PARAM.sub(lambda m: "test" if any(s in m.group(0) for s in sluggy) else "1", path)


async def main() -> int:
    ops: set[tuple[str, str]] = set()
    for r in app.routes:
        path = getattr(r, "path", "")
        methods = getattr(r, "methods", set()) or set()
        if path.startswith("/api"):
            for m in methods:
                if m in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                    ops.add((m, path))
    print(f"{len(ops)} opérations HTTP sous /api")

    failed: list[tuple[str, str, int, str]] = []
    distribution: dict[int, int] = {}
    async with lifespan(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://smoke", timeout=8.0) as client:
            for method, path in sorted(ops):
                url = to_url(path)
                if url in DENYLIST:
                    continue
                try:
                    if method == "GET":
                        resp = await client.get(url)
                    else:
                        resp = await client.request(method, url, json={})
                except Exception as exc:
                    failed.append((method, url, 0, f"EXC {type(exc).__name__}: {str(exc)[:110]}"))
                    continue
                distribution[resp.status_code] = distribution.get(resp.status_code, 0) + 1
                if resp.status_code == 500:
                    failed.append((method, url, 500, resp.text[:150].replace("\n", " ")))
    print("Répartition des statuts :", dict(sorted(distribution.items())))
    if failed:
        print(f"\n❌ {len(failed)} opération(s) en échec (500/exception) :")
        for method, url, code, body in failed:
            print(f"  {code}  {method} {url}\n       {body}")
        return 1
    print("✅ Aucun 500 / exception sur l'ensemble des opérations (hors denylist)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
