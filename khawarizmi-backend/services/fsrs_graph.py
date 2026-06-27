"""
services/fsrs_graph.py - Répétition espacée par graphe de micro-concepts
Recommandé par Claude 3 Opus.
"""

import copy
import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from fsrs import Card, Rating, Scheduler

logger = logging.getLogger("khawarizmi.fsrs_graph")
# scheduler par défaut (sentence-transformers ou initialisation basique)
default_scheduler = Scheduler()

_graph_cache: dict[str, Any] = {"data": {}, "timestamp": 0.0}
GRAPH_CACHE_TTL = 300  # 5 minutes


def get_concept_graph() -> dict[str, list[str]]:
    return _graph_cache["data"]


async def load_concept_graph(db) -> dict[str, list[str]]:
    now = time.time()
    if now - _graph_cache["timestamp"] < GRAPH_CACHE_TTL and _graph_cache["data"]:
        return _graph_cache["data"]
    from sqlalchemy import text

    res = await db.execute(
        text("""
        SELECT concept_id, prerequisite_id
        FROM concept_prerequisites
        ORDER BY concept_id
    """)
    )
    rows = res.fetchall()
    graph: dict[str, list[str]] = {}
    for concept_id, prereq_id in rows:
        graph.setdefault(concept_id, []).append(prereq_id)
    _graph_cache["data"] = graph
    _graph_cache["timestamp"] = now
    logger.info(f"Loaded {len(graph)} concept dependencies from DB")
    return graph


@dataclass
class ConceptNode:
    concept_id: str
    card: Card = field(default_factory=Card)
    prerequisites: list[str] = field(default_factory=list)


@dataclass
class QuestionConceptMapping:
    """Chaque question est annotée avec ses concepts et leur poids relatif."""

    question_id: str
    concepts: dict[str, float]
    # Ex: {"structure_tertiaire": 0.30, "liaison_faible": 0.25}


def score_to_fsrs_rating(score: float) -> Rating:
    """
    Mapping non-linéaire score (0.0-1.0) → FSRS Rating.
    Calibré pour la zone de "desirable difficulty" (50-70%).
    """
    if score >= 0.85:
        return Rating.Easy  # Maîtrisé (4)
    elif score >= 0.60:
        return Rating.Good  # Correct mais effort requis (3)
    elif score >= 0.35:
        return Rating.Hard  # Partiellement compris (2)
    else:
        return Rating.Again  # À revoir complètement (1)


def determine_concept_ratings(
    evaluation_result: dict,  # Sortie de L1 (GPT) ou L2 (fallback)
    mapping: QuestionConceptMapping,
) -> dict[str, Rating]:
    """
    Décompose l'évaluation globale en ratings FSRS par concept.
    """
    concept_ratings = {}
    scores_concepts = evaluation_result.get("scores_concepts", {})

    for concept_id, poids in mapping.concepts.items():
        if concept_id in scores_concepts:
            score = float(scores_concepts[concept_id])
            concept_ratings[concept_id] = score_to_fsrs_rating(score)
        else:
            concepts_trouves = set(evaluation_result.get("concepts_trouves", []))
            concepts_errones = set(evaluation_result.get("concepts_errones", []))
            score_global_raw = evaluation_result.get("score", 0)
            score_global_normalized = (
                score_global_raw / 10.0
                if score_global_raw > 1.0
                else float(score_global_raw)
            )

            if not concepts_trouves and score_global_normalized >= 0.60:
                concepts_trouves = set(mapping.concepts.keys())

            if concept_id in concepts_errones:
                concept_ratings[concept_id] = Rating.Again
            elif concept_id not in concepts_trouves:
                concept_ratings[concept_id] = Rating.Again if poids >= 0.20 else Rating.Hard
            elif score_global_normalized >= 0.85 and poids >= 0.25:
                concept_ratings[concept_id] = Rating.Easy
            elif score_global_normalized >= 0.60:
                concept_ratings[concept_id] = Rating.Good
            else:
                concept_ratings[concept_id] = Rating.Hard

    return concept_ratings


