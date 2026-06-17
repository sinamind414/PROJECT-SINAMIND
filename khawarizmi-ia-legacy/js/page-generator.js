/* ============================================
   PAGE GENERATOR - Auto-generate all unit pages
   ============================================ */

const PAGE_CONTENT = {
  
  'unit-1-3': {
    domain: { num: 1, icon: '🧬', gradient: 'linear-gradient(135deg, #A78BFA, #7C5FCD)' },
    unit: { num: 3, icon: '⚗️', titleAr: 'النشاط الإنزيمي للبروتينات', titleFr: 'L\'Activité Enzymatique des Protéines' },
    pages: '57 → 72',
    prev: { url: 'unit-1-2.html', icon: '🔬', title: 'بنية ووظيفة البروتين' },
    next: { url: 'unit-1-4.html', icon: '🛡️', title: 'المناعة' },
    chapters: [
      { id: 'ch1', num: 1, titleAr: 'مفهوم الإنزيم وأهميته', titleFr: 'Notion d\'enzyme et importance', page: 58,
        content: '<div class="definition-box"><div class="def-title">📌 تعريف: الإنزيم</div><div class="def-text">الإنزيم هو <strong>بروتين متخصص</strong> يعمل كعامل مساعد حيوي (Biocatalyseur)، يُسرِّع التفاعلات الكيميائية في الخلية دون أن يُستهلك. يتميز بـ<strong>النوعية</strong> تجاه مادة التفاعل (الركيزة).</div></div><div class="key-points"><div class="kp-title">📝 خصائص الإنزيمات</div><ul><li><strong>طبيعة بروتينية</strong>: الإنزيم بروتين ذو بنية فراغية خاصة</li><li><strong>النوعية المزدوجة</strong>: نوعية تجاه الركيزة ونوعية تجاه التفاعل</li><li><strong>الموقع الفعال</strong> (Site actif): منطقة ثلاثية الأبعاد تتعرف على الركيزة وتحفز التفاعل</li><li><strong>لا يُستهلك</strong>: يعود لحالته الأصلية بعد كل تفاعل</li><li><strong>يعمل بكميات ضئيلة</strong>: جزيء واحد يُحفِّز آلاف التفاعلات</li></ul></div>',
        quiz: { q: 'ما هي الطبيعة الكيميائية للإنزيمات؟', options: ['سكريات', 'بروتينات', 'دهون', 'أحماض نووية'], correct: 1, feedback: 'الإنزيمات بروتينات ذات بنية فراغية خاصة تعمل كعوامل مساعدة حيوية.' }
      },
      { id: 'ch2', num: 2, titleAr: 'النشاط الإنزيمي والبنية', titleFr: 'Activité et structure de l\'enzyme', page: 60,
        content: '<div class="content-block"><h3 class="content-heading">🔑 الموقع الفعال (Site Actif)</h3><p class="content-text">الموقع الفعال هو جزء صغير من سطح الإنزيم يتكون من <strong>تجويف</strong> ذي شكل فراغي محدد. يشمل: <strong>موقع التثبيت</strong> (تعرُّف على الركيزة) و<strong>موقع التحفيز</strong> (إتمام التفاعل).</p></div><div class="schema-box"><div class="schema-title">🔄 آلية عمل الإنزيم</div><div class="schema-flow"><div class="schema-step"><span class="step-icon">🧩</span>E + S<br><small>إنزيم + ركيزة</small></div><span class="schema-arrow">←</span><div class="schema-step"><span class="step-icon">🔗</span>E-S<br><small>معقد إنزيم-ركيزة</small></div><span class="schema-arrow">←</span><div class="schema-step"><span class="step-icon">✅</span>E + P<br><small>إنزيم + ناتج</small></div></div></div><div class="note-box note-info"><div class="note-icon">🔑</div><div><div class="note-title">نموذج القفل والمفتاح (Clé-serrure)</div><div class="note-text">الركيزة تتلاءم مع الموقع الفعال كما يتلاءم <strong>المفتاح مع القفل</strong>. هذا يُفسِّر <strong>نوعية الإنزيم</strong> تجاه ركيزته.</div></div></div>',
        quiz: { q: 'ما هو نموذج الإنزيم؟', options: ['يُغيِّر شكل الركيزة', 'الركيزة تتلاءم مع الموقع الفعال', 'يحتاج طاقة لبدء التفاعل', 'يُستهلك في التفاعل'], correct: 1, feedback: 'نموذج القفل والمفتاح: شكل الموقع الفعال يتلاءم تماماً مع شكل الركيزة.' }
      },
      { id: 'ch3', num: 3, titleAr: 'تأثير pH على نشاط الإنزيم', titleFr: 'Influence du pH', page: 67,
        content: '<div class="content-block"><p class="content-text">لكل إنزيم <strong>pH مثالي (Optimum)</strong> يكون فيه نشاطه في أقصاه. أي تغيير في pH الوسط يُؤثر على <strong>تأيُّن الأحماض الأمينية</strong> في الموقع الفعال، مما يُغيِّر البنية الفراغية ويُقلل النشاط الإنزيمي.</p></div><div class="key-points"><div class="kp-title">📝 أمثلة</div><ul><li><strong>البيبسين</strong> (المعدة): pH مثالي = 2 (حمضي)</li><li><strong>التريبسين</strong> (الأمعاء): pH مثالي = 8 (قاعدي)</li><li><strong>الأميلاز اللعابي</strong>: pH مثالي = 7 (متعادل)</li></ul></div>',
        quiz: { q: 'ما هو pH المثالي لإنزيم البيبسين؟', options: ['pH = 2 (حمضي)', 'pH = 7 (متعادل)', 'pH = 9 (قاعدي)'], correct: 0, feedback: 'البيبسين يعمل في المعدة حيث الوسط حمضي جداً (pH ≈ 2).' }
      },
      { id: 'ch4', num: 4, titleAr: 'تأثير الحرارة على نشاط الإنزيم', titleFr: 'Influence de la température', page: 68,
        content: '<div class="content-block"><p class="content-text">لكل إنزيم <strong>درجة حرارة مثالية</strong>. عند الإنسان هي حوالي <strong>37°C</strong>. فوق هذه الدرجة، يحدث <strong>تمسُّخ (Dénaturation)</strong> للبنية الفراغية وفقدان لا رجعي للنشاط.</p></div><div class="note-box note-warning"><div class="note-icon">⚠️</div><div><div class="note-title">التمسُّخ الحراري</div><div class="note-text">عند درجات حرارة مرتفعة (> 50°C)، تنكسر <strong>الروابط الضعيفة</strong> التي تحافظ على البنية الفراغية → فقدان شكل الموقع الفعال → <strong>توقف النشاط الإنزيمي بشكل لا رجعي</strong>.</div></div></div>',
        quiz: { q: 'ماذا يحدث للإنزيم عند حرارة عالية؟', options: ['يزداد نشاطه', 'يتمسَّخ ويفقد نشاطه', 'يبقى ثابتاً'], correct: 1, feedback: 'التمسُّخ الحراري يُكسِّر الروابط الضعيفة ويُفقد الإنزيم بنيته.' }
      }
    ]
  },
  
  'unit-1-4': {
    domain: { num: 1, icon: '🧬', gradient: 'linear-gradient(135deg, #A78BFA, #7C5FCD)' },
    unit: { num: 4, icon: '🛡️', titleAr: 'دور البروتينات في الدفاع عن الذات', titleFr: 'Rôle des Protéines dans la Défense de Soi (Immunologie)' },
    pages: '73 → 126',
    prev: { url: 'unit-1-3.html', icon: '⚗️', title: 'النشاط الإنزيمي' },
    next: { url: 'unit-1-5.html', icon: '⚡', title: 'الاتصال العصبي' },
    chapters: [
      { id: 'ch1', num: 1, titleAr: 'تذكير بالمكتسبات', titleFr: 'Rappel des acquis', page: 74, content: '<div class="content-block"><p class="content-text">درست سابقاً أن الجسم يملك جهازاً مناعياً يحميه من الأجسام الغريبة. سنتعرف في هذه الوحدة على <strong>الآليات الجزيئية</strong> للاستجابة المناعية ودور <strong>البروتينات</strong> فيها.</p></div>' },
      { id: 'ch2', num: 2, titleAr: 'الذات واللاذات', titleFr: 'Le soi et le non-soi', page: 76, content: '<div class="definition-box"><div class="def-title">📌 الذات (Le Soi)</div><div class="def-text">مجموع الجزيئات الناتجة عن <strong>التعبير المورثي</strong> لخلايا الفرد. يُعرَّف على سطح الخلايا بواسطة <strong>CMH</strong> (معقد التوافق النسيجي الرئيسي). CMH فريد لكل فرد (عدا التوائم الحقيقية).</div></div><div class="definition-box"><div class="def-title">📌 اللاذات (Le Non-soi)</div><div class="def-text">كل جزيئة أو خلية <strong>غريبة عن الجسم</strong> أو خلايا ذاتية مُعدَّلة (مصابة بفيروس أو سرطانية). يُولِّد اللاذات <strong>استجابة مناعية</strong>.</div></div>' },
      { id: 'ch3', num: 3, titleAr: 'الجزيئات الدفاعية (المناعة غير النوعية)', titleFr: 'Immunité non spécifique', page: 85, content: '<div class="content-block"><p class="content-text">خطوط الدفاع الأولى: <strong>الحواجز الطبيعية</strong> (جلد، مخاط)، <strong>الاستجابة الالتهابية</strong>، و<strong>البلعمة</strong> بواسطة البالعات الكبيرة (Macrophages).</p></div>' },
      { id: 'ch4', num: 4, titleAr: 'المعقد المناعي', titleFr: 'Le complexe immun', page: 87, content: '<div class="definition-box"><div class="def-title">📌 المعقد المناعي</div><div class="def-text">ناتج ارتباط <strong>الجسم المضاد</strong> (Anticorps) بمولد الضد <strong>(Antigène)</strong> بشكل نوعي على مستوى الموقع الفعال للجسم المضاد مع المحدد المستضدي (Épitope).</div></div>' },
      { id: 'ch5', num: 5, titleAr: 'مصدر الأجسام المضادة', titleFr: 'Origine des anticorps', page: 92, content: '<div class="content-block"><p class="content-text">تُفرز الأجسام المضادة من طرف <strong>اللمفاويات البائية (LB)</strong> بعد تمايزها إلى <strong>خلايا بلازمية (Plasmocytes)</strong>. كل خلية LB تُفرز نوعاً واحداً من الأجسام المضادة.</p></div>' },
      { id: 'ch6', num: 6, titleAr: 'المناعة النوعية الخلوية', titleFr: 'Immunité cellulaire', page: 97, content: '<div class="content-block"><p class="content-text">تتدخل <strong>اللمفاويات التائية السامة (LTc)</strong> في تدمير الخلايا المصابة مباشرة عبر التماس الخلوي بإفراز <strong>البرفورين</strong> الذي يُحدث ثقوباً في غشاء الخلية المستهدفة.</p></div>' },
      { id: 'ch7', num: 7, titleAr: 'طرق تأثير LTc', titleFr: 'Modes d\'action des LTc', page: 98, content: '<div class="key-points"><div class="kp-title">📝 آليات تأثير LTc</div><ul><li><strong>البرفورين</strong>: بروتين يُحدث ثقوباً في غشاء الخلية المستهدفة</li><li><strong>الجرانزيمات</strong>: إنزيمات تدخل عبر الثقوب وتُحفِّز الموت المبرمج (Apoptose)</li><li>التأثير يتطلب <strong>تماساً مباشراً</strong> بين LTc والخلية المستهدفة</li></ul></div>' },
      { id: 'ch8', num: 8, titleAr: 'مصدر اللمفاويات LTc', titleFr: 'Origine des LTc', page: 100, content: '<div class="content-block"><p class="content-text">تنشأ LTc من تمايز وتكاثر اللمفاويات T4 (LTh) بعد تعرُّفها على مولد الضد المعروض من طرف الخلية العارضة (CPA) بواسطة CMH.</p></div>' },
      { id: 'ch9', num: 9, titleAr: 'تحفيز LB و LT', titleFr: 'Activation des LB et LT', page: 103, content: '<div class="content-block"><p class="content-text">تحتاج LB و LT8 إلى <strong>إشارة تحفيز</strong> من <strong>LT4 (المساعدة)</strong> عبر إفراز <strong>الأنترلوكينات (Interleukines)</strong> خاصة IL-2. LT4 هي المنظم المركزي للاستجابة المناعية.</p></div>' },
      { id: 'ch10', num: 10, titleAr: 'اختيار نمط الاستجابة', titleFr: 'Choix du type de réponse', page: 105, content: '<div class="schema-box"><div class="schema-title">🔄 أنماط الاستجابة</div><div class="schema-flow"><div class="schema-step"><span class="step-icon">🅱️</span>استجابة خلطية<br><small>أجسام مضادة</small></div><span class="schema-arrow">←</span><div class="schema-step"><span class="step-icon">🇹</span>استجابة خلوية<br><small>LTc</small></div></div></div>' },
      { id: 'ch11', num: 11, titleAr: 'فقدان المناعة (SIDA)', titleFr: 'Perte de l\'immunité SIDA', page: 108, content: '<div class="definition-box"><div class="def-title">📌 فيروس VIH</div><div class="def-text">فيروس يستهدف <strong>اللمفاويات LT4</strong> لأنها تحمل مستقبلات CD4 على سطحها. يتكاثر داخلها ويُدمِّرها تدريجياً، مما يُسبب انهيار الجهاز المناعي (SIDA).</div></div><div class="note-box note-warning"><div class="note-icon">⚠️</div><div><div class="note-title">لماذا SIDA خطير؟</div><div class="note-text">بتدمير LT4 (المنظم المركزي)، لا يمكن تحفيز LB ولا LTc ← فقدان كامل للمناعة المكتسبة ← الجسم يصبح عرضة لكل الأمراض الانتهازية.</div></div></div>' }
    ]
  },
  
  'unit-1-5': {
    domain: { num: 1, icon: '🧬', gradient: 'linear-gradient(135deg, #A78BFA, #7C5FCD)' },
    unit: { num: 5, icon: '⚡', titleAr: 'دور البروتينات في الاتصال العصبي', titleFr: 'Rôle des Protéines dans la Communication Nerveuse' },
    pages: '127 → 172',
    prev: { url: 'unit-1-4.html', icon: '🛡️', title: 'المناعة' },
    next: { url: '../domain-2/unit-2-1.html', icon: '☀️', title: 'التركيب الضوئي' },
    chapters: [
      { id: 'ch1', num: 1, titleAr: 'تذكير بالمكتسبات', titleFr: 'Rappel des acquis', page: 128, content: '<div class="content-block"><p class="content-text">الجهاز العصبي يتكون من <strong>خلايا عصبية (Neurones)</strong> مترابطة. يتم نقل <strong>الرسالة العصبية</strong> على شكل <strong>إشارات كهربائية</strong> على طول الألياف، وعلى شكل <strong>إشارات كيميائية</strong> على مستوى المشابك.</p></div>' },
      { id: 'ch2', num: 2, titleAr: 'النقل المشبكي', titleFr: 'Transmission synaptique', page: 130, content: '<div class="definition-box"><div class="def-title">📌 المشبك (Synapse)</div><div class="def-text">منطقة اتصال وظيفي بين خليتين عصبيتين أو بين خلية عصبية وخلية مستجيبة. يتكون من: العنصر قبل مشبكي، الشق المشبكي، والعنصر بعد مشبكي.</div></div>' },
      { id: 'ch3', num: 3, titleAr: 'آلية النقل المشبكي', titleFr: 'Mécanisme de transmission', page: 132, content: '<div class="schema-box"><div class="schema-title">🔄 مراحل النقل المشبكي</div><div class="schema-flow"><div class="schema-step"><span class="step-icon">⚡</span>وصول السيالة</div><span class="schema-arrow">←</span><div class="schema-step"><span class="step-icon">📦</span>إفراز الناقل</div><span class="schema-arrow">←</span><div class="schema-step"><span class="step-icon">🎯</span>ارتباط بالمستقبل</div><span class="schema-arrow">←</span><div class="schema-step"><span class="step-icon">📊</span>كمون بعد مشبكي</div></div></div>' },
      { id: 'ch4', num: 4, titleAr: 'كمون الراحة', titleFr: 'Potentiel de repos', page: 136, content: '<div class="definition-box"><div class="def-title">📌 كمون الراحة</div><div class="def-text">فرق كمون كهربائي عبر الغشاء الخلوي في حالة الراحة، يساوي حوالي <strong>-70 mV</strong>. ينتج عن التوزيع غير المتساوي للأيونات بفعل مضخة Na⁺/K⁺ ATPase.</div></div><div class="key-points"><div class="kp-title">📝 أساسيات كمون الراحة</div><ul><li>داخل الخلية <strong>سالب</strong> (-70 mV)</li><li>تركيز <strong>K⁺</strong> أعلى داخل الخلية</li><li>تركيز <strong>Na⁺</strong> أعلى خارج الخلية</li><li>مضخة Na⁺/K⁺: تُخرج 3 Na⁺ وتُدخل 2 K⁺ مع استهلاك ATP</li></ul></div>' },
      { id: 'ch5', num: 5, titleAr: 'كمون العمل', titleFr: 'Potentiel d\'action', page: 140, content: '<div class="definition-box"><div class="def-title">📌 كمون العمل</div><div class="def-text">تغيير عابر وسريع في فرق الكمون. يتميز بـ: زوال الاستقطاب (من -70 إلى +30 mV) ثم عودة الاستقطاب.</div></div><div class="key-points"><div class="kp-title">📝 خصائص كمون العمل</div><ul><li><strong>قانون الكل أو لا شيء</strong>: سعة ثابتة مهما زادت شدة التنبيه</li><li><strong>غير متناقص</strong>: يحافظ على سعته أثناء الانتقال</li><li><strong>أحادي الاتجاه</strong>: بسبب فترة الامتناع المطلق</li></ul></div>' },
      { id: 'ch6', num: 6, titleAr: 'الإدماج العصبي', titleFr: 'Intégration nerveuse', page: 148, content: '<div class="content-block"><p class="content-text">الخلية بعد المشبكية تستقبل مشابك <strong>مُنبِّهة (PPSE)</strong> ومشابك <strong>مُثبِّطة (PPSI)</strong>. تقوم بالتجميع على مستوى مخروط الخروج. إذا بلغ مجموع الكمونات العتبة، يُولَّد كمون عمل.</p></div><div class="key-points"><div class="kp-title">📝 أنواع التجميع</div><ul><li><strong>التجميع الزماني</strong>: تراكم كمونات من نفس المشبك عبر الزمن</li><li><strong>التجميع المكاني</strong>: تراكم كمونات من مشابك مختلفة في نفس اللحظة</li></ul></div>' },
      { id: 'ch7', num: 7, titleAr: 'تأثير المخدرات على المشابك', titleFr: 'Effet des drogues', page: 154, content: '<div class="content-block"><p class="content-text">تؤثر المخدرات على مستوى المشبك بعدة طرق: تقليد الناقل العصبي، منع إعادة امتصاصه، أو حصر مستقبلاته.</p></div><div class="key-points"><div class="kp-title">📝 أمثلة</div><ul><li><strong>النيكوتين</strong>: يُقلِّد الأسيتيل كولين</li><li><strong>الكوكايين</strong>: يمنع إعادة امتصاص الدوبامين</li><li><strong>المورفين</strong>: يُقلِّد الإندورفينات</li><li><strong>الكورار</strong>: يحصر مستقبلات الأسيتيل كولين</li></ul></div>' }
    ]
  },
  
  'unit-2-1': {
    domain: { num: 2, icon: '⚡', gradient: 'linear-gradient(135deg, #FB7185, #E11D48)' },
    unit: { num: 1, icon: '☀️', titleAr: 'تحويل الطاقة الضوئية إلى طاقة كيميائية', titleFr: 'Conversion de l\'Énergie Lumineuse (Photosynthèse)' },
    pages: '174 → 204',
    prev: { url: '../domain-1/unit-1-5.html', icon: '⚡', title: 'الاتصال العصبي' },
    next: { url: 'unit-2-2.html', icon: '🔋', title: 'التنفس الخلوي' },
    chapters: [
      { id: 'ch1', num: 1, titleAr: 'تذكير بالتركيب الضوئي', titleFr: 'Rappel photosynthèse', page: 175, content: '<div class="content-block"><p class="content-text">التركيب الضوئي هو تحويل <strong>الطاقة الضوئية</strong> إلى <strong>طاقة كيميائية</strong> في المادة العضوية.<br><br><strong style="font-size:1.1rem;">6CO₂ + 6H₂O + ضوء → C₆H₁₂O₆ + 6O₂</strong></p></div>' },
      { id: 'ch2', num: 2, titleAr: 'مقر التركيب الضوئي', titleFr: 'Siège - chloroplaste', page: 177, content: '<div class="definition-box"><div class="def-title">📌 الصانعة الخضراء (Chloroplaste)</div><div class="def-text">عضية ذات غشاء مزدوج تحتوي على: <strong>التيلاكويدات</strong> (أقراص غشائية تحوي اليخضور) و<strong>السدى (Stroma)</strong> (الوسط الداخلي). التيلاكويدات المتراصة تُشكِّل الغرانا (Grana).</div></div>' },
      { id: 'ch3', num: 3, titleAr: 'المرحلة الكيموضوئية', titleFr: 'Phase photochimique', page: 180, content: '<div class="content-block"><h3 class="content-heading">☀️ المرحلة الضوئية</h3><p class="content-text">تحدث على التيلاكويدات بوجود الضوء.</p></div><div class="key-points"><div class="kp-title">📝 أحداث المرحلة الضوئية</div><ul><li><strong>امتصاص الضوء</strong> بواسطة اليخضور</li><li><strong>التحلل الضوئي للماء</strong>: H₂O → 2H⁺ + ½O₂ + 2e⁻</li><li><strong>إرجاع NADP⁺</strong> إلى NADPH,H⁺</li><li><strong>تركيب ATP</strong> بواسطة ATP synthase</li></ul></div>' },
      { id: 'ch4', num: 4, titleAr: 'حلقة كالفن', titleFr: 'Cycle de Calvin', page: 192, content: '<div class="content-block"><p class="content-text">تحدث في السدى بدون حاجة مباشرة للضوء. تستخدم ATP + NADPH لتثبيت CO₂.</p></div><div class="schema-box"><div class="schema-title">🔄 حلقة كالفن المبسطة</div><div class="schema-flow"><div class="schema-step"><span class="step-icon">🌿</span>C5 (RuBP)</div><span class="schema-arrow">←</span><div class="schema-step"><span class="step-icon">➕</span>تثبيت CO₂<br><small>RuBisCO</small></div><span class="schema-arrow">←</span><div class="schema-step"><span class="step-icon">🔢</span>2 × C3 (APG)</div><span class="schema-arrow">←</span><div class="schema-step"><span class="step-icon">🍬</span>G3P → غلوكوز</div></div></div>' }
    ]
  },
  
  'unit-2-2': {
    domain: { num: 2, icon: '⚡', gradient: 'linear-gradient(135deg, #FB7185, #E11D48)' },
    unit: { num: 2, icon: '🔋', titleAr: 'تحويل الطاقة الكيميائية إلى ATP', titleFr: 'Conversion en ATP (Respiration & Fermentation)' },
    pages: '205 → 226',
    prev: { url: 'unit-2-1.html', icon: '☀️', title: 'التركيب الضوئي' },
    next: { url: 'unit-2-3.html', icon: '🔬', title: 'التحولات الطاقوية' },
    chapters: [
      { id: 'ch1', num: 1, titleAr: 'تذكير بالمكتسبات', titleFr: 'Rappel', page: 206, content: '<div class="content-block"><p class="content-text">التنفس الخلوي هو <strong>أكسدة المادة العضوية</strong> (الغلوكوز) لإنتاج ATP.<br><br><strong>C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + 38 ATP</strong></p></div>' },
      { id: 'ch2', num: 2, titleAr: 'مقر الأكسدة التنفسية', titleFr: 'Siège - mitochondrie', page: 207, content: '<div class="definition-box"><div class="def-title">📌 الميتوكوندري (Mitochondrie)</div><div class="def-text">عضية ذات غشاء مزدوج: الغشاء الخارجي (أملس) والغشاء الداخلي (ذو أعراف). المطرس (Matrice) يحوي إنزيمات حلقة كريبس. الأعراف تحمل سلسلة نقل الإلكترونات + ATP synthase.</div></div>' },
      { id: 'ch3', num: 3, titleAr: 'التحلل السكري', titleFr: 'La glycolyse', page: 210, content: '<div class="content-block"><p class="content-text">يحدث في <strong>الهيولى</strong>. يُحوِّل غلوكوز (C6) إلى حمض بيروفيك (C3). الحصيلة: <strong>2 ATP + 2 NADH</strong>. لا يحتاج O₂.</p></div>' },
      { id: 'ch4', num: 4, titleAr: 'حلقة كريبس', titleFr: 'Cycle de Krebs', page: 213, content: '<div class="content-block"><p class="content-text">في المطرس، يدخل Acétyl-CoA حلقة كريبس. الحصيلة لكل دورة: <strong>2 CO₂ + 3 NADH + 1 FADH₂ + 1 ATP</strong></p></div>' },
      { id: 'ch5', num: 5, titleAr: 'الفسفرة التأكسدية', titleFr: 'Phosphorylation oxydative', page: 215, content: '<div class="content-block"><p class="content-text">تتم على الغشاء الداخلي للميتوكوندري عبر سلسلة نقل الإلكترونات التي تُولِّد تدرج بروتونات يُستغل بواسطة <strong>ATP synthase</strong>.</p></div><div class="key-points"><div class="kp-title">📝 الحصيلة الطاقوية الإجمالية</div><ul><li>التحلل السكري: <strong>2 ATP</strong></li><li>حلقة كريبس: <strong>2 ATP</strong></li><li>الفسفرة التأكسدية: <strong>34 ATP</strong></li><li><strong>المجموع: 38 ATP</strong> لكل جزيئة غلوكوز</li></ul></div>' },
      { id: 'ch6', num: 6, titleAr: 'التخمر (الوسط اللاهوائي)', titleFr: 'Fermentation', page: 218, content: '<div class="content-block"><p class="content-text">في غياب O₂، يتحول حمض البيروفيك عبر التخمر. نوعان: <strong>التخمر الكحولي</strong> (خميرة → إيثانول + CO₂) و<strong>التخمر اللبني</strong> (عضلات → حمض اللبن). الحصيلة: 2 ATP فقط لكل غلوكوز.</p></div>' }
    ]
  },
  
  'unit-2-3': {
    domain: { num: 2, icon: '⚡', gradient: 'linear-gradient(135deg, #FB7185, #E11D48)' },
    unit: { num: 3, icon: '🔬', titleAr: 'تحويل الطاقة على المستوى الخلوي', titleFr: 'Conversions Énergétiques Cellulaires' },
    pages: '227 → 236',
    prev: { url: 'unit-2-2.html', icon: '🔋', title: 'التنفس والتخمر' },
    next: { url: '../domain-3/unit-3-1.html', icon: '🗺️', title: 'النشاط التكتوني' },
    chapters: [
      { id: 'ch1', num: 1, titleAr: 'التحولات الطاقوية الخلوية', titleFr: 'Transformations énergétiques', page: 228, content: '<div class="schema-box"><div class="schema-title">🔄 العلاقة بين التركيب الضوئي والتنفس</div><div class="schema-flow"><div class="schema-step"><span class="step-icon">☀️</span>طاقة ضوئية</div><span class="schema-arrow">←</span><div class="schema-step"><span class="step-icon">🌿</span>تركيب ضوئي<br><small>بلاستيدات</small></div><span class="schema-arrow">←</span><div class="schema-step"><span class="step-icon">🍬</span>غلوكوز</div><span class="schema-arrow">←</span><div class="schema-step"><span class="step-icon">🔋</span>تنفس خلوي<br><small>ميتوكوندري</small></div><span class="schema-arrow">←</span><div class="schema-step"><span class="step-icon">⚡</span>ATP</div></div></div><div class="note-box note-bac"><div class="note-icon">🎯</div><div><div class="note-title">متطلبات BAC</div><div class="note-text">مقارنة بين التركيب الضوئي والتنفس الخلوي في جدول. الربط بين وظيفة البلاستيدات والميتوكوندريات. شرح دورة الطاقة في الخلية.</div></div></div>' }
    ]
  },
  
  'unit-3-1': {
    domain: { num: 3, icon: '🌍', gradient: 'linear-gradient(135deg, #60A5FA, #2563EB)' },
    unit: { num: 1, icon: '🗺️', titleAr: 'النشاط التكتوني للصفائح', titleFr: 'L\'Activité Tectonique des Plaques' },
    pages: '237 → 258',
    prev: { url: '../domain-2/unit-2-3.html', icon: '🔬', title: 'التحولات الطاقوية' },
    next: { url: 'unit-3-2.html', icon: '🌐', title: 'بنية الكرة الأرضية' },
    chapters: [
      { id: 'ch1', num: 1, titleAr: 'تحديد الصفائح التكتونية', titleFr: 'Identification des plaques', page: 238, content: '<div class="definition-box"><div class="def-title">📌 الصفيحة التكتونية</div><div class="def-text">قطعة صلبة من <strong>الغلاف الصخري (Lithosphère)</strong> تتحرك فوق <strong>الأسثينوسفير (Asthénosphère)</strong> المائع. تُحدَّد حدودها بتوزيع النشاط الزلزالي والبركاني.</div></div>' },
      { id: 'ch2', num: 2, titleAr: 'حركات الصفائح التكتونية', titleFr: 'Mouvements des plaques', page: 240, content: '<div class="key-points"><div class="kp-title">📝 أنواع حركات الصفائح</div><ul><li><strong>التباعد</strong>: على الظهرات ← تشكل قشرة محيطية جديدة</li><li><strong>التقارب</strong>: غوص (Subduction) أو تصادم (Collision)</li><li><strong>التحول</strong>: انزلاق أفقي بمحاذاة فوالق تحويلية</li></ul></div>' },
      { id: 'ch3', num: 3, titleAr: 'الطاقة الداخلية للأرض', titleFr: 'Énergie interne du globe', page: 248, content: '<div class="content-block"><p class="content-text">مصدر حركة الصفائح هو الطاقة الحرارية الداخلية الناتجة عن تفكك العناصر المشعة. تُسبب <strong>تيارات الحمل (Convection)</strong> في الأسثينوسفير.</p></div>' }
    ]
  },
  
  'unit-3-2': {
    domain: { num: 3, icon: '🌍', gradient: 'linear-gradient(135deg, #60A5FA, #2563EB)' },
    unit: { num: 2, icon: '🌐', titleAr: 'بنية الكرة الأرضية', titleFr: 'Structure du Globe Terrestre' },
    pages: '259 → 286',
    prev: { url: 'unit-3-1.html', icon: '🗺️', title: 'النشاط التكتوني' },
    next: { url: 'unit-3-3.html', icon: '⛰️', title: 'البنيات الجيولوجية' },
    chapters: [
      { id: 'ch1', num: 1, titleAr: 'الموجات الزلزالية', titleFr: 'Les ondes sismiques', page: 260, content: '<div class="key-points"><div class="kp-title">📝 أنواع الموجات الزلزالية</div><ul><li><strong>الموجات P</strong>: طولية، سريعة، تعبر الصلبة والسائلة</li><li><strong>الموجات S</strong>: عرضية، أبطأ، لا تعبر السائلة</li><li><strong>الموجات السطحية (L)</strong>: أبطأ، تسبب أكبر الأضرار</li></ul></div><div class="note-box note-info"><div class="note-icon">💡</div><div><div class="note-title">فائدة دراسة الموجات</div><div class="note-text">تغيُّر سرعة الموجات يكشف عن سطوح الانقطاع ويُمكِّن من معرفة البنية الداخلية للأرض.</div></div></div>' },
      { id: 'ch2', num: 2, titleAr: 'التركيب الكيميائي للقشرة والمعطف', titleFr: 'Composition croûte/manteau', page: 266, content: '<div class="key-points"><div class="kp-title">📝 مقارنة</div><ul><li><strong>القشرة المحيطية</strong>: بازلت + غابرو، كثافة ~3.0، سمك 5-10 km</li><li><strong>القشرة القارية</strong>: غرانيت، كثافة ~2.7، سمك 30-70 km</li><li><strong>المعطف العلوي</strong>: بيريدوتيت، كثافة ~3.3، سمك ~2900 km</li></ul></div>' },
      { id: 'ch3', num: 3, titleAr: 'نمذجة البنية الداخلية', titleFr: 'Modélisation interne', page: 274, content: '<div class="schema-box"><div class="schema-title">🌍 طبقات الأرض</div><div class="schema-flow"><div class="schema-step"><span class="step-icon">🏔️</span>القشرة<br><small>5-70 km</small></div><span class="schema-arrow">←</span><div class="schema-step"><span class="step-icon">🟤</span>المعطف<br><small>~2900 km</small></div><span class="schema-arrow">←</span><div class="schema-step"><span class="step-icon">🟡</span>النواة الخارجية<br><small>سائلة ~2200 km</small></div><span class="schema-arrow">←</span><div class="schema-step"><span class="step-icon">🔴</span>النواة الداخلية<br><small>صلبة ~1250 km</small></div></div></div><div class="key-points"><div class="kp-title">📝 سطوح الانقطاع</div><ul><li><strong>Moho</strong>: بين القشرة والمعطف</li><li><strong>Gutenberg</strong>: بين المعطف والنواة (2900 km)</li><li><strong>Lehmann</strong>: بين النواة الخارجية والداخلية (5100 km)</li></ul></div>' }
    ]
  },
  
  'unit-3-3': {
    domain: { num: 3, icon: '🌍', gradient: 'linear-gradient(135deg, #60A5FA, #2563EB)' },
    unit: { num: 3, icon: '⛰️', titleAr: 'النشاط التكتوني والبنيات الجيولوجية', titleFr: 'Activité Tectonique et Structures Géologiques' },
    pages: '287 → 326',
    prev: { url: 'unit-3-2.html', icon: '🌐', title: 'بنية الكرة الأرضية' },
    next: null,
    chapters: [
      { id: 'ch1', num: 1, titleAr: 'الظهرات وسط محيطية', titleFr: 'Dorsales médio-océaniques', page: 288, content: '<div class="definition-box"><div class="def-title">📌 الظهرة وسط المحيطية</div><div class="def-text">سلسلة جبلية تحت بحرية طولها 65000 km، تتميز بـ: ريفت مركزي، نشاط بركاني وزلزالي، وتدفق حراري مرتفع.</div></div>' },
      { id: 'ch2', num: 2, titleAr: 'المغماتية وتشكل اللوح المحيطي', titleFr: 'Magmatisme et plaque océanique', page: 290, content: '<div class="content-block"><p class="content-text">يصعد المغما من الأسثينوسفير عبر الريفت. يتبلور ويُشكِّل قشرة محيطية جديدة تتباعد من جانبي الظهرة. هذه العملية تُسمى الاتساع المحيطي (Expansion océanique).</p></div>' },
      { id: 'ch3', num: 3, titleAr: 'صخور الظهرة', titleFr: 'Roches de la dorsale', page: 294, content: '<div class="key-points"><div class="kp-title">📝 الثلاثية الأوفيوليتية</div><ul><li><strong>بازلت عمودي</strong>: تبريد سريع في الماء ← بلورات صغيرة</li><li><strong>غابرو (Gabbro)</strong>: تبريد بطيء في العمق ← بلورات كبيرة</li><li><strong>بيريدوتيت (Péridotite)</strong>: صخر المعطف الأصلي</li></ul></div>' },
      { id: 'ch4', num: 4, titleAr: 'الظواهر المرتبطة بالغوص', titleFr: 'Phénomènes de subduction', page: 302, content: '<div class="definition-box"><div class="def-title">📌 الغوص (Subduction)</div><div class="def-text">انغراز اللوح المحيطي تحت لوح آخر. يتميز بـ: خندق محيطي، نشاط زلزالي عميق (Bénioff)، بركانية انفجارية.</div></div>' },
      { id: 'ch5', num: 5, titleAr: 'اختفاء اللوح المحيطي', titleFr: 'Disparition de la plaque', page: 307, content: '<div class="content-block"><p class="content-text">تزداد كثافة القشرة المحيطية كلما ابتعدت عن الظهرة. عندما تصبح أكثر كثافة من الأسثينوسفير، تنغرز في باطن الأرض. يحدث انصهار جزئي يُنتج مغماً يشكل براكين.</p></div>' },
      { id: 'ch6', num: 6, titleAr: 'التضاريس الناجمة عن التصادم', titleFr: 'Reliefs de collision', page: 316, content: '<div class="content-block"><p class="content-text">عندما يُستهلك اللوح المحيطي بالغوص، تتصادم القارتان مباشرة. يُسبب تشوهات ضخمة (طيات + فوالق عكسية) ونشأة سلاسل جبلية مثل الألب والهيمالايا.</p></div>' },
      { id: 'ch7', num: 7, titleAr: 'شواهد التقلص', titleFr: 'Indices du raccourcissement', page: 319, content: '<div class="key-points"><div class="kp-title">📝 شواهد التصادم</div><ul><li><strong>الطيّات (Plis)</strong>: تشوه مرن للطبقات</li><li><strong>الفوالق العكسية</strong>: تشوه صلب مع تقصير</li><li><strong>التوريق (Schistosité)</strong>: بنية ناتجة عن الضغط</li><li><strong>التحول (Métamorphisme)</strong>: تغير المعادن بالضغط والحرارة</li></ul></div>' },
      { id: 'ch8', num: 8, titleAr: 'شواهد محيط قديم (الأوفيوليت)', titleFr: 'Ophiolites', page: 323, content: '<div class="definition-box"><div class="def-title">📌 الأوفيوليت</div><div class="def-text">بقايا قشرة محيطية قديمة موجودة فوق القشرة القارية في سلاسل التصادم. تُثبت وجود محيط قديم بين القارتين قبل اختفائه.</div></div><div class="note-box note-bac"><div class="note-icon">🎯</div><div><div class="note-title">متطلبات BAC — التكتونية</div><div class="note-text">• تحليل خرائط الزلازل والبراكين • شرح الاتساع المحيطي • مقارنة بنية محيطية وقارية • شرح الغوص • إثبات محيط قديم بالأوفيوليت</div></div></div>' }
    ]
  }
};

