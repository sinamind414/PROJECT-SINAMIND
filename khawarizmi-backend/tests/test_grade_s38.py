"""S38 — le 429 de quota est une RÉPONSE, pas une exception (audit surfaces 2026-08-30).

F12 d'origine : `main.py` branchait `_rate_limit_exceeded_handler` de slowapi sur le
STATUT 429. Ce handler lit `request.state.view_rate_limit`, que seul le
décorateur/middleware de limitation pose. `enforce_evaluate_quota`, lui, était appelé
à la main depuis /api/grade (route non décorée) et LEVAIT `HTTPException(429)` :
dès que l'auto-check du middleware ne passait pas par là (limiter désactivé,
middleware court-circuité), l'élève en surquota recevait

    AttributeError: 'State' object has no attribute 'view_rate_limit'  →  HTTP 500

au lieu du message arabe. Correctif : la réponse 429 est construite directement
(contract `erreur` + `banner_ar` + `Retry-After`) et le handler est branché sur la
CLASSE RateLimitExceeded.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "s38-test-secret-key-0123456789")

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.datastructures import Headers

import rate_limit as rl
from rate_limit import enforce_evaluate_quota, evaluate_limit, get_user_key
from routes.errors import rate_limit_exceeded_handler

BACKEND = Path(__file__).resolve().parent.parent
MAIN_SRC = (BACKEND / "main.py").read_text(encoding="utf-8")
RATE_SRC = (BACKEND / "rate_limit.py").read_text(encoding="utf-8")


class _Req:
    """Juste ce que lit le quota : headers (+ client pour le fallback IP)."""

    def __init__(self, headers: dict[str, str] | None = None):
        self.headers = Headers(headers or {})
        self.client = type("C", (), {"host": "203.0.113.9"})()
        self.state = type("S", (), {})()


def _fake_request(headers: dict[str, str] | None = None):
    """Request starlette minimale, SANS request.state.view_rate_limit (le cas qui crashait)."""
    from starlette.requests import Request

    app = FastAPI()
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/grade",
        "raw_path": b"/api/grade",
        "query_string": b"",
        "root_path": "",
        "scheme": "http",
        "headers": [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()],
        "client": ("203.0.113.9", 5555),
        "server": ("test", 80),
        "app": app,
    }
    return Request(scope), app


# ── 1. enforce_evaluate_quota répond, ne lève jamais ────────────────────────


def test_quota_returns_response_and_never_raises():
    from auth import create_access_token

    key = f"user:s38-{int(time.time() * 1000)}:free"
    tok = create_access_token({"sub": key.split(":")[1], "plan": "free"})
    req = _Req({"Authorization": f"Bearer {tok}"})
    assert get_user_key(req) == key, "la clé doit être celle du compte, sinon le seau est partagé"

    answers = [None] * 15
    for i, _ in enumerate(answers):
        assert enforce_evaluate_quota(req) is None, f"la correction {i + 1} doit passer"
    over = enforce_evaluate_quota(req)
    assert isinstance(over, JSONResponse), "le dépassement doit être une RÉPONSE (pas une levée)"
    import json

    body = json.loads(over.body.decode())
    assert over.status_code == 429
    assert body["code"] == "quota_exceeded"
    assert "Rate limit exceeded" not in json.dumps(body), "plus de wrapper anglais de slowapi"
    assert "ليست علامة بكالوريا رسمية" in body["erreur"], "l'élève doit lire le message arabe"
    assert "ليست علامة بكالوريا رسمية" in body["banner_ar"]
    assert body["status"] == 429


def test_quota_fail_open_when_limiter_disabled():
    """limiter.enabled = False -> aucune limitation, et surtout aucun 500."""
    from auth import create_access_token

    tok = create_access_token({"sub": "s38-disabled", "plan": "free"})
    req = _Req({"Authorization": f"Bearer {tok}"})
    prev = rl.limiter.enabled
    rl.limiter.enabled = False
    try:
        for _ in range(20):
            assert enforce_evaluate_quota(req) is None
    finally:
        rl.limiter.enabled = prev


def test_quota_fail_open_when_limiter_storage_broken():
    """Une panne de storage des limites ne doit JAMAIS remonter jusqu'à l'élève."""
    from auth import create_access_token

    class Boom:
        def hit(self, *a, **k):
            raise ConnectionError("redis down")

    tok = create_access_token({"sub": "s38-boom", "plan": "free"})
    req = _Req({"Authorization": f"Bearer {tok}"})
    prev = rl.limiter._limiter
    rl.limiter._limiter = Boom()
    try:
        assert enforce_evaluate_quota(req) is None
    finally:
        rl.limiter._limiter = prev


# ── 2. le handler 429 ne dépend plus de l'état slowapi ─────────────────────


def test_handler_survives_missing_view_rate_limit():
    """Cœur du crash : pas de request.state.view_rate_limit -> 429 propre, pas d'AttributeError."""
    req, app = _fake_request()
    assert not hasattr(req.state, "view_rate_limit"), "prérequis : l'état n'est pas posé"

    class _ExcError(Exception):
        detail = "15/hour"

    app.state.limiter = rl.limiter
    resp = _run(rate_limit_exceeded_handler(req, _ExcError()))
    assert resp.status_code == 429
    import json

    body = json.loads(resp.body.decode())
    assert body["code"] == "quota_exceeded"
    assert "ليست علامة بكالوريا رسمية" in body["erreur"]


def test_main_wires_handler_on_class_not_status():
    assert "add_exception_handler(429," not in MAIN_SRC, "le statut 429 ne doit plus être hijacké"
    assert "add_exception_handler(RateLimitExceeded" in MAIN_SRC
    assert "_rate_limit_exceeded_handler" not in MAIN_SRC, "le handler lent de slowapi est remplacé"


def test_rate_limit_module_raises_no_http_exception():
    assert "raise HTTPException" not in RATE_SRC
    assert "except HTTPException" not in RATE_SRC


def test_limiter_degrades_on_storage_outage():
    """swallow_errors + fallback mémoire : une panne Redis ne met pas le site en 500."""
    assert rl.limiter._swallow_errors is True
    assert rl.limiter._in_memory_fallback_enabled is True
    assert rl.limiter._fallback_limiter is not None


def test_evaluate_limit_tiers():
    assert evaluate_limit("user:1:free") == "15/hour"
    assert evaluate_limit("user:1:pro") == "80/hour"
    assert evaluate_limit("203.0.113.9") == "15/hour", "anonyme (clé IP) -> free"


def _run(coro):
    import asyncio

    return asyncio.run(coro)
