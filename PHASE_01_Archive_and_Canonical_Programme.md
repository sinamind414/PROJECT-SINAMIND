# PHASE 01 — Archivage + Programme Canonique

## 1. Créer le dossier d'archivage

Crée le dossier :
```
khawarizmi-backend/data_archive/2026-06-20/
```

## 2. Archiver les anciens fichiers corrompus

Déplace (ou copie) les fichiers suivants dans le dossier d'archivage :

- `khawarizmi-backend/data/annales_sciences_3as.json`
- `khawarizmi-backend/data/annales_maths_3as.json`
- `khawarizmi-backend/data/programme_sciences_3as.json`
- `khawarizmi-backend/data/lexique_svt_terminale_complet.json`
- `khawarizmi-backend/data/programme_sciences_3as.backup_20260608_181234.json`

## 3. Créer le Programme Canonique (42 micro-concepts)

Crée le fichier :
```
khawarizmi-backend/data/official/programme_svt_3as_canonical.json
```

Contenu exact :

```json
{
  "metadata": {
    "version": "2026.2.0",
    "source": "ONEC - Programme officiel SVT Terminale Sciences Expérimentales Algérie",
    "matiere": "SVT",
    "niveau": "3AS",
    "filiere": "Sciences Expérimentales",
    "date": "2026-06-20",
    "status": "FOUNDATION"
  },
  "domaines": [
    {
      "id": "domaine_proteines",
      "nom_fr": "Spécialisation fonctionnelle des protéines",
      "nom_ar": "التخصص الوظيفي للبروتينات",
      "importance": "critique",
      "chapitres": [
        {
          "id": "ch1_proteines",
          "nom_fr": "Synthèse des protéines",
          "nom_ar": "تركيب البروتينات",
          "micro_concepts": [
            {"id": "mc_prot_01", "nom_fr": "Transcription de l'ADN", "nom_ar": "نسخ المعلومة الوراثية", "importance": "critique", "bac_frequent": true},
            {"id": "mc_prot_02", "nom_fr": "Traduction de l'ARNm", "nom_ar": "ترجمة الرنا الرسول", "importance": "critique", "bac_frequent": true},
            {"id": "mc_prot_03", "nom_fr": "Code génétique", "nom_ar": "الشفرة الوراثية", "importance": "critique", "bac_frequent": true},
            {"id": "mc_prot_04", "nom_fr": "ARN messager (ARNm)", "nom_ar": "الرنا الرسول", "importance": "critique", "bac_frequent": true},
            {"id": "mc_prot_05", "nom_fr": "ARN de transfert (ARNt)", "nom_ar": "الرنا الناقل", "importance": "haute", "bac_frequent": true},
            {"id": "mc_prot_06", "nom_fr": "Ribosome", "nom_ar": "الريبوزوم", "importance": "critique", "bac_frequent": true},
            {"id": "mc_prot_07", "nom_fr": "Initiation de la traduction", "nom_ar": "بدء الترجمة", "importance": "haute", "bac_frequent": true},
            {"id": "mc_prot_08", "nom_fr": "Élongation et terminaison", "nom_ar": "الاستطالة والإنهاء", "importance": "haute", "bac_frequent": false}
          ]
        },
        {
          "id": "ch_structure_proteines",
          "nom_fr": "Structure et fonction des protéines",
          "nom_ar": "بنية البروتين ووظيفته",
          "micro_concepts": [
            {"id": "mc_struc_01", "nom_fr": "Structure primaire", "nom_ar": "البنية الأولية", "importance": "haute", "bac_frequent": true},
            {"id": "mc_struc_02", "nom_fr": "Structure secondaire (α-hélice, feuillet β)", "nom_ar": "البنية الثانوية", "importance": "haute", "bac_frequent": true},
            {"id": "mc_struc_03", "nom_fr": "Structure tertiaire", "nom_ar": "البنية الثالثية", "importance": "critique", "bac_frequent": true},
            {"id": "mc_struc_04", "nom_fr": "Structure quaternaire", "nom_ar": "البنية الرباعية", "importance": "moyenne", "bac_frequent": false},
            {"id": "mc_struc_05", "nom_fr": "Relation structure-fonction", "nom_ar": "العلاقة بين البنية والوظيفة", "importance": "critique", "bac_frequent": true}
          ]
        },
        {
          "id": "ch2_enzymes",
          "nom_fr": "Activité enzymatique",
          "nom_ar": "النشاط الإنزيمي",
          "micro_concepts": [
            {"id": "mc_enz_01", "nom_fr": "Site actif de l'enzyme", "nom_ar": "الموقع الفعال للإنزيم", "importance": "critique", "bac_frequent": true},
            {"id": "mc_enz_02", "nom_fr": "Spécificité enzymatique", "nom_ar": "النوعية الإنزيمية", "importance": "critique", "bac_frequent": true},
            {"id": "mc_enz_03", "nom_fr": "Vitesse de réaction enzymatique", "nom_ar": "سرعة التفاعل الإنزيمي", "importance": "haute", "bac_frequent": true},
            {"id": "mc_enz_04", "nom_fr": "Facteurs influençant l'activité (température, pH)", "nom_ar": "العوامل المؤثرة على النشاط الإنزيمي", "importance": "critique", "bac_frequent": true},
            {"id": "mc_enz_05", "nom_fr": "Inhibition enzymatique", "nom_ar": "تثبيط الإنزيم", "importance": "haute", "bac_frequent": false}
          ]
        },
        {
          "id": "ch3_immunite",
          "nom_fr": "Immunologie",
          "nom_ar": "المناعة",
          "micro_concepts": [
            {"id": "mc_imm_01", "nom_fr": "Lymphocytes B", "nom_ar": "الخلايا الليمفاوية B", "importance": "critique", "bac_frequent": true},
            {"id": "mc_imm_02", "nom_fr": "Lymphocytes T", "nom_ar": "الخلايا الليمفاوية T", "importance": "critique", "bac_frequent": true},
            {"id": "mc_imm_03", "nom_fr": "Anticorps et antigènes", "nom_ar": "الأجسام المضادة والمستضدات", "importance": "critique", "bac_frequent": true},
            {"id": "mc_imm_04", "nom_fr": "Réponse immunitaire humorale", "nom_ar": "الاستجابة المناعية الخلطية", "importance": "haute", "bac_frequent": true},
            {"id": "mc_imm_05", "nom_fr": "Réponse immunitaire cellulaire", "nom_ar": "الاستجابة المناعية الخلوية", "importance": "haute", "bac_frequent": true},
            {"id": "mc_imm_06", "nom_fr": "Mémoire immunitaire", "nom_ar": "الذاكرة المناعية", "importance": "haute", "bac_frequent": true}
          ]
        },
        {
          "id": "ch4_nerveux",
          "nom_fr": "Transmission de l'information nerveuse",
          "nom_ar": "نقل المعلومة العصبية",
          "micro_concepts": [
            {"id": "mc_nerv_01", "nom_fr": "Potentiel de repos", "nom_ar": "كمون الراحة", "importance": "critique", "bac_frequent": true},
            {"id": "mc_nerv_02", "nom_fr": "Potentiel d'action", "nom_ar": "كمون العمل", "importance": "critique", "bac_frequent": true},
            {"id": "mc_nerv_03", "nom_fr": "Synapse chimique", "nom_ar": "المشبك الكيميائي", "importance": "critique", "bac_frequent": true},
            {"id": "mc_nerv_04", "nom_fr": "Neurotransmetteurs", "nom_ar": "النواقل العصبية", "importance": "haute", "bac_frequent": true}
          ]
        }
      ]
    },
    {
      "id": "domaine_energie",
      "nom_fr": "Transformations énergétiques",
      "nom_ar": "التحولات الطاقوية",
      "chapitres": [
        {
          "id": "ch_photosynthese",
          "nom_fr": "Photosynthèse",
          "nom_ar": "التركيب الضوئي",
          "micro_concepts": [
            {"id": "mc_photo_01", "nom_fr": "Chloroplaste et thylakoïdes", "nom_ar": "البلاستيدات الخضراء والثايلاكويدات", "importance": "critique", "bac_frequent": true},
            {"id": "mc_photo_02", "nom_fr": "Phase photochimique (lumineuse)", "nom_ar": "المرحلة الضوئية", "importance": "critique", "bac_frequent": true},
            {"id": "mc_photo_03", "nom_fr": "Cycle de Calvin (phase obscure)", "nom_ar": "دورة كالفن", "importance": "critique", "bac_frequent": true},
            {"id": "mc_photo_04", "nom_fr": "Facteurs influençant la photosynthèse", "nom_ar": "العوامل المؤثرة على التركيب الضوئي", "importance": "haute", "bac_frequent": true}
          ]
        },
        {
          "id": "ch_respiration",
          "nom_fr": "Respiration cellulaire",
          "nom_ar": "التنفس الخلوي",
          "micro_concepts": [
            {"id": "mc_resp_01", "nom_fr": "Mitochondrie", "nom_ar": "الميتوكوندريا", "importance": "critique", "bac_frequent": true},
            {"id": "mc_resp_02", "nom_fr": "Glycolyse", "nom_ar": "الجليكوليز", "importance": "haute", "bac_frequent": true},
            {"id": "mc_resp_03", "nom_fr": "Cycle de Krebs", "nom_ar": "دورة كربس", "importance": "critique", "bac_frequent": true},
            {"id": "mc_resp_04", "nom_fr": "Chaîne respiratoire et phosphorylation oxydative", "nom_ar": "سلسلة التنفس والفسفرة التأكسدية", "importance": "critique", "bac_frequent": true},
            {"id": "mc_resp_05", "nom_fr": "Fermentation (lactique et alcoolique)", "nom_ar": "التخمر", "importance": "haute", "bac_frequent": true}
          ]
        }
      ]
    },
    {
      "id": "domaine_tectonique",
      "nom_fr": "Tectonique globale",
      "nom_ar": "التكتونية العامة",
      "chapitres": [
        {
          "id": "ch_tectonique",
          "nom_fr": "Tectonique des plaques",
          "nom_ar": "تكتونية الصفائح",
          "micro_concepts": [
            {"id": "mc_tec_01", "nom_fr": "Structure interne de la Terre", "nom_ar": "البنية الداخلية للأرض", "importance": "haute", "bac_frequent": true},
            {"id": "mc_tec_02", "nom_fr": "Plaques tectoniques", "nom_ar": "الصفائح التكتونية", "importance": "critique", "bac_frequent": true},
            {"id": "mc_tec_03", "nom_fr": "Divergence et convergence des plaques", "nom_ar": "تباعد وتقارب الصفائح", "importance": "critique", "bac_frequent": true},
            {"id": "mc_tec_04", "nom_fr": "Subduction et dorsales océaniques", "nom_ar": "الاندساس والحواف المتباعدة", "importance": "haute", "bac_frequent": true},
            {"id": "mc_tec_05", "nom_fr": "Sismicité et volcanisme", "nom_ar": "الزلازل والبراكين", "importance": "haute", "bac_frequent": true}
          ]
        }
      ]
    }
  ]
}
```

**Fin de la Phase 1.** Confirme que tu as terminé cette phase avant de passer à la Phase 2.