"""remediation_service.py — Correction intelligente : page du livre MANHADJIYA.

Mapper l'erreur dominante (dominant_error_code) vers une page precise
du livre pour la remediation automatique de l'eleve.

Couvre les 21 verbes du LIVRE MANHADJIYA (edition Okacha):
- 9 تعليمات بسيطة (simples/fermees): nommer, definir, decrire, citer,
  enumerer, classer, distinguer, schematiser, ecrire texte scientifique
- 12 تعليمات مركبة (composees/ouvertes): analyser, comparer, interpreter,
  deduire, justifier, discuter, expliquer, critiquer, hypothèse,
  valider, determiner, relation
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
        "confusion_analyse_interpret": {
            "page": 39,
            "lesson_title": "الفرق بين التحليل والتفسير",
            "advice_ar": "يبدو أنك خلطت بين التحليل والتفسير. راجع الصفحة 39 للتفرقة بينهما. تذكر: التحليل = وصف الملاحظات فقط، التفسير = ربطها بالمعرفة العلمية.",
        },
    },
    "compare": {
        "methodology_error": {
            "page": 44,
            "lesson_title": "منهجية المقارنة",
            "advice_ar": "لقد نسيت بعض جوانب المقارنة. راجع الصفحة 44 لتعلم كيفية بناء جدول ونقاط التشابه والاختلاف.",
        },
        "scientific_error": {
            "page": 45,
            "lesson_title": "مقارنة دقيقة",
            "advice_ar": "هناك خطأ في المعطيات التي تقارنها. راجع الصفحة 45 لتعرف كيف تميز بين العناصر الصحيحة والخاطئة في المقارنة.",
        },
        "confusion_analyse_interpret": {
            "page": 44,
            "lesson_title": "منهجية المقارنة",
            "advice_ar": "تأكد من استخدام جدول مقارنة: عنصر المقارنة في الوسط، ثم الفرق بين العنصرين. راجع الصفحة 44.",
        },
    },
    "interpret": {
        "methodology_error": {
            "page": 39,
            "lesson_title": "منهجية التفسير",
            "advice_ar": "لقد نسيت ربط الملاحظات بالمعرفة العلمية. راجع الصفحة 39 لتعلم كيفية بناء تفسير علمي صحيح.",
        },
        "scientific_error": {
            "page": 40,
            "lesson_title": "التفسير العلمي الدقيق",
            "advice_ar": "التفسير يحتاج إلى ربط دقيق بالمعارف العلمية. راجع الصفحة 40 لترى الفرق بين التفسير الصحيح والخاطئ.",
        },
        "confusion_analyse_interpret": {
            "page": 39,
            "lesson_title": "الفرق بين التحليل والتفسير",
            "advice_ar": "يبدو أنك اكتفيت بوصف الملاحظات (تحليل) ولم تقدم تفسيراً علمياً. راجع الصفحة 39. تذكر: التفسير = ربط الملاحظة بالقوانين والمفاهيم العلمية.",
        },
    },
    "deduce": {
        "methodology_error": {
            "page": 43,
            "lesson_title": "منهجية الاستنتاج",
            "advice_ar": "الاستنتاج يحتاج إلى مقدمة (معطى) → نتيجة منطقية. راجع الصفحة 43 لتعلم بناء استنتاج صحيح.",
        },
        "scientific_error": {
            "page": 43,
            "lesson_title": "الاستنتاج العلمي",
            "advice_ar": "استنتاجك غير متوافق مع المعطيات العلمية. راجع الصفحة 43 لترى أمثلة على استخلاص النتائج الصحيحة.",
        },
        "confusion_deduire_extraire": {
            "page": 43,
            "lesson_title": "الفرق بين الاستنتاج والاستخلاص",
            "advice_ar": "يبدو أنك استخلصت المعلومة مباشرة من النص بدلاً من استنتاجها. راجع الصفحة 43. تذكر: الاستخلاص = نقل حرفي، الاستنتاج = عملية عقلية منطقية.",
        },
    },
    "justify": {
        "methodology_error": {
            "page": 46,
            "lesson_title": "منهجية التعليل",
            "advice_ar": "التعليل يتطلب: ذكر الحالة → ربطها بالقاعدة → ذكر النتيجة. راجع الصفحة 46.",
        },
        "scientific_error": {
            "page": 46,
            "lesson_title": "التعليل بالمعرفة العلمية",
            "advice_ar": "تعليلك لا يستند إلى المعرفة العلمية الصحيحة. راجع الصفحة 46 لترى أمثلة صحيحة.",
        },
    },
    "discuss": {
        "methodology_error": {
            "page": 47,
            "lesson_title": "منهجية المناقشة",
            "advice_ar": "المناقشة تتطلب وجهين على الأقل ثم الترجيح. راجع الصفحة 47.",
        },
        "scientific_error": {
            "page": 48,
            "lesson_title": "مناقشة بأدلة علمية",
            "advice_ar": "حججك تحتاج إلى أدلة علمية أقوى. راجع الصفحة 48 لترى كيفية بناء حجة علمية.",
        },
    },
    "expliquer": {
        "methodology_error": {
            "page": 49,
            "lesson_title": "منهجية الشرح",
            "advice_ar": "الشرح يتطلب وصفاً منظماً خطوة بخطوة. راجع الصفحة 49.",
        },
        "scientific_error": {
            "page": 50,
            "lesson_title": "شرح دقيق للظواهر",
            "advice_ar": "الشرح يحتوي على أخطاء في المفاهيم. راجع الصفحة 50.",
        },
    },
    "critiquer": {
        "methodology_error": {
            "page": 56,
            "lesson_title": "منهجية النقد",
            "advice_ar": "النقد يتطلب تحديد نقاط القوة والضعف ثم اقتراح التحسين. راجع الصفحة 56.",
        },
        "scientific_error": {
            "page": 57,
            "lesson_title": "نقد علمي موضوعي",
            "advice_ar": "نقدك غير موضوعي أو يفتقر إلى الأدلة. راجع الصفحة 57.",
        },
    },
    "hypothesis": {
        "methodology_error": {
            "page": 51,
            "lesson_title": "منهجية صياغة الفرضية",
            "advice_ar": "الفرضية يجب أن تكون قابلة للاختبار. راجع الصفحة 51.",
        },
        "scientific_error": {
            "page": 52,
            "lesson_title": "فرضية علمية صحيحة",
            "advice_ar": "الفرضية لا تتفق مع المعرفة الحالية. راجع الصفحة 52.",
        },
    },
    "validate-hypothesis": {
        "methodology_error": {
            "page": 53,
            "lesson_title": "منهجية التحقق من الفرضية",
            "advice_ar": "التحقق يتطلب اقتراح تجربة مناسبة. راجع الصفحة 53.",
        },
        "scientific_error": {
            "page": 54,
            "lesson_title": "التحقق التجريبي الدقيق",
            "advice_ar": "تصميم التجربة غير مناسب للفرضية. راجع الصفحة 54.",
        },
    },
    "determiner": {
        "methodology_error": {
            "page": 57,
            "lesson_title": "منهجية التحديد",
            "advice_ar": "التحديد يتطلب قراءة دقيقة للوثيقة. راجع الصفحة 57.",
        },
        "scientific_error": {
            "page": 57,
            "lesson_title": "تحديد دقيق للقيم",
            "advice_ar": "القيمة التي حددتها غير صحيحة علمياً. راجع الصفحة 57.",
        },
    },
    "relationship": {
        "methodology_error": {
            "page": 58,
            "lesson_title": "منهجية إقامة العلاقة",
            "advice_ar": "العلاقة تحتاج إلى ربط سببي أو وظيفي. راجع الصفحة 58.",
        },
        "scientific_error": {
            "page": 58,
            "lesson_title": "علاقات سببية صحيحة",
            "advice_ar": "العلاقة التي أقمتها غير صحيحة علمياً. راجع الصفحة 58.",
        },
    },
    # ═══ تعليمات بسيطة (مغلقة) ════════════════════════════════
    "nommer": {
        "methodology_error": {
            "page": 76,
            "lesson_title": "منهجية التسمية",
            "advice_ar": "التسمية تتطلب الدقة والمصطلح العلمي الصحيح. راجع الصفحة 76.",
        },
        "scientific_error": {
            "page": 77,
            "lesson_title": "المصطلحات العلمية الدقيقة",
            "advice_ar": "المصطلح الذي استعملته غير دقيق. راجع الصفحة 77 للمصطلحات الصحيحة.",
        },
    },
    "definir": {
        "methodology_error": {
            "page": 78,
            "lesson_title": "منهجية التعريف",
            "advice_ar": "التعريف يتطلب: اسم الشيء → جنسه → صفته المميزة. راجع الصفحة 78.",
        },
        "scientific_error": {
            "page": 79,
            "lesson_title": "تعريفات دقيقة",
            "advice_ar": "تعريفك غير دقيق أو ناقص. راجع الصفحة 79 للتعريفات الصحيحة.",
        },
    },
    "decrire": {
        "methodology_error": {
            "page": 8,
            "lesson_title": "منهجية الوصف",
            "advice_ar": "الوصف يتطلب ترتيباً منطقياً للعناصر. راجع الصفحة 8.",
        },
        "scientific_error": {
            "page": 8,
            "lesson_title": "وصف علمي دقيق",
            "advice_ar": "وصفك يفتقر إلى الدقة العلمية. راجع الصفحة 8 للأمثلة.",
        },
    },
    "citer": {
        "methodology_error": {
            "page": 80,
            "lesson_title": "منهجية الاستشهاد",
            "advice_ar": "الاستشهاد يتطلب ذكر العناصر المطلوبة فقط. راجع الصفحة 80.",
        },
        "scientific_error": {
            "page": 80,
            "lesson_title": "استشهاد صحيح",
            "advice_ar": "العناصر التي استشهدت بها غير صحيحة. راجع الصفحة 80.",
        },
    },
    "enumerer": {
        "methodology_error": {
            "page": 81,
            "lesson_title": "منهجية التعداد",
            "advice_ar": "التعداد يتطلب ترتيباً منطقياً. راجع الصفحة 81.",
        },
        "scientific_error": {
            "page": 81,
            "lesson_title": "تعداد كامل",
            "advice_ar": "تعدادك ناقص أو غير صحيح. راجع الصفحة 81.",
        },
    },
    "classer": {
        "methodology_error": {
            "page": 82,
            "lesson_title": "منهجية التصنيف",
            "advice_ar": "التصنيف يتطلب معياراً واضحاً. راجع الصفحة 82.",
        },
        "scientific_error": {
            "page": 82,
            "lesson_title": "تصنيف علمي صحيح",
            "advice_ar": "تصنيفك غير متوافق مع المعايير العلمية. راجع الصفحة 82.",
        },
    },
    "distinguer": {
        "methodology_error": {
            "page": 83,
            "lesson_title": "منهجية التمييز",
            "advice_ar": "التمييز يتطلب عنصرين متشابهين ثم تحديد الفرق. راجع الصفحة 83.",
        },
        "scientific_error": {
            "page": 83,
            "lesson_title": "تمييز دقيق",
            "advice_ar": "التمييز الذي قمت به غير صحيح. راجع الصفحة 83.",
        },
    },
    "schematiser": {
        "methodology_error": {
            "page": 84,
            "lesson_title": "منهجية التخطيط",
            "advice_ar": "الرسم التخطيطي يجب أن يكون مع العناوين والأسهم. راجع الصفحة 84.",
        },
        "scientific_error": {
            "page": 85,
            "lesson_title": "تخطيط علمي صحيح",
            "advice_ar": "محتوى الرسم التخطيطي غير صحيح. راجع الصفحة 85.",
        },
    },
    "scientific-text": {
        "methodology_error": {
            "page": 86,
            "lesson_title": "منهجية كتابة النص العلمي",
            "advice_ar": "النص العلمي يتطلب: مقدمة → عرض منظم → خاتمة. راجع الصفحة 86.",
        },
        "scientific_error": {
            "page": 87,
            "lesson_title": "نص علمي دقيق",
            "advice_ar": "النص يحتوي على أخطاء علمية. راجع الصفحة 87.",
        },
    },
    # ═══ LOT7 — verbes supplémentaires ═══════════════════════
    "extract": {
        "methodology_error": {
            "page": 17,
            "lesson_title": "منهجية الاستخلاص",
            "advice_ar": "الاستخلاص يعني أخذ المعلومة كما هي من الوثيقة دون إضافة أو تحوير. راجع الصفحة 17.",
        },
        "scientific_error": {
            "page": 17,
            "lesson_title": "استخلاص دقيق",
            "advice_ar": "المعلومة التي استخلصتها غير موجودة في الوثيقة أو غير دقيقة. راجع الصفحة 17.",
        },
        "confusion_deduire_extraire": {
            "page": 43,
            "lesson_title": "الفرق بين الاستنتاج والاستخلاص",
            "advice_ar": "يبدو أنك أضفت تفسيراً بدلاً من استخلاص المعلومة. تذكر: الاستخلاص = نقل حرفي من الوثيقة. راجع الصفحة 43.",
        },
    },
    "prove": {
        "methodology_error": {
            "page": 42,
            "lesson_title": "منهجية الإثبات",
            "advice_ar": "الإثبات يتطلب تقديم دليل علمي واضح. راجع الصفحة 42.",
        },
        "scientific_error": {
            "page": 42,
            "lesson_title": "إثبات علمي صحيح",
            "advice_ar": "الدليل الذي قدمته غير كاف أو غير صحيح. راجع الصفحة 42.",
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
    """Retourne la remediation specifique au verbe et a l'erreur.

    Args:
        verb_slug: slug du verbe d'action (analyse, interpret, deduce...)
        error_code: code d'erreur dominant (methodology_error, scientific_error...)

    Returns:
        dict avec page, lesson_title, advice_ar ou None si pas de match.
    """
    verb_data = REMEDIATION_MATRIX.get(verb_slug)
    if verb_data is None:
        return None
    return verb_data.get(error_code)


def get_generic_remediation(error_code: str) -> dict[str, Any] | None:
    """Fallback generique si aucun verbe specifique n'est trouve."""
    return GENERIC_REMEDIATION.get(error_code)


def get_full_remediation(
    verb_slug: str,
    error_code: str,
    unit_key: str | None = None,
    context: str = "",
) -> dict[str, Any]:
    """Remediation enrichie avec contexte scientifique (LOT8)."""
    from prompts.scientific_knowledge import get_contextual_remediation_data

    result: dict[str, Any] = {
        "verb": verb_slug,
        "error_code": error_code,
        "remediation": get_remediation(verb_slug, error_code),
        "generic_remediation": get_generic_remediation(error_code),
    }
    result["contextual"] = get_contextual_remediation_data(verb_slug, context)
    return result
