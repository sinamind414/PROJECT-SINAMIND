"""
prompts/correction_prompt.py — Prompt de correction « comme un prof ».

Prompt système en arabe classique pour évaluer les réponses d'élèves
en SVT (BAC Sciences Naturelles algérien). Ancré dans la méthodologie
officielle du LIVRE MANHADJIYA.

Fonctions exportées :
- build_correction_prompt(...)  → construit le prompt user complet
- SYSTEM_PROMPT_AR              → prompt système (instructions au LLM)
- VERB_METHODOLOGY_AR           → méthodologie par verbe (extraits du livre)
- MANHADJIYA_RUBRICS            → rubriques structurées (steps, common_errors, keywords)
- normalize_arabic(text)        → normalisation de texte arabe
"""

from __future__ import annotations

import re
from typing import Any

# ── Prompt système (instructions au LLM) ──────────

SYSTEM_PROMPT_AR = """أنت مصحح امتحان البكالوريا في مادة العلوم الطبيعية (الجزائر).
مهمتك تصحيح إجابة التلميذ وإعطاء ملاحظات بناءة.

## القواعد الصارمة:

1. **التصحيح بالمقارنة مع الإجابة النموذجية والمنهجية المطلوبة فقط** — لا تخترع معايير جديدة.
2. **النقطة تُعطى فقط إذا ذُكر المفهوم الصحيح** — لا تعطِ نقاطاً على كلام عام.
3. **الكلام غير المفهوم = صفر** — لا تحاول إيجاد معنى في نص غير مفهوم.
4. **التغذية الراجعة باللغة العربية فقط**.
5. **أجب بصيغة JSON فقط** — لا تكتب أي شيء خارج بنية JSON.

## بنية JSON المطلوبة:

```json
{
  "score": <int>,
  "matched_criteria": ["<معيار تم استيفاؤه>", ...],
  "unmatched_criteria": [
    {
      "criterion": "<معيار لم يُستوفَ>",
      "why_ar": "<لماذا لم يُستوفَ>",
      "from_model_answer": "<المقطع المناسب من الإجابة النموذجية>"
    }
  ],
  "highlights": [
    {
      "start": <int>,
      "end": <int>,
      "type": "<نوع>",
      "message_ar": "<ملاحظة>"
    }
  ],
  "feedback_ar": "<تعليق عام 2-4 أسطر>",
  "advice_ar": "<نصيحة تحسين واحدة>",
  "confidence": <float 0.0-1.0>
}
```

## أنواع highlights المسموحة:
- `good_element` — عنصر صحيح
- `off_topic` — خارج الموضوع
- `missing_link` — رابط منطقي ناقص
- `wrong_formulation` — صياغة خاطئة
- `irrelevant` — غير ذي صلة

## حساب النقطة:
- score ∈ [0, score_max]
- لكل معيار: أعطِ النقطة كاملة أو صفر (لا نصف نقطة)
- highlights.start و highlights.end = فهرس الحرف في نص التلميذ (0-indexed)

تذكر: أنت مصحح صارم لكن عادل. لا تعاقب على الأخطاء الإملائية البسيطة."""

# ── Méthodologie par verbe (extraits du LIVRE MANHADJIYA) ──────

