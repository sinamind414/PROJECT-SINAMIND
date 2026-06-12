/* ============================================
   PROGRAM DATA - Programme National Algérien
   3ème AS Sciences Expérimentales - SVT
   ============================================ */

const PROGRAM = {
  meta: {
    title: 'علوم الطبيعة والحياة',
    titleFr: 'Sciences de la Vie et de la Terre',
    level: 'الثالثة ثانوي - علوم تجريبية',
    levelFr: '3ème Année Secondaire - Sciences Expérimentales',
    totalDomains: 3,
    totalUnits: 11,
    totalChapters: 50
  },
  
  domains: [
    {
      id: 'domain-1',
      number: 1,
      titleAr: 'التخصص الوظيفي للبروتينات',
      titleFr: 'La Spécialisation Fonctionnelle des Protéines',
      icon: '🧬',
      color: '#A78BFA',
      gradient: 'linear-gradient(135deg, #A78BFA, #7C5FCD)',
      description: 'دراسة البروتينات من تركيبها إلى دورها في المناعة والاتصال العصبي',
      descriptionFr: 'Étude des protéines de leur synthèse à leur rôle dans l\'immunité et la communication nerveuse',
      unitsCount: 5,
      chaptersCount: 30,
      units: [
        {
          id: 'unit-1-1',
          number: 1,
          titleAr: 'تركيب البروتين',
          titleFr: 'Synthèse des Protéines',
          icon: '✍️',
          startPage: 10,
          chapters: [
            { id: 'ch-1-1-1', num: 1, titleAr: 'تذكير بالمكتسبات', titleFr: 'Rappel des acquis', page: 11 },
            { id: 'ch-1-1-2', num: 2, titleAr: 'مقر تركيب البروتين', titleFr: 'Siège de la synthèse', page: 12 },
            { id: 'ch-1-1-3', num: 3, titleAr: 'استنساخ المعلومات الوراثية', titleFr: 'Transcription de l\'ADN', page: 16 },
            { id: 'ch-1-1-4', num: 4, titleAr: 'الترجمة', titleFr: 'La traduction', page: 20 },
            { id: 'ch-1-1-5', num: 5, titleAr: 'مراحل الترجمة', titleFr: 'Les étapes de la traduction', page: 24 }
          ]
        },
        {
          id: 'unit-1-2',
          number: 2,
          titleAr: 'العلاقة بين بنية ووظيفة البروتين',
          titleFr: 'Relation Structure-Fonction des Protéines',
          icon: '🔬',
          startPage: 39,
          chapters: [
            { id: 'ch-1-2-1', num: 1, titleAr: 'تمثيل البنية الفراغية للبروتين', titleFr: 'Représentation 3D de la protéine', page: 40 },
            { id: 'ch-1-2-2', num: 2, titleAr: 'مستويات البنية الفراغية', titleFr: 'Niveaux de structure spatiale', page: 42 },
            { id: 'ch-1-2-3', num: 3, titleAr: 'العلاقة بنية ووظيفة', titleFr: 'Relation structure-fonction', page: 46 }
          ]
        },
        {
          id: 'unit-1-3',
          number: 3,
          titleAr: 'النشاط الإنزيمي للبروتينات',
          titleFr: 'L\'Activité Enzymatique',
          icon: '⚗️',
          startPage: 57,
          chapters: [
            { id: 'ch-1-3-1', num: 1, titleAr: 'مفهوم الإنزيم وأهميته', titleFr: 'Notion d\'enzyme et importance', page: 58 },
            { id: 'ch-1-3-2', num: 2, titleAr: 'النشاط الإنزيمي والبنية', titleFr: 'Activité et structure de l\'enzyme', page: 60 },
            { id: 'ch-1-3-3', num: 3, titleAr: 'تأثير pH على نشاط الإنزيم', titleFr: 'Influence du pH', page: 67 },
            { id: 'ch-1-3-4', num: 4, titleAr: 'تأثير الحرارة على نشاط الإنزيم', titleFr: 'Influence de la température', page: 68 }
          ]
        },
        {
          id: 'unit-1-4',
          number: 4,
          titleAr: 'دور البروتينات في الدفاع عن الذات',
          titleFr: 'Rôle des Protéines dans la Défense de Soi',
          icon: '🛡️',
          startPage: 73,
          chapters: [
            { id: 'ch-1-4-1', num: 1, titleAr: 'تذكير بالمكتسبات', titleFr: 'Rappel des acquis', page: 74 },
            { id: 'ch-1-4-2', num: 2, titleAr: 'الذات واللاذات', titleFr: 'Le soi et le non-soi', page: 76 },
            { id: 'ch-1-4-3', num: 3, titleAr: 'الجزيئات الدفاعية (الحالة الأولى)', titleFr: 'Molécules de défense immunité non spécifique', page: 85 },
            { id: 'ch-1-4-4', num: 4, titleAr: 'المعقد المناعي', titleFr: 'Le complexe immun', page: 87 },
            { id: 'ch-1-4-5', num: 5, titleAr: 'مصدر الأجسام المضادة', titleFr: 'Origine des anticorps', page: 92 },
            { id: 'ch-1-4-6', num: 6, titleAr: 'العناصر الدفاعية (الحالة الثانية)', titleFr: 'Éléments de défense immunité spécifique', page: 97 },
            { id: 'ch-1-4-7', num: 7, titleAr: 'طرق تأثير اللمفاويات LTc', titleFr: 'Modes d\'action des LTc', page: 98 },
            { id: 'ch-1-4-8', num: 8, titleAr: 'مصدر اللمفاويات LTc', titleFr: 'Origine des LTc', page: 100 },
            { id: 'ch-1-4-9', num: 9, titleAr: 'تحفيز الخلايا LB و LT', titleFr: 'Activation des LB et LT', page: 103 },
            { id: 'ch-1-4-10', num: 10, titleAr: 'اختيار نمط الاستجابة المناعية', titleFr: 'Choix du type de réponse immunitaire', page: 105 },
            { id: 'ch-1-4-11', num: 11, titleAr: 'فقدان المناعة المكتسبة (SIDA)', titleFr: 'Perte de l\'immunité acquise SIDA', page: 108 }
          ]
        },
        {
          id: 'unit-1-5',
          number: 5,
          titleAr: 'دور البروتينات في الاتصال العصبي',
          titleFr: 'Rôle des Protéines dans la Communication Nerveuse',
          icon: '⚡',
          startPage: 127,
          chapters: [
            { id: 'ch-1-5-1', num: 1, titleAr: 'تذكير بالمكتسبات', titleFr: 'Rappel des acquis', page: 128 },
            { id: 'ch-1-5-2', num: 2, titleAr: 'النقل المشبكي (الكمون الغشائي)', titleFr: 'Transmission synaptique', page: 130 },
            { id: 'ch-1-5-3', num: 3, titleAr: 'آلية النقل المشبكي', titleFr: 'Mécanisme de transmission synaptique', page: 132 },
            { id: 'ch-1-5-4', num: 4, titleAr: 'كمون الراحة', titleFr: 'Le potentiel de repos', page: 136 },
            { id: 'ch-1-5-5', num: 5, titleAr: 'كمون العمل', titleFr: 'Le potentiel d\'action', page: 140 },
            { id: 'ch-1-5-6', num: 6, titleAr: 'آلية الإدماج العصبي', titleFr: 'Mécanisme d\'intégration nerveuse', page: 148 },
            { id: 'ch-1-5-7', num: 7, titleAr: 'تأثير المخدرات على المشابك', titleFr: 'Effet des drogues sur les synapses', page: 154 }
          ]
        }
      ]
    },
    
    {
      id: 'domain-2',
      number: 2,
      titleAr: 'التحولات الطاقوية',
      titleFr: 'Les Transformations Énergétiques',
      icon: '⚡',
      color: '#FB7185',
      gradient: 'linear-gradient(135deg, #FB7185, #E11D48)',
      description: 'من الطاقة الضوئية إلى ATP - دراسة الأيض الخلوي',
      descriptionFr: 'De l\'énergie lumineuse à l\'ATP - étude du métabolisme cellulaire',
      unitsCount: 3,
      chaptersCount: 11,
      units: [
        {
          id: 'unit-2-1',
          number: 1,
          titleAr: 'تحويل الطاقة الضوئية إلى طاقة كيميائية',
          titleFr: 'Conversion de l\'Énergie Lumineuse en Énergie Chimique',
          icon: '☀️',
          startPage: 174,
          chapters: [
            { id: 'ch-2-1-1', num: 1, titleAr: 'تذكير بالمكتسبات - التركيب الضوئي', titleFr: 'Rappel photosynthèse', page: 175 },
            { id: 'ch-2-1-2', num: 2, titleAr: 'مقر التركيب الضوئي - الصانعة الخضراء', titleFr: 'Siège chloroplaste', page: 177 },
            { id: 'ch-2-1-3', num: 3, titleAr: 'المرحلة الكيموضوئية', titleFr: 'Phase photochimique claire', page: 180 },
            { id: 'ch-2-1-4', num: 4, titleAr: 'المرحلة الكيموحيوية (حلقة كالفن)', titleFr: 'Phase chimique cycle de Calvin', page: 192 }
          ]
        },
        {
          id: 'unit-2-2',
          number: 2,
          titleAr: 'تحويل الطاقة الكيميائية إلى ATP',
          titleFr: 'Conversion de l\'Énergie Chimique en ATP',
          icon: '🔋',
          startPage: 205,
          chapters: [
            { id: 'ch-2-2-1', num: 1, titleAr: 'تذكير بالمكتسبات', titleFr: 'Rappel des acquis', page: 206 },
            { id: 'ch-2-2-2', num: 2, titleAr: 'مقر الأكسدة التنفسية', titleFr: 'Siège de l\'oxydation respiratoire', page: 207 },
            { id: 'ch-2-2-3', num: 3, titleAr: 'التحلل السكري', titleFr: 'La glycolyse', page: 210 },
            { id: 'ch-2-2-4', num: 4, titleAr: 'حلقة كريبس', titleFr: 'Cycle de Krebs', page: 213 },
            { id: 'ch-2-2-5', num: 5, titleAr: 'الفسفرة التأكسدية', titleFr: 'Phosphorylation oxydative', page: 215 },
            { id: 'ch-2-2-6', num: 6, titleAr: 'التخمر (وسط لا هوائي)', titleFr: 'Fermentation anaérobie', page: 218 }
          ]
        },
        {
          id: 'unit-2-3',
          number: 3,
          titleAr: 'تحويل الطاقة على المستوى الخلوي',
          titleFr: 'Conversion de l\'Énergie au Niveau Cellulaire',
          icon: '🔬',
          startPage: 227,
          chapters: [
            { id: 'ch-2-3-1', num: 1, titleAr: 'التحولات الطاقوية على المستوى الخلوي', titleFr: 'Transformations énergétiques cellulaires', page: 228 }
          ]
        }
      ]
    },
    
    {
      id: 'domain-3',
      number: 3,
      titleAr: 'التكتونية العامة',
      titleFr: 'La Tectonique Globale',
      icon: '🌍',
      color: '#60A5FA',
      gradient: 'linear-gradient(135deg, #60A5FA, #2563EB)',
      description: 'دراسة حركات الصفائح وبنية الأرض الداخلية',
      descriptionFr: 'Étude des mouvements des plaques et structure interne de la Terre',
      unitsCount: 3,
      chaptersCount: 14,
      units: [
        {
          id: 'unit-3-1',
          number: 1,
          titleAr: 'النشاط التكتوني للصفائح',
          titleFr: 'L\'Activité Tectonique des Plaques',
          icon: '🗺️',
          startPage: 237,
          chapters: [
            { id: 'ch-3-1-1', num: 1, titleAr: 'تحديد الصفائح التكتونية', titleFr: 'Identification des plaques', page: 238 },
            { id: 'ch-3-1-2', num: 2, titleAr: 'حركات الصفائح التكتونية', titleFr: 'Mouvements des plaques', page: 240 },
            { id: 'ch-3-1-3', num: 3, titleAr: 'الطاقة الداخلية للكرة الأرضية', titleFr: 'Énergie interne du globe', page: 248 }
          ]
        },
        {
          id: 'unit-3-2',
          number: 2,
          titleAr: 'بنية الكرة الأرضية',
          titleFr: 'Structure du Globe Terrestre',
          icon: '🌐',
          startPage: 259,
          chapters: [
            { id: 'ch-3-2-1', num: 1, titleAr: 'الموجات الزلزالية', titleFr: 'Les ondes sismiques', page: 260 },
            { id: 'ch-3-2-2', num: 2, titleAr: 'التركيب الكيميائي للقشرة والمعطف', titleFr: 'Composition chimique croûte et manteau', page: 266 },
            { id: 'ch-3-2-3', num: 3, titleAr: 'نمذجة البنية الداخلية', titleFr: 'Modélisation de la structure interne', page: 274 }
          ]
        },
        {
          id: 'unit-3-3',
          number: 3,
          titleAr: 'النشاط التكتوني والبنيات الجيولوجية',
          titleFr: 'Activité Tectonique et Structures Géologiques',
          icon: '⛰️',
          startPage: 287,
          chapters: [
            { id: 'ch-3-3-1', num: 1, titleAr: 'ظواهر البناء (الظهرات وسط محيطية)', titleFr: 'Phénomènes de construction dorsales', page: 288 },
            { id: 'ch-3-3-2', num: 2, titleAr: 'المغماتية وتشكل اللوح المحيطي', titleFr: 'Magmatisme et formation plaque océanique', page: 290 },
            { id: 'ch-3-3-3', num: 3, titleAr: 'صخور الظهرة وسط محيطية', titleFr: 'Roches de la dorsale médio-océanique', page: 294 },
            { id: 'ch-3-3-4', num: 4, titleAr: 'الظواهر المرتبطة بالغوص', titleFr: 'Phénomènes liés à la subduction', page: 302 },
            { id: 'ch-3-3-5', num: 5, titleAr: 'اختفاء اللوح المحيطي', titleFr: 'Disparition de la plaque océanique', page: 307 },
            { id: 'ch-3-3-6', num: 6, titleAr: 'التضاريس الناجمة عن التصادم', titleFr: 'Reliefs de collision', page: 316 },
            { id: 'ch-3-3-7', num: 7, titleAr: 'شواهد التقلص', titleFr: 'Indices du raccourcissement', page: 319 },
            { id: 'ch-3-3-8', num: 8, titleAr: 'شواهد محيط قديم (الأوفيوليت)', titleFr: 'Indices d\'un ancien océan ophiolites', page: 323 }
          ]
        }
      ]
    }
  ],
  
  getDomainById(id) {
    return this.domains.find(d => d.id === id);
  },
  
  getUnitById(unitId) {
    for (const domain of this.domains) {
      const unit = domain.units.find(u => u.id === unitId);
      if (unit) return { unit, domain };
    }
    return null;
  },
  
  getChapterById(chapterId) {
    for (const domain of this.domains) {
      for (const unit of domain.units) {
        const chapter = unit.chapters.find(c => c.id === chapterId);
        if (chapter) return { chapter, unit, domain };
      }
    }
    return null;
  },
  
  getTotalChapters() {
    return this.domains.reduce((total, d) => 
      total + d.units.reduce((sum, u) => sum + u.chapters.length, 0), 0);
  }
};

if (typeof window !== 'undefined') window.PROGRAM = PROGRAM;
