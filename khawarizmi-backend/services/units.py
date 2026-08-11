"""Catalogue canonique du programme SVT 3AS algérien.

Ce module est la source de vérité backend des 3 domaines, 11 unités et
22 phases. Les lecteurs (boussole, drill, normalisation des chapitres) doivent
consommer ce catalogue plutôt que maintenir leurs propres listes.
"""

from __future__ import annotations

DOMAINS = [
    {
        "id": "d1",
        "number": 1,
        "title_ar": "التخصص الوظيفي للبروتينات",
        "title_fr": "Spécialisation fonctionnelle des protéines",
        "color": "blue",
    },
    {
        "id": "d2",
        "number": 2,
        "title_ar": "التحولات الطاقوية",
        "title_fr": "Transformations énergétiques",
        "color": "emerald",
    },
    {
        "id": "d3",
        "number": 3,
        "title_ar": "التكتونية العامة",
        "title_fr": "Tectonique générale",
        "color": "amber",
    },
]
DOMAINS_BY_ID = {domain["id"]: domain for domain in DOMAINS}


PHASES = [
    {"slug": "phase1_chapitres_1_2", "number": 1, "title_ar": "تقديم الوحدة: التساؤل الجوهري حول تركيب البروتين"},
    {"slug": "phase2_chapitres_3_4", "number": 2, "title_ar": "الترجمة: من ARNm إلى سلسلة بيبتيدية"},
    {"slug": "phase3_chapitres_5_6", "number": 3, "title_ar": "العلاقة بين بنية ووظيفة البروتين: فقر الدم المنجلي"},
    {"slug": "phase4_chapitres_7_8", "number": 4, "title_ar": "النشاط الإنزيمي: تأثير pH على فعالية الإنزيم"},
    {"slug": "phase5_chapitres_9_10", "number": 5, "title_ar": "الذات واللاذات: رفض زرع الأعضاء"},
    {"slug": "phase6_chapitres_11_12", "number": 6, "title_ar": "الاستجابة المناعية الخلطية: الأجسام المضادة والمصل"},
    {"slug": "phase7_chapitres_13_14", "number": 7, "title_ar": "الاستجابة المناعية الخلوية: دور اللمفاويات LTc"},
    {"slug": "phase8_chapitres_15_16", "number": 8, "title_ar": "كمون الراحة: استقطاب الغشاء العصبي"},
    {"slug": "phase9_chapitres_17_18", "number": 9, "title_ar": "النقل المشبكي: عبور السيالة العصبية"},
    {"slug": "phase10_chapitres_19_20", "number": 10, "title_ar": "تأثير المخدرات على مستوى المشابك"},
    {"slug": "phase11_chapitres_21_22", "number": 11, "title_ar": "التركيب الضوئي: مصدر الأكسجين المنطلق"},
    {"slug": "phase12_chapitres_23_24", "number": 12, "title_ar": "المرحلة الكيميوحيوية: تثبيت CO₂ (حلقة كالفن)"},
    {"slug": "phase13_chapitres_25_26", "number": 13, "title_ar": "التحلل السكري والتخمر: الطاقة في غياب الأكسجين"},
    {"slug": "phase14_chapitres_27_28", "number": 14, "title_ar": "السلسلة التنفسية والفسفرة التأكسدية"},
    {"slug": "phase15_chapitres_29_30", "number": 15, "title_ar": "إنتاج ATP في الصانعة الخضراء والميتوكندري"},
    {"slug": "phase16_chapitres_31_32", "number": 16, "title_ar": "تحديد الصفائح التكتونية: الزلازل والبراكين"},
    {"slug": "phase17_chapitres_33_34", "number": 17, "title_ar": "حركات الصفائح: توسع قاع المحيط"},
    {"slug": "phase18_chapitres_35_36", "number": 18, "title_ar": "الطاقة الداخلية للكرة الأرضية"},
    {"slug": "phase19_chapitres_37_38", "number": 19, "title_ar": "الموجات الزلزالية والبنية الداخلية للأرض"},
    {"slug": "phase20_chapitres_39_40", "number": 20, "title_ar": "نمذجة البنية الداخلية: النواة الصلبة"},
    {"slug": "phase21_chapitres_41_42", "number": 21, "title_ar": "المغماتية وتشكل اللوح المحيطي"},
    {"slug": "phase22_chapitres_43_44", "number": 22, "title_ar": "التحول والصخور المتحولة في مناطق الغوص"},
]
PHASES_BY_SLUG = {phase["slug"]: phase for phase in PHASES}


