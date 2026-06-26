import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from auth import create_access_token, hash_password, verify_password
from config import get_settings
from deps import get_current_user, get_db
from schemas.user import AuthResponse, LoginRequest, RegisterRequest, WaitlistRequest

logger = logging.getLogger("khawarizmi.api")
router = APIRouter()


AUTH_COOKIE_NAME = "khawarizmi_access_token"


def _cookie_secure() -> bool:
    return get_settings().ENVIRONMENT == "production"


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=_cookie_secure(),
        samesite="lax",
        max_age=get_settings().JWT_EXPIRE_HOURS * 3600,
        path="/",
    )


def _clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        httponly=True,
        secure=_cookie_secure(),
        samesite="lax",
        path="/",
    )


def _get_state():
    from main import state

    return state


@router.post("/api/waitlist", status_code=201)
async def add_to_waitlist(entry: WaitlistRequest, response: Response):
    s = _get_state()
    try:
        if not s.db_engine:
            logger.warning(f"📧 Waitlist (no DB) : {entry.email}")
            return {"status": "queued", "message": "Inscription enregistrée (mode dégradé)", "email": entry.email}

        async with s.db_session() as session:
            await session.execute(
                text("""
                    INSERT INTO waitlist
                        (name, email, wilaya, lang, source, created_at, updated_at)
                    VALUES
                        (:name, :email, :wilaya, :lang, :source, NOW(), NOW())
                    ON CONFLICT (email) DO UPDATE SET
                        updated_at = NOW(),
                        source     = EXCLUDED.source
                """),
                {
                    "name": entry.name,
                    "email": entry.email,
                    "wilaya": entry.wilaya,
                    "lang": entry.lang,
                    "source": entry.source,
                },
            )
            res_user = await session.execute(text("SELECT id FROM users WHERE email = :email"), {"email": entry.email})
            user = res_user.fetchone()
            if not user:
                random_pwd = secrets.token_urlsafe(16)
                hashed_pwd = hash_password(random_pwd)
                res_insert = await session.execute(
                    text("""
                        INSERT INTO users (email, password_hash, prenom, wilaya, filiere)
                        VALUES (:email, :pwd, :prenom, :wilaya, 'sciences')
                        RETURNING id
                    """),
                    {"email": entry.email, "pwd": hashed_pwd, "prenom": entry.name, "wilaya": entry.wilaya},
                )
                user_id = res_insert.fetchone()[0]
            else:
                user_id = user[0]

            await session.commit()

        token = create_access_token({"sub": user_id, "plan": "free"})
        _set_auth_cookie(response, token)

        logger.info(f"✅ Waitlist + AutoAuth : {entry.email} (user_id={user_id})")
        return {
            "status": "success",
            "message": "Inscription réussie",
            "email": entry.email,
        }

    except Exception as e:
        logger.error(f"❌ Waitlist error : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'inscription")


@router.get("/api/waitlist/count")
async def get_waitlist_count():
    s = _get_state()
    if not s.db_engine:
        return {"count": 0}
    try:
        async with s.db_session() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM waitlist"))
            return {"count": result.scalar() or 0}
    except Exception as e:
        logger.error(f"Waitlist count error: {e}")
        return {"count": 0}


@router.post("/api/auth/register", response_model=AuthResponse, tags=["Auth"])
async def register(
    body: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": body.email})
    if result.fetchone():
        raise HTTPException(400, "Cet email est déjà utilisé")

    hashed = hash_password(body.password)
    result = await db.execute(
        text("""
            INSERT INTO users (email, password_hash, prenom, wilaya, filiere)
            VALUES (:email, :pwd, :prenom, :wilaya, :filiere)
            RETURNING id, email, prenom, plan
        """),
        {
            "email": body.email,
            "pwd": hashed,
            "prenom": body.prenom,
            "wilaya": body.wilaya,
            "filiere": body.filiere,
        },
    )
    user = result.fetchone()

    token = create_access_token({"sub": user[0], "plan": user[3]})
    _set_auth_cookie(response, token)
    logger.info(f"Nouvel élève inscrit : {body.email} (wilaya={body.wilaya})")

    return AuthResponse(
        access_token=None,
        user={
            "id": user[0],
            "email": user[1],
            "prenom": user[2],
            "plan": user[3],
        },
    )


@router.post("/api/auth/login", response_model=AuthResponse, tags=["Auth"])
async def login(
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("SELECT id, email, password_hash, prenom, plan FROM users WHERE email = :email"), {"email": body.email}
    )
    user = result.fetchone()

    if not user or not verify_password(body.password, user[2]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )

    await db.execute(text("UPDATE users SET last_active = NOW() WHERE id = :id"), {"id": user[0]})

    token = create_access_token({"sub": user[0], "plan": user[4]})
    _set_auth_cookie(response, token)

    return AuthResponse(
        access_token=None,
        user={
            "id": user[0],
            "email": user[1],
            "prenom": user[3],
            "plan": user[4],
        },
    )


@router.post("/api/auth/logout", tags=["Auth"])
async def logout(response: Response):
    _clear_auth_cookie(response)
    return {"status": "success"}


@router.get("/api/auth/me", tags=["Auth"])
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
