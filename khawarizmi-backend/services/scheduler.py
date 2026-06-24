"""
services/scheduler.py — Moteur FSRS Khawarizmi v2.0
Spaced Repetition basé sur FSRS (Free Spaced Repetition Scheduler)
Entraîné sur 700M+ reviews réelles — supérieur à SM-2
"""

from fsrs import Scheduler, Card, Rating
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging


def _topological_sort(concept_ids: list, graph: dict) -> list:
    """Trier les concepts selon leurs dépendances (Kahn algorithm).
    graph = {"A": ["B"]} means A must precede B."""
    in_degree = {c: 0 for c in concept_ids}
    adjacency = {c: [] for c in concept_ids}
    for precursor, dependents in graph.items():
        if precursor not in in_degree:
            continue
        for dependent in dependents:
            if dependent in adjacency:
                adjacency[precursor].append(dependent)
                in_degree[dependent] += 1
    queue = [c for c, d in in_degree.items() if d == 0]
    result = []
    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in adjacency.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    for c in concept_ids:
        if c not in result:
            result.append(c)
    return result

logger = logging.getLogger('khawarizmi.scheduler')

# ═══ COEFFICIENTS BAC ALGÉRIEN ══════════════════════════════
COEFFICIENTS_BAC = {
    'mathematiques':       6,
    'physique':            5,
    'sciences_naturelles': 5,
    'arabe':               3,
    'philosophie':         2,
    'francais':            2,
    'anglais':             2,
    'education_islamique': 2,
    'education_civique':   1,
    'histoire_geo':        2,
}

# ═══ SEUILS DE SCORE → RATING ═══════════════════════════════
SCORE_THRESHOLDS = {
    'easy':  90,   # >= 90% → Easy
    'good':  60,   # >= 60% → Good
    'hard':  30,   # >= 30% → Hard
    # < 30%  → Again
}


