"""S16 — Redis optionnel sur le cache C1. Hors grade(). 0 user_id. 0 copie."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from services.grade_cache import (
    TTL_SEC,
    bind_redis,
    cache_get,
    cache_get_async,
    cache_set,
    cache_set_async,
    key_has_user_id,
    make_key,
    redis_available,
    reset,
)
from services.grade_metrics import snapshot as metrics_snapshot
from services.local_grader import GRADER_VERSION, grade
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent
ROOT = BACKEND.parent
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
CACHE = (BACKEND / "services" / "grade_cache.py").read_text(encoding="utf-8")
ROUTE = (BACKEND / "routes" / "grade.py").read_text(encoding="utf-8")
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")


class _FakeRedis:
    def __init__(self) -> None:
        self.data: dict[str, str] = {}
        self.last_ttl: int | None = None

    async def get(self, key: str):
        return self.data.get(key)

    async def setex(self, key: str, ttl: int, value: str):
        self.last_ttl = ttl
        self.data[key] = value


def setup_function() -> None:
    reset()


def teardown_function() -> None:
    reset()


def test_grader_has_no_redis_or_cache():
    assert "grade_cache" not in GRADER
    assert "redis" not in GRADER.lower()
    assert "from services.grade_cache" not in GRADER


def test_route_uses_async_cache_helpers():
    assert "cache_get_async" in ROUTE
    assert "cache_set_async" in ROUTE
    assert "from_cache" in ROUTE


def test_memory_works_without_redis():
    assert redis_available() is False
    yeast = load("manhadjiya-yeast-analyse")
    assert yeast is not None
    copy = yeast.rubric.model_answer
    r = grade(student_answer=copy, rubric=yeast.rubric, document=yeast.document)
    cache_set(make_key(yeast, copy), r)
    hit = cache_get(make_key(yeast, copy))
    assert hit is not None
    assert hit.from_cache is True
    assert hit.rubric_id == yeast.rubric.rubric_id


def test_redis_setex_7d_and_no_copy_in_blob():
    fake = _FakeRedis()
    bind_redis(fake)
    assert redis_available() is True
    yeast = load("manhadjiya-yeast-analyse")
    enzyme = load("enzyme-temp-analyse")
    assert yeast is not None and enzyme is not None
    copy = yeast.rubric.model_answer
    r = grade(student_answer=copy, rubric=yeast.rubric, document=yeast.document)
    assert r.cacheable is True
    k1 = make_key(yeast, copy)
    k2 = make_key(enzyme, copy)
    assert k1 != k2
    assert not key_has_user_id(k1)
    asyncio.run(cache_set_async(k1, r))
    assert fake.last_ttl == TTL_SEC
    blob = fake.data[k1]
    assert "student_answer" not in blob
    assert "user_id" not in blob
    assert "model_answer" not in blob
    payload = json.loads(blob)
    assert payload.get("from_cache") is False
    assert payload["rubric_id"] == yeast.rubric.rubric_id

    reset()
    bind_redis(fake)
    hit = asyncio.run(cache_get_async(k1))
    assert hit is not None
    assert hit.from_cache is True
    assert hit.rubric_id == yeast.rubric.rubric_id
    miss = asyncio.run(cache_get_async(k2))
    assert miss is None


def test_not_cacheable_not_in_redis():
    fake = _FakeRedis()
    bind_redis(fake)
    yeast = load("manhadjiya-yeast-analyse")
    assert yeast is not None
    r = grade(student_answer="   ", rubric=yeast.rubric, document=yeast.document)
    assert r.cacheable is False
    asyncio.run(cache_set_async(make_key(yeast, "   "), r))
    assert fake.data == {}


def test_metrics_cache_redis_flag_no_identity():
    fake = _FakeRedis()
    bind_redis(fake)
    snap = metrics_snapshot()
    assert snap["cache_redis"] is True
    assert snap["cache_enabled"] is True
    blob = str(snap)
    assert "user_id" not in blob
    assert "model_answer" not in blob


def test_grader_version_unchanged():
    assert GRADER_VERSION == "1.1.7"


def test_evaluate_still_not_mounted():
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT


def test_cache_module_does_not_import_redis_package():
    assert "from redis" not in CACHE
    assert "import redis" not in CACHE
