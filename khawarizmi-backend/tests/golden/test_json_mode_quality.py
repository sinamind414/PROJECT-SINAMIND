"""tests/golden/test_json_mode_quality.py — Test NIGHTLY (audit O7).

⚠️ Nécessite un appel LLM réel : skippé en CI et sans clé API configurée.
Objectif : vérifier que le JSON natif ne dégrade pas la qualité de notation
vs mode texte libre (le piège O7 : certains modèles notent mieux en libre).

Le golden set ONEC n'a pas de scores humains de référence (champs observés :
question, reponse_attendue, mots_cles_attendus, bareme, type) → baseline =
scores du mode texte libre (test de non-régression, pas de justesse absolue),
comme prévu par le plan.

Seuils :
    MAE(json, free) ≤ 0.15 (échelle ratio score/score_max)
    std(json) ≥ 0.70 × std(free)  (pas de notes "plates" — discrimination)

Usage :
    ENABLE_EXTERNAL_LLM=1 OPENAI_API_KEY=... pytest tests/golden/test_json_mode_quality.py -m nightly
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from config import get_settings
from services.correction_v2 import evaluate_answer_v2
from services.llm import _call_with_fallback

# ── Skip nightly : CI ou aucune clé réelle ───────────────────────────

_HAS_REAL_KEY = any(
    os.environ.get(k) and os.environ.get(k) != "test-gemini-key"
    for k in ("OPENAI_API_KEY", "GEMINI_API_KEY",
              "OPENAI_FALLBACK_API_KEY", "REAL_OPENAI_API_KEY")
)

pytestmark = [
    pytest.mark.nightly,
    pytest.mark.skipif(
        os.environ.get("ENVIRONMENT") == "ci" or not _HAS_REAL_KEY,
        reason="nightly : nécessite une clé LLM réelle (hors CI)",
    ),
]


def _load_golden() -> list[dict]:
    path = Path(__file__).parent.parent.parent / "data" / "golden_set_onec.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["questions"]


def _item_to_kwargs(item: dict) -> dict:
    return {
        "scenario_context": item.get("chapitre", ""),
        "documents": None,
        "question_prompt": item.get("question", ""),
        "question_skill": item.get("niveau", "L2"),
        "verb_slug": item.get("type", "restitution"),
        "model_answer": item.get("reponse_attendue", ""),
        "learning_focus": None,
        "score_max": item.get("bareme", 2),
        "use_v2_prompt": True,
        "local_fallback": False,  # night : on veut le VRAI LLM
    }


# Providers JSON-capables pour le test nightly (openai/groq/gemini/zai) —
# l'activation progressive par provider (point O7-1) ne change rien ici : on
# teste la qualité des DEUX modes sur l'ensemble des providers compatibles.
_JSON_CAPABLE = ["openai", "groq", "gemini", "zai"]


async def _grade(item: dict, json_native: bool) -> dict:
    """Corrige une copie modèle (réponse correcte) — mode natif ou libre.

    Le mode est contrôlé par la liste config json_mode_providers (activation
    par provider, point O7-1) ; on la bascule par appel avec restauration en
    finally (settings est un singleton — on ne veut pas fuiter l'état).
    """
    from openai import AsyncOpenAI

    cfg = get_settings()
    previous = list(cfg.json_mode_providers)
    cfg.json_mode_providers = list(_JSON_CAPABLE) if json_native else []
    try:
        client = AsyncOpenAI(api_key=cfg.OPENAI_API_KEY, base_url=cfg.openai_base_url)
        result = await evaluate_answer_v2(
            **_item_to_kwargs(item),
            student_answer=item.get("reponse_attendue", ""),
            llm_call=_call_with_fallback,
            primary_client=client,
            primary_model=cfg.openai_model,
        )
        return result
    finally:
        cfg.json_mode_providers = previous


def _ratio(result: dict) -> float:
    smax = result.get("score_max") or 1
    return result.get("score", 0) / smax


@pytest.mark.asyncio
async def test_json_mode_no_quality_regression():
    """Nightly : MAE et discrimination JSON natif vs texte libre.

    Baseline = mode texte libre (pas de scores humains dans le golden set).
    """
    items = _load_golden()[:10]  # 10 items × 2 appels = 20 appels LLM (nightly)

    scores_free: list[float] = []
    scores_json: list[float] = []
    for item in items:
        r_free = await _grade(item, json_native=False)
        r_json = await _grade(item, json_native=True)
        assert r_free["source"] != "llm_error", f"free a échoué: {item['id']}"
        assert r_json["source"] != "llm_error", f"json a échoué: {item['id']}"
        scores_free.append(_ratio(r_free))
        scores_json.append(_ratio(r_json))

    # MAE entre modes (baseline free) — le JSON natif ne doit pas être
    # significativement pire : ≤ 0.15 sur l'échelle ratio.
    mae = sum(abs(a - b) for a, b in zip(scores_json, scores_free)) / len(scores_free)
    assert mae <= 0.15, (
        f"JSON natif dégrade la notation : MAE {mae:.3f} > 0.15"
    )

    # La variance ne doit pas s'effondrer (notes "plates")
    mean_free = sum(scores_free) / len(scores_free)
    mean_json = sum(scores_json) / len(scores_json)
    std_free = (sum((s - mean_free) ** 2 for s in scores_free) / len(scores_free)) ** 0.5
    std_json = (sum((s - mean_json) ** 2 for s in scores_json) / len(scores_json)) ** 0.5
    assert std_json >= std_free * 0.70, (
        f"JSON natif aplatit les notes : std {std_json:.3f} vs {std_free:.3f}"
    )


@pytest.mark.asyncio
async def test_json_mode_end_to_end():
    """Nightly : evaluate_answer_v2 en mode natif → parse_status ok (v2)."""
    item = _load_golden()[0]
    result = await _grade(item, json_native=True)
    assert result["source"] in ("llm", "llm_v2", "llm_retried")
    assert result["score"] is not None
    assert 0 <= result["score"] <= result["score_max"]
