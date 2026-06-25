"""Route Tuteur Contextuel — POST /api/tuteur.

Chatbot contextuel qui :
- Pousse l'orientation au démarrage (__init__)
- Classifie l'intention localement (0 IA)
- Utilise Gemini pour les réponses socratiques
- Appelle le cerveau orientation en interne
- Retourne des cartes cliquables pour rediriger l'élève
"""

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user, get_openai
from rate_limit import chat_limit, limiter
from schemas.chat import TuteurRequest, TuteurResponse
from services.chat_service import handle_tuteur

logger = logging.getLogger("khawarizmi.api")
router = APIRouter()


@router.post("/api/tuteur", response_model=TuteurResponse, tags=["IA"])
@limiter.limit(chat_limit)
async def tuteur_contextuel(
    request: Request,
    body: TuteurRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    openai_client=Depends(get_openai),
):
    """Tuteur contextuel — chatbot SVT avec contexte FSRS + orientation.

    Pipeline :
    1. Classification locale (0ms)
    2. RAG si concept (50ms)
    3. Orientation si motivation/init (interne)
    4. Gemini 2.5 Flash (1 call, 3-8s)
    5. Fallback 3 niveaux
    """
    context_dict = {
        "chapitre": body.context.chapitre,
        "page_source": body.context.page_source,
        "fsrs_stability": body.context.fsrs_stability,
        "fsrs_due": body.context.fsrs_due,
        "last_score": body.context.last_score,
        "orientation_chapitre": body.context.orientation_chapitre,
        "history": [{"role": m.role, "content": m.content} for m in body.context.history],
    }

    result = await handle_tuteur(
        message=body.message,
        context=context_dict,
        user_id=current_user["id"],
        db=db,
        openai_client=openai_client,
    )

    logger.info(f"Tuteur : user={current_user['id']} type={result['type']} fallback={result['fallback_active']}")

    return TuteurResponse(**result)
