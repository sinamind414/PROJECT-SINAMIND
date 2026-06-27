"""Vérifie que les routes legacy sont bien vivantes avant dépréciation."""
import asyncio
from httpx import AsyncClient

LEGACY = [
    ("POST", "/api/chat"),
    ("POST", "/api/chatbot/ask"),
    ("POST", "/api/evaluate"),
]

NEW = [
    ("POST", "/api/ai/chat"),
    ("POST", "/api/ai/evaluate"),
]


async def check(base_url: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(base_url=base_url) as c:
        for method, path in LEGACY + NEW:
            r = await c.options(path, headers=headers)
            label = "OK" if r.status_code != 404 else "MISS"
            print(f"[{label}] {method} {path} -> {r.status_code}")


if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    tok = sys.argv[2] if len(sys.argv) > 2 else ""
    asyncio.run(check(url, tok))
