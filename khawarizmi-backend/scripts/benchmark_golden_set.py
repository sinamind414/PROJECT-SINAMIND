"""Benchmark Golden Set ONEC — mesure qualité RAG + Eval Engine.

Fait passer le Golden Set (50 Q/R) dans le pipeline actuel et mesure :
1. Couverture RAG : % de questions qui trouvent du contexte
2. Pertinence RAG : similarité entre chunks trouvés et réponse attendue
3. Latence par étape (embedding, RAG, LLM)
4. Score de similarité réponse IA vs réponse attendue

Usage :
    python scripts/benchmark_golden_set.py
    python scripts/benchmark_golden_set.py --limit 10  # quick test
    python scripts/benchmark_golden_set.py --no-llm    # RAG only, skip LLM calls

Output :
    - Console : résumé des métriques
    - data/benchmark_results.json : résultats détaillés
"""

import argparse
import asyncio
import json
import pathlib
import sys
import time

# Ajouter le répertoire backend au path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))


async def benchmark_rag_only(questions: list) -> dict:
    """Benchmark RAG uniquement (sans appel LLM) — mesure la couverture."""
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from config import get_settings
    from services.embedder import embedder

    cfg = get_settings()
    if not cfg.DATABASE_URL:
        return {"error": "DATABASE_URL non configuré"}

    db_url = cfg.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1).replace(
        "postgres://", "postgresql+asyncpg://", 1
    )
    engine = create_async_engine(db_url, pool_size=5, max_overflow=10, pool_pre_ping=True)
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    results = []
    rag_hit = 0
    rag_miss = 0
    total_embedding_time = 0
    total_rag_time = 0

    async with session_maker() as db:
        for q in questions:
            q_id = q["id"]
            chapitre = q["chapitre"]
            question = q["question"]
            q["reponse_attendue"]
            mots_cles = q["mots_cles_attendus"]

            # 1. Embedding
            t0 = time.perf_counter()
            try:
                query_vector = embedder.encode([question])[0]
                emb_time = (time.perf_counter() - t0) * 1000
                total_embedding_time += emb_time
            except Exception as e:
                results.append({"id": q_id, "status": "embed_error", "error": str(e)})
                continue

            # 2. RAG search
            t0 = time.perf_counter()
            try:
                res = await db.execute(
                    text("""
                        SELECT content, source,
                               1 - (embedding <=> CAST(:emb AS vector)) AS similarity
                        FROM rag_chunks
                        WHERE matiere ILIKE '%SVT%'
                        ORDER BY embedding <=> CAST(:emb AS vector)
                        LIMIT 3
                    """),
                    {"emb": str(query_vector.tolist())},
                )
                chunks = res.fetchall()
                rag_time = (time.perf_counter() - t0) * 1000
                total_rag_time += rag_time
            except Exception as e:
                results.append({"id": q_id, "status": "rag_error", "error": str(e), "embed_ms": round(emb_time, 2)})
                continue

            if chunks:
                rag_hit += 1
                # Vérifier si les mots-clés attendus sont dans les chunks
                chunk_text = " ".join([str(c[0]) for c in chunks])
                mots_trouves = [m for m in mots_cles if m.lower() in chunk_text.lower()]
                coverage = len(mots_trouves) / len(mots_cles) if mots_cles else 0

                results.append(
                    {
                        "id": q_id,
                        "status": "rag_hit",
                        "chapitre": chapitre,
                        "niveau": q["niveau"],
                        "embed_ms": round(emb_time, 2),
                        "rag_ms": round(rag_time, 2),
                        "chunks_count": len(chunks),
                        "best_similarity": round(float(chunks[0][2]), 4) if chunks[0][2] else 0,
                        "mots_cles_attendus": mots_cles,
                        "mots_cles_trouves": mots_trouves,
                        "keyword_coverage": round(coverage, 3),
                    }
                )
            else:
                rag_miss += 1
                results.append(
                    {
                        "id": q_id,
                        "status": "rag_miss",
                        "chapitre": chapitre,
                        "niveau": q["niveau"],
                        "embed_ms": round(emb_time, 2),
                        "rag_ms": round(rag_time, 2),
                    }
                )

    await engine.dispose()

    total = len(questions)
    return {
        "total_questions": total,
        "rag_hits": rag_hit,
        "rag_misses": rag_miss,
        "rag_coverage": round(rag_hit / total, 3) if total > 0 else 0,
        "avg_embedding_ms": round(total_embedding_time / total, 2) if total > 0 else 0,
        "avg_rag_ms": round(total_rag_time / total, 2) if total > 0 else 0,
        "results": results,
    }


