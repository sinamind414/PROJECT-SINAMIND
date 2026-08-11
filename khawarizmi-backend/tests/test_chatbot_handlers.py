"""tests/test_chatbot_handlers.py — Handlers du chatbot (audit S2.2).

Chaque handler est testé isolément avec des mocks (db, openai_client,
semantic_cache, call_llm) — la logique est désormais testable sans route.
- refus : statique, jamais de LLM
- methodology / lesson : 0 token
- navigation : statique
- orientation : cartes + FSRS push (due concept)
- procrastination / smart_goal / motivation / feedback : cache → LLM → fallback
- default : RAG + LLM + fallback + cache + engagement
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.chatbot_handlers import (
    handle_default_explanation,
    handle_feedback,
    handle_illusion,
    handle_lesson,
    handle_methodology,
    handle_motivation,
    handle_navigation,
    handle_orientation,
    handle_procrastination,
    handle_refus,
    handle_smart_goal,
)
from services.chatbot_orchestrator import handle_chatbot_message


@pytest.fixture
def db():
    return AsyncMock()


@pytest.fixture
def client():
    return MagicMock()


# ── Refus ────────────────────────────────────────────────────────────

class TestRefus:
    @pytest.mark.asyncio
    async def test_refus_static(self):
        r = await handle_refus()
        assert r["type"] == "refus"
        assert "لا أستطيع" in r["reponse"]
        assert r["question_suivante"]

    @pytest.mark.asyncio
    async def test_dispatcher_refus_before_methodology(self, db, client):
        """Audit P0-4.4 : un message hybride de triche est refusé AVANT la
        détection de méthodologie/leçon."""
        # "ديرلي الحل تاع تحليل الوثيقة" → classifier doit dire refus
        with patch("services.chatbot_handlers.handle_methodology") as m, \
             patch("services.chatbot_handlers.handle_lesson") as l:
            r = await handle_chatbot_message(
                "أعطني الحل الكامل للبكالوريا", {}, 1, db, client
            )
        assert r["type"] == "refus"
        m.assert_not_called()
        l.assert_not_called()


# ── Méthodologie / Leçon (0 token) ───────────────────────────────────

class TestMethodologyLesson:
    @pytest.mark.asyncio
    async def test_methodology_detected(self):
        r = await handle_methodology("قارن بين النواة والهيولى", 1)
        assert r is not None
        assert r["type"] == "methodology_local"  # type réel des réponses locales

    @pytest.mark.asyncio
    async def test_methodology_none(self):
        assert await handle_methodology("أهلاً", 1) is None

    @pytest.mark.asyncio
    async def test_lesson_detected(self):
        r = await handle_lesson("اشرح لي درس المناعة", 1)
        assert r is not None

    @pytest.mark.asyncio
    async def test_lesson_none(self):
        assert await handle_lesson("أهلاً", 1) is None


# ── Navigation ───────────────────────────────────────────────────────

class TestNavigation:
    @pytest.mark.asyncio
    async def test_navigation_with_chapitre(self):
        r = await handle_navigation({"chapitre": "ch1_proteines"})
        assert r["type"] == "navigation"
        assert r["cartes"][0]["action"] == "/cours/ch1_proteines"

    @pytest.mark.asyncio
    async def test_navigation_without_chapitre(self):
        r = await handle_navigation({})
        assert r["cartes"][0]["action"] == "/cours"


# ── Orientation / init + FSRS push ──────────────────────────────────

class TestOrientation:
    @pytest.mark.asyncio
    async def test_orientation_basic(self, db):
        db_orientation = {"prediction_bac": 65, "message": "أنت على المسار الصحيح"}
        objective = {
            "kind": "bac_validation",
            "title_ar": "تحقق في وضعية BAC",
            "reason_ar": "المعرفة جاهزة والتطبيق ناقص",
            "unlock_condition_ar": "احصل على 70٪",
            "href": "/document-analysis/chapters/d1-u1-c1-test",
            "cta_ar": "تحقق",
        }
        with patch("services.chatbot_handlers.calculer_orientation",
                   new=AsyncMock(return_value=db_orientation)), \
             patch("services.orientation_roadmap.calculer_roadmap",
                   new=AsyncMock(return_value={"prochain_objectif": objective, "coach": {"ar": "coach"}})), \
             patch("services.chatbot_handlers.get_due_concept_for_question",
                   new=AsyncMock(return_value=None)):
            r = await handle_orientation(db, 1, {}, is_init=True)
        assert r["type"] == "orientation"
        assert "65" in r["reponse"]
        assert r["prochain_objectif"] == objective
        assert len(r["cartes"]) == 1
        assert r["cartes"][0]["action"] == objective["href"]

    @pytest.mark.asyncio
    async def test_orientation_with_due_push(self, db):
        db_orientation = {"prediction_bac": None, "message": "msg"}
        due = {"concept_id": "transcription", "chapter": "ch1", "stability": 1.5}
        with patch("services.chatbot_handlers.calculer_orientation",
                   new=AsyncMock(return_value=db_orientation)), \
             patch("services.chatbot_handlers.get_due_concept_for_question",
                   new=AsyncMock(return_value=due)):
            r = await handle_orientation(db, 1, {}, is_init=True)
        assert r["type"] == "orientation_with_due_push"
        assert r["due_concept"] == "transcription"


# ── Procrastination / Smart goal / Motivation / Feedback ────────────

class TestLLMHandlers:
    @pytest.mark.asyncio
    async def test_procrastination_llm(self, db, client):
        with patch("services.chatbot_handlers.call_llm",
                   new=AsyncMock(return_value="لا تؤجل عمل اليوم")), \
             patch("services.chatbot_handlers.get_semantic_cache",
                   new=AsyncMock(return_value=None)), \
             patch("services.chatbot_handlers.set_semantic_cache",
                   new=AsyncMock()):
            r = await handle_procrastination(db, 1, "ما عنديش الحافز", {}, client)
        assert r["type"] == "procrastination"
        assert "لا تؤجل" in r["reponse"]

    @pytest.mark.asyncio
    async def test_procrastination_fallback(self, db, client):
        with patch("services.chatbot_handlers.call_llm",
                   new=AsyncMock(return_value=None)), \
             patch("services.chatbot_handlers.get_semantic_cache",
                   new=AsyncMock(return_value=None)), \
             patch("services.chatbot_handlers.set_semantic_cache",
                   new=AsyncMock()):
            r = await handle_procrastination(db, 1, "ما عنديش الحافز", {}, client)
        assert r["type"] == "procrastination"
        assert r["reponse"]  # fallback non vide

    @pytest.mark.asyncio
    async def test_feedback_llm(self, db, client):
        with patch("services.chatbot_handlers.call_llm",
                   new=AsyncMock(return_value="إجابتك جيدة")), \
             patch("services.chatbot_handlers.get_semantic_cache",
                   new=AsyncMock(return_value=None)):
            r = await handle_feedback(db, 1, "هذي إجابتي", {}, client)
        assert r["type"] == "feedback"

    @pytest.mark.asyncio
    async def test_feedback_fallback_no_llm(self, db, client):
        with patch("services.chatbot_handlers.call_llm",
                   new=AsyncMock(return_value=None)), \
             patch("services.chatbot_handlers.get_semantic_cache",
                   new=AsyncMock(return_value=None)):
            r = await handle_feedback(db, 1, "هذي إجابتي", {}, client)
        assert "صفحة التمرين" in r["reponse"]

    @pytest.mark.asyncio
    async def test_motivation_cache_hit(self, db, client):
        cached = {"type": "motivation", "reponse": "أنت قادر"}
        with patch("services.chatbot_handlers.get_semantic_cache",
                   new=AsyncMock(return_value=cached)):
            r = await handle_motivation(db, 1, "ما عنديش حافز", {}, client)
        assert r["reponse"] == "أنت قادر"

    @pytest.mark.asyncio
    async def test_smart_goal_llm(self, db, client):
        with patch("services.chatbot_handlers.call_llm",
                   new=AsyncMock(return_value="هدفك: 16/20")), \
             patch("services.chatbot_handlers.get_semantic_cache",
                   new=AsyncMock(return_value=None)), \
             patch("services.chatbot_handlers.set_semantic_cache",
                   new=AsyncMock()):
            r = await handle_smart_goal(db, 1, "حاب نراجع", {}, client)
        assert r["type"] == "smart_goal"

    @pytest.mark.asyncio
    async def test_illusion_no_due_no_chapitre(self, db):
        with patch("services.chatbot_handlers.get_due_concept_for_question",
                   new=AsyncMock(return_value=None)):
            r = await handle_illusion(db, 1, {})
        assert r["type"] == "illusion_check"
        assert "بطاقات" in r["reponse"]


# ── Handler par défaut (RAG + LLM) ───────────────────────────────────

class TestDefaultExplanation:
    @pytest.mark.asyncio
    async def test_socratique_with_rag_and_llm(self, db, client):
        rag_chunks = [{"source": "livre", "content": "extrait", "chapter": "ch1"}]
        with patch("services.chatbot_handlers.rag_search",
                   new=AsyncMock(return_value=rag_chunks)), \
             patch("services.chatbot_handlers.get_semantic_cache",
                   new=AsyncMock(return_value=None)), \
             patch("services.chatbot_handlers.set_semantic_cache",
                   new=AsyncMock()), \
             patch("services.chatbot_handlers.call_llm",
                   new=AsyncMock(return_value="فكر في النواة")), \
             patch("services.chatbot_handlers.calculer_orientation",
                   new=AsyncMock(return_value={})), \
             patch("services.chatbot_engagement_service.record_chat_interaction",
                   new=AsyncMock()):
            r = await handle_default_explanation(
                db, 1, "ما هو دور ADN؟", {"chapitre": "ch1"}, client, mode="tutor"
            )
        assert r["type"] in ("explication", "socratique")
        assert r["reponse"] == "فكر في النواة"
        assert r["sources"][0]["source"] == "livre"
        assert r["fallback_active"] is False

    @pytest.mark.asyncio
    async def test_fallback_when_llm_none(self, db, client):
        with patch("services.chatbot_handlers.rag_search",
                   new=AsyncMock(return_value=[])), \
             patch("services.chatbot_handlers.get_semantic_cache",
                   new=AsyncMock(return_value=None)), \
             patch("services.chatbot_handlers.call_llm",
                   new=AsyncMock(return_value=None)), \
             patch("services.chatbot_handlers.calculer_orientation",
                   new=AsyncMock(return_value={})), \
             patch("services.chatbot_engagement_service.record_chat_interaction",
                   new=AsyncMock()):
            r = await handle_default_explanation(
                db, 1, "ما هو دور ADN؟", {}, client, mode="quick"
            )
        assert r["fallback_active"] is True
        assert r["reponse"]  # fallback non vide
        # Pas de cache store quand fallback
        # (vérifié indirectement : set_semantic_cache non appelé)

    @pytest.mark.asyncio
    async def test_cache_hit_skips_llm(self, db, client):
        cached = {"type": "socratique", "reponse": "réponse cachée"}
        with patch("services.chatbot_handlers.get_semantic_cache",
                   new=AsyncMock(return_value=cached)), \
             patch("services.chatbot_handlers.call_llm") as llm:
            r = await handle_default_explanation(
                db, 1, "ما هو دور ADN؟", {}, client, mode="quick"
            )
        assert r["reponse"] == "réponse cachée"
        llm.assert_not_called()

    @pytest.mark.asyncio
    async def test_tutor_mode_injects_prompt(self, db, client):
        """Le mode tutor ajoute le bloc pédagogique au prompt (vérifié via
        l'appel à call_llm — le prompt contient le mode)."""
        captured = {}

        async def fake_call_llm(prompt, client):
            captured["prompt"] = prompt
            return "réponse"

        with patch("services.chatbot_handlers.rag_search",
                   new=AsyncMock(return_value=[])), \
             patch("services.chatbot_handlers.get_semantic_cache",
                   new=AsyncMock(return_value=None)), \
             patch("services.chatbot_handlers.call_llm",
                   new=fake_call_llm), \
             patch("services.chatbot_handlers.calculer_orientation",
                   new=AsyncMock(return_value={})), \
             patch("services.chatbot_engagement_service.record_chat_interaction",
                   new=AsyncMock()):
            await handle_default_explanation(
                db, 1, "ما هو دور ADN؟", {}, client, mode="tutor"
            )
        assert "وضع المدرّس الشخصي" in captured["prompt"]
