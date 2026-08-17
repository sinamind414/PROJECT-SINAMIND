# Verrouille la normalisation filière (conflation matière↔filière, corrigée 2026-08-17).
# Cas réels : « Sciences Expérimentales » (formulaire, avec accents) devait converger
# vers l'orthographe de la base « Sciences Experimentales » ; les libellés historiques
# (snv, sciences naturelles, sciences = défaut du schéma) sont ramenés à la filière SE.
import pytest

from routes.programme import normalize_filiere


@pytest.mark.parametrize(
    "entree, attendu",
    [
        ("Sciences Expérimentales", "Sciences Experimentales"),  # formulaire (accents)
        ("Sciences Experimentales", "Sciences Experimentales"),  # orthographe base
        ("sciences expérimentales", "Sciences Experimentales"),  # minuscules accentuées
        ("se", "Sciences Experimentales"),
        ("snv", "Sciences Experimentales"),
        ("sciences naturelles", "Sciences Experimentales"),  # matière, libellé historique
        ("sciences", "Sciences Experimentales"),  # ancien défaut du schéma user.py
    ],
)
def test_normalize_filiere_converge_vers_se(entree, attendu):
    assert normalize_filiere(entree) == attendu


def test_normalize_filiere_laisse_passer_autre_filiere():
    assert normalize_filiere("Mathématiques") == "Mathématiques"


def test_normalize_filiere_ignore_espaces():
    assert normalize_filiere("  se  ") == "Sciences Experimentales"
