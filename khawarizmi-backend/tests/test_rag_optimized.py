#!/usr/bin/env python3
"""
Test du moteur RAG optimisé — 6 cas BAC SVT
Teste les composants purs sans DB : keyword extraction, reranker, format.
"""
import json
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.rag_service import _extract_keywords, merge_chunks, format_rag_context, source_cards, rag_cache_stats
from services.reranker import rerank, _tokenize, _keyword_coverage_score

# ── Mock chunks (simulent des résultats DB) ────────────────
MOCK_VECTOR_CHUNKS = [
    {
        "content": "Les enzymes sont des protéines qui catalysent les réactions biochimiques. Elles sont spécifiques à substrat et fonctionnent à pH optimal. L'amylase salivaire hydrolyse l'amidon en maltose.",
        "source": "manuel_svt",
        "chapter": "Activité enzymatique",
        "similarity": 0.92,
        "retrieval": "vector",
    },
    {
        "content": "La transcription est le processus de copie de l'ADN en ARNm par l'ARN polymérase. Elle se déroule dans le noyau. Le promoteur est la zone de départ.",
        "source": "manuel_svt",
        "chapter": "Transcription",
        "similarity": 0.78,
        "retrieval": "vector",
    },
    {
        "content": "Le système immunitaire inné comprend les barrières physiques, les cellules phagocytaires et les protéines du complément. Il est non spécifique.",
        "source": "manuel_svt",
        "chapter": "Immunologie",
        "similarity": 0.65,
        "retrieval": "vector",
    },
    {
        "content": "La photosynthèse est le processus par lequel les plantes convertissent la lumière en énergie chimique. Elle se déroule dans les chloroplastes.",
        "source": "manuel_svt",
        "chapter": "Photosynthèse",
        "similarity": 0.55,
        "retrieval": "vector",
    },
    {
        "content": "Les protéines sont des polymères d'acides aminés. Leur structure primaire est la séquence d'acides aminés. La structure tertiaire détermine la fonction.",
        "source": "manuel_svt",
        "chapter": "Structure des protéines",
        "similarity": 0.88,
        "retrieval": "vector",
    },
]

MOCK_KEYWORD_CHUNKS = [
    {
        "content": "Les enzymes sont des biocatalyseurs protéiques. Chaque enzyme est spécifique à un substrat. Le modèle serrure-clé explique cette spécificité.",
        "source": "annales_2024",
        "chapter": "Activité enzymatique",
        "similarity": 0.95,
        "retrieval": "keyword",
    },
    {
        "content": "L'ARN polymérase est l'enzyme de la transcription. Elle se fixe sur le promoteur et synthétise l'ARNm complémentaire au brin matrice.",
        "source": "manuel_svt",
        "chapter": "Transcription",
        "similarity": 0.80,
        "retrieval": "keyword",
    },
    {
        "content": "Dans le cadre de l'analyse d'un document biologique, il faut d'abord identifier le type de document, puis les données expérimentales, enfin formuler une hypothèse.",
        "source": "methodologie",
        "chapter": "Méthodologie",
        "similarity": 0.70,
        "retrieval": "keyword",
    },
]

# ── Cas de test ──────────────────────────────────────────
TEST_CASES = [
    {
        "name": "Cas 1 — Définition simple",
        "query": "ما هو دور الأنزيمات في الهضم؟",
        "expected_keywords": ["دور", "الأنzymات", "الهضم"],
    },
    {
        "name": "Cas 2 — Question méthodologique",
        "query": "كيف نحلل الوثيقة في تمارين المناعة؟",
        "expected_keywords": ["نحلل", "الوثيقة", "تمارين", "المناعة"],
    },
    {
        "name": "Cas 3 — Terme technique",
        "query": "اشرح دور ARN polymérase",
        "expected_keywords": ["دور", "arn", "polymérase"],
    },
    {
        "name": "Cas 4 — Requête bruitée",
        "query": "ما فهمتش مليح كيفاش تصرا الترجمة",
        "expected_keywords": ["فهمتش", "مليح", "كيفاش", "تصرا"],
    },
    {
        "name": "Cas 5 — Chapitre précis",
        "query": "في فصل المناعة الأجسام المضادة",
        "expected_keywords": ["المناعة", "الأجسام", "المضادة"],
    },
    {
        "name": "Cas 6 — Requête ambiguë",
        "query": "اشرح النقل",
        "expected_keywords": ["النقل"],
    },
]


