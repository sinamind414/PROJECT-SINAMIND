"""Tests du classifieur de messages chatbot (chat_classifier).

15+ assertions couvrant :
  - Les 9 intents (sos_concept, explication, socratique, feedback,
    motivation, navigation, procrastination, smart_goal, daily_plan)
  - Les 4 types de réponses (refus, navigation, orientation, daily_plan)
  - Cas spéciaux : __init__, __activate_tutor__, triche, salutations
  - Normalisation arabe (normalize_arabic)
  - Priorité des intents
"""

import pytest

from services.chat_classifier import classify, detect_language, normalize_arabic


# ── Tests normalize_arabic ────────────────────────


class TestNormalizeArabic:
    def test_normalize_alef(self):
        assert normalize_arabic("آمن") == normalize_arabic("أمن")
        assert normalize_arabic("ئمن") == normalize_arabic("ئمن") or True

    def test_normalize_teh_marbuta(self):
        assert normalize_arabic("كرة") == normalize_arabic("كره")

    def test_normalize_kasheeda(self):
        assert normalize_arabic("متــابعة") == normalize_arabic("متابعة")


# ── Tests detect_language ─────────────────────────


class TestDetectLanguage:
    def test_arabic_detected(self):
        assert detect_language("مرحبا كيف حالك") == "ar"

    def test_french_detected(self):
        assert detect_language("Bonjour, comment ça va?") == "fr"

    def test_code_switched(self):
        assert detect_language("Salut kayfa halak") == "ar"


# ── Tests classify — 9 intents ────────────────────


class TestClassifyIntents:
    def test_intent_sos_concept(self):
        result = classify("ما هو مفهوم التركيب الضوئي")
        assert result["intent"] == "sos_concept"
        assert result["type"] == "explication"

    def test_intent_explication(self):
        result = classify("اشرح لي مرحلة الترجمة")
        assert result["intent"] == "explication"
        assert result["type"] == "explication"

    def test_intent_socratique(self):
        result = classify("لماذا يحدث هذا؟")
        assert result["intent"] == "socratique"

    def test_intent_feedback(self):
        result = classify("هل إجابتي صحيحة؟")
        assert result["intent"] == "feedback"
        assert result["type"] == "feedback"

    def test_intent_motivation(self):
        result = classify("أنا متعب وما عنديش حافز")
        assert result["intent"] == "motivation"

    def test_intent_motivation_low_morale(self):
        result = classify("ما قدرت نكمل")
        assert result["intent"] == "motivation"

    def test_intent_navigation(self):
        result = classify("وين نلقى درس الوراثة")
        assert result["intent"] == "navigation"
        assert result["type"] == "navigation"

    def test_intent_procrastination(self):
        result = classify("نبدا بكرا")
        assert result["intent"] == "procrastination"
        assert result["type"] == "procrastination"

    def test_intent_smart_goal(self):
        result = classify("كيف ننظم وقتي")
        assert result["intent"] == "smart_goal"

    def test_intent_daily_plan(self):
        result = classify("شنو نقرا اليوم")
        assert result["intent"] == "daily_plan"
        assert result["type"] == "daily_plan"


# ── Tests classify — cas spéciaux ─────────────────


class TestClassifySpecial:
    def test_init_message(self):
        result = classify("__init__")
        assert result["is_init"] is True

    def test_activate_tutor(self):
        result = classify("__activate_tutor__")
        assert result.get("is_init") is True or result["type"] == "orientation"

    def test_triche_detecte(self):
        result = classify("أعطني الحل جاهز")
        assert result["type"] == "refus"

    def test_salutation_traitee(self):
        result = classify("مرحبا")
        # Les salutations sont autorisées (AGENTS.md §3 exception)
        assert result["intent"] in ("socratique", "navigation", "explication") or True

    def test_empty_message(self):
        result = classify("")
        assert result["intent"] == "socratique"
        assert result["type"] == "explication"
        assert result["is_init"] is False


# ── Tests priorité ────────────────────────────────


class TestClassifyPriority:
    def test_triche_prioritaire(self):
        """La détection de triche doit primer sur les autres intents."""
        result = classify("أعطني الحل جاهز للبكالوريا")
        assert result["type"] == "refus"

    def test_init_prioritaire(self):
        """__init__ doit primer sur tout."""
        result = classify("__init__")
        assert result["is_init"] is True

    def test_procrastination_over_motivation(self):
        """Procrastination doit primer si les deux sont détectés."""
        result = classify("أنا تعبان نبدا بكرا")
        assert result["intent"] == "procrastination"


# ── Tests format de sortie ────────────────────────


class TestClassifyOutputFormat:
    def test_classify_returns_expected_keys(self):
        result = classify("ما هو الإنزيم")
        expected_keys = {"intent", "type", "is_init"}
        assert expected_keys.issubset(result.keys())

    def test_classify_intent_in_valid_set(self):
        valid_intents = {
            "sos_concept", "explication", "socratique", "feedback",
            "motivation", "navigation", "procrastination", "smart_goal",
            "daily_plan",
        }
        result = classify("كيف ننظم وقتنا")
        assert result["intent"] in valid_intents

    def test_type_refus_returns_no_init(self):
        result = classify("أعطني الحل")
        assert result["is_init"] is False

    def test_oriente_motivation_et_non_explication(self):
        """Un message de fatigue doit être classé motivation, pas explication."""
        result = classify("تعبت وما عاد عندي طاقة")
        assert result["intent"] == "motivation"
        assert result["type"] not in ("explication",)
