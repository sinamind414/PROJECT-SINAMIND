"""Benchmark de charge — cache correction C2 + latences (sans réseau ni DB).

Mesure, sur les VRAIS chemins (grading/cache.py + app_state), avec un
provider LLM simulé à latence contrôlée :

  1. Single-flight : 30 élèves concurrents sur la même copie → 1 seul appel
     LLM, 29 hits, hit rate, latence ressentie p50/p95/p99.
  2. Miss→Hit : 50 copies uniques (miss) puis re-soumission (hit) — latence
     miss (≈ LLM simulé) vs hit (≈ µs), hit rate global.
  3. Concurrence mixte : 10 questions × 10 élèves (réponses identiques par
     question, lancées en parallèle) → 10 appels LLM pour 100 corrections.

Usage :
    python scripts/benchmark_cache.py            # latence LLM simulée 200ms±80
    python scripts/benchmark_cache.py --llm-ms 150
    python scripts/benchmark_cache.py --quick    # 5 élèves / 5 questions

Sortie : rapport console (markdown-friendly) + data/benchmark_cache_results.json
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

# ── Réponses SVT réalistes (arabe) ───────────────────────────────────
REPONSES = [
    "نلاحظ من الوثيقة أن نسبة الغلوكوز في الدم تزداد من 0.8 إلى 1.4 غ/ل خلال ساعتين",
    "تسمح الوثيقة باستنتاج أن البنكرياس يفرز هرمون الأنسولين الذي يخفض نسبة السكر",
    "نستنتج من التجربة أن غياب الأنسولين يؤدي إلى ارتفاع السكر في الدم بشكل كبير",
    "يبيّن المنحنى أن كمية الأجسام المضادة ترتفع بعد الحقن الأول وتزداد بسرعة بعد الثاني",
    "تفسر هذه النتائج بدخول الماء إلى الخلية عبر الخاصية الأسموزية بسبب فرق التركيز",
    "تدل المعطيات على أن التنفس الخلوي يحدث في المتقدرات حيث يستهلك الأكسجين",
    "نلاحظ أن الكلية تحافظ على توازن الجسم بإعادة امتصاص الماء والأملاح",
    "تظهر الوثيقة أن العصبون ينقل السيالة العصبية من المستقبلات نحو المراكز العصبية",
    "يسمح هذا الاختبار بتحديد نوع الزمرة الدموية اعتمادا على الأجسام المضادة",
    "نستنتج أن الجين المسؤول عن المرض محمول على الصبغي الجنسي X",
    "يبيّن الجدول أن عملية التركيب الضوئي تتطلب ثنائي أكسيد الكربون و الضوء معا",
    "نلاحظ أن الهرمون يثبت مستقبله على الغشاء ثم ينشط الإنزيمات داخل الخلية",
]

VERBES = ["analyse", "interpret", "deduce", "justify", "explain", "compare"]


class FakeRedis:
    """Implémentation minimale in-memory de l'API redis.asyncio utilisée
    par grading/cache.py (get/setex/set nx/ex/exists/delete/eval CAS)."""

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


# ── Helpers ──────────────────────────────────────────────────────────

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


class SimulatedLLM:
    """Correcteur simulé : dort ~llm_ms ± jitter puis renvoie un résultat
    v2 plausible (contrat Public du cache). Compte les appels."""

    def __init__(self, llm_ms: float, jitter_ms: float = 80.0, seed: int = 42) -> None:
        self.llm_ms = llm_ms
        self.jitter_ms = jitter_ms
        self.calls = 0
        self._rng = random.Random(seed)

    async def __call__(self, **kwargs) -> dict:
        self.calls += 1
        await asyncio.sleep(max(0.0, self.llm_ms + self._rng.uniform(-self.jitter_ms, self.jitter_ms)) / 1000.0)
        answer = kwargs.get("student_answer", "")
        score_max = int(kwargs.get("score_max", 7))
        score = 5
        return {
            "source": "llm_v2",
            "score": score,
            "score_max": score_max,
            "percentage": round((score / score_max) * 100),
            "highlights": [
                {"start": 0, "end": min(10, len(answer)), "type": "good_element", "message_ar": "عنصر صحيح"},
            ],
            "matched_criteria": ["تقديم الوثيقة"],
            "unmatched_criteria": [],
            "feedback_ar": "إجابة مقبولة",
            "advice_ar": "حاول توضيح العلاقة السببية",
            "confidence": 0.85,
            "parse_status": "ok",
            "sanity_code": "ok",
            "llm_raw": "{}",
            "student_answer_hash": "sim",
        }


async def run_bench(redis, llm: SimulatedLLM, tasks: list[tuple[int, str, str, str]]) -> dict:
    """tasks = [(question_id, verb_slug, answer), ...] — exécutés en parallèle."""
    from grading.cache import evaluate_with_cache

    async def one(qid: int, verb: str, answer: str) -> dict:
        t0 = time.perf_counter()
        res = await evaluate_with_cache(
            question_id=qid, verb_slug=verb, score_max=7,
            student_answer=answer, model_id="gpt-4o-mini",
            evaluate_fn=llm,
        )
        return {"lat_ms": (time.perf_counter() - t0) * 1000.0, "res": res}

    t0 = time.perf_counter()
    results = await asyncio.gather(*[one(*t) for t in tasks])
    wall = (time.perf_counter() - t0) * 1000.0

    hits = [r for r in results if r["res"].get("from_cache")]
    misses = [r for r in results if not r["res"].get("from_cache")]
    lat_all = [r["lat_ms"] for r in results]
    return {
        "n": len(tasks),
        "llm_calls": llm.calls,
        "hits": len(hits),
        "misses": len(misses),
        "hit_rate": len(hits) / len(tasks),
        "wall_ms": wall,
        "lat_all": lat_all,
        "lat_hit": [r["lat_ms"] for r in hits],
        "lat_miss": [r["lat_ms"] for r in misses],
    }


def report(name: str, b: dict) -> str:
    lines = [
        f"### {name}",
        f"- corrections : **{b['n']}** · appels LLM : **{b['llm_calls']}** "
        f"(économie {(1 - b['llm_calls'] / b['n']) * 100:.1f} %)",
        f"- hit rate : **{b['hit_rate'] * 100:.1f} %** ({b['hits']} hits / {b['misses']} misses)",
        f"- mur : **{b['wall_ms'] / 1000:.2f}s**",
        f"- latence ressentie p50/p95/p99 : "
        f"{_fmt(pct(b['lat_all'], 50))} / {_fmt(pct(b['lat_all'], 95))} / {_fmt(pct(b['lat_all'], 99))}",
    ]
    if b["lat_hit"] and b["lat_miss"]:
        lines.append(
            f"- latence HIT p50/p99 : {_fmt(pct(b['lat_hit'], 50))} / {_fmt(pct(b['lat_hit'], 99))} "
            f"· MISS p50/p99 : {_fmt(pct(b['lat_miss'], 50))} / {_fmt(pct(b['lat_miss'], 99))}"
        )
    return "\n".join(lines)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--llm-ms", type=float, default=200.0, help="latence LLM simulée (ms)")
    parser.add_argument("--quick", action="store_true", help="variante réduite")
    args = parser.parse_args()

    from app_state import state

    state.redis = FakeRedis()
    llm = SimulatedLLM(llm_ms=args.llm_ms)
    print(f"Latence LLM simulée : {args.llm_ms:.0f} ms ± 80 ms (single process, fake redis)\n")

    N = 5 if args.quick else 30          # élèves concurrents (bench 1)
    NQ = 5 if args.quick else 50         # questions uniques (bench 2)
    NQ2 = 3 if args.quick else 10        # questions (bench 3)
    NE = 3 if args.quick else 10         # élèves par question (bench 3)

    # ── Bench 1 : single-flight (30 élèves, même copie) ─────────────
    llm.calls = 0
    b1 = await run_bench(state.redis, llm, [
        (101, "analyse", REPONSES[0]) for _ in range(N)
    ])
    assert b1["llm_calls"] == 1, f"single-flight cassé : {b1['llm_calls']} appels"

    # ── Bench 2 : 50 copies uniques (miss) puis re-soumission (hit) ─
    llm.calls = 0
    copies = [(200 + i, VERBES[i % len(VERBES)], REPONSES[i % len(REPONSES)]) for i in range(NQ)]
    b2_miss = await run_bench(state.redis, llm, copies)
    miss_calls = llm.calls
    assert miss_calls == NQ
    llm.calls = 0
    b2_hit = await run_bench(state.redis, llm, copies)
    hit_calls = llm.calls
    assert hit_calls == 0, f"re-soumission a rappelé le LLM : {hit_calls} fois"
    b2 = {
        "n": b2_miss["n"] + b2_hit["n"],
        "llm_calls": miss_calls + hit_calls,
        "hits": b2_miss["hits"] + b2_hit["hits"],
        "misses": b2_miss["misses"] + b2_hit["misses"],
        "hit_rate": (b2_miss["hits"] + b2_hit["hits"]) / (b2_miss["n"] + b2_hit["n"]),
        "wall_ms": b2_miss["wall_ms"] + b2_hit["wall_ms"],
        "lat_all": b2_miss["lat_all"] + b2_hit["lat_all"],
        "lat_hit": b2_hit["lat_hit"],
        "lat_miss": b2_miss["lat_miss"],
    }

    # ── Bench 3 : concurrence mixte (10 questions × 10 élèves) ──────
    llm.calls = 0
    tasks = []
    for qi in range(NQ2):
        for ei in range(NE):
            tasks.append((300 + qi, VERBES[qi % len(VERBES)], REPONSES[qi % len(REPONSES)]))
    b3 = await run_bench(state.redis, llm, tasks)
    assert b3["llm_calls"] == NQ2, f"single-flight par question cassé : {b3['llm_calls']}"

    # ── Rapport ─────────────────────────────────────────────────────
    out = [
        "# Benchmark cache correction C2 — résultats",
        "",
        f"Provider LLM **simulé** ({args.llm_ms:.0f} ms ± 80 ms par appel), "
        "fake redis in-process, single process asyncio.",
        "",
        report("1. Single-flight — 30 élèves concurrents, même copie", b1),
        "",
        report("2. Miss puis Hit — 50 copies uniques re-soumises", b2),
        "",
        report(f"3. Concurrence mixte — {NQ2} questions × {NE} élèves", b3),
    ]
    print("\n".join(out))

    results = {
        "llm_ms": args.llm_ms,
        "b1_single_flight": {k: v for k, v in b1.items() if k not in ("lat_all", "lat_hit", "lat_miss")},
        "b2_miss_hit": {k: v for k, v in b2.items() if k not in ("lat_all", "lat_hit", "lat_miss")},
        "b3_concurrent": {k: v for k, v in b3.items() if k not in ("lat_all", "lat_hit", "lat_miss")},
        "pct": {
            "b1": {f"p{p}": round(pct(b1["lat_all"], p), 1) for p in (50, 95, 99)},
            "b2_hit": {f"p{p}": round(pct(b2["lat_hit"], p), 1) for p in (50, 95, 99)},
            "b2_miss": {f"p{p}": round(pct(b2["lat_miss"], p), 1) for p in (50, 95, 99)},
            "b3": {f"p{p}": round(pct(b3["lat_all"], p), 1) for p in (50, 95, 99)},
        },
    }
    dest = pathlib.Path(__file__).parent.parent / "data" / "benchmark_cache_results.json"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nDétails → {dest}")


if __name__ == "__main__":
    asyncio.run(main())
