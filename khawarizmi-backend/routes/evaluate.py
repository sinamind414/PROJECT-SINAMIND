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
from services.fallback_v2 import evaluate_l2
from services.llm import call_gpt4o_evaluator


def _safe_json_fallback() -> dict:
    """Niveau 3 — JSON de secours absolu, retourné en cas d'erreur d'évaluateur."""
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

# ═══════════════════════════════════════════════
# HELPER : Cohérence score/statut
# ═══════════════════════════════════════════════


_MANDATORY_CONCEPTS = [
    "ARN polymerase",
    "polimerase",
    "بوليميراز",
    "brin transcrit",
    "الخيط المنقول",
    "القالب",
    "liaison peptidique",
    "الرابطة الببتيدية",
    "replication",
    "تضاعف",
    "mitose",
    "انقسام خيطي",
]


def _is_mandatory(concept: str) -> bool:
    c = concept.lower().strip()
    return any(m.lower() in c for m in _MANDATORY_CONCEPTS)


def normalize_result(result: dict) -> dict:
    """
    Garantit la cohérence entre score, statut et manquants.
    Un CORRECT avec des concepts obligatoires manquants → PARTIEL.
    """
    manquant = result.get("manquant", [])
    mandatory_missing = [m for m in manquant if _is_mandatory(m)]

    if mandatory_missing and result.get("statut") == "CORRECT":
        result["statut"] = "PARTIEL"
        result["score"] = min(result.get("score", 10), 6)
        result["feedback"] = result.get("feedback", "").replace("Excellent", "Bien")

    # Score 0 doit être FAUX
    if result.get("score", 0) == 0 and result.get("statut") != "FAUX":
        result["statut"] = "FAUX"

    # RETRY (common_mistakes) reste inchangé
    return result


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
    next_review_date = None

    if eval_result["source"] in ["GPT4O", "FALLBACK_L2"]:
        # Charger les mappings concepts pour cette question
        res_mapping = await db.execute(
            text("SELECT micro_concept AS concept_id, weight FROM question_concept_map WHERE question_id = :qid"),
            {"qid": req.question_id},
        )
        mapping_rows = res_mapping.fetchall()

        # Si aucun mapping n'existe encore en base, on crée un mapping par défaut sur le concept_cle
        if not mapping_rows:
            concept_cle = question.get("concept_cle", "concept_general")
            concepts_dict = {concept_cle: 1.0}
        else:
            concepts_dict = {row[0]: row[1] for row in mapping_rows}

        from services.fsrs_graph import QuestionConceptMapping, update_concept_graph

        mapping = QuestionConceptMapping(question_id=req.question_id, concepts=concepts_dict)

        # Charger l'état actuel de ces concepts pour l'utilisateur
        concept_ids = list(concepts_dict.keys())
        concept_states = {}

        if concept_ids:
            # Safe tuple injection in query — asyncpg requires `expanding` for IN
            cids_param = tuple(concept_ids) if len(concept_ids) > 1 else (concept_ids[0],)
            stmt = text(
                "SELECT concept_id, fsrs_state FROM mastery_micro_concepts WHERE user_id = :uid AND concept_id IN :cids"
            ).bindparams(bindparam("cids", expanding=True))
            res_states = await db.execute(stmt, {"uid": user_id, "cids": cids_param})

            from fsrs import Card

            for row in res_states.fetchall():
                c_id = row[0]
                fsrs_state_dict = row[1] if row[1] else {}
                card = Card()
                if fsrs_state_dict:
                    try:
                        card.stability = fsrs_state_dict.get("stability", card.stability)
                        card.difficulty = fsrs_state_dict.get("difficulty", card.difficulty)
                        # Utiliser setattr pour les attributs facultatifs
                        for attr in ["scheduled_days", "reps", "lapses"]:
                            if hasattr(card, attr) and attr in fsrs_state_dict:
                                setattr(card, attr, fsrs_state_dict[attr])
                    except Exception as e:
                        logger.error(f"Erreur hydratation FSRS: {e}")
                concept_states[c_id] = card

        # Remplir par des cartes par défaut pour ceux non commencés
        for c_id in concept_ids:
            if c_id not in concept_states:
                from fsrs import Card

                concept_states[c_id] = Card()

        # Charger la configuration FSRS de l'élève
        res_config = await db.execute(text("SELECT fsrs_config FROM users WHERE id = :uid"), {"uid": user_id})
        config_row = res_config.fetchone()
        user_fsrs_config = config_row[0] if config_row else None

        # Mettre à jour le graphe
        updates = update_concept_graph(
            user_id=user_id,
            question_id=req.question_id,
            evaluation_result=eval_result,
            mapping=mapping,
            concept_states=concept_states,
            now=datetime.now(UTC),
            user_fsrs_config=user_fsrs_config,
        )

        chapter = question.get("chapitre_id", "ch_inconnu")
        for c_id, upd in updates.items():
            new_card = upd["card"]
            # Récupérer les jours planifiés de manière sécurisée ( scheduled_days ou calcul par rapport à due )
            sched_days = getattr(new_card, "scheduled_days", 0)
            if not sched_days and new_card.due and new_card.last_review:
                sched_days = (new_card.due - new_card.last_review).days

            fsrs_json = json.dumps(
                {
                    "stability": new_card.stability,
                    "difficulty": new_card.difficulty,
                    "scheduled_days": sched_days,
                    "reps": getattr(new_card, "reps", 0),
                    "lapses": getattr(new_card, "lapses", 0),
                    "state": str(new_card.state),
                    "last_review": new_card.last_review.isoformat() if new_card.last_review else None,
                }
            )

            # Sauvegarde DB
            await db.execute(
                text("""
                    INSERT INTO mastery_micro_concepts
                        (user_id, concept_id, chapter, due_date,
                         interval_jours, difficulty, stability, fsrs_state, pending_real_evaluation, updated_at)
                    VALUES
                        (:user_id, :c_id, :chapter, :due,
                         :interval, :difficulty, :stability, :fsrs_state::jsonb, :pending_eval, NOW())
                    ON CONFLICT (user_id, concept_id)
                    DO UPDATE SET
                        due_date           = EXCLUDED.due_date,
                        interval_jours     = EXCLUDED.interval_jours,
                        difficulty         = EXCLUDED.difficulty,
                        stability          = EXCLUDED.stability,
                        fsrs_state         = EXCLUDED.fsrs_state,
                        pending_real_evaluation = EXCLUDED.pending_real_evaluation,
                        updated_at         = NOW()
                """),
                {
                    "user_id": user_id,
                    "c_id": c_id,
                    "chapter": chapter,
                    "due": upd["due"],
                    "interval": sched_days,
                    "difficulty": new_card.difficulty,
                    "stability": new_card.stability,
                    "fsrs_state": fsrs_json,
                    "pending_eval": eval_result.get("needs_l1_review", False),
                },
            )

            # Utiliser la date du concept clé principal comme date de retour principale de l'API
            if c_id == question.get("concept_cle"):
                next_review_date = upd["due"].isoformat()

        await db.commit()

        # Enfiler pour réévaluation L1 si le score L2 est ambigu (dans la zone grise 0.40 - 0.70)
        if eval_result.get("needs_l1_review"):
            from services.reconciliation_queue import PendingReview, enque_for_l1_review

            review = PendingReview(
                student_id=str(user_id),
                question_id=req.question_id,
                answer=req.reponse_eleve,
                l2_score=float(eval_result["score"]) / 10.0,
                session_id="",
                timestamp=datetime.now(UTC),
            )
            await enque_for_l1_review(review)

        logger.info(
            f"EVAL_OK | user={user_id} | q={req.question_id} | "
            f"score={eval_result['score']} | source={eval_result['source']} | "
            f"next_review={next_review_date}"
        )

    else:
        # Fallback L3 ou erreur totale : carte en attente (Tag)
        await db.execute(
            text("""
                INSERT INTO mastery_micro_concepts (user_id, concept_id, chapter, pending_real_evaluation, updated_at)
                VALUES (:user_id, :mc_id, :chapter, TRUE, NOW())
                ON CONFLICT (user_id, concept_id)
                DO UPDATE SET pending_real_evaluation = TRUE, updated_at = NOW()
            """),
            {"user_id": user_id, "mc_id": req.question_id, "chapter": question.get("chapitre_id", "ch_inconnu")},
        )
        await db.commit()

        logger.warning(f"PENDING_TAGGED | user={user_id} | q={req.question_id} | source={eval_result['source']}")

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
            "score": int(round(res_l2.score_final * 10)),
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
