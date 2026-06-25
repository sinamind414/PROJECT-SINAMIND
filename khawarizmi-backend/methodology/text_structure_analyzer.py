"""
Analyseur de structure du texte scientifique — Couche 3
Vérifie si la réponse contient Introduction / Développement / Conclusion
"""

def analyze_text_structure(answer: str) -> dict:
    has_intro = any(word in answer for word in [
        "مقدمة", "المشكل", "يهدف", "يتمثل", "الهدف من"
    ])

    has_development = any(word in answer for word in [
        "عرض", "تطوير", "من خلال", "لأن", "بسبب", "حسب الوثيقة"
    ])

    has_conclusion = any(word in answer for word in [
        "خاتمة", "إذن", "نستنتج", "لذلك", "يتبين", "مما سبق"
    ])

    structure_score = sum([
        has_intro * 5,
        has_development * 7,
        has_conclusion * 4,
    ])

    return {
        "has_intro": has_intro,
        "has_development": has_development,
        "has_conclusion": has_conclusion,
        "structure_score": structure_score,
        "max_structure_score": 16,
    }
