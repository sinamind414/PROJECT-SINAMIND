# PHASE 05 — Créer les Templates

## 5.1 Template JSON

**Fichier** : `khawarizmi-backend/templates/question_template.json`

```json
{
  "id": "TEMPLATE_001",
  "source": {
    "pdf": "KHELIFA_2023_Vol3.pdf",
    "volume": "KHELIFA 2023",
    "page": 47
  },
  "type": "analyse_document",
  "texte": "أكمل الجدول الخاص بالكواشف المستعملة للتعرف على مكونات الحليب",
  "micro_concept_id": "mc_prot_01",
  "secondary_concepts": ["mc_prot_04"],
  "points": 3,
  "difficulte": "moyenne",
  "annee": 2023,
  "session": "Principale",
  "notes": "Question classique sur la transcription."
}
```

## 5.2 Template CSV (recommandé pour batch)

**Fichier** : `khawarizmi-backend/templates/questions_batch_template.csv`

```
id,source_pdf,volume,page,texte,micro_concept_id,secondary_concepts,points,difficulte,annee,session,type,notes
q_khelifa_2023_01,KHELIFA_2023_Vol3.pdf,KHELIFA 2023,47,"ما دور الريبوزوم في عملية الترجمة؟",mc_prot_06,mc_prot_02,2,moyenne,2023,Principale,question_courte,"Concept ribosome"
q_finalbac_2022_05,FINALBAC_VOLUME_2.pdf,FINAL BAC,112,"اشرح تأثير درجة الحرارة على نشاط الإنزيم.",mc_enz_04,,3,haute,2022,Principale,exercice,"Facteurs enzymatiques"
q_morafik_2024_03,SCIENCES_MORAFIK_Vol1.pdf,MORAFIK 2024,28,"أذكر ثلاث خصائص للإنزيم.",mc_enz_01,mc_enz_02,3,moyenne,2024,Principale,exercice,"Spécificité + site actif"
```

**Fin de la Phase 5.**