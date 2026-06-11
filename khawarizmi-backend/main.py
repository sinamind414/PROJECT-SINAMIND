"""
main.py — API FastAPI Khawarizmi v1.0
Point d'entrée unique du backend.
Connecte : Engine IA + FSRS + Interleaving + Dual Coding + Auth + Cache

Lancement :
    uvicorn main:app --reload --port 8000
"""

# ═══════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════

import os
import json
import logging
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from pathlib import Path
from contextlib import asynccontextmanager
from functools import lru_cache
import asyncio

# FastAPI
from fastapi import (
    FastAPI, HTTPException, Depends,
    status, UploadFile, File, Request
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Pydantic
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

# Auth
from jose import JWTError, jwt
from passlib.context import CryptContext

# DB
from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker
)
from sqlalchemy import text

# Cache
import redis.asyncio as aioredis

# OpenAI
from openai import AsyncOpenAI

# FSRS
from fsrs import Card

# Services Khawarizmi
from services.khawarizmi_engine import KhawarizmiTutor
from services.scheduler         import KhawarizmiScheduler
from services.interleaving      import InterleavingSession
from services.dual_coding       import DualCodingService

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    # ── App ──────────────────────────────────────────────
    app_name:        str  = "Khawarizmi API"
    environment:     str  = "development"
    debug:           bool = False

    # ── Database ─────────────────────────────────────────
    database_url:    str  = ""

    # ── Redis ─────────────────────────────────────────────
    redis_url:       str  = ""
    cache_ttl:       int  = 3600          # 1 heure

    # ── Auth JWT ──────────────────────────────────────────
    secret_key:      str  = "changeme-use-strong-secret-in-production"
    algorithm:       str  = "HS256"
    token_expire_min:int  = 1440          # 24 heures

    # ── IA ────────────────────────────────────────────────
    openai_api_key:  str  = ""
    openai_base_url: str  = "https://api.openai.com/v1"
    openai_model:    str  = "gpt-4o-mini"
    ia_temperature:  float= 0.3
    ia_max_tokens:   int  = 600

    # ── Données BAC ───────────────────────────────────────
    data_dir:        str  = ""

    # ── Chargily Pay ──────────────────────────────────────
    chargily_secret_key: str = "test_sk_fake"

    # ── CORS ──────────────────────────────────────────────
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5500",
        "https://khawarizmi-ia.vercel.app",
        "https://ia-khawarizmi.dz",
    ]

    model_config = ConfigDict(extra='ignore', env_file='.env', env_file_encoding='utf-8')


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# ═══════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════

logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("khawarizmi.api")


# ═══════════════════════════════════════════════════════════════
# ÉTAT GLOBAL (initialisé au démarrage)
# ═══════════════════════════════════════════════════════════════

class AppState:
    tutor:       Optional[KhawarizmiTutor]      = None
    scheduler:   Optional[KhawarizmiScheduler]  = None
    interleaving:Optional[InterleavingSession]  = None
    dual_coding: Optional[DualCodingService]    = None
    openai:      Optional[AsyncOpenAI]          = None
    redis:       Optional[aioredis.Redis]        = None
    db_engine:   Any                             = None
    db_session:  Any                             = None
    reconciliation_task: Optional[asyncio.Task]  = None


state = AppState()


