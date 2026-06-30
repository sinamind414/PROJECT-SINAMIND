import pytest

from services.dashboard_orchestrator import (
    _build_continue_card,
    _build_engine_pulse,
    _build_priority_action,
    _build_strategic_chapter,
)


class TestBuildPriorityAction:
    def test_prefers_orientation_recommendation(self):
        orientation = {
            "recommendations": [
                {
                    "priorite": 1,
                    "type": "document_analysis",
                    "chapitre_slug": "immunologie",
                    "chapitre_ar": "المناعة",
                    "raison": "analyse de document en retard",
                    "action": "/document-analysis/chapters/immunologie",
                }
            ]
        }
        progress = {
            "concepts": [
                {"chapitre_id": "genetique", "est_due": True}
            ]
        }

        result = _build_priority_action(orientation, progress)

        assert result["source"] == "orientation"
        assert result["title"] == "المناعة"
        assert result["href"] == "/document-analysis/chapters/immunologie"
        assert result["cta"] == "ابدأ تحليل الوثائق"
        assert result["tone"] == "danger"

    def test_falls_back_to_fsrs_due_concept(self):
        orientation = {"recommendations": []}
        progress = {
            "concepts": [
                {
                    "chapitre_id": "respiration_cellulaire",
                    "est_due": True,
                }
            ]
        }

        result = _build_priority_action(orientation, progress)

        assert result["source"] == "fsrs"
        assert result["href"] == "/cours/respiration_cellulaire"
        assert "respiration cellulaire" in result["title"]
        assert result["cta"] == "ابدأ المراجعة الآن"

    def test_returns_safe_fallback_when_no_orientation_and_no_due_concept(self):
        orientation = {"recommendations": []}
        progress = {"concepts": []}

        result = _build_priority_action(orientation, progress)

        assert result == {
            "title": "ارجع إلى المراجعة السريعة",
            "reason": "لا توجد أولوية حادة الآن، فثبّت المكتسبات قبل الانتقال.",
            "href": "/drill",
            "cta": "راجع الآن",
            "badge": "🔄 تثبيت المكتسبات",
            "tone": "amber",
            "source": "fallback",
        }


class TestBuildContinueCard:
    def test_prefers_orientation_recommendation(self):
        orientation = {
            "recommendations": [
                {
                    "chapitre_slug": "genetique_humaine",
                    "chapitre_ar": "الوراثة البشرية",
                    "raison": "chapitre critique",
                    "action": "/cours/genetique_humaine",
                }
            ]
        }
        progress = {"concepts": []}

        result = _build_continue_card(orientation, progress)

        assert result["source"] == "orientation"
        assert result["title"] == "الوراثة البشرية"
        assert result["href"] == "/cours/genetique_humaine"
        assert result["cta"] == "تابع من هنا"

    def test_uses_weakest_fsrs_concept_when_no_orientation(self):
        orientation = {"recommendations": []}
        progress = {
            "concepts": [
                {"chapitre_id": "genetique", "retrievability": 0.78},
                {"chapitre_id": "immunologie", "retrievability": 0.32},
                {"chapitre_id": "respiration", "retrievability": 0.51},
            ]
        }

        result = _build_continue_card(orientation, progress)

        assert result["source"] == "fsrs"
        assert result["title"] == "immunologie"
        assert result["href"] == "/cours/immunologie"

    def test_returns_safe_fallback_when_nothing_exists(self):
        orientation = {"recommendations": []}
        progress = {"concepts": []}

        result = _build_continue_card(orientation, progress)

        assert result == {
            "title": "آخر درس درسته",
            "subtitle": "استأنف من حيث توقفت",
            "href": "/cours",
            "cta": "تابع الآن",
            "source": "fallback",
        }


