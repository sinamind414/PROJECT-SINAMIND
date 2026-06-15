# Prompt pour Claude — Structuration du Lexique SVT Terminale (Algérie)

## Contexte Projet

Plateforme **IA Khawarizmi Pro** — assistant IA pour lycéens algériens préparant le Bac Sciences Naturelles.
Stack : FastAPI/Python 3.12, PostgreSQL 16 + pgvector, Redis 7, Gemini 2.5 Flash, JWT, FSRS, Docker/Railway.

## Objectif

Générer un **lexique bilingue français-arabe** complet pour le programme SVT Terminale Sciences Expérimentales (Algérie), structuré en JSON selon le schéma défini ci-dessous, couvrant **les 3 domaines et 11 chapitres** du programme officiel ONEC.

---

## Schéma JSON du lexique (à respecter strictement)

```json
{
  "metadata": {
    "matiere": "SVT",
    "niveau": "Terminale",
    "filiere": "Sciences Expérimentales",
    "source": "Programme officiel ONEC Algérie",
    "version": "1.0",
    "langue_source": "français",
    "langues_cibles": ["arabe"]
  },
  "domaines": [
    {
      "id": "domaine-1",
      "nom_fr": "...",
      "nom_ar": "...",
      "categories": [
        {
          "id": "cat-1-1",
          "nom_fr": "...",
          "nom_ar": "...",
          "termes": [
            {
              "id": "term-XXX",
              "terme_fr": "...",
              "terme_ar": "...",
              "abreviation": "..." ou null,
              "type": "molecule|enzyme|concept|processus|cellule|organite|structure|mecanisme",
              "definition_fr": "...",
              "definition_ar": "...",
              "synonymes_fr": ["..."],
              "synonymes_ar": ["..."],
              "importance": "critique|haute|moyenne",
              "bac_frequent": true|false,
              "chapitre_principal": "Nom du chapitre",
              "micro_concept_id": "ch1_proteines|ch_structure|ch2_enzymes|ch3_immunite|ch_nerveux|...",
              "exemples_contexte": ["..."],
              "termes_lies": ["term-XXX", "term-YYY"],
              "tags": ["mot-cle1", "mot-cle2"]
            }
          ]
        }
      ]
    }
  ],
  "liens_transversaux": [
    {
      "source": "term-XXX",
      "target": "term-YYY",
      "relation": "description courte",
      "type": "causal|dependance|opposition|inclusion"
    }
  ]
}
```

---

## Structure du Programme (3 Domaines, 11 Chapitres)

### Domaine 1 : Spécialisation fonctionnelle des protéines / التخصص الوظيفي للبروتينات

| Catégorie | ID Chapitre | Nom FR | Nom AR | Concepts Clés |
|-----------|-------------|--------|--------|---------------|
| Génétique moléculaire | `ch1_proteines` | Synthèse des protéines | تركيب البروتين | الاستنساخ, الترجمة, الشفرة الوراثية, بنية البروتين |
| Structure des protéines | `ch_structure` | Structure-fonction des protéines | العلاقة بين بنية ووظيفة البروتين | الأحماض الأمينية, السلوك الأمفوتيري, الروابط الكيميائية, البنية الفراغية |
| Enzymologie | `ch2_enzymes` | Activité enzymatique | النشاط الإنزيمي للبروتينات | التحفيز الإنزيمي, الموقع الفعال, السرعة الابتدائية, تأثير الحرارة والـ pH |
| Immunologie | `ch3_immunite` | Immunologie (rôle des protéines dans la défense) | دور البروتينات في الدفاع عن الذات | المناعة الخلطية, المناعة الخلوية, المعقد المناعي, التعرف المزدوج |
| Neurobiologie | `ch_nerveux` | Communication nerveuse | دور البروتينات في الاتصال العصبي | كمون الراحة, كمون العمل, المشبك, المبلغ العصبي |

### Domaine 2 : Transformations énergétiques / التحولات الطاقوية

| Catégorie | Nom FR | Nom AR |
|-----------|--------|--------|
| Photosynthèse | Photosynthèse | آليات تحويل الطاقة الضوئية إلى طاقة كيميائية |
| Respiration cellulaire | Respiration cellulaire | آليات تحويل الطاقة الكيميائية في الجزيئات العضوية إلى ATP |
| Fermentation | Énergie cellulaire (Fermentation) | التخمر |

### Domaine 3 : Tectonique globale / التكتونية العامة

| Catégorie | Nom FR | Nom AR |
|-----------|--------|--------|
| Plaques tectoniques | Tectonique des plaques | النشاط التكتوني للصفائح |
| Structure interne | Structure du globe | بنية الكرة الأرضية |
| Magmatisme | Magmatisme | النشاط التكتوني والبنيات المرتبطة به |

---

## Règles de génération

