#!/usr/bin/env python3
"""Génère la banque minimale 55 × (restitution + document) depuis les fiches internes."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_PATH = ROOT / "khawarizmi-frontend/data/chapter-learning-contracts.json"
FICHES_PATH = ROOT / "khawarizmi-frontend/data/fiches-resume.json"
FRONTEND_OUTPUT_PATH = ROOT / "khawarizmi-frontend/data/chapter-exercise-bank.json"
BACKEND_OUTPUT_PATH = ROOT / "khawarizmi-backend/data/chapter_exercise_bank.json"

RESTITUTION_PROMPTS = {
    "rappel": "من ذاكرتك، اذكر المكتسبات الضرورية لفهم «{title}» ونظمها في فقرة علمية قصيرة.",
    "concept": "من ذاكرتك، عرّف «{title}» وحدد خصائصه أو عناصره الأساسية بدقة علمية.",
    "processus": "من ذاكرتك، اشرح «{title}» بترتيب المراحل وذكر البنيات أو الجزيئات المتدخلة.",
    "experience": "من ذاكرتك، اشرح كيف تسمح دراسة «{title}» بتحديد أثر العامل المدروس وصياغة استنتاج.",
    "synthese": "اكتب من ذاكرتك نصا علميا منظما يوضح «{title}» والعلاقات الأساسية التي يتضمنها.",
}

DOCUMENT_PROMPTS = {
    "rappel": "استخرج من الوثيقة معلومتين ضروريتين لفهم «{title}»، ثم نظمهما في خلاصة قصيرة.",
    "concept": "استخرج من الوثيقة معلومتين علميتين تحددان «{title}» أو خصائصه الأساسية.",
    "processus": "استخرج من الوثيقة المراحل أو العلاقات الأساسية المرتبطة بـ«{title}» ورتبها بوضوح.",
    "experience": "استخرج من الوثيقة العامل المدروس وأثره في «{title}»، ثم لخص النتيجة.",
    "synthese": "استخرج من الوثيقة العلاقات العلمية الأساسية حول «{title}» ونظمها في خلاصة.",
}

RESTITUTION_VERBS = {chapter_type: "scientific-text" for chapter_type in RESTITUTION_PROMPTS}
DOCUMENT_VERBS = {chapter_type: "extract" for chapter_type in DOCUMENT_PROMPTS}

EXCLUDED_MARKERS = (
    "اضغط",
    "ستشاهد",
    "ستلاحظ",
    "اختبر",
    "اسحب",
    "اختر",
    "انقر",
)

# Correctifs ciblés lorsque plusieurs chapitres partagent une fiche trop large.
# Les formulations synthétisent le contenu des fiches/livres internes et restent
# explicitement en attente de validation enseignante dans la banque générée.
CURATED_POINTS: dict[str, list[str]] = {
    "d1-u4-c3-les-molecules-de-defense-dans-le-premier-cas-immunite-non-specifique": [
        "تمنع الحواجز الجلدية والمخاطية دخول العناصر الغريبة، وتساهم جزيئات مثل الليزوزيم والمتممة والإنترفيرونات في الدفاع غير النوعي.",
        "عند تجاوز الحواجز تنطلق الاستجابة الالتهابية، ثم تقوم البلعميات بالتعرف غير النوعي على العنصر الغريب وابتلاعه وهضمه.",
        "الاستجابة غير النوعية سريعة ومتشابهة تجاه عناصر غريبة مختلفة ولا تتطلب تعرفا نوعيا سابقا على المستضد.",
    ],
    "d1-u4-c5-origine-des-anticorps": [
        "بعد التعرف النوعي على المستضد وانتقاء اللمفاوية LB الموافقة، تتكاثر هذه الخلية تكاثرا لميا.",
        "تتمايز الخلايا الناتجة إلى خلايا بلازمية مفرزة للأجسام المضادة النوعية وإلى خلايا LB ذاكرة.",
        "إذن مصدر الأجسام المضادة هو الخلايا البلازمية الناتجة عن تنشيط وتمايز اللمفاويات LB النوعية.",
    ],
    "d1-u4-c6-les-elements-de-defense-dans-le-deuxieme-cas-immunite-specifique": [
        "تضم الاستجابة المناعية النوعية استجابة خلطية تقودها اللمفاويات LB والأجسام المضادة، واستجابة خلوية تنفذها اللمفاويات LTc.",
        "تتعرف كل لمفاوية نوعيا على مستضد موافق لمستقبلاتها، ثم تتكاثر وتتمايز إلى خلايا منفذة وخلايا ذاكرة.",
        "تنسق اللمفاويات LTh الاستجابتين بإفراز رسائل كيميائية مثل IL-2 تنشط LB وLT8.",
    ],
    "d1-u4-c8-origine-des-lymphocytes-ltc": [
        "تنشأ الخلايا اللمفاوية من خلايا جذعية في نخاع العظم، وتنضج الخلايا التائية في الغدة السعترية.",
        "بعد التعرف النوعي المزدوج على خلية مصابة وبوجود تنشيط من LTh، تتكاثر اللمفاويات LT8 الموافقة تكاثرا لميا.",
        "تتمايز اللمفاويات LT8 المنشطة إلى خلايا قاتلة LTc منفذة وإلى خلايا ذاكرة.",
    ],
    "d1-u4-c10-choix-du-type-de-reponse-immunitaire": [
        "توجَّه الاستجابة الخلطية نحو المستضدات الحرة خارج الخلايا، حيث تنتج الخلايا البلازمية أجساما مضادة نوعية.",
        "توجَّه الاستجابة الخلوية نحو خلايا الذات المصابة أو الغريبة، حيث تتعرف عليها LTc ثم تخربها.",
        "يحدد موضع المستضد وطبيعته نمط الاستجابة، بينما تنسق LTh تنشيط LB وLT8.",
    ],
    "d1-u4-c11-cause-de-la-perte-de-l-immunite-acquise-sida": [
        "يصيب فيروس VIH خصوصا اللمفاويات المساعدة LTh الحاملة للمؤشر CD4 ويتكاثر داخلها ثم يؤدي إلى تناقص عددها.",
        "يؤدي نقص LTh إلى ضعف إفراز الرسائل المنشطة، فلا تنشط اللمفاويات LB وLT8 بكفاءة.",
        "تفقد الاستجابتان الخلطية والخلوية فعاليتهما فتظهر أمراض انتهازية تميز مرحلة SIDA.",
    ],
    "d2-u2-c2-siege-de-l-oxydation-respiratoire": [
        "يحدث التحلل السكري في الهيولى، بينما تتم أكسدة حمض البيروفيك ودورة كريبس في مطرس الميتوكندري.",
        "تتم السلسلة التنفسية والفسفرة التأكسدية على مستوى الغشاء الداخلي وأعراف الميتوكندري.",
        "إذن الميتوكندري هو مقر الأكسدة التنفسية الأساسية، ويضمن تنظيمه الحجيري تكامل مراحل إنتاج ATP.",
    ],
    "d2-u2-c5-la-phosphorylation-oxydative": [
        "الأكسجين هو المستقبل النهائي لإلكترونات السلسلة التنفسية، ويؤدي إرجاعه إلى تشكل الماء.",
        "حسب الحصيلة المعتمدة داخليا، تسمح أكسدة كل NADH بإنتاج 3 ATP وكل FADH₂ بإنتاج 2 ATP.",
        "ينشئ انتقال الإلكترونات تدرجا بروتونيا عبر الغشاء الداخلي، وتستعمل ATP synthase هذا التدرج لفسفرة ADP.",
    ],
    "d2-u2-c6-mecanismes-de-conversion-en-milieu-anaerobie-fermentation": [
        "يحدث التخمر في الهيولى عند غياب الأكسجين ويهدم الغلوكوز هدما جزئيا.",
        "يسمح التخمر بتجديد +NAD الضروري لاستمرار التحلل السكري، وتبقى حصيلته الطاقوية الصافية 2 ATP لكل غلوكوز.",
        "قد يكون التخمر لبنيا منتجا حمض اللبن أو كحوليا منتجا الإيثانول وCO₂ حسب الخلايا والوسط.",
    ],
    "d3-u1-c3-l-energie-interne-du-globe-terrestre": [
        "ينتج جزء مهم من الطاقة الداخلية للأرض عن التفكك الإشعاعي لنظائر اليورانيوم والثوريوم والبوتاسيوم.",
        "تنتقل الحرارة ببطء بالتوصيل في الغلاف الصخري الصلب، وتنتقل بالحمل الحراري في مواد البرنس القابلة للتشوه.",
        "تحول تيارات الحمل جزءا من الطاقة الحرارية الداخلية إلى حركة ميكانيكية تساهم في حركة الصفائح.",
    ],
    "d3-u3-c7-indices-du-raccourcissement": [
        "تدل الطيات المتقاربة والفوالق المعكوسة والتراكبات على تعرض القشرة لقوى انضغاطية سببت تقصيرها أفقيا.",
        "يؤدي تراكم الشرائح الصخرية إلى زيادة سمك القشرة وتشكل جذر قاري عميق تحت السلسلة الجبلية.",
        "تسمح مقارنة طول الطبقات قبل التشوه وبعده بإثبات التقصير المرتبط بتقارب كتلتين قاريتين وتصادمهما.",
    ],
}


def clean_text(value: str) -> str:
    value = re.sub(r"^[\s•*#🟢🟡🔴💡📈🧪✅⚠️]+", "", value).strip()
    value = value.replace("؟", ".").replace("?", ".")
    return re.sub(r"\s+", " ", value)


def select_scientific_points(
    chapter_slug: str,
    fiches: list[dict],
    limit: int = 4,
) -> list[dict[str, str]]:
    if chapter_slug in CURATED_POINTS:
        source_id = fiches[0]["id"]
        return [
            {"textAr": text, "sourceFicheId": source_id}
            for text in CURATED_POINTS[chapter_slug]
        ]

    candidates: list[dict[str, str]] = []
    seen: set[str] = set()
    for fiche in fiches:
        for raw in [*fiche.get("idees", []), *fiche.get("bac", [])]:
            text = clean_text(raw)
            if len(text) < 45 or any(marker in text for marker in EXCLUDED_MARKERS):
                continue
            key = text.casefold()
            if key in seen:
                continue
            seen.add(key)
            candidates.append({"textAr": text, "sourceFicheId": fiche["id"]})

    if len(candidates) < 2:
        for fiche in fiches:
            text = clean_text(fiche.get("objectif", ""))
            if len(text) < 30 or text.casefold() in seen:
                continue
            seen.add(text.casefold())
            candidates.append({"textAr": text, "sourceFicheId": fiche["id"]})

    return candidates[:limit]


def build_reference(
    points: list[dict[str, str]],
    objective: str,
    *,
    kind: str,
    title: str,
) -> str:
    statements = [point["textAr"] for point in points[:3]]
    if len(statements) < 2:
        statements.append(objective)
    if kind == "document":
        return (
            f"يتضح من الوثيقة حول «{title}» أن {statements[0]} "
            f"كما يظهر أن {statements[1]} "
            f"نستخلص أن {statements[2] if len(statements) > 2 else objective}"
        )
    return (
        f"مقدمة: يتناول الفصل «{title}». أولا، {statements[0]} "
        f"ثانيا، {statements[1]} "
        f"في الختام، نستنتج أن {statements[2] if len(statements) > 2 else objective}"
    )


def main() -> None:
    contracts_payload = json.loads(CONTRACTS_PATH.read_text(encoding="utf-8"))
    contracts = contracts_payload["contracts"]
    fiches = {item["id"]: item for item in json.loads(FICHES_PATH.read_text(encoding="utf-8"))}

    chapters = []
    for contract in contracts:
        linked_fiches = [fiches[fiche_id] for fiche_id in contract["ficheIds"] if fiche_id in fiches]
        if not linked_fiches:
            raise ValueError(f"Aucune fiche source pour {contract['chapterSlug']}")

        points = select_scientific_points(contract["chapterSlug"], linked_fiches)
        if len(points) < 2:
            raise ValueError(f"Moins de deux données scientifiques pour {contract['chapterSlug']}")

        chapter_type = contract.get("type", "concept")
        title = contract["titleAr"]
        restitution_reference = build_reference(
            points,
            contract["objectiveAr"],
            kind="restitution",
            title=title,
        )
        document_reference = build_reference(
            points,
            contract["objectiveAr"],
            kind="document",
            title=title,
        )
        source_ids = [fiche["id"] for fiche in linked_fiches]
        common = {
            "validationStatus": "internal_pending_teacher",
            "formativeOnly": True,
            "isEnrichment": False,
            "contentOrigin": (
                "curated_internal_synthesis"
                if contract["chapterSlug"] in CURATED_POINTS
                else "source_excerpt"
            ),
            "sourceFicheIds": source_ids,
        }

        restitution = {
            "id": f"{contract['chapterSlug']}:restitution",
            "kind": "restitution",
            "verbSlug": RESTITUTION_VERBS.get(chapter_type, "scientific-text"),
            "titleAr": "نشاط استرجاع علمي",
            "promptAr": RESTITUTION_PROMPTS.get(chapter_type, RESTITUTION_PROMPTS["concept"]).format(title=title),
            "documents": [],
            "referenceAnswerAr": restitution_reference,
            "criteria": [
                {"code": "scientific_core", "labelAr": "يذكر المعارف العلمية الأساسية المرتبطة بالفصل.", "points": 2},
                {"code": "scientific_relation", "labelAr": "يربط العناصر أو المراحل بعلاقة علمية صحيحة.", "points": 1},
                {"code": "scientific_terms", "labelAr": "يستعمل المصطلحات العلمية الدقيقة دون حشو.", "points": 1},
            ],
            "scoreMax": 4,
            **common,
        }

        document = {
            "id": f"{contract['chapterSlug']}:document",
            "kind": "document",
            "verbSlug": DOCUMENT_VERBS.get(chapter_type, "analyse"),
            "titleAr": "نشاط استغلال وثيقة",
            "promptAr": DOCUMENT_PROMPTS.get(chapter_type, DOCUMENT_PROMPTS["concept"]).format(title=title),
            "documents": [
                {
                    "id": f"doc-{contract['chapterSlug']}",
                    "titleAr": f"وثيقة داخلية: {title}",
                    "captionAr": "معطيات مبنية على fiches ومراجع الدرس الداخلية وليست وثيقة ONEC.",
                    "dataAr": [point["textAr"] for point in points],
                    "sourceFicheIds": sorted({point["sourceFicheId"] for point in points}),
                }
            ],
            "referenceAnswerAr": document_reference,
            "criteria": [
                {"code": "document_evidence", "labelAr": "يستخرج معلومتين واضحتين من الوثيقة دون نسخ عشوائي.", "points": 2},
                {"code": "document_relation", "labelAr": "يربط المعطيات وفق المطلوب وعلاقة علمية صحيحة.", "points": 1},
                {"code": "document_conclusion", "labelAr": "يصوغ استنتاجا قصيرا يجيب عن السؤال.", "points": 1},
            ],
            "scoreMax": 4,
            **common,
        }

        chapters.append(
            {
                "chapterSlug": contract["chapterSlug"],
                "domainNumero": contract["domainNumero"],
                "unitNumero": contract["unitNumero"],
                "chapterNumero": contract["chapterNumero"],
                "titleAr": title,
                "titleFr": contract["titleFr"],
                "practiceHref": contract["practiceHref"],
                "courseHref": contract["courseHref"],
                "activities": [restitution, document],
            }
        )

    if len(chapters) != 55 or len({item["chapterSlug"] for item in chapters}) != 55:
        raise ValueError("La banque doit couvrir exactement 55 chapitres uniques")
    if sum(len(item["activities"]) for item in chapters) != 110:
        raise ValueError("La banque doit contenir exactement 110 activités")

    output = {
        "metadata": {
            "version": "2026-08-22.2",
            "source": "fiches-resume-et-syntheses-internes",
            "validationStatus": "internal_pending_teacher",
            "scope": "formative_only",
            "chapterCount": len(chapters),
            "activityCount": 110,
            "activitiesPerChapter": {"restitution": 1, "document": 1},
            "provenanceNoticeFr": "Banque dérivée des fiches internes; aucune revendication ONEC ou validation ministérielle.",
            "provenanceNoticeAr": "بنك مشتق من fiches داخلية؛ لا يحمل صفة وثيقة ONEC أو اعتماد وزاري.",
        },
        "chapters": chapters,
    }
    serialized = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    FRONTEND_OUTPUT_PATH.write_text(serialized, encoding="utf-8")
    BACKEND_OUTPUT_PATH.write_text(serialized, encoding="utf-8")
    print(
        f"Generated {FRONTEND_OUTPUT_PATH} and {BACKEND_OUTPUT_PATH} "
        f"({len(chapters)} chapters, 110 activities)"
    )


if __name__ == "__main__":
    main()
