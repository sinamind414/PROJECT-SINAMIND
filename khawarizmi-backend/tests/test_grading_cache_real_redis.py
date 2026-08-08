"""Tests d'intégration du cache C2 contre un VRAI Redis (Lua CAS réel).

Le FakeRedis des tests unitaires ne parse jamais le script Lua de
libération du verrou (_RELEASE_LUA) ni ne respecte la sémantique NX/TTL
réelle de Redis. Ces tests valident le single-flight et les invariants C2
contre un vrai serveur Redis 6.x+.

Condition : REDIS_TEST_URL (défaut redis://127.0.0.1:6390) joignable —
sinon les tests sont SKIPPÉS (la suite reste verte dans les sandboxes
sans Redis). Pour lancer localement :
    redis-server --port 6390 &
    REDIS_TEST_URL=redis://127.0.0.1:6390 pytest tests/test_grading_cache_real_redis.py -q
"""

from __future__ import annotations

import json
import os
from unittest.mock import AsyncMock

import pytest
import redis.asyncio as aioredis

from app_state import state
from grading.cache import (
    evaluate_with_cache,
    is_cacheable,
)
from grading.cache_key import key_normalize

REDIS_TEST_URL = os.environ.get("REDIS_TEST_URL", "redis://127.0.0.1:6390")

ANS = "نلاحظ من الوثيقة أن نسبة الغلوكوز تزداد من 0.8 إلى 1.4 غ/ل"
QID = 4242
VERB = "analyse"
SMAX = 7


def _llm_result(score: int = 5) -> dict:
    return {
        "source": "llm_v2",
        "score": score,
        "score_max": SMAX,
        "percentage": round((score / SMAX) * 100),
        "highlights": [
            {"start": 4, "end": 8, "type": "good_element", "message_ar": "عنصر صحيح"},
        ],
        "matched_criteria": ["تقديم الوثيقة"],
        "unmatched_criteria": [],
        "feedback_ar": "إجابة متوسطة",
        "advice_ar": "حاول التوضيح",
        "confidence": 0.9,
        "parse_status": "ok",
        "sanity_code": "ok",
    }


def _make_evaluate_fn(return_result: dict | None = None):
    holder = {"result": return_result}
    mock = AsyncMock()

    async def _impl(**kwargs):
        return json.loads(json.dumps(holder["result"]))

    mock.side_effect = _impl
    mock.set_result = lambda r: holder.__setitem__("result", r)
    return mock


async def _call(evaluate_fn, answer: str = ANS, **overrides) -> dict:
    return await evaluate_with_cache(
        question_id=overrides.pop("question_id", QID),
        verb_slug=overrides.pop("verb_slug", VERB),
        score_max=overrides.pop("score_max", SMAX),
        student_answer=answer,
        model_id=overrides.pop("model_id", "gpt-4o-mini"),
        evaluate_fn=evaluate_fn,
        scenario_context="ctx",
        documents=None,
        question_prompt="حلل",
        question_skill="تحليل",
        model_answer="modèle",
        learning_focus=None,
        use_v2_prompt=True,
        **overrides,
    )


@pytest.fixture
async def real_redis():
    """Client VRAI Redis (connexion vérifiée) — patch state.redis, purge DB."""
    try:
        client = aioredis.from_url(REDIS_TEST_URL, decode_responses=True)
        await client.ping()
    except Exception as e:
        pytest.skip(f"Redis indisponible ({REDIS_TEST_URL}) : {e}")

    await client.flushdb()
    previous = state.redis
    state.redis = client
    try:
        yield client
    finally:
        state.redis = previous
        await client.flushdb()
        await client.aclose()


@pytest.fixture
async def empty_redis():
    """Vrai Redis SANS patcher state.redis (contrôle direct de la DB)."""
    try:
        client = aioredis.from_url(REDIS_TEST_URL, decode_responses=True)
        await client.ping()
    except Exception as e:
        pytest.skip(f"Redis indisponible ({REDIS_TEST_URL}) : {e}")
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()


