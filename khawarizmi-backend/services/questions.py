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

# Mots-clés indiquant qu'une question nécessite une figure/courbe/schéma absent
_FIGURE_KEYWORDS = (
    "figure", "courbe", "schéma", "schema", "dessin", "graphique",
    "document", "tableau", "وثيقة", "شكل", "منحنى", "تمثيل",
    "الوثيقة", "الشكل", "المنحنى", "التمثيل",
)


def _text_references_figure(text: str) -> bool:
    """Détecte si le texte référence une figure/courbe/schéma non disponible."""
    lower = text.lower()
    return any(kw in lower for kw in _FIGURE_KEYWORDS)


# --- Chargement des annales classiques (134 questions) ---
try:
    with open(ANNALES_PATH, encoding="utf-8") as f:
        annales = json.load(f)
        _residuelles = 0
        _filtrees_figure = 0
        for sujet in annales:
            # Les question_id bruts (ex. q_0) sont uniques PAR sujet/exercice
            # mais PAS globalement → 31 questions écrasées silencieusement avant.
            # On espace la clé : sujet_id:exercice_id:question_id (134 uniques).
            sujet_id = sujet.get("sujet_id") or sujet.get("id") or "sujet"
            for _ex_idx, exercice in enumerate(sujet.get("exercices", [])):
                ex_id = exercice.get("exercice_id") or f"ex{_ex_idx}"
                for q in exercice.get("questions", []):
                    raw_qid = q["question_id"]
                    unique_qid = f"{sujet_id}:{ex_id}:{raw_qid}"
                    q["question_id"] = unique_qid      # propager l'ID globalement unique
                    q["question_id_orig"] = raw_qid    # tracer l'ID d'origine
                    # Filtrer les questions qui référencent une figure absente
                    if _text_references_figure(q.get("texte", "")):
                        _filtrees_figure += 1
                        continue
                    if unique_qid in questions_db:
                        _residuelles += 1
                    questions_db[unique_qid] = q
        if _residuelles:
            logger.warning(f"{_residuelles} collisions résiduelles (clés composées non uniques)")
        if _filtrees_figure:
            logger.info(f"📊 {_filtrees_figure} questions filtrées (figure/courbe absente)")
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
            if question_id in questions_db:
                logger.warning(f"Collision question_id détectée (taggées): {question_id} → écrasé")
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

def _is_question_usable(q: dict[str, Any]) -> bool:
    text_value = (q.get("texte_ar") or q.get("texte") or "").strip()
    if len(text_value) < 12:
        return False
    if text_value in {"-", "_", "..."}:
        return False
    # Les cartes définition sont des prompts courts par design ( "عرّف: ..." )
    # mais ont leur contenu dans reponse_attendue → pas de filtre non_ws.
    if q.get("kind") == "definition":
        return True
    # Filtrer les questions junk : contenu réel (non-whitespace) trop court
    # → OCR mal extrait, numéros de page seuls, titres sans contenu
    non_ws = len(text_value.replace("\n", "").replace("\r", "").replace(" ", "").replace("\t", ""))
    if non_ws < 30:
        return False
    # Filtrer les questions majoritairement vides (lignes vides > 70%)
    lines = [l.strip() for l in text_value.split("\n") if l.strip()]
    if not lines:
        return False
    non_empty_ratio = len("\n".join(lines)) / len(text_value) if len(text_value) > 0 else 0
    if non_empty_ratio < 0.3:
        return False
    return True


_total_before_filter = len(questions_db)
questions_db = {
    qid: q
    for qid, q in questions_db.items()
    if _is_question_usable(q)
}
_total_after_filter = len(questions_db)

logger.info(
    f"📊 Total questions en mémoire : {_total_after_filter} "
    f"(filtrées: {_total_before_filter - _total_after_filter})"
)

# --- Injection des cartes définition (46 cartes) ---
from services.definition_cards import load_definition_cards
_definition_cards = load_definition_cards()
for card in _definition_cards:
    qid = card["question_id"]
    if qid in questions_db:
        logger.warning(f"Collision question_id détectée (définition): {qid} → écrasé")
    questions_db[qid] = card

logger.info(f"📚 {len(_definition_cards)} cartes définition injectées dans questions_db")


def get_question(question_id: str) -> dict[str, Any] | None:
    q = questions_db.get(question_id)
    if q:
        if not q.get("texte_ar"):
            q["texte_ar"] = q.get("texte", "")
        if not q.get("concept_cle_ar"):
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
