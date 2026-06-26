"""Tests Flashcards Méthodologiques — Semaine 5"""

from methodology.methodology_flashcards import (
    get_all_methodology_flashcards,
    get_flashcards_by_category,
    VERB_FLASHCARDS,
    ERROR_FLASHCARDS,
    STRUCTURE_FLASHCARDS,
)


class TestFlashcardCounts:
    def test_total_cards(self):
        cards = get_all_methodology_flashcards()
        assert len(cards) == 65  # 30 verbes + 20 erreurs + 15 structure

    def test_verb_cards_count(self):
        assert len(VERB_FLASHCARDS) == 30

    def test_error_cards_count(self):
        assert len(ERROR_FLASHCARDS) == 20

    def test_structure_cards_count(self):
        assert len(STRUCTURE_FLASHCARDS) == 15


class TestFlashcardStructure:
    def test_all_have_required_fields(self):
        for card in get_all_methodology_flashcards():
            assert "id" in card
            assert "front" in card
            assert "back" in card
            assert "category" in card
            assert "difficulty" in card

    def test_unique_ids(self):
        ids = [c["id"] for c in get_all_methodology_flashcards()]
        assert len(ids) == len(set(ids))


class TestFlashcardCategories:
    def test_get_by_verb_category(self):
        cards = get_flashcards_by_category("verbe")
        assert len(cards) == 30

    def test_get_by_error_category(self):
        cards = get_flashcards_by_category("erreur")
        assert len(cards) == 20

    def test_get_by_structure_category(self):
        cards = get_flashcards_by_category("structure")
        assert len(cards) == 15

    def test_unknown_category(self):
        cards = get_flashcards_by_category("unknown")
        assert len(cards) == 0


class TestSeedScript:
    def test_seed_runs(self):
        from scripts.seed_methodology_flashcards import seed
        cards = seed()
        assert len(cards) == 65


class TestRoute:
    def test_router_imports(self):
        from routes.methodology_flashcards import router
        assert "/api/flashcards/methodology" in str(router.prefix)
