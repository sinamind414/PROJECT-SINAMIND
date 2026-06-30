from datetime import UTC, datetime, timedelta

import pytest

from services.orientation_service import _find_chapter_meta, calculer_orientation


class FakeRow:
    def __init__(self, mapping):
        self._mapping = mapping


class FakeResult:
    def __init__(self, rows):
        self._rows = [FakeRow(r) for r in rows]

    def fetchall(self):
        return self._rows


class SequencedDb:
    def __init__(self, sequence):
        self.sequence = sequence
        self.index = 0

    async def execute(self, *_args, **_kwargs):
        rows = self.sequence[self.index]
        self.index += 1
        return FakeResult(rows)


class TestFindChapterMeta:
    def test_returns_exact_match_first(self):
        meta = {
            "genetique_humaine": {"titre_ar": "الوراثة البشرية"},
            "immunologie": {"titre_ar": "المناعة"},
        }
        assert _find_chapter_meta("immunologie", meta) == {"titre_ar": "المناعة"}

    def test_returns_partial_match_when_exact_missing(self):
        meta = {
            "u3_genetique_humaine": {"titre_ar": "الوراثة البشرية"},
        }
        assert _find_chapter_meta("genetique_humaine", meta) == {"titre_ar": "الوراثة البشرية"}

    def test_returns_empty_dict_when_no_match(self):
        assert _find_chapter_meta("xyz", {}) == {}


class TestCalculerOrientation:
    pytestmark = pytest.mark.asyncio
    async def test_returns_empty_priority_message_when_no_signals(self):
        db = SequencedDb([
            [],  # flashcards dues
            [],  # action verbs
            [],  # da_fsrs
            [],  # mindmap weak nodes
            [],  # chapters meta
            [],  # prediction source
        ])

        result = await calculer_orientation(db, "1")

        assert result["prediction_bac"] is None
        assert result["dues_aujourd_hui"] == {
            "flashcards": 0,
            "action_verbs": 0,
            "document_analysis": 0,
        }
        assert result["recommendations"] == []
        assert "Aucune priorité" in result["message"]

    async def test_prioritizes_course_recommendations_from_cross_engine_signals(self):
        now = datetime.now(UTC)
        db = SequencedDb([
            [
                {"chapter": "genetique_humaine", "nb_dues": 3},
                {"chapter": "immunologie", "nb_dues": 1},
            ],
            [
                {"verb_slug": "analyser", "last_score": 45, "attempts": 3, "prochaine_revision": now - timedelta(hours=2)},
            ],
            [
                {"verb_slug": "interpreter", "chapter_slug": "genetique_humaine", "last_score": 50, "attempts": 2, "prochaine_revision": None},
                {"verb_slug": "conclure", "chapter_slug": "immunologie", "last_score": 70, "attempts": 1, "prochaine_revision": now - timedelta(hours=1)},
            ],
            [
                {"chapitre": "genetique_humaine", "label": "node1", "importance": "critique"},
                {"chapitre": "genetique_humaine", "label": "node2", "importance": "haute"},
            ],
            [
                {"chapter_id": "genetique_humaine", "titre_fr": "Génétique humaine", "titre_ar": "الوراثة البشرية", "importance": "critique", "bac_frequent": True},
                {"chapter_id": "immunologie", "titre_fr": "Immunologie", "titre_ar": "المناعة", "importance": "haute", "bac_frequent": True},
            ],
            [
                {"chapter": "genetique_humaine", "avg_stability": 2.0, "nb_concepts": 4},
                {"chapter": "immunologie", "avg_stability": 6.0, "nb_concepts": 2},
            ],
        ])

        result = await calculer_orientation(db, "1")

        assert result["prediction_bac"] == 33
        assert result["dues_aujourd_hui"] == {
            "flashcards": 4,
            "action_verbs": 1,
            "document_analysis": 2,
        }
        assert len(result["recommendations"]) == 2
        top = result["recommendations"][0]
        assert top["type"] == "cours"
        assert top["chapitre_slug"] == "genetique_humaine"
        assert top["chapitre_ar"] == "الوراثة البشرية"
        assert top["action"] == "/cours/genetique_humaine"
        assert "chapitre critique" in top["raison"]
        assert "analyse de document" in top["raison"]
        assert "Commence par" in result["message"]

    async def test_adds_action_verb_recommendation_when_room_left(self):
        now = datetime.now(UTC)
        db = SequencedDb([
            [],
            [
                {"verb_slug": "analyser", "last_score": 20, "attempts": 5, "prochaine_revision": now - timedelta(days=1)},
                {"verb_slug": "interpreter", "last_score": 55, "attempts": 3, "prochaine_revision": now - timedelta(hours=1)},
            ],
            [],
            [],
            [],
            [],
        ])

        result = await calculer_orientation(db, "1")

        assert len(result["recommendations"]) == 2
        assert result["recommendations"][0]["type"] == "action_verb"
        assert result["recommendations"][0]["action"] == "/action-verbs/analyser"
        assert "score moyen 20%" in result["recommendations"][0]["raison"]
        assert result["recommendations"][1]["type"] == "action_verb"
        assert result["dues_aujourd_hui"]["action_verbs"] == 2

    async def test_document_analysis_signals_appear_in_course_raison(self):
        now = datetime.now(UTC)
        db = SequencedDb([
            [],
            [],
            [
                {"verb_slug": "interpreter", "chapter_slug": "immunologie", "last_score": 40, "attempts": 2, "prochaine_revision": None},
            ],
            [],
            [
                {"chapter_id": "immunologie", "titre_fr": "Immunologie", "titre_ar": "المناعة", "importance": "haute", "bac_frequent": True},
            ],
            [],
        ])

        result = await calculer_orientation(db, "1")

        assert len(result["recommendations"]) == 1
        rec = result["recommendations"][0]
        assert rec["type"] == "cours"
        assert rec["chapitre_slug"] == "immunologie"
        assert "analyse de document" in rec["raison"]
