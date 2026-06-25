"""Mindmaps Methodologiques — Semaine 7
6 mindmaps statiques + generation dynamique par verbe
"""

from typing import Dict, Any, List

STATIC_MINDMAPS = {
    "structure_texte_scientifique": {
        "id": "mm_structure",
        "title": "Structure du Texte Scientifique",
        "root": {
            "id": "root",
            "label": "Texte Scientifique",
            "children": [
                {"id": "intro", "label": "Introduction", "children": [
                    {"id": "intro1", "label": "Poser le probleme"},
                    {"id": "intro2", "label": "Objectif de l exercice"}
                ]},
                {"id": "dev", "label": "Developpement", "children": [
                    {"id": "dev1", "label": "Arguments"},
                    {"id": "dev2", "label": "Exploitation documents"},
                    {"id": "dev3", "label": "Explication scientifique"}
                ]},
                {"id": "conc", "label": "Conclusion", "children": [
                    {"id": "conc1", "label": "Reponse au probleme"},
                    {"id": "conc2", "label": "Synthese"}
                ]}
            ]
        }
    },
    "verbe_wadhah": {
        "id": "mm_wadhah",
        "title": "Comment repondre a 'وضّح في نص علمي'",
        "root": {
            "id": "root",
            "label": "وضّح في نص علمي",
            "children": [
                {"id": "intro", "label": "Introduction"},
                {"id": "dev", "label": "Developpement structure"},
                {"id": "conc", "label": "Conclusion"}
            ]
        }
    },
    "verbe_athbat": {
        "id": "mm_athbat",
        "title": "Comment repondre a 'أثبت'",
        "root": {
            "id": "root",
            "label": "أثبت",
            "children": [
                {"id": "arg", "label": "Arguments clairs"},
                {"id": "doc", "label": "Exploitation documents"},
                {"id": "lien", "label": "Lien preuve > conclusion"}
            ]
        }
    },
    "verbe_barrir": {
        "id": "mm_barrir",
        "title": "Comment repondre a 'برّر'",
        "root": {
            "id": "root",
            "label": "برّر",
            "children": [
                {"id": "justif", "label": "Justification scientifique"},
                {"id": "preuve", "label": "Preuves"},
                {"id": "lien", "label": "Lien avec le contexte"}
            ]
        }
    },
    "verbe_fassar": {
        "id": "mm_fassar",
        "title": "Comment repondre a 'فسر'",
        "root": {
            "id": "root",
            "label": "فسر",
            "children": [
                {"id": "expl", "label": "Explication scientifique"},
                {"id": "donnees", "label": "Lien avec les donnees"},
                {"id": "cause", "label": "Cause > Effet"}
            ]
        }
    },
    "verbe_naqish": {
        "id": "mm_naqish",
        "title": "Comment repondre a 'ناقش'",
        "root": {
            "id": "root",
            "label": "ناقش",
            "children": [
                {"id": "pour", "label": "Arguments pour"},
                {"id": "contre", "label": "Arguments contre"},
                {"id": "position", "label": "Prise de position"}
            ]
        }
    }
}


def get_static_mindmap(mindmap_id: str) -> Dict[str, Any] | None:
    return STATIC_MINDMAPS.get(mindmap_id)


def get_all_static_mindmaps() -> List[Dict[str, Any]]:
    return list(STATIC_MINDMAPS.values())


def generate_dynamic_mindmap(verb: str) -> Dict[str, Any]:
    base = {
        "id": f"dynamic_{verb.replace(' ', '_')}",
        "title": f"Mindmap dynamique - {verb}",
        "generated": True,
        "root": {
            "id": "root",
            "label": verb,
            "children": []
        }
    }

    if "وضّح" in verb or "نص علمي" in verb:
        base["root"]["children"] = [
            {"id": "intro", "label": "Introduction (probleme)"},
            {"id": "dev", "label": "Developpement structure"},
            {"id": "conc", "label": "Conclusion"}
        ]
    elif "أثبت" in verb:
        base["root"]["children"] = [
            {"id": "arg", "label": "Arguments"},
            {"id": "doc", "label": "Documents"},
            {"id": "lien", "label": "Lien preuve > conclusion"}
        ]
    elif "برّر" in verb:
        base["root"]["children"] = [
            {"id": "justif", "label": "Justification"},
            {"id": "preuve", "label": "Preuves scientifiques"}
        ]
    elif "فسر" in verb:
        base["root"]["children"] = [
            {"id": "expl", "label": "Explication"},
            {"id": "donnees", "label": "Donnees du document"}
        ]
    elif "ناقش" in verb:
        base["root"]["children"] = [
            {"id": "pour", "label": "Pour"},
            {"id": "contre", "label": "Contre"},
            {"id": "position", "label": "Position finale"}
        ]
    else:
        base["root"]["children"] = [
            {"id": "structure", "label": "Structure"},
            {"id": "contenu", "label": "Contenu"}
        ]

    return base
