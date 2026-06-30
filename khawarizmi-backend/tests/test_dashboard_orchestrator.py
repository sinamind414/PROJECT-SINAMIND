from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from schemas.dashboard import DashboardOrchestratorPayload
from services.scheduler import KhawarizmiScheduler


@pytest.fixture(autouse=True)
def _patch_scheduler():
    s = KhawarizmiScheduler()
    with patch("routes.dashboard.get_scheduler", return_value=s):
        yield


def _mock_progress_snapshot(concepts=None):
    """Retourne un snapshot progress standard pour les tests."""
    concepts = concepts or []
    prediction_bac = {"note_globale": 0.0, "par_matiere": {}}
    if concepts:
        prediction_bac = {"note_globale": 12.5, "par_matiere": {"sciences_naturelles": {"note": 12.5, "coefficient": 5, "nb_concepts": 3, "retrievability": 0.625}}}
    return {
        "nb_concepts": len(concepts),
        "dues_aujourd_hui": sum(1 for c in concepts if c.get("est_due")),
        "prediction_bac": prediction_bac,
        "concepts": concepts,
    }


def _mock_orientation(recommendations=None):
    """Retourne une orientation standard pour les tests."""
    recommendations = recommendations or []
    return {
        "prediction_bac": 12,
        "dues_aujourd_hui": {"flashcards": 3, "action_verbs": 1, "document_analysis": 0},
        "recommendations": recommendations,
        "message": "Analyse effectuée",
    }


def _mock_week_activity():
    return {
        "week_start": "2026-06-29T00:00:00",
        "days": [
            {"date": "2026-06-29", "day_index": 0, "dues_count": 2, "reviewed_count": 1, "status": "active", "primary_task": None, "primary_chapter": None, "load": 1},
            {"date": "2026-06-30", "day_index": 1, "dues_count": 3, "reviewed_count": 0, "status": "planned", "primary_task": None, "primary_chapter": None, "load": 1},
        ],
        "streak_days": 5,
        "total_dues_this_week": 5,
        "total_reviewed_this_week": 1,
    }


def _mock_due_cards(count=0):
    cards = [
        {
            "id": str(i + 1),
            "micro_concept_id": f"mc_{i}",
            "concept_id": f"c_{i}",
            "chapter": "chapitre_test",
            "difficulty": 5.0,
            "stability": 3.0,
            "state": 0,
            "due_date": "2026-06-30T10:00:00",
            "next_review": "2026-06-30T10:00:00",
            "interval_jours": 1,
        }
        for i in range(count)
    ]
    return {"cards": cards, "total": len(cards)}


