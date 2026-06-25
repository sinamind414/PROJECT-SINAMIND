import hashlib


def _get_state():
    from main import state

    return state


async def get_cache(key: str) -> str | None:
    s = _get_state()
    if not s.redis:
        return None
    try:
        return await s.redis.get(key)
    except Exception:
        return None


async def set_cache(key: str, value: str, ttl: int = 3600):
    s = _get_state()
    if not s.redis:
        return
    try:
        await s.redis.setex(key, ttl, value)
    except Exception:
        pass


def make_cache_key(*parts) -> str:
    raw = ":".join(str(p) for p in parts)
    return f"khawarizmi:{hashlib.md5(raw.encode()).hexdigest()}"