1. **Minimum 100 termes** par domaine (300+ termes au total)
2. Termes **critiques** (bac_frequent=true) : définitions précises, 2 exemples contexte
3. Termes **importants** (importance=haute) : 1-2 exemples contexte
4. Termes **moyens** : définition seule suffit
5. Chaque terme doit avoir un `type` valide parmi les types listés
6. `micro_concept_id` doit correspondre exactement aux IDs du programme (ch1_proteines, ch_structure, ch2_enzymes, ch3_immunite, ch_nerveux, etc.)
7. Liens transversaux entre domaines (ex: ATP synthase ↔ Phosphorylation oxydative)
8. Max 5 mots par label, 3 niveaux de profondeur max
9. **Encodage UTF-8** — caractères arabes préservés
10. **Indentation 2 espaces**, pas de commentaires dans le JSON

## Types valides pour chaque terme

| Type | Description | Exemple |
|------|-------------|---------|
| `molecule` | Molécule biologique | ADN, ARNm, ATP |
| `enzyme` | Enzyme | ARN polymérase, ATP synthase |
| `concept` | Concept théorique | Code génétique, Site actif, Subduction |
| `processus` | Processus biologique/géologique | Cycle de Calvin, Glycolyse, Subduction |
| `cellule` | Type cellulaire | Lymphocyte T, CPA |
| `organite` | Organite cellulaire | Mitochondrie, Chloroplaste |
| `structure` | Structure anatomique/géologique | Lithosphère, Dorsale océanique |
| `mecanisme` | Mécanisme | Phosphorylation oxydative, Chimiosmose |

## Exemple de terme bien formé

```json
{
  "id": "term-001",
  "terme_fr": "ADN",
  "terme_ar": "الحمض النووي ADN",
  "abreviation": "ADN",
  "type": "molecule",
  "definition_fr": "Acide désoxyribonucléique, support de l'information génétique, constitué de deux chaînes complémentaires en double hélice",
  "definition_ar": "الحمض النووي الريبي منقوص الأكسجين، حامل المعلومات الوراثية، يتكون من سلسلتين متكاملتين بشكل حلزوني مزدوج",
  "synonymes_fr": ["acide désoxyribonucléique"],
  "synonymes_ar": ["الدنا"],
  "importance": "critique",
  "bac_frequent": true,
  "chapitre_principal": "Synthèse des protéines",
  "micro_concept_id": "ch1_proteines",
  "exemples_contexte": [
    "L'ADN est une molécule en double hélice située dans le noyau",
    "La transcription utilise l'ADN comme matrice pour synthétiser l'ARNm"
  ],
  "termes_lies": ["term-002", "term-003"],
  "tags": ["molecule", "genetique", "structure", "noyau"]
}
```

---

## Structure des fichiers source disponibles

### 1. `programme_sciences_3as.backup_20260608_181234.json`
Backup propre : 6 chapitres avec noms arabes + concepts clés (voir tableau Domaine 1 ci-dessus).

### 2. `programme_sciences_3as.json` (fichier principal de travail)
Fichier évolué contenant des centaines de questions BAC réelles avec :
- `micro_concept_id` : mapping vers les chapitres (ch1_proteines, ch_structure, ch2_enzymes, ch3_immunite, ch_nerveux, ch_minhajiya)
- `diagnostic_erreur_cible` : codes d'erreur type `ERR_IMM_METH_01`
- Solutions arabes et notes pédagogiques

### 3. `methodologie_sciences_3as.json`
Fichier de méthodologie contenant :
- Progression officielle des apprentissages (تدريج التعليمات)
- Règles d'analyse et d'interprétation (التحليل والاستنتاج)
- Méthodologie du texte scientifique (النص العلمي)
- Erreurs fréquentes des élèves (الأخطاء الشائعة)
- Résumés par unité (ملخصات)

### 4. `eddirasa_minhajiya_links.json`
31 URLs eddirasa.com organisées en :
- Méthodologie (analyse, texte scientifique, erreurs fréquentes)
- Résumés par chapitre (ملخصات لكل وحدة)
- Couvre les 3 domaines

---

## Instructions spécifiques pour la génération

1. **Générer d'abord le Domaine 1 (Protéines)** — le plus riche, 5 catégories, ~40 termes minimum par catégorie
2. **Puis Domaine 2 (Énergie)** — 3 catégories
3. **Puis Domaine 3 (Tectonique)** — 3 catégories
4. Ajouter des **liens transversaux** entre domaines (ex: ATP synthase apparaît dans Photosynthèse ET Respiration)
5. Marquer `bac_frequent: true` pour les termes qui apparaissent fréquemment dans les sujets BAC (guidé par les questions du programme_sciences_3as.json)
6. Utiliser les définitions précises du programme officiel algérien (pas les définitions françaises standard)

## Format de sortie attendu

Fichier JSON unique : `lexique_svt_terminale_complet.json`
- Minimum 300 termes
- 3 domaines, 11 catégories
- Liens transversaux (minimum 15-20)
- Validation JSON stricte avant livraison

---

*Généré le 2026-06-15 pour le projet IA Khawarizmi Pro v2.0.0*
