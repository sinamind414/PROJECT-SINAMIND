"""tests/golden/metrics.py — Métriques de qualité de notation (golden CI).

Calcule MAE, accord exact, écarts graves, biais, Cohen κ et ratio de
variance entre scores humains et scores système. Utilisé par
tests/golden/test_golden_local.py (CI, 0 token) et test_golden_llm.py (nightly).

Seuils bloquants (calibrés après première exécution, marge +20 %) :
    L2     : MAE ≤ 0.85/4 · severe ≤ 0.10 · κ ≥ 0.45
    savoir : MAE ≤ 0.35/4 · severe == 0.0 (spécialiste haute précision)
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import cohen_kappa_score, mean_absolute_error

GOLDEN_ANNOTATED = Path(__file__).parent / "golden_annotated.json"
GOLDEN_ONEC = Path(__file__).parent.parent.parent / "data" / "golden_set_onec.json"


def load_golden_annotated() -> list[dict]:
    """Charge le golden set annoté (scores humains de référence).

    S'il est absent (pas encore généré), retourne [] — les tests CI skippent.
    """
    if not GOLDEN_ANNOTATED.exists():
        return []
    data = json.loads(GOLDEN_ANNOTATED.read_text(encoding="utf-8"))
    return data.get("items", data if isinstance(data, list) else [])


def load_golden_onec() -> dict:
    return json.loads(GOLDEN_ONEC.read_text(encoding="utf-8"))


def compute_golden_metrics(
    human_scores: list[float],
    system_scores: list[float],
    human_codes: list[str],
    system_codes: list[str],
    score_max: float = 4.0,
) -> dict:
    """Calcule toutes les métriques de qualité de notation."""
    n = len(human_scores)
    assert n == len(system_scores), "tailles de scores incohérentes"
    # Les listes de codes peuvent être vides (appel sans codes : κ = None)
    has_codes = len(human_codes) == n == len(system_codes) and n > 0
    if n == 0:
        return {"n": 0, "mae": None, "exact_match": None, "severe_error_rate": None,
                "bias": None, "kappa": None, "std_ratio": None}

    mae = mean_absolute_error(human_scores, system_scores)

    exact_match = sum(
        1 for h, s in zip(human_scores, system_scores) if round(h) == round(s)
    ) / n

    severe_errors = sum(
        1 for h, s in zip(human_scores, system_scores) if abs(h - s) >= 2.0
    ) / n

    bias = float(np.mean(np.asarray(system_scores) - np.asarray(human_scores)))

    # Cohen κ : nécessite des codes fournis ET ≥ 2 classes, sinon None
    kappa = None
    if has_codes:
        try:
            if len(set(human_codes) | set(system_codes)) >= 2:
                kappa = float(cohen_kappa_score(human_codes, system_codes))
        except ValueError:
            kappa = None

    std_h = float(np.std(human_scores))
    std_ratio = float(np.std(system_scores) / max(std_h, 0.01))

    return {
        "n": n,
        "mae": round(mae, 3),
        "exact_match": round(exact_match, 3),
        "severe_error_rate": round(severe_errors, 3),
        "bias": round(bias, 3),
        "kappa": round(kappa, 3) if kappa is not None else None,
        "std_ratio": round(std_ratio, 3),
    }


def format_metrics(m: dict) -> str:
    """Format multi-ligne pour l'affichage dans les tests."""
    lines = [f"  n={m['n']}  MAE={m['mae']}  exact={m['exact_match']}  "
             f"severe={m['severe_error_rate']}  bias={m['bias']}"]
    lines.append(f"  κ={m['kappa']}  std_ratio={m['std_ratio']}")
    return "\n".join(lines)