VERB_METHODOLOGY_AR: dict[str, str] = {
    "analyse": """## منهجية فعل «حلّل»
- **الهدف**: وصف ما تُظهره الوثيقة دون تفسير.
- **الخطوات**:
  1. تقديم الوثيقة (طبيعتها، عنوانها، ما تمثله)
  2. قراءة المعطيات (الأرقام، الاتجاهات، التغيرات)
  3. المقارنة بين المعطيات إن وُجدت
- **الكلمات المفتاحية**: نلاحظ، يُظهر، يتغير، يزداد، ينخفض، ثابت
- **الممنوع**: لا تفسير (لأن، بسبب) — لا استنتاج""",

    "interpret": """## منهجية فعل «فسّر»
- **الهدف**: إعطاء السبب العلمي لظاهرة ملاحَظة.
- **الخطوات**:
  1. ذكر الملاحظة المراد تفسيرها
  2. ربطها بالمعلومة العلمية (من الدرس)
  3. استعمال روابط السببية
- **الكلمات المفتاحية**: لأن، بسبب، يعود ذلك إلى، يُفسَّر بـ
- **البنية**: ملاحظة + سبب علمي""",

    "deduce": """## منهجية فعل «استنتج»
- **الهدف**: استخلاص نتيجة منطقية من معطيات.
- **الخطوات**:
  1. ذكر المعطيات الأساسية (باختصار)
  2. الربط المنطقي
  3. صياغة الاستنتاج
- **الكلمات المفتاحية**: نستنتج أن، ومنه، يدل ذلك على، نستخلص
- **ملاحظة**: الاستنتاج يجب أن يكون مختصراً وواضحاً""",

    "hypothesis": """## منهجية فعل «اقترح فرضية»
- **الهدف**: طرح تفسير محتمل قابل للتحقق.
- **الخطوات**:
  1. تحديد المشكلة أو الظاهرة
  2. صياغة الفرضية بشكل واضح
  3. يجب أن تكون قابلة للاختبار
- **الكلمات المفتاحية**: نفترض أن، قد يكون، ربما، من المحتمل
- **البنية**: إذا... فإن... (شرطية)""",

    "scientific-text": """## منهجية «النص العلمي»
- **الهدف**: كتابة فقرة علمية متماسكة تلخص المعلومات.
- **الخطوات**:
  1. مقدمة (تحديد الموضوع)
  2. عرض المعلومات بترتيب منطقي
  3. استعمال الروابط المنطقية
  4. خلاصة
- **المعايير**: الترابط، التسلسل المنطقي، المصطلحات العلمية
- **الطول**: 5-10 أسطر على الأقل""",

    "compare": """## منهجية فعل «قارن»
- **الهدف**: إبراز أوجه التشابه والاختلاف بين عنصرين أو أكثر.
- **الخطوات**:
  1. تحديد عناصر المقارنة (معيار بمعيار)
  2. ذكر التشابهات
  3. ذكر الاختلافات
- **الكلمات المفتاحية**: بينما، على عكس، مقارنة بـ، أكبر/أقل من
- **البنية**: جدول مقارنة أو فقرة منظمة""",

    "justify": """## منهجية فعل «علّل» / «برّر»
- **الهدف**: تقديم حجج علمية لدعم موقف أو نتيجة.
- **الخطوات**:
  1. ذكر النتيجة أو الموقف
  2. تقديم الحجة العلمية
  3. الاستشهاد بالوثيقة/المعطيات
- **الكلمات المفتاحية**: لأن، بسبب، بدليل أن، الوثيقة تُظهر أن
- **ملاحظة**: التعليل يختلف عن التفسير — هنا نبرر موقفاً""",

    "validate-hypothesis": """## منهجية «التحقق من صحة فرضية»
- **الهدف**: تأكيد أو نفي فرضية بناءً على نتائج تجريبية.
- **الخطوات**:
  1. إعادة ذكر الفرضية
  2. مقارنة مع النتائج المحصل عليها
  3. الحكم: الفرضية صحيحة/خاطئة
- **الكلمات المفتاحية**: نستنتج أن الفرضية صحيحة/خاطئة لأن
- **البنية**: فرضية + نتيجة + حكم + تعليل""",

    "discuss": """## منهجية فعل «ناقش»
- **الهدف**: تحليل موضوع من عدة زوايا.
- **الخطوات**:
  1. عرض الطرح الأول (مع حجج)
  2. عرض الطرح المقابل (مع حجج)
  3. المقارنة والتوصل إلى موقف
- **الكلمات المفتاحية**: من جهة... ومن جهة أخرى، بينما
- **البنية**: أطروحة + نقيض + تركيب""",

    "relationship": """## منهجية «العلاقة بين»
- **الهدف**: تحديد طبيعة العلاقة بين متغيرين.
- **الخطوات**:
  1. ذكر المتغيرين
  2. وصف تأثير أحدهما على الآخر
  3. تحديد نوع العلاقة (طردية/عكسية/سببية)
- **الكلمات المفتاحية**: كلما... كلما، العلاقة طردية/عكسية
- **البنية**: متغير1 ← تأثير → متغير2 + نوع العلاقة""",
}


