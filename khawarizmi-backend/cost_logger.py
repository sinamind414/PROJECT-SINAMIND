"""
COST LOGGER — JSONL append-only pour tracer le coût LLM par correction.

Usage:
    from cost_logger import get_logger
    log = get_logger()
    log.record("gpt-4o-mini", 824, 167, "cbe2d7c28f69", "expliquer", "exp_pompe_NaK", 900)
    print(log.report())
"""

import json
import os
import threading
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

_PRICING = {
    "gpt-4o-mini":     {"input": 0.15, "output": 0.60},
    "gpt-4o":          {"input": 2.50, "output": 10.00},
    "gpt-4.1-mini":    {"input": 0.40, "output": 1.60},
    "gpt-4.1-nano":    {"input": 0.10, "output": 0.40},
    "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
}

_DEFAULT_LOG_PATH = os.environ.get(
    "COST_LOG_PATH",
    str(Path(__file__).parent.parent / "cost_log.jsonl"),
)


class CostLogger:
    def __init__(self, log_path: str = _DEFAULT_LOG_PATH):
        self._path = Path(log_path)
        self._lock = threading.Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        prompt_hash: str,
        verb_slug: str = "",
        scenario_id: str = "",
        latency_ms: int = 0,
    ) -> dict:
        pricing = _PRICING.get(model, _PRICING["gpt-4o-mini"])
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000

        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": round(cost, 8),
            "prompt_hash": prompt_hash,
            "verb_slug": verb_slug,
            "scenario_id": scenario_id,
            "latency_ms": latency_ms,
        }

        with self._lock:
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return entry

    def _read_all(self) -> list[dict]:
        if not self._path.exists():
            return []
        entries = []
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries

    def total_cost(self) -> float:
        return sum(e["cost_usd"] for e in self._read_all())

    def total_calls(self) -> int:
        return len(self._read_all())

    def avg_cost(self) -> float:
        calls = self.total_calls()
        return self.total_cost() / calls if calls > 0 else 0.0

    def avg_tokens(self) -> dict:
        entries = self._read_all()
        if not entries:
            return {"input": 0, "output": 0}
        total_in = sum(e["input_tokens"] for e in entries)
        total_out = sum(e["output_tokens"] for e in entries)
        n = len(entries)
        return {"input": total_in // n, "output": total_out // n}

    def cost_by_verb(self) -> dict[str, float]:
        entries = self._read_all()
        by_verb = defaultdict(float)
        for e in entries:
            by_verb[e.get("verb_slug", "unknown")] += e["cost_usd"]
        return dict(by_verb)

    def projection(self, daily_users: int, corrections_per_user: int) -> dict:
        monthly_corrections = daily_users * corrections_per_user * 30
        avg = self.avg_cost()
        monthly_cost = monthly_corrections * avg
        return {
            "monthly_corrections": monthly_corrections,
            "avg_cost_per_correction": avg,
            "projected_monthly_usd": round(monthly_cost, 2),
        }

    def report(self) -> str:
        calls = self.total_calls()
        if calls == 0:
            return "=== COST REPORT ===\nNo calls recorded."
        avg = self.avg_tokens()
        proj = self.projection(daily_users=1000, corrections_per_user=2)
        return (
            f"=== COST REPORT ===\n"
            f"Total calls:    {calls}\n"
            f"Total cost:     ${self.total_cost():.6f}\n"
            f"Avg cost/call:  ${self.avg_cost():.6f}\n"
            f"Avg tokens:     in={avg['input']} out={avg['output']}\n"
            f"Monthly @ 1k×2: ${proj['projected_monthly_usd']:.2f}"
        )


_logger: CostLogger | None = None


def get_logger() -> CostLogger:
    global _logger
    if _logger is None:
        _logger = CostLogger()
    return _logger