async def benchmark_full(questions: list) -> dict:
    """Benchmark complet RAG + LLM — mesure la qualité des réponses."""
    from openai import AsyncOpenAI
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from config import get_settings
    from services.embedder import embedder

    cfg = get_settings()
    if not cfg.DATABASE_URL:
        return {"error": "DATABASE_URL non configuré"}

    db_url = cfg.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1).replace(
        "postgres://", "postgresql+asyncpg://", 1
    )
    engine = create_async_engine(db_url, pool_size=5, max_overflow=10, pool_pre_ping=True)
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    openai_client = AsyncOpenAI(api_key=cfg.OPENAI_API_KEY, base_url=cfg.openai_base_url)

    results = []
    rag_hit = 0
    llm_success = 0
    llm_fail = 0
    total_embedding_time = 0
    total_rag_time = 0
    total_llm_time = 0

    async with session_maker() as db:
        for i, q in enumerate(questions):
            q_id = q["id"]
            chapitre = q["chapitre"]
            question = q["question"]
            reponse_attendue = q["reponse_attendue"]
            mots_cles = q["mots_cles_attendus"]

            print(f"  [{i + 1}/{len(questions)}] {q_id} — {chapitre}...", end=" ", flush=True)

            # 1. Embedding
            t0 = time.perf_counter()
            try:
                query_vector = embedder.encode([question])[0]
                emb_time = (time.perf_counter() - t0) * 1000
                total_embedding_time += emb_time
            except Exception as e:
                print("EMBED ERROR")
                results.append({"id": q_id, "status": "embed_error", "error": str(e)})
                continue

            # 2. RAG search
            t0 = time.perf_counter()
            try:
                res = await db.execute(
                    text("""
                        SELECT content, source,
                               1 - (embedding <=> CAST(:emb AS vector)) AS similarity
                        FROM rag_chunks
                        WHERE matiere ILIKE '%SVT%'
                        ORDER BY embedding <=> CAST(:emb AS vector)
                        LIMIT 3
                    """),
                    {"emb": str(query_vector.tolist())},
                )
                chunks = res.fetchall()
                rag_time = (time.perf_counter() - t0) * 1000
                total_rag_time += rag_time
            except Exception as e:
                print("RAG ERROR")
                results.append({"id": q_id, "status": "rag_error", "error": str(e)})
                continue

            if not chunks:
                print("RAG MISS")
                results.append({"id": q_id, "status": "rag_miss", "chapitre": chapitre})
                continue

            rag_hit += 1
            context_text = "\n\n".join([f"Source: {c[1]}\n{c[0]}" for c in chunks])

            # 3. LLM call
            t0 = time.perf_counter()
            try:
                prompt = f"""Tu es un tuteur SVT. Réponds à la question en arabe en utilisant le contexte.

CONTEXTE :
{context_text}

QUESTION : {question}

Réponds en arabe, sois précis et pédagogique."""

                response = await openai_client.chat.completions.create(
                    model=cfg.openai_model,
                    messages=[
                        {"role": "system", "content": "Tu es un tuteur SVT expert pour le Bac algérien."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=300,
                    timeout=20.0,
                )
                llm_response = response.choices[0].message.content or ""
                llm_time = (time.perf_counter() - t0) * 1000
                total_llm_time += llm_time
                llm_success += 1

                # Vérifier la présence des mots-clés dans la réponse LLM
                mots_trouves_llm = [m for m in mots_cles if m.lower() in llm_response.lower()]
                llm_keyword_coverage = len(mots_trouves_llm) / len(mots_cles) if mots_cles else 0

                print(f"OK ({llm_time:.0f}ms, cov={llm_keyword_coverage:.0%})")

                results.append(
                    {
                        "id": q_id,
                        "status": "success",
                        "chapitre": chapitre,
                        "niveau": q["niveau"],
                        "embed_ms": round(emb_time, 2),
                        "rag_ms": round(rag_time, 2),
                        "llm_ms": round(llm_time, 2),
                        "best_similarity": round(float(chunks[0][2]), 4) if chunks[0][2] else 0,
                        "mots_cles_attendus": mots_cles,
                        "mots_cles_trouves_llm": mots_trouves_llm,
                        "llm_keyword_coverage": round(llm_keyword_coverage, 3),
                        "llm_response_preview": llm_response[:200],
                        "reponse_attendue_preview": reponse_attendue[:200],
                    }
                )

            except Exception as e:
                llm_fail += 1
                llm_time = (time.perf_counter() - t0) * 1000
                total_llm_time += llm_time
                print(f"LLM FAIL ({e})")
                results.append(
                    {
                        "id": q_id,
                        "status": "llm_error",
                        "chapitre": chapitre,
                        "embed_ms": round(emb_time, 2),
                        "rag_ms": round(rag_time, 2),
                        "llm_ms": round(llm_time, 2),
                        "error": str(e)[:200],
                    }
                )

    await engine.dispose()

    total = len(questions)
    # Calculer la couverture moyenne des mots-clés
    keyword_coverages = [r.get("llm_keyword_coverage", 0) for r in results if r["status"] == "success"]

    return {
        "total_questions": total,
        "rag_hits": rag_hit,
        "rag_coverage": round(rag_hit / total, 3) if total > 0 else 0,
        "llm_success": llm_success,
        "llm_fail": llm_fail,
        "llm_success_rate": round(llm_success / total, 3) if total > 0 else 0,
        "avg_embedding_ms": round(total_embedding_time / total, 2) if total > 0 else 0,
        "avg_rag_ms": round(total_rag_time / total, 2) if total > 0 else 0,
        "avg_llm_ms": round(total_llm_time / max(llm_success, 1), 2) if llm_success > 0 else 0,
        "avg_keyword_coverage": round(sum(keyword_coverages) / len(keyword_coverages), 3) if keyword_coverages else 0,
        "results": results,
    }


def print_summary(stats: dict, full: bool = False):
    """Affiche un résumé lisible du benchmark."""
    print("\n" + "=" * 60)
    print("BENCHMARK GOLDEN SET ONEC — RÉSULTATS")
    print("=" * 60)

    if "error" in stats:
        print(f"ERREUR: {stats['error']}")
        return

    print(f"\nTotal questions : {stats['total_questions']}")
    print(f"RAG couverture  : {stats['rag_coverage']:.1%} ({stats.get('rag_hits', 0)} hits)")

    if full:
        print(
            f"LLM succès     : {stats.get('llm_success_rate', 0):.1%} ({stats.get('llm_success', 0)}/{stats['total_questions']})"
        )
        print(f"Keyword coverage moyen : {stats.get('avg_keyword_coverage', 0):.1%}")

    print("\nLatences :")
    print(f"  Embedding : {stats['avg_embedding_ms']:.1f} ms (moyenne)")
    print(f"  RAG       : {stats['avg_rag_ms']:.1f} ms (moyenne)")
    if full:
        print(f"  LLM       : {stats.get('avg_llm_ms', 0):.1f} ms (moyenne)")

    # Détail par chapitre
    print("\nPar chapitre :")
    chapitre_stats = {}
    for r in stats.get("results", []):
        ch = r.get("chapitre", "?")
        if ch not in chapitre_stats:
            chapitre_stats[ch] = {"total": 0, "hits": 0, "misses": 0}
        chapitre_stats[ch]["total"] += 1
        if r["status"] in ("rag_hit", "success"):
            chapitre_stats[ch]["hits"] += 1
        else:
            chapitre_stats[ch]["misses"] += 1

    for ch, s in sorted(chapitre_stats.items()):
        cov = s["hits"] / s["total"] if s["total"] > 0 else 0
        print(f"  {ch:40s} : {s['hits']}/{s['total']} ({cov:.0%})")

    print("=" * 60)


async def main():
    parser = argparse.ArgumentParser(description="Benchmark Golden Set ONEC")
    parser.add_argument("--limit", type=int, default=None, help="Limiter le nombre de questions")
    parser.add_argument("--no-llm", action="store_true", help="RAG only, skip LLM calls")
    parser.add_argument("--output", type=str, default="data/benchmark_results.json", help="Fichier de sortie")
    args = parser.parse_args()

    # Charger le Golden Set
    golden_path = pathlib.Path(__file__).parent.parent / "data" / "golden_set_onec.json"
    if not golden_path.exists():
        print(f"Golden Set introuvable: {golden_path}")
        print("Génère-le d'abord: python scripts/generate_golden_set.py")
        return

    with open(golden_path, encoding="utf-8") as f:
        golden = json.load(f)

    questions = golden["questions"]
    if args.limit:
        questions = questions[: args.limit]

    print(f"Benchmark Golden Set — {len(questions)} questions")
    print(f"Mode: {'RAG only' if args.no_llm else 'Full (RAG + LLM)'}")
    print()

    if args.no_llm:
        stats = await benchmark_rag_only(questions)
    else:
        stats = await benchmark_full(questions)

    # Sauvegarder les résultats
    output_path = pathlib.Path(__file__).parent.parent / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    # Afficher le résumé
    print_summary(stats, full=not args.no_llm)
    print(f"\nRésultats détaillés: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