class KhawarizmiScheduler:
    """
    Moteur de répétition espacée FSRS pour le BAC algérien.

    Remplace SM-2 par FSRS :
    - Courbe d'oubli en loi de puissance (plus précise)
    - Entraîné sur 700M+ reviews réelles
    - Coefficients BAC algérien intégrés
    """

    def __init__(self):
        self.fsrs = Scheduler()
        self._verify_fsrs_api()

    def _verify_fsrs_api(self):
        """Détecte la version de l'API fsrs installée."""
        test_card = Card()
        if hasattr(self.fsrs, 'review_card'):
            self._api_version = 'new'   # fsrs >= 4.0
            logger.info("fsrs API v4.0+ détectée (review_card)")
        elif hasattr(self.fsrs, 'repeat'):
            self._api_version = 'old'   # fsrs < 4.0
            logger.info("fsrs API < 4.0 détectée (repeat)")
        else:
            raise ImportError(
                "Version fsrs incompatible. "
                "Installe : pip install fsrs>=4.0"
            )

    # ═══ INTERFACE PRINCIPALE ═══════════════════════════════

    def calculer_prochain_intervalle(
        self,
        card: Card,
        score_percent: float
    ) -> Dict[str, Any]:
        """
        Calcule le prochain intervalle de révision.

        Args:
            card          : État actuel de la carte FSRS
            score_percent : Score de l'élève (0-100%)

        Returns:
            Dict avec card mise à jour + métriques FSRS
        """
        rating = self._score_to_rating(score_percent)
        now    = datetime.now(timezone.utc)

        try:
            result_card = self._appeler_fsrs(card, rating, now)
        except Exception as e:
            logger.error(f"Erreur FSRS : {e}")
            raise

        retrievability = self._get_retrievability(result_card)

        logger.debug(
            f"FSRS: rating={rating.name} "
            f"→ {result_card.scheduled_days}j "
            f"stability={result_card.stability:.2f}"
        )

        return {
            'card':               result_card,
            'prochaine_revision': result_card.due,
            'difficulty':         round(result_card.difficulty, 3),
            'stability':          round(result_card.stability, 3),
            'retrievability':     retrievability,
            'interval_jours':     result_card.scheduled_days,
            'rating':             rating.name,
        }

    def _appeler_fsrs(
        self,
        card: Card,
        rating: Rating,
        now: datetime
    ) -> Card:
        """Appel FSRS compatible toutes versions."""
        if self._api_version == 'new':
            result_card, _ = self.fsrs.review_card(card, rating)
            return result_card
        else:
            scheduling_cards = self.fsrs.repeat(card, now)
            return scheduling_cards[rating].card

    # ═══ CONVERSIONS ════════════════════════════════════════

    def _score_to_rating(self, score_percent: float) -> Rating:
        """
        Convertit le score Khawarizmi (0-100%) en Rating FSRS.

        Calibré pour le BAC algérien :
        Again (0-30%)  → Revoir dans quelques heures
        Hard  (30-60%) → Revoir dans 1-2 jours
        Good  (60-90%) → Revoir dans 4-7 jours
        Easy  (90%+)   → Revoir dans 2-4 semaines
        """
        score = max(0.0, min(100.0, score_percent))  # Clamp 0-100
        if score >= SCORE_THRESHOLDS['easy']:  return Rating.Easy
        if score >= SCORE_THRESHOLDS['good']:  return Rating.Good
        if score >= SCORE_THRESHOLDS['hard']:  return Rating.Hard
        return Rating.Again

    def _get_retrievability(self, card: Card) -> float:
        """
        Probabilité de rappel à l'instant présent (0.0-1.0).
        Formule FSRS : R = (1 + t/9S)^(-1)
        Supérieure à SM-2 (exponentielle) car validée empiriquement.
        """
        if not card.last_review or card.stability <= 0:
            return 1.0  # Carte jamais vue = fraîche

        now         = datetime.now(timezone.utc)
        last_review = card.last_review

        # Normaliser timezone
        if last_review.tzinfo is None:
            last_review = last_review.replace(tzinfo=timezone.utc)

        elapsed_days = max(0.0, (now - last_review).total_seconds() / 86400)

        # Loi de puissance FSRS
        retrievability = (1 + elapsed_days / (9 * card.stability)) ** (-1)
        return round(min(1.0, max(0.0, retrievability)), 3)

    # ═══ PRÉDICTION BAC ══════════════════════════════════════

    def predire_score_bac(
        self,
        cards_par_matiere: Dict[str, List[Card]]
    ) -> Dict[str, Any]:
        """
        Prédit le score BAC pondéré par les coefficients officiels.

        Args:
            cards_par_matiere : {'mathematiques': [Card, ...], ...}

        Returns:
            {
                'note_globale':     14.5,   # /20
                'par_matiere':      {...},  # détail par matière
                'points_forts':     [...],  # matières > 14/20
                'points_faibles':   [...],  # matières < 10/20
            }
        """
        if not cards_par_matiere:
            return {'note_globale': 0.0, 'par_matiere': {}}

        scores_ponderes  = []
        coeffs_total     = 0
        detail           = {}

        for matiere, cards in cards_par_matiere.items():
            if not cards:
                continue

            coeff = COEFFICIENTS_BAC.get(matiere, 1)

            # Récupérabilité moyenne de la matière
            avg_ret = sum(
                self._get_retrievability(c) for c in cards
            ) / len(cards)

            note_matiere = round(avg_ret * 20, 1)

            detail[matiere] = {
                'note':          note_matiere,
                'coefficient':   coeff,
                'nb_concepts':   len(cards),
                'retrievability':round(avg_ret, 3),
            }

            scores_ponderes.append(note_matiere * coeff)
            coeffs_total   += coeff

        if coeffs_total == 0:
            return {'note_globale': 0.0, 'par_matiere': detail}

        note_globale = round(sum(scores_ponderes) / coeffs_total, 1)

        # Points forts / faibles
        points_forts   = [m for m, d in detail.items() if d['note'] >= 14]
        points_faibles = [m for m, d in detail.items() if d['note'] < 10]

        logger.info(
            f"Prédiction BAC : {note_globale}/20 "
            f"({len(points_forts)} forces, {len(points_faibles)} faiblesses)"
        )

        return {
            'note_globale':   note_globale,
            'par_matiere':    detail,
            'points_forts':   points_forts,
            'points_faibles': points_faibles,
            'mention':        self._get_mention(note_globale),
        }

    def _get_mention(self, note: float) -> str:
        """Mention BAC algérienne officielle."""
        if note >= 18: return "Excellent"
        if note >= 16: return "Très Bien"
        if note >= 14: return "Bien"
        if note >= 12: return "Assez Bien"
        if note >= 10: return "Passable"
        return "Insuffisant"

    # ═══ UTILITAIRES ════════════════════════════════════════

    def get_cartes_dues(
        self,
        cards: List[Dict],
        limit: int = 10
    ) -> List[Dict]:
        """
        Retourne les cartes à réviser AUJOURD'HUI.
        Triées par urgence (retrievability croissante).

        Args:
            cards : [{'card': Card, 'concept_id': str, ...}]
            limit : nombre max de cartes retournées
        """
        now = datetime.now(timezone.utc)

        dues = [
            {
                **c,
                'retrievability':  self._get_retrievability(c['card']),
                'est_due':         c['card'].due <= now,
            }
            for c in cards
        ]

        # Trier par récupérabilité croissante
        # (les plus "oubliées" en premier)
        dues_filtrees = [d for d in dues if d['est_due']]
        dues_filtrees.sort(key=lambda x: x['retrievability'])

        return dues_filtrees[:limit]

    async def get_due_concepts(self, student_id: int, db: AsyncSession) -> List[Dict[str, Any]]:
        from sqlalchemy import text
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        target_date = now + timedelta(days=1)
        query = text("""
            SELECT concept_id, stability, due_date, state
            FROM mastery_micro_concepts
            WHERE user_id = :uid
              AND due_date <= :target_date
              AND state IN (1,2,3)
            ORDER BY due_date ASC, stability ASC
        """)
        result = await db.execute(query, {"uid": student_id, "target_date": target_date})
        rows = result.fetchall()
        due_concepts = []
        for row in rows:
            due_concepts.append({
                "concept_id": row[0],
                "stability": row[1] if row[1] is not None else 0.0,
                "due_date": row[2],
                "state": row[3]
            })
        return due_concepts

    async def select_next_question(self, student_id: int, db: AsyncSession) -> Optional[Dict[str, Any]]:
        from sqlalchemy import text
        due_concepts = await self.get_due_concepts(student_id, db)
        if not due_concepts:
            query_new = text("""
                SELECT qcm.question_id, qcm.micro_concept
                FROM question_concept_map qcm
                LEFT JOIN mastery_micro_concepts mmc 
                  ON mmc.concept_id = qcm.micro_concept AND mmc.user_id = :uid
                WHERE mmc.id IS NULL
                ORDER BY RANDOM()
                LIMIT 1
            """)
            res_new = await db.execute(query_new, {"uid": student_id})
            row = res_new.fetchone()
            if row:
                return {"question_id": row[0], "concept_id": row[1], "type": "NEW"}
            query_fallback = text("""
                SELECT question_id, micro_concept 
                FROM question_concept_map 
                ORDER BY RANDOM() 
                LIMIT 1
            """)
            res_fallback = await db.execute(query_fallback)
            row_fb = res_fallback.fetchone()
            if row_fb:
                return {"question_id": row_fb[0], "concept_id": row_fb[1], "type": "NEW_FALLBACK"}
            return {"question_id": "q_test", "concept_id": "transcription", "type": "DEFAULT"}

        concept_ids = [c["concept_id"] for c in due_concepts]
        concept_stability = {c["concept_id"]: c["stability"] for c in due_concepts}
        cids_param = list(concept_ids)
        query_mappings = text("""
            SELECT question_id, micro_concept, weight
            FROM question_concept_map
            WHERE micro_concept = ANY(:cids)
        """)
        res_mappings = await db.execute(query_mappings, {"cids": cids_param})
        mappings = res_mappings.fetchall()
        if not mappings:
            concept_fb = concept_ids[0]
            return {"question_id": "q_test", "concept_id": concept_fb, "type": "DUE_FALLBACK"}
            
        question_scores = {}
        question_concept_assoc = {}
        for q_id, concept_id, weight in mappings:
            stability = concept_stability.get(concept_id, 0.0)
            inv_stability = 1.0 / max(stability, 0.1)
            score_contrib = weight * inv_stability
            if q_id not in question_scores:
                question_scores[q_id] = 0.0
                question_concept_assoc[q_id] = concept_id
            question_scores[q_id] += score_contrib
            
        sorted_questions = sorted(question_scores.items(), key=lambda x: x[1], reverse=True)
        best_q_id, best_score = sorted_questions[0]
        best_concept_id = question_concept_assoc[best_q_id]
        return {
            "question_id": best_q_id,
            "concept_id": best_concept_id,
            "score": best_score,
            "type": "DUE"
        }