@pytest.mark.usefixtures("override_deps")
class TestDashboardOrchestratorContract:

    async def test_orchestrator_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/dashboard/orchestrator")
        assert response.status_code == 401

    @patch("services.dashboard_orchestrator.get_progress_snapshot")
    @patch("services.dashboard_orchestrator.calculer_orientation")
    @patch("services.dashboard_orchestrator.get_week_activity_snapshot")
    @patch("services.dashboard_orchestrator.get_due_cards_snapshot")
    async def test_orchestrator_response_matches_schema(
        self,
        mock_due: AsyncMock,
        mock_week: AsyncMock,
        mock_orient: AsyncMock,
        mock_progress: AsyncMock,
        client: AsyncClient,
        auth_headers: dict,
    ):
        concept = {
            "matiere": "sciences_naturelles",
            "chapitre_id": "transcription_proteines",
            "stability": 8.5,
            "difficulty": 4.2,
            "retrievability": 0.72,
            "prochaine_revision": "2026-06-30T10:00:00",
            "interval_jours": 3,
            "est_due": True,
            "statut_revision": "a_revoir_aujourdhui",
            "priority": "haute",
        }
        mock_progress.return_value = _mock_progress_snapshot([concept])
        mock_orient.return_value = _mock_orientation([
            {"priorite": 1, "type": "cours", "chapitre_slug": "transcription_proteines", "chapitre_ar": "الترجمة", "raison": "Priorité moteur", "action": "/cours/transcription_proteines", "score_priorite": 95}
        ])
        mock_week.return_value = _mock_week_activity()
        mock_due.return_value = _mock_due_cards(2)

        response = await client.get("/api/dashboard/orchestrator", headers=auth_headers)
        assert response.status_code == 200

        body = response.json()

        # Validation Pydantic du contrat
        payload = DashboardOrchestratorPayload(**body)

        assert payload.orchestration.source == "backend_orchestrator"
        assert payload.orchestration.priority_action.source == "orientation"
        assert payload.orchestration.priority_action.tone == "danger"
        assert payload.orchestration.priority_action.href.startswith("/")

        assert payload.progress.nb_concepts == 1
        assert payload.progress.dues_aujourd_hui == 1
        assert payload.progress.concepts[0].priority == "haute"

        assert payload.orchestration.engine_pulse.source == "backend"
        assert payload.orchestration.engine_pulse.predictionBac == 12.5
        assert payload.orchestration.engine_pulse.dueCardsTotal == 2
        assert payload.orchestration.engine_pulse.urgentConceptsCount == 1

        assert payload.orchestration.continue_card.source == "orientation"
        assert payload.orchestration.strategic_chapter.source == "orientation"
        assert payload.orchestration.strategic_chapter.chapterSlug == "transcription_proteines"

        assert payload.week_activity.streak_days == 5
        assert len(payload.due_cards.cards) == 2

    @patch("services.dashboard_orchestrator.get_progress_snapshot")
    @patch("services.dashboard_orchestrator.calculer_orientation")
    @patch("services.dashboard_orchestrator.get_week_activity_snapshot")
    @patch("services.dashboard_orchestrator.get_due_cards_snapshot")
    async def test_orchestrator_fallback_without_recommendations_uses_fsrs_due_concept(
        self,
        mock_due: AsyncMock,
        mock_week: AsyncMock,
        mock_orient: AsyncMock,
        mock_progress: AsyncMock,
        client: AsyncClient,
        auth_headers: dict,
    ):
        due_concept = {
            "matiere": "sciences_naturelles",
            "chapitre_id": "mitochondrie_role",
            "stability": 3.2,
            "difficulty": 6.0,
            "retrievability": 0.35,
            "prochaine_revision": "2026-06-29T08:00:00",
            "interval_jours": 0,
            "est_due": True,
            "statut_revision": "a_revoir_aujourdhui",
            "priority": "urgente",
        }

        mock_progress.return_value = _mock_progress_snapshot([due_concept])
        mock_orient.return_value = _mock_orientation([])
        mock_week.return_value = _mock_week_activity()
        mock_due.return_value = _mock_due_cards(1)

        response = await client.get("/api/dashboard/orchestrator", headers=auth_headers)
        assert response.status_code == 200

        body = response.json()
        payload = DashboardOrchestratorPayload(**body)

        assert payload.orchestration.priority_action.source == "fsrs"
        assert "mitochondrie" in payload.orchestration.priority_action.title
        assert "/cours/" in payload.orchestration.priority_action.href
        assert payload.orchestration.priority_action.cta == "ابدأ المراجعة الآن"

        assert payload.orchestration.continue_card.source == "fsrs"
        assert payload.orchestration.strategic_chapter.source == "fsrs"
        assert payload.orchestration.strategic_chapter.chapterSlug == "mitochondrie_role"

        assert payload.orchestration.engine_pulse.urgentConceptsCount == 1
        assert payload.orchestration.engine_pulse.dueCardsTotal == 1

    @patch("services.dashboard_orchestrator.get_progress_snapshot")
    @patch("services.dashboard_orchestrator.calculer_orientation")
    @patch("services.dashboard_orchestrator.get_week_activity_snapshot")
    @patch("services.dashboard_orchestrator.get_due_cards_snapshot")
    async def test_orchestrator_empty_state_returns_safe_fallback_contract(
        self,
        mock_due: AsyncMock,
        mock_week: AsyncMock,
        mock_orient: AsyncMock,
        mock_progress: AsyncMock,
        client: AsyncClient,
        auth_headers: dict,
    ):
        mock_progress.return_value = _mock_progress_snapshot([])
        mock_orient.return_value = _mock_orientation([])
        mock_week.return_value = _mock_week_activity()
        mock_due.return_value = _mock_due_cards(0)

        response = await client.get("/api/dashboard/orchestrator", headers=auth_headers)
        assert response.status_code == 200

        body = response.json()
        payload = DashboardOrchestratorPayload(**body)

        assert payload.orchestration.priority_action.source == "fallback"
        assert payload.orchestration.priority_action.href == "/drill"
        assert payload.orchestration.priority_action.cta == "راجع الآن"

        assert payload.orchestration.continue_card.source == "fallback"
        assert payload.orchestration.continue_card.href == "/cours"

        assert payload.orchestration.strategic_chapter.source == "fallback"
        assert payload.orchestration.strategic_chapter.mindmapHref == "/mindmap"
        assert payload.orchestration.strategic_chapter.chapterSlug is None
        assert payload.orchestration.strategic_chapter.title is not None

        assert payload.orchestration.engine_pulse.predictionBac == 0.0
        assert payload.orchestration.engine_pulse.dueToday == 0
        assert payload.orchestration.engine_pulse.dueCardsTotal == 0
        assert payload.orchestration.engine_pulse.urgentConceptsCount == 0
