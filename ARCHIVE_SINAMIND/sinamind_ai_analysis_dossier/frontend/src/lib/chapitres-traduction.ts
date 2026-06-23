export const CHAPITRES_TRADUCTION: Record<string, string> = {
  // Domaine 1 — Protéines
  "Rappel des acquis": "تذكير بالمكتسبات",
  "Siege de la synthese des proteines": "مقر تركيب البروتين",
  "Transcription de l'information genetique au niveau de l'ADN":
    "استنساخ المعلومة الوراثية على مستوى ADN",
  "La traduction": "الترجمة",
  "Les etapes de la traduction": "مراحل الترجمة",
  "Representation de la structure tridimensionnelle de la proteine":
    "تمثيل البنية الفراغية للبروتين",
  "Niveaux de la structure spatiale des proteines":
    "مستويات البنية الفراغية للبروتينات",
  "Relation entre structure et fonction de la proteine":
    "العلاقة بين بنية ووظيفة البروتين",
  "Notion d'enzyme et son importance": "مفهوم الإنزيم وأهميته",
  "L'activite enzymatique et sa relation avec la structure de l'enzyme":
    "النشاط الإنزيمي وعلاقته ببنية الإنزيم",
  "Etude de l'influence du pH du milieu sur l'activite enzymatique":
    "دراسة تأثير pH على النشاط الإنزيمي",
  "Etude de l'influence de la temperature sur l'activite enzymatique":
    "دراسة تأثير الحرارة على النشاط الإنزيمي",
  "Le soi et le non-soi": "الذات واللاذات",
  "Les molecules de defense dans le premier cas (immunite non specifique)":
    "جزيئات الدفاع في الاستجابة المناعية غير النوعية",
  "Le complexe immun": "المعقد المناعي",
  "Origine des anticorps": "منشأ الأجسام المضادة",
  "Les elements de defense dans le deuxieme cas (immunite specifique)":
    "عناصر الدفاع في الاستجابة المناعية النوعية",
  "Modes d'action des lymphocytes LTc": "آليات عمل اللمفاويات LTc",
  "Origine des lymphocytes LTc": "منشأ اللمفاويات LTc",
  "Activation des cellules LB et LT": "تنشيط الخلايا LB و LT",
  "Choix du type de reponse immunitaire": "اختيار نوع الاستجابة المناعية",
  "Cause de la perte de l'immunite acquise (SIDA)":
    "أسباب فقدان المناعة المكتسبة (SIDA)",
  "La transmission synaptique (potentiel membranaire)":
    "النقل المشبكي (الكمون الغشائي)",
  "Mecanisme de la transmission synaptique": "آلية النقل المشبكي",
  "Le potentiel de repos": "كمون الراحة",
  "Le potentiel d'action": "كمون العمل",
  "Mecanisme de l'integration nerveuse": "آلية التكامل العصبي",
  "Effet des drogues au niveau des synapses":
    "تأثير المخدرات على مستوى المشابك",

  // Domaine 2 — Énergie
  "Siege de la photosynthese - Ultrastructure du chloroplaste":
    "مقر التركيب الضوئي — البنية التحتية للصانعة الخضراء",
  "Reactions de la phase photochimique (phase claire)":
    "تفاعلات المرحلة الكيموضوئية",
  "Reactions de la phase chimique (cycle de Calvin - phase sombre)":
    "تفاعلات المرحلة الكيميائية (دورة كالفن)",
  "Siege de l'oxydation respiratoire": "مقر الأكسدة التنفسية",
  "La glycolyse": "تحلل السكر",
  "Etapes de degradation de l'acide pyruvique (reactions du cycle de Krebs)":
    "مراحل تفكك حمض البيروفيك (دورة كريبس)",
  "La phosphorylation oxydative": "الفسفرة التأكسدية",
  "Mecanismes de conversion en milieu anaerobie (fermentation)":
    "آليات التحويل في الوسط اللاهوائي (التخمر)",
  "Les transformations energetiques au niveau cellulaire":
    "التحولات الطاقوية على المستوى الخلوي",

  // Domaine 3 — Tectonique
  "Identification des plaques tectoniques": "تحديد الصفائح التكتونية",
  "Mouvements des plaques tectoniques": "حركات الصفائح التكتونية",
  "L'energie interne du globe terrestre": "الطاقة الداخلية للكرة الأرضية",
  "Les ondes sismiques": "الموجات الزلزالية",
  "Composition chimique des roches de la croute terrestre et du manteau":
    "التركيب الكيميائي لصخور القشرة والوشاح",
  "Modelisation de la structure interne du globe terrestre":
    "نمذجة البنية الداخلية للكرة الأرضية",
  "Caracteristiques des dorsales medio-oceaniques":
    "خصائص الظهرات وسط محيطية",
  "Le magmatisme et la formation de la plaque oceanique":
    "الماغماتية وتشكل اللوح المحيطي",
  "Formation des roches caracteristiques de la dorsale medio-oceanique":
    "تشكل الصخور المميزة للظهرة وسط محيطية",
  "Phenomenes lies a la subduction": "الظواهر المرتبطة بالغوص",
  "Disparition de la plaque oceanique et phenomenes lies a la subduction":
    "اختفاء اللوح المحيطي والظواهر المرتبطة بالغوص",
  "Reliefs resultant de la collision": "التضاريس الناتجة عن التصادم",
  "Indices du raccourcissement": "مؤشرات التقصير",
  "Indices d'un ancien ocean (ophiolites)": "مؤشرات محيط قديم (الأوفيوليت)"
}

export function traduireChapitre(label: string): string {
  if (/[\u0600-\u06FF]/.test(label)) {
    return label
  }

  if (CHAPITRES_TRADUCTION[label]) {
    return CHAPITRES_TRADUCTION[label]
  }

  for (const [fr, ar] of Object.entries(CHAPITRES_TRADUCTION)) {
    if (label.includes(fr) || fr.includes(label)) {
      return ar
    }
  }

  return label
}

export const UI_AR: Record<string, string> = {
  mode_feynman: "وضع فاينمان",
  choisis_chapitre: "اختر فصلا",
  selectionne_chapitre: "اختر فصلا لبدء شرحه بطريقة فاينمان",
  session_drill: "جلسة تمرين",
  rappel_actif: "التذكر النشط",
  description_rappel: "اختبر ذاكرتك بأسئلة متنوعة من جميع الفصول",
  effort_recup: "مجهود الاسترجاع يعزز الحفظ على المدى الطويل",
  commencer_session: "بدء الجلسة",
}
