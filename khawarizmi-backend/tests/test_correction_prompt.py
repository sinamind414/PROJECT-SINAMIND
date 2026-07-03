"""
tests/test_correction_prompt.py — 32 tests pour la construction du prompt.

Couvre :
- Prompt systeme (non vide, en arabe, regle d'or)
- Methodologie par verbe (25 verbes couverts)
- Construction du prompt (champs obligatoires, documents, formats)
- Techniques experimentales (4 techniques p.117)
- Structure du BAC (5/7/8 p.127)
- Revision tips (7 categories p.120-127)
"""

from prompts.correction_prompt import (
    ANALYSIS_TERMINOLOGY,
    COMMON_BAC_ERRORS,
    REVISION_TIPS_AR,
    SYSTEM_PROMPT_AR,
    VERB_COGNITIVE_LEVELS,
    VERB_METHODOLOGY_AR,
    build_correction_prompt,
)
from prompts.scientific_knowledge import (
    ALL_UNITS,
    build_knowledge_block,
    get_relevant_knowledge,
    get_relevant_knowledge_raw,
)

# ruff: noqa: RUF012 — mutable class defaults in tests are acceptable

# ── Prompt systeme ───────────────────────────────


class TestSystemPrompt:
    """Verifie que le prompt systeme est bien forme."""

    def test_system_prompt_not_empty(self):
        assert SYSTEM_PROMPT_AR
        assert len(SYSTEM_PROMPT_AR) > 100

    def test_system_prompt_contains_json_instruction(self):
        assert "JSON" in SYSTEM_PROMPT_AR

    def test_system_prompt_contains_arabic(self):
        """Le prompt doit contenir du texte arabe."""
        arabic_chars = [c for c in SYSTEM_PROMPT_AR if "\u0600" <= c <= "\u06FF"]
        assert len(arabic_chars) > 50

    def test_system_prompt_mentions_score(self):
        assert "score" in SYSTEM_PROMPT_AR.lower() or "النقطة" in SYSTEM_PROMPT_AR

    def test_system_prompt_mentions_highlights(self):
        assert "highlights" in SYSTEM_PROMPT_AR or "highlight" in SYSTEM_PROMPT_AR.lower()

    def test_system_prompt_no_interpret_in_analysis(self):
        """Regle d'or : dans l'analyse, pas d'interpretation."""
        assert "في التحليل لا تفسير" in SYSTEM_PROMPT_AR

    def test_system_prompt_simple_compound_distinction(self):
        """Le prompt distingue les verbes simples des composes."""
        assert "التعليمات البسيطة" in SYSTEM_PROMPT_AR
        assert "التعليمات المركبة" in SYSTEM_PROMPT_AR


# ── Methodologie par verbe ───────────────────────


class TestVerbMethodology:
    """Verifie la couverture des verbes dans VERB_METHODOLOGY_AR."""

    EXPECTED_VERBS = [
        # تعليمات مركبة (مفتوحة)
        "analyse",
        "interpret",
        "deduce",
        "hypothesis",
        "scientific-text",
        "compare",
        "justify",
        "validate-hypothesis",
        "discuss",
        "relationship",
        "expliquer",
        "critiquer",
        "determiner",
        # تعليمات مركبة إضافية (من الكتاب المنهجي التفصيلي)
        "exploit-document",
        "formulate-problem",
        "prove",
        "comment",
        # تعليمات بسيطة (مغلقة)
        "nommer",
        "definir",
        "decrire",
        "citer",
        "enumerer",
        "classer",
        "distinguer",
        "schematiser",
    ]

    def test_all_main_verbs_covered(self):
        for verb in self.EXPECTED_VERBS:
            assert verb in VERB_METHODOLOGY_AR, f"Verbe '{verb}' manquant"

    def test_methodology_content_not_empty(self):
        for verb, content in VERB_METHODOLOGY_AR.items():
            assert content, f"Methodologie vide pour '{verb}'"
            assert len(content) > 20, f"Methodologie trop courte pour '{verb}'"

    def test_methodology_contains_arabic(self):
        for verb, content in VERB_METHODOLOGY_AR.items():
            arabic_chars = [c for c in content if "\u0600" <= c <= "\u06FF"]
            assert len(arabic_chars) > 10, f"Pas assez d'arabe dans la methodologie de '{verb}'"

    def test_analyse_forbids_interpretation(self):
        """Le verbe 'analyse' doit mentionner l'interdiction de causalite."""
        content = VERB_METHODOLOGY_AR["analyse"]
        assert "الممنوع" in content or "لا تفسير" in content


