import json
from typing import Dict, Any
from openai import AsyncOpenAI
from config import get_settings

CORRECTION_PROMPT = """
Tu es un correcteur expert du Bac Algérien (SVT).

Corrige la réponse de l'élève de manière pédagogique et bienveillante.

Question : {question}
Réponse de l'élève : {student_answer}
Barème : {points} points

Retourne UNIQUEMENT ce JSON valide :
{{
  "score": nombre,
  "max_score": {points},
  "points_forts": ["..."],
  "erreurs": ["..."],
  "reponse_correcte": "Réponse académique complète en arabe",
  "explication": "Explication claire",
  "conseils": "Conseils d'amélioration"
}}
"""

async def correct_student_answer(question: str, student_answer: str, points: int = 4, language: str = "ar") -> Dict[str, Any]:
    try:
        prompt = CORRECTION_PROMPT.format(
            question=question,
            student_answer=student_answer,
            points=points
        )

        client = AsyncOpenAI(api_key=get_settings().OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Correcteur Bac Algérie rigoureux."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        return {
            "score": 0,
            "max_score": points,
            "points_forts": [],
            "erreurs": [str(e)],
            "reponse_correcte": "Erreur technique",
            "explication": "",
            "conseils": "Réessaie plus tard"
        }