# ═══════════════════════════════════════════════════════════════
# LIFESPAN (démarrage + arrêt)
# ═══════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialise tous les services au démarrage.
    Libère les ressources à l'arrêt.
    """
    cfg = get_settings()
    logger.info(f"🚀 Démarrage Khawarizmi API [{cfg.environment}]")

    # ── Résolution data_dir ─────────────────────────────
    data_dir = cfg.data_dir
    if data_dir and not Path(data_dir).exists():
        logger.warning(f"⚠️ DATA_DIR configuré ({data_dir}) introuvable, tentative de fallback.")
        data_dir = ""

    if not data_dir:
        parent = Path(__file__).parent.parent.resolve()
        if (parent / "programme_maths_3as.json").exists():
            data_dir = str(parent)
        elif (Path(__file__).parent / "data").exists():
            data_dir = str(Path(__file__).parent / "data")
        else:
            data_dir = str(Path(__file__).parent / "data") # force to data

    logger.info(f"📚 Data dir : {data_dir}")

    # ── KhawarizmiTutor ─────────────────────────────────
    try:
        state.tutor = KhawarizmiTutor(data_dir=data_dir)
        logger.info("✅ KhawarizmiTutor chargé")
    except Exception as e:
        logger.error(f"❌ KhawarizmiTutor : {e}")
        raise RuntimeError(f"Corpus BAC introuvable : {e}")

    # ── Scheduler FSRS ──────────────────────────────────
    state.scheduler    = KhawarizmiScheduler()
    state.interleaving = InterleavingSession()
    logger.info("✅ Scheduler FSRS + Interleaving initialisés")

    # ── Client OpenAI ───────────────────────────────────
    if cfg.openai_api_key:
        state.openai = AsyncOpenAI(
            api_key  = cfg.openai_api_key,
            base_url = cfg.openai_base_url,
        )
        state.dual_coding = DualCodingService(state.openai)
        logger.info(f"✅ OpenAI client → {cfg.openai_model}")
    else:
        logger.warning("⚠️  OPENAI_API_KEY manquante — IA désactivée")

    # ── PostgreSQL ──────────────────────────────────────
    try:
        db_url = cfg.database_url
        if db_url:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif db_url.startswith("postgresql://"):
                db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        state.db_engine = create_async_engine(
            db_url,
            pool_size       = 10,
            max_overflow    = 20,
            pool_pre_ping   = True,
            echo            = cfg.debug,
        )
        state.db_session = async_sessionmaker(
            state.db_engine,
            class_       = AsyncSession,
            expire_on_commit = False,
        )

        # ── Auto-migration : exécute migrations/*.sql ──
        try:
            migrations_dir = Path(__file__).parent / "migrations"
            if migrations_dir.exists():
                sql_files = sorted(migrations_dir.glob("*.sql"))
                async with state.db_engine.begin() as conn:
                    for sql_file in sql_files:
                        sql_content = sql_file.read_text(encoding="utf-8")
                        # Split par ; pour exécuter chaque statement
                        statements = [
                            s.strip() for s in sql_content.split(";")
                            if s.strip() and not s.strip().startswith("--")
                        ]
                        for stmt in statements:
                            try:
                                await conn.execute(text(stmt))
                            except Exception as e:
                                logger.warning(
                                    f"Migration {sql_file.name} stmt skipped: {e}"
                                )
                logger.info(f"✅ Migrations appliquées : {len(sql_files)} fichiers")
        except Exception as e:
            logger.error(f"⚠️ Erreur migration : {e}")
        # Test de connexion
        async with state.db_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ PostgreSQL connecté")
    except Exception as e:
        logger.error(f"❌ PostgreSQL : {e}")
        logger.warning("⚠️  Démarrage sans base de données")

    # ── Redis ───────────────────────────────────────────
    try:
        state.redis = await aioredis.from_url(
            cfg.redis_url,
            encoding         = "utf-8",
            decode_responses = True,
        )
        await state.redis.ping()
        logger.info("✅ Redis connecté")
    except Exception as e:
        logger.warning(f"⚠️  Redis indisponible : {e} — Cache désactivé")
        state.redis = None

    logger.info("✅ Khawarizmi API prête")
    
    from services.reconciliation_queue import process_review_queue
    state.reconciliation_task = asyncio.create_task(process_review_queue())

    yield  # ← L'app tourne ici

    # ── Nettoyage ───────────────────────────────────────
    logger.info("🛑 Arrêt de l'API...")
    if state.reconciliation_task:
        state.reconciliation_task.cancel()
        try:
            await state.reconciliation_task
        except asyncio.CancelledError:
            pass
    if state.redis:
        await state.redis.aclose()
    if state.db_engine:
        await state.db_engine.dispose()
    logger.info("✅ Ressources libérées")


# ═══════════════════════════════════════════════════════════════
# APP FASTAPI
# ═══════════════════════════════════════════════════════════════

app = FastAPI(
    title       = "Khawarizmi API",
    description = "Backend IA pour le BAC algérien — Tuteur Socratique + FSRS",
    version     = "1.0.0",
    lifespan    = lifespan,
    docs_url    = "/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url   = None,
)

# ── CORS ────────────────────────────────────────────────────────
cfg_for_cors = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins     = cfg_for_cors.allowed_origins,
    allow_credentials = True,
    allow_methods     = ["GET", "POST", "PUT", "DELETE"],
    allow_headers     = ["*"],
)

# ── Trusted Hosts (production) ───────────────────────────────────
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts = ["ia-khawarizmi.dz", "*.ia-khawarizmi.dz"],
    )


# ═══════════════════════════════════════════════════════════════
# DÉPENDANCES
# ═══════════════════════════════════════════════════════════════

async def get_db() -> AsyncSession:
    """Injecte une session DB dans les routes."""
    if not state.db_session:
        raise HTTPException(503, "Base de données indisponible")
    async with state.db_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_tutor() -> KhawarizmiTutor:
    if not state.tutor:
        raise HTTPException(503, "Moteur pédagogique non initialisé")
    return state.tutor


def get_scheduler() -> KhawarizmiScheduler:
    if not state.scheduler:
        raise HTTPException(503, "Scheduler FSRS non initialisé")
    return state.scheduler


def get_openai() -> AsyncOpenAI:
    if not state.openai:
        raise HTTPException(503, "Service IA non configuré — clé API manquante")
    return state.openai


# ═══════════════════════════════════════════════════════════════
# AUTH — JWT + Bcrypt
# ═══════════════════════════════════════════════════════════════

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    cfg     = get_settings()
    payload = data.copy()
    expire  = datetime.now(timezone.utc) + timedelta(minutes=cfg.token_expire_min)
    payload.update({"exp": expire})
    return jwt.encode(payload, cfg.secret_key, algorithm=cfg.algorithm)


async def get_current_user(
    request: Request,
    db:      AsyncSession = Depends(get_db),
) -> Dict:
    """Vérifie le JWT et retourne l'utilisateur courant."""
    cfg         = get_settings()
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail      = "Token invalide ou expiré",
        headers     = {"WWW-Authenticate": "Bearer"},
    )

    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, cfg.secret_key, algorithms=[cfg.algorithm])
        user_id: int = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Récupérer l'utilisateur depuis la DB
    result = await db.execute(
        text("SELECT id, email, prenom, plan FROM users WHERE id = :id"),
        {"id": user_id}
    )
    user = result.fetchone()
    if not user:
        raise credentials_exception

    return {"id": user[0], "email": user[1], "prenom": user[2], "plan": user[3]}


