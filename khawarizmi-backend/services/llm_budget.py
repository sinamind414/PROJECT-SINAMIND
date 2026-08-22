"""
services/llm_budget.py — Compteur de coût LLM journalier + kill-switch (G0-3)

L'audit 100k v2 constatait (reçu R13 + §B) : circuit breaker par provider
PRÉSENT, mais « alerte budgétaire globale, kill-switch par feature,
compteurs de coût par jour » ABSENTS. Ce module les fournit :

  1. COMPTEUR JOURNALIER — chaque appel LLM externe réussi enregistre son
     coût réel (usage tokens × grille tarifaire) dans le compteur du jour UTC
     ET dans cost_log.jsonl (cost_logger). Avant ce module, le coût réel
     n'était tracé NULLEPART en production (le logger existait sans aucun
     appelant).
  2. ALERTE + COUPURE AUTOMATIQUE — si le coût du jour dépasse
     LLM_DAILY_BUDGET_USD, le LLM externe est coupé pour le reste de la
     journée UTC (le fallback local du produit reste actif : sanity,
     savoir, pattern matching). Alerte CRITICAL structurée dans les logs :
     `BUDGET_KILL | jour=... | cout=... > budget=...`
     + alertes SORTANTES (une fois par journée de coupure) : Sentry
     (capture_message fatal, no-op si SENTRY_DSN absent), webhook optionnel
     BUDGET_ALERT_WEBHOOK (POST JSON, thread fond, 3 s), métriques
     Prometheus (llm_budget_day_cost_usd / llm_budget_auto_killed /
     llm_budget_kills_total via grading/observability).
  3. KILL-SWITCH MANUEL — LLM_KILL=1 (global) ou LLM_KILL_FEATURES="evaluate,…"
     (par feature), vérifiés à CHAQUE appel : effectif sans redémarrage,
     réversible sans redémarrage.

Sémantique : `is_allowed(feature)` est consulté en tête de
`_call_with_fallback` (services/llm.py) — la seule porte d'entrée du LLM
externe. Si refus → `LLMExternalDisabled` est levé AVANT tout appel
provider, et la chaîne de fallback existante (evaluate_with_fallback etc.)
basculle sur les étages locaux comme pour n'importe quel échec LLM —
le produit ne tombe jamais, il dégrade.
"""

from __future__ import annotations

import logging
import threading
from datetime import UTC, date, datetime

from config import get_settings

logger = logging.getLogger("khawazri.llm_budget")

# Horloge isolée pour les tests (patcher _now, pas datetime global).
def _now() -> datetime:
    return datetime.now(UTC)


class LLMExternalDisabled(Exception):
    """Le LLM externe est coupé (budget dépassé ou kill-switch manuel).

    Levé AVANT tout appel provider. Les chaînes de fallback existantes
    (except Exception) basculent sur les étages locaux — c'est une
    dégradation, pas une erreur produit."""


