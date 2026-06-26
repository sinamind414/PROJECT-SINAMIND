"""Tests Mindmap Methodologique — Semaine 7"""

import pytest
from methodology.mindmap_methodology import (
    get_static_mindmap,
    get_all_static_mindmaps,
    generate_dynamic_mindmap,
    STATIC_MINDMAPS,
)


class TestStaticMindmaps:
    def test_count(self):
        assert len(STATIC_MINDMAPS) == 6

    def test_get_all_returns_list(self):
        maps = get_all_static_mindmaps()
        assert len(maps) == 6

    def test_get_structure_mindmap(self):
        mm = get_static_mindmap("structure_texte_scientifique")
        assert mm is not None
        assert mm["id"] == "mm_structure"
        assert len(mm["root"]["children"]) == 3  # intro, dev, conc

    def test_get_verbe_wadhah(self):
        mm = get_static_mindmap("verbe_wadhah")
        assert mm is not None
        assert "وضّح" in mm["root"]["label"]

    def test_get_verbe_athbat(self):
        mm = get_static_mindmap("verbe_athbat")
        assert mm is not None

    def test_get_verbe_barrir(self):
        mm = get_static_mindmap("verbe_barrir")
        assert mm is not None

    def test_get_verbe_fassar(self):
        mm = get_static_mindmap("verbe_fassar")
        assert mm is not None

    def test_get_verbe_naqish(self):
        mm = get_static_mindmap("verbe_naqish")
        assert mm is not None

    def test_get_unknown(self):
        mm = get_static_mindmap("unknown")
        assert mm is None


class TestDynamicMindmap:
    def test_wadhah(self):
        mm = generate_dynamic_mindmap("وضّح في نص علمي")
        assert len(mm["root"]["children"]) == 3
        assert mm["generated"] is True

    def test_athbat(self):
        mm = generate_dynamic_mindmap("أثبت")
        assert len(mm["root"]["children"]) == 3

    def test_barrir(self):
        mm = generate_dynamic_mindmap("برّر")
        assert len(mm["root"]["children"]) == 2

    def test_fassar(self):
        mm = generate_dynamic_mindmap("فسر")
        assert len(mm["root"]["children"]) == 2

    def test_naqish(self):
        mm = generate_dynamic_mindmap("ناقش")
        assert len(mm["root"]["children"]) == 3

    def test_unknown_verb(self):
        mm = generate_dynamic_mindmap("unknown_verb")
        assert len(mm["root"]["children"]) == 2  # fallback

    def test_all_mindmaps_have_unique_ids(self):
        ids = [mm["id"] for mm in STATIC_MINDMAPS.values()]
        assert len(ids) == len(set(ids))


class TestEndpoint:
    def test_router_imports(self):
        from routes.mindmap_methodology import router
        assert "/api/mindmap/methodology" in str(router.prefix)
