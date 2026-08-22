#!/usr/bin/env python3
"""Construit le manifeste d'accessibilité/provenance des 35 figures SVT."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs/audit-contenu/iconographie_inventaire.json"
OUTPUT = ROOT / "docs/audit-contenu/iconography-manifest.json"

P1_UNITS = {3, 4, 5, 6, 7, 11}

TITLES_FR = {
    (1, 1): "Transcription",
    (1, 2): "Étapes de la traduction",
    (1, 3): "Polyribosome",
    (2, 1): "Quatre niveaux de structure protéique",
    (2, 2): "Hémoglobine normale et drépanocytaire",
    (2, 3): "Structure du collagène",
    (3, 1): "Clé-serrure et ajustement induit",
    (3, 2): "Influence du pH sur l'activité enzymatique",
    (3, 3): "Influence de la température sur l'activité enzymatique",
    (3, 4): "Étapes de l'action enzymatique",
    (4, 1): "Réponse immunitaire spécifique",
    (4, 2): "Cycle du VIH dans un lymphocyte T auxiliaire",
    (4, 3): "Mécanisme d'action du lymphocyte T cytotoxique",
    (5, 1): "Potentiel d'action",
    (5, 2): "Synapse chimique",
    (5, 3): "Intégration nerveuse",
    (6, 1): "Ultrastructure du chloroplaste",
    (6, 2): "Schéma Z de la phase photochimique",
    (6, 3): "Cycle de Calvin",
    (7, 1): "Ultrastructure de la mitochondrie",
    (7, 2): "Glycolyse",
    (7, 3): "Cycle de Krebs",
    (7, 4): "Phosphorylation oxydative",
    (8, 1): "Vue d'ensemble des transformations énergétiques cellulaires",
    (8, 2): "Comparaison énergétique des cellules végétale et animale",
    (8, 3): "Pyramide énergétique (enrichissement)",
    (9, 1): "Carte schématique des plaques tectoniques",
    (9, 2): "Trois types de limites de plaques",
    (9, 3): "Convection mantellique",
    (10, 1): "Sismogramme et arrivées P, S, L",
    (10, 2): "Zones d'ombre sismiques",
    (10, 3): "Structure interne de la Terre",
    (11, 1): "Structure de la plaque océanique à la dorsale",
    (11, 2): "Séquence ophiolitique",
    (11, 3): "Cycle de Wilson",
}

LABELS = {
    (1, 1): (["النواة", "ADN", "ARN بوليميراز", "ARNm", "المسام النووية", "الريبوزوم"], ["Noyau", "ADN", "ARN polymérase", "ARNm", "Pore nucléaire", "Ribosome"]),
    (1, 2): (["البداية", "الاستطالة", "النهاية", "ARNm", "ARNt", "الريبوزوم", "السلسلة الببتيدية"], ["Initiation", "Élongation", "Terminaison", "ARNm", "ARNt", "Ribosome", "Chaîne peptidique"]),
    (1, 3): (["ARNm", "الريبوزومات", "السلاسل الببتيدية", "اتجاه القراءة"], ["ARNm", "Ribosomes", "Chaînes peptidiques", "Sens de lecture"]),
    (2, 1): (["البنية الأولية", "البنية الثانوية", "البنية الثالثية", "البنية الرابعية"], ["Structure primaire", "Structure secondaire", "Structure tertiaire", "Structure quaternaire"]),
    (2, 2): (["كرية حمراء طبيعية", "كرية منجلية", "HbA", "HbS", "Glu", "Val", "الليف البروتيني"], ["Hématie normale", "Hématie falciforme", "HbA", "HbS", "Glu", "Val", "Fibre protéique"]),
    (2, 3): (["ثلاث سلاسل ببتيدية", "حلزون ثلاثي", "Gly", "Pro", "Hyp", "لييف كولاجيني"], ["Trois chaînes peptidiques", "Triple hélice", "Gly", "Pro", "Hyp", "Fibrille de collagène"]),
    (3, 1): (["الإنزيم", "الموقع الفعال", "الركيزة", "معقد ES", "التلاؤم المحفز"], ["Enzyme", "Site actif", "Substrat", "Complexe ES", "Ajustement induit"]),
    (3, 2): (["سرعة التفاعل", "pH", "بيبسين", "أميلاز", "تريبسين", "pH أمثل"], ["Vitesse", "pH", "Pepsine", "Amylase", "Trypsine", "pH optimal"]),
    (3, 3): (["سرعة التفاعل", "درجة الحرارة", "درجة مثلى", "التصادمات", "التمسخ"], ["Vitesse", "Température", "Température optimale", "Collisions", "Dénaturation"]),
    (3, 4): (["الإنزيم", "الركيزة", "معقد ES", "النواتج"], ["Enzyme", "Substrat", "Complexe ES", "Produits"]),
    (4, 1): (["المستضد", "البلعمية", "LTh", "LB", "الخلايا البلازمية", "الأجسام المضادة", "LTc", "خلايا الذاكرة"], ["Antigène", "Phagocyte", "LTh", "LB", "Plasmocytes", "Anticorps", "LTc", "Cellules mémoire"]),
    (4, 2): (["VIH", "LTh / CD4", "الارتباط", "الاندماج", "النسخ العكسي", "الإدماج", "التكاثر", "التبرعم"], ["VIH", "LTh / CD4", "Fixation", "Fusion", "Transcription inverse", "Intégration", "Réplication", "Bourgeonnement"]),
    (4, 3): (["LTc", "الخلية الهدف", "البيرفورين", "الغرانزيم", "الاستماتة"], ["LTc", "Cellule cible", "Perforine", "Granzyme", "Apoptose"]),
    (5, 1): (["كمون الراحة", "زوال الاستقطاب", "إعادة الاستقطاب", "فرط الاستقطاب", "mV", "الزمن"], ["Potentiel de repos", "Dépolarisation", "Repolarisation", "Hyperpolarisation", "mV", "Temps"]),
    (5, 2): (["النهاية قبل المشبكية", "الحويصلات", "Ca²⁺", "الشق المشبكي", "الناقل العصبي", "المستقبلات"], ["Terminaison présynaptique", "Vésicules", "Ca²⁺", "Fente synaptique", "Neurotransmetteur", "Récepteurs"]),
    (5, 3): (["PPSE", "PPSI", "الجمع", "القطعة الابتدائية", "كمون العمل"], ["PPSE", "PPSI", "Sommation", "Segment initial", "Potentiel d'action"]),
    (6, 1): (["الغشاء الخارجي", "الغشاء الداخلي", "الغرانا", "الثايلاكويد", "الصفائح بين الحبيبية", "الحشوة"], ["Membrane externe", "Membrane interne", "Grana", "Thylakoïde", "Lamelles intergranaires", "Stroma"]),
    (6, 2): (["PSII", "PSI", "الضوء", "سلسلة نقل الإلكترونات", "H⁺", "ATP", "NADPH", "O₂"], ["PSII", "PSI", "Lumière", "Chaîne de transport d'électrons", "H⁺", "ATP", "NADPH", "O₂"]),
    (6, 3): (["التثبيت", "CO₂", "RuBP", "RuBisCO", "APG / 3-PGA", "G3P", "ATP", "NADPH"], ["Fixation", "CO₂", "RuBP", "RuBisCO", "APG / 3-PGA", "G3P", "ATP", "NADPH"]),
    (7, 1): (["الغشاء الخارجي", "الغشاء الداخلي", "الحيز بين الغشائين", "الأعراف", "المطرس", "ATP synthase"], ["Membrane externe", "Membrane interne", "Espace intermembranaire", "Crêtes", "Matrice", "ATP synthase"]),
    (7, 2): (["الغلوكوز", "مرحلة الاستثمار", "مرحلة الإنتاج", "البيروفات", "ATP", "NADH"], ["Glucose", "Phase d'investissement", "Phase de production", "Pyruvate", "ATP", "NADH"]),
    (7, 3): (["Acétyl-CoA", "السترات", "CO₂", "NADH", "FADH₂", "ATP"], ["Acétyl-CoA", "Citrate", "CO₂", "NADH", "FADH₂", "ATP"]),
    (7, 4): (["المطرس", "الحيز بين الغشائين", "المعقدات I–IV", "الإلكترونات", "H⁺", "ATP synthase", "O₂", "H₂O"], ["Matrice", "Espace intermembranaire", "Complexes I–IV", "Électrons", "H⁺", "ATP synthase", "O₂", "H₂O"]),
    (8, 1): (["الضوء", "الصانعة الخضراء", "الغلوكوز", "O₂", "الميتوكندري", "ATP", "CO₂", "H₂O"], ["Lumière", "Chloroplaste", "Glucose", "O₂", "Mitochondrie", "ATP", "CO₂", "H₂O"]),
    (8, 2): (["خلية نباتية", "خلية حيوانية", "الصانعة الخضراء", "الميتوكندري", "التركيب الضوئي", "التنفس"], ["Cellule végétale", "Cellule animale", "Chloroplaste", "Mitochondrie", "Photosynthèse", "Respiration"]),
    (8, 3): (["المنتجون", "المستهلك الأول", "المستهلك الثاني", "المفترس القمّي", "فقدان الطاقة"], ["Producteurs", "Consommateur primaire", "Consommateur secondaire", "Superprédateur", "Perte d'énergie"]),
    (9, 1): (["الصفائح الكبرى", "حدود تباعدية", "حدود تقاربية", "حدود تحويلية", "البراكين"], ["Plaques majeures", "Limites divergentes", "Limites convergentes", "Limites transformantes", "Volcans"]),
    (9, 2): (["التباعد", "الظهرة", "الغوص", "الخندق", "القوس البركاني", "الفالق التحويلي"], ["Divergence", "Dorsale", "Subduction", "Fosse", "Arc volcanique", "Faille transformante"]),
    (9, 3): (["الغلاف الصخري", "البرنس", "تيار صاعد ساخن", "تيار هابط بارد", "الظهرة", "الغوص"], ["Lithosphère", "Manteau", "Courant chaud ascendant", "Courant froid descendant", "Dorsale", "Subduction"]),
    (10, 1): (["السعة", "الزمن", "موجات P", "موجات S", "موجات L", "فرق الوصول P–S"], ["Amplitude", "Temps", "Ondes P", "Ondes S", "Ondes L", "Écart d'arrivée P–S"]),
    (10, 2): (["البؤرة", "موجات P", "موجات S", "النواة الخارجية السائلة", "منطقة الظل", "103°", "143°"], ["Foyer", "Ondes P", "Ondes S", "Noyau externe liquide", "Zone d'ombre", "103°", "143°"]),
    (10, 3): (["القشرة", "الغلاف الصخري", "الأستينوسفير", "البرنس", "النواة الخارجية", "النواة الداخلية", "Fe–Ni"], ["Croûte", "Lithosphère", "Asthénosphère", "Manteau", "Noyau externe", "Noyau interne", "Fe–Ni"]),
    (11, 1): (["الرواسب", "البازلت الوسائدي", "عروق الدوليريت", "الغابرو", "البيريدوتيت", "الصهارة", "التباعد"], ["Sédiments", "Basaltes en coussins", "Filons de dolérite", "Gabbro", "Péridotite", "Magma", "Divergence"]),
    (11, 2): (["اللوح المحيطي", "الأوفيوليت", "البازلت الوسائدي", "الدوليريت", "الغابرو", "البيريدوتيت"], ["Plaque océanique", "Ophiolite", "Basaltes en coussins", "Dolérite", "Gabbro", "Péridotite"]),
    (11, 3): (["التصدع", "محيط فتي", "محيط ناضج", "الغوص", "انغلاق المحيط", "التصادم"], ["Rifting", "Océan jeune", "Océan mature", "Subduction", "Fermeture océanique", "Collision"]),
}

P2_FILES = {
    (1, 1): "u1-fig1-transcription-proposition.png",
    (1, 2): "u1-fig2-translation-stages-proposition.png",
    (1, 3): "u1-fig3-polyribosome-proposition.png",
    (2, 1): "u2-fig1-protein-structure-levels-proposition.png",
    (2, 2): "u2-fig2-hemoglobin-sickle-proposition.png",
    (2, 3): "u2-fig3-collagen-proposition.png",
    (8, 1): "u8-fig1-cellular-energy-overview-proposition.png",
    (8, 2): "u8-fig2-plant-animal-cell-energy-proposition.png",
    (8, 3): "u8-fig3-energy-pyramid-proposition.png",
    (9, 1): "u9-fig1-tectonic-plates-map-proposition.png",
    (9, 2): "u9-fig2-plate-boundaries-proposition.png",
    (9, 3): "u9-fig3-mantle-convection-proposition.png",
    (10, 1): "u10-fig1-seismogram-proposition.png",
    (10, 2): "u10-fig2-seismic-shadow-zones-proposition.png",
    (10, 3): "u10-fig3-earth-interior-proposition.png",
}

P1_FILES = {
    (3, 1): "u3-fig1-clef-serrure-proposition.png",
    (3, 2): "u3-fig2-ph-curves-proposition.png",
    (3, 3): "u3-fig3-temp-curve-proposition.png",
    (3, 4): "u3-fig4-enzyme-stages-proposition.png",
    (4, 1): "u4-fig1-immune-response-proposition.png",
    (4, 2): "u4-fig2-vih-cycle-proposition.png",
    (4, 3): "u4-fig3-ltc-mechanism-proposition.png",
    (5, 1): "u5-fig1-action-potential-proposition.png",
    (5, 2): "u5-fig2-synapse-proposition.png",
    (5, 3): "u5-fig3-neural-integration-proposition.png",
    (6, 1): "u6-fig1-chloroplast-proposition.png",
    (6, 2): "u6-fig2-z-scheme-proposition.png",
    (6, 3): "u6-fig3-calvin-proposition.png",
    (7, 1): "u7-fig1-mitochondrion-proposition.png",
    (7, 2): "u7-fig2-glycolysis-proposition.png",
    (7, 3): "u7-fig3-krebs-proposition.png",
    (7, 4): "u7-fig4-oxidative-phosphorylation-proposition.png",
    (11, 1): "u11-fig1-ridges-proposition.png",
    (11, 2): "u11-fig2-ophiolite-proposition.png",
    (11, 3): "u11-fig3-wilson-cycle-proposition.png",
}

P2_REVIEW_NOTES = {
    (1, 1): "Vérifier le brin matrice, le sens 3′→5′ de lecture et la synthèse 5′→3′ de l'ARNm.",
    (1, 2): "Remplacer tous les labels anglais; vérifier les sites A/P/E et le facteur de terminaison.",
    (1, 3): "Vérifier que la longueur des chaînes augmente dans le sens de lecture de l'ARNm.",
    (2, 1): "Vérifier l'hélice alpha, le feuillet bêta et l'assemblage quaternaire; ajouter les liaisons pertinentes.",
    (2, 2): "Remplacer les labels anglais; expliciter β6 Glu→Val sans suggérer une mutation de plusieurs résidus.",
    (2, 3): "Vérifier la triple hélice, Gly tous les trois résidus et le passage vers la fibrille.",
    (8, 1): "Remplacer les labels anglais et contrôler le sens de chaque flux CO₂/O₂/glucose/H₂O.",
    (8, 2): "Éviter le doublon avec U8-F1; vérifier l'absence de chloroplaste dans la cellule animale.",
    (8, 3): "ENRICHISSEMENT hors socle 55 chapitres: ne pas publier dans le parcours Bac sans décision pédagogique.",
    (9, 1): "Carte schématique à confronter à une carte de référence; contrôler toutes les limites et directions.",
    (9, 2): "Remplacer tous les labels anglais; vérifier le plan de Benioff et la géométrie de la faille transformante.",
    (9, 3): "Contrôler que le manteau est présenté comme solide déformable et non comme liquide; revoir les callouts.",
    (10, 1): "Contrôler l'ordre P–S–L, les amplitudes et l'intervalle P–S; ajouter les axes AR/FR.",
    (10, 2): "Vérifier les trajets P/S et les angles 103°/143°; la couleur des rayons ne doit pas inverser P et S.",
    (10, 3): "AMENDEMENT MAJEUR: supprimer les labels anglais/gibberish et corriger la représentation hybride avant toute utilisation.",
}


def png_size(path: Path) -> tuple[int, int]:
    payload = path.read_bytes()
    if payload[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not a PNG: {path}")
    return struct.unpack(">II", payload[16:24])


def main() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    figures = []
    for unit_index, unit in enumerate(inventory, start=1):
        for spec in unit["figures"]:
            key = (unit_index, spec["num"])
            tier = "P1" if unit_index in P1_UNITS else "P2"
            filename = (P1_FILES if tier == "P1" else P2_FILES)[key]
            folder = "figures-pilote-p1" if tier == "P1" else "figures-pilote-p2"
            relative_path = f"docs/audit-contenu/{folder}/{filename}"
            path = ROOT / relative_path
            if not path.exists():
                raise FileNotFoundError(path)
            width, height = png_size(path)
            labels_ar, labels_fr = LABELS[key]
            title_fr = TITLES_FR[key]
            sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
            is_enrichment = key == (8, 3)
            review_note = (
                P2_REVIEW_NOTES[key]
                if tier == "P2"
                else "Appliquer les points de relecture consignés dans figures-pilote-p1/README.md."
            )
            figures.append({
                "id": f"u{unit_index}-fig{spec['num']}",
                "unit": unit_index,
                "figure": spec["num"],
                "tier": tier,
                "titleAr": spec["titre"],
                "titleFr": title_fr,
                "file": relative_path,
                "sha256": sha256,
                "width": width,
                "height": height,
                "aspectRatio": round(width / height, 3),
                "sourceSpec": "docs/audit-contenu/iconographie_inventaire.json",
                "sourceAuthority": "internal_pending_teacher",
                "productionMethod": "AI-generated proposal from internal specification",
                "productionDate": "2026-08-22",
                "isEnrichment": is_enrichment,
                "labelsAr": labels_ar,
                "labelsFr": labels_fr,
                "labelOverlayStatus": "pending_vector_overlay",
                "altAr": f"مقترح رسم علمي يوضح {spec['titre']}. العناصر الأساسية: {'، '.join(labels_ar)}.",
                "altFr": f"Proposition de schéma scientifique illustrant {title_fr}. Éléments clés : {', '.join(labels_fr)}.",
                "accessibility": {
                    "highResolution": width >= 1200 and height >= 700,
                    "mobileReadableCandidate": min(width, height) >= 700,
                    "a4ReadableCandidate": width >= 1200 and height >= 700,
                    "bilingualTextAlternativePresent": True,
                    "visualContrast": "requires_human_check",
                },
                "precheck": {
                    "status": "agent_precheck_only",
                    "note": review_note,
                },
                "humanReview": {
                    "status": "required",
                    "reviewer": None,
                    "reviewedAt": None,
                    "decision": None,
                    "scientificAccuracy": False,
                    "bilingualLabelsApplied": False,
                    "mobilePrintReadability": False,
                },
                "publicationStatus": "blocked_pending_teacher_review",
                "licenseStatus": "internal_proposal_not_cleared_for_publication",
            })

    if len(figures) != 35 or len({item["id"] for item in figures}) != 35:
        raise ValueError("Expected exactly 35 unique figures")

    output = {
        "metadata": {
            "version": "2026-08-22.1",
            "count": 35,
            "p1Count": 20,
            "p2Count": 15,
            "producedProposals": 35,
            "humanValidated": 0,
            "publicationReady": 0,
            "labelOverlayComplete": 0,
            "status": "PROPOSALS_BLOCKED_PENDING_TEACHER_REVIEW",
            "noticeFr": "Production technique complète; aucune figure n'est validée ni publiable sans relecture humaine et surimpression AR/FR.",
            "noticeAr": "اكتمل الإنتاج التقني للمقترحات، لكن لا يوجد أي شكل معتمد أو قابل للنشر قبل المراجعة البشرية وإضافة الملصقات AR/FR.",
        },
        "figures": figures,
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {OUTPUT} ({len(figures)} proposals, 0 human validated)")


if __name__ == "__main__":
    main()
