"""
services/definition_cards.py — Charge les cartes définition depuis micro_concepts.json

Injecte les concepts définition dans questions_db avec kind="definition".
Format injecté :
  {
    "question_id": "mcd_001",
    "texte": "عرّف: مفهوم الخلية",
    "texte_ar": "عرّف: مفهوم الخلية",
    "reponse_attendue": "مفهوم الخلية هو الوحدة الأساسية للحياة، ...",
    "concept_cle": "مفهوم الخلية",
    "concept_cle_ar": "مفهوم الخلية",
    "micro_concept_id": "mc_001",
    "kind": "definition",
    "source": "programme_officiel_svt"
  }
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger("khawarizmi.definition_cards")

# Résolution du chemin du fichier de concepts
_data_dir = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
MICRO_CONCEPTS_PATH = os.path.join(_data_dir, "micro_concepts.json")

MIN_DEF_LEN = 25  # Longueur minimale pour considérer une définition exploitable


def load_definition_cards() -> List[Dict[str, Any]]:
    """Charge les cartes définition depuis micro_concepts.json."""
    if not Path(MICRO_CONCEPTS_PATH).exists():
        logger.warning(f"Fichier micro_concepts.json introuvable ({MICRO_CONCEPTS_PATH})")
        return []

    try:
        with open(MICRO_CONCEPTS_PATH, encoding="utf-8") as f:
            concepts = json.load(f)

        cards = []
        for concept in concepts:
            definition = concept.get("definition", "").strip()
            if len(definition) < MIN_DEF_LEN:
                continue

            card = {
                "question_id": f"mcd_{concept['id'][3:]}",  # mc_001 → mcd_001
                "texte": f"عرّف: {concept['label']}",
                "texte_ar": f"عرّف: {concept['label']}",
                "reponse_attendue": definition,
                "concept_cle": concept["label"],
                "concept_cle_ar": concept["label"],
                "micro_concept_id": concept["id"],
                "kind": "definition",
                "source": concept.get("source", "programme_officiel_svt"),
                "unit": concept.get("unit", ""),
                "domain": concept.get("domain", ""),
                "unit_slug": concept.get("unit_slug", ""),
            }
            cards.append(card)

        logger.info(f"✅ {len(cards)} cartes définition chargées depuis {MICRO_CONCEPTS_PATH}")
        return cards

    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement des cartes définition ({MICRO_CONCEPTS_PATH}): {e}")
        return []