"""socratic_tutor.py — Mode Socratique : indice guidant sans note.

Flux B du Blueprint : quand request_hint=True, le système ne note pas
mais génère une question guidante pour forcer l'élève à relire le doc
ou appliquer la Manhadjiya.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from config import get_settings
from services.llm import _call_with_fallback

logger = logging.getLogger("khawarizmi.socratic_tutor")

SYSTEM_PROMPT_SOCRATIC = (
    "أنت مرشد تربوي خبير في العلوم الطبيعية (الجزائر). "
    "مهمتك تقديم تلميحات وإرشادات بدون إعطاء الإجابة مباشرة.\n\n"
    "## القواعد الصارمة:\n"
    "1. لا تعطِ الإجابة النهائية أو النتيجة.\n"
    "2. وجه التلميذ نحو الخطوة التالية في المنهجية.\n"
    "3. استخدم أسئلة توجيهية مثل: 'ماذا تلاحظ في الوثيقة؟' 'ما العلاقة بين...؟'\n"
    "4. أشر إلى الخطوة المنهجية المطلوبة دون شرحها كاملاً.\n"
    "5. أجب بصيغة JSON فقط:\n"
    "```json\n"
    '{"hint_ar": "<تلميح قصير 1-2 جمل>", '
    '"focus_area": "<Document|Methodology|Conclusion>", '
    '"methodology_step": "<اسم الخطوة>"}\n'
    "```\n"
    "6. التلميح بالعربية فقط."
)

DEFAULT_HINT = {
    "hint_ar": "حاول مرة أخرى بالتركيز على الوثائق المعطاة.",
    "focus_area": "Documents",
    "methodology_step": "Analyse",
}


async def get_socratic_hint(
    scenario_context: str,
    documents: list[dict[str, Any]] | None,
    question_prompt: str,
    question_skill: str,
    verb_slug: str,
    model_answer: str,
    learning_focus: str | None,
    student_answer: str,
) -> dict[str, Any]:
    """Génère un indice guidant (hint) sans note.

    Args:
        Mêmes paramètres que evaluate_answer_v2 (sauf score_max).

    Returns:
        dict avec hint_ar, focus_area, methodology_step.
    """
    doc_block = ""
    if documents:
        for i, doc in enumerate(documents[:3]):
            title = doc.get("title", "")
            caption = doc.get("caption", "")
            doc_block += f"\n--- وثيقة {i+1}: {title}\n{caption}\n"

    user_prompt = (
        f"السياق: {scenario_context}\n"
        f"{doc_block}"
        f"السؤال: {question_prompt}\n"
        f"المهارة: {question_skill}\n"
        f"الفعل: {verb_slug}\n"
        f"إجابة التلميذ: {student_answer}\n"
        f"الإجابة النموذجية: {model_answer}\n"
    )
    if learning_focus:
        user_prompt += f"محور التعلم: {learning_focus}\n"

    cfg = get_settings()
    client = AsyncOpenAI(
        api_key=cfg.OPENAI_API_KEY,
        base_url=cfg.openai_base_url,
    )

    try:
        response = await _call_with_fallback(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_SOCRATIC},
                {"role": "user", "content": user_prompt},
            ],
            primary_client=client,
            primary_model=cfg.openai_model,
            temperature=0.7,
            max_tokens=512,
        )
        content = response.choices[0].message.content or ""
        # Nettoyer les fences markdown avant parse
        cleaned = content.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned)
        return {
            "hint_ar": result.get("hint_ar", DEFAULT_HINT["hint_ar"]),
            "focus_area": result.get("focus_area", DEFAULT_HINT["focus_area"]),
            "methodology_step": result.get(
                "methodology_step", DEFAULT_HINT["methodology_step"]
            ),
        }
    except Exception as e:
        logger.warning(f"socratic_hint_fallback | error={e}")
        return dict(DEFAULT_HINT)