# ═══════════════════════════════════════════════════════════════
# CACHE REDIS — Décorateur
# ═══════════════════════════════════════════════════════════════

async def get_cache(key: str) -> Optional[str]:
    if not state.redis:
        return None
    try:
        return await state.redis.get(key)
    except Exception:
        return None


async def set_cache(key: str, value: str, ttl: int = 3600):
    if not state.redis:
        return
    try:
        await state.redis.setex(key, ttl, value)
    except Exception:
        pass


def make_cache_key(*parts) -> str:
    """Génère une clé de cache déterministe."""
    raw = ":".join(str(p) for p in parts)
    return f"khawarizmi:{hashlib.md5(raw.encode()).hexdigest()}"


# ═══════════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════════

class RegisterRequest(BaseModel):
    email:    EmailStr
    password: str = Field(min_length=8, max_length=100)
    prenom:   str = Field(min_length=2, max_length=50)
    wilaya:   Optional[str] = None
    filiere:  str = Field(default="sciences")

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if v.isdigit():
            raise ValueError("Le mot de passe ne peut pas être que des chiffres")
        return v


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         Dict[str, Any]


class ChatRequest(BaseModel):
    sujet_id:    str  = Field(min_length=3, max_length=100)
    question_id: str  = Field(min_length=1, max_length=50)
    message:     str  = Field(min_length=5, max_length=5000)
    mode_force:  Optional[str] = None
    niveau_sm2:  int  = Field(default=0, ge=0, le=4)
    score_actuel:float = Field(default=0.0, ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    type_erreur:        str
    ce_qui_est_correct: str
    question_socratique:str
    indice_si_bloque:   Optional[str] = None
    feedback_bienveillant: str
    pre_analyse:        Optional[Dict] = None
    tokens_utilises:    Optional[int]  = None
    economie_tokens:    int = 0


class DrillRequest(BaseModel):
    matiere:      str = "sciences_naturelles"
    nb_questions: int = Field(default=12, ge=4, le=20)


class ScheduleRequest(BaseModel):
    micro_concept_id: str
    score_percent:    float = Field(ge=0.0, le=100.0)
    fsrs_state:       Optional[Dict] = None


class SchemaEvalRequest(BaseModel):
    schema_id:    str
    image_base64: str = Field(min_length=100)


class WaitlistRequest(BaseModel):
    name:      str = Field(min_length=2, max_length=50)
    email:     EmailStr
    wilaya:    Optional[str] = None
    lang:      str = "fr"
    source:    Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# ROUTES — SANTÉ
# ═══════════════════════════════════════════════════════════════

@app.get("/health", tags=["Système"])
async def health_check():
    """Vérifie l'état de tous les services."""
    db_ok    = False
    redis_ok = False
    ia_ok    = state.openai is not None

    if state.db_session:
        try:
            async with state.db_session() as db:
                await db.execute(text("SELECT 1"))
            db_ok = True
        except Exception:
            pass

    if state.redis:
        try:
            await state.redis.ping()
            redis_ok = True
        except Exception:
            pass

    nb_questions = 0
    if state.tutor:
        nb_questions = sum(len(v) for v in state.tutor._index_questions.values())

    return {
        "status":       "ok" if (db_ok and ia_ok) else "degraded",
        "services": {
            "database":  db_ok,
            "redis":     redis_ok,
            "ia":        ia_ok,
            "corpus":    state.tutor is not None,
        },
        "corpus": {
            "questions":     nb_questions,
            "micro_concepts":len(state.tutor._index_micro_concepts) if state.tutor else 0,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ═══════════════════════════════════════════════════════════════
# WAITLIST — Inscription des élèves intéressés
# ═══════════════════════════════════════════════════════════════

class WaitlistEntry(BaseModel):
    name:   str       = Field(..., min_length=2, max_length=50)
    email:  EmailStr
    wilaya: Optional[str] = Field(None, max_length=50)
    lang:   Optional[str] = Field("fr", max_length=5)
    source: Optional[str] = "landing_page"


@app.post("/api/waitlist", status_code=201)
async def add_to_waitlist(entry: WaitlistEntry):
    """Inscription à la liste d'attente Khawarizmi."""
    try:
        if not state.db_engine:
            logger.warning(f"📧 Waitlist (no DB) : {entry.email}")
            return {
                "status":  "queued",
                "message": "Inscription enregistrée (mode dégradé)",
                "email":   entry.email
            }

        async with state.db_session() as session:
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
                    "name":   entry.name,
                    "email":  entry.email,
                    "wilaya": entry.wilaya,
                    "lang":   entry.lang,
                    "source": entry.source,
                }
            )
            # 2. Auto-create user for beta
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
                    {
                        "email": entry.email,
                        "pwd": hashed_pwd,
                        "prenom": entry.name,
                        "wilaya": entry.wilaya
                    }
                )
                user_id = res_insert.fetchone()[0]
            else:
                user_id = user[0]
            
            await session.commit()

        # 3. Generate token
        token = create_access_token({"sub": user_id})

        logger.info(f"✅ Waitlist + AutoAuth : {entry.email} (user_id={user_id})")
        return {
            "status":  "success",
            "message": "Inscription réussie",
            "email":   entry.email,
            "access_token": token,
            "token_type": "bearer"
        }

    except Exception as e:
        logger.error(f"❌ Waitlist error : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de l'inscription"
        )


