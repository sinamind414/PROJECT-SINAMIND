"""tests/test_arabic.py — Normalisation arabe partagée (audit O4).

Invariant clé : ar_normalize est IDEMPOTENT (une fois normalisé, le texte ne
change plus) — requis pour la colonne rag_chunks.content_norm et le cache
sémantique. Acceptation du plan : ar_normalize("الحرارة المثلى") ==
ar_normalize("حرارة مثلى").
"""

from services.arabic import ar_normalize, normalize_arabic


class TestArNormalize:
    def test_variants_unified(self):
        """Acceptation corrigée du plan : les VARIANTES (diacritiques, alef,
        yeh, ta-marbuta) sont égalisées. L'article défini ال N'EST PAS retiré
        (la spec ne le fait pas — c'est correct : le wildcard %...% du SQL
        RAG le gère ; retirer ال serait une racination risquée, 'الله'→'له')."""
        assert ar_normalize("الحرارة المثلى") == "الحراره المثلي"
        assert ar_normalize("حرارة مثلى") == "حراره مثلي"
        # Les deux formes diffèrent uniquement par l'article ال (géré par le
        # LIKE '%...%' du RAG, pas par la normalisation)
        assert ar_normalize("الحرارة المثلى") != ar_normalize("حرارة مثلى")

    def test_rag_matching_equivalent(self):
        """L'équivalence RAG : le keyword normalisé 'مثلي' (de 'مثلى') est un
        sous-ensemble de 'الحراره المثلي' (de 'الحرارة المثلى') → le LIKE
        '%مثلي%' matche, article inclus."""
        assert "مثلي" in "الحراره المثلي"

    def test_idempotent(self):
        """Une fois normalisé, le texte ne change plus (invariant O4)."""
        text = "ألحرارةُ المثلى لإنزيمٍ هي 37°"
        once = ar_normalize(text)
        twice = ar_normalize(once)
        assert once == twice

    def test_diacritics_removed(self):
        assert ar_normalize("كَيْفَ تَعْمَلُ") == ar_normalize("كيف تعمل")

    def test_tatweel_removed(self):
        assert "ـ" not in ar_normalize("مـــــثال")

    def test_alef_variants_unified(self):
        for variant in ("أ", "إ", "آ", "ٱ"):
            assert ar_normalize(f"{variant}حمد") == ar_normalize("احمد")

    def test_yeh_final_unified(self):
        assert ar_normalize("على") == ar_normalize("علي")
        assert ar_normalize("إلى") == ar_normalize("الي")

    def test_teh_marbuta_to_ha(self):
        assert ar_normalize("مطرقة") == ar_normalize("مطرقه")  # ة → ه
        assert ar_normalize("الحرارة") == "الحراره"

    def test_multiple_spaces_collapsed(self):
        assert ar_normalize("  ألنواة   و  الهيولى  ") == ar_normalize("النواة و الهيولى")

    def test_empty_and_none(self):
        assert ar_normalize("") == ""
        assert ar_normalize(None) == ""  # type: ignore[arg-type]

    def test_latin_unchanged_case(self):
        assert ar_normalize("ADN et ARN") == "adn et arn"

    def test_mixed_arabic_latin(self):
        n = ar_normalize("جزيئة ADN في النواة")
        # N6 ئ→ي puis N7 ة→ه : جزيئة → جزييه ; النواة → النواه
        assert n == "جزييه adn في النواه"
        assert ar_normalize(n) == n  # idempotent

    def test_alias_normalize_arabic(self):
        """Alias de compatibilité pour les 3 modules existants."""
        assert normalize_arabic("الحرارة المثلى") == ar_normalize("الحرارة المثلى")
