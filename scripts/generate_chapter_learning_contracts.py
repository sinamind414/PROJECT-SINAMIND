#!/usr/bin/env python3
"""Génère les contrats d’apprentissage des 55 chapitres depuis le référentiel."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAMME = ROOT / "khawarizmi-backend/data/programmes/svt_sciences_experimentales.json"
FICHE_MAP = ROOT / "khawarizmi-frontend/data/chapitres-fiches-map.json"
OUTPUT = ROOT / "khawarizmi-frontend/data/chapter-learning-contracts.json"

VERBS_BY_TYPE = {
    "rappel": ["analyse", "justify"],
    "concept": ["analyse", "interpret", "compare", "relationship"],
    "processus": ["analyse", "interpret", "deduce", "scientific-text"],
    "experience": ["analyse", "interpret", "justify", "deduce"],
    "synthese": ["scientific-text", "compare", "relationship", "deduce"],
}

CHECKLISTS = {
    "rappel": [
        "أحدد فعل التعليمة والمطلوب بدقة.",
        "أسترجع التعاريف والمكتسبات الضرورية فقط.",
        "أستعمل المصطلحات العلمية الصحيحة بالعربية والفرنسية.",
        "أربط المكتسب السابق بموضوع الوحدة الحالية.",
        "أجيب بجمل قصيرة ومنظمة دون حشو.",
        "أتحقق أن كل جملة تجيب عن المطلوب ولا تخرج عن الموضوع.",
    ],
    "concept": [
        "أحدد فعل التعليمة والمهمة المطلوبة.",
        "أعرّف المفهوم العلمي بعبارة دقيقة.",
        "أحدد عناصر المفهوم أو خصائصه الأساسية.",
        "أقيم العلاقة بين العناصر دون خلط السبب بالنتيجة.",
        "أستشهد بمعطى أو قيمة من الوثيقة عند وجودها.",
        "أختم بخلاصة قصيرة تستعمل المصطلحات العلمية الصحيحة.",
    ],
    "processus": [
        "أحدد فعل التعليمة وبداية العملية ونهايتها.",
        "أرتب المراحل زمنيا أو وظيفيا دون قفز.",
        "أسمي البنيات والجزيئات المتدخلة في كل مرحلة.",
        "أشرح الانتقال من مرحلة إلى التالية برابط سببي صحيح.",
        "أحترم المقر والاتجاه والأسهم والحصيلة.",
        "أراجع التسلسل وأكتب النتيجة النهائية للعملية.",
    ],
    "experience": [
        "أحدد المشكلة العلمية والمتغير المدروس.",
        "أميز الشاهد عن التجربة وأثبت ثبات باقي الشروط.",
        "أستخرج الملاحظات والقيم دون تفسير مسبق.",
        "أقارن النتائج باستعمال معيار مشترك.",
        "أفسر النتائج بمعرفة علمية مرتبطة بالوثيقة.",
        "أصوغ استنتاجا يجيب مباشرة عن المشكلة العلمية.",
    ],
    "synthese": [
        "أحدد المشكلة وفعل التعليمة قبل الكتابة.",
        "أبني مخططا: مقدمة، عرض، خاتمة.",
        "أستغل جميع الوثائق المطلوبة دون نسخها.",
        "أدمج المعارف العلمية بروابط منطقية وسببية.",
        "أستعمل المصطلحات والاتجاهات والحصائل بدقة.",
        "أراجع أن الخاتمة تجيب عن المشكلة وأن النص خال من التناقض.",
    ],
}


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFD", value).lower()
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", value))


def main() -> None:
    programme = json.loads(PROGRAMME.read_text(encoding="utf-8"))
    fiche_map = {
        item["chapterSlug"]: item["ficheIds"]
        for item in json.loads(FICHE_MAP.read_text(encoding="utf-8"))
    }
    contracts = []
    for domain in programme["domains"]:
        for unit in domain["units"]:
            for chapter in unit["chapters"]:
                chapter_type = chapter.get("type") or "concept"
                chapter_slug = (
                    f"d{domain['numero']}-u{unit['numero']}-c{chapter['numero']}-"
                    f"{slugify(chapter['titre_fr'])}"
                )
                if chapter_slug not in fiche_map:
                    raise ValueError(f"Fiche absente pour {chapter_slug}")
                contracts.append(
                    {
                        "chapterSlug": chapter_slug,
                        "domainNumero": domain["numero"],
                        "unitNumero": unit["numero"],
                        "chapterNumero": chapter["numero"],
                        "titleAr": chapter.get("titre_ar") or chapter["titre_fr"],
                        "titleFr": chapter["titre_fr"],
                        "type": chapter_type,
                        "importance": chapter.get("importance", "moyenne"),
                        "validationStatus": "internal_pending_teacher",
                        "objectiveAr": (
                            f"أن يتمكن التلميذ من معالجة «{chapter.get('titre_ar') or chapter['titre_fr']}» "
                            "بدقة علمية ووفق فعل التعليمة في وضعية بكالوريا."
                        ),
                        "recommendedVerbs": VERBS_BY_TYPE.get(chapter_type, VERBS_BY_TYPE["concept"]),
                        "checklistAr": CHECKLISTS.get(chapter_type, CHECKLISTS["concept"]),
                        "ficheIds": fiche_map[chapter_slug],
                        "courseHref": f"/cours/d{domain['numero']}/u{unit['numero']}/{chapter_slug}",
                        "practiceHref": f"/document-analysis/chapters/{chapter_slug}",
                        "exerciseHref": f"/exercices/{chapter_slug}",
                    }
                )

    if len(contracts) != 55 or len({item["chapterSlug"] for item in contracts}) != 55:
        raise ValueError("Le référentiel doit produire exactement 55 contrats uniques")

    output = {
        "metadata": {
            "version": "2026-08-22.2",
            "source": "referentiel-interne-svt-3as",
            "validationStatus": "internal_pending_teacher",
            "count": len(contracts),
            "checklistLength": 6,
        },
        "contracts": contracts,
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {OUTPUT} ({len(contracts)} contracts)")


if __name__ == "__main__":
    main()