def run_fsrs_step(card: Card, rating: Rating, now: datetime, scheduler_inst: Scheduler) -> Card:
    """Appel FSRS v4 ou v3 compatible."""
    if hasattr(scheduler_inst, "review_card"):
        res_card, _ = scheduler_inst.review_card(card, rating, now)
        return res_card
    else:
        scheduling_cards = scheduler_inst.repeat(card, now)
        return scheduling_cards[rating].card


def update_concept_graph(
    user_id: int,
    question_id: str,
    evaluation_result: dict,
    mapping: QuestionConceptMapping,
    concept_states: dict[str, Card],  # États FSRS actuels (depuis la base)
    now: datetime | None = None,
    user_fsrs_config: dict | None = None,
    graph: dict[str, list[str]] | None = None,
) -> dict[str, dict]:
    """
    Met à jour l'état FSRS de chaque micro-concept impliqué.
    """
    if now is None:
        now = datetime.now(UTC)

    from services.fsrs_config import get_fsrs_scheduler

    scheduler_inst = get_fsrs_scheduler(user_fsrs_config)

    ratings = determine_concept_ratings(evaluation_result, mapping)
    updates = {}

    for concept_id, rating in ratings.items():
        card = concept_states.get(concept_id, Card())

        try:
            updated_card = run_fsrs_step(card, rating, now, scheduler_inst)

            updates[concept_id] = {
                "card": updated_card,
                "due": updated_card.due,
                "stability": updated_card.stability,
                "difficulty": updated_card.difficulty,
                "reps": getattr(updated_card, "reps", 0),
                "lapses": getattr(updated_card, "lapses", 0),
                "rating_applied": rating.value,
            }
        except Exception as e:
            logger.error(f"Erreur FSRS sur le concept {concept_id}: {e}")

    active_graph = graph if graph is not None else get_concept_graph()
    if not active_graph:
        logger.warning(
            f"FSRS_GRAPH_EMPTY | user={user_id} | q={question_id} | "
            f"Propagation prérequis ignorée. "
            f"Appeler load_concept_graph(db) avant update_concept_graph."
        )
        return updates

    _propagate_prerequisite_penalties(ratings, concept_states, updates, now, active_graph)
    _propagate_dependent_penalties(ratings, concept_states, updates, active_graph)

    return updates


def _propagate_prerequisite_penalties(
    ratings: dict[str, Rating],
    concept_states: dict[str, Card],
    updates: dict,
    now: datetime,
    graph: dict[str, list[str]],
):
    """
    Pénalise ou reprogramme les prérequis si le concept de haut niveau échoue.
    """
    for concept_id, rating in ratings.items():
        if rating == Rating.Again and concept_id in graph:
            for prereq_id in graph[concept_id]:
                if prereq_id not in updates:
                    prereq_card = copy.deepcopy(concept_states.get(prereq_id, Card()))
                    prereq_card.due = now

                    updates[prereq_id] = {
                        "card": prereq_card,
                        "due": now,
                        "stability": prereq_card.stability,
                        "difficulty": prereq_card.difficulty,
                        "reps": getattr(prereq_card, "reps", 0),
                        "lapses": getattr(prereq_card, "lapses", 0),
                        "rating_applied": None,  # Non évalué, juste reprogrammé
                        "forced_review_reason": f"prerequisite_of:{concept_id}",
                    }


def _propagate_dependent_penalties(
    ratings: dict[str, Rating],
    concept_states: dict[str, Card],
    updates: dict,
    graph: dict[str, list[str]],
    penalty: float = 0.15,
):
    """
    Si un concept de prérequis échoue (Again), réduit la stabilité de tous les concepts dépendants.
    """
    for failed_concept, rating in ratings.items():
        if rating == Rating.Again:
            for dependent_concept, prereqs in graph.items():
                if failed_concept in prereqs and dependent_concept not in updates:
                    card = copy.deepcopy(concept_states.get(dependent_concept, Card()))
                    card.stability *= 1.0 - penalty

                    updates[dependent_concept] = {
                        "card": card,
                        "due": card.due,
                        "stability": card.stability,
                        "difficulty": card.difficulty,
                        "reps": getattr(card, "reps", 0),
                        "lapses": getattr(card, "lapses", 0),
                        "rating_applied": None,  # Non évalué directement
                        "forced_review_reason": f"dependency_weakness:{failed_concept}",
                    }