# ── Rubriques structurées Manhadjiya (Blueprint § Fichier B) ──────

MANHADJIYA_RUBRICS: dict[str, dict[str, Any]] = {
    "analyse": {
        "steps": ["Définition doc", "Décomposition", "Relation", "Conclusion"],
        "common_errors": "Confondre analyse et interprétation",
        "keywords": ["تمثل الوثيقة", "نلاحظ", "كلما"],
    },
    "interpret": {
        "steps": ["Rappel fait", "Justification", "Causalité", "Conclusion"],
        "common_errors": "Sauter la justification",
        "keywords": ["بسبب", "راجع إلى"],
    },
    "deduce": {
        "steps": ["Synthèse", "Logique", "Réponse concise"],
        "common_errors": "Trop long",
        "keywords": ["نستنتج", "ومنه"],
    },
    "hypothesis": {
        "steps": ["Formulation hypothétique", "Lien problème", "Mécanisme"],
        "common_errors": "Présentée comme certitude",
        "keywords": ["نفترض أن", "ربما"],
    },
    "scientific-text": {
        "steps": ["Intro", "Développement structuré", "Conclusion"],
        "common_errors": "Oubli intro/conclusion",
        "keywords": ["مقدمة", "عرض", "خاتمة"],
    },
}


# ── Normalisation de texte arabe ──────────────────

_ARABIC_DIACRITICS = re.compile(r"[\u064B-\u0652\u0670\u0640]")
_ALEF_VARIANTS = {"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا"}
_TA_MARBUTA = re.compile(r"ة")


def normalize_arabic(text: str) -> str:
    if not text:
        return ""
    t = _ARABIC_DIACRITICS.sub("", text)
    for variant, canonical in _ALEF_VARIANTS.items():
        t = t.replace(variant, canonical)
    t = _TA_MARBUTA.sub("ه", t)
    return t.lower().strip()


# ── Construction du prompt utilisateur ────────────


def build_correction_prompt(
    *,
    scenario_context: str,
    documents: list[dict[str, Any]] | None,
    question_prompt: str,
    question_skill: str,
    verb_slug: str,
    model_answer: str,
    learning_focus: str | None,
    score_max: int,
    student_answer: str,
) -> str:
    """Construit le prompt user envoyé au LLM pour corriger une réponse.

    Le prompt inclut :
    - Le contexte du scénario (situation-problème)
    - La description des documents (si disponibles)
    - La consigne exacte (question)
    - La méthodologie du verbe d'action
    - L'éjabée النموذجية (model answer)
    - La copie de l'élève
    - Le barème (score_max)
    """
    parts: list[str] = []

    # Contexte du scénario
    parts.append(f"## السياق\n{scenario_context}")

    # Documents
    if documents:
        docs_text = []
        for i, doc in enumerate(documents, 1):
            title = doc.get("title") or doc.get("title_ar") or f"وثيقة {i}"
            caption = doc.get("caption") or doc.get("caption_ar") or ""
            data = doc.get("data")
            doc_str = f"### الوثيقة {i}: {title}"
            if caption:
                doc_str += f"\n{caption}"
            if data:
                if isinstance(data, dict):
                    # Résumé structurel pour le LLM
                    doc_str += f"\nالبيانات: {_summarize_data(data)}"
                elif isinstance(data, str):
                    doc_str += f"\n{data}"
            docs_text.append(doc_str)
        parts.append("## الوثائق\n" + "\n\n".join(docs_text))

    # Consigne
    parts.append(f"## السؤال\n**المهارة**: {question_skill}\n**التعليمة**: {question_prompt}")

    # Méthodologie du verbe
    methodology = VERB_METHODOLOGY_AR.get(verb_slug)
    if methodology:
        parts.append(f"## المنهجية المطلوبة\n{methodology}")

    # Focus pédagogique
    if learning_focus:
        parts.append(f"## التركيز التعليمي\n{learning_focus}")

    # Réponse modèle
    parts.append(f"## الإجابة النموذجية\n{model_answer}")

    # Barème
    parts.append(f"## السلم\nالنقطة القصوى: {score_max}")

    # Copie de l'élève
    parts.append(f"## إجابة التلميذ\n{student_answer}")

    # Instruction finale
    parts.append(
        "## التعليمات\n"
        "صحّح إجابة التلميذ بالمقارنة مع الإجابة النموذجية والمنهجية المطلوبة.\n"
        "أعطِ النقطة والملاحظات بصيغة JSON فقط."
    )

    return "\n\n".join(parts)


