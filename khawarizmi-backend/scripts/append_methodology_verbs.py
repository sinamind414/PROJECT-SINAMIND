# -*- coding: utf-8 -*-
"""
append_methodology_verbs.py
───────────────────────────
Injecte les 14 verbes d'action méthodologiques ONEC
dans lexique_svt_terminale_complet.json.

Usage:
    cd khawarizmi-backend
    python scripts/append_methodology_verbs.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
LEXIQUE_PATH = ROOT / "data" / "lexique_svt_terminale_complet.json"
SEED_FILES = [
    ROOT / "data" / "action_verbs_seed.json",
    ROOT / "data" / "action_verbs_seed2.json",
    ROOT / "data" / "action_verbs_seed3.json",
]

# ── 14 verbes ONEC (arabe / français / slug / définition) ───────────
# Source: Programme officiel ONEC — الأفعال الأدائية المنهجية
METHODOLOGY_VERBS = [
    {
        "slug": "analyse",
        "terme_fr": "Analyser",
        "terme_ar": "حلّل",
        "definition_fr": "Décomposer les données d'un document pour en décrire les tendances, valeurs et relations, sans interpréter ni expliquer.",
        "definition_ar": "تفكيك معطيات الوثيقة لوصف الاتجاهات والقيم والعلاقات فيها، دون تفسير أو شرح.",
        "tags": ["methode", "analyse", "document", "onec"],
    },
    {
        "slug": "interpret",
        "terme_fr": "Interpréter / Expliquer",
        "terme_ar": "فسّر",
        "definition_fr": "Répondre au pourquoi ou au comment en établissant une relation de cause à effet entre les données et les connaissances scientifiques.",
        "definition_ar": "الإجابة عن لماذا أو كيف بإيجاد علاقة سببية بين المعطيات والمكتسبات العلمية.",
        "tags": ["methode", "interpretation", "onec"],
    },
    {
        "slug": "deduce",
        "terme_fr": "Déduire",
        "terme_ar": "استنتج",
        "definition_fr": "Tirer une conclusion concise à partir de l'analyse ou de l'interprétation, sans ajouter d'informations nouvelles.",
        "definition_ar": "استخلاص نتيجة مختصرة من التحليل أو التفسير دون إضافة معلومات جديدة.",
        "tags": ["methode", "deduction", "onec"],
    },
    {
        "slug": "justify",
        "terme_fr": "Justifier / Argumenter",
        "terme_ar": "علّل / برّر",
        "definition_fr": "Appuyer une affirmation par un argument tiré du document et confirmé par une connaissance scientifique préalable.",
        "definition_ar": "تمسك بحجة مستخرجة من الوثيقة ومدعومة بمعرفة علمية سابقة.",
        "tags": ["methode", "argumentation", "onec"],
    },
    {
        "slug": "hypothesis",
        "terme_fr": "Proposer une hypothèse",
        "terme_ar": "اقترح فرضية",
        "definition_fr": "Formuler une explication provisoire et testable reliant une cause possible à un effet observé.",
        "definition_ar": "صياغة تفسير مؤقت وقابل للاختبار يربط سبباً محتملاً بنتيجة ملاحظة.",
        "tags": ["methode", "hypothese", "onec"],
    },
    {
        "slug": "define",
        "terme_fr": "Définir",
        "terme_ar": "عرّف",
        "definition_fr": "Donner les limites précises d'un terme scientifique : propriétés, caractéristiques, rôle.",
        "definition_ar": "إعطاء الحدود الدقيقة للمصطلح العلمي: الخصائص والسمات والدور.",
        "tags": ["methode", "definition", "onec"],
    },
    {
        "slug": "name",
        "terme_fr": "Nommer / Identifier",
        "terme_ar": "سمّى / تعرّف",
        "definition_fr": "Reconnaître et désigner un élément par son nom exact : donnée, structure, organe, concept.",
        "definition_ar": "التعرف على عنصر وتحديده بالاسم الدقيق: بيانات، بنية، عضو، مفهوم.",
        "tags": ["methode", "identification", "onec"],
    },
    {
        "slug": "cite",
        "terme_fr": "Citer / Énumérer",
        "terme_ar": "اذكر",
        "definition_fr": "Lister brièvement les éléments en utilisant un minimum de mots.",
        "definition_ar": "سرد العناصر بإيجاز مع الحد الأدنى من الكلمات.",
        "tags": ["methode", "enumeration", "onec"],
    },
    {
        "slug": "validate-hypothesis",
        "terme_fr": "Valider une hypothèse",
        "terme_ar": "تحقق من صحة الفرضية / صادق على فرضية",
        "definition_fr": "Parcours complet : analyse, interprétation partielle, conclusion partielle, synthèse, puis confirmation ou réfutation de la hypothèse.",
        "definition_ar": "مسار كامل: تحليل، تفسير جزئي، استنتاج جزئي، تركيب، ثم تأكيد أو نفي الفرضية.",
        "tags": ["methode", "hypothese", "verification", "onec"],
    },
    {
        "slug": "discuss",
        "terme_fr": "Discuter",
        "terme_ar": "ناقش",
        "definition_fr": "Tâche complexe combinant analyse de documents, interprétation et mise en regard d'arguments pour et contre.",
        "definition_ar": "مهمة مركبة تجمع بين تحليل الوثائق والتفسير ومقارنة الحجج المؤيدة والمعارضة.",
        "tags": ["methode", "discussion", "onec"],
    },
    {
        "slug": "scientific-text",
        "terme_fr": "Composer un texte scientifique",
        "terme_ar": "اكتب نصاً علمياً",
        "definition_fr": "Rédiger un texte structuré avec introduction, problématique, développement organisé et conclusion.",
        "definition_ar": "كتابة نص منظم يتضمن مقدمة وإشكالية وعرض مترتب وخاتمة.",
        "tags": ["methode", "redaction", "onec"],
    },
    {
        "slug": "compare",
        "terme_fr": "Comparer",
        "terme_ar": "قارن",
        "definition_fr": "Mettre deux éléments sous un critère unique pour mettre en évidence différences et similitudes.",
        "definition_ar": "وضع عنصرین تحت معيار واحد لإبراز الاختلافات والتشابهات.",
        "tags": ["methode", "comparaison", "document", "onec"],
    },
    {
        "slug": "relationship",
        "terme_fr": "Déterminer la relation",
        "terme_ar": "حدد العلاقة",
        "definition_fr": "Établir la liaison entre deux variables en formulant une phrase du type « chaque fois que… alors… ».",
        "definition_ar": "إيجاد الربط بين متغيرين بصياغة جملة من نوع « كلما… فإن… ».",
        "tags": ["methode", "relation", "document", "onec"],
    },
    {
        "slug": "describe",
        "terme_fr": "Décrire",
        "terme_ar": "صِف",
        "definition_fr": "Exposer de manière détaillée les caractéristiques d'un phénomène, d'une structure ou d'une expérience en se basant sur les observations directes.",
        "definition_ar": "عرض تفصيلي لخصائص ظاهرة أو بنية أو تجربة استناداً إلى الملاحظات المباشرة.",
        "tags": ["methode", "description", "onec"],
    },
]

DOMAIN_ID = "domaine-methode"
CATEGORY_ID = "cat-methode-1"
CAT_NOM_FR = "Verbes d'action méthodologiques (ONEC)"
CAT_NOM_AR = "الأفعال الأدائية المنهجية (الONEC)"


def load_seed_verbs():
    """Charge les métadonnées complètes depuis les fichiers seed."""
    seed_map = {}
    for f in SEED_FILES:
        if not f.exists():
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        for v in data:
            seed_map[v["slug"]] = v
    return seed_map


def find_next_term_id(lexique: dict) -> int:
    """Trouve le prochain ID disponible."""
    max_n = 0
    for dom in lexique["domaines"]:
        for cat in dom["categories"]:
            for t in cat["termes"]:
                n = int(t["id"].split("-")[1])
                if n > max_n:
                    max_n = n
    return max_n + 1


def build_term(slug: str, verb: dict, seed: dict | None, next_id: int) -> dict:
    """Construit un terme lexique à partir des données verb + seed."""
    term = {
        "id": f"term-{next_id:03d}",
        "terme_fr": verb["terme_fr"],
        "terme_ar": verb["terme_ar"],
        "abreviation": None,
        "type": "methode",
        "definition_fr": verb["definition_fr"],
        "definition_ar": verb["definition_ar"],
        "synonymes_fr": [],
        "synonymes_ar": [],
        "importance": "haute",
        "bac_frequent": True,
        "chapitre_principal": "Méthodologie ONEC",
        "micro_concept_id": "methode_onec",
        "exemples_contexte": [],
        "termes_lies": [],
        "tags": verb["tags"],
    }

    # Enrichir avec les données seed si disponibles
    if seed:
        term["exemples_contexte"] = [
            seed.get("good_example", {}).get("answerAr", "")
        ] if seed.get("good_example") else []
        term["definition_ar"] = seed.get("definition_ar", verb["definition_ar"])

    return term


def main():
    if not LEXIQUE_PATH.exists():
        print(f"ERREUR: {LEXIQUE_PATH} introuvable")
        sys.exit(1)

    lexique = json.loads(LEXIQUE_PATH.read_text(encoding="utf-8"))

    # Vérifier si la catégorie existe déjà
    for dom in lexique["domaines"]:
        for cat in dom["categories"]:
            if cat["id"] == CATEGORY_ID:
                print(f"La catégorie '{CAT_NOM_FR}' existe déjà ({len(cat['termes'])} termes). Skip.")
                return

    # Charger les seeds pour enrichissement
    seed_map = load_seed_verbs()
    next_id = find_next_term_id(lexique)

    # Construire les termes
    terms = []
    for i, verb in enumerate(METHODOLOGY_VERBS):
        slug = verb["slug"]
        seed = seed_map.get(slug)
        term = build_term(slug, verb, seed, next_id + i)
        terms.append(term)

    # Créer la catégorie
    category = {
        "id": CATEGORY_ID,
        "nom_fr": CAT_NOM_FR,
        "nom_ar": CAT_NOM_AR,
        "termes": terms,
    }

    # Créer le domaine
    domain = {
        "id": DOMAIN_ID,
        "nom_fr": "Méthodologie scientifique",
        "nom_ar": "المنهجية العلمية",
        "categories": [category],
    }

    lexique["domaines"].append(domain)
    lexique["metadata"]["total_entrees"] = sum(
        len(cat["termes"])
        for dom in lexique["domaines"]
        for cat in dom["categories"]
    )

    # Sauvegarder
    LEXIQUE_PATH.write_text(
        json.dumps(lexique, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"[OK] {len(terms)} verbes ONEC injectés dans {LEXIQUE_PATH.name}")
    print(f"     Nouveau total: {lexique['metadata']['total_entrees']} termes")
    print(f"     Domaine ajouté: {domain['nom_fr']} / {domain['nom_ar']}")
    for i, t in enumerate(terms, 1):
        print(f"     [{i:02d}] {t['terme_ar']} — {t['terme_fr']}")


if __name__ == "__main__":
    main()