# ── Construction du prompt ───────────────────────


class TestBuildPrompt:
    """Verifie build_correction_prompt."""

    BASE_KWARGS = {
        "scenario_context": "دراسة تأثير التغذية على نسبة الغلوكوز في الدم",
        "documents": None,
        "question_prompt": "حلّل الوثيقة 1",
        "question_skill": "تحليل وثيقة",
        "verb_slug": "analyse",
        "model_answer": "نلاحظ من خلال الوثيقة أن نسبة الغلوكوز تزداد بعد الوجبة",
        "learning_focus": "التنظيم الهرموني لنسبة السكر في الدم",
        "score_max": 8,
        "student_answer": "نلاحظ أن النسبة تزداد",
    }

    def test_returns_string(self):
        result = build_correction_prompt(**self.BASE_KWARGS)
        assert isinstance(result, str)

    def test_contains_context(self):
        result = build_correction_prompt(**self.BASE_KWARGS)
        assert "التغذية" in result

    def test_contains_question(self):
        result = build_correction_prompt(**self.BASE_KWARGS)
        assert "حلّل الوثيقة" in result

    def test_contains_model_answer(self):
        result = build_correction_prompt(**self.BASE_KWARGS)
        assert "الإجابة النموذجية" in result

    def test_contains_student_answer(self):
        result = build_correction_prompt(**self.BASE_KWARGS)
        assert "إجابة التلميذ" in result
        assert "نلاحظ أن النسبة تزداد" in result

    def test_contains_score_max(self):
        result = build_correction_prompt(**self.BASE_KWARGS)
        assert "8" in result

    def test_contains_methodology(self):
        result = build_correction_prompt(**self.BASE_KWARGS)
        assert "المنهجية" in result

    def test_with_documents(self):
        docs = [
            {"title": "وثيقة 1", "caption": "منحنى تغير نسبة الغلوكوز", "data": None},
            {"title": "وثيقة 2", "caption": "جدول المقارنة", "data": {"rows": [1, 2, 3]}},
        ]
        kwargs = {**self.BASE_KWARGS, "documents": docs}
        result = build_correction_prompt(**kwargs)
        assert "وثيقة 1" in result
        assert "وثيقة 2" in result
        assert "منحنى" in result

    def test_without_learning_focus(self):
        kwargs = {**self.BASE_KWARGS, "learning_focus": None}
        result = build_correction_prompt(**kwargs)
        assert isinstance(result, str)
        assert "حلّل الوثيقة" in result

    def test_new_verb_nommer_in_prompt(self):
        """Le verbe 'nommer' doit etre injecte dans le prompt."""
        kwargs = {**self.BASE_KWARGS, "verb_slug": "nommer"}
        result = build_correction_prompt(**kwargs)
        assert "تعرّف/سمّ" in result

    def test_new_verb_expliquer_in_prompt(self):
        """Le verbe 'expliquer' doit etre injecte dans le prompt."""
        kwargs = {**self.BASE_KWARGS, "verb_slug": "expliquer"}
        result = build_correction_prompt(**kwargs)
        assert "اشرح/وضّح/بيّن" in result


# ── Techniques experimentales (p.117) ─────────────


class TestExperimentalTechniques:
    """Verifie que le prompt systeme mentionne les 4 techniques de base."""

    def test_autoradiographie_presente(self):
        assert "التصوير الإشعاعي الذاتي" in SYSTEM_PROMPT_AR

    def test_immunomarquage_present(self):
        assert "الوسم المناعي" in SYSTEM_PROMPT_AR

    def test_electrophorese_presente(self):
        assert "الهجرة الكهربائية" in SYSTEM_PROMPT_AR

    def test_ouchterlony_present(self):
        assert "أوخترلوني" in SYSTEM_PROMPT_AR or "Ouchterlony" in SYSTEM_PROMPT_AR

    def test_analyse_experimentale_mentionne_technique(self):
        """Le sous-type analyse experimentale doit mentionner l'identification de la technique."""
        content = VERB_METHODOLOGY_AR["analyse"]
        assert "التقنية المستعملة" in content or "تقنية" in content