@app.get("/api/waitlist/count")
async def get_waitlist_count():
    """Compteur public d'inscrits."""
    if not state.db_engine:
        return {"count": 0}
    try:
        async with state.db_session() as session:
            result = await session.execute(
                text("SELECT COUNT(*) FROM waitlist")
            )
            return {"count": result.scalar() or 0}
    except Exception as e:
        logger.error(f"Waitlist count error: {e}")
        return {"count": 0}


# ═══════════════════════════════════════════════════════════════
# ROUTES — AUTHENTIFICATION
# ═══════════════════════════════════════════════════════════════

@app.post("/api/auth/register", response_model=AuthResponse, tags=["Auth"])
async def register(
    body: RegisterRequest,
    db:   AsyncSession = Depends(get_db),
):
    """Inscription d'un nouvel élève."""

    # Vérifier si l'email existe déjà
    result = await db.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": body.email}
    )
    if result.fetchone():
        raise HTTPException(400, "Cet email est déjà utilisé")

    # Créer l'utilisateur
    hashed = hash_password(body.password)
    result = await db.execute(
        text("""
            INSERT INTO users (email, password_hash, prenom, wilaya, filiere)
            VALUES (:email, :pwd, :prenom, :wilaya, :filiere)
            RETURNING id, email, prenom, plan
        """),
        {
            "email":   body.email,
            "pwd":     hashed,
            "prenom":  body.prenom,
            "wilaya":  body.wilaya,
            "filiere": body.filiere,
        }
    )
    user = result.fetchone()

    token = create_access_token({"sub": user[0]})
    logger.info(f"Nouvel élève inscrit : {body.email} (wilaya={body.wilaya})")

    return AuthResponse(
        access_token = token,
        user = {
            "id":     user[0],
            "email":  user[1],
            "prenom": user[2],
            "plan":   user[3],
        }
    )


