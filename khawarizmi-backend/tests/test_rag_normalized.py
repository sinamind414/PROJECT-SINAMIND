"""tests/test_rag_normalized.py — RAG sur contenu normalisé (audit O4).

- _extract_keywords retourne des keywords NORMALISÉS (variantes égalisées)
- keyword_rag_search matche content_norm via COALESCE(content_norm, content)
- Test d'intégration SQLite réel : une requête avec des variantes
  (« الحرارة المثلى ») retrouve un chunk écrit avec les formes canoniques
  (« حرارة مثلى ») — le cas d'usage réel (élève écrit avec tashkîl/variantes,
  le livre est en forme canonique).
"""

from __future__ import annotations

import os
import tempfile

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from services.arabic import ar_normalize
from services.rag_service import _extract_keywords, keyword_rag_search

# ⚠️ database.py est importé (via conftest) : le hook @compiles(TextClause,
# "sqlite") transforme ILIKE → LIKE pour SQLite — requis pour ce test.


class TestExtractKeywordsNormalized:
    def test_keywords_are_normalized(self):
        """Les mots-clés sont normalisés (variantes arabes égalisées)."""
        kws = _extract_keywords("اشرح تأثير الحرارة المثلى على الإنزيم")
        assert all(ar_normalize(k) == k for k in kws), (
            f"keywords non normalisés : {kws}"
        )
        # 'المثلى' → 'المثلي' (ى→ي)
        assert "المثلي" in kws

    def test_stop_words_normalized_filtered(self):
        """'على' normalisé en 'علي' reste filtré (stop words normalisés)."""
        kws = _extract_keywords("ما هو دور الإنزيم على الركيزة")
        assert "علي" not in kws
        assert "دور" in kws

    def test_hamza_variants_unified(self):
        kws = _extract_keywords("أين تحدث الترجمة في الهيولى")
        assert "الهيولي" in kws  # الهيولى → الهيولي (ى→ي)


@pytest.fixture
async def rag_db():
    """Base SQLite temporaire avec la table rag_chunks (content_norm)."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
    async with engine.begin() as conn:
        await conn.exec_driver_sql(
            """
            CREATE TABLE rag_chunks (
                id INTEGER PRIMARY KEY,
                content TEXT NOT NULL,
                content_norm TEXT,
                source TEXT,
                chapitre TEXT,
                importance REAL DEFAULT 1.0,
                chunk_index INTEGER DEFAULT 0
            )
            """
        )
        chunks = [
            # Forme canonique (livre) — content_norm = ar_normalize
            ("تصل سرعة التفاعل إلى قيمتها العظمى عند درجة الحرارة المثلى",
             "enzyme", "ch1", 2),
            ("الترجمة تتم في الهيولى بمساعدة الريبوزوم والرنا الناقل",
             "proteines", "ch2", 1),
            ("الجملة الإنجليزية the enzyme works at optimal temperature",
             "enzyme", "ch3", 0),
        ]
        for i, (content, source, chap, idx) in enumerate(chunks):
            await conn.exec_driver_sql(
                "INSERT INTO rag_chunks (id, content, content_norm, source, chapitre, chunk_index) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (i + 1, content, ar_normalize(content), source, chap, idx),
            )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield session_factory
    finally:
        await engine.dispose()
        os.unlink(path)


class TestKeywordRagSearchNormalized:
    @pytest.mark.asyncio
    async def test_variant_query_matches_canonical_chunk(self, rag_db):
        """Acceptation O4 : « الحرارة المثلى » (variantes) retrouve le chunk
        écrit « ...الحرارة المثلى » (formes identiques ici) — et surtout le
        matching passe par content_norm (COALESCE)."""
        async with rag_db() as db:
            results = await keyword_rag_search(
                db, "درجة الحرارة المثلى", chapter=None, limit=8
            )
        assert results, "aucun résultat pour 'درجة الحرارة المثلى'"
        assert any("الحرارة المثلى" in r["content"] for r in results)

    @pytest.mark.asyncio
    async def test_tashkeel_variants_match(self, rag_db):
        """Requête avec tashkîl + variantes : « الحَرارةُ المُثْلى » matche le
        chunk canonique via content_norm (les diacritiques sont retirés)."""
        async with rag_db() as db:
            results = await keyword_rag_search(
                db, "الحَرارةُ المُثْلى", chapter=None, limit=8
            )
        assert any("الحرارة المثلى" in r["content"] for r in results)

    @pytest.mark.asyncio
    async def test_chapter_filter_still_works(self, rag_db):
        async with rag_db() as db:
            results = await keyword_rag_search(
                db, "درجة الحرارة المثلى", chapter="ch1", limit=8
            )
        assert results
        assert all(r["chapter"] == "ch1" for r in results)

    @pytest.mark.asyncio
    async def test_no_match_returns_empty(self, rag_db):
        async with rag_db() as db:
            results = await keyword_rag_search(
                db, "qqxxzzzyyy", chapter=None, limit=8
            )
        assert results == []
