import logging

from methodology.feedback_generator import generate_feedback
from methodology.task_classifier import classify_task
from methodology.text_structure_validator import validate_structure
from methodology.verb_database import identify_verb

logger = logging.getLogger("khawarizmi.methodology")


async def evaluate_methodology(
    instruction: str,
    student_answer: str,
) -> dict:
    classification = classify_task(instruction)
    verb = identify_verb(instruction) if classification["verb"] else None

    weaknesses = []
    structure_result = None

    if verb and verb.get("required_structure"):
        structure_result = validate_structure(student_answer, verb["required_structure"])
        if structure_result["score"] < 1.0:
            for part, found in structure_result["parts"].items():
                if not found:
                    weaknesses.append(f"missing_{part}")

    if verb and verb["type"] == "complex":
        word_count = len(student_answer.split())
        if word_count < 20:
            weaknesses.append("too_short")
        if verb["type"] == "complex" and not structure_result:
            weaknesses.append("missing_structure")

    feedback = generate_feedback(verb, classification, structure_result, weaknesses)

    methodology_score = _compute_methodology_score(
        verb=verb,
        structure_result=structure_result,
        weaknesses=weaknesses,
        classification=classification,
    )

    result = {
        "verb_identifie": classification["verb"],
        "type_tache": classification["task_type"],
        "note_methodologie": methodology_score,
        "note_max": verb["max_score"] if verb else 10,
        "points_forts": feedback["points_forts"],
        "points_faibles": feedback["points_faibles"],
        "feedback_principal": feedback["feedback_principal"],
        "recommandation": feedback["recommandation"],
        "structure": structure_result,
    }

    logger.info(
        f"MethodologyEval | verb={classification['verb']} | "
        f"type={classification['task_type']} | score={methodology_score}"
    )

    return result


def _compute_methodology_score(
    verb: dict | None,
    structure_result: dict | None,
    weaknesses: list[str],
    classification: dict,
) -> int:
    if classification["task_type"] == "unknown" or classification["task_type"] == "simple":
        base = 8
        penalty = len(weaknesses) * 2
        return max(0, base - penalty)

    if not verb:
        return 5

    max_score = verb.get("max_score", 10)
    score = max_score

    if structure_result:
        structure_ratio = structure_result["score"]
        score = int(max_score * structure_ratio)

    for w in weaknesses:
        if w in ("missing_conclusion", "missing_introduction", "missing_structure"):
            score -= 3
        elif w in ("weak_argumentation", "weak_analysis"):
            score -= 2
        else:
            score -= 1

    return max(0, min(score, max_score))
