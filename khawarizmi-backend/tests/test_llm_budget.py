# tests/test_llm_budget.py
# G0-3 (grille go-no-go-100k) : alerte budgétaire + kill-switch + compteur
# journalier du coût LLM.
#
# Audit 100k v2 (reçu R13) : circuit breaker par provider PRÉSENT, mais
# « alerte budgétaire globale, kill-switch par feature, compteurs de coût
# par jour » ABSENTS — et le coût réel n'était tracé NULLEPART en
# production (cost_logger existait sans aucun appelant).
#
# Ce que ça prouve (reçus) :
#   B1 — le compteur journalier accumule le coût réel des appels réussis.
#   B2 — budget dépassé → coupure automatique (BUDGET_KILL) + LLM externe
#        désautorisé pour la journée.
#   B3 — la coupure automatique se lève au jour UTC suivant (compteur remis à 0).
#   B4 — kill-switch manuels : LLM_KILL (global) et LLM_KILL_FEATURES
#        (par feature, les autres features continuent).
#   B5 — _call_with_fallback lève LLMExternalDisabled AVANT tout appel
#        provider (le client provider n'est jamais touché).
#   B6 — sur succès, l'usage réel (tokens) est enregistré dans le compteur
#        ET dans cost_log.jsonl (avec la feature).
#   B7 — l'état du budget est exposé dans /health (business.llm_budget).
#   B8 — sur BUDGET_KILL, Sentry est notifié (capture_message, fatal).
#   B9 — sur BUDGET_KILL, le webhook BUDGET_ALERT_WEBHOOK reçoit le POST
#        JSON — exactement UNE fois par journée de coupure.
#   B10 — un échec du webhook n'affecte ni la coupure ni la comptabilité.
#   B11 — métriques Prometheus : llm_budget_day_cost_usd / _auto_killed /
#        llm_budget_kills_total suivent l'état réel.

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

import cost_logger
import services.llm_budget as llm_budget
from config import settings
from services.llm_budget import LLMExternalDisabled, LLMBudget


@pytest.fixture(autouse=True)
def _fresh_budget():
    """Budget dédié par test (pas d'état partagé entre tests)."""
    llm_budget._budget = LLMBudget()
    yield
    llm_budget._budget = None


@pytest.fixture(autouse=True)
def _cost_log_isolated(tmp_path):
    """cost_logger pointé sur un fichier temporaire (pas le cost_log.jsonl
    du repo)."""
    previous = cost_logger._logger
    cost_logger._logger = cost_logger.CostLogger(str(tmp_path / "cost.jsonl"))
    yield
    cost_logger._logger = previous


# ─── B1 — compteur journalier ────────────────────────────────────────────


def test_budget_accumulates_real_costs():
    b = llm_budget.get_budget()
    b.record_cost(0.001, model="gemini-2.5-flash")
    b.record_cost(0.002, model="gemini-2.5-flash")
    st = b.status()
    assert st["day_cost_usd"] == pytest.approx(0.003)
    assert st["day_calls"] == 2
    assert st["auto_killed"] is False
    assert b.is_allowed("general") is True


# ─── B2 — budget dépassé → coupure automatique ───────────────────────────


def test_budget_exceeded_triggers_auto_kill(monkeypatch):
    monkeypatch.setattr(settings, "LLM_DAILY_BUDGET_USD", 0.01)
    b = llm_budget.get_budget()
    assert b.is_allowed("general") is True
    b.record_cost(0.02, model="gemini-2.5-flash")
    st = b.status()
    assert st["auto_killed"] is True
    assert b.is_allowed("general") is False
    assert b.is_allowed("evaluate") is False


# ─── B3 — levée de la coupure au jour UTC suivant ────────────────────────


def test_auto_kill_releases_next_utc_day(monkeypatch):
    monkeypatch.setattr(settings, "LLM_DAILY_BUDGET_USD", 0.01)
    b = llm_budget.get_budget()
    b.record_cost(0.02)
    assert b.is_allowed("general") is False

    now = datetime.now(UTC)
    monkeypatch.setattr(
        llm_budget, "_now", lambda: now + timedelta(days=1)
    )
    assert b.is_allowed("general") is True
    st = b.status()
    assert st["day_cost_usd"] == 0.0
    assert st["day_calls"] == 0
    assert st["auto_killed"] is False


# ─── B4 — kill-switch manuels ────────────────────────────────────────────


def test_manual_kill_global(monkeypatch):
    monkeypatch.setattr(settings, "LLM_KILL", True)
    b = llm_budget.get_budget()
    assert b.is_allowed("general") is False
    assert b.is_allowed("evaluate") is False
    assert b.is_allowed("tutor") is False


def test_manual_kill_per_feature(monkeypatch):
    monkeypatch.setattr(settings, "LLM_KILL_FEATURES", "evaluate,chat")
    b = llm_budget.get_budget()
    assert b.is_allowed("evaluate") is False
    assert b.is_allowed("chat") is False
    # Les autres features continuent :
    assert b.is_allowed("tutor") is True
    assert b.is_allowed("engine") is True


# ─── B5 — porte d'entrée : LLMExternalDisabled avant tout provider ──────


async def test_call_with_fallback_raises_when_killed(monkeypatch):
    from services.llm import _call_with_fallback

    monkeypatch.setattr(settings, "LLM_KILL", True)
    never_touched = object()  # si le provider était touché → AttributeError
    with pytest.raises(LLMExternalDisabled):
        await _call_with_fallback(
            messages=[{"role": "user", "content": "x"}],
            primary_client=never_touched,
            primary_model="gpt-4o-mini",
            feature="evaluate",
        )


