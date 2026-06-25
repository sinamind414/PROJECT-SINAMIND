"""Re-ranking hybride pour le moteur RAG.

Le bi-encoder (pgvector + MiniLM) est rapide mais imprécis sur les termes
techniques. Le re-ranking applique un second filtre sur les top-K chunks
récupérés par pgvector pour améliorer la Precision@K.

Pipeline :
  1. pgvector récupère 20 chunks (bi-encoder, rapide)
  2. reranker.py re-score ces 20 chunks avec 3 signaux :
     a) Similarité cosinus (déjà calculée par pgvector) — poids 0.4
     b) Score BM25 (fréquence des termes de la question dans le chunk) — poids 0.3
     c) Couverture des mots-clés (mots importants de la question présents) — poids 0.3
  3. On garde les 5 meilleurs chunks après re-ranking

Gain attendu : +30% de précision sur les termes scientifiques techniques
(ARN polymérase, ATP, etc.) que le bi-encoder manque parfois.
"""

import logging
import math
import re

logger = logging.getLogger("khawarizmi.reranker")

# Poids des signaux
W_COSINE = 0.4
W_BM25 = 0.3
W_KEYWORD = 0.3

# Paramètres BM25
BM25_K1 = 1.5
BM25_B = 0.75

# Stop-words arabes + français (mots fréquents à ignorer)
STOP_WORDS = {
    # Arabe
    "ما",
    "هو",
    "هي",
    "في",
    "من",
    "إلى",
    "على",
    "عن",
    "مع",
    "هذا",
    "هذه",
    "التي",
    "الذي",
    "كان",
    "كانت",
    "قد",
    "لقد",
    "بين",
    "كل",
    "بعض",
    "أو",
    "ثم",
    "و",
    "لا",
    "نعم",
    "كيف",
    "أين",
    "متى",
    "لماذا",
    "ماذا",
    "اشرح",
    "حدد",
    "صف",
    "حلل",
    "قارن",
    "استنتج",
    "اذكر",
    "عرف",
    # Français
    "le",
    "la",
    "les",
    "un",
    "une",
    "des",
    "de",
    "du",
    "et",
    "ou",
    "mais",
    "dans",
    "sur",
    "pour",
    "par",
    "avec",
    "sans",
    "ce",
    "cette",
    "ces",
    "qui",
    "que",
    "quoi",
    "dont",
    "où",
    "est",
    "sont",
    "a",
    "the",
    "is",
    "what",
    "how",
    "why",
    "where",
    "explain",
    "define",
}


def _tokenize(text: str) -> list[str]:
    """Tokenisation simple : split sur espaces et ponctuation, lowercase."""
    # Supprimer la ponctuation et splitter
    tokens = re.findall(r"[\u0600-\u06FF\u0750-\u077F\w]+", text.lower())
    return [t for t in tokens if len(t) > 1 and t not in STOP_WORDS]


def _bm25_score(
    query_tokens: list[str], chunk_text: str, avg_doc_len: float, doc_freq: dict[str, int], total_docs: int
) -> float:
    """Score BM25 pour un chunk donné.

    BM25 = sum over query terms of:
        IDF(q) * (f(q,d) * (k1+1)) / (f(q,d) + k1 * (1 - b + b * |d|/avgdl))
    """
    chunk_tokens = _tokenize(chunk_text)
    doc_len = len(chunk_tokens)
    if doc_len == 0:
        return 0.0

    # Fréquence des termes dans le chunk
    term_freq = {}
    for t in chunk_tokens:
        term_freq[t] = term_freq.get(t, 0) + 1

    score = 0.0
    for q_term in set(query_tokens):
        if q_term not in term_freq:
            continue

        # IDF (Inverse Document Frequency)
        df = doc_freq.get(q_term, 0)
        if df == 0:
            continue
        idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1)

        # TF normalisé
        f = term_freq[q_term]
        tf_norm = (f * (BM25_K1 + 1)) / (f + BM25_K1 * (1 - BM25_B + BM25_B * doc_len / max(avg_doc_len, 1)))

        score += idf * tf_norm

    return score


def _keyword_coverage_score(query_tokens: list[str], chunk_text: str) -> float:
    """Score de couverture : % des mots de la question présents dans le chunk."""
    if not query_tokens:
        return 0.0
    chunk_lower = chunk_text.lower()
    found = sum(1 for t in query_tokens if t in chunk_lower)
    return found / len(query_tokens)


def rerank(
    query: str,
    chunks: list[dict],
    top_k: int = 5,
) -> list[dict]:
    """Re-ranke les chunks récupérés par pgvector.

    Args:
        query: question de l'élève
        chunks: liste de chunks avec 'content', 'source', 'similarity' (de pgvector)
        top_k: nombre de chunks à garder après re-ranking

    Returns:
        Liste re-rankée des top_k chunks avec score_rerank ajouté
    """
    if not chunks:
        return []

    query_tokens = _tokenize(query)
    if not query_tokens:
        # Fallback : garder l'ordre pgvector
        return chunks[:top_k]

    # Calculer les statistiques BM25 sur ce batch de chunks
    all_chunk_tokens = [_tokenize(c.get("content", "")) for c in chunks]
    avg_doc_len = sum(len(t) for t in all_chunk_tokens) / len(all_chunk_tokens) if all_chunk_tokens else 0

    # Document frequency pour chaque terme de la requête
    doc_freq = {}
    for q_term in set(query_tokens):
        doc_freq[q_term] = sum(1 for tokens in all_chunk_tokens if q_term in tokens)

    total_docs = len(chunks)

    # Normaliser les scores cosinus (pgvector) sur [0, 1]
    cosine_scores = [c.get("similarity", 0) for c in chunks]
    max_cos = max(cosine_scores) if cosine_scores else 1
    min_cos = min(cosine_scores) if cosine_scores else 0
    cos_range = max(max_cos - min_cos, 1e-9)

    # Calculer le score de re-ranking pour chaque chunk
    scored_chunks = []
    for i, chunk in enumerate(chunks):
        # a) Cosinus normalisé
        cos_norm = (cosine_scores[i] - min_cos) / cos_range

        # b) BM25
        bm25 = _bm25_score(query_tokens, chunk.get("content", ""), avg_doc_len, doc_freq, total_docs)
        # Normaliser BM25 sur [0, 1]
        max_bm25 = max(
            [_bm25_score(query_tokens, c.get("content", ""), avg_doc_len, doc_freq, total_docs) for c in chunks] or [1]
        )
        bm25_norm = bm25 / max(max_bm25, 1e-9)

        # c) Couverture mots-clés
        kw_cov = _keyword_coverage_score(query_tokens, chunk.get("content", ""))

        # Score combiné
        final_score = W_COSINE * cos_norm + W_BM25 * bm25_norm + W_KEYWORD * kw_cov

        chunk_copy = {**chunk}
        chunk_copy["score_rerank"] = round(final_score, 4)
        chunk_copy["score_cosine"] = round(cos_norm, 4)
        chunk_copy["score_bm25"] = round(bm25_norm, 4)
        chunk_copy["score_keyword"] = round(kw_cov, 4)
        scored_chunks.append(chunk_copy)

    # Trier par score de re-ranking décroissant
    scored_chunks.sort(key=lambda x: x["score_rerank"], reverse=True)

    logger.debug(
        f"RERANK | query='{query[:40]}...' | "
        f"input={len(chunks)} output={min(top_k, len(scored_chunks))} | "
        f"best_score={scored_chunks[0]['score_rerank'] if scored_chunks else 0}"
    )

    return scored_chunks[:top_k]
