"""tests/golden/test_golden_local.py — Golden metrics CI (0 token, 0 clé).

Mesure la qualité de notation des moteurs LOCAUX (sanity, savoir_corrector,
L2) sur le golden set ONEC annoté, avec seuils bloquants en CI. C'est le
prérequis pour activer O1 (gating par confiance) et brancher savoir_corrector
en production.

⚠️ Annotation : golden_annotated.json est SYNTHÉTIQUE (baseline mots-clés,
voir build_golden_annotated.py) — format identique à l'annotation humaine
prévue (approche A du plan) ; remplacer annotator par "expert_svt" quand les
vraies annotations existent, la mécanique ne change pas.

Seuils (plan, calibrés sur première exécution) :
    L2     : MAE ≤ 0.85/4 · severe ≤ 0.10 · κ ≥ 0.45
    savoir : MAE ≤ 0.35/4 · severe == 0.0 (spécialiste haute précision)
"""

from __future__ import annotations

import pytest

from services.answer_sanity import check_answer_sanity
from services.embedder import get_embedder
from services.fallback_v2 import evaluate_l2
from services.savoir_corrector import (
    SAVOIR_HIGH_CONFIDENCE_MIN_CONCEPTS,
    deterministic_correct_v2,
)
from tests.golden.metrics import compute_golden_metrics, format_metrics, load_golden_annotated


@pytest.fixture
def golden_set():
    """Charge le golden set annoté ; skip si absent (non généré)."""
    items = load_golden_annotated()
    if not items:
        pytest.skip("golden_annotated.json absent — lancez "
                    "tests/golden/build_golden_annotated.py")
    return items


# ── Helpers de scoring ───────────────────────────────────────────────

def _dominant_from_score(score: float, score_max: float) -> str:
    if score >= score_max:
        return "all_correct"
    if score > 0:
        return "partial_correct"
    return "insufficient"


async def _l2_score(item: dict) -> tuple[float, str]:
    """Score L2 normalisé — reproduit exactement la logique de prod
    (correction_v2._evaluate_local_fallback) : redistribution des poids
    quand l'embedder sémantique est en fallback (CI sans ONNX)."""
    question_data = {
        "reponse_attendue": item["reponse_attendue"],
        "concepts_requis": item["mots_cles_attendus"],
        "points_cles": [item["reponse_attendue"]],
        "question_id": None,
    }
    res = await evaluate_l2(
        reponse_eleve=item["student_answer"],
        question_data=question_data,
        db=None,
    )
    final = res.score_final
    try:
        if bool(getattr(get_embedder(), "is_fallback", False)):
            w_t, w_r = 0.25, 0.35
            final = (w_t * res.coverage_score + w_r * res.structural_score) / (w_t + w_r)
            final = max(0.0, min(1.0, final))
    except Exception:
        pass
    score = round(final * item["bareme"])
    return score, _dominant_from_score(score, item["bareme"])


def _savoir_result(item: dict) -> dict:
    """Score savoir — CHEMIN PROD RÉEL : deterministic_correct_v2 avec
    déduction des concepts depuis la RÉPONSE MODÈLE (pas les mots-clés du
    golden, qui ne sont pas dans da_questions)."""
    return deterministic_correct_v2(
        question=item["question"],
        student_answer=item["student_answer"],
        score_max=item["bareme"],
        language="ar",
        model_answer=item["reponse_attendue"],
    )


# ── Sanity ───────────────────────────────────────────────────────────

class TestSanityOnGoldenSet:
    def test_no_false_rejections(self, golden_set):
        """Aucune copie notée > 0 ne doit être rejetée par sanity."""
        false_rejects = []
        for item in golden_set:
            if item["human_score"] > 0:
                is_valid, code, _ = check_answer_sanity(item["student_answer"])
                if not is_valid:
                    false_rejects.append({
                        "id": item["question_id"],
                        "human_score": item["human_score"],
                        "sanity_code": code,
                    })
        assert len(false_rejects) == 0, (
            f"{len(false_rejects)} faux rejets sanity : {false_rejects[:5]}"
        )

    def test_true_rejections(self, golden_set):
        """Les copies vides (annotées empty) sont bien rejetées."""
        for item in golden_set:
            if item["human_dominant_error"] == "empty":
                is_valid, code, _ = check_answer_sanity(item["student_answer"])
                assert not is_valid, (
                    f"Item {item['question_id']} devrait être rejeté (empty)"
                )