# ─── B6 — usage réel enregistré sur succès ───────────────────────────────


async def test_usage_recorded_on_success(tmp_path):
    from services.llm import _call_with_fallback

    class _FakeUsage:
        prompt_tokens = 1000
        completion_tokens = 500

    class _FakeCompletions:
        async def create(self, **kwargs):
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))],
                usage=_FakeUsage(),
            )

    fake_client = SimpleNamespace(chat=SimpleNamespace(completions=_FakeCompletions()))
    b = llm_budget.get_budget()
    before = b.status()["day_cost_usd"]

    resp = await _call_with_fallback(
        messages=[{"role": "user", "content": "x"}],
        primary_client=fake_client,
        primary_model="gpt-4o-mini",
        feature="evaluate",
    )
    assert resp is not None

    st = b.status()
    # gpt-4o-mini : 1000×0.15/M + 500×0.60/M = 0.00045 $
    assert st["day_cost_usd"] == pytest.approx(before + 0.00045)
    assert st["day_calls"] == 1

    # Et dans cost_log.jsonl (avec la feature) :
    import json

    log = json.loads(cost_logger._logger._path.read_text().strip().splitlines()[-1])
    assert log["model"] == "gpt-4o-mini"
    assert log["feature"] == "evaluate"
    assert log["input_tokens"] == 1000


# ─── B8 — alerte Sentry sur BUDGET_KILL ──────────────────────────────────


def test_sentry_notified_on_kill(monkeypatch):
    import sentry_sdk

    calls: list[tuple[str, dict]] = []
    monkeypatch.setattr(
        sentry_sdk, "capture_message",
        lambda msg, **kw: calls.append((msg, kw)),
        raising=False,
    )
    monkeypatch.setattr(settings, "LLM_DAILY_BUDGET_USD", 0.01)
    b = llm_budget.get_budget()
    b.record_cost(0.02, model="gemini-2.5-flash")

    assert len(calls) == 1
    msg, kw = calls[0]
    assert "BUDGET_KILL" in msg
    assert "gemini-2.5-flash" in msg
    assert kw.get("level") == "fatal"


# ─── B9 — webhook une seule fois par journée de coupure ─────────────────


def test_webhook_called_once_per_kill_day(monkeypatch):
    sent: list[tuple[str, dict]] = []
    monkeypatch.setattr(llm_budget, "_send_webhook", lambda url, p: sent.append((url, p)))
    monkeypatch.setattr(settings, "LLM_DAILY_BUDGET_USD", 0.01)
    monkeypatch.setattr(settings, "BUDGET_ALERT_WEBHOOK", "https://alerte.example/hook")

    b = llm_budget.get_budget()
    b.record_cost(0.006)   # sous le plafond → pas d'alerte
    assert sent == []
    b.record_cost(0.005)   # 0.011 ≥ 0.01 → coupure → 1re (et unique) alerte
    b.record_cost(0.005)   # déjà coupé → pas de 2e alerte

    assert len(sent) == 1
    url, payload = sent[0]
    assert url == "https://alerte.example/hook"
    assert payload["event"] == "BUDGET_KILL"
    # Le payload porte le coût AU MOMENT de la coupure (0.011) :
    assert payload["day_cost_usd"] == pytest.approx(0.011)
    assert payload["budget_usd"] == pytest.approx(0.01)
    assert payload["day"]
    # … et le compteur continue de s'alimenter après la coupure :
    assert b.status()["day_cost_usd"] == pytest.approx(0.016)


# ─── B10 — échec webhook sans effet sur la coupure ──────────────────────


def test_webhook_failure_does_not_break_kill(monkeypatch):
    def _boom(url, payload):
        raise RuntimeError("webhook down")

    monkeypatch.setattr(llm_budget, "_send_webhook", _boom)
    monkeypatch.setattr(settings, "LLM_DAILY_BUDGET_USD", 0.01)
    b = llm_budget.get_budget()
    b.record_cost(0.02)  # ne doit pas lever
    assert b.is_allowed("general") is False
    assert b.status()["day_cost_usd"] == pytest.approx(0.02)


# ─── B11 — métriques Prometheus ─────────────────────────────────────────


def _metric_value(text: str, name: str) -> float | None:
    for line in text.splitlines():
        if line.startswith(name + " "):
            return float(line.split()[-1])
    return None


def test_prometheus_metrics_follow_budget(monkeypatch):
    from prometheus_client import generate_latest

    monkeypatch.setattr(settings, "LLM_DAILY_BUDGET_USD", 0.01)
    b = llm_budget.get_budget()
    b.record_cost(0.004)
    text = generate_latest().decode()
    assert _metric_value(text, "llm_budget_day_cost_usd") == pytest.approx(0.004)
    assert _metric_value(text, "llm_budget_auto_killed") == 0.0

    kills_before = _metric_value(text, "llm_budget_kills_total") or 0.0
    b.record_cost(0.01)  # dépassement → coupure + kill
    text = generate_latest().decode()
    assert _metric_value(text, "llm_budget_auto_killed") == 1.0
    assert _metric_value(text, "llm_budget_kills_total") == pytest.approx(kills_before + 1.0)


# ─── B7 — état exposé dans /health ───────────────────────────────────────


async def test_health_exposes_llm_budget(client):
    r = await client.get("/health")
    assert r.status_code == 200
    st = r.json()["business"]["llm_budget"]
    for key in ("day", "day_cost_usd", "day_calls", "budget_usd",
                "auto_killed", "manual_kill", "killed_features"):
        assert key in st, f"clé manquante dans /health.llm_budget : {key}"
