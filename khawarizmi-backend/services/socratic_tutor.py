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
from prompts.correction_prompt import MANHADJIYA_RUBRICS
from services.llm import _call_with_fallback
from services.llm_guard import is_llm_enabled

logger = logging.getLogger("khawarizmi.socratic_tutor")

SYSTEM_PROMPT_SOCRATIC = (
    "أنت مرشد تربوي خبير في العلوم الطبيعية (الجزائر) وفق منهجية المنهجية (Manhadjiya). "
    "مهمتك تقديم تلميحات وإرشادات بدون إعطاء الإجابة مباشرة.\n\n"
    "## القواعد الصارمة:\n"
    "1. لا تعطِ الإجابة النهائية أو النتيجة.\n"
    "2. لا تعطِ الدرجة أو التصحيح.\n"
    "3. وجه التلميذ نحو الخطوة التالية في المنهجية المطلوبة.\n"
    "4. استخدم أسئلة توجيهية مثل: 'ماذا تلاحظ في الوثيقة؟' 'ما العلاقة بين...؟'\n"
    "5. ركز على الخطوة التي فاته التلميذ: تعريف الوثيقة؟ استخراج المعطيات؟ الربط السببي؟\n"
    "6. أشر إلى الخطوة المنهجية المطلوبة دون شرحها كاملاً.\n"
    "7. أجب بصيغة JSON فقط:\n"
    "```json\n"
    '{"hint_ar": "<تلميح قصير 1-2 جمل بالعربية فقط>", '
    '"focus_area": "<Document|Methodology|Conclusion|Revision>", '
    '"methodology_step": "<اسم الخطوة من المنهجية المقدمة>"}\n'
    "```\n"
    "8. التلميح بالعربية فقط.\n\n"
    "## إرشادات تربوية إضافية (من كتاب المنهجية):\n"
    "- إذا تكرر نفس الخطأ في عدة أسئلة ← شجّع التلميذ على تنويع التمارين وعدم الاكتفاء بنمط واحد.\n"
    "- ذكّر بأهمية المعلومات الثانوية في الوثائق — ليست كل نقطة في الأفكار الرئيسية فقط.\n"
    "- التمييز بين التعليمات البسيطة (تعرّف، عرّف، صف، اذكر) والتعليمات المركبة (حلّل، فسّر، استنتج، ناقش).\n"
    "- تذكير: 'في التحليل لا تفسير' — العلاقة بين المعطيات ليست تفسيراً بل وصف.\n"
    "- إذا كان التلميذ مشتتاً بين عدة أفكار ⇒ أرشده إلى فكرة واحدة في كل تلميح.\n"
    "- استعمل أسلوب 'ماذا لو؟' لدفع التلميذ إلى التفكير النقدي.\n\n"
    "## أنماط الأخطاء الشائعة والتوجيه المناسب (10 أنماط):\n"
    "1. **خلط التحليل بالتفسير**: 'لاحظت أنك تستعمل روابط سببية (لأن، بسبب) في التحليل — "
    "التحليل يصف فقط، التفسير يأتي لاحقاً. حاول إعادة الصياغة بدون أسباب.'\n"
    "2. **الاستنتاج بدل الاستخلاص**: 'الاستخلاص يعني استخراج المعلومة من النص مباشرة — "
    "ليس استنتاجاً. اقرأ النص مرة أخرى واكتب الفكرة الرئيسية كما هي.'\n"
    "3. **الخلط بين الخاص والعام**: 'الاستنتاج الخاص من معطيات التمرين فقط. "
    "الاستنتاج العام يتجاوز هذا الإطار. أي نوع مطلوب هنا؟'\n"
    "4. **الإغراق في العموميات**: 'إجابتك عامة جداً. اربطها بالوثائق المعطاة — "
    "ماذا ترى بالضبط في المنحنى/الجدول؟'\n"
    "5. **نسيان الإطار الثلاثي للتحليل**: 'التحليل الجيد يحتاج: تحديد العناصر ← "
    "العلاقة بينها ← توضيح النتائج. أي خطوة فاتتك؟'\n"
    "6. **غياب الأسلوب السببي**: 'السؤال يطلب تفسيراً أو تعليلاً. "
    "استعمل روابط السببية: لأن، بسبب، يعود ذلك إلى.'\n"
    "7. **إجابة ناقصة (توقف بعد أول فكرة)**: 'لديك فكرة صحيحة لكن الإجابة غير مكتملة. "
    "ماذا بعد؟ تابع التسلسل المنطقي.'\n"
    "8. **تجاهل صيغة السؤال**: 'أنت تجيب على سؤال مختلف. "
    "أعد قراءة التعليمة: ما هو فعل الأمر بالضبط (حلّل؟ فسّر؟ استنتج؟)'\n"
    "9. **عدم التمييز بين المقدمة والعرض والخاتمة**: 'النص العلمي له بنية: "
    "مقدمة (مشكل) ← عرض (معلومة) ← خاتمة (خلاصة). رتب أفكارك حسب هذه البنية.'\n"
    "10. **الاكتفاء بالوصف المنفصل في المقارنة**: 'المقارنة تحتاج معياراً مشتركاً. "
    "قارن elemento بآخر: في ماذا يتشابهان؟ في ماذا يختلفان؟'"
)

