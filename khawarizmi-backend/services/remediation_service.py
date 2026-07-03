"""remediation_service.py — Correction intelligente : page du livre MANHADJIYA.

Mapper l'erreur dominante (dominant_error_code) vers une page précise
du livre pour la remédiation automatique de l'élève.

Couvre les 21 verbes du LIVRE MANHADJIYA (édition Okacha):
- 9 تعليمات بسيطة (simples/fermées): nommer, définir, décrire, citer,
  énumérer, classer, distinguer, schématiser, écrire texte scientifique
- 12 تعليمات مركبة (composées/ouvertes): analyser, comparer, interpréter,
  déduire, justifier, discuter, expliquer, critiquer, hypothèse,
  valider, déterminer, relation
"""

from __future__ import annotations

from typing import Any

REMEDIATION_MATRIX: dict[str, dict[str, dict[str, Any]]] = {
    # ═══ تعليمات مركبة (مفتوحة) ═══════════════════════════════
    "analyse": {
        "methodology_error": {
            "page": 41,
            "lesson_title": "منهجية التحليل",
            "advice_ar": "لقد نسيت بعض خطوات التحليل. راجع الصفحة 41 لتعلم كيفية تعريف الوثيقة ثم تفكيك المعطيات.",
        },
        "scientific_error": {
            "page": 42,
            "lesson_title": "تحليل النتائج التجريبية",
            "advice_ar": "هناك خطأ في فهم المعطيات العلمية. راجع الأمثلة في الصفحة 42 لتدريب نفسك.",
        },
        "off_topic": {
            "page": 40,
            "lesson_title": "الهدف من التمرين",
            "advice_ar": "إجابتك بعيدة عن المطلوب. راجع الصفحة 40 لتعلم كيف تستخرج الهدف من سياق التمرين.",
        },
    },
    "interpret": {
        "methodology_error": {
            "page": 49,
            "lesson_title": "منهجية التفسير",
            "advice_ar": "تفسيرك يفتقر إلى الروابط السببية. راجع الصفحة 49 لتعلم استعمال 'بسبب' و 'راجع إلى'.",
        },
        "scientific_error": {
            "page": 55,
            "lesson_title": "أمثلة تطبيقية على التفسير",
            "advice_ar": "التعليل العلمي غير دقيق. راجع الصفحة 55 لترى كيف يتم ربط المعطيات بالمكتسبات.",
        },
    },
    "deduce": {
        "methodology_error": {
            "page": 40,
            "lesson_title": "كيفية الاستنتاج",
            "advice_ar": "الاستنتاج يجب أن يكون مباشراً وموجزاً. راجع الصفحة 40 لتجنب الإطالة غير الضرورية.",
        },
        "scientific_error": {
            "page": 40,
            "lesson_title": "الاستنتاج العلمي",
            "advice_ar": "الاستنتاج لا يتوافق مع نتيجة التحليل. راجع الصفحة 40.",
        },
    },
    "hypothesis": {
        "methodology_error": {
            "page": 22,
            "lesson_title": "صياغة الفرضيات",
            "advice_ar": "الفرضية يجب أن تصاغ بصيغة 'نفترض أن...'. راجع الصفحة 22 لتصحيح صياغتك.",
        },
        "scientific_error": {
            "page": 22,
            "lesson_title": "المنطق العلمي للفرضية",
            "advice_ar": "الفرضية غير منطقية علمياً. راجع الصفحة 22 لفهم كيف تقترح فرضية قابلة للتحقق.",
        },
    },
    "scientific-text": {
        "methodology_error": {
            "page": 21,
            "lesson_title": "بنية النص العلمي",
            "advice_ar": "نصك يفتقر إلى الهيكلة (مقدمة، عرض، خاتمة). راجع الصفحة 21 لتعلم التنظيم.",
        },
        "scientific_error": {
            "page": 22,
            "lesson_title": "أمثلة النصوص العلمية",
            "advice_ar": "المعلومات العلمية في نصك غير دقيقة. راجع الأمثلة في الصفحة 22.",
        },
    },
    "compare": {
        "methodology_error": {
            "page": 43,
            "lesson_title": "منهجية المقارنة",
            "advice_ar": "المقارنة تتطلب معايير واضحة وأوجه تشابه واختلاف. راجع الصفحة 43 لتعلم منهجية المقارنة الصحيحة.",
        },
        "scientific_error": {
            "page": 44,
            "lesson_title": "أمثلة تطبيقية على المقارنة",
            "advice_ar": "المعلومات العلمية في المقارنة غير دقيقة. راجع الصفحة 44 لتدريب نفسك.",
        },
    },
    "justify": {
        "methodology_error": {
            "page": 45,
            "lesson_title": "منهجية التعليل",
            "advice_ar": "التعليل يختلف عن التفسير — يجب تقديم حجة علمية تدعم النتيجة. راجع الصفحة 45.",
        },
        "scientific_error": {
            "page": 46,
            "lesson_title": "أمثلة تطبيقية على التعليل",
            "advice_ar": "الحجة العلمية غير دقيقة أو غير كافية. راجع الصفحة 46 لترى أمثلة صحيحة.",
        },
    },
    "validate-hypothesis": {
        "methodology_error": {
            "page": 22,
            "lesson_title": "التحقق من صحة الفرضية",
            "advice_ar": "يجب مقارنة الفرضية بالنتائج ثم الحكم بدليل. راجع الصفحة 22 لفهم الخطوات.",
        },
        "scientific_error": {
            "page": 22,
            "lesson_title": "الحكم على الفرضية",
            "advice_ar": "الحكم على الفرضية يجب أن يكون مبنياً على النتائج لا على الرأي. راجع الصفحة 22.",
        },
    },
    "discuss": {
        "methodology_error": {
            "page": 50,
            "lesson_title": "منهجية المناقشة",
            "advice_ar": "المناقشة تتطلب عرض موقفين ثم التركيب. راجع الصفحة 50 لتعلم منهجية المناقشة.",
        },
        "scientific_error": {
            "page": 51,
            "lesson_title": "أمثلة تطبيقية على المناقشة",
            "advice_ar": "الحجج العلمية في مناقشتك غير كافية. راجع الصفحة 51 لترى أمثلة.",
        },
    },
    "relationship": {
        "methodology_error": {
            "page": 41,
            "lesson_title": "استخراج العلاقة",
            "advice_ar": "العلاقة تُستخرج من التحليل وليست تفسيراً. راجع الصفحة 41 لفهم الفرق بين العلاقة والتفسير.",
        },
        "scientific_error": {
            "page": 42,
            "lesson_title": "أنواع العلاقات العلمية",
            "advice_ar": "نوع العلاقة غير محدد بدقة (طردية/عكسية/سببية). راجع الصفحة 42.",
        },
    },
    "expliquer": {
        "methodology_error": {
            "page": 47,
            "lesson_title": "منهجية الشرح",
            "advice_ar": "الشرح يتوقف على السياق — حدد نوع الشرح المطلوب أولاً. راجع الصفحة 47-48.",
        },
        "scientific_error": {
            "page": 48,
            "lesson_title": "أمثلة تطبيقية على الشرح",
            "advice_ar": "الشرح العلمي غير دقيق أو ناقص الخطوات. راجع الصفحة 48 لترى أمثلة صحيحة.",
        },
    },
    "critiquer": {
        "methodology_error": {
            "page": 52,
            "lesson_title": "منهجية النقد",
            "advice_ar": "النقد يتطلب تقييماً موضوعياً بإيجابيات وسلبيات. راجع الصفحة 52.",
        },
        "scientific_error": {
            "page": 52,
            "lesson_title": "النقد العلمي",
            "advice_ar": "النقد يجب أن يكون مبنياً على حجج علمية لا على رأي شخصي. راجع الصفحة 52.",
        },
    },
    "determiner": {
        "methodology_error": {
            "page": 14,
            "lesson_title": "فعل حدّد — تعددية السياق",
            "advice_ar": "فعل 'حدّد' يتوقف على السياق — قد يعني اذكر أو علّل أو اشرح. راجع الصفحة 14 لفهم الفرق.",
        },
        "scientific_error": {
            "page": 14,
            "lesson_title": "الدقة في التحديد",
            "advice_ar": "التحديد غير دقيق علمياً. راجع السياق بعناية وحدد نوع الإجابة المطلوبة — صفحة 14.",
        },
    },
    # ═══ تعليمات بسيطة (مغلقة) ═══════════════════════════════
    "nommer": {
        "methodology_error": {
            "page": 15,
            "lesson_title": "كيفية التسمية",
            "advice_ar": "التسمية تتطلب ذكر الاسم الدقيق فقط — لا شرح ولا تفسير. راجع الصفحة 15.",
        },
        "scientific_error": {
            "page": 15,
            "lesson_title": "الدقة في التسمية",
            "advice_ar": "الاسم غير صحيح علمياً. راجع الوثيقة بدقة واستخرج التسمية الصحيحة — صفحة 15.",
        },
    },
    "definir": {
        "methodology_error": {
            "page": 16,
            "lesson_title": "كيفية التعريف",
            "advice_ar": "التعريف يجب أن يكون شاملاً ومحدداً (جنس + فصل نوعي). راجع الصفحة 16.",
        },
        "scientific_error": {
            "page": 16,
            "lesson_title": "الدقة في التعريف",
            "advice_ar": "التعريف غير دقيق — لا تعطِ مثالاً بدل التعريف. راجع الصفحة 16.",
        },
    },
    "decrire": {
        "methodology_error": {
            "page": 17,
            "lesson_title": "كيفية الوصف",
            "advice_ar": "الوصف يجب أن يكون موضوعياً — لا تضف تفسيراً. راجع الصفحة 17.",
        },
        "scientific_error": {
            "page": 17,
            "lesson_title": "الدقة في الوصف",
            "advice_ar": "المعلومات في الوصف غير دقيقة. راجع الوثيقة وصفّط المعطيات — صفحة 17.",
        },
    },
    "citer": {
        "methodology_error": {
            "page": 15,
            "lesson_title": "كيفية الذكر",
            "advice_ar": "الذكر يتطلب إجابة مباشرة — لا شرح ولا إطالة. راجع الصفحة 15.",
        },
        "scientific_error": {
            "page": 15,
            "lesson_title": "الدقة في الذكر",
            "advice_ar": "العنصر المذكور غير صحيح. راجع الوثيقة واذكر ما هو مطلوب بدقة — صفحة 15.",
        },
    },
    "enumerer": {
        "methodology_error": {
            "page": 15,
            "lesson_title": "كيفية العدّ",
            "advice_ar": "العدّ يتطلب ذكر جميع العناصر بشكل منظم. راجع الصفحة 15.",
        },
        "scientific_error": {
            "page": 15,
            "lesson_title": "اكتمال العدّ",
            "advice_ar": "نسيت بعض العناصر في العدّ. راجع الوثيقة بعناية — صفحة 15.",
        },
    },
    "classer": {
        "methodology_error": {
            "page": 18,
            "lesson_title": "كيفية التصنيف",
            "advice_ar": "التصنيف يتطلب معياراً واضحاً وتوزيعاً صحيحاً. راجع الصفحة 18.",
        },
        "scientific_error": {
            "page": 18,
            "lesson_title": "الدقة في التصنيف",
            "advice_ar": "بعض العناصر في فئة خاطئة. راجع المعيار وأعد التوزيع — صفحة 18.",
        },
    },
    "distinguer": {
        "methodology_error": {
            "page": 19,
            "lesson_title": "كيفية التمييز",
            "advice_ar": "التمييز يتطلب ذكر الفرق الجوهري فقط. راجع الصفحة 19.",
        },
        "scientific_error": {
            "page": 19,
            "lesson_title": "الدقة في التمييز",
            "advice_ar": "الفرق المذكور غير صحيح علمياً. راجع الصفحة 19.",
        },
    },
    "schematiser": {
        "methodology_error": {
            "page": 20,
            "lesson_title": "كيفية إنجاز الرسم التخطيطي",
            "advice_ar": "الرسم التخطيطي يتطلب: عناوين، تسميات، نسب، أسهم. راجع الصفحة 20.",
        },
        "scientific_error": {
            "page": 20,
            "lesson_title": "الدقة في الرسم التخطيطي",
            "advice_ar": "الرسم التخطيطي غير دقيق علمياً أو ناقص. راجع الصفحة 20.",
        },
    },
    # ═══ تعليمات مركبة إضافية ═══════════════════════════════
    "exploit-document": {
        "methodology_error": {
            "page": 36,
            "lesson_title": "منهجية استغلال وثيقة",
            "advice_ar": "استغلال الوثيقة يتطلب: تعريف → تحليل → تفسير → ربط بالهدف. راجع الصفحة 36.",
        },
        "scientific_error": {
            "page": 37,
            "lesson_title": "الربط المنطقي بين الوثائق",
            "advice_ar": "المعلومات المستخرجة غير مربوطة بالهدف من السؤال. راجع الصفحة 37.",
        },
    },
    "formulate-problem": {
        "methodology_error": {
            "page": 36,
            "lesson_title": "كيفية طرح مشكل علمي",
            "advice_ar": "المشكل العلمي يجب أن يكون دقيقاً ومحدد النطاق — ليس سؤالاً عادياً. راجع الصفحة 36.",
        },
        "scientific_error": {
            "page": 36,
            "lesson_title": "تحديد نطاق المشكل",
            "advice_ar": "نطاق المشكل غير محدد بدقة. راجع الصفحة 36.",
        },
    },
    "prove": {
        "methodology_error": {
            "page": 37,
            "lesson_title": "منهجية الإثبات",
            "advice_ar": "الإثبات يتطلب جمع أدلة من الوثائق والمكتسبات لإبراز صحة المعلومة. راجع الصفحة 37.",
        },
        "scientific_error": {
            "page": 37,
            "lesson_title": "الدقة في الإثبات",
            "advice_ar": "الأدلة المقدمة غير كافية أو غير مربوطة بالمعلومة. راجع الصفحة 37.",
        },
    },
    "comment": {
        "methodology_error": {
            "page": 37,
            "lesson_title": "منهجية التعليق",
            "advice_ar": "التعليق يتطلب موقفاً علمياً واضحاً مدعماً بالحجج — ليس مجرد وصف. راجع الصفحة 37.",
        },
        "scientific_error": {
            "page": 37,
            "lesson_title": "الدقة في التعليق",
            "advice_ar": "التعليق يفتقر إلى الحجج العلمية أو الموقف الواضح. راجع الصفحة 37.",
        },
    },
    # ── LOT 7 — فعلان جديدان ──────────────────────────
    "extract": {
        "methodology_error": {
            "page": 40,
            "lesson_title": "منهجية الاستخلاص",
            "advice_ar": "الاستخلاص يعني استخراج المعلومة الأساسية من النص مباشرة — ليس استنتاجاً. راجع الصفحة 40.",
        },
        "scientific_error": {
            "page": 40,
            "lesson_title": "الاستخلاص الدقيق",
            "advice_ar": "تأكد من أن المستخلص يعكس جوهر النص وليس تفصيلاً جانبياً. راجع الصفحة 40.",
        },
    },
    "prove-experimentally": {
        "methodology_error": {
            "page": 42,
            "lesson_title": "منهجية الإثبات التجريبي",
            "advice_ar": "الإثبات التجريبي يتطلب ترتيباً إجبارياً: تجربة ← ملاحظة ← نتيجة. راجع الصفحة 42.",
        },
        "scientific_error": {
            "page": 42,
            "lesson_title": "الإثبات التجريبي الدقيق",
            "advice_ar": "تأكد من التمييز بين الشاهد والاختبار، وأن النتيجة مستخلصة من الملاحظة وليست مفروضة. راجع الصفحة 42.",
        },
    },
}

