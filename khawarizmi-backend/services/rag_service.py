import logging
import re

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("khawarizmi.rag")

STOP_WORDS_RAG = {
    "ما", "هو", "هي", "في", "من", "إلى", "على", "عن", "مع", "هذا", "هذه", "التي", "الذي", "كيف", "لماذا", "ماذا",
    "اشرح", "حدد", "صف", "حلل", "قارن", "استنتج", "اذكر", "عرف",
    "le", "la", "les", "un", "une", "des", "de", "du", "et", "ou", "dans", "sur", "pour", "par", "avec",
    "the", "is", "what", "how", "why", "where", "explain", "define",
}


def _extract_keywords(message: str, limit: int = 4) -> list[str]:
    tokens = re.findall(r"[\u0600-\u06FF\u0750-\u077F\w]+", message.lower())
    keywords = []
    seen = set()
    for token in tokens:
        if len(token) <= 2 or token in STOP_WORDS_RAG or token in seen:
            continue
        seen.add(token)
        keywords.append(token)
        if len(keywords) >= limit:
            break
    return keywords


async def vector_rag_search(
    db: AsyncSession,
    message: str,
    chapter: str | None,
    limit: int = 8,
) -> list[dict]:
    try:
        from services.embedder import embedder

        query_vector = embedder.encode([message])[0]
        query_emb = str(query_vector.tolist())
    except Exception as e:
        logger.warning(f"Embedding échec, fallback keyword only: {e}")
        return []

    try:
        if chapter:
            result = await db.execute(
                text("""
                    SELECT content, source, chapitre AS chapter,
                           1 - (embedding <=> CAST(:query_emb AS vector)) AS similarity
                    FROM rag_chunks
                    WHERE LOWER(chapitre) LIKE LOWER(:chapter)
                    ORDER BY embedding <=> CAST(:query_emb AS vector)
                    LIMIT :lim
                """),
                {"chapter": f"%{chapter}%", "query_emb": query_emb, "lim": limit},
            )
        else:
            result = await db.execute(
                text("""
                    SELECT content, source, chapitre AS chapter,
                           1 - (embedding <=> CAST(:query_emb AS vector)) AS similarity
                    FROM rag_chunks
                    ORDER BY embedding <=> CAST(:query_emb AS vector)
                    LIMIT :lim
                """),
                {"query_emb": query_emb, "lim": limit},
            )
        return [
            {
                "content": r._mapping["content"][:420],
                "source": r._mapping["source"],
                "chapter": r._mapping["chapter"],
                "similarity": float(r._mapping["similarity"]) if r._mapping["similarity"] else 0.0,
                "retrieval": "vector",
            }
            for r in result.fetchall()
        ]
    except Exception as e:
        logger.warning(f"Vector RAG search échec : {e}")
        return []


async def keyword_rag_search(
    db: AsyncSession,
    message: str,
    chapter: str | None,
    limit: int = 8,
) -> list[dict]:
    try:
        keywords = _extract_keywords(message, limit=4)
        if not keywords:
            return []

        if chapter:
            result = await db.execute(
                text("""
                    SELECT content, source, chapitre AS chapter, importance
                    FROM rag_chunks
                    WHERE LOWER(chapitre) LIKE LOWER(:chapter)
                      AND LOWER(content) ILIKE ANY(:keywords)
                    ORDER BY chunk_index
                    LIMIT :lim
                """),
                {"chapter": f"%{chapter}%", "keywords": [f"%{k}%" for k in keywords], "lim": limit},
            )
        else:
            result = await db.execute(
                text("""
                    SELECT content, source, chapitre AS chapter, importance
                    FROM rag_chunks
                    WHERE LOWER(content) ILIKE ANY(:keywords)
                    ORDER BY chunk_index
                    LIMIT :lim
                """),
                {"keywords": [f"%{k}%" for k in keywords], "lim": limit},
            )

        importance_scores = {"critique": 0.95, "haute": 0.80, "moyenne": 0.60}
        return [
            {
                "content": r._mapping["content"][:420],
                "source": r._mapping["source"],
                "chapter": r._mapping["chapter"],
                "similarity": importance_scores.get(r._mapping.get("importance", "moyenne"), 0.60),
                "retrieval": "keyword",
            }
            for r in result.fetchall()
        ]
    except Exception as e:
        logger.warning(f"Keyword RAG search échec : {e}")
        return []


def merge_chunks(
    vector_chunks: list[dict],
    keyword_chunks: list[dict],
) -> list[dict]:
    seen: dict[str, dict] = {}

    for c in vector_chunks:
        key = (c.get("source", ""), c.get("content", "")[:160])
        if key not in seen:
            seen[key] = c

    for c in keyword_chunks:
        key = (c.get("source", ""), c.get("content", "")[:160])
        if key in seen:
            seen[key]["retrieval"] = "hybrid"
        else:
            seen[key] = c

    return list(seen.values())


async def rag_search(
    db: AsyncSession,
    message: str,
    chapter: str | None = None,
    limit: int = 3,
) -> list[dict]:
    vector_chunks = await vector_rag_search(db, message, chapter, limit=max(limit * 2, 6))
    keyword_chunks = await keyword_rag_search(db, message, chapter, limit=max(limit * 2, 6))
    candidates = merge_chunks(vector_chunks, keyword_chunks)

    if not candidates:
        return []

    try:
        from services.reranker import rerank

        reranked = rerank(message, candidates, top_k=limit)
    except Exception as e:
        logger.warning(f"Reranker indisponible, fallback tri par similarité : {e}")
        reranked = sorted(candidates, key=lambda c: c.get("similarity", 0), reverse=True)[:limit]

    return reranked


def format_rag_context(chunks: list[dict]) -> str:
    if not chunks:
        return ""
    parts = []
    for c in chunks:
        src = c.get("source", "manuel")
        chap = c.get("chapter", "")
        excerpt = c.get("content", "")[:220].strip()
        parts.append(f"[{src}/{chap}] {excerpt}")
    return "\n\n".join(parts)


def source_cards(chunks: list[dict]) -> list[dict]:
    seen = set()
    sources = []
    for c in chunks:
        key = (c.get("source", ""), c.get("chapter", ""))
        if key not in seen:
            seen.add(key)
            sources.append({
                "source": c.get("source", "manuel_svt"),
                "chapter": c.get("chapter"),
                "excerpt": c["content"][:200],
            })
    return sources
