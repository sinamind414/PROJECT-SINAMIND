"""
services/qcm_items.py — Charge les QCM extraits du programme officiel.

50 QCM extraits de programme_national_svt_claude_opus.md par
scripts/extract_qcm_from_programme.py. Chargés en mémoire au démarrage
( comme questions_db ) — zéro DB requise, cold start immédiat.

Ces QCM sont 100% conformes au programme national algérien SVT 3AS,
extraits ( pas générés ) — zéro hallucination, zéro coût IA.
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger("khawarizmi.qcm")

_data_dir = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
QCM_PATH = os.path.join(_data_dir, "qcm_items.json")

qcm_db: dict[str, dict[str, Any]] = {}

try:
    with open(QCM_PATH, encoding="utf-8") as f:
        _raw = json.load(f)
        for item in _raw:
            qid = item["id"]
            qcm_db[qid] = item
        logger.info(f"✅ {len(qcm_db)} QCM chargés depuis {QCM_PATH}")
except FileNotFoundError:
    logger.warning(f"⚠️ qcm_items.json introuvable ({QCM_PATH}) — drill QCM désactivé")
except Exception as e:
    logger.error(f"❌ Erreur chargement QCM ({QCM_PATH}): {e}")


def get_qcm(qcm_id: str) -> dict[str, Any] | None:
    return qcm_db.get(qcm_id)


def get_all_qcm_ids() -> list[str]:
    return list(qcm_db.keys())
