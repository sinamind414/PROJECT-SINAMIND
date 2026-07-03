"""
routes/document_analysis_v2.py

Route v2 du correcteur : appelle evaluate_answer_v2 (voie B — hybride LLM + sanity).
Coexiste avec routes/document_analysis.py qui reste inchangée.

Route montée : POST /api/document-analysis/evaluate-v2
"""

from __future__ import annotations

import json
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from openai import AsyncOpenAI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from deps import get_current_user, get_db, get_openai
from rate_limit import evaluate_limit, limiter
from schemas.document_analysis import EvaluateRequest
from services.correction_audit import log_correction_audit
from services.correction_v2_retry import evaluate_answer_v2_with_retry
from services.llm import _call_with_fallback
from services.rag_service import format_rag_context, rag_search
from services.socratic_tutor import get_socratic_hint

logger = logging.getLogger("khawarizmi.document_analysis_v2")
router = APIRouter(prefix="/api/document-analysis", tags=["Document Analysis V2"])


async def _make_rag_provider(db: AsyncSession):
    """Fabrique un provider RAG filtré par verbe du LIVRE MANHADJIYA.

    Si aucun chunk trouvé (ingestion pas encore faite / verbe non couvert),
    retourne "" — le correcteur dégrade proprement vers la méthodo hardcode.
    """
    async def _provider(*, verb_slug: str, question_prompt: str, student_answer: str) -> str:
        query = f"{verb_slug} {question_prompt[:200]}"
        try:
            chunks = await rag_search(db, message=query, chapter=verb_slug)
        except Exception:
            return ""
        return format_rag_context(chunks[:3])

    return _provider