@pytest.mark.asyncio
async def test_lua_release_script_parses_and_works(empty_redis):
    """Le script Lua de libération du verrou (réel, pas fake) est valide :
    ne supprime QUE si le token correspond (CAS)."""
    from grading.cache import _RELEASE_LUA

    # token présent → suppression
    await empty_redis.set("lock:1", "tokA", nx=True, ex=30)
    assert await empty_redis.exists("lock:1") == 1
    assert await empty_redis.eval(_RELEASE_LUA, 1, "lock:1", "tokA") == 1
    assert await empty_redis.exists("lock:1") == 0

    # token DIFFÉRENT → pas de suppression (verrou d'un autre worker)
    await empty_redis.set("lock:2", "tokA", nx=True, ex=30)
    assert await empty_redis.eval(_RELEASE_LUA, 1, "lock:2", "tokB") == 0
    assert await empty_redis.exists("lock:2") == 1


@pytest.mark.asyncio
async def test_single_flight_real_redis(real_redis):
    """Acceptation C2 #9 contre VRAI Redis : 10 corrections concurrentes
    identiques → 1 seul appel LLM (le verrou NX + Lua CAS réels)."""
    import asyncio

    evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5))

    results = await asyncio.gather(*[_call(evaluate_fn) for _ in range(10)])

    assert evaluate_fn.await_count == 1
    assert all(r["score"] == 5 for r in results)
    assert sum(1 for r in results if r.get("from_cache")) == 9
    assert sum(1 for r in results if not r.get("from_cache")) == 1


@pytest.mark.asyncio
async def test_payload_ttl_7_days_real(real_redis, empty_redis):
    """Le payload caché porte le TTL réel (7 jours) et ne contient jamais
    llm_raw ni la copie élève."""
    evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5))
    await _call(evaluate_fn)

    # La clé de cache existe avec TTL ~7 jours
    from grading.cache_key import build_correction_key

    canonical, _ = key_normalize(ANS)
    key = build_correction_key(
        question_id=QID, verb_slug=VERB, score_max=SMAX,
        answer=canonical, model_id="gpt-4o-mini", prompt_variant="v2",
    )
    ttl = await empty_redis.ttl(key)
    assert 6 * 86400 < ttl <= 7 * 86400, f"TTL réel inattendu : {ttl}s"

    payload = await empty_redis.get(key)
    assert payload is not None
    stored = json.loads(payload)
    assert "llm_raw" not in stored
    assert "student_answer" not in stored
    assert "student_answer_hash" not in stored
    assert "source" in stored  # source d'origine préservée (observabilité)


@pytest.mark.asyncio
async def test_key_isolation_real_redis(real_redis):
    """Deux réponses différentes → 2 clés distinctes (pas de collision)."""

    evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5))
    ans2 = "نستنتج أن البنكرياس يفرز الأنسولين الذي يخفض نسبة السكر"

    r1 = await _call(evaluate_fn, ANS)
    r2 = await _call(evaluate_fn, ans2, question_id=QID + 1)

    assert evaluate_fn.await_count == 2  # 2 misses (2 clés)
    assert r1.get("from_cache") is None and r2.get("from_cache") is None

    # re-soumission → 2 hits
    r1b = await _call(evaluate_fn, ANS)
    r2b = await _call(evaluate_fn, ans2, question_id=QID + 1)
    assert r1b["from_cache"] is True and r2b["from_cache"] is True
    assert evaluate_fn.await_count == 2  # aucun nouvel appel LLM


@pytest.mark.asyncio
async def test_lock_released_after_correction_real(real_redis):
    """Après une correction, le verrou single-flight est libéré (CAS réel)
    — la correction suivante (réponse différente) ne reste pas bloquée."""
    evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5))
    await _call(evaluate_fn, ANS)

    # aucun verrou résiduel dans la DB (le CAS Lua l'a supprimé)
    keys = [k async for k in real_redis.scan_iter("corr:lock:*")]
    assert keys == [], f"verrous résiduels : {keys}"


@pytest.mark.asyncio
async def test_is_cacheable_contract_unchanged():
    """Le contrat d'écriture (whitelist source + parse_status) est inchangé
    avec le vrai Redis — un résultat dégradé n'est toujours pas caché."""
    good = _llm_result(score=5)
    assert is_cacheable(good) is True
    bad = _llm_result(score=5)
    bad["source"] = "llm_error"
    assert is_cacheable(bad) is False
    bad2 = _llm_result(score=5)
    bad2["parse_status"] = "unparsable"
    assert is_cacheable(bad2) is False
