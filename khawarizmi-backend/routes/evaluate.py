import json
import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import bindparam, text
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db, get_openai
from methodology.evaluator import evaluate_methodology
from rate_limit import evaluate_limit, limiter
from services.evaluation_utils import normalize_result
from services.fallback_v2 import evaluate_l2
from services.llm import call_gpt4o_evaluator


def _safe_json_fallback() -> dict:
    return {
        "score": 0,
        "statut": "ERREUR",
        "feedback": "L'algorithme de Khawarizmi est en cours de mise à jour. Réessaie dans quelques secondes.",
        "manquant": [],
    }


logger = logging.getLogger("khawarizmi.evaluate")
router = APIRouter()

from services.questions import get_question

# ═══════════════════════════════
# SCHÉMAS
# ═══════════════════════════════


class EvaluateRequest(BaseModel):
    question_id: str
    reponse_eleve: str
    tentative: int = 1
    lang: str = "fr"
    include_methodology: bool = True


class MethodologyResponse(BaseModel):
    note_methodologie: int = 0
    note_max: int = 10
    verb_identifie: str | None = None
    type_tache: str = "unknown"
    points_forts: list[str] = []
    points_faibles: list[str] = []
    feedback_principal: str = ""
    recommandation: str = ""



class EvaluateResponse(BaseModel):
    score: int
    statut: str
    feedback: str
    manquant: list[str]
    next_review_date: str | None = None
    source: str
    methodology: MethodologyResponse | None = None



# ═══════════════════════════════
# ENDPOINT PRINCIPAL
# ═══════════════════════════════


@router.post("/api/evaluate", response_model=EvaluateResponse)
@limiter.limit(evaluate_limit)
async def evaluate(
    request: Request,
    req: EvaluateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    openai_client=Depends(get_openai),
):
    user_id = current_user["id"]

    # 1. Charger la question
    question = get_question(req.question_id)
    if not question:
        raise HTTPException(status_code=404, detail=f"Question {req.question_id} introuvable")

    # 2. Tentative d'évaluation (avec fallbacks)
    eval_result = await evaluate_with_fallback(question, req, openai_client, user_id, db)

    # 3. Mise à jour FSRS par Graphe de Concepts
    # ( extrait vers services/evaluation_fsrs.py — partagé avec le drill, Phase 2 )
    from services.evaluation_fsrs import apply_evaluation_to_fsrs

    next_review_date = await apply_evaluation_to_fsrs(
        db=db,
        user_id=user_id,
        question_id=req.question_id,
        reponse_eleve=req.reponse_eleve,
        question=question,
        eval_result=eval_result,
    )

    # Normaliser la cohérence score/statut/manquant
    eval_result = normalize_result(eval_result)

    # Traduire le feedback si la langue est arabe
    if req.lang == "ar":
        from services.feedback_translator import translate_feedback

        eval_result["feedback"] = translate_feedback(eval_result.get("feedback", ""))

    # Évaluation méthodologique
    methodology_result = None
    if req.include_methodology:
        try:
            question_texte = question.get("texte", "") or question.get("texte_ar", "")
            methodo = await evaluate_methodology(
                instruction=question_texte,
                student_answer=req.reponse_eleve,
            )
            fb = methodo.get("feedback", {})
            methodology_result = MethodologyResponse(
                note_methodologie=methodo.get("score", 0),
                note_max=methodo.get("max_score", 10),
                verb_identifie=methodo.get("verb", None),
                type_tache=methodo.get("task_type", "unknown"),
                points_forts=fb.get("strengths", []),
                points_faibles=fb.get("weaknesses", []),
                feedback_principal=fb.get("message", ""),
                recommandation=fb.get("recommendation", ""),
            )
        except Exception as e:
            logger.warning(f"Methodology eval skipped: {e}")

    return EvaluateResponse(
        score=eval_result["score"],
        statut=eval_result["statut"],
        feedback=eval_result["feedback"],
        manquant=eval_result["manquant"],
        next_review_date=next_review_date,
        source=eval_result["source"],
        methodology=methodology_result,
    )


# ═══════════════════════════════
# LOGIQUE DE FALLBACK
# ═══════════════════════════════


async def evaluate_with_fallback(
    question: dict, req: EvaluateRequest, openai_client, user_id: str, db: AsyncSession
) -> dict:

    # NIVEAU 0 — Common Mistakes (gratuit, instantané, pas de LLM)
    try:
        from services.fallback_v2 import check_common_mistakes

        chapter_id = question.get("chapitre_id", question.get("chapitre", "ch1_proteines"))
        instant = await check_common_mistakes(req.reponse_eleve, chapter_id, db)
        if instant:
            instant["source"] = "COMMON_MISTAKES"
            logger.info(f"COMMON_MISTAKE | user={user_id} | q={req.question_id} | type={instant.get('error_type')}")
            return instant
    except Exception as e:
        logger.warning(f"COMMON_MISTAKES_SKIP | user={user_id} | reason={e!s}")

    # NIVEAU 1 — GPT-4o avec retry
    try:
        result = await call_gpt4o_evaluator(
            client=openai_client, question=question, reponse=req.reponse_eleve, tentative=req.tentative
        )
        result["source"] = "GPT4O"
        return result

    except Exception as e:
        logger.warning(f"FALLBACK_L2 | user={user_id} | q={req.question_id} | reason={e!s}")

    # NIVEAU 2 — Pattern matching local composite
    try:
        res_l2 = await evaluate_l2(reponse_eleve=req.reponse_eleve, question_data=question, db=db)

        # Déterminer les scores individuels par concept pour FSRS
        scores_concepts = {}
        concepts_requis = question.get("concepts_requis", [])
        if not concepts_requis and question.get("concept_cle"):
            concepts_requis = [question["concept_cle"]]

        for c_id in concepts_requis:
            if c_id in res_l2.concepts_trouves:
                scores_concepts[c_id] = 1.0
            else:
                scores_concepts[c_id] = 0.0

        if question.get("concept_cle") and question["concept_cle"] not in scores_concepts:
            scores_concepts[question["concept_cle"]] = res_l2.score_final

        return {
            "score": round(res_l2.score_final * 10),
            "statut": res_l2.verdict.upper(),
            "feedback": res_l2.feedback_fallback,
            "manquant": res_l2.concepts_manquants,
            "concepts_trouves": res_l2.concepts_trouves,
            "scores_concepts": scores_concepts,
            "needs_l1_review": res_l2.needs_l1_review,
            "source": "FALLBACK_L2",
        }

    except Exception as e:
        logger.error(f"FALLBACK_L3 | user={user_id} | q={req.question_id} | reason={e!s}")

    # NIVEAU 3 — JSON de sécurité absolu
    result = _safe_json_fallback()
    result["source"] = "FALLBACK_L3"
    return result