@router.post("/evaluate-v2")
@limiter.limit(evaluate_limit)
async def evaluer_reponses_v2(
    request: Request,
    body: EvaluateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    openai_client: AsyncOpenAI = Depends(get_openai),
):
    """Nouvelle évaluation « comme un prof » : sanity → LLM → validation."""
    cfg = get_settings()

    # 1. Charger le scénario
    scenario = await db.execute(
        text("""
            SELECT id, context_ar
            FROM da_scenarios
            WHERE slug = :slug
        """),
        {"slug": body.scenario_id},
    )
    scenario_row = scenario.fetchone()
    if not scenario_row:
        raise HTTPException(404, f"Scénario introuvable : {body.scenario_id}")
    scenario_id = scenario_row._mapping["id"]
    scenario_context = scenario_row._mapping["context_ar"]

    # 2. Charger TOUS les documents du scénario (l'élève les a tous vus)
    docs_result = await db.execute(
        text("""
            SELECT title_ar, caption_ar, data, sort_order
            FROM da_documents
            WHERE scenario_id = :scenario_id
            ORDER BY sort_order
        """),
        {"scenario_id": scenario_id},
    )
    documents = [
        {
            "title": row._mapping["title_ar"],
            "caption": row._mapping["caption_ar"],
            "data": row._mapping["data"],
        }
        for row in docs_result.fetchall()
    ]

    # 3. Créer la session d'évaluation (comme routes/document_analysis.py)
    session_result = await db.execute(
        text("""
            INSERT INTO da_sessions
                (user_id, scenario_id, chapter_slug, score_global, nb_questions)
            VALUES (:user_id, :scenario_id, :chapter_slug, 0, :nb)
            RETURNING id
        """),
        {
            "user_id": current_user["id"],
            "scenario_id": scenario_id,
            "chapter_slug": body.chapter_slug,
            "nb": len(body.answers),
        },
    )
    session_id = session_result.fetchone()._mapping["id"]

    evaluations = []
    total_score = 0
    total_max = 0

    rag_provider = await _make_rag_provider(db)

    for ans in body.answers:
        # 4. Charger la question ciblée
        if ans.question_id:
            q_result = await db.execute(
                text("""
                    SELECT id, verb_slug, prompt_ar, skill_ar,
                           model_answer_ar, learning_focus_ar
                    FROM da_questions WHERE id = :qid
                """),
                {"qid": ans.question_id},
            )
        else:
            q_result = await db.execute(
                text("""
                    SELECT q.id, q.verb_slug, q.prompt_ar, q.skill_ar,
                           q.model_answer_ar, q.learning_focus_ar
                    FROM da_questions q
                    JOIN da_scenarios s ON q.scenario_id = s.id
                    WHERE s.slug = :scenario_slug AND q.verb_slug = :verb_slug
                """),
                {"scenario_slug": body.scenario_id, "verb_slug": ans.verb_slug},
            )
        q_row = q_result.fetchone()
        if not q_row:
            continue

        q = q_row._mapping

        # 5. Score_max : reprendre les totaux de VERB_RULES existants
        score_max = _compute_score_max_for_verb(q["verb_slug"])

        # 6. SWITCH : Mode Socratique (indice) vs Mode Évaluation (note)
        if body.request_hint:
            hint = await get_socratic_hint(
                scenario_context=scenario_context,
                documents=documents,
                question_prompt=q["prompt_ar"],
                question_skill=q["skill_ar"],
                verb_slug=q["verb_slug"],
                model_answer=q["model_answer_ar"],
                learning_focus=q["learning_focus_ar"],
                student_answer=ans.answer,
            )
            # Pas de note, pas de persistance, pas de FSRS
            evaluations.append({
                "question_id": str(q["id"]),
                "verb_slug": q["verb_slug"],
                "score": 0,
                "score_max": score_max,
                "percentage": 0,
                "highlights": [],
                "matched_criteria": [],
                "unmatched_criteria": [],
                "feedback_ar": hint["hint_ar"],
                "advice_ar": hint["hint_ar"],
                "source": "socratic",
                "missing": [],
                "dominant_error_code": "socratic_hint",
                "success": [],
                "errors": [],
                "remediation": {"hint": hint},
            })
            continue

        # 6b. Mode Évaluation : appel du correcteur v2 avec retry
        result = await evaluate_answer_v2_with_retry(
            scenario_context=scenario_context,
            documents=documents,
            question_prompt=q["prompt_ar"],
            question_skill=q["skill_ar"],
            verb_slug=q["verb_slug"],
            model_answer=q["model_answer_ar"],
            learning_focus=q["learning_focus_ar"],
            score_max=score_max,
            student_answer=ans.answer,
            llm_call=_call_with_fallback,
            primary_client=openai_client,
            primary_model=cfg.openai_model,
            rag_context_provider=rag_provider,
            request_id=str(uuid.uuid4()),
        )

        # 7. Persistance MINIMALE dans da_answers (décision validée).
        #    matched_criteria → success, [u["criterion"] for u in unmatched] → errors
        #    highlights → NON persisté (renvoyé dans la réponse API uniquement)
        #    Si source=llm_error (panne serveur), NE PAS insérer pour ne pas
        #    polluer l'historique pédagogique de l'élève.
        if result["source"] != "llm_error":
            await db.execute(
                text("""
                    INSERT INTO da_answers
                        (session_id, question_id, verb_slug, chapter_slug,
                         answer_text, score, score_max, percentage, feedback_ar,
                         success, errors, missing_markers, forbidden_found)
                    VALUES
                        (:session_id, :question_id, :verb_slug, :chapter_slug,
                         :answer_text, :score, :score_max, :percentage, :feedback_ar,
                         :success, :errors, :missing_markers, :forbidden_found)
                """),
                {
                    "session_id": session_id,
                    "question_id": str(q["id"]),
                    "verb_slug": q["verb_slug"],
                    "chapter_slug": body.chapter_slug or "",
                    "answer_text": ans.answer,
                    "score": result["score"],
                    "score_max": result["score_max"],
                    "percentage": result["percentage"],
                    "feedback_ar": result["feedback_ar"],
                    "success": json.dumps(result["matched_criteria"], ensure_ascii=False),
                    "errors": json.dumps(
                        [u["criterion"] for u in result["unmatched_criteria"]],
                        ensure_ascii=False,
                    ),
                    "missing_markers": json.dumps([], ensure_ascii=False),
                    "forbidden_found": json.dumps([], ensure_ascii=False),
                },
            )
        else:
            logger.warning(
                f"eval_v2 | source=llm_error pour question_id={q['id']} "
                f"user={current_user['id']} — insertion da_answers SKIP "
                f"pour ne pas polluer l'historique élève. "
                f"error_message={result.get('error_message', '?')[:200]}"
            )

        # Ne PAS mettre à jour FSRS si source == "llm_error" (échec technique)
        if result["source"] != "llm_error":
            await _update_fsrs_v2(
                db=db,
                user_id=current_user["id"],
                verb_slug=q["verb_slug"],
                chapter_slug=body.chapter_slug or "general",
                percentage=result["percentage"],
            )

        # Compter uniquement les évaluations pédagogiques réussies dans le
        # score de session. Sinon une panne LLM sur une question ferait
        # chuter le score global de l'élève injustement.
        if result["source"] != "llm_error":
            total_score += result["score"]
            total_max += result["score_max"]

        # 8. Format de réponse enrichi avec highlights
        evaluations.append({
            "question_id": str(q["id"]),
            "verb_slug": q["verb_slug"],
            "score": result["score"],
            "score_max": result["score_max"],
            "percentage": result["percentage"],
            "highlights": result["highlights"],
            "matched_criteria": result["matched_criteria"],
            "unmatched_criteria": result["unmatched_criteria"],
            "feedback_ar": result["feedback_ar"],
            "advice_ar": result["advice_ar"],
            "source": result["source"],
            # Spec §3.1 — feedback enrichi
            "missing": result.get("missing", []),
            "dominant_error_code": result.get("dominant_error_code", "unknown"),
            "success": result.get("success", []),
            "errors": result.get("errors", []),
            "remediation": result.get("remediation"),
            # Ne PAS exposer llm_raw au frontend en prod
        })

        # 8b. Audit logging asynchrone (hashes uniquement)
        await log_correction_audit(
            db=db,
            result=result,
            verb_slug=q["verb_slug"],
            user_id=current_user["id"],
            session_id=str(session_id),
        )

    # 9. Update session
    global_pct = round((total_score / total_max) * 100) if total_max else 0
    await db.execute(
        text("UPDATE da_sessions SET score_global = :pct WHERE id = :sid"),
        {"pct": global_pct, "sid": session_id},
    )
    await db.commit()

    logger.info(
        f"eval_v2 | user={current_user['id']} scenario={body.scenario_id} "
        f"score={total_score}/{total_max} ({global_pct}%)"
    )

    n_errors = sum(1 for e in evaluations if e["source"] == "llm_error")

    return {
        "session_id": str(session_id),
        "score_global": total_score,
        "score_max": total_max,
        "percentage": global_pct,
        "evaluations": evaluations,
        "technical_errors": n_errors,
    }


def _compute_score_max_for_verb(verb_slug: str) -> int:
    """Score max par verbe. Aligné sur les VERB_RULES existants
    dans services/document_analysis_service.py pour ne pas
    perturber les statistiques."""
    from services.document_analysis_service import VERB_RULES

    rules = VERB_RULES.get(verb_slug)
    if not rules:
        return 4  # fallback raisonnable
    return sum(r.get("points", 0) for r in rules.get("rules", [])) or 4


async def _update_fsrs_v2(
    db: AsyncSession,
    user_id: str,
    verb_slug: str,
    chapter_slug: str,
    percentage: int,
):
    """Met à jour le score et le compteur FSRS (identique à document_analysis.py)."""
    await db.execute(
        text("""
            INSERT INTO da_fsrs
                (user_id, verb_slug, chapter_slug, last_score, attempts, updated_at)
            VALUES
                (:user_id, :verb, :chapter, :score, 1, NOW())
            ON CONFLICT (user_id, verb_slug, chapter_slug) DO UPDATE SET
                last_score = EXCLUDED.last_score,
                attempts = da_fsrs.attempts + 1,
                updated_at = NOW()
        """),
        {"user_id": user_id, "verb": verb_slug, "chapter": chapter_slug, "score": percentage},
    )
