"""Benchmark pipeline complet — étage savoir local vs LLM (sans réseau ni DB).

Mesure sur les VRAIS chemins (evaluate_with_cache → retry → façade →
grading/pipeline.py) avec un llm_call simulé à latence contrôlée :

  A. Savoir ACTIVÉ (config.savoir_enabled_verbs) — corpus mixte de copies
     fortes (≥ 3 concepts → promues localement, 0 token) et faibles
     (→ LLM simulé) : répartition des sources, appels LLM, latence par
     source.
  B. Savoir DÉSACTIVÉ (défaut prod) — même corpus : 100 % LLM → coût
     comparé.
  C. Micro-benchmark de l'étage savoir pur (run_savoir) : latence moyenne,
     throughput.

Le corpus est construit depuis tests/golden/golden_annotated.json (125 items
synthétiques) : questions uniques, copies fortes = réponse modèle (garantie
≥ 3 concepts), copies faibles = réponse modèle d'une AUTRE question (match
< 3 vérifié). Les questions non couvertes par le lexique sont exclues du
corpus et comptées (taux de couverture).

Usage :
    python scripts/benchmark_pipeline.py
    python scripts/benchmark_pipeline.py --llm-ms 150
    python scripts/benchmark_pipeline.py --quick

Sortie : rapport console + data/benchmark_pipeline_results.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import pathlib
import random
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))


class FakeRedis:
    """API redis.asyncio minimale utilisée par grading/cache.py."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        self._expiry: dict[str, float] = {}

    def _prune(self, key: str) -> None:
        if key in self._expiry and self._expiry[key] < time.monotonic():
            del self._data[key]
            del self._expiry[key]

    async def get(self, key: str) -> str | None:
        self._prune(key)
        return self._data.get(key)

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self._data[key] = value
        self._expiry[key] = time.monotonic() + ttl

    async def set(self, key: str, value: str, nx: bool = False, ex: int | None = None):
        self._prune(key)
        if nx and key in self._data:
            return False
        self._data[key] = value
        if ex:
            self._expiry[key] = time.monotonic() + ex
        return True

    async def exists(self, key: str) -> int:
        self._prune(key)
        return 1 if key in self._data else 0

    async def delete(self, key: str) -> int:
        existed = key in self._data
        self._data.pop(key, None)
        self._expiry.pop(key, None)
        return 1 if existed else 0

    async def eval(self, _lua: str, _numkeys: int, key: str, token: str) -> int:
        if self._data.get(key) == token:
            await self.delete(key)
            return 1
        return 0


class SimulatedLLM:
    """llm_call simulé : dort ~llm_ms ± jitter puis renvoie une réponse
    parseable (JSON v1, format du mock des tests)."""

    def __init__(self, llm_ms: float, jitter_ms: float = 80.0, seed: int = 7) -> None:
        self.llm_ms = llm_ms
        self.jitter_ms = jitter_ms
        self.calls = 0
        self._rng = random.Random(seed)

    async def __call__(self, **kwargs) -> object:
        self.calls += 1
        await asyncio.sleep(
            max(0.0, self.llm_ms + self._rng.uniform(-self.jitter_ms, self.jitter_ms)) / 1000.0
        )
        from unittest.mock import MagicMock

        resp = MagicMock()
        resp.choices = [MagicMock()]
        resp.choices[0].message.content = json.dumps({
            "score": 2,
            "matched_criteria": ["a"],
            "unmatched_criteria": [],
            "highlights": [],
            "feedback_ar": "f",
            "advice_ar": "",
            "confidence": 0.9,
        }, ensure_ascii=False)
        resp.choices[0].finish_reason = "stop"
        resp._khawarizmi_json_mode = False
        resp._khawarizmi_provider = "primary"
        resp._khawarizmi_model = "bench-sim"
        return resp


# ── Construction du corpus ───────────────────────────────────────────

