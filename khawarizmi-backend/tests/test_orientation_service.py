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
        assert len(result["recommendations"]) == 3
        top = result["recommendations"][0]
        assert top["type"] == "cours"
        assert top["chapitre_slug"] == "genetique_humaine"
        assert top["chapitre_ar"] == "الوراثة البشرية"
        assert top["action"] == "/cours/genetique_humaine"
        assert "chapitre critique" in top["raison"]
        assert "analyse" in top["raison"]
        assert top["niveau_urgence"] == "critique"
        assert top["nature_besoin"] == "memoire"
        assert top["moteur_source_principal"] == "flashcards"
        assert top["impact_note_estime"] == "fort"
        # 3ème reco : DA pour genetique_humaine (permissive already check)
        da_reco = result["recommendations"][2]
        assert da_reco["type"] == "document_analysis"
        assert da_reco["chapitre_slug"] == "genetique_humaine"
        assert "analyse" in da_reco["raison"]
        assert da_reco["niveau_urgence"] == "normale"
        assert da_reco["nature_besoin"] == "bac"
        assert da_reco["moteur_source_principal"] == "document_analysis"
        assert da_reco["impact_note_estime"] == "limite"
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
        av0 = result["recommendations"][0]
        assert av0["type"] == "action_verb"
        assert av0["action"] == "/action-verbs/analyser"
        assert "score moyen 20%" in av0["raison"]
        assert av0["niveau_urgence"] == "critique"
        assert av0["nature_besoin"] == "methodologie"
        assert av0["moteur_source_principal"] == "action_verbs"
        assert av0["impact_note_estime"] == "fort"
        assert result["recommendations"][1]["type"] == "action_verb"
        assert result["dues_aujourd_hui"]["action_verbs"] == 2

    async def test_adds_document_analysis_recommendation_if_only_da_signal(self):
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
        assert rec["type"] == "document_analysis"
        assert rec["chapitre_slug"] == "immunologie"
        assert "analyse" in rec["raison"]
        assert rec["action"] == "/document-analysis/chapters/immunologie"
        assert rec["niveau_urgence"] == "normale"
        assert rec["nature_besoin"] == "bac"
        assert rec["moteur_source_principal"] == "document_analysis"
        assert rec["impact_note_estime"] == "limite"

    async def test_bac_frequent_breaks_tie_in_chapter_ranking(self):
        now = datetime.now(UTC)
        db = SequencedDb([
            [
                {"chapter": "chap_a", "nb_dues": 1},
                {"chapter": "chap_b", "nb_dues": 1},
            ],
            [],
            [],
            [],
            [
                {"chapter_id": "chap_a", "titre_fr": "Chap A", "titre_ar": "أ", "importance": "haute", "bac_frequent": True},
                {"chapter_id": "chap_b", "titre_fr": "Chap B", "titre_ar": "ب", "importance": "haute", "bac_frequent": False},
            ],
            [
                {"chapter": "chap_a", "avg_stability": 5.0, "nb_concepts": 2},
                {"chapter": "chap_b", "avg_stability": 5.0, "nb_concepts": 2},
            ],
        ])

        result = await calculer_orientation(db, "1")

        slugs = [r["chapitre_slug"] for r in result["recommendations"]]
        assert slugs == ["chap_a", "chap_b"]
        a = result["recommendations"][0]
        assert a["niveau_urgence"] == "normale"
        assert a["nature_besoin"] == "memoire"
        assert a["moteur_source_principal"] == "flashcards"
        assert a["impact_note_estime"] == "limite"

    async def test_critical_domination_over_moyenne_with_fc_dues(self):
        now = datetime.now(UTC)
        db = SequencedDb([
            [
                {"chapter": "chap_crit", "nb_dues": 1},
                {"chapter": "chap_moy", "nb_dues": 1},
            ],
            [],
            [],
            [],
            [
                {"chapter_id": "chap_crit", "titre_fr": "Critique", "titre_ar": "ج", "importance": "critique", "bac_frequent": False},
                {"chapter_id": "chap_moy", "titre_fr": "Moyen", "titre_ar": "م", "importance": "moyenne", "bac_frequent": False},
            ],
            [
                {"chapter": "chap_crit", "avg_stability": 5.0, "nb_concepts": 1},
                {"chapter": "chap_moy", "avg_stability": 5.0, "nb_concepts": 1},
            ],
        ])

        result = await calculer_orientation(db, "1")

        slugs = [r["chapitre_slug"] for r in result["recommendations"]]
        assert slugs[0] == "chap_crit"

    async def test_av_gate_skips_moderate_verb_when_courses_strong(self):
        now = datetime.now(UTC)
        db = SequencedDb([
            [
                {"chapter": "critique_chap", "nb_dues": 3},
            ],
            [
                {"verb_slug": "analyser", "last_score": 45, "attempts": 3, "prochaine_revision": now - timedelta(hours=2)},
            ],
            [],
            [],
            [
                {"chapter_id": "critique_chap", "titre_fr": "Critique", "titre_ar": "ج", "importance": "critique", "bac_frequent": True},
            ],
            [
                {"chapter": "critique_chap", "avg_stability": 5.0, "nb_concepts": 2},
            ],
        ])

        result = await calculer_orientation(db, "1")

        types = [r["type"] for r in result["recommendations"]]
        assert "action_verb" not in types
        cours = result["recommendations"][0]
        assert cours["type"] == "cours"
        assert cours["niveau_urgence"] is not None
        assert cours["nature_besoin"] is not None
        assert cours["moteur_source_principal"] is not None
        assert cours["impact_note_estime"] is not None

    async def test_av_included_when_severe_score_below_threshold(self):
        now = datetime.now(UTC)
        db = SequencedDb([
            [
                {"chapter": "critique_chap", "nb_dues": 3},
            ],
            [
                {"verb_slug": "analyser", "last_score": 30, "attempts": 3, "prochaine_revision": now - timedelta(hours=2)},
            ],
            [],
            [],
            [
                {"chapter_id": "critique_chap", "titre_fr": "Critique", "titre_ar": "ج", "importance": "critique", "bac_frequent": True},
            ],
            [
                {"chapter": "critique_chap", "avg_stability": 5.0, "nb_concepts": 2},
            ],
        ])

        result = await calculer_orientation(db, "1")

        types = [r["type"] for r in result["recommendations"]]
        assert "action_verb" in types
        av_reco = [r for r in result["recommendations"] if r["type"] == "action_verb"][0]
        assert av_reco["niveau_urgence"] is not None
        assert av_reco["nature_besoin"] == "methodologie"
        assert av_reco["moteur_source_principal"] == "action_verbs"
        assert av_reco["impact_note_estime"] is not None

    async def test_dangerous_cumul_bonus_ranks_chapter_higher(self):
        now = datetime.now(UTC)
        db = SequencedDb([
            [
                {"chapter": "chap_a", "nb_dues": 1},
                {"chapter": "chap_b", "nb_dues": 1},
            ],
            [],
            [
                {"verb_slug": "interpreter", "chapter_slug": "chap_a", "last_score": 50, "attempts": 2, "prochaine_revision": None},
                {"verb_slug": "interpreter", "chapter_slug": "chap_b", "last_score": 50, "attempts": 2, "prochaine_revision": None},
            ],
            [],
            [
                {"chapter_id": "chap_a", "titre_fr": "Chap A", "titre_ar": "أ", "importance": "critique", "bac_frequent": False},
                {"chapter_id": "chap_b", "titre_fr": "Chap B", "titre_ar": "ب", "importance": "critique", "bac_frequent": False},
            ],
            [
                {"chapter": "chap_a", "avg_stability": 2.5, "nb_concepts": 2},
                {"chapter": "chap_b", "avg_stability": 5.0, "nb_concepts": 2},
            ],
        ])

        result = await calculer_orientation(db, "1")

        slugs = [r["chapitre_slug"] for r in result["recommendations"] if r["type"] == "cours"]
        assert slugs[0] == "chap_a"