@app.post("/api/auth/login", response_model=AuthResponse, tags=["Auth"])
async def login(
    body: LoginRequest,
    db:   AsyncSession = Depends(get_db),
):
    """Connexion d'un élève existant."""

    result = await db.execute(
        text("SELECT id, email, password_hash, prenom, plan FROM users WHERE email = :email"),
        {"email": body.email}
    )
    user = result.fetchone()

    if not user or not verify_password(body.password, user[2]):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "Email ou mot de passe incorrect",
        )

    # Mettre à jour last_active
    await db.execute(
        text("UPDATE users SET last_active = NOW() WHERE id = :id"),
        {"id": user[0]}
    )

    token = create_access_token({"sub": user[0]})

    return AuthResponse(
        access_token = token,
        user = {
            "id":     user[0],
            "email":  user[1],
            "prenom": user[3],
            "plan":   user[4],
        }
    )


@app.get("/api/auth/me", tags=["Auth"])
async def get_me(current_user: Dict = Depends(get_current_user)):
    """Retourne le profil de l'utilisateur connecté."""
    return current_user


# ═══════════════════════════════════════════════════════════════
# ROUTES — CHAT SOCRATIQUE (Core Feature)
# ═══════════════════════════════════════════════════════════════

@app.post("/api/chat", tags=["IA"])
async def chat_socratique(
    body:         ChatRequest,
    current_user: Dict        = Depends(get_current_user),
    tutor:        KhawarizmiTutor = Depends(get_tutor),
    openai_client:AsyncOpenAI = Depends(get_openai),
):
    """
    Route principale du tuteur socratique.
    Reçoit la réponse d'un élève → retourne un feedback JSON socratique.
    """
    cfg = get_settings()

    # ── Cache Redis ────────────────────────────────────────
    cache_key = make_cache_key(
        "chat", body.sujet_id, body.question_id,
        body.message[:100], body.mode_force or "auto"
    )
    cached = await get_cache(cache_key)
    if cached:
        logger.debug(f"Cache HIT : {cache_key[:20]}...")
        result = json.loads(cached)
        result["from_cache"] = True
        return result

    # ── Pré-analyse sans IA ────────────────────────────────
    pre_analyse = tutor.pre_analyser_sans_ia(
        body.sujet_id,
        body.question_id,
        body.message,
    )

    # ── Construction du prompt ─────────────────────────────
    try:
        system_prompt = tutor.build_system_prompt(
            sujet_id      = body.sujet_id,
            question_id   = body.question_id,
            student_input = body.message,
            pre_analyse   = pre_analyse,
            niveau_sm2    = body.niveau_sm2,
            score_actuel  = body.score_actuel,
            mode_force    = body.mode_force,
        )
    except ValueError as e:
        raise HTTPException(404, f"Contenu introuvable : {e}")

    # ── Appel IA ───────────────────────────────────────────
    try:
        response = await openai_client.chat.completions.create(
            model           = cfg.openai_model,
            messages        = [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": body.message},
            ],
            response_format = {"type": "json_object"},
            temperature     = cfg.ia_temperature,
            max_tokens      = cfg.ia_max_tokens,
            timeout         = 30.0,
        )

        raw_content  = response.choices[0].message.content
        tokens_used  = response.usage.total_tokens
        ia_result    = json.loads(raw_content)

    except json.JSONDecodeError:
        logger.error(f"Réponse IA non-JSON : {raw_content[:200]}")
        raise HTTPException(500, "Réponse IA malformée")
    except Exception as e:
        logger.error(f"Erreur OpenAI : {e}")
        raise HTTPException(502, f"Service IA temporairement indisponible : {e}")

    # ── Construire la réponse ──────────────────────────────
    result = {
        **ia_result,
        "pre_analyse":     pre_analyse,
        "tokens_utilises": tokens_used,
        "economie_tokens": pre_analyse.get("economie_tokens", 0) if pre_analyse else 0,
        "from_cache":      False,
    }

    # ── Sauvegarder en cache (TTL 1h) ─────────────────────
    await set_cache(cache_key, json.dumps(result, ensure_ascii=False), cfg.cache_ttl)

    logger.info(
        f"Chat : user={current_user['id']} "
        f"sujet={body.sujet_id} q={body.question_id} "
        f"tokens={tokens_used}"
    )

    return result


