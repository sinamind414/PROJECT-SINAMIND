"""remediation_service.py — Correction intelligente : page du livre MANHADJIYA.

Mapper l'erreur dominante (dominant_error_code) vers une page précise
du livre pour la remédiation automatique de l'élève.
"""

from __future__ import annotations

from typing import Any

REMEDIATION_MATRIX: dict[str, dict[str, dict[str, Any]]] = {
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