def test_keyword_extraction():
    print("\n" + "=" * 60)
    print("  TEST 1 — Extraction de mots-clés")
    print("=" * 60)

    for tc in TEST_CASES:
        keywords = _extract_keywords(tc["query"], limit=4)
        print(f"\n  {tc['name']}")
        print(f"    Requête : {tc['query']}")
        print(f"    Mots-clés extraits : {keywords}")
        assert len(keywords) <= 4, f"Trop de mots-clés : {len(keywords)}"
        assert all(len(k) > 2 for k in keywords), f"Mots-clés trop courts : {keywords}"
        # Vérifier pas de stop words
        stop_in_results = [k for k in keywords if k in {"ما", "هو", "في", "من", "le", "la", "the", "is"}]
        assert not stop_in_results, f"Stop words dans les résultats : {stop_in_results}"
        print(f"    OK — {len(keywords)} mots-clés valides")


def test_reranker():
    print("\n" + "=" * 60)
    print("  TEST 2 — Reranker")
    print("=" * 60)

    all_chunks = MOCK_VECTOR_CHUNKS + MOCK_KEYWORD_CHUNKS

    for tc in TEST_CASES:
        reranked = rerank(tc["query"], all_chunks, top_k=3)
        print(f"\n  {tc['name']}")
        print(f"    Input : {len(all_chunks)} chunks → Output : {len(reranked)} chunks")
        assert len(reranked) <= 3, f"Trop de chunks : {len(reranked)}"
        assert all("score_rerank" in c for c in reranked), "score_rerank manquant"
        # Vérifier tri décroissant
        scores = [c["score_rerank"] for c in reranked]
        assert scores == sorted(scores, reverse=True), "Pas trié par score_rerank"
        print(f"    Top score : {reranked[0]['score_rerank']}")
        print(f"    Scores : {scores}")
        print(f"    Meilleur chapitre : {reranked[0].get('chapter', '?')}")
        print(f"    OK — reranker fonctionne")


def test_merge_chunks():
    print("\n" + "=" * 60)
    print("  TEST 3 — Fusion chunks")
    print("=" * 60)

    merged = merge_chunks(MOCK_VECTOR_CHUNKS, MOCK_KEYWORD_CHUNKS)
    print(f"  Vector : {len(MOCK_VECTOR_CHUNKS)} + Keyword : {len(MOCK_KEYWORD_CHUNKS)} → Fusion : {len(merged)}")

    # Vérifier déduplication
    hybrid_count = sum(1 for c in merged if c.get("retrieval") == "hybrid")
    print(f"  Chunks hybrides : {hybrid_count}")
    assert len(merged) <= len(MOCK_VECTOR_CHUNKS) + len(MOCK_KEYWORD_CHUNKS), "Trop de chunks après fusion"
    print(f"  OK — fusion fonctionne")


def test_format_rag_context():
    print("\n" + "=" * 60)
    print("  TEST 4 — Format contexte RAG")
    print("=" * 60)

    merged = merge_chunks(MOCK_VECTOR_CHUNKS, MOCK_KEYWORD_CHUNKS)
    context = format_rag_context(merged)

    print(f"  Chunks formatés : {len(merged)}")
    print(f"  Taille contexte : {len(context)} chars")

    # Vérifier format • excerpt (sans tags [source])
    assert "•" in context, "Format • excerpt manquant"
    assert "[" not in context, "Les tags [source] ne doivent plus apparaître dans le contexte"
    for line in context.split("\n\n"):
        if line.startswith("•"):
            excerpt_part = line[2:].strip()
            assert len(excerpt_part) <= 180, f"Excerpt trop long : {len(excerpt_part)} chars"
    print(f"  OK — format compact (180 chars max par excerpt, sans tags source)")

    # Afficher un extrait
    lines = context.split("\n\n")
    if lines:
        print(f"\n  Exemple :")
        print(f"  {lines[0][:120]}...")


