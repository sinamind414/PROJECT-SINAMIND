from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from services.dashboard_orchestrator import build_dashboard_orchestrator


pytestmark = pytest.mark.asyncio


class DummyScheduler:
    pass


class DummyDb:
    pass


class TestDashboardOrchestratorService:
    async def test_build_dashboard_orchestrator_prefers_orientation_over_fsrs(self, monkeypatch):
        now = datetime.now(UTC).isoformat()
        progress_snapshot = {
            "nb_concepts": 1,
            "dues_aujourd_hui": 1,
            "prediction_bac": {
                "note_globale": 15.2,
                "par_matiere": {},
                "points_forts": ["sciences_naturelles"],
                "points_faibles": [],
                "mention": "Bien",
            },
            "concepts": [
                {
                    "matiere": "sciences_naturelles",
                    "chapitre_id": "genetique",
                    "stability": 0.8,
                    "difficulty": 6.0,
                    "retrievability": 0.35,
                    "prochaine_revision": now,
                    "interval_jours": 1,
                    "est_due": True,
                    "statut_revision": "a_revoir_aujourdhui",
                    "priority": "urgente",
                }
            ],
        }
        orientation_snapshot = {
            "prediction_bac": 72,
            "dues_aujourd_hui": {"flashcards": 2, "action_verbs": 1, "document_analysis": 0},
            "recommendations": [
                {
                    "priorite": 1,
                    "type": "cours",
                    "chapitre_slug": "immunologie",
                    "chapitre_ar": "المناعة",
                    "raison": "chapitre critique",
                    "action": "/cours/immunologie",
                    "score_priorite": 20,
                }
            ],
            "message": "Commence par immunologie.",
        }
        week_snapshot = {
            "week_start": now,
            "days": [],
            "streak_days": 0,
            "total_dues_this_week": 0,
            "total_reviewed_this_week": 0,
        }
        due_cards_snapshot = {"cards": [], "total": 0}

        monkeypatch.setattr(
            "services.dashboard_orchestrator.get_progress_snapshot",
            AsyncMock(return_value=progress_snapshot),
        )
        monkeypatch.setattr(
            "services.dashboard_orchestrator.calculer_orientation",
            AsyncMock(return_value=orientation_snapshot),
        )
        monkeypatch.setattr(
            "services.dashboard_orchestrator.get_week_activity_snapshot",
            AsyncMock(return_value=week_snapshot),
        )
        monkeypatch.setattr(
            "services.dashboard_orchestrator.get_due_cards_snapshot",
            AsyncMock(return_value=due_cards_snapshot),
        )

        payload = await build_dashboard_orchestrator(DummyDb(), {"id": 7, "prenom": "Lina", "filiere": "SVT", "plan": "free"}, DummyScheduler())

        assert payload["user"]["id"] == 7
        assert payload["orchestration"]["priority_action"]["source"] == "orientation"
        assert payload["orchestration"]["priority_action"]["href"] == "/cours/immunologie"
        assert payload["orchestration"]["continue_card"]["title"] == "المناعة"
        assert payload["orchestration"]["strategic_chapter"]["chapterSlug"] == "immunologie"
        assert payload["orchestration"]["engine_pulse"]["predictionBac"] == 15.2
        assert payload["orchestration"]["engine_pulse"]["topOrientation"]["chapitre_slug"] == "immunologie"

    async def test_build_dashboard_orchestrator_uses_fsrs_when_orientation_empty(self, monkeypatch):
        now = datetime.now(UTC).isoformat()
        progress_snapshot = {
            "nb_concepts": 2,
            "dues_aujourd_hui": 1,
            "prediction_bac": {
                "note_globale": 11.0,
                "par_matiere": {},
                "points_forts": [],
                "points_faibles": ["sciences_naturelles"],
                "mention": "Passable",
            },
            "concepts": [
                {
                    "matiere": "sciences_naturelles",
                    "chapitre_id": "respiration_cellulaire",
                    "stability": 0.6,
                    "difficulty": 7.0,
                    "retrievability": 0.28,
                    "prochaine_revision": now,
                    "interval_jours": 1,
                    "est_due": True,
                    "statut_revision": "a_revoir_aujourdhui",
                    "priority": "urgente",
                },
                {
                    "matiere": "sciences_naturelles",
                    "chapitre_id": "genetique",
                    "stability": 2.4,
                    "difficulty": 5.0,
                    "retrievability": 0.57,
                    "prochaine_revision": now,
                    "interval_jours": 2,
                    "est_due": False,
                    "statut_revision": "bientot",
                    "priority": "haute",
                },
            ],
        }
        orientation_snapshot = {
            "prediction_bac": None,
            "dues_aujourd_hui": {"flashcards": 1, "action_verbs": 0, "document_analysis": 0},
            "recommendations": [],
            "message": "Aucune priorité détectée.",
        }
        week_snapshot = {
            "week_start": now,
            "days": [],
            "streak_days": 0,
            "total_dues_this_week": 0,
            "total_reviewed_this_week": 0,
        }
        due_cards_snapshot = {"cards": [], "total": 0}

        monkeypatch.setattr("services.dashboard_orchestrator.get_progress_snapshot", AsyncMock(return_value=progress_snapshot))
        monkeypatch.setattr("services.dashboard_orchestrator.calculer_orientation", AsyncMock(return_value=orientation_snapshot))
        monkeypatch.setattr("services.dashboard_orchestrator.get_week_activity_snapshot", AsyncMock(return_value=week_snapshot))
        monkeypatch.setattr("services.dashboard_orchestrator.get_due_cards_snapshot", AsyncMock(return_value=due_cards_snapshot))

        payload = await build_dashboard_orchestrator(DummyDb(), {"id": 9}, DummyScheduler())

        assert payload["orchestration"]["priority_action"]["source"] == "fsrs"
        assert payload["orchestration"]["priority_action"]["href"] == "/cours/respiration_cellulaire"
        assert payload["orchestration"]["continue_card"]["source"] == "fsrs"
        assert payload["orchestration"]["continue_card"]["href"] == "/cours/respiration_cellulaire"
        assert payload["orchestration"]["strategic_chapter"]["source"] == "fsrs"
        assert payload["orchestration"]["strategic_chapter"]["mindmapHref"] == "/mindmap?chapter=respiration_cellulaire"
        assert payload["orchestration"]["engine_pulse"]["urgentConceptsCount"] == 1
        assert payload["orchestration"]["engine_pulse"]["soonConceptsCount"] == 1
        assert payload["orchestration"]["engine_pulse"]["stableConceptsCount"] == 0
        assert payload["orchestration"]["engine_pulse"]["topPriorityConcept"]["chapitre_id"] == "respiration_cellulaire"

    async def test_build_dashboard_orchestrator_safe_fallback_when_everything_empty(self, monkeypatch):
        progress_snapshot = {
            "message": "Aucune progression enregistrée",
            "concepts": [],
            "prediction_bac": None,
            "nb_concepts": 0,
            "dues_aujourd_hui": 0,
        }
        orientation_snapshot = {
            "prediction_bac": None,
            "dues_aujourd_hui": {"flashcards": 0, "action_verbs": 0, "document_analysis": 0},
            "recommendations": [],
            "message": "Aucune priorité détectée.",
        }
        week_snapshot = {
            "week_start": datetime.now(UTC).isoformat(),
            "days": [],
            "streak_days": 0,
            "total_dues_this_week": 0,
            "total_reviewed_this_week": 0,
        }
        due_cards_snapshot = {"cards": [], "total": 0}

        monkeypatch.setattr("services.dashboard_orchestrator.get_progress_snapshot", AsyncMock(return_value=progress_snapshot))
        monkeypatch.setattr("services.dashboard_orchestrator.calculer_orientation", AsyncMock(return_value=orientation_snapshot))
        monkeypatch.setattr("services.dashboard_orchestrator.get_week_activity_snapshot", AsyncMock(return_value=week_snapshot))
        monkeypatch.setattr("services.dashboard_orchestrator.get_due_cards_snapshot", AsyncMock(return_value=due_cards_snapshot))

        payload = await build_dashboard_orchestrator(DummyDb(), {"id": 11, "prenom": None}, DummyScheduler())

        assert payload["user"]["id"] == 11
        assert payload["orchestration"]["priority_action"]["source"] == "fallback"
        assert payload["orchestration"]["priority_action"]["href"] == "/drill"
        assert payload["orchestration"]["continue_card"]["source"] == "fallback"
        assert payload["orchestration"]["continue_card"]["href"] == "/cours"
        assert payload["orchestration"]["strategic_chapter"]["source"] == "fallback"
        assert payload["orchestration"]["strategic_chapter"]["lessonHref"] == "/cours"
        assert payload["orchestration"]["engine_pulse"]["predictionBac"] is None
        assert payload["orchestration"]["engine_pulse"]["dueCardsTotal"] == 0
        assert payload["orchestration"]["engine_pulse"]["topPriorityConcept"] is None
        assert payload["orchestration"]["engine_pulse"]["topOrientation"] is None
