import time

from fastapi import Request
from fastapi.responses import JSONResponse
from jose import jwt
from slowapi import Limiter
from slowapi.util import get_remote_address


def _get_cfg():
    from main import get_settings

    return get_settings()


def _get_user_plan(request: Request):
    """(user_id, plan) du JWT. None si pas d'token lisible -> l'appel retombe sur l'IP.

    S39 (audit surfaces 2026-08-30, F14) — `verify_sub: False` est OBLIGATOIRE ici :
    les tokens de l'app portent `sub` en int (cf. deps.get_current_user) et
    python-jose rejette un sub non-string (`Subject must be a string.`). Sans cette
    option, TOUTS les élèves authentifiés retombaient silencieusement sur la clé IP —
    et uvicorn tourne sans `--proxy-headers` derrière le proxy (Railway) : le budget
    de correction (15/h) était donc PARTAGÉ entre tous les élèves du site, et le plan
    `pro` (80/h, chat 100/h) n'était jamais reconnu.
    """
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return None
    try:
        cfg = _get_cfg()
        payload = jwt.decode(
            token, cfg.SECRET_KEY, algorithms=[cfg.JWT_ALGORITHM], options={"verify_sub": False}
        )
        sub = payload.get("sub")
        if sub is None:
            return None
        return str(sub), payload.get("plan") or "free"
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


limiter = Limiter(
    key_func=get_user_key,
    # S38 (audit surfaces 2026-08-30) — une panne de storage des limites (Redis
    # indisponible) ne doit JAMAIS transformer une requête élève en 500 : on dégrade
    # vers les compteurs mémoire par instance, conformément au fail-open documenté.
    swallow_errors=True,
    in_memory_fallback_enabled=True,
)

QUOTA_MESSAGE_AR = "تم بلوغ حد التصحيح. ليست علامة بكالوريا رسمية."
QUOTA_BANNER_AR = (
    "تم بلوغ حد التصحيح — 15 تصحيحًا في الساعة. هذه علامة تدريبية، "
    "وليست علامة بكالوريا رسمية. أعد المحاولة بعد انتهاء الفترة."
)


def enforce_evaluate_quota(request) -> JSONResponse | None:
    """S36 (audit 2026-08-30 F8) / S38 — application du quota de correction.

    15/h free, 80/h pro (evaluate_limit). Fail-open si limiter down ou désactivé.
    Partagé par /api/grade et /api/evaluate/methodology : même budget, même
    équité. La DÉCISION de compter reste dans services/grade_quota (module pur).

    S38 — RETOURNE une `JSONResponse(429)` au lieu de lever `HTTPException(429)`.
    Un 429 « manuel » traversait `add_exception_handler(429, ...)` → le handler
    slowapi exige `request.state.view_rate_limit`, que seul le décorateur/middleware
    de limitation pose : sans lui (limiter.enabled=False, middleware court-circuité)
    l'élève en surquota recevait un 500. Réponse directe = aucune dépendance au
    handler, corps conforme au contrat `erreur`, `Retry-After` utile à l'UI.
    """
    key = get_user_key(request)
    limit_str = evaluate_limit(key)
    try:
        if not getattr(limiter, "enabled", True):
            return None
        inner = getattr(limiter, "limiter", None)
        if inner is None:
            return None
        from limits import parse

        item = parse(limit_str)
        if inner.hit(item, key) is not False:
            return None
        retry_after: int | None = None
        try:
            reset_in, _remaining = inner.get_window_stats(item, key)
            retry_after = max(1, int(reset_in - time.time()))
        except Exception:
            retry_after = None
        content = {
            "erreur": QUOTA_MESSAGE_AR,
            "code": "quota_exceeded",
            "status": 429,
            "question_id": None,
            "banner_ar": QUOTA_BANNER_AR,
        }
        headers = {}
        if retry_after is not None:
            content["retry_after_s"] = retry_after
            headers["Retry-After"] = str(retry_after)
        return JSONResponse(status_code=429, content=content, headers=headers)
    except Exception:
        return None
