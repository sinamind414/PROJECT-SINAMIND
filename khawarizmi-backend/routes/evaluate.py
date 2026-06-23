import json
import logging
import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any, Optional, List

from deps import get_current_user, get_db, get_openai, get_scheduler
from rate_limit import limiter, evaluate_limit
from services.llm import call_gpt4o_evaluator
from services.fallback import fallback_safe_json
from services.fallback_v2 import evaluate_l2
from services.remediation import update_mindmap_after_eval, suggest_action_verb

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

class ActionVerbSuggestion(BaseModel):
    verb_slug: str
    verb_fr: str
    reason_ar: str
    href: str
    priority: str = "medium"

class EvaluateResponse(BaseModel):
    score: int
    statut: str
    feedback: str
    manquant: List[str]
    next_review_date: Optional[str] = None
    source: str
    recommended_verb: Optional[ActionVerbSuggestion] = None

# ═══════════════════════════════
# ENDPOINT PRINCIPAL
# ═══════════════════════════════

# ═══════════════════════════════════════════════
# HELPER : Cohérence score/statut
# ═══════════════════════════════════════════════

_MANDATORY_CONCEPTS = [
    "ARN polymerase", "polimerase", "بوليميراز",
    "brin transcrit", "الخيط المنقول", "القالب",
    "liaison peptidique", "الرابطة الببتيدية",
    "replication", "تضاعف",
    "mitose", "انقسام خيطي",
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
    request:      Request,
    req:          EvaluateRequest,
    current_user: Dict           = Depends(get_current_user),
    db:           AsyncSession   = Depends(get_db),
    openai_client                = Depends(get_openai)
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
            {"qid": req.question_id}
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
            res_states = await db.execute(
                text("SELECT concept_id, fsrs_state FROM mastery_micro_concepts WHERE user_id = :uid AND concept_id = ANY(:cids)"),
                {"uid": user_id, "cids": list(concept_ids)}
            )
            
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
        res_config = await db.execute(
            text("SELECT fsrs_config FROM users WHERE id = :uid"),
            {"uid": user_id}
        )
        config_row = res_config.fetchone()
        user_fsrs_config = config_row[0] if config_row else None

        # Charger le graphe de dépendances depuis la DB
        from services.fsrs_graph import load_concept_graph
        concept_graph = await load_concept_graph(db)

        # Mettre à jour le graphe
        updates = update_concept_graph(
            user_id=user_id,
            question_id=req.question_id,
            evaluation_result=eval_result,
            mapping=mapping,
            concept_states=concept_states,
            now=datetime.now(timezone.utc),
            user_fsrs_config=user_fsrs_config,
            graph=concept_graph,
        )
        
        chapter = question.get("chapitre_id", "ch_inconnu")
        for c_id, upd in updates.items():
            new_card = upd["card"]
            # Récupérer les jours planifiés de manière sécurisée ( scheduled_days ou calcul par rapport à due )
            sched_days = getattr(new_card, "scheduled_days", 0)
            if not sched_days and new_card.due and new_card.last_review:
                sched_days = (new_card.due - new_card.last_review).days
                
            fsrs_json = json.dumps({
                "stability":      new_card.stability,
                "difficulty":     new_card.difficulty,
                "scheduled_days": sched_days,
                "reps":           getattr(new_card, "reps", 0),
                "lapses":         getattr(new_card, "lapses", 0),
                "state":          str(new_card.state),
                "last_review":    new_card.last_review.isoformat() if new_card.last_review else None,
            })
            
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
                    "user_id":    user_id,
                    "c_id":       c_id,
                    "chapter":    chapter,
                    "due":        upd["due"],
                    "interval":   sched_days,
                    "difficulty": new_card.difficulty,
                    "stability":  new_card.stability,
                    "fsrs_state": fsrs_json,
                    "pending_eval": eval_result.get("needs_l1_review", False),
                }
            )
            
            # Utiliser la date du concept clé principal comme date de retour principale de l'API
            if c_id == question.get("concept_cle"):
                next_review_date = upd["due"].isoformat()
                
        await db.commit()
        
        # Enfiler pour réévaluation L1 si le score L2 est ambigu (dans la zone grise 0.40 - 0.70)
        if eval_result.get("needs_l1_review"):
            from services.reconciliation_queue import enque_for_l1_review, PendingReview
            review = PendingReview(
                student_id=str(user_id),
                question_id=req.question_id,
                answer=req.reponse_eleve,
                l2_score=float(eval_result["score"]) / 10.0,
                session_id="",
                timestamp=datetime.now(timezone.utc)
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
            {
                "user_id": user_id,
                "mc_id": req.question_id,
                "chapter": question.get("chapitre_id", "ch_inconnu")
            }
        )
        await db.commit()
        
        logger.warning(
            f"PENDING_TAGGED | user={user_id} | "
            f"q={req.question_id} | source={eval_result['source']}"
        )

    # Normaliser la cohérence score/statut/manquant
    eval_result = normalize_result(eval_result)

    # ── Lien 2 (Eval → MindMap color) : mettre à jour le nœud MindMap ──
    concept_cle = question.get("concept_cle", "")
    chapter = question.get("chapitre_id", "")
    try:
        await update_mindmap_after_eval(
            db=db,
            user_id=str(user_id),
            concept_id=concept_cle,
            score=eval_result.get("score", 0),
            chapter=chapter,
        )
        await db.commit()
    except Exception as e:
        logger.warning(f"MINDMAP_LINK | Erreur mise à jour nœud: {e}")

    # ── Lien 3 (Eval → Verbe d'action) : suggérer un verbe pour la remédiation ──
    error_type = eval_result.get("error_type")
    missing_concepts = eval_result.get("manquant", [])
    action_verb = suggest_action_verb(
        error_type=error_type,
        chapter=chapter,
        score=eval_result.get("score", 0),
        missing_concepts=missing_concepts,
    )
    if action_verb:
        eval_result["recommended_verb"] = action_verb
        logger.info(
            f"ACTION_VERB_LINK | user={user_id} | q={req.question_id} | "
            f"verb={action_verb['verb_slug']} | reason={action_verb['reason_ar']}"
        )

    # Traduire le feedback si la langue est arabe
    if req.lang == "ar":
        from services.feedback_translator import translate_feedback
        eval_result["feedback"] = translate_feedback(eval_result.get("feedback", ""))

    return EvaluateResponse(
        score            = eval_result["score"],
        statut           = eval_result["statut"],
        feedback         = eval_result["feedback"],
        manquant         = eval_result["manquant"],
        next_review_date = next_review_date,
        source           = eval_result["source"]
    )

