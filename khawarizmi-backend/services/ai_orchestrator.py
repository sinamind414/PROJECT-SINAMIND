import logging
import time

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from services.ai_modes.evaluation_mode import handle_evaluation
from services.ai_modes.free_mode import handle_free_chat
from services.ai_modes.guided_mode import handle_guided_chat
from schemas.ai_request import ChatOrchestratorRequest, EvaluateOrchestratorRequest

logger = logging.getLogger("khawarizmi.orchestrator")

_CHAT_MODES = {
    "guided": handle_guided_chat,
    "methodology": handle_guided_chat,
    "free": handle_free_chat,
    "quick": handle_free_chat,
}


class AIOrchestrator:
    async def handle_chat(
        self,
        body: ChatOrchestratorRequest,
        user: dict,
        db: AsyncSession,
        openai_client: AsyncOpenAI,
        cfg,
        tutor,
    ) -> dict:
        start = time.monotonic()
        handler = _CHAT_MODES.get(body.mode)
        if not handler:
            raise ValueError(f"Mode inconnu : {body.mode}")

        if body.mode == "methodology" and not body.mode_force:
            body = body.model_copy(update={"mode_force": "METHODOLOGY"})

        try:
            result = await handler(body, user, db, openai_client, cfg, tutor)
            duration_ms = int((time.monotonic() - start) * 1000)
            logger.info(
                f"AI_CHAT_OK | mode={body.mode} | user={user['id']} | "
                f"duration_ms={duration_ms} | tokens={result.get('tokens_used', 0)} | "
                f"cache={result.get('from_cache', False)} | "
                f"fallback={result.get('fallback_active', False)}"
            )
            return result
        except Exception as e:
            duration_ms = int((time.monotonic() - start) * 1000)
            logger.error(
                f"AI_CHAT_ERROR | mode={body.mode} | user={user['id']} | "
                f"duration_ms={duration_ms} | error={type(e).__name__}: {e}"
            )
            raise

    async def handle_evaluation(
        self,
        body: EvaluateOrchestratorRequest,
        user: dict,
        db: AsyncSession,
        openai_client,
    ) -> dict:
        start = time.monotonic()
        logger.info(f"orchestrator.handle_evaluation | q={body.question_id} user={user['id']}")
        try:
            result = await handle_evaluation(body, user, db, openai_client)
            duration_ms = int((time.monotonic() - start) * 1000)
            logger.info(
                f"AI_EVAL_OK | q={body.question_id} | user={user['id']} | "
                f"duration_ms={duration_ms} | score={result.get('score')} | "
                f"source={result.get('source')}"
            )
            return result
        except Exception as e:
            duration_ms = int((time.monotonic() - start) * 1000)
            logger.error(
                f"AI_EVAL_ERROR | q={body.question_id} | user={user['id']} | "
                f"duration_ms={duration_ms} | error={type(e).__name__}: {e}"
            )
            raise


_orchestrator: AIOrchestrator | None = None


def get_orchestrator() -> AIOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AIOrchestrator()
    return _orchestrator