class LLMBudget:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._day: date = _now().date()
        self._day_cost_usd: float = 0.0
        self._day_calls: int = 0
        self._auto_killed: bool = False

    # ── interne ────────────────────────────────────────────────────────
    def _rollover_if_new_day(self) -> None:
        today = _now().date()
        if today != self._day:
            if self._auto_killed:
                logger.info(
                    f"🔓 BUDGET_REOPEN | jour={self._day} coupé → nouveau jour "
                    f"{today}, le LLM externe est réautorisé (compteur remis à 0)."
                )
            self._day = today
            self._day_cost_usd = 0.0
            self._day_calls = 0
            self._auto_killed = False

    @staticmethod
    def _budget_usd() -> float:
        cfg = get_settings()
        return float(cfg.LLM_DAILY_BUDGET_USD or 0.0)

    # ── API publique ───────────────────────────────────────────────────
    def record_cost(self, cost_usd: float, model: str = "") -> None:
        """Enregistre le coût d'un appel LLM externe réussi (jour UTC)."""
        killed_now = False
        budget = 0.0
        with self._lock:
            self._rollover_if_new_day()
            self._day_cost_usd += cost_usd
            self._day_calls += 1
            budget = self._budget_usd()
            if (
                budget > 0
                and not self._auto_killed
                and self._day_cost_usd >= budget
            ):
                self._auto_killed = True
                killed_now = True
                logger.critical(
                    f"🛑 BUDGET_KILL | jour={self._day} | "
                    f"cout={self._day_cost_usd:.4f} USD >= budget={budget:.4f} USD "
                    f"(modèle={model or '?'}, {self._day_calls} appels) → LLM externe "
                    f"COUPÉ jusqu'à minuit UTC. Fallback local actif. "
                    f"Réouverture : attendre le jour suivant ou réinitialiser "
                    f"(get_budget().reset())."
                )
        # Hors verrou : métriques + alertes sortantes (best-effort).
        self._notify_external(killed_now, budget, model)

    def _notify_external(self, killed_now: bool, budget: float, model: str) -> None:
        """Métriques Prometheus + alertes sortantes (Sentry/webhook).
        Tout est best-effort : un échec d'alerte ne doit jamais affecter
        la comptabilité ou la coupure."""
        try:
            from grading.observability import (
                observe_llm_budget,
                record_budget_kill,
            )

            with self._lock:
                day_cost, killed = self._day_cost_usd, self._auto_killed
            observe_llm_budget(day_cost, killed)
            if killed_now:
                record_budget_kill()
        except Exception as e:  # métriques = best-effort
            logger.debug(f"budget_metrics_skip | {e!s}")
        if killed_now:
            _emit_kill_alert(self, model, budget)

    def is_allowed(self, feature: str = "general") -> bool:
        """Doit-on autoriser un appel LLM externe pour cette feature ?"""
        cfg = get_settings()
        if cfg.LLM_KILL:
            return False
        killed_features = {
            f.strip() for f in cfg.LLM_KILL_FEATURES.split(",") if f.strip()
        }
        if feature in killed_features:
            return False
        with self._lock:
            self._rollover_if_new_day()
            return not self._auto_killed

    def status(self) -> dict:
        """État courant — exposé dans /health (R18)."""
        with self._lock:
            self._rollover_if_new_day()
            return {
                "day": str(self._day),
                "day_cost_usd": round(self._day_cost_usd, 6),
                "day_calls": self._day_calls,
                "budget_usd": self._budget_usd(),
                "auto_killed": self._auto_killed,
                "manual_kill": bool(get_settings().LLM_KILL),
                "killed_features": [
                    f.strip()
                    for f in get_settings().LLM_KILL_FEATURES.split(",")
                    if f.strip()
                ],
            }

    def reset(self) -> None:
        """Réinitialisation (tests / administration après incident)."""
        with self._lock:
            self._day = _now().date()
            self._day_cost_usd = 0.0
            self._day_calls = 0
            self._auto_killed = False


def _emit_kill_alert(budget_obj: LLMBudget, model: str, limit_usd: float) -> None:
    """Alertes SORTANTES sur BUDGET_KILL (G0-3) — une fois par jour de coupure.

    1) Sentry : capture_message niveau fatal (no-op si SENTRY_DSN absent).
    2) Webhook : POST JSON sur BUDGET_ALERT_WEBHOOK si défini (Telegram,
       Discord, n8n, Bark…) — thread fond, timeout 3 s.
    Best-effort : aucun échec d'alerte n'affecte la coupure elle-même.
    """
    message = (
        f"BUDGET_KILL | jour={budget_obj._day} | "
        f"cout={budget_obj._day_cost_usd:.4f} USD >= budget={limit_usd:.4f} USD "
        f"| modele={model or '?'}"
    )
    try:
        import sentry_sdk

        sentry_sdk.capture_message(message, level="fatal")
    except Exception:
        pass
    url = get_settings().BUDGET_ALERT_WEBHOOK
    if url:
        _send_webhook(
            url,
            {
                "event": "BUDGET_KILL",
                "day": str(budget_obj._day),
                "day_cost_usd": round(budget_obj._day_cost_usd, 6),
                "budget_usd": limit_usd,
                "model": model,
            },
        )


def _send_webhook(url: str, payload: dict) -> None:
    """POST best-effort en arrière-plan (daemon, 3 s) — ne bloque jamais
    le chemin d'appel LLM."""

    def _run() -> None:
        try:
            import httpx

            r = httpx.post(url, json=payload, timeout=3.0)
            if r.status_code >= 400:
                logger.warning(f"⚠️ BUDGET_ALERT_WEBHOOK → HTTP {r.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ BUDGET_ALERT_WEBHOOK injoignable : {e}")

    threading.Thread(target=_run, name="budget-alert-webhook", daemon=True).start()


_budget: LLMBudget | None = None
_budget_lock = threading.Lock()


def get_budget() -> LLMBudget:
    global _budget
    if _budget is None:
        with _budget_lock:
            if _budget is None:
                _budget = LLMBudget()
    return _budget