function generateUnitPage(unitId) {
  const data = PAGE_CONTENT[unitId];
  if (!data) return '';
  
  const chaptersHTML = data.chapters.map(ch => {
    const quizHTML = ch.quiz ? `
      <div class="mini-quiz">
        <div class="mini-quiz-title">🧪 اختبر فهمك</div>
        <div class="mini-quiz-question">${ch.quiz.q}</div>
        <div class="mini-quiz-options">
          ${ch.quiz.options.map((opt, i) => `
            <button class="mini-quiz-option" data-correct="${i === ch.quiz.correct}">
              <span class="opt-letter">${String.fromCharCode(1571 + i)}</span> ${opt}
            </button>
          `).join('')}
        </div>
        <div class="mini-quiz-feedback">${ch.quiz.feedback}</div>
      </div>` : '';
    
    return `
      <section class="chapter-section" id="${ch.id}">
        <div class="chapter-header">
          <div class="chapter-num-badge" style="background: ${data.domain.gradient};">${ch.num}</div>
          <div class="chapter-header-info">
            <h2 class="chapter-title-ar">${ch.titleAr}</h2>
            <p class="chapter-title-fr">${ch.titleFr}</p>
            <span class="chapter-page-ref">📄 صفحة ${ch.page}</span>
          </div>
        </div>
        ${ch.content}
        ${quizHTML}
        <div class="chapter-actions">
          <button class="ch-action-btn primary" onclick="UnitPage.markCompleted('${ch.id}')">✅ أنهيت هذا الفصل</button>
          <button class="ch-action-btn" onclick="UnitPage.askKhawarizmi('اشرح لي ${ch.titleAr}')">🤖 اسأل خوارزمي</button>
        </div>
      </section>`;
  }).join('\n');
  
  const sidebarHTML = data.chapters.map((ch, i) => `
    <a href="#${ch.id}" class="sidebar-chapter ${i === 0 ? 'active' : ''}" data-chapter="${ch.id}" onclick="UnitPage.scrollToChapter('${ch.id}'); return false;">
      <span class="sidebar-num">${ch.num}</span> ${ch.titleAr}
    </a>`).join('\n');
  
  const prevHTML = data.prev ? `
    <a href="${data.prev.url}" class="footer-nav-card">
      <span class="footer-nav-arrow">→</span>
      <div class="footer-nav-info">
        <div class="footer-nav-label">الوحدة السابقة</div>
        <div class="footer-nav-title">${data.prev.icon} ${data.prev.title}</div>
      </div>
    </a>` : '<div></div>';
  
  const nextHTML = data.next ? `
    <a href="${data.next.url}" class="footer-nav-card next">
      <span class="footer-nav-arrow">←</span>
      <div class="footer-nav-info">
        <div class="footer-nav-label">الوحدة التالية</div>
        <div class="footer-nav-title">${data.next.icon} ${data.next.title}</div>
      </div>
    </a>` : '<div></div>';
  
  return { chaptersHTML, sidebarHTML, prevHTML, nextHTML };
}

if (typeof window !== 'undefined') {
  window.PAGE_CONTENT = PAGE_CONTENT;
  window.generateUnitPage = generateUnitPage;
}