def load_corpus(limit: int | None = None) -> tuple[list[dict], int, int]:
    """Questions uniques du golden, avec copies forte/faible validées."""
    # Pré-test du MATCH lexical indépendant du flag (deterministic_correct_v2
    # ne consulte pas savoir_enabled_verbs — c'est run_savoir qui le fait).
    from services.savoir_corrector import deterministic_correct_v2

    raw = json.load(open(pathlib.Path(__file__).parent.parent / "tests" / "golden" / "golden_annotated.json"))
    items = raw.get("items", raw) if isinstance(raw, dict) else raw

    by_qid: dict[str, dict] = {}
    for it in items:
        qid = it.get("question_id") or it.get("id")
        if qid not in by_qid and it.get("question"):
            by_qid[qid] = it
    questions = list(by_qid.values())[:limit] if limit else list(by_qid.values())

    corpus = []
    n_uncovered = 0
    for it in questions:
        q = it["question"]
        m = it.get("reponse_attendue") or ""
        if not m:
            continue
        score_max = int(it.get("bareme") or 2)
        verb = it.get("verb_slug") or "restitution"
        # copie forte = réponse modèle → vérifier ≥ 3 concepts (match lexique)
        strong = deterministic_correct_v2(
            question=q, student_answer=m, score_max=score_max, model_answer=m,
        )
        if not (strong["_savoir_can_handle"] and strong["_savoir_n_concepts"] >= 3):
            n_uncovered += 1
            continue
        corpus.append({
            "question_id": it.get("question_id") or it.get("id"),
            "question": q,
            "model_answer": m,
            "score_max": score_max,
            "verb_slug": verb,
        })

    # copies faibles : réponse modèle d'une AUTRE question (match < 3)
    for i, c in enumerate(corpus):
        other = corpus[(i + 1) % len(corpus)]
        c["weak_answer"] = other["model_answer"]

    return corpus, n_uncovered, len(questions)


async def run_scenario(redis, llm: SimulatedLLM, corpus: list[dict],
                       savoir_verbs: list[str], label: str) -> dict:
    """Toutes les copies (forte + faible par question) via le chemin PROD
    (wrapper cache → retry → pipeline), en parallèle."""
    from config import get_settings

    get_settings().savoir_enabled_verbs = savoir_verbs

    from grading.cache import evaluate_with_cache
    from services.correction_v2_retry import evaluate_answer_v2_with_retry

    tasks = []
    for c in corpus:
        for tag, ans in (("forte", c["model_answer"]), ("faible", c["weak_answer"])):
            tasks.append((c, tag, ans))

    async def one(c: dict, tag: str, ans: str) -> dict:
        t0 = time.perf_counter()
        res = await evaluate_with_cache(
            question_id=f"{c['question_id']}_{tag}",
            verb_slug=c["verb_slug"],
            score_max=c["score_max"],
            student_answer=ans,
            model_id="gpt-4o-mini",
            evaluate_fn=evaluate_answer_v2_with_retry,
            llm_call=llm,
            primary_client=None,
            primary_model="bench-sim",
            scenario_context="",
            documents=None,
            question_prompt=c["question"],
            question_skill="",
            model_answer=c["model_answer"],
            learning_focus=None,
            use_v2_prompt=True,
        )
        return {"tag": tag, "source": res.get("source", "?"),
                "attempts": res.get("attempts"),
                "lat_ms": (time.perf_counter() - t0) * 1000.0}

    t0 = time.perf_counter()
    results = await asyncio.gather(*[one(*t) for t in tasks])
    wall = (time.perf_counter() - t0) * 1000.0

    from collections import Counter
    sources = Counter(r["source"] for r in results)
    lat_by_src: dict[str, list[float]] = {}
    attempts_by_src: dict[str, Counter] = {}
    for r in results:
        lat_by_src.setdefault(r["source"], []).append(r["lat_ms"])
        attempts_by_src.setdefault(r["source"], Counter())[r.get("attempts")] += 1

    return {
        "label": label,
        "n": len(results),
        "llm_calls": llm.calls,
        "sources": dict(sources),
        "lat_by_src": lat_by_src,
        "attempts_by_src": {k: dict(v) for k, v in attempts_by_src.items()},
        "wall_ms": wall,
    }


def pct(vals: list[float], p: float) -> float:
    if not vals:
        return 0.0
    vals = sorted(vals)
    k = max(0, min(len(vals) - 1, int(round((p / 100.0) * (len(vals) - 1)))))
    return vals[k]


def _fmt(ms: float) -> str:
    if ms >= 1000:
        return f"{ms / 1000:.2f}s"
    if ms >= 1:
        return f"{ms:.1f}ms"
    return f"{ms * 1000:.0f}µs"


