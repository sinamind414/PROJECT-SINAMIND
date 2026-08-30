from fastapi import Request
from jose import jwt
from slowapi import Limiter
from slowapi.util import get_remote_address


def _get_cfg():
    from main import get_settings

    return get_settings()


def _get_user_plan(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return None
    try:
        cfg = _get_cfg()
        payload = jwt.decode(token, cfg.SECRET_KEY, algorithms=[cfg.JWT_ALGORITHM])
        return payload.get("sub"), payload.get("plan", "free")
    except Exception:
        return None


def get_user_key(request: Request) -> str:
    info = _get_user_plan(request)
    if info is None:
        return get_remote_address(request)
    user_id, plan = info
    return f"user:{user_id}:{plan}"


def chat_limit(key: str) -> str:
    return "100/hour" if (key and ":pro" in key) else "20/hour"


def evaluate_limit(key: str) -> str:
    return "80/hour" if (key and ":pro" in key) else "15/hour"


def configure_limiter_storage(redis) -> None:
    """Branche le rate-limiter sur Redis quand il est disponible.

    Appelé au startup (lifespan) : si Redis est connecté, le stockage des
    compteurs passe de la mémoire (défaut) à Redis — les limites sont alors
    partagées entre toutes les instances. Sinon, on reste en mémoire.
    """
    if redis is None:
        return
    try:
        cfg = _get_cfg()
        if not cfg.REDIS_URL:
            return
        from limits.storage import RedisStorage

        limiter._limiter.storage = RedisStorage(cfg.REDIS_URL)
    except Exception:
        pass


limiter = Limiter(key_func=get_user_key)


def enforce_evaluate_quota(request) -> None:
    """S36 (audit 2026-08-30 F8) — application du quota de correction.

    15/h free, 80/h pro (evaluate_limit). Fail-open si limiter down.
    Partagé par /api/grade et /api/evaluate/methodology : même budget,
    même équité. La DÉCISION de compter reste dans services/grade_quota
    (module pur) — ici, seul l'I/O du limiter.
    """
    from fastapi import HTTPException

    key = get_user_key(request)
    limit_str = evaluate_limit(key)
    try:
        inner = getattr(limiter, "limiter", None)
        if inner is None:
            return
        from limits import parse

        item = parse(limit_str)
        allowed = inner.hit(item, key)
        if allowed is False:
            raise HTTPException(
                status_code=429,
                detail="تم بلوغ حد التصحيح. ليست علامة بكالوريا رسمية.",
            )
    except HTTPException:
        raise
    except Exception:
        return