# ═══════════════════════════════════════════════════════════════
# ROUTES — DRILL (Spaced Repetition + Interleaving)
# ═══════════════════════════════════════════════════════════════

@app.post("/api/drill/session", tags=["Drill"])
async def generer_session_drill(
    body:         DrillRequest,
    current_user: Dict          = Depends(get_current_user),
    db:           AsyncSession  = Depends(get_db),
):
    """Génère une session Drill interleaving personnalisée pour l'élève."""

    session = await state.interleaving.generer_session(
        user_id      = current_user["id"],
        db           = db,
        matiere      = body.matiere,
        nb_questions = body.nb_questions,
    )

    # Vérifier le quota (plan Free : 5 questions/jour)
    if current_user["plan"] == "free":
        session["questions"] = session["questions"][:5]
        session["nb_questions"] = len(session["questions"])
        session["quota_atteint"] = len(session["questions"]) == 5

    logger.info(
        f"Drill : user={current_user['id']} "
        f"matiere={body.matiere} "
        f"questions={session['nb_questions']}"
    )

    return session


@app.post("/api/drill/result", tags=["Drill"])
async def soumettre_resultat_drill(
    body:         ScheduleRequest,
    current_user: Dict           = Depends(get_current_user),
    db:           AsyncSession   = Depends(get_db),
):
    """
    Soumet le résultat d'un exercice Drill.
    Met à jour l'état FSRS dans PostgreSQL.
    """
    scheduler = get_scheduler()

    # Charger ou créer la carte FSRS
    fsrs_state = body.fsrs_state or {}
    card = Card()

    # Calculer le prochain intervalle
    result = scheduler.calculer_prochain_intervalle(card, body.score_percent)
    new_card = result["card"]

    # Sérialiser l'état FSRS
    fsrs_json = json.dumps({
        "stability":     new_card.stability,
        "difficulty":    new_card.difficulty,
        "scheduled_days":new_card.scheduled_days,
        "reps":          new_card.reps,
        "lapses":        new_card.lapses,
        "state":         str(new_card.state),
        "last_review":   datetime.now(timezone.utc).isoformat(),
    })

    # Sauvegarder dans PostgreSQL (UPSERT)
    await db.execute(
        text("""
            INSERT INTO mastery_micro_concepts
                (user_id, micro_concept_id, prochaine_revision,
                 interval_jours, difficulty, stability, fsrs_state)
            VALUES
                (:user_id, :mc_id, :next_rev,
                 :interval, :difficulty, :stability, :fsrs_state::jsonb)
            ON CONFLICT (user_id, micro_concept_id)
            DO UPDATE SET
                prochaine_revision = EXCLUDED.prochaine_revision,
                interval_jours     = EXCLUDED.interval_jours,
                difficulty         = EXCLUDED.difficulty,
                stability          = EXCLUDED.stability,
                fsrs_state         = EXCLUDED.fsrs_state,
                updated_at         = NOW()
        """),
        {
            "user_id":    current_user["id"],
            "mc_id":      body.micro_concept_id,
            "next_rev":   result["prochaine_revision"],
            "interval":   result["interval_jours"],
            "difficulty": result["difficulty"],
            "stability":  result["stability"],
            "fsrs_state": fsrs_json,
        }
    )

    logger.info(
        f"FSRS update : user={current_user['id']} "
        f"mc={body.micro_concept_id} "
        f"score={body.score_percent}% "
        f"→ {result['interval_jours']}j"
    )

    return {
        "prochaine_revision": result["prochaine_revision"].isoformat(),
        "interval_jours":     result["interval_jours"],
        "retrievability":     result["retrievability"],
        "rating":             result["rating"],
    }