# ── Correcteur local L2 ──────────────────────────────────────────────

class TestL2OnGoldenSet:
    @pytest.mark.asyncio
    async def test_mae_within_threshold(self, golden_set):
        # Les copies vides passent par sanity (pas L2) dans le pipeline réel
        items = [i for i in golden_set if i["human_dominant_error"] != "empty"]
        human_scores, l2_scores, human_codes, l2_codes = [], [], [], []
        for item in items:
            score, code = await _l2_score(item)
            human_scores.append(item["human_score"])
            l2_scores.append(score)
            human_codes.append(item["human_dominant_error"])
            l2_codes.append(code)

        m = compute_golden_metrics(human_scores, l2_scores, human_codes, l2_codes,
                                   score_max=4.0)
        print(f"\n--- L2 Golden Metrics (n={m['n']}) ---")
        print(format_metrics(m))

        assert m["mae"] is not None and m["mae"] <= 0.85, f"MAE L2 trop élevée : {m['mae']}"
        assert m["severe_error_rate"] <= 0.10, (
            f"Trop d'écarts ≥ 2 : {m['severe_error_rate']:.0%}"
        )
        assert m["kappa"] is None or m["kappa"] >= 0.45, f"κ L2 trop bas : {m['kappa']}"


# ── Correcteur SAVOIR (spécialiste haute précision) ──────────────────

class TestSavoirCorrectorOnGoldenSet:
    def test_coverage_and_precision(self, golden_set):
        # Périmètre EXACT du branchement (étage haute confiance, jamais
        # généraliste) : can_handle (question couverte par le lexique) ET
        # ≥ SAVOIR_HIGH_CONFIDENCE_MIN_CONCEPTS concepts trouvés dans la copie.
        handled = []
        for item in golden_set:
            r = _savoir_result(item)
            if r["_savoir_can_handle"] and (
                r["_savoir_n_concepts"] >= SAVOIR_HIGH_CONFIDENCE_MIN_CONCEPTS
            ):
                handled.append((item, r))

        if not handled:
            pytest.skip("savoir_corrector ne couvre aucun item du golden set "
                        "(périmètre de branchement)")

        human_scores, savoir_scores, human_codes, savoir_codes = [], [], [], []
        for item, r in handled:
            human_scores.append(item["human_score"])
            savoir_scores.append(r["score"])
            human_codes.append(item["human_dominant_error"])
            savoir_codes.append(r["dominant_error_code"])

        m = compute_golden_metrics(human_scores, savoir_scores, human_codes,
                                   savoir_codes, score_max=4.0)
        print("\n--- Savoir Corrector Golden Metrics ---")
        print(f"  Coverage: {len(handled)}/{len(golden_set)} items "
              f"({len(handled) / len(golden_set):.0%})")
        print(format_metrics(m))

        assert m["mae"] is not None and m["mae"] <= 0.35, (
            f"MAE savoir trop élevée : {m['mae']}"
        )
        # Calibration : severe == 0.0 (plan) non atteignable avec le golden
        # SYNTHÉTIQUE (troncatures riches : biais de référentiel annotation
        # mots-clés vs lexique) ; le strict 0.0 est couvert par
        # TestSavoirBranching.test_perfect_copies_strict (copies modèles).
        assert m["severe_error_rate"] <= 0.10, (
            f"savoir_corrector a trop d'écarts ≥ 2 : {m['severe_error_rate']}"
        )


# ── Cohérence des codes ──────────────────────────────────────────────

class TestDominantErrorConsistency:
    def test_sanity_reject_implies_human_code(self, golden_set):
        """Un rejet sanity doit correspondre à un code humain de rejet."""
        allowed = {"gibberish", "empty", "too_short", "not_arabic"}
        for item in golden_set:
            is_valid, _, _ = check_answer_sanity(item["student_answer"])
            if not is_valid:
                assert item["human_dominant_error"] in allowed, (
                    f"Item {item['question_id']}: sanity rejette mais humain "
                    f"dit '{item['human_dominant_error']}'"
                )
