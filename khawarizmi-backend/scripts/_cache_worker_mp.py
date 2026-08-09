"""Worker de test multi-process pour le single-flight du cache C2.

Chaque processus corrige la MÊME copie (même clé de cache) contre le MÊME
Redis. Le test d'orchestration (tests/test_grading_cache_multiprocess.py)
démarre 2 workers simultanément via un « starting gate » (clé Redis) et
compte le nombre total d'appels LLM : le single-flight inter-workers doit
fusionner les 2 corrections → 1 seul appel.

Usage (interne aux tests) :
    python scripts/_cache_worker_mp.py --redis-url URL --gate-key K --qid N
        --verb analyse --answer "..." [--llm-ms 500]

Sortie : une ligne JSON {"calls": int, "from_cache": bool, "source": str}.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import redis.asyncio as aioredis

from app_state import state


class SimulatedLLM:
    """Correcteur simulé : dort ~llm_ms puis renvoie un résultat v2 cacheable."""

    def __init__(self, llm_ms: float) -> None:
        self.llm_ms = llm_ms
        self.calls = 0

    async def __call__(self, **kwargs) -> dict:
        self.calls += 1
        await asyncio.sleep(self.llm_ms / 1000.0)
        answer = kwargs.get("student_answer", "")
        score_max = int(kwargs.get("score_max", 7))
        return {
            "source": "llm_v2",
            "score": 5,
            "score_max": score_max,
            "percentage": round((5 / max(score_max, 1)) * 100),
            "highlights": [
                {"start": 0, "end": min(10, len(answer)), "type": "good_element",
                 "message_ar": "عنصر صحيح"},
            ],
            "matched_criteria": ["تقديم الوثيقة"],
            "unmatched_criteria": [],
            "feedback_ar": "إجابة مقبولة",
            "advice_ar": "",
            "confidence": 0.85,
            "parse_status": "ok",
            "sanity_code": "ok",
        }


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--redis-url", required=True)
    parser.add_argument("--gate-key", required=True)
    parser.add_argument("--qid", type=int, default=777)
    parser.add_argument("--verb", default="analyse")
    parser.add_argument("--answer", required=True)
    parser.add_argument("--llm-ms", type=float, default=500.0)
    args = parser.parse_args()

    from grading.cache import evaluate_with_cache

    client = aioredis.from_url(args.redis_url, decode_responses=True)
    state.redis = client

    # Signaler que ce worker est PRÊT (imports faits) puis attendre le départ.
    # Clé UNIQUE par worker (PID) : l'orchestrateur compte les ready via
    # KEYS gate:*:ready:* (une clé partagée ne permettrait pas de compter).
    await client.set(f"{args.gate_key}:ready:{os.getpid()}", "1")
    deadline = time.monotonic() + 20.0
    while time.monotonic() < deadline:
        if await client.exists(args.gate_key):
            break
        await asyncio.sleep(0.05)

    llm = SimulatedLLM(args.llm_ms)
    res = await evaluate_with_cache(
        question_id=args.qid,
        verb_slug=args.verb,
        score_max=7,
        student_answer=args.answer,
        model_id="gpt-4o-mini",
        evaluate_fn=llm,
        scenario_context="ctx",
        documents=None,
        question_prompt="حلل الوثيقة",
        question_skill="تحليل",
        model_answer="نسبة الغلوكوز تزداد",
        learning_focus=None,
        use_v2_prompt=True,
    )
    print(json.dumps({
        "calls": llm.calls,
        "from_cache": bool(res.get("from_cache")),
        "source": res.get("source"),
        "score": res.get("score"),
    }))
    # PAS de flushdb ici : il détruirait le cache pendant que l'autre worker
    # n'a pas encore lu (l'orchestrateur nettoie la DB avant/après).
    await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