# ═══════════════════════════════════════════════════════════════
# ROUTES — PROGRESSION & PRÉDICTION BAC
# ═══════════════════════════════════════════════════════════════

@app.get("/api/progress", tags=["Progression"])
async def get_progression(
    current_user: Dict         = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    """
    Retourne la progression complète de l'élève
    avec prédiction de note BAC.
    """
    result = await db.execute(
        text("""
            SELECT
                mc.matiere,
                mc.chapitre_id,
                mmc.difficulty,
                mmc.stability,
                mmc.fsrs_state,
                mmc.prochaine_revision,
                mmc.interval_jours
            FROM mastery_micro_concepts mmc
            JOIN micro_concepts mc ON mc.id = mmc.micro_concept_id
            WHERE mmc.user_id = :user_id
            ORDER BY mc.matiere, mc.chapitre_id
        """),
        {"user_id": current_user["id"]}
    )
    rows = result.fetchall()

    if not rows:
        return {
            "message":   "Aucune progression enregistrée",
            "concepts":  [],
            "prediction_bac": None,
        }

    # Grouper par matière pour la prédiction BAC
    scheduler = get_scheduler()
    cards_par_matiere: Dict[str, List] = {}

    concepts = []
    for row in rows:
        matiere, chapitre_id, difficulty, stability, fsrs_state_json, next_rev, interval = row

        card = Card()
        card.stability  = stability  or 0.0
        card.difficulty = difficulty or 0.0

        cards_par_matiere.setdefault(matiere, []).append(card)
        retrievability = scheduler._get_retrievability(card)

        concepts.append({
            "matiere":          matiere,
            "chapitre_id":      chapitre_id,
            "stability":        round(stability or 0.0, 3),
            "difficulty":       round(difficulty or 0.0, 3),
            "retrievability":   retrievability,
            "prochaine_revision": next_rev.isoformat() if next_rev else None,
            "interval_jours":   interval,
            "est_due":          next_rev <= datetime.now(timezone.utc) if next_rev else True,
        })

    # Prédiction BAC pondérée
    prediction = scheduler.predire_score_bac(cards_par_matiere)

    # Stats drill du jour
    dues_auj = sum(1 for c in concepts if c["est_due"])

    return {
        "user_id":        current_user["id"],
        "nb_concepts":    len(concepts),
        "dues_aujourd_hui": dues_auj,
        "prediction_bac": prediction,
        "concepts":       concepts,
    }


# ═══════════════════════════════════════════════════════════════
# ROUTES — DUAL CODING (Évaluation de schémas)
# ═══════════════════════════════════════════════════════════════

@app.post("/api/schema/evaluer", tags=["Dual Coding"])
async def evaluer_schema(
    body:         SchemaEvalRequest,
    current_user: Dict             = Depends(get_current_user),
):
    """
    Évalue la photo d'un schéma manuscrit avec GPT-4o Vision.
    Feature Premium uniquement.
    """
    if current_user["plan"] == "free":
        raise HTTPException(
            status_code = 403,
            detail      = "L'évaluation de schémas est réservée au plan Premium."
        )

    if not state.dual_coding:
        raise HTTPException(503, "Service Vision IA non configuré")

    result = await state.dual_coding.evaluer_schema_photo(
        image_base64 = body.image_base64,
        schema_id    = body.schema_id,
    )

    logger.info(
        f"Schema eval : user={current_user['id']} "
        f"schema={body.schema_id}"
    )

    return result


@app.get("/api/schema/{schema_id}", tags=["Dual Coding"])
async def get_schema(
    schema_id:    str,
    current_user: Dict = Depends(get_current_user),
):
    """Retourne le schéma de référence pour affichage."""
    if not state.dual_coding:
        raise HTTPException(503, "Service Dual Coding non initialisé")

    schema = state.dual_coding.get_schema(schema_id)
    if not schema:
        raise HTTPException(404, f"Schéma '{schema_id}' introuvable")

    return {
        "id":          schema_id,
        "nom":         schema["nom"],
        "schema_ascii":schema["schema_ascii"],
        "instruction": state.dual_coding.get_instruction_eleve(schema_id),
    }


# ═══════════════════════════════════════════════════════════════



# ═══════════════════════════════════════════════════════════════
# ROUTES — CONTENU (Corpus BAC)
# ═══════════════════════════════════════════════════════════════

@app.get("/api/chapitres/{matiere}", tags=["Contenu"])
async def get_chapitres(
    matiere:      str,
    current_user: Dict = Depends(get_current_user),
    tutor:        KhawarizmiTutor = Depends(get_tutor),
):
    """Retourne les chapitres disponibles pour une matière."""

    programme = {
        "maths":    tutor.programme_maths,
        "physique": tutor.programme_physique,
        "sciences": tutor.programme_sciences,
    }.get(matiere)

    if not programme:
        raise HTTPException(404, f"Matière '{matiere}' introuvable")

    chapitres = programme.get("chapitres", [])

    return {
        "matiere":    matiere,
        "nb_chapitres": len(chapitres),
        "chapitres":  [
            {
                "id":   ch.get("id"),
                "nom":  ch.get("nom"),
                "nb_micro_concepts": len(ch.get("micro_concepts", [])),
            }
            for ch in chapitres
        ],
    }
@app.get("/health", tags=["System"])
async def health():
    return {"status": "healthy"}


# ═══════════════════════════════════════════════════════════════
# EVALUATE, SESSION & PAYMENT
# ═══════════════════════════════════════════════════════════════
from routes.evaluate import router as evaluate_router
from routes.session import router as session_router
from routes.payment import router as payment_router
app.include_router(evaluate_router)
app.include_router(session_router)
app.include_router(payment_router)

# ═══════════════════════════════════════════════════════════════
# GESTIONNAIRE D'ERREURS GLOBAL
# ═══════════════════════════════════════════════════════════════

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code = exc.status_code,
        content     = {
            "erreur":  exc.detail,
            "status":  exc.status_code,
            "path":    str(request.url.path),
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erreur non gérée : {exc}", exc_info=True)
    return JSONResponse(
        status_code = 500,
        content     = {
            "erreur": "Erreur serveur interne",
            "status": 500,
        }
    )
if __name__ == "__main__":
    import uvicorn
    import os
    
    # Récupérer le port dynamique fourni par Railway
    port = int(os.environ.get("PORT", 8000))
    
    # Lancer le serveur
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
