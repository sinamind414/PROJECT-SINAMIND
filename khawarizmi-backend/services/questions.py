import json
import logging
import os
from typing import Dict, Any

logger = logging.getLogger("khawarizmi.questions")

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'annales_sciences_3as.json')
questions_db: Dict[str, Any] = {}

try:
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        annales = json.load(f)
        for sujet in annales:
            for exercice in sujet.get('exercices', []):
                for q in exercice.get('questions', []):
                    questions_db[q['question_id']] = q
    logger.info(f"✅ {len(questions_db)} questions charges en mmoire.")
except Exception as e:
    logger.error(f"❌ Erreur lors du chargement des questions: {e}")

def get_question(question_id: str) -> Dict[str, Any]:
    return questions_db.get(question_id, None)

def get_all_question_ids() -> list:
    return list(questions_db.keys())
