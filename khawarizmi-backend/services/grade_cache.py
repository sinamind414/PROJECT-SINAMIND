"""S14/S16/S19/S23 — cache route /api/grade. Hors grade() (P7). Pas de user_id (équité).

Mémoire toujours (preview / tests). Redis SETEX 7 j si state.redis — jamais
dans local_grader. Copie jamais en clair. sha16 = ceinture si bump de version oublié.
filet_sha16 = ceinture si Savoir / $lex changent sans bump GRADER_VERSION (B2).
"""

from __future__ import annotations

import hashlib
import json
import time
from functools import lru_cache
from threading import Lock

from schemas.rubric import GradeResult
from services.local_grader import GRADER_VERSION

TTL_SEC = 7 * 24 * 3600
_MAX_MEM = 256
_lock = Lock()
_mem: dict[str, tuple[float, dict]] = {}

_AUTO = object()
_bound_redis = _AUTO  # _AUTO → state.redis ; None → forcer mémoire ; client → tests


def bind_redis(client) -> None:
    """Tests / opt-in. None = mémoire seule. Ne pas appeler depuis grade()."""
    global _bound_redis
    _bound_redis = client


def redis_available() -> bool:
    return _redis_client() is not None


def reset() -> None:
    global _bound_redis, _sha_fallback_warned
    with _lock:
        _mem.clear()
    _bound_redis = _AUTO
    _sha_fallback_warned = False
    filet_sha16.cache_clear()


def _redis_client():
    if _bound_redis is not _AUTO:
        return _bound_redis
    try:
        from app_state import state

        return getattr(state, "redis", None)
    except Exception:
        return None


_sha_fallback_warned = False


def _digest(answer: str) -> str:
    """HMAC(pepper) si possible. Fallback SHA-256 sec : bruyant UNE fois (S35).

    Un pepper absent ne doit pas se taire — le SHA-256 brut est
    dictionnalisable sur des copies arabes courtes (audit P0-4.2).
    """
    global _sha_fallback_warned
    stripped = answer.lstrip().rstrip()
    try:
        from services.hashing import hash_answer

        h = hash_answer(stripped)
        if h:
            return h
    except Exception:
        if not _sha_fallback_warned:
            import logging

            logging.getLogger(__name__).warning(
                "hash_answer indisponible (SECRET_KEY absent ?) — digest cache "
                "en SHA-256 NON pepperé (dictionnalisable). Définir SECRET_KEY."
            )
            _sha_fallback_warned = True
    return hashlib.sha256(stripped.encode("utf-8")).hexdigest()


@lru_cache(maxsize=1)
def filet_sha16() -> str:
    """Empreinte filet science + $lex. Hors grade(). 0 copie, 0 user_id.

    `_SYNONYMS` / `_GRAVE_ERRORS` / lexique fichier ne sont pas dans
    `canon_sha16(Rubric)`. Sans ça, éditer Savoir sans bump moteur sert
    un GradeResult périmé (B2).
    """
    from services.lexicon import _load_file
    from services.savoir_corrector import (
        _CTX_ARNR,
        _CTX_ARNT,
        _EXP_10_4,
        _EXP_10_6,
        _GRAVE_ERRORS,
        _NUMERIC_RULES,
        _SYNONYMS,
    )

    blob = json.dumps(
        {
            "errata": [_EXP_10_6, _EXP_10_4, _CTX_ARNR, _CTX_ARNT],
            "grave": [[pat, msg] for pat, msg, *_ in _GRAVE_ERRORS],
            "lex": _load_file(),
            "numeric": _NUMERIC_RULES,
            "syn": _SYNONYMS,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def canon_sha16(packed) -> str:
    """sha16 JSON canonique Rubric+Document. 0 copie élève, 0 user_id.

    `model_answer` exclu : il ne change pas `grade(copy)`.
    criteria / theme / keypoints / advice inclus (ils changent le GradeResult).
    """
    r = packed.rubric.model_dump(mode="json")
    r.pop("model_answer", None)
    d = packed.document.model_dump(mode="json") if packed.document is not None else None
    blob = json.dumps(
        {"r": r, "d": d},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def make_key(packed, answer: str) -> str:
    """C1 + sha16 + filet_sha16. 0 user_id."""
    r = packed.rubric
    d = packed.document
    doc_id = d.doc_id if d is not None else "none"
    doc_ver = d.version if d is not None else "none"
    return (
        f"grade:{GRADER_VERSION}:{r.rubric_id}:{r.version}:"
        f"{doc_id}:{doc_ver}:{r.verb_slug}:{canon_sha16(packed)}:"
        f"{filet_sha16()}:{_digest(answer)}"
    )


def _sanitize_payload(data: dict) -> dict:
    out = dict(data)
    out.pop("student_answer", None)
    out.pop("model_answer", None)
    out.pop("user_id", None)
    out.pop("answer", None)
    return out


def _to_payload(result: GradeResult) -> dict:
    payload = _sanitize_payload(result.model_dump())
    payload["from_cache"] = False
    return payload


def _from_payload(data: dict, *, from_cache: bool) -> GradeResult | None:
    data = _sanitize_payload(data)
    data["from_cache"] = from_cache
    try:
        return GradeResult.model_validate(data)
    except Exception:
        return None


def cache_get(key: str) -> GradeResult | None:
    now = time.time()
    with _lock:
        hit = _mem.get(key)
        if hit is None:
            return None
        exp, payload = hit
        if exp < now:
            _mem.pop(key, None)
            return None
        data = dict(payload)
    return _from_payload(data, from_cache=True)


def cache_set(key: str, result: GradeResult) -> None:
    if not result.cacheable:
        return
    payload = _to_payload(result)
    exp = time.time() + TTL_SEC
    with _lock:
        if len(_mem) >= _MAX_MEM and key not in _mem:
            oldest = min(_mem, key=lambda k: _mem[k][0])
            _mem.pop(oldest, None)
        _mem[key] = (exp, payload)


async def cache_get_async(key: str) -> GradeResult | None:
    """Mémoire d'abord, Redis ensuite. 0 I/O dans grade()."""
    hit = cache_get(key)
    if hit is not None:
        return hit
    client = _redis_client()
    if client is None:
        return None
    try:
        raw = await client.get(key)
    except Exception:
        return None
    if not raw:
        return None
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    try:
        data = json.loads(raw)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    parsed = _from_payload(data, from_cache=True)
    if parsed is None or not parsed.cacheable:
        return None
    cache_set(key, parsed)
    parsed.from_cache = True
    return parsed


async def cache_set_async(key: str, result: GradeResult) -> None:
    cache_set(key, result)
    if not result.cacheable:
        return
    client = _redis_client()
    if client is None:
        return
    try:
        blob = json.dumps(_to_payload(result), ensure_ascii=False)
    except Exception:
        return
    try:
        await client.setex(key, TTL_SEC, blob)
    except Exception:
        return


def key_has_user_id(key: str) -> bool:
    return "user_id" in key or ":uid:" in key