def _phases(start: int, end: int) -> list[dict]:
    return [dict(phase) for phase in PHASES if start <= phase["number"] <= end]


UNITS_CATALOG = [
    {
        "id": "u1", "roadmap_id": "d1_u1", "domain_id": "d1", "unit_number": 1,
        "chapter_id": "ch1_proteines", "unit_ar": "تركيب البروتين",
        "unit_fr": "Synthèse des protéines", "emoji": "🧬", "phases": _phases(1, 2),
        "methodology_slug": "d1-u1-c1-composition-chimique-des-proteines",
        "keywords": ["تركيب البروتين", "synthese des proteines", "transcription", "traduction", "gene et proteine"],
    },
    {
        "id": "u2", "roadmap_id": "d1_u2", "domain_id": "d1", "unit_number": 2,
        "chapter_id": "ch_structure_proteines", "unit_ar": "العلاقة بين بنية ووظيفة البروتين",
        "unit_fr": "Relation structure-fonction des protéines", "emoji": "🔬", "phases": _phases(3, 3),
        "methodology_slug": "d1-u2-c1-structure-spatiale-des-proteines",
        "keywords": ["بنية ووظيفة البروتين", "وظيفة البروتين", "structure et fonction", "structure spatiale", "hemoglobine", "collagene"],
    },
    {
        "id": "u3", "roadmap_id": "d1_u3", "domain_id": "d1", "unit_number": 3,
        "chapter_id": "ch2_enzymes", "unit_ar": "النشاط الإنزيمي للبروتينات",
        "unit_fr": "Activité enzymatique des protéines", "emoji": "⚗️", "phases": _phases(4, 4),
        "methodology_slug": "d1-u3-c1-proprietes-des-enzymes",
        "keywords": ["النشاط الإنزيمي", "activite enzymatique", "enzyme", "enzymatique", "site actif", "substrat"],
    },
    {
        "id": "u4", "roadmap_id": "d1_u4", "domain_id": "d1", "unit_number": 4,
        "chapter_id": "ch3_immunite", "unit_ar": "دور البروتينات في الدفاع عن الذات",
        "unit_fr": "Rôle des protéines dans la défense de soi", "emoji": "🛡️", "phases": _phases(5, 7),
        "methodology_slug": "d1-u4-c1-reponse-immunitaire-humorale",
        "keywords": ["الدفاع عن الذات", "المناعة", "defense de soi", "immunite", "anticorps", "lymphocyte", "sida"],
    },
    {
        "id": "u5", "roadmap_id": "d1_u5", "domain_id": "d1", "unit_number": 5,
        "chapter_id": "ch4_nerveux", "unit_ar": "دور البروتينات في الاتصال العصبي",
        "unit_fr": "Rôle des protéines dans la communication nerveuse", "emoji": "🧠", "phases": _phases(8, 10),
        "methodology_slug": "d1-u5-c1-structure-du-tissu-nerveux",
        "keywords": ["الاتصال العصبي", "communication nerveuse", "nerveux", "neurone", "potentiel", "synap", "drogues"],
    },
    {
        "id": "u6", "roadmap_id": "d2_u1", "domain_id": "d2", "unit_number": 1,
        "chapter_id": "ch_photosynthese", "unit_ar": "آليات تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة",
        "unit_fr": "Conversion de l'énergie lumineuse en énergie chimique", "emoji": "🌿", "phases": _phases(11, 12),
        "methodology_slug": "d2-u1-c1-structure-du-chloroplaste",
        "keywords": ["التركيب الضوئي", "الطاقة الضوئية", "photosynthese", "chloroplaste", "chlorophylle", "calvin", "phase claire", "phase sombre"],
    },
    {
        "id": "u7", "roadmap_id": "d2_u2", "domain_id": "d2", "unit_number": 2,
        "chapter_id": "ch_respiration", "unit_ar": "تحويل الطاقة الكيميائية الكامنة في الجزيئات العضوية إلى ATP",
        "unit_fr": "Respiration cellulaire et fermentation", "emoji": "⚡", "phases": _phases(13, 14),
        "methodology_slug": "d2-u2-c1-respiration-cellulaire-concept-general",
        "keywords": ["التنفس الخلوي", "التخمر", "respiration cellulaire", "fermentation", "glycolyse", "krebs", "phosphorylation oxydative"],
    },
    {
        "id": "u8", "roadmap_id": "d2_u3", "domain_id": "d2", "unit_number": 3,
        "chapter_id": "ch_bilan_energetique", "unit_ar": "تحويل الطاقة على المستوى ما فوق البنية الخلوية",
        "unit_fr": "Bilan énergétique au niveau cellulaire", "emoji": "🔋", "phases": _phases(15, 15),
        "methodology_slug": "d2-u3-c1-echanges-gazeux-pulmonaires",
        "keywords": ["الحصيلة الطاقوية", "bilan energetique", "niveau ultrastructural", "التكامل الوظيفي", "integration fonctionnelle", "echanges gazeux"],
    },
    {
        "id": "u9", "roadmap_id": "d3_u1", "domain_id": "d3", "unit_number": 1,
        "chapter_id": "ch_tectonique_plaques", "unit_ar": "النشاط التكتوني للصفائح",
        "unit_fr": "Activité tectonique des plaques", "emoji": "🌋", "phases": _phases(16, 18),
        "methodology_slug": "d3-u1-c1-structure-de-la-lithosphere",
        "keywords": ["النشاط التكتوني للصفائح", "plaques tectoniques", "tectonique des plaques", "mouvements des plaques", "identification des plaques"],
    },
    {
        "id": "u10", "roadmap_id": "d3_u2", "domain_id": "d3", "unit_number": 2,
        "chapter_id": "ch_structure_terre", "unit_ar": "بنية الكرة الأرضية",
        "unit_fr": "Structure du globe terrestre", "emoji": "🌍", "phases": _phases(19, 20),
        "methodology_slug": "d3-u2-c1-ondes-sismiques-et-structure-de-la-terre",
        "keywords": ["بنية الكرة الأرضية", "الكرة الأرضية", "structure du globe", "ondes sismiques", "structure interne", "croute terrestre", "manteau"],
    },
    {
        "id": "u11", "roadmap_id": "d3_u3", "domain_id": "d3", "unit_number": 3,
        "chapter_id": "ch_structures_geologiques", "unit_ar": "النشاط التكتوني والبنيات الجيولوجية المرتبطة به",
        "unit_fr": "Structures géologiques associées à la tectonique", "emoji": "🏔️", "phases": _phases(21, 22),
        "methodology_slug": "d3-u3-c1-expansion-oceanique-et-magnetisme",
        "keywords": ["البنيات الجيولوجية", "structures geologiques", "subduction", "collision", "ophiolite", "dorsale", "plaque oceanique", "magmatisme", "roches metamorphiques"],
    },
]