class TestBuildStrategicChapter:
    def test_prefers_orientation_chapter(self):
        orientation = {
            "recommendations": [
                {
                    "chapitre_slug": "immunologie",
                    "chapitre_ar": "المناعة",
                    "raison": "analyse de document en retard",
                }
            ]
        }
        progress = {"concepts": []}

        result = _build_strategic_chapter(orientation, progress)

        assert result["source"] == "orientation"
        assert result["chapterSlug"] == "immunologie"
        assert result["lessonHref"] == "/cours/immunologie"
        assert result["mindmapHref"] == "/mindmap?chapter=immunologie"

    def test_uses_due_fsrs_concept_when_no_orientation(self):
        orientation = {"recommendations": []}
        progress = {
            "concepts": [
                {"chapitre_id": "respiration_cellulaire", "est_due": True},
                {"chapitre_id": "genetique", "est_due": False},
            ]
        }

        result = _build_strategic_chapter(orientation, progress)

        assert result["source"] == "fsrs"
        assert result["chapterSlug"] == "respiration_cellulaire"
        assert result["lessonHref"] == "/cours/respiration_cellulaire"
        assert result["mindmapHref"] == "/mindmap?chapter=respiration_cellulaire"

    def test_returns_safe_fallback_when_no_signal_exists(self):
        orientation = {"recommendations": []}
        progress = {"concepts": []}

        result = _build_strategic_chapter(orientation, progress)

        assert result == {
            "title": "لا توجد نقطة ضعف واضحة حالياً",
            "subtitle": "استمر في المراجعة السريعة أو انتقل إلى تمارين BAC",
            "lessonHref": "/cours",
            "mindmapHref": "/mindmap",
            "chapterSlug": None,
            "source": "fallback",
        }


class TestBuildEnginePulse:
    def test_aggregates_counts_and_top_objects(self):
        progress = {
            "dues_aujourd_hui": 3,
            "prediction_bac": {"note_globale": 13.7},
            "concepts": [
                {
                    "chapitre_id": "genetique",
                    "est_due": False,
                    "statut_revision": "stable",
                },
                {
                    "chapitre_id": "immunologie",
                    "est_due": True,
                    "statut_revision": "a_revoir_aujourdhui",
                },
                {
                    "chapitre_id": "respiration",
                    "est_due": False,
                    "statut_revision": "bientot",
                },
            ],
        }
        orientation = {
            "dues_aujourd_hui": {
                "flashcards": 4,
                "action_verbs": 2,
                "document_analysis": 1,
            },
            "recommendations": [
                {
                    "chapitre_slug": "immunologie",
                    "chapitre_ar": "المناعة",
                    "raison": "chapitre critique",
                }
            ],
        }
        due_cards = {"total": 5}

        result = _build_engine_pulse(progress, orientation, due_cards)

        assert result["predictionBac"] == 13.7
        assert result["dueToday"] == 3
        assert result["flashcardsDue"] == 4
        assert result["actionVerbsDue"] == 2
        assert result["documentAnalysisDue"] == 1
        assert result["urgentConceptsCount"] == 1
        assert result["soonConceptsCount"] == 1
        assert result["stableConceptsCount"] == 1
        assert result["topPriorityConcept"]["chapitre_id"] == "immunologie"
        assert result["topOrientation"]["chapitre_slug"] == "immunologie"
        assert result["dueCardsTotal"] == 5
        assert result["source"] == "backend"

    def test_handles_empty_inputs_safely(self):
        progress = {
            "dues_aujourd_hui": 0,
            "prediction_bac": None,
            "concepts": [],
        }
        orientation = {
            "dues_aujourd_hui": {
                "flashcards": 0,
                "action_verbs": 0,
                "document_analysis": 0,
            },
            "recommendations": [],
        }
        due_cards = {"total": 0}

        result = _build_engine_pulse(progress, orientation, due_cards)

        assert result == {
            "predictionBac": None,
            "dueToday": 0,
            "flashcardsDue": 0,
            "actionVerbsDue": 0,
            "documentAnalysisDue": 0,
            "urgentConceptsCount": 0,
            "soonConceptsCount": 0,
            "stableConceptsCount": 0,
            "topPriorityConcept": None,
            "topOrientation": None,
            "dueCardsTotal": 0,
            "source": "backend",
        }