# ═══════════════════════════════
# LOGIQUE DE FALLBACK
# ═══════════════════════════════

async def evaluate_with_fallback(question: dict, req: EvaluateRequest, openai_client, user_id: str, db: AsyncSession) -> dict:
    
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
        logger.warning(f"COMMON_MISTAKES_SKIP | user={user_id} | reason={str(e)}")

    # NIVEAU 1 — GPT-4o avec retry
    try:
        result = await call_gpt4o_evaluator(
            client      = openai_client,
            question    = question,
            reponse     = req.reponse_eleve,
            tentative   = req.tentative
        )
        result["source"] = "GPT4O"
        return result

    except Exception as e:
        logger.warning(f"FALLBACK_L2 | user={user_id} | q={req.question_id} | reason={str(e)}")

    # NIVEAU 2 — Pattern matching local composite
    try:
        res_l2 = await evaluate_l2(
            reponse_eleve = req.reponse_eleve,
            question_data = question,
            db = db
        )
        
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
            "source": "FALLBACK_L2"
        }

    except Exception as e:
        logger.error(f"FALLBACK_L3 | user={user_id} | q={req.question_id} | reason={str(e)}")

    # NIVEAU 3 — JSON de sécurité absolu
    result = fallback_safe_json()
    result["source"] = "FALLBACK_L3"
    return result