for unit in UNITS_CATALOG:
    domain = DOMAINS_BY_ID[unit["domain_id"]]
    unit["domain_number"] = domain["number"]
    unit["domain_ar"] = domain["title_ar"]
    unit["domain_fr"] = domain["title_fr"]

UNITS_BY_ID = {unit["id"]: unit for unit in UNITS_CATALOG}
UNITS_BY_ROADMAP_ID = {unit["roadmap_id"]: unit for unit in UNITS_CATALOG}
UNITS_BY_CHAPTER = {unit["chapter_id"]: unit for unit in UNITS_CATALOG}


def normalize_unit(unit_str: str | None) -> dict:
    """Retourne l'unité canonique reconnue, sans inventer pour l'ambigu."""
    if not unit_str:
        return {"unit_id": "u_unknown", "unit_ar": "", "domain_ar": ""}

    from services.chapter_identity import fold_identity, normalize_chapter_id

    chapter_id = normalize_chapter_id(unit_str)
    if chapter_id and chapter_id in UNITS_BY_CHAPTER:
        unit = UNITS_BY_CHAPTER[chapter_id]
        return {"unit_id": unit["id"], "unit_ar": unit["unit_ar"], "domain_ar": unit["domain_ar"]}

    text = fold_identity(unit_str)
    for unit in UNITS_CATALOG:
        if any(fold_identity(keyword) in text for keyword in unit["keywords"]):
            return {"unit_id": unit["id"], "unit_ar": unit["unit_ar"], "domain_ar": unit["domain_ar"]}

    return {"unit_id": "u_unknown", "unit_ar": str(unit_str)[:50], "domain_ar": ""}


def get_units_catalog() -> list[dict]:
    return UNITS_CATALOG
