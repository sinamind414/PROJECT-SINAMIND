"""G16 — contrat N1–N10 de normalize_arabic (liste fermée)."""

from services.arabic import ar_normalize, normalize_arabic


class TestContractN1ToN10:
    def test_n1_nfkc_compat(self):
        lig = "ﻻ"
        assert "لا" in normalize_arabic(lig) or normalize_arabic(lig) == normalize_arabic("لا")

    def test_n2_zwj_zwnj_kashida(self):
        assert "\u200d" not in normalize_arabic("م\u200dثال")
        assert "\u200c" not in normalize_arabic("م\u200cثال")
        assert "ـ" not in normalize_arabic("مـــــثال")

    def test_n3_diacritics(self):
        assert normalize_arabic("تَحْلِيل") == normalize_arabic("تحليل")
        assert "\u0670" not in normalize_arabic("ا\u0670")

    def test_n4_alef(self):
        for v in ("أ", "إ", "آ", "ٱ"):
            assert normalize_arabic(f"{v}نزيم") == normalize_arabic("انزيم")

    def test_n5_alef_maksura(self):
        assert normalize_arabic("على") == normalize_arabic("علي")

    def test_n6_yeh_waw_hamza(self):
        # ضوئي = ض+و+ئ+ي → ضويي (pas de fusion يي : hors liste N1–N10)
        assert normalize_arabic("ضوئي") == normalize_arabic("ضويي")
        assert normalize_arabic("مؤثر") == normalize_arabic("موثر")

    def test_n7_teh_marbuta(self):
        assert normalize_arabic("الطاقة") == normalize_arabic("الطاقه")
        assert normalize_arabic("الطاقة").endswith("ه") or "طاقه" in normalize_arabic("الطاقة")

    def test_n8_indian_digits(self):
        assert "38" in normalize_arabic("٣٨ ATP")
        assert "38" in normalize_arabic("۳۸")

    def test_n8b_arabic_decimal_and_percent(self):
        assert "2.5" in normalize_arabic("٢٫٥")
        assert "," not in normalize_arabic("٢٫٥")
        assert "36%" in normalize_arabic("٣٦٪") or "36" in normalize_arabic("٣٦٪")

    def test_n9_chemistry_co2(self):
        assert "co2" in normalize_arabic("CO₂")
        assert "co2" in normalize_arabic("CO2")
        assert "co2" in normalize_arabic("co₂")

    def test_n10_spaces_lower(self):
        assert normalize_arabic("  ATP   et  ARN  ") == "atp et arn"

    def test_idempotent(self):
        samples = [
            "ألحرارةُ المثلى لإنزيمٍ هي ٣٧°",
            "CO₂ و O₂",
            "ضوئي",
            "مـــــثال",
        ]
        for s in samples:
            once = normalize_arabic(s)
            assert once == normalize_arabic(once)

    def test_alias(self):
        assert normalize_arabic("الحرارة") == ar_normalize("الحرارة")

    def test_existing_golden_unchanged(self):
        assert ar_normalize("الحرارة المثلى") == "الحراره المثلي"
        assert ar_normalize("ADN et ARN") == "adn et arn"
        assert ar_normalize("جزيئة ADN في النواة") == "جزييه adn في النواه"
