import type { MethodologyVerbSlug } from "@/lib/methodology-documents"

export type MethodologyChapterLink = {
  slug: string
  domainNumero: number
  domainAr: string
  domainFr: string
  unitNumero: number
  unitAr: string
  unitFr: string
  chapterNumero: number
  chapterAr: string
  chapterFr: string
  chapterType?: string
  chapterImportance: "critique" | "haute" | "moyenne"
  scenarioId: string
  focusAr: string
  recommendedVerbs: MethodologyVerbSlug[]
}

export const methodologyChapterLinks: MethodologyChapterLink[] = [
  // ===================== DOMAINE 1: التخصص الوظيفي للبروتينات =====================
  // Unité 1: تركيب البروتين / Synthese des proteines
  {
    slug: "d1-u1-c1-composition-chimique-des-proteines",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 1, unitAr: "تركيب البروتين", unitFr: "Synthese des proteines",
    chapterNumero: 1, chapterAr: "التركيب الكيميائي للبروتينات", chapterFr: "Composition chimique des proteines",
    chapterType: "concept", chapterImportance: "critique",
    scenarioId: "gene-expression-protein-disorder-v1",
    focusAr: "التركيز المنهجي: تحليل بنية الأحماض الأمينية ودراسة الروابط الببتيدية لفهم مبدأ تعدد مستويات البنية.",
    recommendedVerbs: ["analyse", "interpret", "compare", "relationship"],
  },
  {
    slug: "d1-u1-c2-relation-entre-adn-et-proteine",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 1, unitAr: "تركيب البروتين", unitFr: "Synthese des proteines",
    chapterNumero: 2, chapterAr: "العلاقة بين ADN والبروتين", chapterFr: "Relation entre ADN et proteine",
    chapterType: "concept", chapterImportance: "critique",
    scenarioId: "gene-expression-protein-disorder-v1",
    focusAr: "التركيز المنهجي: تحليل وثائق تظهر العلاقة بين تسلسل ADN وتسلسل الأحماض الأمينية وربطها بمفهوم المورثة.",
    recommendedVerbs: ["analyse", "interpret", "compare", "relationship"],
  },
  {
    slug: "d1-u1-c3-transcription-de-linformation-genetique-au-niveau-de-ladn",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 1, unitAr: "تركيب البروتين", unitFr: "Synthese des proteines",
    chapterNumero: 3, chapterAr: "استنساخ المعلومات الوراثية الموجودة على مستوى ADN", chapterFr: "Transcription de l'information genetique au niveau de l'ADN",
    chapterType: "processus", chapterImportance: "critique",
    scenarioId: "gene-expression-protein-disorder-v1",
    focusAr: "التركيز المنهجي في هذا الفصل هو تحليل مراحل الاستنساخ وربطها بنتائج الوثائق والمكتسبات العلمية.",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d1-u1-c4-traduction-de-larnm-en-proteine",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 1, unitAr: "تركيب البروتين", unitFr: "Synthese des proteines",
    chapterNumero: 4, chapterAr: "الترجمة: من ARNm إلى البروتين", chapterFr: "Traduction: de l'ARNm a la proteine",
    chapterType: "processus", chapterImportance: "critique",
    scenarioId: "gene-expression-protein-disorder-v1",
    focusAr: "التركيز المنهجي: متابعة مراحل الترجمة على الريبوسوم وتحليل دور ARNt والشفرة الوراثية.",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d1-u1-c5-synthese-du-gene-a-la-proteine",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 1, unitAr: "تركيب البروتين", unitFr: "Synthese des proteines",
    chapterNumero: 5, chapterAr: "تمرين شامل: من المورثة إلى البروتين", chapterFr: "Synthese: du gene a la proteine",
    chapterType: "synthese", chapterImportance: "haute",
    scenarioId: "gene-expression-protein-disorder-v1",
    focusAr: "التركيز المنهجي: ربط جميع مراحل التعبير المورثي في نص علمي منسق مع تحليل وثائق متنوعة.",
    recommendedVerbs: ["scientific-text", "compare", "relationship", "deduce"],
  },

  // Unité 2: العلاقة بين بنية ووظيفة البروتين / Relation entre structure et fonction
  {
    slug: "d1-u2-c1-structure-spatiale-des-proteines",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 2, unitAr: "العلاقة بين بنية ووظيفة البروتين", unitFr: "Relation entre structure et fonction des proteines",
    chapterNumero: 1, chapterAr: "البنية الفراغية للبروتينات", chapterFr: "Structure spatiale des proteines",
    chapterType: "concept", chapterImportance: "critique",
    scenarioId: "protein-structure-function-v1",
    focusAr: "التركيز المنهجي: فهم مستويات البنية (أولي، ثانوي، ثالثي، رابعي) وربطها بالوظيفة.",
    recommendedVerbs: ["analyse", "interpret", "compare", "relationship"],
  },
  {
    slug: "d1-u2-c2-relation-structure-fonction-enzymatique",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 2, unitAr: "العلاقة بين بنية ووظيفة البروتين", unitFr: "Relation entre structure et fonction des proteines",
    chapterNumero: 2, chapterAr: "العلاقة بين البنية والوظيفة الإنزيمية", chapterFr: "Relation structure-fonction enzymatique",
    chapterType: "concept", chapterImportance: "critique",
    scenarioId: "protein-structure-function-v1",
    focusAr: "التركيز المنهجي: تحليل تأثير تغير بنية الموقع النشط على وظيفة الإنزيم.",
    recommendedVerbs: ["analyse", "interpret", "compare", "relationship"],
  },
  {
    slug: "d1-u2-c3-proteines-de-transport-exemple-hemoglobine",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 2, unitAr: "العلاقة بين بنية ووظيفة البروتين", unitFr: "Relation entre structure et fonction des proteines",
    chapterNumero: 3, chapterAr: "البروتينات الناقلة: مثال الهيموغلوبين", chapterFr: "Proteines de transport: exemple de l'hemoglobine",
    chapterType: "processus", chapterImportance: "haute",
    scenarioId: "protein-structure-function-v1",
    focusAr: "التركيز المنهجي: دراسة بنية الهيموغلوبين وعلاقتها بنقل الأكسجين وتأثير الطفرات.",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d1-u2-c4-effet-des-mutations-sur-la-structure-des-proteines",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 2, unitAr: "العلاقة بين بنية ووظيفة البروتين", unitFr: "Relation entre structure et fonction des proteines",
    chapterNumero: 4, chapterAr: "تأثير الطفرات على بنية البروتين", chapterFr: "Effet des mutations sur la structure des proteines",
    chapterType: "experience", chapterImportance: "haute",
    scenarioId: "protein-structure-function-v1",
    focusAr: "التركيز المنهجي: تحليل وثائق طفرية ومقارنة البروتين الطبيعي بالطافر وربط التغير بالوظيفة.",
    recommendedVerbs: ["analyse", "interpret", "justify", "relationship"],
  },
  {
    slug: "d1-u2-c5-synthese-analyse-de-documents-structure-fonction",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 2, unitAr: "العلاقة بين بنية ووظيفة البروتين", unitFr: "Relation entre structure et fonction des proteines",
    chapterNumero: 5, chapterAr: "تمرين شامل: تحليل وثائق بنية ووظيفة البروتين", chapterFr: "Synthese: analyse de documents structure-fonction",
    chapterType: "synthese", chapterImportance: "haute",
    scenarioId: "protein-structure-function-v1",
    focusAr: "التركيز المنهجي: توظيف المكتسبات في تحليل وثائق متنوعة حول العلاقة بين بنية ووظيفة البروتينات.",
    recommendedVerbs: ["scientific-text", "compare", "relationship", "deduce"],
  },

  // Unité 3: النشاط الإنزيمي للبروتينات / L'activite enzymatique
  {
    slug: "d1-u3-c1-proprietes-des-enzymes",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 3, unitAr: "النشاط الإنزيمي للبروتينات", unitFr: "L'activite enzymatique des proteines",
    chapterNumero: 1, chapterAr: "خصائص الإنزيمات", chapterFr: "Proprietes des enzymes",
    chapterType: "concept", chapterImportance: "critique",
    scenarioId: "enzyme-activity-v1",
    focusAr: "التركيز المنهجي: استخراج خصائص الإنزيمات من وثائق (النوعية، قابلية التثبيط، الظروف المثلى).",
    recommendedVerbs: ["analyse", "interpret", "compare", "relationship"],
  },
  {
    slug: "d1-u3-c2-effet-de-la-temperature-sur-lactivite-enzymatique",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 3, unitAr: "النشاط الإنزيمي للبروتينات", unitFr: "L'activite enzymatique des proteines",
    chapterNumero: 2, chapterAr: "تأثير درجة الحرارة على النشاط الإنزيمي", chapterFr: "Effet de la temperature sur l'activite enzymatique",
    chapterType: "experience", chapterImportance: "critique",
    scenarioId: "enzyme-activity-v1",
    focusAr: "التركيز المنهجي: تحليل منحنيات تأثير درجة الحرارة وتفسير ظاهرة التمسخ الحراري.",
    recommendedVerbs: ["analyse", "interpret", "justify", "relationship"],
  },
  {
    slug: "d1-u3-c3-effet-du-ph-sur-lactivite-enzymatique",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 3, unitAr: "النشاط الإنزيمي للبروتينات", unitFr: "L'activite enzymatique des proteines",
    chapterNumero: 3, chapterAr: "تأثير pH الوسط على النشاط الإنزيمي", chapterFr: "Effet du pH sur l'activite enzymatique",
    chapterType: "experience", chapterImportance: "critique",
    scenarioId: "enzyme-activity-v1",
    focusAr: "التركيز المنهجي: تحليل نتائج تجارب تأثير pH وتحديد pH الأمثل لكل إنزيم.",
    recommendedVerbs: ["analyse", "interpret", "justify", "relationship"],
  },
  {
    slug: "d1-u3-c4-role-des-cofacteurs-enzymatiques",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 3, unitAr: "النشاط الإنزيمي للبروتينات", unitFr: "L'activite enzymatique des proteines",
    chapterNumero: 4, chapterAr: "دور العوامل المساعدة للإنزيمات", chapterFr: "Role des cofacteurs enzymatiques",
    chapterType: "concept", chapterImportance: "moyenne",
    scenarioId: "enzyme-activity-v1",
    focusAr: "التركيز المنهجي: تحليل دور الأيونات المعدنية والفيتامينات كعوامل مساعدة في النشاط الإنزيمي.",
    recommendedVerbs: ["analyse", "interpret", "compare", "relationship"],
  },
  {
    slug: "d1-u3-c5-synthese-activite-enzymatique",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 3, unitAr: "النشاط الإنزيمي للبروتينات", unitFr: "L'activite enzymatique des proteines",
    chapterNumero: 5, chapterAr: "تمرين شامل: دراسة النشاط الإنزيمي", chapterFr: "Synthese: etude de l'activite enzymatique",
    chapterType: "synthese", chapterImportance: "haute",
    scenarioId: "enzyme-activity-v1",
    focusAr: "التركيز المنهجي: توظيف المكتسبات في تحليل وثائق متكاملة حول النشاط الإنزيمي والعوامل المؤثرة.",
    recommendedVerbs: ["scientific-text", "compare", "relationship", "deduce"],
  },

  // Unité 4: دور البروتينات في الدفاع عن الذات / Defense de soi
  {
    slug: "d1-u4-c1-reponse-immunitaire-humorale",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 4, unitAr: "دور البروتينات في الدفاع عن الذات", unitFr: "Role des proteines dans la defense de soi",
    chapterNumero: 1, chapterAr: "الاستجابة المناعية الخلطية", chapterFr: "Reponse immunitaire humorale",
    chapterType: "processus", chapterImportance: "critique",
    scenarioId: "immunity-defense-v1",
    focusAr: "التركيز المنهجي: تحليل مراحل تنشيط الخلايا B وإنتاج الأجسام المضادة ودورها في تحييد المستضدات.",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d1-u4-c2-reponse-immunitaire-cellulaire",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 4, unitAr: "دور البروتينات في الدفاع عن الذات", unitFr: "Role des proteines dans la defense de soi",
    chapterNumero: 2, chapterAr: "الاستجابة المناعية الخلوية", chapterFr: "Reponse immunitaire cellulaire",
    chapterType: "processus", chapterImportance: "critique",
    scenarioId: "immunity-defense-v1",
    focusAr: "التركيز المنهجي: تحليل دور الخلايا T القاتلة والتعاون بين الخلايا المناعية في القضاء على الخلايا المصابة.",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d1-u4-c3-memoire-immunitaire",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 4, unitAr: "دور البروتينات في الدفاع عن الذات", unitFr: "Role des proteines dans la defense de soi",
    chapterNumero: 3, chapterAr: "الذاكرة المناعية", chapterFr: "Memoire immunitaire",
    chapterType: "rappel", chapterImportance: "haute",
    scenarioId: "immunity-defense-v1",
    focusAr: "التركيز المنهجي: مقارنة الاستجابة الأولية والثانوية وتحليل منحنيات الاستجابة المناعية.",
    recommendedVerbs: ["analyse", "justify", "scientific-text"],
  },
  {
    slug: "d1-u4-c4-vaccins-et-serum",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 4, unitAr: "دور البروتينات في الدفاع عن الذات", unitFr: "Role des proteines dans la defense de soi",
    chapterNumero: 4, chapterAr: "اللقاحات والمصل", chapterFr: "Vaccins et serum",
    chapterType: "concept", chapterImportance: "haute",
    scenarioId: "immunity-defense-v1",
    focusAr: "التركيز المنهجي: التمييز بين اللقاح والمصل وتحليل مبدأ الوقاية والعلاج المناعي.",
    recommendedVerbs: ["analyse", "interpret", "compare", "relationship"],
  },
  {
    slug: "d1-u4-c5-synthese-immunite",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 4, unitAr: "دور البروتينات في الدفاع عن الذات", unitFr: "Role des proteines dans la defense de soi",
    chapterNumero: 5, chapterAr: "تمرين شامل: تحليل وثائق المناعة", chapterFr: "Synthese: analyse de documents immunitaires",
    chapterType: "synthese", chapterImportance: "haute",
    scenarioId: "immunity-defense-v1",
    focusAr: "التركيز المنهجي: ربط الاستجابة الخلطية والخلوية والذاكرة المناعية في تحليل وثائق البكالوريا.",
    recommendedVerbs: ["scientific-text", "compare", "relationship", "deduce"],
  },

  // Unité 5: دور البروتينات في الاتصال العصبي / Communication nerveuse
  {
    slug: "d1-u5-c1-structure-du-tissu-nerveux",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 5, unitAr: "دور البروتينات في الاتصال العصبي", unitFr: "Role des proteines dans la communication nerveuse",
    chapterNumero: 1, chapterAr: "بنية النسيج العصبي", chapterFr: "Structure du tissu nerveux",
    chapterType: "concept", chapterImportance: "critique",
    scenarioId: "nervous-communication-v1",
    focusAr: "التركيز المنهجي: التعرف على بنية العصبون والمشبك وأنواع الخلايا الدبقية من وثائق.",
    recommendedVerbs: ["analyse", "interpret", "compare", "relationship"],
  },
  {
    slug: "d1-u5-c2-potentiel-de-repos-et-daction",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 5, unitAr: "دور البروتينات في الاتصال العصبي", unitFr: "Role des proteines dans la communication nerveuse",
    chapterNumero: 2, chapterAr: "كمون الراحة وكمون العمل", chapterFr: "Potentiel de repos et potentiel d'action",
    chapterType: "processus", chapterImportance: "critique",
    scenarioId: "nervous-communication-v1",
    focusAr: "التركيز المنهجي: تحليل التسجيلات الكهربائية وتفسير تغيرات النفوذية الغشائية ودور مضخات الصوديوم والبوتاسيوم.",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d1-u5-c3-transmission-synaptique",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 5, unitAr: "دور البروتينات في الاتصال العصبي", unitFr: "Role des proteines dans la communication nerveuse",
    chapterNumero: 3, chapterAr: "النقل المشبكي", chapterFr: "Transmission synaptique",
    chapterType: "processus", chapterImportance: "critique",
    scenarioId: "nervous-communication-v1",
    focusAr: "التركيز المنهجي: تحليل مراحل النقل المشبكي ودور الناقلات العصبية والمستقبلات الغشائية.",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d1-u5-c4-role-des-neurotransmetteurs",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 5, unitAr: "دور البروتينات في الاتصال العصبي", unitFr: "Role des proteines dans la communication nerveuse",
    chapterNumero: 4, chapterAr: "دور الناقلات العصبية", chapterFr: "Role des neurotransmetteurs",
    chapterType: "concept", chapterImportance: "haute",
    scenarioId: "nervous-communication-v1",
    focusAr: "التركيز المنهجي: التمييز بين أنواع الناقلات العصبية (مثبطة/منبهة) وتحليل تأثير الأدوية والسموم.",
    recommendedVerbs: ["analyse", "interpret", "compare", "relationship"],
  },
  {
    slug: "d1-u5-c5-synthese-communication-nerveuse",
    domainNumero: 1, domainAr: "التخصص الوظيفي للبروتينات", domainFr: "La specialisation fonctionnelle des proteines",
    unitNumero: 5, unitAr: "دور البروتينات في الاتصال العصبي", unitFr: "Role des proteines dans la communication nerveuse",
    chapterNumero: 5, chapterAr: "تمرين شامل: الاتصال العصبي", chapterFr: "Synthese: communication nerveuse",
    chapterType: "synthese", chapterImportance: "haute",
    scenarioId: "nervous-communication-v1",
    focusAr: "التركيز المنهجي: ربط كمون العمل والنقل المشبكي في نص علمي متكامل مع تحليل وثائق البكالوريا.",
    recommendedVerbs: ["scientific-text", "compare", "relationship", "deduce"],
  },

  // ===================== DOMAINE 2: تحويل الطاقة / Conversion de l'energie =====================
  // Unité 1: آليات تحويل الطاقة الضوئية / Photosynthese
  {
    slug: "d2-u1-c1-structure-du-chloroplaste",
    domainNumero: 2, domainAr: "تحويل الطاقة", domainFr: "Conversion de l'energie",
    unitNumero: 1, unitAr: "آليات تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة", unitFr: "Mecanismes de conversion de l'energie lumineuse en energie chimique potentielle",
    chapterNumero: 1, chapterAr: "بنية الصانعة اليخضورية", chapterFr: "Structure du chloroplaste",
    chapterType: "rappel", chapterImportance: "haute",
    scenarioId: "photosynthesis-v1",
    focusAr: "التركيز المنهجي: التعرف على بنية الصانعة اليخضورية وربط الأغشية الثايلاكويدية بمراحل التركيب الضوئي.",
    recommendedVerbs: ["analyse", "justify", "scientific-text"],
  },
  {
    slug: "d2-u1-c2-reactions-photochimiques-phase-claire",
    domainNumero: 2, domainAr: "تحويل الطاقة", domainFr: "Conversion de l'energie",
    unitNumero: 1, unitAr: "آليات تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة", unitFr: "Mecanismes de conversion de l'energie lumineuse en energie chimique potentielle",
    chapterNumero: 2, chapterAr: "التفاعلات الضوئية (الطور الضوئي)", chapterFr: "Reactions photochimiques (phase claire)",
    chapterType: "processus", chapterImportance: "critique",
    scenarioId: "photosynthesis-v1",
    focusAr: "التركيز المنهجي: تحليل آليات تحويل الطاقة الضوئية إلى ATP وNADPH+H+ ودور اليخضور والسلسلة الضوئية.",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d2-u1-c3-reactions-non-photochimiques-phase-sombre",
    domainNumero: 2, domainAr: "تحويل الطاقة", domainFr: "Conversion de l'energie",
    unitNumero: 1, unitAr: "آليات تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة", unitFr: "Mecanismes de conversion de l'energie lumineuse en energie chimique potentielle",
    chapterNumero: 3, chapterAr: "التفاعلات اللاضوئية (طور التثبيت)", chapterFr: "Reactions non photochimiques (phase sombre)",
    chapterType: "processus", chapterImportance: "critique",
    scenarioId: "photosynthesis-v1",
    focusAr: "التركيز المنهجي: تحليل دورة كالفن وتثبيت CO2 ودور ATP وNADPH+H+ في تركيب الجلوكوز.",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d2-u1-c4-facteurs-influencant-la-photosynthese",
    domainNumero: 2, domainAr: "تحويل الطاقة", domainFr: "Conversion de l'energie",
    unitNumero: 1, unitAr: "آليات تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة", unitFr: "Mecanismes de conversion de l'energie lumineuse en energie chimique potentielle",
    chapterNumero: 4, chapterAr: "العوامل المؤثرة في التركيب الضوئي", chapterFr: "Facteurs influencant la photosynthese",
    chapterType: "experience", chapterImportance: "haute",
    scenarioId: "photosynthesis-v1",
    focusAr: "التركيز المنهجي: تحليل منحنيات تأثير شدة الضوء وتركيز CO2 ودرجة الحرارة على سرعة التركيب الضوئي.",
    recommendedVerbs: ["analyse", "interpret", "justify", "relationship"],
  },
  {
    slug: "d2-u1-c5-synthese-photosynthese",
    domainNumero: 2, domainAr: "تحويل الطاقة", domainFr: "Conversion de l'energie",
    unitNumero: 1, unitAr: "آليات تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة", unitFr: "Mecanismes de conversion de l'energie lumineuse en energie chimique potentielle",
    chapterNumero: 5, chapterAr: "تمرين شامل: التركيب الضوئي", chapterFr: "Synthese: photosynthese",
    chapterType: "synthese", chapterImportance: "haute",
    scenarioId: "photosynthesis-v1",
    focusAr: "التركيز المنهجي: ربط الطور الضوئي والطور اللاضوئي في نص علمي منسق مع تحليل وثائق متنوعة.",
    recommendedVerbs: ["scientific-text", "compare", "relationship", "deduce"],
  },

  // Unité 2: آليات تحويل الطاقة الكيميائية / Respiration cellulaire
  {
    slug: "d2-u2-c1-respiration-cellulaire-concept-general",
    domainNumero: 2, domainAr: "تحويل الطاقة", domainFr: "Conversion de l'energie",
    unitNumero: 2, unitAr: "آليات تحويل الطاقة الكيميائية الكامنة في الجزيئات العضوية إلى ATP", unitFr: "Mecanismes de conversion de l'energie chimique potentielle des molecules organiques en ATP",
    chapterNumero: 1, chapterAr: "التنفس الخلوي: مفهوم عام", chapterFr: "Respiration cellulaire: concept general",
    chapterType: "concept", chapterImportance: "critique",
    scenarioId: "cellular-respiration-v1",
    focusAr: "التركيز المنهجي: فهم المفهوم العام للتنفس الخلوي وربطه بإنتاج ATP في الميتوكندري.",
    recommendedVerbs: ["analyse", "interpret", "compare", "relationship"],
  },
  {
    slug: "d2-u2-c2-glycolyse",
    domainNumero: 2, domainAr: "تحويل الطاقة", domainFr: "Conversion de l'energie",
    unitNumero: 2, unitAr: "آليات تحويل الطاقة الكيميائية الكامنة في الجزيئات العضوية إلى ATP", unitFr: "Mecanismes de conversion de l'energie chimique potentielle des molecules organiques en ATP",
    chapterNumero: 2, chapterAr: "التحلل السكري", chapterFr: "Glycolyse",
    chapterType: "processus", chapterImportance: "haute",
    scenarioId: "cellular-respiration-v1",
    focusAr: "التركيز المنهجي: تحليل مراحل التحلل السكري في الهيولى وربطها بإنتاج ATP وNADH+H+.",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d2-u2-c3-cycle-de-krebs-et-chaine-respiratoire",
    domainNumero: 2, domainAr: "تحويل الطاقة", domainFr: "Conversion de l'energie",
    unitNumero: 2, unitAr: "آليات تحويل الطاقة الكيميائية الكامنة في الجزيئات العضوية إلى ATP", unitFr: "Mecanismes de conversion de l'energie chimique potentielle des molecules organiques en ATP",
    chapterNumero: 3, chapterAr: "دورة كريبس وسلسلة التنفس", chapterFr: "Cycle de Krebs et chaine respiratoire",
    chapterType: "processus", chapterImportance: "critique",
    scenarioId: "cellular-respiration-v1",
    focusAr: "التركيز المنهجي: تحليل مراحل دورة كريبس وسلسلة نقل الإلكترونات والفسفرة التأكسدية في الميتوكندري.",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d2-u2-c4-fermentation",
    domainNumero: 2, domainAr: "تحويل الطاقة", domainFr: "Conversion de l'energie",
    unitNumero: 2, unitAr: "آليات تحويل الطاقة الكيميائية الكامنة في الجزيئات العضوية إلى ATP", unitFr: "Mecanismes de conversion de l'energie chimique potentielle des molecules organiques en ATP",
    chapterNumero: 4, chapterAr: "التخمر", chapterFr: "Fermentation",
    chapterType: "processus", chapterImportance: "haute",
    scenarioId: "cellular-respiration-v1",
    focusAr: "التركيز المنهجي: مقارنة التخمر بالتنفس وتحليل مساري التخمر الكحولي واللبني في غياب الأكسجين.",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d2-u2-c5-synthese-conversion-energie-mitochondriale",
    domainNumero: 2, domainAr: "تحويل الطاقة", domainFr: "Conversion de l'energie",
    unitNumero: 2, unitAr: "آليات تحويل الطاقة الكيميائية الكامنة في الجزيئات العضوية إلى ATP", unitFr: "Mecanismes de conversion de l'energie chimique potentielle des molecules organiques en ATP",
    chapterNumero: 5, chapterAr: "تمرين شامل: تحويل الطاقة في الميتوكندري", chapterFr: "Synthese: conversion d'energie dans la mitochondrie",
    chapterType: "synthese", chapterImportance: "haute",
    scenarioId: "cellular-respiration-v1",
    focusAr: "التركيز المنهجي: ربط جميع مراحل التنفس الخلوي في نص علمي مع تحليل وثائق البكالوريا.",
    recommendedVerbs: ["scientific-text", "compare", "relationship", "deduce"],
  },

  // Unité 3: تحويل الطاقة على المستوى ما فوق البنية الخلوية / Ultrastructural
  {
    slug: "d2-u3-c1-echanges-gazeux-pulmonaires",
    domainNumero: 2, domainAr: "تحويل الطاقة", domainFr: "Conversion de l'energie",
    unitNumero: 3, unitAr: "تحويل الطاقة على المستوى ما فوق البنية الخلوية", unitFr: "Conversion de l'energie au niveau ultrastructural cellulaire",
    chapterNumero: 1, chapterAr: "تبادل الغازات على مستوى الرئة", chapterFr: "Echanges gazeux au niveau pulmonaire",
    chapterType: "processus", chapterImportance: "haute",
    scenarioId: "ultrastructural-energy-v1",
    focusAr: "التركيز المنهجي: تحليل آلية تبادل O2 وCO2 بين الحويصلات الهوائية والشعيرات الدموية.",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d2-u3-c2-transport-des-gaz-dans-le-sang",
    domainNumero: 2, domainAr: "تحويل الطاقة", domainFr: "Conversion de l'energie",
    unitNumero: 3, unitAr: "تحويل الطاقة على المستوى ما فوق البنية الخلوية", unitFr: "Conversion de l'energie au niveau ultrastructural cellulaire",
    chapterNumero: 2, chapterAr: "نقل الغازات في الدم", chapterFr: "Transport des gaz dans le sang",
    chapterType: "processus", chapterImportance: "haute",
    scenarioId: "ultrastructural-energy-v1",
    focusAr: "التركيز المنهجي: تحليل دور الهيموغلوبين في نقل O2 وCO2 ومنحنيات تفارق الأكسجين.",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d2-u3-c3-integration-fonctionnelle-des-organites",
    domainNumero: 2, domainAr: "تحويل الطاقة", domainFr: "Conversion de l'energie",
    unitNumero: 3, unitAr: "تحويل الطاقة على المستوى ما فوق البنية الخلوية", unitFr: "Conversion de l'energie au niveau ultrastructural cellulaire",
    chapterNumero: 3, chapterAr: "التكامل الوظيفي بين العضيات", chapterFr: "Integration fonctionnelle des organites",
    chapterType: "concept", chapterImportance: "critique",
    scenarioId: "ultrastructural-energy-v1",
    focusAr: "التركيز المنهجي: فهم العلاقة الوظيفية بين الصانعة اليخضورية والميتوكندري والشبكة الهيولية في تحويل الطاقة.",
    recommendedVerbs: ["analyse", "interpret", "compare", "relationship"],
  },
  {
    slug: "d2-u3-c4-comparaison-chloroplaste-mitochondrie",
    domainNumero: 2, domainAr: "تحويل الطاقة", domainFr: "Conversion de l'energie",
    unitNumero: 3, unitAr: "تحويل الطاقة على المستوى ما فوق البنية الخلوية", unitFr: "Conversion de l'energie au niveau ultrastructural cellulaire",
    chapterNumero: 4, chapterAr: "مقارنة بين اليخضور والميتوكندري", chapterFr: "Comparaison chloroplaste et mitochondrie",
    chapterType: "rappel", chapterImportance: "moyenne",
    scenarioId: "ultrastructural-energy-v1",
    focusAr: "التركيز المنهجي: مقارنة بنية ووظيفة الصانعة اليخضورية والميتوكندري في تحويل الطاقة.",
    recommendedVerbs: ["analyse", "justify", "scientific-text"],
  },
  {
    slug: "d2-u3-c5-synthese-conversion-energie-cellulaire",
    domainNumero: 2, domainAr: "تحويل الطاقة", domainFr: "Conversion de l'energie",
    unitNumero: 3, unitAr: "تحويل الطاقة على المستوى ما فوق البنية الخلوية", unitFr: "Conversion de l'energie au niveau ultrastructural cellulaire",
    chapterNumero: 5, chapterAr: "تمرين شامل: تحويل الطاقة على المستوى الخلوي", chapterFr: "Synthese: conversion de l'energie au niveau cellulaire",
    chapterType: "synthese", chapterImportance: "haute",
    scenarioId: "ultrastructural-energy-v1",
    focusAr: "التركيز المنهجي: ربط التبادل الغازي والنقل والتكامل الوظيفي للعضيات في نص علمي متكامل.",
    recommendedVerbs: ["scientific-text", "compare", "relationship", "deduce"],
  },

  // ===================== DOMAINE 3: ديناميكية الكرة الأرضية / Dynamique du globe =====================
  // Unité 1: النشاط التكتوني للصفائح / Tectonique des plaques
  {
    slug: "d3-u1-c1-structure-de-la-lithosphere",
    domainNumero: 3, domainAr: "ديناميكية الكرة الأرضية", domainFr: "Dynamique du globe terrestre",
    unitNumero: 1, unitAr: "النشاط التكتوني للصفائح", unitFr: "L'activite tectonique des plaques",
    chapterNumero: 1, chapterAr: "بنية الغلاف الصخري", chapterFr: "Structure de la lithosphere",
    chapterType: "concept", chapterImportance: "critique",
    scenarioId: "tectonics-general-v1",
    focusAr: "التركيز المنهجي: تحليل بنية الغلاف الصخري وتقسيمه إلى صفائح تكتونية باستخدام الوثائق.",
    recommendedVerbs: ["analyse", "interpret", "compare", "relationship"],
  },
  {
    slug: "d3-u1-c2-seismes-et-leur-distribution",
    domainNumero: 3, domainAr: "ديناميكية الكرة الأرضية", domainFr: "Dynamique du globe terrestre",
    unitNumero: 1, unitAr: "النشاط التكتوني للصفائح", unitFr: "L'activite tectonique des plaques",
    chapterNumero: 2, chapterAr: "الزلازل وتوزيعها", chapterFr: "Seismes et leur distribution",
    chapterType: "experience", chapterImportance: "critique",
    scenarioId: "tectonics-general-v1",
    focusAr: "التركيز المنهجي: تحليل خريطة توزيع الزلازل وربطها بحدود الصفائح التكتونية.",
    recommendedVerbs: ["analyse", "interpret", "justify", "relationship"],
  },
  {
    slug: "d3-u1-c3-volcans-et-leur-distribution",
    domainNumero: 3, domainAr: "ديناميكية الكرة الأرضية", domainFr: "Dynamique du globe terrestre",
    unitNumero: 1, unitAr: "النشاط التكتوني للصفائح", unitFr: "L'activite tectonique des plaques",
    chapterNumero: 3, chapterAr: "البراكين وتوزيعها", chapterFr: "Volcans et leur distribution",
    chapterType: "experience", chapterImportance: "critique",
    scenarioId: "tectonics-general-v1",
    focusAr: "التركيز المنهجي: تحليل خريطة توزيع البراكين والتمييز بين براكين الحدود المتقاربة والمتباعدة.",
    recommendedVerbs: ["analyse", "interpret", "justify", "relationship"],
  },
  {
    slug: "d3-u1-c4-limites-des-plaques-tectoniques",
    domainNumero: 3, domainAr: "ديناميكية الكرة الأرضية", domainFr: "Dynamique du globe terrestre",
    unitNumero: 1, unitAr: "النشاط التكتوني للصفائح", unitFr: "L'activite tectonique des plaques",
    chapterNumero: 4, chapterAr: "الحدود بين الصفائح التكتونية", chapterFr: "Limites des plaques tectoniques",
    chapterType: "concept", chapterImportance: "critique",
    scenarioId: "tectonics-general-v1",
    focusAr: "التركيز المنهجي: التمييز بين الحدود المتباعدة والمتقاربة والمتحولة وربطها بالظواهر الجيولوجية.",
    recommendedVerbs: ["analyse", "interpret", "compare", "relationship"],
  },
  {
    slug: "d3-u1-c5-synthese-mouvement-des-plaques",
    domainNumero: 3, domainAr: "ديناميكية الكرة الأرضية", domainFr: "Dynamique du globe terrestre",
    unitNumero: 1, unitAr: "النشاط التكتوني للصفائح", unitFr: "L'activite tectonique des plaques",
    chapterNumero: 5, chapterAr: "تمرين شامل: حركة الصفائح التكتونية", chapterFr: "Synthese: mouvement des plaques tectoniques",
    chapterType: "synthese", chapterImportance: "haute",
    scenarioId: "tectonics-general-v1",
    focusAr: "التركيز المنهجي: ربط الزلازل والبراكين والحدود في نص علمي شامل مع تحليل خريطة العالم.",
    recommendedVerbs: ["scientific-text", "compare", "relationship", "deduce"],
  },

  // Unité 2: بنية الكرة الأرضية / Structure du globe terrestre
  {
    slug: "d3-u2-c1-ondes-sismiques-et-structure-de-la-terre",
    domainNumero: 3, domainAr: "ديناميكية الكرة الأرضية", domainFr: "Dynamique du globe terrestre",
    unitNumero: 2, unitAr: "بنية الكرة الأرضية", unitFr: "Structure du globe terrestre",
    chapterNumero: 1, chapterAr: "الموجات الزلزالية وبنية الأرض", chapterFr: "Ondes sismiques et structure de la Terre",
    chapterType: "concept", chapterImportance: "critique",
    scenarioId: "earth-structure-v1",
    focusAr: "التركيز المنهجي: تحليل سرعة انتشار الموجات الزلزالية واستنتاج بنية الأرض الداخلية.",
    recommendedVerbs: ["analyse", "interpret", "compare", "relationship"],
  },
  {
    slug: "d3-u2-c2-structure-de-la-croute-terrestre",
    domainNumero: 3, domainAr: "ديناميكية الكرة الأرضية", domainFr: "Dynamique du globe terrestre",
    unitNumero: 2, unitAr: "بنية الكرة الأرضية", unitFr: "Structure du globe terrestre",
    chapterNumero: 2, chapterAr: "بنية القشرة الأرضية", chapterFr: "Structure de la croute terrestre",
    chapterType: "rappel", chapterImportance: "haute",
    scenarioId: "earth-structure-v1",
    focusAr: "التركيز المنهجي: التمييز بين القشرة القارية والمحيطية من حيث التركيب والسمك والكثافة.",
    recommendedVerbs: ["analyse", "justify", "scientific-text"],
  },
  {
    slug: "d3-u2-c3-lithosphere-et-asthenosphere",
    domainNumero: 3, domainAr: "ديناميكية الكرة الأرضية", domainFr: "Dynamique du globe terrestre",
    unitNumero: 2, unitAr: "بنية الكرة الأرضية", unitFr: "Structure du globe terrestre",
    chapterNumero: 3, chapterAr: "الغلاف الصخري والغلاف الموري", chapterFr: "Lithosphere et asthenosphere",
    chapterType: "concept", chapterImportance: "haute",
    scenarioId: "earth-structure-v1",
    focusAr: "التركيز المنهجي: التمييز بين الغلاف الصخري والغلاف الموري من حيث الصلابة واللدونة.",
    recommendedVerbs: ["analyse", "interpret", "compare", "relationship"],
  },
  {
    slug: "d3-u2-c4-atmosphere-et-hydrosphere",
    domainNumero: 3, domainAr: "ديناميكية الكرة الأرضية", domainFr: "Dynamique du globe terrestre",
    unitNumero: 2, unitAr: "بنية الكرة الأرضية", unitFr: "Structure du globe terrestre",
    chapterNumero: 4, chapterAr: "الغلاف الجوي والغلاف المائي", chapterFr: "Atmosphere et hydrosphere",
    chapterType: "rappel", chapterImportance: "moyenne",
    scenarioId: "earth-structure-v1",
    focusAr: "التركيز المنهجي: التعرف على طبقات الغلاف الجوي وأهمية الغلاف المائي في ديناميكية الأرض.",
    recommendedVerbs: ["analyse", "justify", "scientific-text"],
  },
  {
    slug: "d3-u2-c5-synthese-structure-du-globe",
    domainNumero: 3, domainAr: "ديناميكية الكرة الأرضية", domainFr: "Dynamique du globe terrestre",
    unitNumero: 2, unitAr: "بنية الكرة الأرضية", unitFr: "Structure du globe terrestre",
    chapterNumero: 5, chapterAr: "تمرين شامل: بنية الكرة الأرضية", chapterFr: "Synthese: structure du globe terrestre",
    chapterType: "synthese", chapterImportance: "haute",
    scenarioId: "earth-structure-v1",
    focusAr: "التركيز المنهجي: ربط الموجات الزلزالية وبنية القشرة والأغلفة في نص علمي متكامل مع تحليل وثائق.",
    recommendedVerbs: ["scientific-text", "compare", "relationship", "deduce"],
  },

  // Unité 3: النشاط التكتوني والبنيات الجيولوجية / Subduction, collision, dorsale
  {
    slug: "d3-u3-c1-expansion-oceanique-et-magnetisme",
    domainNumero: 3, domainAr: "ديناميكية الكرة الأرضية", domainFr: "Dynamique du globe terrestre",
    unitNumero: 3, unitAr: "النشاط التكتوني والبنيات الجيولوجية المرتبطة به", unitFr: "L'activite tectonique et les structures geologiques associees",
    chapterNumero: 1, chapterAr: "توسع قاع المحيط والحرية المغناطيسية", chapterFr: "Expansion oceanique et magnetisme",
    chapterType: "processus", chapterImportance: "critique",
    scenarioId: "subduction-collision-ridge-v1",
    focusAr: "التركيز المنهجي: تحليل الشذوذ المغناطيسي لقاع المحيط وإثبات توسع قاع المحيط عند الأعراف.",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d3-u3-c2-subduction",
    domainNumero: 3, domainAr: "ديناميكية الكرة الأرضية", domainFr: "Dynamique du globe terrestre",
    unitNumero: 3, unitAr: "النشاط التكتوني والبنيات الجيولوجية المرتبطة به", unitFr: "L'activite tectonique et les structures geologiques associees",
    chapterNumero: 2, chapterAr: "الاندساس", chapterFr: "Subduction",
    chapterType: "processus", chapterImportance: "critique",
    scenarioId: "subduction-collision-ridge-v1",
    focusAr: "التركيز المنهجي في هذا الفصل هو تحليل آلية اندساس الصفيحة المحيطية والظواهر المرافقة (زلازل، براكين، تشكل السلاسل).",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d3-u3-c3-collision-continentale",
    domainNumero: 3, domainAr: "ديناميكية الكرة الأرضية", domainFr: "Dynamique du globe terrestre",
    unitNumero: 3, unitAr: "النشاط التكتوني والبنيات الجيولوجية المرتبطة به", unitFr: "L'activite tectonique et les structures geologiques associees",
    chapterNumero: 3, chapterAr: "التصادم القاري", chapterFr: "Collision continentale",
    chapterType: "processus", chapterImportance: "critique",
    scenarioId: "subduction-collision-ridge-v1",
    focusAr: "التركيز المنهجي: تحليل مراحل التصادم القاري وتشكل السلاسل الجبلية (مثال جبال الألب والهيمالايا).",
    recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
  },
  {
    slug: "d3-u3-c4-formation-des-chaines-de-montagnes",
    domainNumero: 3, domainAr: "ديناميكية الكرة الأرضية", domainFr: "Dynamique du globe terrestre",
    unitNumero: 3, unitAr: "النشاط التكتوني والبنيات الجيولوجية المرتبطة به", unitFr: "L'activite tectonique et les structures geologiques associees",
    chapterNumero: 4, chapterAr: "تشكل السلاسل الجبلية", chapterFr: "Formation des chaines de montagnes",
    chapterType: "concept", chapterImportance: "haute",
    scenarioId: "subduction-collision-ridge-v1",
    focusAr: "التركيز المنهجي: تحليل البنيات الجيولوجية المميزة للسلاسل الجبلية (الطيور، الفوالق، الأفيوليت).",
    recommendedVerbs: ["analyse", "interpret", "compare", "relationship"],
  },
  {
    slug: "d3-u3-c5-disparition-de-la-plaque-oceanique-et-phenomenes-lies-a-la-subduction",
    domainNumero: 3, domainAr: "ديناميكية الكرة الأرضية", domainFr: "Dynamique du globe terrestre",
    unitNumero: 3, unitAr: "النشاط التكتوني والبنيات الجيولوجية المرتبطة به", unitFr: "L'activite tectonique et les structures geologiques associees",
    chapterNumero: 5, chapterAr: "اختفاء الصفيحة المحيطية والظواهر المرتبطة بالاندساس", chapterFr: "Disparition de la plaque oceanique et phenomenes lies a la subduction",
    chapterType: "synthese", chapterImportance: "critique",
    scenarioId: "subduction-collision-ridge-v1",
    focusAr: "التركيز المنهجي: ربط جميع العناصر (توسع، اندساس، تصادم) في نص علمي متكامل حول ديناميكية الأرض.",
    recommendedVerbs: ["scientific-text", "compare", "relationship", "deduce"],
  },
]