# ── Structure du BAC (p.127) ──────────────────────


class TestBACScoringStructure:
    """Verifie que le prompt systeme contient la structure de notation."""

    def test_contains_5_7_8_points(self):
        assert "5 نقاط" in SYSTEM_PROMPT_AR
        assert "7 نقاط" in SYSTEM_PROMPT_AR
        assert "8 نقاط" in SYSTEM_PROMPT_AR

    def test_contains_trois_exercices(self):
        assert "التمرين الأول" in SYSTEM_PROMPT_AR
        assert "التمرين الثاني" in SYSTEM_PROMPT_AR
        assert "التمرين الثالث" in SYSTEM_PROMPT_AR


# ── Revision tips (p.120-127) ─────────────────────


class TestRevisionTips:
    """Verifie la structure de REVISION_TIPS_AR."""

    EXPECTED_CATEGORIES = [
        "in_class",
        "at_home",
        "ineffective_revision",
        "exercise_strategy",
        "why_low_scores",
        "bac_exam_structure",
        "group_study",
    ]

    def test_all_categories_present(self):
        for cat in self.EXPECTED_CATEGORIES:
            assert cat in REVISION_TIPS_AR, f"Categorie '{cat}' manquante"

    def test_all_categories_contain_arabic(self):
        for cat, tips in REVISION_TIPS_AR.items():
            assert tips, f"Categorie '{cat}' vide"
            for tip in tips:
                arabic_chars = [c for c in tip if "\u0600" <= c <= "\u06FF"]
                assert len(arabic_chars) > 5, f"Pas assez d'arabe dans le conseil: {tip[:30]}"

    def test_bac_structure_in_revision_tips(self):
        assert "5 نقاط" in " ".join(REVISION_TIPS_AR["bac_exam_structure"])
        assert "7 نقاط" in " ".join(REVISION_TIPS_AR["bac_exam_structure"])
        assert "8 نقاط" in " ".join(REVISION_TIPS_AR["bac_exam_structure"])

    def test_home_revision_mentions_30_minutes(self):
        tips_text = " ".join(REVISION_TIPS_AR["at_home"])
        assert "30 دقيقة" in tips_text


# ── Structure de la base de connaissance ──────────


class TestScientificKnowledgeStructure:
    """Verifie la structure de scientific_knowledge.py."""

    EXP_UNIT_IDS = [
        "unite1-synthese-proteines",
        "unite2-immunite",
        "unite3-systeme-nerveux",
        "unite4-geologie",
        "unite5-energetique",
    ]

    def test_all_5_units_present(self):
        found_ids = [u["id"] for u in ALL_UNITS]
        for uid in self.EXP_UNIT_IDS:
            assert uid in found_ids, f"Unite '{uid}' manquante"

    def test_each_unit_has_vocabulary(self):
        for unit in ALL_UNITS:
            assert unit.get("vocabulary"), f"Vocabulary vide pour {unit['id']}"
            assert len(unit["vocabulary"]) >= 20

    def test_each_unit_has_facts(self):
        for unit in ALL_UNITS:
            assert unit.get("facts"), f"Facts vide pour {unit['id']}"
            assert len(unit["facts"]) >= 10

    def test_each_unit_has_errors(self):
        for unit in ALL_UNITS:
            assert unit.get("errors"), f"Errors vide pour {unit['id']}"
            assert len(unit["errors"]) >= 8

    def test_each_unit_has_keywords(self):
        for unit in ALL_UNITS:
            assert unit.get("keywords"), f"Keywords vide pour {unit['id']}"
            assert len(unit["keywords"]) >= 10

    def test_vocabulary_contains_arabic(self):
        for unit in ALL_UNITS:
            for term in unit["vocabulary"][:5]:
                arabic_chars = [c for c in term if "\u0600" <= c <= "\u06FF"]
                assert len(arabic_chars) > 5, f"Pas assez d'arabe dans vocab de {unit['id']}: {term[:30]}"

    def test_errors_contain_correction_indicator(self):
        for unit in ALL_UNITS:
            for err in unit["errors"]:
                assert "→" in err, f"Erreur sans fleche (→) dans {unit['id']}: {err[:30]}"


# ── Selection automatique ────────────────────────


