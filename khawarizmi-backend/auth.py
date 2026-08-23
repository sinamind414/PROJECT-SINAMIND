from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from config import get_settings

BCRYPT_MAX_PASSWORD_BYTES = 72


def _password_bytes(password: str) -> bytes:
    encoded = password.encode("utf-8")
    if len(encoded) > BCRYPT_MAX_PASSWORD_BYTES:
        raise ValueError("Mot de passe trop long pour bcrypt (72 octets maximum).")
    return encoded


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt(rounds=12)).decode("ascii")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_password_bytes(plain), hashed.encode("ascii"))
    except (ValueError, UnicodeError):
        return False


def create_access_token(data: dict) -> str:
    cfg = get_settings()
    payload = data.copy()
    expire = datetime.now(UTC) + timedelta(hours=cfg.JWT_EXPIRE_HOURS)
    payload.update({"exp": expire})
    return jwt.encode(payload, cfg.SECRET_KEY, algorithm=cfg.JWT_ALGORITHM)
