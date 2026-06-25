from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from models.exercise import Exercise

PROMPT_ARABE = """
Tu es un expert en traduction éducative pour le Baccalauréat Algérien SVT.

Traduis cette question en **arabe classique académique** (style Bac Algérie).

Règles :
- Arabe clair et scolaire
- Conserve les termes scientifiques (ADN, transcription, eucaryote...)
- Retourne UNIQUEMENT la traduction arabe

Question : {question}
"""


async def generate_arabic_version(question: str) -> str | None:
    try:
        client = AsyncOpenAI(api_key=get_settings().OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Expert éducation algérienne."},
                {"role": "user", "content": PROMPT_ARABE.format(question=question)},
            ],
            temperature=0.3,
            max_tokens=800,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erreur génération arabe: {e}")
        return None


async def ensure_arabic_version(exercise: Exercise, db: AsyncSession):
    if exercise.language == "ar" and not exercise.question_ar:
        arabic = await generate_arabic_version(exercise.question)
        if arabic:
            exercise.question_ar = arabic
            await db.commit()
            return True
    return False