class TestKnowledgeAutoSelection:
    """Verifie la fonction get_relevant_knowledge."""

    def test_selects_unite1_for_adn_context(self):
        context = "الاستنساخ والترجمة والإنزيم والحمض النووي"
        result = get_relevant_knowledge(context)
        assert "الوحدة الأولى" in result or "تركيب البروتين" in result

    def test_selects_unite2_for_immunite_context(self):
        context = "مناعة الأجسام المضادة و LB و LT"
        result = get_relevant_knowledge(context)
        assert "المناعة" in result

    def test_selects_unite3_for_nerveux_context(self):
        context = "كمون الراحة وكمون العمل والمشبك العصبي"
        result = get_relevant_knowledge(context)
        assert "العصبي" in result or "الجهاز العصبي" in result

    def test_selects_unite4_for_geologie_context(self):
        context = "الغلاف الصخري والاندساس والظهرة المحيطية"
        result = get_relevant_knowledge(context)
        assert "الجيولوجيا" in result

    def test_selects_unite5_for_energetique_context(self):
        context = "البناء الضوئي والتنفس الخلوي والميتوكوندري"
        result = get_relevant_knowledge(context)
        assert "التحولات الطاقوية" in result

    def test_unrelated_context_returns_empty(self):
        context = "مرحبا كيف حالك اليوم"
        result = get_relevant_knowledge(context)
        assert result == ""

    def test_raw_returns_correct_number(self):
        context = "الاستنساخ والترجمة والمناعة والأجسام المضادة"
        result = get_relevant_knowledge_raw(context, max_units=1)
        assert isinstance(result, list)
        assert len(result) <= 1


# ── Construction du bloc ─────────────────────────


class TestKnowledgeBlock:
    """Verifie build_knowledge_block et _build_knowledge_block."""

    def test_build_block_contains_sections(self):
        block = build_knowledge_block(["unite2-immunite"])
        assert "المصطلحات العلمية الأساسية" in block
        assert "حقائق يجب التحقق منها" in block
        assert "أخطاء شائعة يجب كشفها" in block

    def test_build_block_contains_arabic(self):
        block = build_knowledge_block(["unite2-immunite"])
        arabic_chars = [c for c in block if "\u0600" <= c <= "\u06FF"]
        assert len(arabic_chars) > 50

    def test_build_block_has_title(self):
        block = build_knowledge_block(["unite1-synthese-proteines"])
        assert "الوحدة الأولى" in block

    def test_build_block_multiple_units(self):
        block = build_knowledge_block(["unite1-synthese-proteines", "unite2-immunite"])
        assert "الوحدة الأولى" in block
        assert "الوحدة الثانية" in block

    def test_build_block_empty_list(self):
        assert build_knowledge_block([]) == ""

    def test_build_block_unknown_unit(self):
        assert build_knowledge_block(["unknown-unit"]) == ""

    def test_build_block_limits_size(self):
        """Verifie que le bloc ne depasse pas des limites raisonnables."""
        block = build_knowledge_block(["unite1-synthese-proteines"])
        lines = block.split("\n")
        assert len(lines) < 80, f"Bloc trop long: {len(lines)} lignes"


# ── Injection dans le prompt de correction ───────


class TestKnowledgeInCorrectionPrompt:
    """Verifie l'injection automatique dans build_correction_prompt."""

    BASE_KWARGS = {
        "scenario_context": "دراسة تأثير التغذية على نسبة الغلوكوز في الدم",
        "documents": None,
        "question_prompt": "حلّل الوثيقة 1",
        "question_skill": "تحليل وثيقة",
        "verb_slug": "analyse",
        "model_answer": "نلاحظ من خلال الوثيقة أن نسبة الغلوكوز تزداد بعد الوجبة",
        "learning_focus": "التنظيم الهرموني لنسبة السكر في الدم",
        "score_max": 8,
        "student_answer": "نلاحظ أن النسبة تزداد",
    }

    def test_knowledge_injected_when_context_matches(self):
        kwargs = {**self.BASE_KWARGS, "scenario_context": "الاستنساخ والترجمة في الخلية"}
        result = build_correction_prompt(**kwargs)
        assert "المرجع العلمي" in result

    def test_knowledge_contains_terms_from_selected_unit(self):
        kwargs = {**self.BASE_KWARGS, "scenario_context": "الإنزيمات والحمض النووي DNA"}
        result = build_correction_prompt(**kwargs)
        assert "ADN" in result or "المورثة" in result or "بروتين" in result


