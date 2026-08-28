"""S12 — compteurs /api/grade. 0 copie, 0 user_id. Hors local_grader (P7)."""

from __future__ import annotations

from collections import defaultdict
from threading import Lock

_MAX_KEYS = 64
_lock = Lock()

_ungraded_by_qid: dict[str, int] = defaultdict(int)
_sanity: dict[str, int] = defaultdict(int)
_science: dict[str, int] = defaultdict(int)
_diagnosis: dict[str, int] = defaultdict(int)
_stuffing = 0
_graded = 0
_ungraded = 0
_latency_ms_sum = 0.0
_latency_n = 0
_latency_max_ms = 0.0
_cache_hits = 0
_cache_misses = 0


def reset() -> None:
    global _stuffing, _graded, _ungraded, _latency_ms_sum, _latency_n, _latency_max_ms
    global _cache_hits, _cache_misses
    with _lock:
        _ungraded_by_qid.clear()
        _sanity.clear()
        _science.clear()
        _diagnosis.clear()
        _stuffing = 0
        _graded = 0
        _ungraded = 0
        _latency_ms_sum = 0.0
        _latency_n = 0
        _latency_max_ms = 0.0
        _cache_hits = 0
        _cache_misses = 0


def _bump(store: dict[str, int], key: str) -> None:
    if key not in store and len(store) >= _MAX_KEYS:
        key = "_other"
    store[key] += 1


def record_ungraded(question_id: str, latency_ms: float = 0.0) -> None:
    """422 ungraded. question_id seulement — jamais la copie."""
    global _ungraded, _latency_ms_sum, _latency_n, _latency_max_ms
    qid = (question_id or "")[:200] or "_empty"
    with _lock:
        _ungraded += 1
        _bump(_ungraded_by_qid, qid)
        if latency_ms >= 0:
            _latency_ms_sum += latency_ms
            _latency_n += 1
            if latency_ms > _latency_max_ms:
                _latency_max_ms = latency_ms


def record_result(result, latency_ms: float = 0.0) -> None:
    """GradeResult sans copie. Hors grade() — appelé par la route."""
    global _graded, _stuffing, _latency_ms_sum, _latency_n, _latency_max_ms
    with _lock:
        _graded += 1
        _bump(_sanity, str(getattr(result, "sanity_code", "") or "unknown"))
        _bump(_science, str(getattr(result, "science_status", "") or "unknown"))
        diag = getattr(result, "diagnosis", None)
        code = getattr(diag, "code", None) if diag is not None else None
        _bump(_diagnosis, str(code or "none"))
        if getattr(result, "stuffing_suspected", False):
            _stuffing += 1
        if latency_ms >= 0:
            _latency_ms_sum += latency_ms
            _latency_n += 1
            if latency_ms > _latency_max_ms:
                _latency_max_ms = latency_ms


def record_cache(hit: bool) -> None:
    global _cache_hits, _cache_misses
    with _lock:
        if hit:
            _cache_hits += 1
        else:
            _cache_misses += 1


def _cache_redis_flag() -> bool:
    try:
        from services.grade_cache import redis_available

        return bool(redis_available())
    except Exception:
        return False


def snapshot() -> dict:
    """JSON ops. Pas de copie, pas d'identité élève."""
    redis_on = _cache_redis_flag()
    with _lock:
        total = _graded + _ungraded
        avg = round(_latency_ms_sum / _latency_n, 3) if _latency_n else 0.0
        return {
            "graded": _graded,
            "ungraded": _ungraded,
            "ungraded_by_question_id": dict(_ungraded_by_qid),
            "sanity": dict(_sanity),
            "science_status": dict(_science),
            "diagnosis": dict(_diagnosis),
            "stuffing_suspected": _stuffing,
            "cache_enabled": True,
            "cache_redis": redis_on,
            "cache_hits": _cache_hits,
            "cache_misses": _cache_misses,
            "latency_ms_avg": avg,
            "latency_ms_max": round(_latency_max_ms, 3),
            "calls": total,
            "banner_ar": "ملاحظة تدريبية — منهج + محتوى. ليست علامة بكالوريا رسمية.",
        }
