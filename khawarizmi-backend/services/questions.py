import json
import logging
import os
from typing import Dict, Any, List

logger = logging.getLogger("khawarizmi.questions")

# Résolution du chemin du fichier de questions
# 1. Variable d'environnement DATA_DIR (Docker / production)
# 2. Fallback : chemin relatif (développement local)
_data_dir = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), '..', 'data'))
DATA_PATH = os.path.join(_data_dir, 'annales_sciences_3as.json')

questions_db: Dict[str, Any] = {}

try:
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        annales = json.load(f)
        for sujet in annales:
            for exercice in sujet.get('exercices', []):
                for q in exercice.get('questions', []):
                    questions_db[q['question_id']] = q
    logger.info(f"✅ {len(questions_db)} questions chargées en mémoire depuis {DATA_PATH}")
except Exception as e:
    logger.error(f"❌ Erreur lors du chargement des questions ({DATA_PATH}): {e}")

def get_question(question_id: str) -> Dict[str, Any]:
    q = questions_db.get(question_id, None)
    if q:
        # Garantir les champs bilingues (texte_ar initial = texte si pas encore traduit)
        if 'texte_ar' not in q:
            q['texte_ar'] = q.get('texte', '')
        if 'concept_cle_ar' not in q:
            q['concept_cle_ar'] = q.get('concept_cle', '')
    return q

def get_all_question_ids() -> List[str]:
    return list(questions_db.keys())
