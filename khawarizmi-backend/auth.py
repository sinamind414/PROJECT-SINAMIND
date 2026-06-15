from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    cfg     = get_settings()
    payload = data.copy()
    expire  = datetime.now(timezone.utc) + timedelta(hours=cfg.JWT_EXPIRE_HOURS)
    payload.update({"exp": expire})
    return jwt.encode(payload, cfg.SECRET_KEY, algorithm=cfg.JWT_ALGORITHM)
