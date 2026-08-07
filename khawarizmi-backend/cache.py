import contextlib
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
    with contextlib.suppress(Exception):
        await s.redis.setex(key, ttl, value)


# Version du contrat de cache (audit O2) : bump à chaque changement de prompt
# ou de format qui rendrait les réponses cachées obsolètes.
CACHE_CONTRACT_VERSION = "v2"


def make_cache_key(*parts) -> str:
    raw = ":".join(str(p) for p in parts)
    return f"khawarizmi:{CACHE_CONTRACT_VERSION}:{hashlib.md5(raw.encode()).hexdigest()}"
