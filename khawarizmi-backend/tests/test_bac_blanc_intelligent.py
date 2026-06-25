"""Tests Bac Blanc Intelligent — Semaine 6"""

import pytest
from methodology.bac_blanc_guidance import get_guidance, generate_real_time_guidance
from methodology.action_plan import generate_personalized_action_plan


class TestGuidance:
    def test_get_guidance_before(self):
        msg = get_guidance("وضّح في نص علمي", "before")
        assert "introduction" in msg.lower()

    def test_get_guidance_during(self):
        msg = get_guidance("أثبت", "during")
        assert "document" in msg

    def test_get_guidance_after(self):
        msg = get_guidance("برّر", "after")
        assert "justification" in msg.lower()

    def test_unknown_verb(self):
        msg = get_guidance("unknown_verb", "before")
        assert msg == "Respecte la methodologie du verbe demande."

    def test_unknown_phase(self):
        msg = get_guidance("ناقش", "unknown")
        assert msg == "Respecte la methodologie du verbe demande."

    def test_generate_real_time_with_intro(self):
        result = generate_real_time_guidance(
            instruction="وضّح في نص علمي",
            current_text="مقدمة المشكل العلمي",
            verb_info={"arabic": "وضّح في نص علمي"}
        )
        assert "tips" in result
        # should not suggest introduction since "مقدمة" is present
        assert not any("introduction" in t.lower() for t in result["tips"])

    def test_generate_real_time_without_intro(self):
        result = generate_real_time_guidance(
            instruction="وضّح في نص علمي",
            current_text="body text without introduction",
            verb_info={"arabic": "وضّح في نص علمي"}
        )
        assert any("introduction" in t.lower() for t in result["tips"])

    def test_generate_real_time_short_text(self):
        text = "court"  # less than 30 words
        result = generate_real_time_guidance(
            instruction="أثبت",
            current_text=text,
            verb_info={"arabic": "أثبت"}
        )
        assert any("Developpe" in t for t in result["tips"])


class TestActionPlan:
    def test_debutant_plan(self):
        plan = generate_personalized_action_plan("Debutant", [])
        assert "Introduction" in plan["priority_actions"][0]

    def test_intermediaire_plan(self):
        plan = generate_personalized_action_plan("Intermediaire", [])
        assert "documents" in plan["priority_actions"][0].lower()

    def test_avance_plan(self):
        plan = generate_personalized_action_plan("Avance", [])
        assert len(plan["priority_actions"]) > 0

    def test_expert_plan(self):
        plan = generate_personalized_action_plan("Expert", [])
        assert "Maintenir" in plan["priority_actions"][0]

    def test_plan_with_error_profiles(self):
        plan = generate_personalized_action_plan(
            "Intermediaire",
            [{"recommendation": "Revois la structure attendue"}]
        )
        assert "Revois la structure attendue" in plan["focus_areas"]


class TestEndpoint:
    def test_router_imports(self):
        from routes.bac_blanc_intelligent import router
        assert "/api/bac-blanc" in str(router.prefix)
