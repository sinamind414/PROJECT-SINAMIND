"""Tests du correctif d'alias unité 5 (bug 2026-08-20).

VERB_UNIT_MAP/PRACTICAL_EXAMPLES utilisent « unite5-energie », ALL_UNITS
utilise « unite5-energetique ». Avant correctif, les erreurs/connaissances
de l'unité 5 étaient silencieusement absentes de la remédiation.
"""

from __future__ import annotations

from prompts.scientific_knowledge import (
    build_knowledge_block,
    get_contextual_remediation_data,
    get_practical_examples,
    get_unit_specific_errors,
)


def test_unite5_alias_resout_les_memes_erreurs() -> None:
    alias = get_unit_specific_errors("unite5-energie")
    canonique = get_unit_specific_errors("unite5-energetique")
    assert alias, "l'alias unite5-energie doit résoudre des erreurs (non vides)"
    assert alias == canonique


def test_build_knowledge_block_accepte_l_alias() -> None:
    bloc = build_knowledge_block(["unite5-energie"])
    assert bloc, "le bloc de connaissance de l'unité 5 doit être non vide via l'alias"
    assert bloc == build_knowledge_block(["unite5-energetique"])


def test_practical_examples_accepte_l_alias() -> None:
    assert get_practical_examples(unit="unite5-energie") == get_practical_examples(
        unit="unite5-energetique"
    )


def test_remediation_inclut_les_erreurs_energetiques() -> None:
    data = get_contextual_remediation_data("interpret", "")
    erreurs = "\n".join(data["relevant_errors"])
    # Les erreurs unité 5 (photosynthèse/énergie) doivent maintenant apparaître.
    assert "ضوء" in erreurs
    # et l'identifiant alias reste présent dans units (compatibilité tests existants)
    assert "unite5-energie" in data["units"]