DEFAULT_HINT = {
    "hint_ar": "حاول مرة أخرى بالتركيز على الوثائق المعطاة.",
    "focus_area": "Documents",
    "methodology_step": "Analyse",
}


def build_local_socratic_hint(
    *,
    verb_slug: str,
    student_answer: str,
    question_prompt: str,
    documents: list[dict[str, Any]] | None,
) -> dict[str, str]:
    """Indice déterministe spécifique au verbe, sans révéler la réponse."""
    answer = (student_answer or "").strip()
    has_document = any(marker in answer for marker in ("الوثيقة", "الشكل", "الجدول", "المنحنى", "نلاحظ"))
    has_cause = any(marker in answer for marker in ("لأن", "بسبب", "يعود", "يفسر"))
    has_deduction = any(marker in answer for marker in ("نستنتج", "ومنه", "يدل", "نستخلص"))
    has_comparison = any(marker in answer for marker in ("بينما", "يتشابه", "يختلف", "مقارنة"))

    if verb_slug == "analyse":
        if has_cause:
            return {"hint_ar": "أنت تفسّر باستعمال سبب. أعد الجملة بوصف ما يتغير في الوثيقة فقط، مع قيمة أو اتجاه إن وُجد.", "focus_area": "Methodology", "methodology_step": "وصف المعطيات دون تفسير"}
        if not has_document:
            return {"hint_ar": "ابدأ بتحديد الوثيقة والعناصر المقاسة، ثم اذكر اتجاه التغير أو القيم البارزة.", "focus_area": "Document", "methodology_step": "تعريف الوثيقة واستخراج المعطيات"}
        return {"hint_ar": "ما العلاقة الوصفية بين العنصرين؟ عبّر عنها دون استعمال «لأن» أو «بسبب».", "focus_area": "Document", "methodology_step": "ربط الملاحظات"}
    if verb_slug in {"interpret", "justify", "explain"}:
        if not has_cause:
            return {"hint_ar": "ما المعرفة العلمية التي تفسر الملاحظة؟ اربط النتيجة بسبب باستعمال «لأن» أو «يعود ذلك إلى».", "focus_area": "Methodology", "methodology_step": "الربط السببي"}
        return {"hint_ar": "تحقق الآن: هل السبب الذي كتبته يفسر المعطى المحدد في الوثيقة، أم هو معلومة عامة؟", "focus_area": "Conclusion", "methodology_step": "التحقق من السببية"}
    if verb_slug in {"deduce", "extract"}:
        if not has_deduction:
            return {"hint_ar": "حوّل الملاحظات إلى نتيجة واحدة قصيرة تبدأ بـ «نستنتج أن…» دون إضافة معلومات غير موجودة.", "focus_area": "Conclusion", "methodology_step": "صياغة الاستنتاج"}
        return {"hint_ar": "هل استنتاجك يجيب مباشرة عن المطلوب ويمكن إثباته بالوثيقة؟ احذف كل تفصيل لا يخدم النتيجة.", "focus_area": "Conclusion", "methodology_step": "التحقق من الاستنتاج"}
    if verb_slug == "compare":
        if not has_comparison:
            return {"hint_ar": "اختر معيارا مشتركا واحدا، ثم اكتب حالة العنصر الأول وحالة العنصر الثاني في الجملة نفسها.", "focus_area": "Methodology", "methodology_step": "تحديد معيار المقارنة"}
        return {"hint_ar": "بعد أوجه الاختلاف، هل ذكرت وجها للتشابه إن كان موجودا في الوثيقة؟", "focus_area": "Document", "methodology_step": "التشابه والاختلاف"}
    if verb_slug in {"hypothesis", "validate-hypothesis"}:
        return {"hint_ar": "صغ فرضية قابلة للاختبار، ثم حدّد النتيجة التي تتوقع ملاحظتها إذا كانت صحيحة.", "focus_area": "Methodology", "methodology_step": "فرضية ثم توقع"}
    if verb_slug == "scientific-text":
        return {"hint_ar": "رتّب جوابك: طرح المشكل، عرض مترابط للمعلومات، ثم خلاصة تجيب عن المشكل.", "focus_area": "Methodology", "methodology_step": "مقدمة، عرض، خاتمة"}

    methodology = MANHADJIYA_RUBRICS.get(verb_slug) or MANHADJIYA_RUBRICS["analyse"]
    first_step = (methodology.get("steps") or ["قراءة التعليمة"])[0]
    doc_note = " اعتمادا على الوثيقة." if documents else ""
    return {
        "hint_ar": f"ابدأ بالخطوة التالية: {first_step}.{doc_note}",
        "focus_area": "Methodology",
        "methodology_step": str(first_step),
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
    local_hint = build_local_socratic_hint(
        verb_slug=verb_slug,
        student_answer=student_answer,
        question_prompt=question_prompt,
        documents=documents,
    )
    if not is_llm_enabled():
        return local_hint

    doc_block = ""
    if documents:
        for i, doc in enumerate(documents[:3]):
            title = doc.get("title", "")
            caption = doc.get("caption", "")
            doc_block += f"\n--- وثيقة {i + 1}: {title}\n{caption}\n"

    methodology = MANHADJIYA_RUBRICS.get(verb_slug) or MANHADJIYA_RUBRICS["analyse"]
    user_prompt = (
        f"السياق: {scenario_context}\n"
        f"{doc_block}"
        f"السؤال: {question_prompt}\n"
        f"المهارة: {question_skill}\n"
        f"الفعل: {verb_slug}\n"
        f"المنهجية:\n"
        f"  - الخطوات: {' ← '.join(methodology['steps'])}\n"
        f"  - الأخطاء الشائعة: {methodology['common_errors']}\n"
        f"  - الكلمات المفتاحية: {'، '.join(methodology['keywords'])}\n"
        f"إجابة التلميذ: {student_answer}\n"
        f"الإجابة النموذجية: {model_answer}\n"
    )
    if learning_focus:
        user_prompt += f"محور التعلم: {learning_focus}\n"

    try:
        cfg = get_settings()
        client = AsyncOpenAI(
            api_key=cfg.OPENAI_API_KEY or "sk-placeholder",
            base_url=cfg.openai_base_url,
        )
    except Exception as e:
        logger.warning(f"socratic_hint_fallback | client_init_error={e}")
        return local_hint

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
            feature="tutor",
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
        return local_hint