def test_source_cards():
    print("\n" + "=" * 60)
    print("  TEST 5 — Source cards")
    print("=" * 60)

    merged = merge_chunks(MOCK_VECTOR_CHUNKS, MOCK_KEYWORD_CHUNKS)
    cards = source_cards(merged)

    print(f"  Sources uniques : {len(cards)}")
    for card in cards:
        print(f"    - {card['source']} / {card['chapter']}")
    assert len(cards) > 0, "Aucune source card"
    print(f"  OK — source cards fonctionnent")


def test_tokenization():
    print("\n" + "=" * 60)
    print("  TEST 6 — Tokenisation reranker")
    print("=" * 60)

    test_texts = [
        "ما هو دور الأنزيمات في الهضم",
        "ARN polymérase transcription",
        "Les protéines sont des enzymes",
    ]
    for text in test_texts:
        tokens = _tokenize(text)
        print(f"  '{text[:40]}...' → {tokens}")
        assert all(len(t) > 1 for t in tokens), f"Tokens trop courts : {tokens}"
    print(f"  OK — tokenisation fonctionne")


def run_all_tests():
    start = time.time()

    test_keyword_extraction()
    test_reranker()
    test_merge_chunks()
    test_format_rag_context()
    test_source_cards()
    test_tokenization()

    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"  RESUME")
    print(f"{'='*60}")
    print(f"  Tests : 6/6")
    print(f"  Temps : {elapsed:.3f}s")
    print(f"  Résultat : TOUS OK")

    return True


if __name__ == "__main__":
    success = run_all_tests()
    print(f"\n{'SUCCES' if success else 'ECHEC'} — Tests RAG termines.")
    sys.exit(0 if success else 1)


def test_rag_cache_stats():
    stats = rag_cache_stats()
    assert "hits" in stats
    assert "misses" in stats
    assert "hit_rate" in stats
    assert "size" in stats
    assert "max_size" in stats
    assert "ttl_seconds" in stats
    assert stats["max_size"] == 256
    assert stats["ttl_seconds"] == 300
    assert isinstance(stats["hit_rate"], float)


def test_chatbot_fallbacks():
    from services.chatbot_fallbacks import (
        fallback_motivation,
        fallback_procrastination,
        fallback_socratique,
        fallback_smart_goal,
    )
    assert isinstance(fallback_motivation({}), str)
    assert isinstance(fallback_procrastination(None), str)
    assert isinstance(fallback_socratique("test", []), str)
    assert isinstance(fallback_smart_goal(None), str)
    assert len(fallback_motivation({})) > 20
    assert len(fallback_procrastination(None)) > 20


def test_chatbot_response():
    from services.chatbot_response import make_response, normalize_response, normalize_cached
    r = make_response("test", type_="socratique")
    assert r["reponse"] == "test"
    assert r["type"] == "socratique"
    assert r["lang"] == "ar"
    assert r["from_cache"] is False

    n = normalize_response({"reponse": "x", "type": "motivation"})
    assert n["type"] == "motivation"
    assert n["from_cache"] is False

    c = normalize_cached({"reponse": "y", "type": "feedback"})
    assert c["from_cache"] is True


def test_llm_helpers():
    from services.llm_helpers import sanitize_response
    assert sanitize_response("") == ""
    assert sanitize_response("hello") == "hello"
    assert "Claude" not in (sanitize_response("I am Claude and I help.") or "clean")
    assert "حسب الكتاب" not in (sanitize_response("حسب الكتاب هذا درس.") or "clean")