GENERIC_REMEDIATION: dict[str, dict[str, Any]] = {
    "methodology_error": {
        "page": 14,
        "lesson_title": "التعليمات والمهمات",
        "advice_ar": "راجع الصفحة 14 لفهم الفرق بين المهمات البسيطة والمركبة.",
    },
    "scientific_error": {
        "page": 8,
        "lesson_title": "أسرار العلامة الكاملة",
        "advice_ar": "راجع الصفحة 8 لتعلم كيف تتجنب الأخطاء الشائعة في SVT.",
    },
    "off_topic": {
        "page": 17,
        "lesson_title": "فائدة سياق التمرين",
        "advice_ar": "راجع الصفحة 17 لتعلم كيف تستخرج المشكل العلمي من السياق.",
    },
}


def get_remediation(
    verb_slug: str,
    error_code: str,
) -> dict[str, Any] | None:
    """Retourne la remédiation spécifique au verbe et à l'erreur.

    Args:
        verb_slug: slug du verbe d'action (analyse, interpret, deduce…)
        error_code: code d'erreur dominant (methodology_error, scientific_error…)

    Returns:
        dict avec page, lesson_title, advice_ar ou None si pas de match.
    """
    verb_data = REMEDIATION_MATRIX.get(verb_slug)
    if verb_data is None:
        return None
    return verb_data.get(error_code)


def get_generic_remediation(error_code: str) -> dict[str, Any] | None:
    """Fallback générique si aucun verbe spécifique n'est trouvé."""
    return GENERIC_REMEDIATION.get(error_code)
