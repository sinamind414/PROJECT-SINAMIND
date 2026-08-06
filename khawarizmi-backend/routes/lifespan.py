"""routes/lifespan.py — Lifespan FastAPI (démarrage/arrêt propre).

L'état global (singletons) vit dans `app_state.state` (dataclass AppState).
Les DDL automatiques ont été supprimés : les migrations Alembic sont
responsables du schéma (voir `alembic upgrade head` dans le Dockerfile).
"""
from __future__ import annotations

import asyncio
import logging
import os
import pathlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis as AsyncRedis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app_state import state
from config import get_settings

logger = logging.getLogger("khawarizmi.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = get_settings()
    data_dir = cfg.data_dir or str(pathlib.Path(__file__).parent.parent / "data")

    # ── Moteur pédagogique (KhawarizmiTutor) ──────────────────────────
    try:
        from services.khawarizmi_engine import KhawarizmiTutor

        state.tutor = KhawarizmiTutor(data_dir=data_dir)
        logger.info("✅ KhawarizmiTutor initialisé")
    except Exception as e:
        logger.error(f"❌ KhawarizmiTutor init failed: {e} — tutor disabled")
        state.tutor = None

    # Rapport sur la fondation de données (canonical vs legacy)
    try:
        report = state.tutor.loader.get_data_foundation_report()
        logger.info("── DATA FOUNDATION ──")
        logger.info(f"  Programme source : {report['programme']['source']}")
        logger.info(f"  Micro-concepts   : {report['programme']['total_micro_concepts']}")
    except Exception as e:
        logger.error(f"Failed to report data foundation: {e}")

    # ── Scheduler FSRS ────────────────────────────────────────────────
    try:
        from services.scheduler import KhawarizmiScheduler

        state.scheduler = KhawarizmiScheduler()
        logger.info("✅ Scheduler FSRS initialisé")
    except Exception as e:
        logger.error(f"❌ Scheduler init failed: {e} — scheduler disabled")
        state.scheduler = None

    # ── Interleaving ──────────────────────────────────────────────────
    try:
        from services.interleaving import InterleavingSession

        state.interleaving = InterleavingSession()
    except Exception as e:
        logger.error(f"❌ Interleaving init failed: {e} — interleaving disabled")
        state.interleaving = None

    # ── Client IA : PAR DÉFAUT AUCUN appel LLM externe ne doit partir. ─
    # Double opt-in OBLIGATOIRE : ENABLE_EXTERNAL_LLM=1 + clé API.
    # Sinon on branche un GuardedOpenAIClient qui lève LLMDisabledError sur
    # tout appel → garantit 0 fuite réseau, même si un service oublie un guard.
    from services.llm_guard import (
        GuardedOpenAIClient,
        is_llm_enabled,
        llm_status,
    )

    if is_llm_enabled():
        try:
            from openai import AsyncOpenAI

            from services.dual_coding import DualCodingService

            api_key = cfg.OPENAI_API_KEY
            base_url = cfg.openai_base_url
            model = cfg.openai_model

            if api_key.startswith("gsk_"):
                base_url = "https://api.groq.com/openai/v1"
                if not model or model in ("gpt-4o-mini",) or "gpt" in model:
                    model = "llama-3.3-70b-versatile"
                logger.info(f"IA Provider auto-détecté: Groq ({model})")
            elif api_key.startswith("AIza"):
                base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
                if not model or "gpt" in model:
                    model = "gemini-2.5-flash"
                logger.info(f"IA Provider auto-détecté: Gemini ({model})")
            elif api_key.startswith("sk-or-v1"):
                base_url = "https://openrouter.ai/v1"
                if not model or "gpt" in model:
                    model = "google/gemini-2.5-flash"
                logger.info(f"IA Provider auto-détecté: OpenRouter ({model})")

            state.openai = AsyncOpenAI(api_key=api_key, base_url=base_url)
            state.dual_coding = DualCodingService(state.openai)
            state.ai_model = model
            logger.info(f"✅ IA EXTERNE activée: {base_url} | model={model}")
        except Exception as e:
            logger.error(f"❌ IA init failed: {e} — IA désactivée")
            state.openai = GuardedOpenAIClient()
            state.dual_coding = None
            state.ai_model = None
    else:
        state.openai = GuardedOpenAIClient()
        state.dual_coding = None
        state.ai_model = None
        status = llm_status()
        logger.info(
            "🛑 IA EXTERNE DÉSACTIVÉE (mode déterministe local) — "
            f"raison: opt-in={bool(cfg.OPENAI_API_KEY and os.environ.get('ENABLE_EXTERNAL_LLM'))}, "
            f"env={cfg.ENVIRONMENT}. Posez ENABLE_EXTERNAL_LLM=1 + une clé pour l'activer."
        )

    # ── SQLAlchemy async engine (PostgreSQL ou SQLite preview) ────────
    if cfg.DATABASE_URL:
        try:
            db_url = cfg.DATABASE_URL
            is_sqlite = db_url.startswith("sqlite://") or db_url.startswith("sqlite+aiosqlite://")
            if db_url.startswith("postgresql://") or db_url.startswith("postgres://"):
                db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1).replace(
                    "postgres://", "postgresql+asyncpg://", 1
                )
            elif is_sqlite and "+aiosqlite" not in db_url:
                db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

            state.db_engine = create_async_engine(
                db_url, pool_pre_ping=True,
                **({"pool_size": 10, "max_overflow": 20} if "asyncpg" in db_url else {}),
            )
            state.db_session = async_sessionmaker(
                state.db_engine, class_=AsyncSession, expire_on_commit=False
            )
            logger.info(f"✅ DB engine initialisé ({db_url.split('://')[0]})")

            # Auto-réparation SQLite : si une requête échoue "no such column/table",
            # on crée la colonne/table automatiquement.
            if is_sqlite:
                try:
                    from database import _install_sqlite_auto_alter
                    _install_sqlite_auto_alter(state.db_engine.sync_engine)
                except Exception as e:
                    logger.warning(f"Auto-ALTER non installé: {e}")

                # Définir NOW() comme fonction SQLite native (alias CURRENT_TIMESTAMP)
                # pour compatibilité avec le code écrit pour PostgreSQL.
                from sqlalchemy import event as _sa_event

                @_sa_event.listens_for(state.db_engine.sync_engine, "connect")
                def _sqlite_now_patch(dbapi_conn, rec):  # noqa: ARG001
                    try:
                        dbapi_conn.create_function("NOW", 0, lambda: None)
                        # NOW() en SQLite : utiliser strftime
                        import datetime as _dt
                        def _now():
                            return _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                        dbapi_conn.create_function("NOW", 0, _now)
                    except Exception:
                        pass

            # En mode preview SQLite, créer automatiquement TOUTES les
            # tables pour que le site fonctionne 100% localement, sans
            # migrations Alembic ni PostgreSQL/Redis.
            if is_sqlite:
                try:
                    from database import sqlite_preview_create_all

                    # Résoudre le chemin du fichier SQLite
                    db_path = cfg.DATABASE_URL
                    for prefix in ("sqlite+aiosqlite:///", "sqlite:///"):
                        if db_path.startswith(prefix):
                            db_path = db_path[len(prefix):]
                            break
                    if db_path.startswith("."):
                        db_path = str(
                            (pathlib.Path(__file__).parent.parent / db_path).resolve()
                        )

                    def _do_create(sync_conn):
                        return sqlite_preview_create_all(sync_conn, db_path)

                    async with state.db_engine.begin() as conn:
                        created = await conn.run_sync(_do_create)
                    logger.info(f"✅ Tables SQLite créées: {created} (preview local, 0 LLM, 0 FK)")
                except Exception as te:
                    logger.warning(f"Tables SQLite non créées (non bloquant): {te}", exc_info=True)
        except Exception as e:
            logger.error(f"DB init error: {e}")

    # ── Redis (cache + rate-limit) ────────────────────────────────────
    if cfg.REDIS_URL:
        try:
            state.redis = await AsyncRedis.from_url(
                cfg.REDIS_URL, encoding="utf-8", decode_responses=True
            )
            await state.redis.ping()
            logger.info("✅ Redis connecté")
        except Exception as e:
            logger.warning(f"Redis indisponible: {e}")
            state.redis = None

    # ── Rate limiter : Redis si dispo, sinon mémoire ─────────────────
    try:
        from rate_limit import configure_limiter_storage
        configure_limiter_storage(state.redis)
    except Exception as e:
        logger.warning(f"Rate-limiter config échouée: {e}")

    # ── Tâche de fond : réconciliation des réponses à revoir ─────────
    try:
        from services.reconciliation_queue import process_review_queue

        state.reconciliation_task = asyncio.create_task(process_review_queue())
        logger.info("✅ Reconciliation task démarrée (in-process)")
    except Exception as e:
        logger.error(f"❌ Reconciliation task init failed: {e}")

    # ── Golden Set ONEC (calibration évaluateur) ─────────────────────
    try:
        from services.eval_calibration import get_calibration_stats

        cal_stats = get_calibration_stats()
        if cal_stats["total_questions"] == 0:
            logger.error(
                "GOLDEN_SET_ABSENT | "
                "Évaluations sans calibration ONEC. "
                "Vérifier data/golden_set_onec.json"
            )
        else:
            logger.info(
                f"GOLDEN_SET_OK | "
                f"{cal_stats['total_questions']} exemples chargés | "
                f"chapitres={list(cal_stats['by_chapter'].keys())}"
            )
    except Exception as e:
        logger.warning(f"GOLDEN_SET_CHECK_FAILED | {e}")

    # ── Embedder : détecter le mode fallback ────────────────────────
    try:
        from services.embedder import get_embedder

        emb = get_embedder()
        state.embedder_fallback = bool(getattr(emb, "is_fallback", False))
        if state.embedder_fallback:
            logger.warning(
                "EMBEDDER_FALLBACK_ACTIVE | "
                "Le RAG sémantique utilise un encodage bag-of-ngrams déterministe "
                "(pas de vecteurs sémantiques). "
                "Le RAG mot-clé reste fonctionnel. Cause : %s",
                getattr(emb, "fallback_reason", "modèle ONNX indisponible"),
            )
        else:
            logger.info("✅ Embedder ONNX chargé (RAG sémantique opérationnel)")
    except Exception as e:
        state.embedder_fallback = True
        logger.warning(f"EMBEDDER_CHECK_FAILED | {e}")

    # ── Contenus statiques pédagogiques (lazy-load, réduction bundle) ─
    try:
        from routes.static_content import preload_static_cache

        preload_static_cache()
    except Exception as e:
        logger.warning(f"STATIC_CONTENT_PRELOAD_FAILED | {e}")

    logger.info(f"Khawarizmi API prête [{cfg.ENVIRONMENT}]")
    yield

    # ── Arrêt propre ──────────────────────────────────────────────────
    if state.reconciliation_task:
        state.reconciliation_task.cancel()
        try:
            await state.reconciliation_task
        except asyncio.CancelledError:
            pass
    if state.redis:
        try:
            close = getattr(state.redis, "aclose", None) or getattr(state.redis, "close", None)
            if close:
                result = close()
                if hasattr(result, "__await__"):
                    await result
        except Exception:
            pass
    if state.db_engine:
        await state.db_engine.dispose()
    logger.info("Khawarizmi API arrêtée")