# ── COMMON_BAC_ERRORS ────────────────────────────


class TestBacErrors:
    """Verifie COMMON_BAC_ERRORS constant."""

    def test_three_categories_present(self):
        assert "methodology" in COMMON_BAC_ERRORS
        assert "knowledge" in COMMON_BAC_ERRORS
        assert "form" in COMMON_BAC_ERRORS

    def test_total_37_errors(self):
        total = sum(len(v) for v in COMMON_BAC_ERRORS.values())
        assert total >= 37, f"Seulement {total} erreurs attendu >= 37"

    def test_methodology_has_25_errors(self):
        assert len(COMMON_BAC_ERRORS["methodology"]) >= 25

    def test_knowledge_has_5_errors(self):
        assert len(COMMON_BAC_ERRORS["knowledge"]) >= 5

    def test_form_has_7_errors(self):
        assert len(COMMON_BAC_ERRORS["form"]) >= 7

    def test_all_errors_are_arabic(self):
        for category, errors in COMMON_BAC_ERRORS.items():
            for err in errors:
                arabic_chars = [c for c in err if "\u0600" <= c <= "\u06FF"]
                assert len(arabic_chars) > 5, f"Pas assez d'arabe dans {category}: {err[:30]}"


# ── VERB_COGNITIVE_LEVELS ────────────────────────


class TestVerbCognitiveLevels:
    """Verifie VERB_COGNITIVE_LEVELS constant."""

    EXPECTED_LEVELS = ["remember", "understand", "apply", "compare_and_analyse", "synthesize"]

    def test_all_5_levels_present(self):
        for level in self.EXPECTED_LEVELS:
            assert level in VERB_COGNITIVE_LEVELS, f"Niveau '{level}' manquant"

    def test_each_level_has_verbs(self):
        for level, verbs in VERB_COGNITIVE_LEVELS.items():
            assert verbs, f"Niveau '{level}' vide"
            assert len(verbs) >= 5, f"Niveau '{level}' a moins de 5 verbes"

    def test_total_at_least_67_verbs(self):
        total = sum(len(v) for v in VERB_COGNITIVE_LEVELS.values())
        assert total >= 67, f"Seulement {total} verbes attendu >= 67"

    def test_verbs_are_arabic(self):
        for level, verbs in VERB_COGNITIVE_LEVELS.items():
            for verb in verbs:
                arabic_chars = [c for c in verb if "\u0600" <= c <= "\u06FF"]
                assert len(arabic_chars) > 1, f"Pas assez d'arabe dans {level}: {verb}"

    def test_compare_analyse_largest_level(self):
        ca = len(VERB_COGNITIVE_LEVELS["compare_and_analyse"])
        assert ca >= 15, f"compare_and_analyse trop petit: {ca}"

    def test_synthesize_has_prove_experimentally(self):
        assert "أثبت تجريبياً" in VERB_COGNITIVE_LEVELS["synthesize"]

    def test_analyse_present(self):
        assert "حلل" in VERB_COGNITIVE_LEVELS["compare_and_analyse"]
        assert "استنتج" in VERB_COGNITIVE_LEVELS["compare_and_analyse"]


# ── ANALYSIS_TERMINOLOGY ─────────────────────────


class TestAnalysisTerminology:
    """Verifie ANALYSIS_TERMINOLOGY constant."""

    EXPECTED_CATEGORIES = ["positive", "negative", "comparison", "interpretation_forbidden_in_analysis"]

    def test_all_4_categories_present(self):
        for cat in self.EXPECTED_CATEGORIES:
            assert cat in ANALYSIS_TERMINOLOGY, f"Categorie '{cat}' manquante"

    def test_each_category_has_terms(self):
        for cat, terms in ANALYSIS_TERMINOLOGY.items():
            assert terms, f"Categorie '{cat}' vide"

    def test_total_at_least_38_terms(self):
        total = sum(len(v) for v in ANALYSIS_TERMINOLOGY.values())
        assert total >= 38, f"Seulement {total} termes attendu >= 38"

    def test_terms_are_arabic(self):
        for cat, terms in ANALYSIS_TERMINOLOGY.items():
            for term in terms:
                arabic_chars = [c for c in term if "\u0600" <= c <= "\u06FF"]
                assert len(arabic_chars) > 1, f"Pas assez d'arabe dans {cat}: {term}"

    def test_forbidden_includes_lian(self):
        assert "لأن" in ANALYSIS_TERMINOLOGY["interpretation_forbidden_in_analysis"]

    def test_positive_includes_thabat(self):
        assert "ثبات" in ANALYSIS_TERMINOLOGY["positive"]

    def test_negative_includes_ghiyab(self):
        assert "غياب" in ANALYSIS_TERMINOLOGY["negative"]


