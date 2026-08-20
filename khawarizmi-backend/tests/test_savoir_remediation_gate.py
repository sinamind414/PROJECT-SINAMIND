"""Gate de remédiation savoir — config.savoir_remediation_enabled.

Le processus golden (scripts/golden_human_report.py) mesure κ savoir ≥ 0.65
→ « RÉACTIVER la remédiation savoir ». Mesure 2026-08-20 : κ = 0.858
(MAE 0.279, exact 0.791 sur la baseline synthétique) → verdict RÉACTIVER.

Défaut False : comportement historique inchangé (remediation=None,
raison local_savoir_no_remediation — verrouillé par le test gelé
test_savoir_branching.py). Activation = SAVOIR_REMEDIATION_ENABLED=true :
la remédiation réutilise la matrice du chemin LLM
(services.remediation_service) pour un payload identique.
"""
from __future__ import annotations

import pytest

from config import get_settings
from grading.savoir import run_savoir

Q = "أين يحدث نسخ المعلومة الوراثية في الخلية حقيقية النواة؟"
MODEL = "يحدث نسخ المعلومة الوراثية في النواة حيث تتواجد جزيئة ADN"
GOOD = MODEL  # copie modèle : promotion savoir garantie (≥ 3 concepts)


@pytest.fixture
def savoir_verb_active(monkeypatch):
    monkeypatch.setattr(get_settings(), "savoir_enabled_verbs", ["analyse"])
    monkeypatch.setattr(get_settings(), "savoir_remediation_enabled", False)
    yield
    monkeypatch.setattr(get_settings(), "savoir_enabled_verbs", [])
    monkeypatch.setattr(get_settings(), "savoir_remediation_enabled", False)


def test_defaut_aucune_remediation(savoir_verb_active) -> None:
    r = run_savoir(question=Q, student_answer=GOOD, verb_slug="analyse", score_max=2, model_answer=MODEL)
    assert r is not None
    assert r["finish_reason"] == "savoir_high_confidence"
    assert r["remediation"] is None
    assert r["remediation_reason"] == "local_savoir_no_remediation"


def test_flag_actif_branche_la_matrice(monkeypatch, savoir_verb_active) -> None:
    """Flag ON → la remédiation vient de la matrice (même chemin que le LLM)."""
    fake_remediation = {"page": 8, "lesson_title": "أسرار العلامة الكاملة", "advice_ar": "راجع الصفحة 8."}
    monkeypatch.setattr(get_settings(), "savoir_remediation_enabled", True)
    monkeypatch.setattr(
        "services.remediation_service.get_remediation",
        lambda verb_slug, error_code: fake_remediation if error_code else None,
    )
    r = run_savoir(question=Q, student_answer=GOOD, verb_slug="analyse", score_max=2, model_answer=MODEL)
    assert r is not None
    assert r["remediation"] == fake_remediation
    assert r["remediation_reason"] == "local_savoir_lexique"


def test_flag_actif_sans_entree_matrice_retombe_silencieusement(monkeypatch, savoir_verb_active) -> None:
    """Flag ON mais code sans remédiation → None + raison historique (honnête)."""
    monkeypatch.setattr(get_settings(), "savoir_remediation_enabled", True)
    monkeypatch.setattr("services.remediation_service.get_remediation", lambda v, e: None)
    monkeypatch.setattr("services.remediation_service.get_generic_remediation", lambda e: None)
    r = run_savoir(question=Q, student_answer=GOOD, verb_slug="analyse", score_max=2, model_answer=MODEL)
    assert r is not None
    assert r["remediation"] is None
    assert r["remediation_reason"] == "local_savoir_no_remediation"


def test_faute_conceptuelle_donne_remediation_reelle(savoir_verb_active) -> None:
    """Chaîne réelle : copie avec erreur conceptuelle → scientific_error →
    remédiation (matrice du verbe, sinon générique) quand le flag est ON."""
    from services.remediation_service import get_generic_remediation, get_remediation

    get_settings().savoir_remediation_enabled = True
    try:
        faulty = "نسخ المعلومة الوراثية يحدث في النواة حيث تتواجد جزيئة ADN لكن الترجمة تتم في الهيولى"
        r = run_savoir(question=Q, student_answer=faulty, verb_slug="analyse", score_max=2, model_answer=MODEL)
        assert r is not None
        assert r["dominant_error_code"] == "scientific_error"
        expected = get_remediation("analyse", "scientific_error") or get_generic_remediation("scientific_error")
        assert expected is not None
        assert r["remediation"] == expected
        assert r["remediation_reason"] == "local_savoir_lexique"
    finally:
        get_settings().savoir_remediation_enabled = False
