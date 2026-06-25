import json
import logging
import os
from typing import Any

logger = logging.getLogger("khawarizmi.questions")

# Résolution du chemin du fichier de questions
# 1. Variable d'environnement DATA_DIR (Docker / production)
# 2. Fallback : chemin relatif (développement local)
_data_dir = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
ANNALES_PATH = os.path.join(_data_dir, "annales_sciences_3as.json")
TAGGEES_PATH = os.path.join(_data_dir, "questions_taggees.json")

questions_db: dict[str, Any] = {}

# --- Chargement des annales classiques (134 questions) ---
try:
    with open(ANNALES_PATH, encoding="utf-8") as f:
        annales = json.load(f)
        for sujet in annales:
            for exercice in sujet.get("exercices", []):
                for q in exercice.get("questions", []):
                    questions_db[q["question_id"]] = q
    logger.info(f"✅ {len(questions_db)} questions chargées depuis {ANNALES_PATH}")
except Exception as e:
    logger.error(f"❌ Erreur lors du chargement des annales ({ANNALES_PATH}): {e}")

# --- Chargement des questions taggées OCR (234 questions) ---
_count_before = len(questions_db)
try:
    with open(TAGGEES_PATH, encoding="utf-8") as f:
        taggees = json.load(f)
        for q in taggees:
            # Normalisation vers le format attendu par le backend
            question_id = q["id"]
            questions_db[question_id] = {
                "question_id": question_id,
                "texte": q.get("texte_corrige", ""),
                "texte_ar": q.get("texte_corrige", ""),
                "reponse_attendue": "",
                "concept_cle": q.get("micro_concept_id", ""),
                "concept_cle_ar": q.get("micro_concept_id", ""),
                "pattern_recherche": "",
                # Champs supplémentaires des questions taggées
                "micro_concept_id": q.get("micro_concept_id", ""),
                "secondary_concepts": q.get("secondary_concepts", []),
                "source": q.get("source", ""),
                "type": q.get("type", ""),
                "difficulte": q.get("difficulte", ""),
                "bac_frequent": q.get("bac_frequent", False),
                "notes": q.get("notes", ""),
            }
    _added = len(questions_db) - _count_before
    logger.info(f"✅ {_added} questions taggées chargées depuis {TAGGEES_PATH}")
except FileNotFoundError:
    logger.warning(f"⚠️ Fichier questions_taggees.json introuvable ({TAGGEES_PATH})")
except Exception as e:
    logger.error(f"❌ Erreur lors du chargement des questions taggées ({TAGGEES_PATH}): {e}")

logger.info(f"📊 Total questions en mémoire : {len(questions_db)}")


def get_question(question_id: str) -> dict[str, Any]:
    q = questions_db.get(question_id)
    if q:
        # Garantir les champs bilingues (texte_ar initial = texte si pas encore traduit)
        if "texte_ar" not in q:
            q["texte_ar"] = q.get("texte", "")
        if "concept_cle_ar" not in q:
            q["concept_cle_ar"] = q.get("concept_cle", "")
    return q


def get_all_question_ids() -> list[str]:
    return list(questions_db.keys())


def get_questions_by_micro_concept(mc_id: str) -> list[str]:
    """Retourne les question_ids liés à un micro-concept donné."""
    return [
        qid
        for qid, q in questions_db.items()
        if q.get("micro_concept_id") == mc_id or mc_id in q.get("secondary_concepts", [])
    ]