# ── Nouveaux verbes LOT 7 ────────────────────────


class TestNewVerbsLOT7:
    """Verifie les 2 nouveaux verbes (extract, prove-experimentally)."""

    def test_extract_in_methodology(self):
        assert "extract" in VERB_METHODOLOGY_AR

    def test_prove_experimentally_in_methodology(self):
        assert "prove-experimentally" in VERB_METHODOLOGY_AR

    def test_extract_methodology_contains_keywords(self):
        assert "استخلص" in VERB_METHODOLOGY_AR["extract"]
        assert "استخلاص" in VERB_METHODOLOGY_AR["extract"]

    def test_prove_experimentally_contains_3_etapes(self):
        content = VERB_METHODOLOGY_AR["prove-experimentally"]
        assert "التجربة" in content
        assert "الملاحظة" in content
        assert "النتيجة" in content

    def test_extract_differs_from_deduce(self):
        ext = VERB_METHODOLOGY_AR["extract"]
        assert "الفرق بين" in ext or "الاستنتاج" in ext


# ── SYSTEM_PROMPT_AR nouvelles sections ──────────


class TestSystemPromptEnriched:
    """Verifie les 5 nouvelles sections de SYSTEM_PROMPT_AR."""

    def test_extraction_vs_deduction_section(self):
        assert "الاستنتاج" in SYSTEM_PROMPT_AR
        assert "الاستخلاص" in SYSTEM_PROMPT_AR

    def test_analysis_vs_interpretation_section(self):
        assert "التحليل" in SYSTEM_PROMPT_AR
        assert "التفسير" in SYSTEM_PROMPT_AR

    def test_cosmic_triple_framework(self):
        assert "التحليل الثلاثي" in SYSTEM_PROMPT_AR

    def test_terminology_table_section(self):
        assert "مصطلحات التحليل" in SYSTEM_PROMPT_AR

    def test_bac_errors_reference(self):
        assert "37" in SYSTEM_PROMPT_AR and "خطأ" in SYSTEM_PROMPT_AR


# ── Socratic prompt enrichi ──────────────────────


class TestSocraticPromptEnriched:
    """Verifie l'enrichissement du SYSTEM_PROMPT_SOCRATIC."""

    def test_10_error_patterns_present(self):
        import os
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from services.socratic_tutor import SYSTEM_PROMPT_SOCRATIC
        count = SYSTEM_PROMPT_SOCRATIC.count("**")
        assert count >= 10, f"Trouve {count} patterns, attendu >= 10"

    def test_extraction_vs_deduction_in_socratic(self):
        from services.socratic_tutor import SYSTEM_PROMPT_SOCRATIC
        assert "الاستنتاج" in SYSTEM_PROMPT_SOCRATIC or "الاستخلاص" in SYSTEM_PROMPT_SOCRATIC

    def test_causal_style_in_socratic(self):
        from services.socratic_tutor import SYSTEM_PROMPT_SOCRATIC
        assert "السببية" in SYSTEM_PROMPT_SOCRATIC

    def test_triple_analysis_in_socratic(self):
        from services.socratic_tutor import SYSTEM_PROMPT_SOCRATIC
        assert "التحليل الثلاثي" in SYSTEM_PROMPT_SOCRATIC or "الثلاثي" in SYSTEM_PROMPT_SOCRATIC


# ── Remediation nouveaux verbes ──────────────────


class TestRemediationNewVerbs:
    """Verifie que extract et prove-experimentally sont dans REMEDIATION_MATRIX."""

    def test_extract_in_remediation(self):
        import os
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from services.remediation_service import get_remediation
        assert get_remediation("extract", "methodology_error") is not None
        assert get_remediation("extract", "scientific_error") is not None

    def test_prove_experimentally_in_remediation(self):
        import os
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from services.remediation_service import get_remediation
        assert get_remediation("prove-experimentally", "methodology_error") is not None
        assert get_remediation("prove-experimentally", "scientific_error") is not None
