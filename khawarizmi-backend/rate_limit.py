from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from jose import jwt


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


def chat_limit(request: Request) -> str:
    info = _get_user_plan(request)
    if info is None:
        return "20/hour"
    _, plan = info
    return "100/hour" if plan == "pro" else "20/hour"


def evaluate_limit(request: Request) -> str:
    info = _get_user_plan(request)
    if info is None:
        return "15/hour"
    _, plan = info
    return "80/hour" if plan == "pro" else "15/hour"


limiter = Limiter(key_func=get_user_key)
