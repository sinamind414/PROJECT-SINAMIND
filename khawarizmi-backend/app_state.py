"""app_state.py — État global applicatif (singletons).

L'état global (singletons) vit dans `app_state.state` (dataclass AppState).
Créé à partir de la définition historique qui vivait dans routes/lifespan.py
avant le refactor (commit bdad539) ; le fichier n'avait pas été committé,
ce qui cassait `import main` (et donc tout le backend + les tests).
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from redis.asyncio import Redis as AsyncRedis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@dataclass
class AppState:
    tutor: Any | None = None
    scheduler: Any | None = None
    interleaving: Any | None = None
    dual_coding: Any | None = None
    openai: Any | None = None
    redis: AsyncRedis | None = None
    db_engine: Any | None = None
    db_session: async_sessionmaker[AsyncSession] | None = None
    reconciliation_task: asyncio.Task | None = None
    # Modèle IA réellement résolu (Groq llama / Gemini / gpt-4o-mini) ou None.
    # Health le lit au lieu du défaut statique cfg.AI_MODEL_PRIMARY (souvent faux).
    ai_model: str | None = None
    # Embedder ONNX : False = mode sémantique réel, True = fallback déterministe.
    embedder_fallback: bool = False


state = AppState()