def _summarize_data(data: dict) -> str:
    """Résumé compact d'un objet data de document pour le prompt LLM."""
    doc_type = data.get("type")
    unit = data.get("unit")

    # ── Graphiques à points (méthodology-documents.ts) ──
    if "points" in data:
        points = data["points"]
        if isinstance(points, list) and points:
            labels_values = []
            numeric_values = []
            for p in points[:8]:
                if not isinstance(p, dict):
                    continue
                label = p.get("label") or p.get("x") or "?"
                value = p.get("value") or p.get("y")
                labels_values.append(f"{label}={value}{unit or ''}")
                if isinstance(value, (int, float)):
                    numeric_values.append(value)
            trend = ""
            if len(numeric_values) >= 2:
                if numeric_values[-1] > numeric_values[0]:
                    trend = " | اتجاه: ارتفاع"
                elif numeric_values[-1] < numeric_values[0]:
                    trend = " | اتجاه: انخفاض"
                else:
                    trend = " | اتجاه: ثبات"
            axes = []
            if data.get("xLabel"):
                axes.append(f"س={data['xLabel']}")
            if data.get("yLabel"):
                axes.append(f"ع={data['yLabel']}")
            prefix = doc_type or "رسم بياني"
            base = f"{prefix}: {'؛ '.join(axes)}" if axes else prefix
            return f"{base} | القيم: {', '.join(labels_values)}{trend}"

    # ── Graphiques à labels+values (format DB brut) ──
    if "labels" in data and "values" in data:
        labels = data["labels"]
        values = data["values"]
        if isinstance(values, list) and values:
            if isinstance(values[0], dict):
                series_names = [v.get("label", "?") for v in values[:3]]
                return f"رسم بياني: {', '.join(map(str, labels[:5]))}... | سلاسل: {', '.join(series_names)}"
            return f"رسم بياني: {', '.join(map(str, labels[:5]))}... → {', '.join(map(str, values[:5]))}..."

    # ── Tableaux ──
    if "rows" in data:
        rows = data["rows"]
        n = len(rows)
        if n > 0 and isinstance(rows[0], dict):
            columns = data.get("columns") or []
            # Format méthodology-documents.ts : {columns: [...], rows: [{cells: [...], tone: ...}]}
            if columns and isinstance(rows[0].get("cells"), list):
                lines = []
                for r in rows[:5]:
                    cells = r.get("cells", [])
                    pairs = [f"{columns[i]}={cells[i]}" for i in range(min(len(columns), len(cells)))]
                    lines.append(" | ".join(pairs))
                return f"جدول ({n} صفوف):\n" + "\n".join(lines)
            # Format dict plat : clés = colonnes
            skip_keys = {"tone", "style", "className"}
            cols = [c for c in rows[0].keys() if c not in skip_keys]
            if cols:
                lines = []
                for r in rows[:5]:
                    vals = [str(r.get(c, "")) for c in cols]
                    lines.append(" | ".join(vals))
                return f"جدول ({n} صفوف):\n" + "\n".join(lines)
        return f"جدول بـ {n} صفوف"

    # ── Schémas / flux (steps + arrows) ──
    if "steps" in data:
        steps = data["steps"]
        arrows = data.get("arrows") or []
        n = len(steps)
        if isinstance(steps, list) and steps:
            parts = []
            for i, step in enumerate(steps[:8]):
                parts.append(str(step))
                if i < len(arrows):
                    parts.append(f"←{arrows[i]}→")
            return f"مخطط تدفق ({n} خطوات): " + " ".join(parts)
        return f"مخطط تدفق بـ {n} خطوات"

    # Fallback
    import json
    return json.dumps(data, ensure_ascii=False)[:200]