export function getMethodologyChapterLink(slug: string) {
  return methodologyChapterLinks.find((chapter) => chapter.slug === slug)
}

export function getMethodologyChaptersByScenario(scenarioId: string) {
  return methodologyChapterLinks.filter((chapter) => chapter.scenarioId === scenarioId)
}

export function getMethodologyChaptersByUnit(unitFr: string) {
  return methodologyChapterLinks.filter((chapter) => chapter.unitFr === unitFr)
}

export type UnitConfig = {
  slug: string
  unitAr: string
  unitFr: string
  domainNumero: number
  domainAr: string
  scenarioId: string
  emoji: string
  chapters: typeof methodologyChapterLinks
}

export const UNITS_CONFIG: UnitConfig[] = [
  {
    slug: "synthese-proteines",
    unitAr: "تركيب البروتين",
    unitFr: "Synthese des proteines",
    domainNumero: 1,
    domainAr: "التخصص الوظيفي للبروتينات",
    scenarioId: "gene-expression-protein-disorder-v1",
    emoji: "🧬",
    chapters: [],
  },
  {
    slug: "relation-structure-fonction",
    unitAr: "العلاقة بين بنية ووظيفة البروتين",
    unitFr: "Relation entre structure et fonction des proteines",
    domainNumero: 1,
    domainAr: "التخصص الوظيفي للبروتينات",
    scenarioId: "protein-structure-function-v1",
    emoji: "🔬",
    chapters: [],
  },
  {
    slug: "activite-enzymatique",
    unitAr: "النشاط الإنزيمي للبروتينات",
    unitFr: "L'activite enzymatique des proteines",
    domainNumero: 1,
    domainAr: "التخصص الوظيفي للبروتينات",
    scenarioId: "enzyme-activity-v1",
    emoji: "⚡",
    chapters: [],
  },
  {
    slug: "defense-soi",
    unitAr: "دور البروتينات في الدفاع عن الذات",
    unitFr: "Role des proteines dans la defense de soi",
    domainNumero: 1,
    domainAr: "التخصص الوظيفي للبروتينات",
    scenarioId: "immunity-defense-v1",
    emoji: "🛡️",
    chapters: [],
  },
  {
    slug: "communication-nerveuse",
    unitAr: "دور البروتينات في الاتصال العصبي",
    unitFr: "Role des proteines dans la communication nerveuse",
    domainNumero: 1,
    domainAr: "التخصص الوظيفي للبروتينات",
    scenarioId: "nervous-communication-v1",
    emoji: "🧠",
    chapters: [],
  },
  {
    slug: "photosynthese",
    unitAr: "آليات تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة",
    unitFr: "Mecanismes de conversion de l'energie lumineuse en energie chimique potentielle",
    domainNumero: 2,
    domainAr: "تحويل الطاقة",
    scenarioId: "photosynthesis-v1",
    emoji: "☀️",
    chapters: [],
  },
  {
    slug: "respiration-cellulaire",
    unitAr: "آليات تحويل الطاقة الكيميائية الكامنة في الجزيئات العضوية إلى ATP",
    unitFr: "Mecanismes de conversion de l'energie chimique potentielle des molecules organiques en ATP",
    domainNumero: 2,
    domainAr: "تحويل الطاقة",
    scenarioId: "cellular-respiration-v1",
    emoji: "⚡",
    chapters: [],
  },
  {
    slug: "ultrastructural-energie",
    unitAr: "تحويل الطاقة على المستوى ما فوق البنية الخلوية",
    unitFr: "Conversion de l'energie au niveau ultrastructural cellulaire",
    domainNumero: 2,
    domainAr: "تحويل الطاقة",
    scenarioId: "ultrastructural-energy-v1",
    emoji: "🔋",
    chapters: [],
  },
  {
    slug: "tectonique-plaques",
    unitAr: "النشاط التكتوني للصفائح",
    unitFr: "L'activite tectonique des plaques",
    domainNumero: 3,
    domainAr: "ديناميكية الكرة الأرضية",
    scenarioId: "tectonics-general-v1",
    emoji: "🌋",
    chapters: [],
  },
  {
    slug: "structure-globe",
    unitAr: "بنية الكرة الأرضية",
    unitFr: "Structure du globe terrestre",
    domainNumero: 3,
    domainAr: "ديناميكية الكرة الأرضية",
    scenarioId: "earth-structure-v1",
    emoji: "🌍",
    chapters: [],
  },
  {
    slug: "subduction-collision",
    unitAr: "النشاط التكتوني والبنيات الجيولوجية المرتبطة به",
    unitFr: "L'activite tectonique et les structures geologiques associees",
    domainNumero: 3,
    domainAr: "ديناميكية الكرة الأرضية",
    scenarioId: "subduction-collision-ridge-v1",
    emoji: "🏔️",
    chapters: [],
  },
]

// Populate chapters for each unit config
UNITS_CONFIG.forEach((unit) => {
  unit.chapters = methodologyChapterLinks.filter((ch) => ch.unitFr === unit.unitFr)
})

export function getUnitConfig(slug: string) {
  return UNITS_CONFIG.find((unit) => unit.slug === slug)
}

export function getUnitConfigByUnitAr(unitAr: string) {
  return UNITS_CONFIG.find((unit) => unit.unitAr === unitAr)
}

export function getUnitsByDomain(domainNumero: number) {
  return UNITS_CONFIG.filter((unit) => unit.domainNumero === domainNumero)
}
