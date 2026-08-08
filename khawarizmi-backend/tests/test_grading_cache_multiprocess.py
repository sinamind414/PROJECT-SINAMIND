"""Test multi-process du single-flight C2 — 2 vrais workers sur le même Redis.

Le single-flight inter-workers repose sur : verrou Redis NX (30 s) + attente
bornée + double-check post-verrou. Ce test lance 2 PROCESSUS Python réels
(scripts/_cache_worker_mp.py) qui corrigent la MÊME copie en même temps
(starting gate par clé Redis) et vérifie :

  1. total des appels LLM = 1 (fusion inter-workers) ;
  2. un worker a from_cache=True, l'autre a corrigé ;
  3. les deux obtiennent le même score (cohérence).

SKIP si REDIS_TEST_URL indisponible (suite verte partout).
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from pathlib import Path

import pytest
import redis.asyncio as aioredis

REDIS_TEST_URL = os.environ.get("REDIS_TEST_URL", "redis://127.0.0.1:6390")
BACKEND = Path(__file__).resolve().parent.parent

ANS = "نلاحظ من الوثيقة أن نسبة الغلوكوز تزداد من 0.8 إلى 1.4 غ/ل"


def _env() -> dict:
    env = dict(os.environ)
    env.setdefault("SECRET_KEY", "ci-test-key-for-smoke-tests-only")
    env.setdefault("ENVIRONMENT", "ci")
    env.setdefault("DATABASE_URL", "sqlite+aiosqlite:////tmp/audit_test.db")
    env.setdefault("REDIS_URL", "")
    return env


@pytest.fixture
async def real_redis():
    try:
        client = aioredis.from_url(REDIS_TEST_URL, decode_responses=True)
        await client.ping()
    except Exception as e:
        pytest.skip(f"Redis indisponible ({REDIS_TEST_URL}) : {e}")
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()


async def _run_worker(redis_url: str, gate_key: str, qid: int) -> dict:
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        str(BACKEND / "scripts" / "_cache_worker_mp.py"),
        "--redis-url", redis_url,
        "--gate-key", gate_key,
        "--qid", str(qid),
        "--verb", "analyse",
        "--answer", ANS,
        "--llm-ms", "500",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=_env(),
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=40)
    except TimeoutError:
        proc.kill()
        await proc.communicate()
        pytest.fail(f"worker {qid} timeout")
    if proc.returncode != 0:
        pytest.fail(f"worker {qid} a échoué (rc={proc.returncode}) : "
                    f"{stderr.decode(errors='replace')[-500:]}")
    return json.loads(stdout.decode().strip().splitlines()[-1])


async def _wait_ready(real_redis, gate_key: str, n: int, timeout: float = 30.0) -> None:
    deadline = asyncio.get_event_loop().time() + timeout
    ready = 0
    while asyncio.get_event_loop().time() < deadline:
        try:
            ready = len(await real_redis.keys(f"{gate_key}:ready:*"))
        except Exception as e:  # pragma: no cover — diagnostic
            print(f"_wait_ready: keys() erreur: {e}")
            ready = -1
        if ready >= n:
            return
        await asyncio.sleep(0.2)
    pytest.fail(f"workers non prêts après {timeout}s (ready={ready}/{n}, gate={gate_key})")


@pytest.mark.asyncio
async def test_two_workers_same_copy_single_llm_call(real_redis):
    """Acceptation C2 #9 inter-workers : 2 processus réels, même copie,
    même Redis → 1 seul appel LLM."""
    qid = 777
    gate_key = f"gate:{uuid.uuid4().hex}"

    # Démarrage simultané : les 2 workers se bloquent sur le gate
    workers = [
        asyncio.create_task(_run_worker(REDIS_TEST_URL, gate_key, qid)),
        asyncio.create_task(_run_worker(REDIS_TEST_URL, gate_key, qid)),
    ]
    await _wait_ready(real_redis, gate_key, 2)
    await real_redis.set(gate_key, "go")

    r1, r2 = await asyncio.gather(*workers)
    await real_redis.delete(gate_key)

    total_calls = r1["calls"] + r2["calls"]
    assert total_calls == 1, f"single-flight inter-workers cassé : {total_calls} appels"
    assert sorted([r1["from_cache"], r2["from_cache"]]) == [False, True]
    assert r1["score"] == r2["score"] == 5


@pytest.mark.asyncio
async def test_two_workers_different_copies_two_calls(real_redis):
    """Contrôle : 2 workers sur des copies DIFFÉRENTES → 2 appels LLM
    (pas de fusion abusive)."""

    # réutiliser le worker avec une réponse différente via un wrapper
    # (le worker prend --answer en argument)
    qid = 778
    gate_key = f"gate:{uuid.uuid4().hex}"
    ans2 = "نستنتج أن البنكرياس يفرز الأنسولين الذي يخفض نسبة السكر"

    async def run(ans: str):
        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            str(BACKEND / "scripts" / "_cache_worker_mp.py"),
            "--redis-url", REDIS_TEST_URL,
            "--gate-key", gate_key,
            "--qid", str(qid),
            "--verb", "analyse",
            "--answer", ans,
            "--llm-ms", "300",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=_env(),
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=40)
        assert proc.returncode == 0, stderr.decode(errors="replace")[-500:]
        return json.loads(stdout.decode().strip().splitlines()[-1])

    workers = [
        asyncio.create_task(run(ANS)),
        asyncio.create_task(run(ans2)),
    ]
    await _wait_ready(real_redis, gate_key, 2)
    await real_redis.set(gate_key, "go")

    r1, r2 = await asyncio.gather(*workers)
    await real_redis.delete(gate_key)

    total_calls = r1["calls"] + r2["calls"]
    assert total_calls == 2, f"2 copies distinctes devraient coûter 2 appels : {total_calls}"
    assert r1["from_cache"] is False and r2["from_cache"] is False
