"""
services/units.py — Catalogue canonique des 11 unités du programme SVT 3AS.

Normalise les formats incohérents du champ `unit` des QCM.
"""

import re

UNITS_CATALOG = [
    {"id": "u1", "domain_ar": "التخصص الوظيفي للبروتينات", "unit_ar": "تركيب البروتين",
     "keywords": ["تركيب البروتين", "الاستنساخ", "الترجمة"]},
    {"id": "u2", "domain_ar": "التخصص الوظيفي للبروتينات", "unit_ar": "العلاقة بين بنية ووظيفة البروتين",
     "keywords": ["بنية ووظيفة", "البنية", "الهيموغلوبين", "الكولاجين"]},
    {"id": "u3", "domain_ar": "التخصص الوظيفي للبروتينات", "unit_ar": "النشاط الإنزيمي للبروتينات",
     "keywords": ["النشاط الإنزيمي", "الإنزيم", "الموقع الفعال", "الركيزة"]},
    {"id": "u4", "domain_ar": "التخصص الوظيفي للبروتينات", "unit_ar": "دور البروتينات في الدفاع عن الذات",
     "keywords": ["الدفاع عن الذات", "المناعة", "المستضد", "الأجسام المضادة", "VIH"]},
    {"id": "u5", "domain_ar": "التخصص الوظيفي للبروتينات", "unit_ar": "دور البروتينات في الاتصال العصبي",
     "keywords": ["الاتصال العصبي", "العصبون", "كمون", "السيالة العصبية", "المشبك"]},
    {"id": "u6", "domain_ar": "التحولات الطاقوية", "unit_ar": "التركيب الضوئي",
     "keywords": ["التركيب الضوئي", "الصانعة الخضراء", "كلوروفيل", "كالفن", "الطاقة الضوئية"]},
    {"id": "u7", "domain_ar": "التحولات الطاقوية", "unit_ar": "التنفس الخلوي والتخمر",
     "keywords": ["التنفس الخلوي", "الميتوكندري", "كريبس", "التخمر"]},
    {"id": "u8", "domain_ar": "التحولات الطاقوية", "unit_ar": "الحصيلة الطاقوية على المستوى الخلوي",
     "keywords": ["الحصيلة الطاقوية", "ATP", "الفسفرة", "تحويل الطاقة على المستوى الخلوي"]},
    {"id": "u9", "domain_ar": "التكتونية العامة", "unit_ar": "النشاط التكتوني للصفائح",
     "keywords": ["النشاط التكتوني للصفائح", "الصفائح", "الزلازل", "التيارات الحملية"]},
    {"id": "u10", "domain_ar": "التكتونية العامة", "unit_ar": "بنية الكرة الأرضية",
     "keywords": ["بنية الكرة الأرضية", "البرنس", "الوشاح", "القشرة"]},
    {"id": "u11", "domain_ar": "التكتونية العامة", "unit_ar": "البنيات الجيولوجية المرتبطة بالنشاط التكتوني",
     "keywords": ["البنيات الجيولوجية", "التصادم", "الغوص", "دورة ويلسون"]},
]

UNITS_BY_ID = {u["id"]: u for u in UNITS_CATALOG}


def normalize_unit(unit_str: str) -> dict:
    if not unit_str:
        return {"unit_id": "u_unknown", "unit_ar": "", "domain_ar": ""}

    text = unit_str.strip()

    for unit in UNITS_CATALOG:
        for kw in unit["keywords"]:
            if kw in text:
                return {
                    "unit_id": unit["id"],
                    "unit_ar": unit["unit_ar"],
                    "domain_ar": unit["domain_ar"],
                }

    return {"unit_id": "u_unknown", "unit_ar": text[:50], "domain_ar": ""}


def get_units_catalog() -> list[dict]:
    return UNITS_CATALOG