def report_scenario(b: dict) -> str:
    lines = [f"### {b['label']}"]
    lines.append(f"- corrections : **{b['n']}** · appels LLM : **{b['llm_calls']}** "
                 f"(économie {(1 - b['llm_calls'] / b['n']) * 100:.1f} %) · mur : {b['wall_ms'] / 1000:.2f}s")
    total = b["n"]
    for src, count in sorted(b["sources"].items(), key=lambda kv: -kv[1]):
        lat = b["lat_by_src"][src]
        att = b.get("attempts_by_src", {}).get(src, {})
        att_str = f" · attempts : {att}" if att else ""
        lines.append(f"- `{src}` : {count} ({count / total * 100:.1f} %) · latence "
                     f"p50/p95/p99 : {_fmt(pct(lat, 50))} / {_fmt(pct(lat, 95))} / {_fmt(pct(lat, 99))}{att_str}")
    return "\n".join(lines)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--llm-ms", type=float, default=200.0)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    # Désactiver le tracing OTel console (spam de sortie dans un benchmark)
    import grading.tracing as _tracing
    from app_state import state
    _tracing._ENABLED = False

    limit = 6 if args.quick else None
    corpus, n_uncovered, n_questions = load_corpus(limit)
    verbs = sorted({c["verb_slug"] for c in corpus})
    if not corpus:
        print("Corpus vide — aucun item golden couvert par le lexique ?")
        sys.exit(1)

    llm = SimulatedLLM(llm_ms=args.llm_ms)
    print(f"Corpus : {len(corpus)} questions ({n_questions} au total, "
          f"{n_uncovered} non couvertes par le lexique) · verbes : {verbs}")
    print(f"Latence LLM simulée : {args.llm_ms:.0f} ms ± 80 ms\n")

    # ── A. Savoir activé ────────────────────────────────────────────
    state.redis = FakeRedis()
    llm.calls = 0
    a = await run_scenario(state.redis, llm, corpus, savoir_verbs=verbs, label="A. Savoir activé")

    # ── B. Savoir désactivé (défaut prod) ───────────────────────────
    state.redis = FakeRedis()
    llm.calls = 0
    b = await run_scenario(state.redis, llm, corpus, savoir_verbs=[], label="B. Savoir désactivé (défaut)")

    # ── C. Micro-benchmark étage savoir pur ─────────────────────────
    # Le flag DOIT rester actif : is_savoir_enabled() est la première ligne
    # de run_savoir — flag vide → return None immédiat (ne mesure rien).
    from config import get_settings
    from grading.savoir import run_savoir

    get_settings().savoir_enabled_verbs = verbs
    t0 = time.perf_counter()
    n_savoir = 0
    for _ in range(200):
        for c in corpus:
            run_savoir(question=c["question"], student_answer=c["model_answer"],
                       verb_slug=c["verb_slug"], score_max=c["score_max"],
                       model_answer=c["model_answer"])
            n_savoir += 1
    savoir_wall = (time.perf_counter() - t0) * 1000.0
    per_call = savoir_wall / max(n_savoir, 1)

    # ── Rapport ─────────────────────────────────────────────────────
    out = [
        "# Benchmark pipeline — étage savoir local vs LLM",
        "",
        f"Corpus : **{len(corpus)} questions** du golden (couverture lexique "
        f"{len(corpus)}/{n_questions}) · provider LLM simulé "
        f"({args.llm_ms:.0f} ms ± 80 ms), fake redis, chemin prod complet "
        "(cache → retry → pipeline).",
        "",
        report_scenario(a),
        "",
        report_scenario(b),
        "",
        "### C. Étage savoir pur (run_savoir)",
        f"- {n_savoir} appels · mur {savoir_wall / 1000:.2f}s · **{per_call * 1000:.1f} µs/appel** "
        f"(soit ~{int(1000 / max(per_call, 1e-9))} copies/s mono-thread)",
    ]
    print("\n".join(out))

    results = {
        "llm_ms": args.llm_ms,
        "corpus": {"questions": len(corpus), "total": n_questions, "uncovered": n_uncovered, "verbs": verbs},
        "a_savoir_active": {
            "n": a["n"], "llm_calls": a["llm_calls"], "sources": a["sources"], "wall_ms": a["wall_ms"],
            "lat_pct": {src: {f"p{p}": round(pct(v, p), 2) for p in (50, 95, 99)} for src, v in a["lat_by_src"].items()},
        },
        "b_savoir_desactive": {
            "n": b["n"], "llm_calls": b["llm_calls"], "sources": b["sources"], "wall_ms": b["wall_ms"],
            "lat_pct": {src: {f"p{p}": round(pct(v, p), 2) for p in (50, 95, 99)} for src, v in b["lat_by_src"].items()},
        },
        "c_savoir_pur": {"calls": n_savoir, "wall_ms": round(savoir_wall, 1), "us_per_call": round(per_call * 1000, 1)},
    }
    dest = pathlib.Path(__file__).parent.parent / "data" / "benchmark_pipeline_results.json"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nDétails → {dest}")


if __name__ == "__main__":
    asyncio.run(main())
