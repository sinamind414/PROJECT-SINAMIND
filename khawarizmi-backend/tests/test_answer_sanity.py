"""
tests/test_answer_sanity.py — 25 tests pour le filtre anti-charabia.

Couvre :
- Les 5 charabias observés en production (ERRETREZR, etc.)
- Réponses vides et whitespace
- Réponses trop courtes
- Réponses non-arabes (latin pur)
- Réponses arabes légitimes (courtes et longues)
- Cas limites (mixte arabe/latin, chiffres, ponctuation)
"""


from services.answer_sanity import check_answer_sanity

# ── Les 5 charabias de production ─────────────────


class TestProductionGibberish:
    """Les 5 réponses charabias observées sur le site."""

    def test_gibberish_erretrezr(self):
        valid, code, _ = check_answer_sanity("ERRETREZR")
        assert not valid
        assert code in ("gibberish", "not_arabic")

    def test_gibberish_erezrezt(self):
        valid, code, _ = check_answer_sanity("EREZREZT")
        assert not valid
        assert code in ("gibberish", "not_arabic")

    def test_gibberish_kjybyutiujpo(self):
        valid, code, _ = check_answer_sanity("?KJ YBYUTIUJPO?K?PO")
        assert not valid
        assert code in ("gibberish", "not_arabic")

    def test_gibberish_bvcggcvuvuy(self):
        valid, code, _ = check_answer_sanity("BVCGGCVUVUY")
        assert not valid
        assert code in ("gibberish", "not_arabic")

    def test_gibberish_zezreztert(self):
        valid, code, _ = check_answer_sanity("ZEZREZTERT")
        assert not valid
        assert code in ("gibberish", "not_arabic")


# ── Réponses vides et trop courtes ────────────────


class TestEmptyAndShort:
    """Réponses vides, whitespace, et trop courtes."""

    def test_empty_string(self):
        valid, code, msg = check_answer_sanity("")
        assert not valid
        assert code == "empty"
        assert msg  # message non vide

    def test_none_like_empty(self):
        valid, code, _ = check_answer_sanity("   ")
        assert not valid
        assert code == "empty"

    def test_only_newlines(self):
        valid, code, _ = check_answer_sanity("\n\n\n")
        assert not valid
        assert code == "empty"

    def test_too_short_arabic(self):
        valid, code, _ = check_answer_sanity("مرحبا")
        assert not valid
        assert code == "too_short"

    def test_too_short_3_chars(self):
        valid, code, _ = check_answer_sanity("abc")
        assert not valid
        # Peut être too_short ou not_arabic, les deux sont acceptables
        assert code in ("too_short", "not_arabic")

    def test_single_word(self):
        valid, code, _ = check_answer_sanity("نعم")
        assert not valid
        assert code in ("too_short", "empty")


# ── Réponses non-arabes ──────────────────────────


class TestNotArabic:
    """Réponses en latin pur ou avec très peu d'arabe."""

    def test_english_sentence(self):
        valid, code, _ = check_answer_sanity("This is a normal English sentence about biology.")
        assert not valid
        assert code == "not_arabic"

    def test_french_sentence(self):
        valid, code, _ = check_answer_sanity("Les cellules sont les unités de base du vivant.")
        assert not valid
        assert code == "not_arabic"

    def test_numbers_only(self):
        valid, code, _ = check_answer_sanity("12345678901234567890")
        assert not valid
        assert code in ("not_arabic", "gibberish")


# ── Réponses arabes légitimes ────────────────────


class TestLegitimateArabic:
    """Réponses arabes qui doivent passer le filtre."""

    def test_short_arabic_answer(self):
        valid, code, _ = check_answer_sanity("نلاحظ من خلال الوثيقة أن نسبة الغلوكوز تزداد")
        assert valid
        assert code == "ok"

    def test_medium_arabic_answer(self):
        answer = "من خلال تحليل الوثيقة نلاحظ أن نسبة الغلوكوز في الدم تزداد بعد تناول وجبة غنية بالسكريات ثم تنخفض تدريجياً"
        valid, code, _ = check_answer_sanity(answer)
        assert valid
        assert code == "ok"

    def test_long_arabic_answer(self):
        answer = (
            "نلاحظ من خلال الوثيقة أن نسبة الغلوكوز في الدم تزداد بعد تناول وجبة غنية "
            "بالسكريات حيث ترتفع من 0.8 غ/ل إلى 1.4 غ/ل خلال الساعة الأولى. "
            "ثم تنخفض تدريجياً لتعود إلى قيمتها الطبيعية بعد حوالي 3 ساعات. "
            "هذا يدل على وجود آلية تنظيمية تعيد نسبة السكر إلى وضعها الطبيعي."
        )
        valid, code, _ = check_answer_sanity(answer)
        assert valid
        assert code == "ok"

    def test_arabic_with_numbers(self):
        answer = "نلاحظ أن القيمة تزداد من 0.8 إلى 1.4 غ/ل خلال المرحلة الأولى"
        valid, code, _ = check_answer_sanity(answer)
        assert valid
        assert code == "ok"


# ── Cas limites ──────────────────────────────────


class TestEdgeCases:
    """Cas limites : mixte arabe/latin, ponctuation, etc."""

    def test_arabic_with_some_latin(self):
        """Arabe avec termes scientifiques en latin (ADN, ARN, etc.) — valide."""
        answer = "يتم نسخ الـ ADN إلى ARN messager في النواة ثم يتم ترجمته في الريبوزومات"
        valid, code, _ = check_answer_sanity(answer)
        assert valid
        assert code == "ok"

    def test_repeated_arabic_letter(self):
        """Lettre arabe répétée — charabia."""
        valid, code, _ = check_answer_sanity("ااااااااااااااااا")
        assert not valid
        assert code in ("gibberish", "repeated_chars")

    def test_punctuation_only(self):
        """Juste de la ponctuation."""
        valid, code, _ = check_answer_sanity("...!!! ???")
        assert not valid
        assert code in ("too_short", "not_arabic", "gibberish")

    def test_return_tuple_structure(self):
        """Vérifie que le retour est un tuple de 3 éléments."""
        result = check_answer_sanity("test")
        assert isinstance(result, tuple)
        assert len(result) == 3
        valid, code, msg = result
        assert isinstance(valid, bool)
        assert isinstance(code, str)
        assert isinstance(msg, str)
