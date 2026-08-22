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
        # verify_sub=False : les tokens portent sub en INT (pattern aligné sur
        # deps.get_current_user — python-jose exigerait une chaîne sinon
        # JWTClaimsError et la clé rate-limit retombait sur l'IP : tous les
        # élèves derrière la même IP/NAT partageaient un seul compteur free,
        # et le tier pro (80/h) n'était jamais appliqué. Bug corrigé 2026-08-21,
        # tests : tests/test_rate_limit.py.)
        payload = jwt.decode(
            token, cfg.SECRET_KEY, algorithms=[cfg.JWT_ALGORITHM],
            options={"verify_sub": False},
        )
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
