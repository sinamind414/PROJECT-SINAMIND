/* ============================================
   BANQUE COMPLÈTE DE QUESTIONS BAC SVT
   50+ Questions organisées par domaine
   ============================================ */

const BACQuestions = {

  questions: [

    // ═══════════════════════════════════════
    // DOMAINE 1 : PROTÉINES (28 questions)
    // ═══════════════════════════════════════

    // --- Unité 1.1 : Synthèse des protéines ---
    {
      id: 1,
      domain: 'proteines',
      unit: 'تركيب البروتين',
      topic: 'الاستنساخ',
      difficulty: 'easy',
      type: 'definition',
      question: 'عرّف عملية الاستنساخ (Transcription) وحدد مقرها والإنزيم المسؤول عنها.',
      modelAnswer: 'الاستنساخ هو عملية نسخ المعلومة الوراثية المحمولة على أحد خيطي ADN (الخيط القالب) إلى جزيئة ARNm. يتم في النواة عند حقيقيات النواة بواسطة إنزيم ARN polymérase.',
      keyWords: ['الاستنساخ', 'نسخ المعلومة', 'ADN', 'ARNm', 'النواة', 'ARN polymérase', 'الخيط القالب'],
      points: 3,
      year: 'BAC 2019',
      hint: 'لا تنسَ ذكر الخيط القالب واتجاه القراءة'
    },
    {
      id: 2,
      domain: 'proteines',
      unit: 'تركيب البروتين',
      topic: 'الاستنساخ',
      difficulty: 'medium',
      type: 'analyse',
      question: 'إذا كان تتابع الخيط القالب لـ ADN هو: 3\'-TACGGATCA-5\'، أعطِ تتابع ARNm الناتج مع التعليل.',
      modelAnswer: 'نطبق قاعدة التكامل مع استبدال T بـ U:\nخيط ADN القالب: 3\'-T A C G G A T C A-5\'\nARNm الناتج:       5\'-A U G C C U A G U-3\'\n\nالتعليل: ARN polymérase يقرأ الخيط القالب من 3\' إلى 5\' ويبني ARNm من 5\' إلى 3\' وفق قاعدة التكامل: A↔U, T↔A, G↔C, C↔G.',
      keyWords: ['قاعدة التكامل', 'U بدل T', '3\' إلى 5\'', '5\' إلى 3\''],
      points: 4,
      year: 'BAC 2020'
    },
    {
      id: 3,
      domain: 'proteines',
      unit: 'تركيب البروتين',
      topic: 'النضج',
      difficulty: 'medium',
      type: 'explication',
      question: 'وضّح مراحل نضج ARN pré-messager عند حقيقيات النواة.',
      modelAnswer: 'يخضع ARN pré-messager لثلاث معالجات قبل خروجه من النواة:\n1) إضافة الغطاء (Cap): إضافة 7-méthylguanosine في الطرف 5\' لحماية ARNm.\n2) إضافة ذيل Poly-A: إضافة ~200 نيوكليوتيد A في الطرف 3\' لزيادة الاستقرار.\n3) الإلصاق (Épissage): حذف القطع غير الدالة (Introns) والإبقاء على القطع الدالة (Exons) بواسطة مركب Spliceosome.',
      keyWords: ['Cap', 'Poly-A', 'Épissage', 'Introns', 'Exons', 'Spliceosome', 'نضج'],
      points: 5,
      year: 'BAC 2021'
    },
    {
      id: 4,
      domain: 'proteines',
      unit: 'تركيب البروتين',
      topic: 'الترجمة',
      difficulty: 'easy',
      type: 'definition',
      question: 'حدد رامزة الانطلاق ورامزات التوقف في الشفرة الوراثية.',
      modelAnswer: 'رامزة الانطلاق: AUG وتشفر للحمض الأميني الميثيونين (Met). تحدد بداية الترجمة.\nرامزات التوقف: UAA, UAG, UGA. لا تشفر لأي حمض أميني وتحدد نهاية الترجمة.',
      keyWords: ['AUG', 'Met', 'الانطلاق', 'UAA', 'UAG', 'UGA', 'التوقف'],
      points: 3,
      year: 'BAC 2018'
    },
    {
      id: 5,
      domain: 'proteines',
      unit: 'تركيب البروتين',
      topic: 'الترجمة',
      difficulty: 'medium',
      type: 'application',
      question: 'ترجم تتابع ARNm التالي إلى سلسلة ببتيدية: 5\'-AUGGCUUACAAGUAA-3\'',
      modelAnswer: 'نقرأ الرامزات من 5\' إلى 3\':\nAUG = Met (انطلاق)\nGCU = Ala\nUAC = Tyr\nAAG = Lys\nUAA = STOP\n\nالسلسلة الببتيدية: Met-Ala-Tyr-Lys (4 أحماض أمينية)',
      keyWords: ['AUG', 'Met', 'رامزة', 'ترجمة', 'سلسلة ببتيدية'],
      points: 4,
      year: 'BAC 2022'
    },
    {
      id: 6,
      domain: 'proteines',
      unit: 'تركيب البروتين',
      topic: 'الشفرة الوراثية',
      difficulty: 'medium',
      type: 'explication',
      question: 'اذكر خصائص الشفرة الوراثية الأربع مع شرح مختصر لكل خاصية.',
      modelAnswer: '1) عالمية (Universelle): نفس الشفرة عند جميع الكائنات الحية.\n2) تنكسية (Dégénérée): عدة رامزات يمكنها تشفير نفس الحمض الأميني (مثلاً: Leu له 6 رامزات).\n3) غير متراكبة (Non chevauchante): كل نيوكليوتيد ينتمي لرامزة واحدة فقط.\n4) محددة (Univoque): كل رامزة تشفر لحمض أميني واحد فقط (لا غموض).',
      keyWords: ['عالمية', 'تنكسية', 'غير متراكبة', 'محددة'],
      points: 4,
      year: 'BAC 2019'
    },
    {
      id: 7,
      domain: 'proteines',
      unit: 'تركيب البروتين',
      topic: 'الترجمة',
      difficulty: 'hard',
      type: 'comparaison',
      question: 'قارن بين عملية الاستنساخ والترجمة في جدول يتضمن: المقر، القالب، الإنزيم، المنتج، الطاقة.',
      modelAnswer: 'المقارنة:\nالمقر: الاستنساخ في النواة | الترجمة في الهيولى (الريبوزومات)\nالقالب: خيط ADN (3\'→5\') | ARNm (5\'→3\')\nالإنزيم: ARN polymérase | Peptidyl transférase\nالمنتج: ARNm | سلسلة ببتيدية (بروتين)\nالطاقة: ATP | GTP\nالإشارة: Promoteur → Terminateur | AUG → UAA/UAG/UGA',
      keyWords: ['النواة', 'الهيولى', 'ARN polymérase', 'Peptidyl transférase', 'ATP', 'GTP'],
      points: 6,
      year: 'BAC 2023'
    },

    // --- Unité 1.2 : Structure-Fonction ---
    {
      id: 8,
      domain: 'proteines',
      unit: 'بنية ووظيفة البروتين',
      topic: 'مستويات البنية',
      difficulty: 'medium',
      type: 'explication',
      question: 'صف المستويات الأربعة للبنية الفراغية للبروتين مع ذكر نوع الروابط في كل مستوى.',
      modelAnswer: 'I. البنية الأولية: تتابع الأحماض الأمينية. الروابط: ببتيدية (تساهمية).\nII. البنية الثانوية: طي محلي (حلزون α + صفائح β). الروابط: هيدروجينية.\nIII. البنية الثالثية: طي ثلاثي الأبعاد الكامل. الروابط: هيدروجينية + أيونية + كارهة للماء + كبريتية (S-S).\nIV. البنية الرباعية: تجمع عدة سلاسل ببتيدية. الروابط: كل الأنواع السابقة.',
      keyWords: ['أولية', 'ثانوية', 'ثالثية', 'رباعية', 'حلزون α', 'صفائح β', 'كبريتية'],
      points: 6,
      year: 'BAC 2020'
    },
    {
      id: 9,
      domain: 'proteines',
      unit: 'بنية ووظيفة البروتين',
      topic: 'فقر الدم المنجلي',
      difficulty: 'hard',
      type: 'analyse',
      question: 'حلّل حالة فقر الدم المنجلي (Drépanocytose) لإثبات العلاقة بين بنية البروتين ووظيفته.',
      modelAnswer: 'في فقر الدم المنجلي:\n- طفرة نقطية في ADN: CTC → CAC\n- تغير على ARNm: GAG → GUG\n- تغير حمض أميني واحد في الموضع 6: Glu (محب للماء) → Val (كاره للماء)\n- Val الكارهة للماء تخلق منطقة لزجة على سطح الهيموغلوبين\n- جزيئات الهيموغلوبين تلتصق ببعضها وتشكل ألياف\n- الكريات الحمراء تأخذ شكلاً منجلياً بدل القرصي\n\nالاستنتاج: تغيير حمض أميني واحد → تغير البنية الفراغية → تغير الوظيفة → مرض.',
      keyWords: ['Glu', 'Val', 'كاره للماء', 'منجلي', 'طفرة نقطية', 'بنية', 'وظيفة'],
      points: 7,
      year: 'BAC 2021'
    },

    // --- Unité 1.3 : Enzymes ---
    {
      id: 10,
      domain: 'proteines',
      unit: 'النشاط الإنزيمي',
      topic: 'مفهوم الإنزيم',
      difficulty: 'easy',
      type: 'definition',
      question: 'عرّف الإنزيم واذكر 4 من خصائصه الأساسية.',
      modelAnswer: 'الإنزيم محفز حيوي ذو طبيعة بروتينية يسرع التفاعلات الكيميائية.\n\nالخصائص:\n1) طبيعة بروتينية\n2) لا يُستهلك في التفاعل\n3) نوعية مزدوجة (للركيزة وللتفاعل)\n4) يخفض طاقة التنشيط\n5) حساس للظروف (pH, T°)',
      keyWords: ['محفز حيوي', 'بروتينية', 'لا يُستهلك', 'نوعية مزدوجة', 'طاقة التنشيط'],
      points: 4,
      year: 'BAC 2018'
    },
    {
      id: 11,
      domain: 'proteines',
      unit: 'النشاط الإنزيمي',
      topic: 'نموذج القفل والمفتاح',
      difficulty: 'medium',
      type: 'comparaison',
      question: 'قارن بين نموذج القفل والمفتاح (Fischer) ونموذج التوافق المحدث (Koshland).',
      modelAnswer: 'نموذج القفل والمفتاح (Fischer 1894):\n- الموقع الفعال صلب وثابت الشكل\n- الركيزة تتطابق تماماً مع الموقع الفعال\n- لا يتغير شكل الإنزيم\n\nنموذج التوافق المحدث (Koshland 1958):\n- الموقع الفعال مرن وقابل للتكيف\n- الإنزيم يعدل شكله عند ارتباط الركيزة\n- مثل القفاز الذي يتشكل حول اليد\n- هذا النموذج المعتمد حالياً',
      keyWords: ['Fischer', 'Koshland', 'صلب', 'مرن', 'تكيف', 'الموقع الفعال'],
      points: 5,
      year: 'BAC 2020'
    },
    {
      id: 12,
      domain: 'proteines',
      unit: 'النشاط الإنزيمي',
      topic: 'تأثير pH',
      difficulty: 'medium',
      type: 'analyse',
      question: 'حلل منحنى النشاط الإنزيمي = f(pH) وفسر شكل الجرس.',
      modelAnswer: 'التحليل:\n- عند pH منخفض: نشاط ضعيف\n- عند pH الأمثل: نشاط أقصى\n- عند pH مرتفع: نشاط ينخفض\n- المنحنى على شكل جرس متماثل\n\nالتفسير:\n- عند pH الأمثل: تأين الأحماض الأمينية في الموقع الفعال مثالي للارتباط بالركيزة\n- عند تغير pH: تغير تأين الأحماض الأمينية → تغير شكل الموقع الفعال → فقدان النوعية',
      keyWords: ['pH أمثل', 'جرس', 'تأين', 'الموقع الفعال', 'نوعية'],
      points: 4,
      year: 'BAC 2019'
    },

    // --- Unité 1.4 : Immunité ---
    {
      id: 13,
      domain: 'proteines',
      unit: 'المناعة',
      topic: 'الذات واللاذات',
      difficulty: 'easy',
      type: 'definition',
      question: 'عرّف الذات واللاذات وحدد دور نظام HLA.',
      modelAnswer: 'الذات (Le Soi): مجموع الجزيئات الموجودة طبيعياً في الجسم والمقبولة من الجهاز المناعي.\nاللاذات (Le Non-Soi): كل جزيء غريب عن الجسم (بكتيريا, فيروسات, خلايا مزروعة...).\n\nنظام HLA (CMH): بروتينات سطحية على كل خلايا الجسم تعمل كبطاقة هوية بيولوجية. فريدة لكل شخص.',
      keyWords: ['الذات', 'اللاذات', 'HLA', 'CMH', 'بطاقة هوية'],
      points: 4,
      year: 'BAC 2022'
    },
    {
      id: 14,
      domain: 'proteines',
      unit: 'المناعة',
      topic: 'المناعة النوعية',
      difficulty: 'hard',
      type: 'synthese',
      question: 'اكتب نصاً علمياً تشرح فيه آلية الاستجابة المناعية الخلطية ضد بكتيريا خارج خلوية.',
      modelAnswer: 'عند دخول بكتيريا خارج خلوية:\n\n1) البالعات (CPA) تلتقط البكتيريا بالبلعمة، تهضمها، وتعرض شظايا Ag على سطحها مع CMH-II.\n\n2) LT4 تتعرف على معقد [Ag-CMH-II] عبر TCR + CD4 → تنشيط LT4 → إفراز IL-2.\n\n3) IL-2 تحفز LB المناسبة (التي تحمل BCR مكمل لـ Ag).\n\n4) LB تتكاثر (انتقاء نسيلي - Burnet) وتتمايز إلى:\n   - بلاسموسيتات: تنتج أجسام مضادة (~2000/ثانية)\n   - خلايا ذاكرة B: للاستجابة السريعة لاحقاً\n\n5) الأجسام المضادة تعمل بعدة طرق:\n   - التحييد: تحجب المواقع النشطة للبكتيريا\n   - التراص: تجمع البكتيريا في كتل\n   - الأوبسنة: تسهل البلعمة\n   - تفعيل المتممة: ثقب غشاء البكتيريا',
      keyWords: ['CPA', 'CMH-II', 'LT4', 'IL-2', 'LB', 'بلاسموسيتات', 'أجسام مضادة', 'انتقاء نسيلي', 'التحييد', 'التراص', 'الأوبسنة'],
      points: 8,
      year: 'BAC 2023'
    },
    {
      id: 15,
      domain: 'proteines',
      unit: 'المناعة',
      topic: 'LTc',
      difficulty: 'medium',
      type: 'explication',
      question: 'صف آلية قتل الخلايا المصابة بواسطة اللمفاويات LTc.',
      modelAnswer: 'آلية القتل:\n1) التعرف: LTc تتعرف على الخلية المصابة عبر TCR + CD8 الذي يرتبط بمعقد [Ag-CMH-I] على سطحها.\n\n2) القتل بآلية Perforine/Granzymes:\n   - LTc تفرز بروتين البرفورين الذي يثقب غشاء الخلية\n   - الجرانزيمات تدخل عبر الثقوب وتحفز الـ Apoptose\n   \n3) القتل بآلية Fas/FasL:\n   - FasL على سطح LTc يرتبط بـ Fas على الخلية المصابة\n   - يحفز Apoptose (موت مبرمج نظيف)\n\n4) النتيجة: الخلية تنكمش وتتفكك بدون التهاب. البالعات تنظف البقايا.',
      keyWords: ['TCR', 'CD8', 'CMH-I', 'البرفورين', 'الجرانزيمات', 'Apoptose', 'Fas', 'FasL'],
      points: 6,
      year: 'BAC 2021'
    },
    {
      id: 16,
      domain: 'proteines',
      unit: 'المناعة',
      topic: 'SIDA',
      difficulty: 'hard',
      type: 'explication',
      question: 'فسر لماذا يؤدي تدمير VIH لخلايا LT4 إلى انهيار الجهاز المناعي بأكمله.',
      modelAnswer: 'VIH يستهدف LT4 لأن بروتين gp120 الفيروسي يرتبط بمستقبل CD4 على سطحها.\n\nLT4 هي المنسق المركزي للاستجابة المناعية:\n\n1) بدون LT4، LB لا تنتج Ac بكفاءة → ضعف المناعة الخلطية.\n2) بدون LT4، LT8 لا تتمايز إلى LTc → ضعف المناعة الخلوية.\n3) الذاكرة المناعية تضعف.\n4) كل الاستجابات النوعية تنهار.\n\nالنتيجة: عدوى انتهازية (السل, الفطريات, السرطان...) → SIDA → الوفاة.',
      keyWords: ['gp120', 'CD4', 'LT4', 'المنسق', 'انهيار', 'عدوى انتهازية', 'SIDA'],
      points: 6,
      year: 'BAC 2022'
    },

    // --- Unité 1.5 : Communication nerveuse ---
    {
      id: 17,
      domain: 'proteines',
      unit: 'الاتصال العصبي',
      topic: 'كمون الراحة',
      difficulty: 'medium',
      type: 'explication',
      question: 'فسر أسباب كمون الراحة (-70 mV) في العصبون.',
      modelAnswer: 'كمون الراحة ≈ -70 mV (الداخل سالب) بسبب:\n\n1) التوزيع غير المتكافئ للأيونات:\n   - Na⁺: كثير خارجاً (150) / قليل داخلاً (15)\n   - K⁺: كثير داخلاً (150) / قليل خارجاً (5)\n   - بروتينات سالبة كثيرة داخلاً\n\n2) النفاذية الانتقائية: الغشاء أكثر نفاذية لـ K⁺ منه لـ Na⁺ في الراحة → K⁺ يخرج → الداخل يصبح أكثر سلبية.\n\n3) مضخة Na⁺/K⁺ ATPase: تُخرج 3 Na⁺ وتُدخل 2 K⁺ مقابل ATP → تحافظ على التوزيع.',
      keyWords: ['−70 mV', 'Na⁺', 'K⁺', 'نفاذية انتقائية', 'مضخة Na⁺/K⁺'],
      points: 5,
      year: 'BAC 2020'
    },
    {
      id: 18,
      domain: 'proteines',
      unit: 'الاتصال العصبي',
      topic: 'كمون العمل',
      difficulty: 'hard',
      type: 'analyse',
      question: 'ارسم منحنى كمون العمل وفسر كل مرحلة مع ذكر الأيونات المتدخلة.',
      modelAnswer: 'مراحل كمون العمل:\n\n1) زوال الاستقطاب (-70 → +30 mV):\n   - فتح قنوات Na⁺ الجهدية\n   - دخول Na⁺ بكميات كبيرة\n   - الكمون يرتفع بسرعة\n\n2) إعادة الاستقطاب (+30 → -70 mV):\n   - إغلاق قنوات Na⁺\n   - فتح قنوات K⁺ الجهدية\n   - خروج K⁺\n   - الكمون ينخفض\n\n3) فرط الاستقطاب (-70 → -80 mV):\n   - استمرار خروج K⁺ قليلاً\n   - ثم مضخة Na⁺/K⁺ تُعيد التوزيع\n\nقانون الكل أو لا شيء: PA ثابتة السعة (~100 mV). المعلومة مرمزة بالتواتر.',
      keyWords: ['زوال الاستقطاب', 'إعادة الاستقطاب', 'فرط', 'Na⁺', 'K⁺', 'قنوات جهدية', 'الكل أو لا شيء'],
      points: 7,
      year: 'BAC 2023'
    },
    {
      id: 19,
      domain: 'proteines',
      unit: 'الاتصال العصبي',
      topic: 'النقل المشبكي',
      difficulty: 'medium',
      type: 'explication',
      question: 'صف مراحل النقل المشبكي الست.',
      modelAnswer: '1) وصول كمون العمل إلى النهاية المشبكية.\n2) فتح قنوات Ca²⁺ الجهدية → دخول Ca²⁺.\n3) اندماج الحويصلات المشبكية مع الغشاء (بروتينات SNARE).\n4) إفراز الناقل العصبي في الشق المشبكي (Exocytose).\n5) ارتباط الناقل بمستقبلات نوعية → فتح قنوات أيونية → توليد PPS.\n6) إزالة الناقل: تحلل إنزيمي أو إعادة امتصاص.',
      keyWords: ['Ca²⁺', 'حويصلات', 'SNARE', 'Exocytose', 'ناقل عصبي', 'مستقبلات', 'PPS'],
      points: 5,
      year: 'BAC 2019'
    },
    {
      id: 20,
      domain: 'proteines',
      unit: 'الاتصال العصبي',
      topic: 'الإدماج العصبي',
      difficulty: 'hard',
      type: 'explication',
      question: 'فسر آلية الإدماج العصبي مع التمييز بين PPSE و PPSI والإدماج الزمني والمكاني.',
      modelAnswer: 'الإدماج العصبي: جمع الإشارات المتعددة الواردة على الجسم الخلوي.\n\nPPSE (مُنبه): فتح قنوات Na⁺ → زوال استقطاب محلي → يُقرّب من العتبة → يُسهّل PA.\nPPSI (مُثبط): فتح قنوات Cl⁻ أو K⁺ → فرط استقطاب → يُبعد عن العتبة → يمنع PA.\n\nالإدماج الزمني: تراكم إشارات من نفس المشبك بسرعة.\nالإدماج المكاني: تجميع إشارات من عدة مشابك مختلفة في نفس الوقت.\n\nتل المحور يقوم بالجمع الجبري: ∑PPSE - ∑PPSI. إذا تجاوز العتبة (-55 mV) → PA.',
      keyWords: ['PPSE', 'PPSI', 'زمني', 'مكاني', 'جمع جبري', 'تل المحور', 'العتبة'],
      points: 7,
      year: 'BAC 2022'
    },

    // --- Questions supplémentaires Protéines ---
    {
      id: 37,
      domain: 'proteines',
      unit: 'تركيب البروتين',
      topic: 'تجربة α-amanitine',
      difficulty: 'medium',
      type: 'analyse',
      question: 'حلّل نتائج تجربة إضافة α-amanitine على خلايا حية واستخلص الدليل على دور ARN polymérase.',
      modelAnswer: 'الملاحظات:\n- قبل الإضافة: تركيب ARN طبيعي ومنتظم\n- بعد إضافة α-amanitine: توقف فوري وكامل لتركيب ARN\n\nالتفسير:\nα-amanitine (مستخرج من فطر سام Amanite phalloïde) هي مثبط نوعي لإنزيم ARN polymérase. ترتبط بالإنزيم وتمنعه من العمل.\n\nالاستنتاج:\n- ARN polymérase ضروري للاستنساخ\n- الاستنساخ عملية أنزيمية (وليست تلقائية)\n- إيقاف الاستنساخ يؤدي تدريجياً لتوقف تركيب البروتين',
      keyWords: ['α-amanitine', 'مثبط نوعي', 'ARN polymérase', 'توقف فوري', 'عملية أنزيمية'],
      points: 5,
      year: 'BAC 2020'
    },
    {
      id: 38,
      domain: 'proteines',
      unit: 'تركيب البروتين',
      topic: 'تجربة Nirenberg',
      difficulty: 'medium',
      type: 'analyse',
      question: 'صف تجربة Nirenberg واشرح كيف ساهمت في فك الشفرة الوراثية.',
      modelAnswer: 'البروتوكول:\n1) صنع ARNm اصطناعي بسيط: Poly-U (UUUUUUUUU...)\n2) وضعه في وسط مع: ريبوزومات + 20 حمض أميني + ARNt + إنزيمات + ATP\n\nالملاحظة:\nتكوّن بروتين مكون من Phénylalanine (Phe) فقط: Phe-Phe-Phe...\n\nالاستنتاج:\nالرامزة UUU تشفر للحمض الأميني Phe\n\nالأهمية:\n- أول رمز يُفك في الشفرة الوراثية!\n- فتح الطريق لفك كل الـ 64 رامزة (1961-1966)\n- نوبل 1968',
      keyWords: ['Poly-U', 'UUU', 'Phe', 'أول رمز', 'فك الشفرة', 'Nobel'],
      points: 5,
      year: 'BAC 2019'
    },
    {
      id: 39,
      domain: 'proteines',
      unit: 'المناعة',
      topic: 'البلعمة',
      difficulty: 'medium',
      type: 'explication',
      question: 'صف مراحل البلعمة الخمس ووضح كيف تربط بين المناعتين الفطرية والمكتسبة.',
      modelAnswer: 'مراحل البلعمة:\n1) الانجذاب (Chimiotactisme): البالعة تتحرك نحو العامل الممرض.\n2) الالتصاق (Adhésion): البالعة تلتصق بسطح الجرثوم.\n3) الابتلاع (Ingestion): تكوين Phagosome بالأرجل الكاذبة.\n4) الهضم (Digestion): Phagosome + Lysosome → Phagolysosome → تحلل الجرثوم.\n5) الإخراج (Exocytose): طرد البقايا + عرض شظايا Ag على CMH-II.\n\nالربط بين المناعتين:\nالبالعة (Macrophage) تصبح CPA بعد عرض Ag على CMH-II → تحفز LT4 → بداية المناعة النوعية!\nالبالعة = جسر بين المناعة الفطرية والمكتسبة.',
      keyWords: ['انجذاب', 'التصاق', 'ابتلاع', 'Phagosome', 'هضم', 'CPA', 'CMH-II', 'جسر'],
      points: 6,
      year: 'BAC 2022'
    },
    {
      id: 44,
      domain: 'proteines',
      unit: 'تركيب البروتين',
      topic: 'البوليسوم',
      difficulty: 'medium',
      type: 'analyse',
      question: 'صف تجربة إضافة الريبونيوكلياز (RNase) على متعدد الريبوزوم واستخلص النتائج.',
      modelAnswer: 'البروتوكول:\n1) ملاحظة Polysome (عدة ريبوزومات مرتبطة) تحت المجهر الإلكتروني.\n2) إضافة RNase (إنزيم يحلل ARN فقط).\n\nالملاحظة:\nPolysome يتفكك → ريبوزومات منفردة (Monosomes)\n\nالتفسير:\nRNase دمر ARNm الذي كان يربط الريبوزومات معاً.\n\nالاستنتاجات:\n1) ARNm هو الرابط بين الريبوزومات في Polysome\n2) تدمير ARNm → تفكك Polysome → توقف الترجمة\n3) فائدة Polysome: إنتاج عدة نسخ من نفس البروتين بسرعة',
      keyWords: ['RNase', 'Polysome', 'Monosomes', 'ARNm الرابط', 'عدة نسخ'],
      points: 5,
      year: 'BAC 2019'
    },
    {
      id: 45,
      domain: 'proteines',
      unit: 'تركيب البروتين',
      topic: 'الثلاث أنواع ARN',
      difficulty: 'medium',
      type: 'comparaison',
      question: 'قارن بين أنواع ARN الثلاثة: ARNm, ARNt, ARNr.',
      modelAnswer: 'ARNm (الرسول):\n- حجم: متغير (300-15000 nt)\n- دور: قالب للترجمة\n- عمر: قصير (دقائق-ساعات)\n- نسبة: ~5%\n- ARN pol: II\n\nARNt (الناقل):\n- حجم: صغير (75-90 nt)\n- دور: نقل الأحماض الأمينية\n- شكل: ورقة برسيم / L\n- نسبة: ~15%\n- ARN pol: III\n\nARNr (الريبوزومي):\n- حجم: متنوع (120-5000 nt)\n- دور: بنية الريبوزوم\n- عمر: طويل (أيام-أسابيع)\n- نسبة: ~80% (الأكثر وفرة!)\n- ARN pol: I',
      keyWords: ['ARNm رسول', 'ARNt ناقل', 'ARNr ريبوزومي', 'Pol I', 'Pol II', 'Pol III', '80%'],
      points: 5,
      year: 'BAC 2021'
    },
    {
      id: 46,
      domain: 'proteines',
      unit: 'تركيب البروتين',
      topic: 'تنشيط AA',
      difficulty: 'medium',
      type: 'explication',
      question: 'صف آلية تنشيط الأحماض الأمينية وحدد دور إنزيم Aminoacyl-ARNt Synthétase.',
      modelAnswer: 'التنشيط يحدث في مرحلتين:\n\n1) تفعيل الحمض الأميني:\nAA + ATP → AA-AMP + 2 Pi\n\n2) نقل إلى ARNt:\nAA-AMP + ARNt → AA-ARNt + AMP\n\nالناتج: Aminoacyl-ARNt (جاهز للترجمة)\n\nإنزيم Aminoacyl-ARNt Synthétase:\n- 20 نوع مختلف (واحد لكل حمض أميني)\n- نوعية مزدوجة: يتعرف على AA محدد + ARNt مناسب\n- بعضها له وظيفة تصحيح (Proofreading)\n- معدل الخطأ: ~1/10,000\n\nأهمية التنشيط:\n1) تخزين الطاقة (لتكوين الرابطة الببتيدية لاحقاً)\n2) ضمان الدقة (الحمض الصحيح مع ARNt الصحيح)',
      keyWords: ['Aminoacyl-ARNt Synthétase', '20 نوع', 'ATP', 'AMP', 'نوعية مزدوجة', 'تصحيح'],
      points: 5,
      year: 'BAC 2020'
    },
    {
      id: 47,
      domain: 'proteines',
      unit: 'المناعة',
      topic: 'الزمر الدموية',
      difficulty: 'easy',
      type: 'application',
      question: 'شخص من الزمرة O يحتاج لنقل دم. من أي زمر يمكنه الاستقبال؟ علّل.',
      modelAnswer: 'الزمرة O تحتوي على:\n- Ag على الكريات: لا شيء\n- Ac في المصل: Anti-A + Anti-B\n\nلذلك:\n- يرفض زمرة A (بسبب Anti-A)\n- يرفض زمرة B (بسبب Anti-B)\n- يرفض زمرة AB (بسبب Anti-A و Anti-B)\n- يقبل فقط من O (لا Ag عليها)\n\nالاستنتاج: O يستقبل من O فقط.\nلكن O يُعطي للجميع (مُعطٍ عام) لأن كرياته بدون Ag.',
      keyWords: ['O', 'Anti-A', 'Anti-B', 'مُعطٍ عام', 'يستقبل من O'],
      points: 4,
      year: 'BAC 2018'
    },
    {
      id: 48,
      domain: 'proteines',
      unit: 'الاتصال العصبي',
      topic: 'المخدرات',
      difficulty: 'medium',
      type: 'explication',
      question: 'اشرح كيف يؤثر الكوكايين على مستوى المشابك العصبية.',
      modelAnswer: 'الكوكايين يعمل بمنع إعادة امتصاص الدوبامين:\n\n1) في الحالة الطبيعية: بعد إفراز الدوبامين في الشق المشبكي, يتم إعادة امتصاصه بسرعة بواسطة بروتين ناقل على العصبون قبل المشبكي.\n\n2) مع الكوكايين: يحجب بروتين إعادة الامتصاص → الدوبامين يتراكم في الشق المشبكي → تحفيز مطول لمستقبلات الدوبامين → نشوة قوية.\n\n3) العواقب:\n- تحفيز دارة المكافأة بشكل اصطناعي\n- الإدمان (الدماغ يربط الكوكايين بالمتعة)\n- التحمل (الحاجة لجرعات أكبر)\n- أعراض انسحاب مؤلمة',
      keyWords: ['إعادة الامتصاص', 'الدوبامين', 'تراكم', 'دارة المكافأة', 'إدمان'],
      points: 5,
      year: 'BAC 2021'
    },

    // ═══════════════════════════════════════
    // DOMAINE 2 : ÉNERGIE (10 questions)
    // ═══════════════════════════════════════

    {
      id: 21,
      domain: 'energie',
      unit: 'التركيب الضوئي',
      topic: 'المعادلة العامة',
      difficulty: 'easy',
      type: 'definition',
      question: 'اكتب المعادلة العامة للتركيب الضوئي وحدد الشروط اللازمة.',
      modelAnswer: 'المعادلة: 6 CO₂ + 6 H₂O → C₆H₁₂O₆ + 6 O₂ (في وجود الضوء والكلوروفيل)\n\nالشروط:\n- الضوء (مصدر الطاقة)\n- الكلوروفيل (الصبغة)\n- CO₂ (من الهواء عبر الثغور)\n- H₂O (من التربة عبر الجذور)\n- درجة حرارة مناسبة',
      keyWords: ['6 CO₂', '6 H₂O', 'C₆H₁₂O₆', '6 O₂', 'الضوء', 'الكلوروفيل'],
      points: 3,
      year: 'BAC 2018'
    },
    {
      id: 22,
      domain: 'energie',
      unit: 'التركيب الضوئي',
      topic: 'الصانعة الخضراء',
      difficulty: 'medium',
      type: 'explication',
      question: 'صف بنية الصانعة الخضراء وحدد مقر كل مرحلة من التركيب الضوئي.',
      modelAnswer: 'بنية الصانعة الخضراء:\n- غشاءان (خارجي وداخلي)\n- الستروما: سائل داخلي يحتوي على إنزيمات حلقة كالفن\n- الثايلاكويدات: أكياس غشائية تحتوي على الكلوروفيل\n- الغرانا: أكوام من الثايلاكويدات\n\nمقر المراحل:\n- المرحلة الكيموضوئية (Phase claire): على غشاء الثايلاكويدات\n- المرحلة الكيموحيوية (Cycle de Calvin): في الستروما',
      keyWords: ['ستروما', 'ثايلاكويدات', 'غرانا', 'كيموضوئية', 'كالفن'],
      points: 5,
      year: 'BAC 2020'
    },
    {
      id: 23,
      domain: 'energie',
      unit: 'التركيب الضوئي',
      topic: 'المرحلة الكيموضوئية',
      difficulty: 'hard',
      type: 'explication',
      question: 'صف تفاعلات المرحلة الكيموضوئية وحدد مصدر الأكسجين المنطلق.',
      modelAnswer: 'المرحلة الكيموضوئية تتم على غشاء الثايلاكويدات:\n\n1) الكلوروفيل في PSII تمتص الضوء → إثارة → فقدان إلكترون.\n2) التحلل الضوئي للماء: 2 H₂O → 4 H⁺ + 4 e⁻ + O₂ (تعويض الإلكترونات).\n3) الإلكترونات تنتقل عبر سلسلة النقل الإلكتروني → ضخ H⁺ نحو اللومن.\n4) PSI يمتص الضوء مرة ثانية → إلكترونات ذات طاقة عالية.\n5) إرجاع NADP⁺: NADP⁺ + 2 e⁻ + H⁺ → NADPH,H⁺.\n6) H⁺ يعود عبر ATP synthase → تركيب ATP.\n\nالأكسجين يأتي من تحلل الماء (وليس من CO₂!) أثبته Ruben و Kamen بـ ¹⁸O.',
      keyWords: ['PSII', 'PSI', 'تحلل ضوئي', 'O₂ من الماء', 'NADPH', 'ATP synthase', 'Ruben'],
      points: 7,
      year: 'BAC 2023'
    },
    {
      id: 24,
      domain: 'energie',
      unit: 'التركيب الضوئي',
      topic: 'دورة كالفن',
      difficulty: 'hard',
      type: 'explication',
      question: 'صف المراحل الثلاث لدورة كالفن وحدد دور إنزيم RuBisCO.',
      modelAnswer: 'دورة كالفن تتم في الستروما:\n\n1) التثبيت: CO₂ + RuBP (5C) → 2 APG (3C) بواسطة إنزيم RuBisCO.\n2) الإرجاع: APG + ATP + NADPH → G3P + ADP + NADP⁺.\n3) التجديد: 5 G3P من كل 6 تُستخدم لتجديد RuBP (تستهلك ATP).\n\n1 G3P من كل 6 يخرج من الدورة → 2 G3P = 1 غلوكوز.\n\nRuBisCO: أكثر بروتين وفرة على الأرض (~500 مليون طن). يثبت CO₂. بطيء (3 جزيئات/ثانية).\n\nحصيلة لغلوكوز واحد: 6 CO₂ + 18 ATP + 12 NADPH.',
      keyWords: ['التثبيت', 'الإرجاع', 'التجديد', 'RuBP', 'APG', 'G3P', 'RuBisCO'],
      points: 7,
      year: 'BAC 2022'
    },
    {
      id: 25,
      domain: 'energie',
      unit: 'التنفس الخلوي',
      topic: 'المعادلة والمقر',
      difficulty: 'easy',
      type: 'definition',
      question: 'اكتب المعادلة العامة للتنفس الخلوي وحدد مقر كل مرحلة.',
      modelAnswer: 'المعادلة: C₆H₁₂O₆ + 6 O₂ → 6 CO₂ + 6 H₂O + ~38 ATP\n\nمقر المراحل:\n1) التحلل السكري: الهيولى (لاهوائي)\n2) نزع الكربوكسيل: ماتريكس الميتوكوندري\n3) حلقة كريبس: ماتريكس الميتوكوندري\n4) الفسفرة التأكسدية: الغشاء الداخلي للميتوكوندري (الكريستا)',
      keyWords: ['C₆H₁₂O₆', '38 ATP', 'هيولى', 'ماتريكس', 'كريستا'],
      points: 4,
      year: 'BAC 2019'
    },
    {
      id: 26,
      domain: 'energie',
      unit: 'التنفس الخلوي',
      topic: 'التحلل السكري',
      difficulty: 'medium',
      type: 'explication',
      question: 'صف عملية التحلل السكري واحسب حصيلتها الطاقوية الصافية.',
      modelAnswer: 'التحلل السكري يتم في الهيولى وهو لاهوائي:\n\nالمراحل:\n1) مرحلة الاستثمار: الغلوكوز (6C) يُفسفر بـ 2 ATP → Fructose-1,6-bisphosphate.\n2) التفكك: Fructose-1,6-bisphosphate → 2 G3P (3C).\n3) مرحلة الإنتاج: كل G3P يُنتج 2 ATP + 1 NADH → 2 Pyruvate.\n\nالحصيلة الصافية:\n- الإنتاج: 4 ATP + 2 NADH\n- الاستهلاك: 2 ATP\n- الصافي: +2 ATP + 2 NADH + 2 Pyruvate',
      keyWords: ['لاهوائي', 'هيولى', 'G3P', 'Pyruvate', '2 ATP صافي', '2 NADH'],
      points: 5,
      year: 'BAC 2020'
    },
    {
      id: 27,
      domain: 'energie',
      unit: 'التنفس الخلوي',
      topic: 'الفسفرة التأكسدية',
      difficulty: 'hard',
      type: 'explication',
      question: 'صف آلية الفسفرة التأكسدية ووضح دور O₂ كمستقبل نهائي.',
      modelAnswer: 'الفسفرة التأكسدية تتم على الغشاء الداخلي (الكريستا):\n\n1) NADH و FADH₂ يُسلّمان إلكتروناتهما للسلسلة التنفسية (4 معقدات بروتينية).\n2) انتقال الإلكترونات يُحرر طاقة تُضخ H⁺ من الماتريكس إلى الفراغ بين الغشائي.\n3) تكوين تدرج بروتوني (Chimiosmose - Peter Mitchell).\n4) H⁺ تعود عبر ATP synthase → تركيب ATP.\n5) O₂ = المستقبل النهائي: ½ O₂ + 2 e⁻ + 2 H⁺ → H₂O.\n\nبدون O₂: السلسلة تتوقف → لا ATP → الموت.\n\nالإنتاجية: 1 NADH → ~3 ATP | 1 FADH₂ → ~2 ATP.',
      keyWords: ['سلسلة تنفسية', 'تدرج بروتوني', 'Chimiosmose', 'ATP synthase', 'O₂ مستقبل نهائي', 'H₂O'],
      points: 7,
      year: 'BAC 2023'
    },
    {
      id: 28,
      domain: 'energie',
      unit: 'التنفس الخلوي',
      topic: 'التخمر',
      difficulty: 'medium',
      type: 'comparaison',
      question: 'قارن بين التنفس الخلوي والتخمر من حيث: الأكسجين، المقر، المنتجات، إنتاج ATP.',
      modelAnswer: 'المقارنة:\n\nالأكسجين:\n- التنفس: يحتاج O₂ (هوائي)\n- التخمر: لا يحتاج O₂ (لاهوائي)\n\nالمقر:\n- التنفس: الهيولى + الميتوكوندري\n- التخمر: الهيولى فقط\n\nالمنتجات:\n- التنفس: CO₂ + H₂O\n- التخمر اللبني: حمض اللبن\n- التخمر الكحولي: إيثانول + CO₂\n\nإنتاج ATP:\n- التنفس: ~38 ATP (أكسدة كاملة)\n- التخمر: 2 ATP فقط (أكسدة جزئية)',
      keyWords: ['هوائي', 'لاهوائي', '38 ATP', '2 ATP', 'أكسدة كاملة', 'جزئية'],
      points: 6,
      year: 'BAC 2021'
    },
    {
      id: 29,
      domain: 'energie',
      unit: 'التحولات الطاقوية',
      topic: 'التكامل',
      difficulty: 'medium',
      type: 'explication',
      question: 'وضح التكامل بين التركيب الضوئي والتنفس الخلوي.',
      modelAnswer: 'التكامل:\n- التركيب الضوئي يأخذ CO₂ + H₂O ويُنتج Glucose + O₂.\n- التنفس الخلوي يأخذ Glucose + O₂ ويُنتج CO₂ + H₂O + ATP.\n\nنواتج إحداهما = متفاعلات الأخرى!\n\nالمادة تدور (CO₂, H₂O, O₂, Glucose) بينما الطاقة تتدفق (شمس → ATP → حرارة).\n\nATP هو العملة الطاقوية العالمية.',
      keyWords: ['تكامل', 'عكسيتان', 'المادة تدور', 'الطاقة تتدفق', 'ATP عالمي'],
      points: 5,
      year: 'BAC 2020'
    },
    {
      id: 49,
      domain: 'energie',
      unit: 'التركيب الضوئي',
      topic: 'الكلوروفيل',
      difficulty: 'easy',
      type: 'explication',
      question: 'فسر لماذا الأوراق خضراء وماذا يحدث في الخريف.',
      modelAnswer: 'الأوراق خضراء لأن:\n- الكلوروفيل تمتص الضوء الأحمر (~660 nm) والأزرق (~430 nm)\n- لا تمتص الضوء الأخضر → يُعكَس\n- الضوء المنعكس يصل لأعيننا → نرى الورقة خضراء\n\nفي الخريف:\n- برودة الجو → الكلوروفيل تتفكك\n- تظهر الصبغات الأخرى المخفية:\n  - الكاروتينات (أصفر, برتقالي)\n  - الأنثوسيانينات (أحمر)\n- هذا يفسر ألوان الخريف الجميلة!',
      keyWords: ['الكلوروفيل', 'تمتص الأحمر والأزرق', 'تعكس الأخضر', 'الخريف', 'الكاروتينات'],
      points: 3,
      year: 'BAC 2019'
    },

    // ═══════════════════════════════════════
    // DOMAINE 3 : GÉOLOGIE (12 questions)
    // ═══════════════════════════════════════

    {
      id: 30,
      domain: 'geologie',
      unit: 'الصفائح التكتونية',
      topic: 'تعريف',
      difficulty: 'easy',
      type: 'definition',
      question: 'عرّف الصفيحة التكتونية وميّز بين الغلاف الصخري والأستينوسفير.',
      modelAnswer: 'الصفيحة التكتونية: قطعة صلبة من الغلاف الصخري (Lithosphère) تطفو على الأستينوسفير اللزج. 12 صفيحة رئيسية.\n\nالغلاف الصخري (Lithosphère):\n- صلب\n- ~100 كم سمك\n- يحتوي على القشرة + الجزء العلوي للمعطف\n- مُجزأ إلى صفائح\n\nالأستينوسفير (Asthénosphère):\n- لزج وقابل للتشكل\n- ~200-300 كم سمك\n- يسمح للصفائح بالتحرك فوقه',
      keyWords: ['الغلاف الصخري', 'الأستينوسفير', 'صلب', 'لزج', '12 صفيحة'],
      points: 4,
      year: 'BAC 2019'
    },
    {
      id: 31,
      domain: 'geologie',
      unit: 'الصفائح التكتونية',
      topic: 'أنواع الحدود',
      difficulty: 'medium',
      type: 'comparaison',
      question: 'قارن بين الأنواع الثلاثة لحدود الصفائح التكتونية مع أمثلة.',
      modelAnswer: '1) تباعدية (Divergence) ⬅️➡️:\n   - الصفائح تبتعد\n   - ظهرات وسط محيطية\n   - بركانية بازلتية هادئة\n   - مثال: الظهرة وسط الأطلسي\n\n2) تقاربية (Convergence) ➡️⬅️:\n   - الصفائح تتقارب\n   - غوص أو تصادم\n   - بركانية أنديزيتية متفجرة\n   - مثال: الهيمالايا، الأنديز\n\n3) انزلاقية (Transformante) ↔️:\n   - الصفائح تنزلق جانبياً\n   - فوالق تحويلية\n   - لا بركانية عادة\n   - مثال: فالق سان أندرياس',
      keyWords: ['تباعدية', 'تقاربية', 'انزلاقية', 'ظهرة', 'غوص', 'تصادم'],
      points: 6,
      year: 'BAC 2021'
    },
    {
      id: 32,
      domain: 'geologie',
      unit: 'بنية الأرض',
      topic: 'الموجات الزلزالية',
      difficulty: 'medium',
      type: 'comparaison',
      question: 'قارن بين موجات P و S وبيّن كيف ساعدت في اكتشاف بنية الأرض.',
      modelAnswer: 'موجات P (Primaires):\n- طولية (ضغط)\n- الأسرع (~6-14 كم/ث)\n- تنتشر في كل الأوساط (صلبة, سائلة, غازية)\n\nموجات S (Secondaires):\n- مستعرضة (قص)\n- أبطأ (~3-8 كم/ث)\n- تنتشر فقط في الأوساط الصلبة\n\nالاكتشاف:\n- اختفاء موجات S عند عمق 2900 كم (Gutenberg) → النواة الخارجية سائلة!\n- زيادة سرعة P عند 5150 كم (Lehmann) → النواة الداخلية صلبة!',
      keyWords: ['P طولية', 'S مستعرضة', 'سوائل', 'Gutenberg', 'Lehmann', 'النواة سائلة'],
      points: 6,
      year: 'BAC 2020'
    },
    {
      id: 33,
      domain: 'geologie',
      unit: 'بنية الأرض',
      topic: 'الطبقات الأربع',
      difficulty: 'medium',
      type: 'explication',
      question: 'صف الطبقات الأربع لباطن الأرض مع ذكر العمق والحالة والتركيب.',
      modelAnswer: '1) القشرة (0-70 كم): صلبة. قارية (غرانيت, 2.7) + محيطية (بازلت, 3.0).\n2) المعطف (70-2900 كم): صلب + لزج في الأستينوسفير. بيريدوتيت (أوليفين, 3.3). T°: 500-3500°C.\n3) النواة الخارجية (2900-5150 كم): سائلة! حديد + نيكل (10-12). تُولّد المجال المغناطيسي.\n4) النواة الداخلية (5150-6370 كم): صلبة رغم 5500°C! حديد + نيكل (13). صلبة بسبب الضغط الهائل.\n\n3 انقطاعات: Moho, Gutenberg, Lehmann.',
      keyWords: ['القشرة', 'المعطف', 'النواة الخارجية سائلة', 'النواة الداخلية صلبة', 'Moho', 'Gutenberg', 'Lehmann'],
      points: 6,
      year: 'BAC 2022'
    },
    {
      id: 34,
      domain: 'geologie',
      unit: 'البنيات الجيولوجية',
      topic: 'الغوص',
      difficulty: 'hard',
      type: 'explication',
      question: 'صف ظاهرة الغوص (Subduction) والظواهر المرتبطة بها.',
      modelAnswer: 'الغوص: انغراز لوح محيطي تحت لوح آخر بسبب كثافته العالية.\n\nالظواهر المرتبطة:\n1) خندق محيطي: شق عميق (حتى 11 كم - ماريانا)\n2) زلازل عميقة: حتى 700 كم (نطاق بنيوف)\n3) بركانية أنديزيتية: صهارة لزجة ومتفجرة\n4) سلسلة جبال بركانية أو قوس جزر\n\nالمغماتية:\n- القشرة الغاطسة تحمل ماءً\n- الماء يُنقص نقطة انصهار البيريدوتيت\n- انصهار جزئي → صهارة أنديزيتية\n\nالتحولات:\nSchiste vert (0-15 كم) → Schiste bleu (15-50 كم) → Éclogite (>50 كم)',
      keyWords: ['خندق', 'نطاق بنيوف', 'أنديزيتية', 'الماء', 'انصهار جزئي', 'Schiste', 'Éclogite'],
      points: 7,
      year: 'BAC 2023'
    },
    {
      id: 35,
      domain: 'geologie',
      unit: 'البنيات الجيولوجية',
      topic: 'التصادم',
      difficulty: 'medium',
      type: 'explication',
      question: 'فسر كيف تتشكل سلاسل الجبال بالتصادم القاري مع أمثلة.',
      modelAnswer: 'التصادم القاري: اصطدام كتلتين قاريتين بعد اختفاء المحيط بينهما.\n\nالمراحل:\n1) محيط بين قارتين (مع ظهرة)\n2) بداية الغوص (تقارب الصفائح)\n3) اختفاء كامل المحيط\n4) تصادم القارتين (نفس الكثافة → لا غوص → طي وتراكب)\n5) تكوّن جبال ضخمة (جذور قارية عميقة - Isostasie)\n\nأمثلة:\n- الهيمالايا: الهند ↔ آسيا (محيط Téthys)\n- الألب: أفريقيا ↔ أوراسيا\n- الأطلس: أفريقيا ↔ أوراسيا (الجزائر!)',
      keyWords: ['تصادم', 'نفس الكثافة', 'طي', 'تراكب', 'Isostasie', 'Téthys'],
      points: 6,
      year: 'BAC 2021'
    },
    {
      id: 36,
      domain: 'geologie',
      unit: 'البنيات الجيولوجية',
      topic: 'الأوفيوليت',
      difficulty: 'hard',
      type: 'explication',
      question: 'عرّف الأوفيوليتات ووضح أهميتها في إثبات وجود محيطات قديمة.',
      modelAnswer: 'الأوفيوليتات: بقايا قشرة محيطية قديمة + جزء من المعطف، رُفعت على القارة بفعل التصادم (Obduction).\n\nالتسلسل الأوفيوليتي (من الأعلى للأسفل):\n1) رواسب بحرية\n2) بازلت وسادي (Pillow lavas) ← الدليل الأقوى!\n3) كتل بازلتية عمودية (Sheeted dykes)\n4) غابرو\n5) بيريدوتيت (معطف)\n\nالأهمية:\n- العثور على هذا التسلسل على اليابسة = دليل قاطع على وجود محيط قديم\n- Pillow lavas تتشكل فقط تحت الماء\n\nأمثلة: عُمان, قبرص, الألب, الجزائر (القبائل)',
      keyWords: ['أوفيوليت', 'Pillow lavas', 'قشرة محيطية', 'Obduction', 'محيط قديم'],
      points: 7,
      year: 'BAC 2022'
    },
    {
      id: 41,
      domain: 'geologie',
      unit: 'الصفائح التكتونية',
      topic: 'الطاقة الداخلية',
      difficulty: 'medium',
      type: 'explication',
      question: 'حدد مصادر الطاقة الداخلية للأرض وكيف تحرك الصفائح التكتونية.',
      modelAnswer: 'مصادر الحرارة الداخلية:\n1) الحرارة الأصلية (Primordiale): متبقية من تشكل الأرض (~20-30%).\n2) التفكك الإشعاعي (Radioactivité): تفكك U, Th, K-40 في الصخور (~70-80%). المصدر الرئيسي.\n\nالمحرك:\nتيارات الحمل الحراري (Convection) في المعطف:\n- المواد الحارة ترتفع\n- المواد الباردة تنزل\n- تشكل خلايا حمل تحرك الصفائح\n\nالقوى الإضافية:\n- Ridge push (دفع من الظهرة)\n- Slab pull (سحب اللوح الغاطس) ← الأقوى!',
      keyWords: ['حرارة أصلية', 'تفكك إشعاعي', 'حمل حراري', 'Ridge push', 'Slab pull'],
      points: 5,
      year: 'BAC 2021'
    },
    {
      id: 42,
      domain: 'geologie',
      unit: 'البنيات الجيولوجية',
      topic: 'الظهرات',
      difficulty: 'medium',
      type: 'analyse',
      question: 'حلل الأدلة على تباعد الصفائح عند الظهرات وسط محيطية.',
      modelAnswer: 'الأدلة:\n\n1) أعمار الصخور: تزداد بالابتعاد عن الظهرة (متماثلة في الجانبين). القشرة الأقرب = الأحدث.\n\n2) الشرائط المغناطيسية: أنماط مغناطيسية متناوبة ومتماثلة في جانبَي الظهرة (Vine & Matthews 1963). تسجل انعكاسات المجال المغناطيسي.\n\n3) سُمك الرواسب: رقيقة عند الظهرة, أسمك كلما ابتعدنا (وقت أطول لتجمع الرواسب).\n\n4) قياسات GPS: تؤكد التباعد بـ سنتيمترات/سنة.\n\n5) البركانية البازلتية المستمرة عند الظهرة.',
      keyWords: ['أعمار متماثلة', 'شرائط مغناطيسية', 'Vine Matthews', 'رواسب', 'GPS'],
      points: 6,
      year: 'BAC 2023'
    },
    {
      id: 43,
      domain: 'geologie',
      unit: 'البنيات الجيولوجية',
      topic: 'شواهد التقلص',
      difficulty: 'medium',
      type: 'explication',
      question: 'صف أنواع التشوهات الناتجة عن التقلص الجيولوجي.',
      modelAnswer: 'التقلص: اختصار مسافة بسبب قوى ضاغطة.\n\nأنواع التشوهات:\n\n1) التشوه المرن (Ductile) → الطيات (Plis):\n   - Anticlinal (محدبة): الصخور القديمة في المركز\n   - Synclinal (مقعرة): الصخور الحديثة في المركز\n   - تتناوب مثل الموجات\n\n2) التشوه الهش (Cassant) → الفوالق:\n   - فالق عكسي (Inverse): الجزء العلوي يرتفع (تقلص)\n   - فالق تراكبي (Chevauchement): صخور تتراكب لعشرات الكيلومترات\n\nالقياس: L₀ (الأصلي) - L (الحالي) = التقلص\nفي الألب: ~50% | الهيمالايا: ~70%',
      keyWords: ['Anticlinal', 'Synclinal', 'فالق عكسي', 'تراكبي', 'تقلص'],
      points: 5,
      year: 'BAC 2020'
    },
    {
      id: 50,
      domain: 'geologie',
      unit: 'بنية الأرض',
      topic: 'التركيب الكيميائي',
      difficulty: 'medium',
      type: 'comparaison',
      question: 'قارن بين صخور القشرة القارية والمحيطية والمعطف.',
      modelAnswer: 'القشرة القارية:\n- الغرانيت (فاتح)\n- كثافة: 2.7 g/cm³\n- سمك: 30-70 كم\n- معادن: كوارتز + فلدسبات + ميكا\n- تركيب: SIAL (Si + Al)\n\nالقشرة المحيطية:\n- البازلت/الغابرو (داكن)\n- كثافة: 3.0 g/cm³\n- سمك: 5-10 كم\n- معادن: بلاجيوكلاز + بيروكسين + أوليفين\n- تركيب: SIMA (Si + Mg)\n\nالمعطف:\n- البيريدوتيت (أخضر)\n- كثافة: 3.3 g/cm³\n- معادن: أوليفين (رئيسي) + بيروكسين\n- تركيب: غني Mg, Fe\n\nالقاعدة: الكثيف يغوص, الخفيف يطفو!',
      keyWords: ['غرانيت', 'بازلت', 'بيريدوتيت', 'SIAL', 'SIMA', 'أوليفين', 'الكثيف يغوص'],
      points: 6,
      year: 'BAC 2022'
    },

    // ═══════════════════════════════════════
    // QUESTIONS SUPPLÉMENTAIRES
    // ═══════════════════════════════════════

    {
      id: 40,
      domain: 'energie',
      unit: 'التحولات الطاقوية',
      topic: 'ATP',
      difficulty: 'easy',
      type: 'definition',
      question: 'عرّف ATP وحدد استخداماته في الخلية.',
      modelAnswer: 'ATP (Adénosine Triphosphate): جزيء يخزن وينقل الطاقة في الخلية.\n\nالبنية: أدينين + ريبوز + 3 مجموعات فوسفاتية مرتبطة بروابط عالية الطاقة.\n\nالاستخدامات:\n1) التركيب الحيوي (بروتينات, ADN, ARN)\n2) النقل النشط (مضخة Na⁺/K⁺)\n3) الحركة (تقلص العضلات)\n4) النقل العصبي (كمون الراحة)\n5) إنتاج الحرارة\n6) الإفراز (هرمونات, ناقلات عصبية)\n\nالجسم ينتج ويستهلك ~50-75 كغ ATP يومياً!',
      keyWords: ['ATP', 'طاقة', 'ADP', 'Pi', 'عملة طاقوية'],
      points: 4,
      year: 'BAC 2018'
    }
  ],

  // ===== FONCTIONS UTILITAIRES =====

  getByDomain(domain) {
    return this.questions.filter(q => q.domain === domain);
  },

  getByUnit(unit) {
    return this.questions.filter(q => q.unit === unit);
  },

  getByDifficulty(difficulty) {
    return this.questions.filter(q => q.difficulty === difficulty);
  },

  getByType(type) {
    return this.questions.filter(q => q.type === type);
  },

  getByYear(year) {
    return this.questions.filter(q => q.year === year);
  },

  getRandomQuestions(count = 5, domain = null) {
    let pool = domain ? this.getByDomain(domain) : this.questions;
    const shuffled = [...pool].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, Math.min(count, shuffled.length));
  },

  search(keyword) {
    const lower = keyword.toLowerCase();
    return this.questions.filter(q =>
      q.question.toLowerCase().includes(lower) ||
      q.unit.toLowerCase().includes(lower) ||
      q.topic.toLowerCase().includes(lower) ||
      q.keyWords.some(kw => kw.toLowerCase().includes(lower))
    );
  },

  getStats() {
    return {
      total: this.questions.length,
      byDomain: {
        proteines: this.getByDomain('proteines').length,
        energie: this.getByDomain('energie').length,
        geologie: this.getByDomain('geologie').length
      },
      byDifficulty: {
        easy: this.getByDifficulty('easy').length,
        medium: this.getByDifficulty('medium').length,
        hard: this.getByDifficulty('hard').length
      },
      byType: {
        definition: this.getByType('definition').length,
        explication: this.getByType('explication').length,
        analyse: this.getByType('analyse').length,
        comparaison: this.getByType('comparaison').length,
        synthese: this.getByType('synthese').length,
        application: this.getByType('application').length
      }
    };
  }
};

if (typeof window !== 'undefined') {
  window.BACQuestions = BACQuestions;
}
