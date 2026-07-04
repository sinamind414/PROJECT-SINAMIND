"use client"

import { useParams } from "next/navigation"
import Link from "next/link"
import { AppShell } from "@/components/layout/AppShell"
import GenZInteractiveLesson from "@/components/lessons/GenZInteractiveLesson"
import GenZQCMFlow from "@/components/lessons/GenZQCMFlow"

const GENZ_LESSONS: Record<string, { titleAr: string; phases: any[] }> = {
  "phase1_chapitres_1_2": {
    titleAr: "التركيب الكيميائي للبروتين",
    phases: [
      { id: "1", titleAr: "شنو هو البروتين؟", content: <div className="text-lg leading-relaxed">البروتينات جزيئات عضوية كبيرة تتكون من الكربون والهيدروجين والأكسجين والنيتروجين. تتكون من سلسلة طويلة من الأحماض الأمينية مرتبطة بروابط ببتيدية. كل بروتين له تركيب خاص يحدد وظيفته في الجسم.</div> },
      { id: "2", titleAr: "مستويات البنية الأربعة", content: <div className="text-lg leading-relaxed">1. البنية الأولية: تسلسل الأحماض الأمينية. 2. الثانوية: حلزون ألفا أو صفائح بيتا. 3. الثالثية: الطي ثلاثي الأبعاد. 4. الرباعية: تجمع عدة سلاسل. كل مستوى يعطي خاصية جديدة.</div> },
      { id: "3", titleAr: "أهمية التركيب", content: <div className="text-lg leading-relaxed">التركيب يحدد الوظيفة. لو تغيرت البنية الثالثية يتغير عمل البروتين كله. مثال: الهيموغلوبين ينقل الأكسجين بفضل شكله الخاص.</div> },
      { id: "4", titleAr: "دورك الحين يا خويا 🔥", practice: true, content: <div>اشرح بالتفصيل كيف تؤثر مستويات البنية على وظيفة البروتين. أعط مثالاً من الجسم.</div> },
    ]
  },

  "phase2_chapitres_3_4": {
    titleAr: "خصائص الإنزيمات",
    phases: [
      { id: "1", titleAr: "شنو هو الإنزيم؟", content: <div className="text-lg leading-relaxed">الإنزيم بروتين خاص يسرّع التفاعلات الكيميائية بدون ما يتغير أو يستهلك. يعمل كمحفز بيولوجي. كل إنزيم له موقع نشط يرتبط بالركيزة فقط.</div> },
      { id: "2", titleAr: "الخصائص المهمة", content: <div className="text-lg leading-relaxed">1. الخصوصية: إنزيم واحد لركيزة معينة. 2. يتأثر بالحرارة والـ pH. 3. يعمل بكميات قليلة. 4. يسرّع التفاعل ملايين المرات.</div> },
      { id: "3", titleAr: "كيف يعمل الإنزيم؟", content: <div className="text-lg leading-relaxed">نظرية القفل والمفتاح: الركيزة تدخل الموقع النشط مثل المفتاح في القفل. بعد التفاعل يخرج المنتج والإنزيم يبقى كما هو.</div> },
      { id: "4", titleAr: "تدرب واربح نقاط", practice: true, content: <div>لماذا تتأثر سرعة الإنزيم بالحرارة العالية؟ اشرح باستخدام البنية.</div> },
    ]
  },

  "phase3_chapitres_5_6": {
    titleAr: "التنظيم الهرموني",
    phases: [
      { id: "1", titleAr: "شنو هي الهرمونات؟", content: <div className="text-lg leading-relaxed">الهرمونات رسائل كيميائية تفرزها الغدد الصماء في الدم. تنتقل لتتحكم في أعضاء بعيدة. أمثلة: الأنسولين، الغدة الدرقية، الأدرينالين.</div> },
      { id: "2", titleAr: "آلية العمل", content: <div className="text-lg leading-relaxed">ترتبط الهرمونات بمستقبلات على الخلايا المستهدفة. تغير نشاط الخلية: زيادة أو نقصان إفراز أو نمو. سريعة أو بطيئة حسب النوع.</div> },
      { id: "3", titleAr: "أمثلة رئيسية", content: <div className="text-lg leading-relaxed">الأنسولين: يخفض السكر في الدم. الغلوكاغون: يرفعه. هرمون النمو: يحفز النمو. الإستروجين: ينظم الدورة عند الإناث.</div> },
      { id: "4", titleAr: "الآن دورك", practice: true, content: <div>قارن بين عمل الأنسولين والغلوكاغون في تنظيم السكر. ماذا يحدث لو اختل التوازن؟</div> },
    ]
  },

  "phase4_chapitres_7_8": {
    titleAr: "المناعة الخلطية والخلوية",
    phases: [
      { id: "1", titleAr: "المناعة الطبيعية", content: <div className="text-lg leading-relaxed">المناعة الخلطية تعتمد على الأجسام المضادة في الدم. الخلايا البائية تنتج أجسام مضادة تستهدف المستضدات. تعمل في السوائل خارج الخلايا.</div> },
      { id: "2", titleAr: "المناعة الخلوية", content: <div className="text-lg leading-relaxed">تعتمد على الخلايا التائية. الخلايا التائية القاتلة تدمر الخلايا المصابة مباشرة. مهمة ضد الفيروسات والسرطان.</div> },
      { id: "3", titleAr: "الفرق بينهما", content: <div className="text-lg leading-relaxed">الخلطية: أجسام مضادة + خلايا بائية. الخلوية: خلايا تائية. كلتاهما تتعاونان مع المناعة الفطرية.</div> },
      { id: "4", titleAr: "يلا نجرب", practice: true, content: <div>اشرح كيف تساهم المناعة الخلطية والخلوية معاً في حماية الجسم من فيروس.</div> },
    ]
  },

  "phase5_chapitres_9_10": {
    titleAr: "الأجسام المضادة واللقاحات",
    phases: [
      { id: "1", titleAr: "ما هي الأجسام المضادة؟", content: <div className="text-lg leading-relaxed">بروتينات على شكل Y تنتجها الخلايا البائية. ترتبط بالمستضدات وتحيدها أو تساعد في تدميرها. لكل مستضد جسم مضاد خاص.</div> },
      { id: "2", titleAr: "السيروم واللقاح", content: <div className="text-lg leading-relaxed">السيروم: أجسام مضادة جاهزة تعطى فوراً. اللقاح: يحفز الجسم على إنتاج أجسام مضادة وذاكرة مناعية.</div> },
      { id: "3", titleAr: "المناعة الاصطناعية", content: <div className="text-lg leading-relaxed">اللقاح يعطي مناعة طويلة الأمد بدون إصابة. مثال: لقاح شلل الأطفال، كوفيد. يحتوي على مستضدات ضعيفة أو ميتة.</div> },
      { id: "4", titleAr: "دورك الحين", practice: true, content: <div>ما الفرق بين السيروم واللقاح؟ متى نستخدم كل واحد؟</div> },
    ]
  },

  "phase6_chapitres_11_12": {
    titleAr: "التنفس والتخمر",
    phases: [
      { id: "1", titleAr: "التنفس الخلوي", content: <div className="text-lg leading-relaxed">عملية تحويل الغلوكوز إلى طاقة (ATP) + ثاني أكسيد الكربون + ماء. يحدث في الميتوكوندRIA. يحتاج أكسجين. معادلة: C6H12O6 + 6O2 → 6CO2 + 6H2O + طاقة.</div> },
      { id: "2", titleAr: "التخمر", content: <div className="text-lg leading-relaxed">في غياب الأكسجين. يحول الغلوكوز إلى طاقة قليلة + حمض لاكتيك أو كحول. يحدث في العضلات أثناء الجهد أو في الخميرة.</div> },
      { id: "3", titleAr: "مقارنة", content: <div className="text-lg leading-relaxed">التنفس: كثير طاقة + أكسجين. التخمر: طاقة قليلة + بدون أكسجين. الخلايا تفضل التنفس لأنه أكثر كفاءة.</div> },
      { id: "4", titleAr: "تدرب الآن", practice: true, content: <div>قارن بين التنفس الخلوي والتخمر. متى يلجأ الجسم إلى التخمر؟</div> },
    ]
  },

  "phase7_chapitres_13_14": {
    titleAr: "مصادر الطاقة وامتصاص المغذيات",
    phases: [
      { id: "1", titleAr: "مصادر الطاقة", content: <div className="text-lg leading-relaxed">الغلوكوز هو المصدر الرئيسي. يأتي من هضم الكربوهيدرات. الدهون والپروتينات مصادر ثانوية. الجسم يخزن الطاقة على شكل غليكوجين ودهون.</div> },
      { id: "2", titleAr: "الامتصاص في الأمعاء", content: <div className="text-lg leading-relaxed">الأمعاء الدقيقة تمتص المغذيات عبر الزغابات. الغلوكوز والأحماض الأمينية تمتص بالنقل النشط. الدهون بالانتشار.</div> },
      { id: "3", titleAr: "النقل إلى الخلايا", content: <div className="text-lg leading-relaxed">الدم ينقل المغذيات إلى الخلايا. الإنسولين يساعد على دخول الغلوكوز. الطاقة تستخدم فوراً أو تخزن.</div> },
      { id: "4", titleAr: "دورك يا بطل", practice: true, content: <div>اشرح كيف يحصل الجسم على الطاقة من الطعام وكيف يتم نقلها إلى الخلايا.</div> },
    ]
  },

  "phase8_chapitres_15_16": {
    titleAr: "الهضم والنقل الدموي",
    phases: [
      { id: "1", titleAr: "مراحل الهضم", content: <div className="text-lg leading-relaxed">الفم: مضغ + لعاب. المعدة: حمض + إنزيمات. الأمعاء الدقيقة: إنزيمات + امتصاص. الأمعاء الغليظة: امتصاص الماء.</div> },
      { id: "2", titleAr: "النقل الدموي", content: <div className="text-lg leading-relaxed">الدم ينقل الأكسجين والمغذيات والهرمونات. القلب يضخ الدم. الشرايين تحمل الدم المؤكسج. الأوردة الدم غير المؤكسج.</div> },
      { id: "3", titleAr: "الدورة الدموية", content: <div className="text-lg leading-relaxed">دورة صغيرة: قلب ← رئتين ← قلب. دورة كبيرة: قلب ← جسم ← قلب. الشعيرات الدموية مكان التبادل.</div> },
      { id: "4", titleAr: "الآن دورك", practice: true, content: <div>صف رحلة الطعام من الفم إلى الخلايا مع التركيز على الامتصاص والنقل.</div> },
    ]
  },

  "phase9_chapitres_17_18": {
    titleAr: "التبادل الغازي والتنظيم الدقيق للتنفس",
    phases: [
      { id: "1", titleAr: "التبادل الغازي", content: <div className="text-lg leading-relaxed">في الحويصلات الرئوية: الأكسجين يدخل الدم وثاني أكسيد الكربون يخرج. الانتشار البسيط عبر الغشاء الرقيق.</div> },
      { id: "2", titleAr: "التنظيم العصبي", content: <div className="text-lg leading-relaxed">مركز التنفس في النخاع المستطيل. يستجيب لمستوى CO2 و pH. يزيد أو يقلل معدل التنفس حسب الحاجة.</div> },
      { id: "3", titleAr: "التنظيم الكيميائي", content: <div className="text-lg leading-relaxed">مستقبلات في الأبهر والسباتي تحس بمستوى الأكسجين. الهرمونات مثل الأدرينالين تزيد التنفس في الجهد.</div> },
      { id: "4", titleAr: "تدرب", practice: true, content: <div>كيف يتكيف الجسم مع الجهد البدني من خلال التنفس؟ اشرح الآليات.</div> },
    ]
  },

  "phase10_chapitres_19_20": {
    titleAr: "الجهد العضلي والتعب العضلي",
    phases: [
      { id: "1", titleAr: "الجهد العضلي", content: <div className="text-lg leading-relaxed">العضلة تحتاج ATP للانقباض. أثناء الجهد: زيادة تدفق الدم + أكسجين + غلوكوز. التنفس يزداد لتوفير الطاقة.</div> },
      { id: "2", titleAr: "الألياف العضلية", content: <div className="text-lg leading-relaxed">ألياف سريعة: قوة كبيرة لكن تتعب سريعاً. ألياف بطيئة: تحمل أكثر ومقاومة التعب. كل عضلة مزيج من الاثنين.</div> },
      { id: "3", titleAr: "التعب العضلي", content: <div className="text-lg leading-relaxed">يحدث بسبب تراكم حمض اللاكتيك + نقص الأكسجين + نفاذ الغليكوجين. الجسم يحتاج راحة لإزالة السموم.</div> },
      { id: "4", titleAr: "دورك الحين", practice: true, content: <div>اشرح أسباب التعب العضلي وكيف يتعافى الجسم بعد التمرين.</div> },
    ]
  },

  "phase11_chapitres_21_22": {
    titleAr: "الحركة عند الإنسان ووضعية الانتصاب",
    phases: [
      { id: "1", titleAr: "الهيكل العظمي", content: <div className="text-lg leading-relaxed">206 عظمة. يحمي الأعضاء ويعطي الشكل. المفاصل تسمح بالحركة. العضلات ترتبط بالعظام عبر الأوتار.</div> },
      { id: "2", titleAr: "آلية الحركة", content: <div className="text-lg leading-relaxed">العضلات تعمل في أزواج: قابضة وباسطة. الانقباض يحرك العظم حول المفصل. الجهاز العصبي يتحكم.</div> },
      { id: "3", titleAr: "وضعية الانتصاب", content: <div className="text-lg leading-relaxed">الإنسان يقف منتصباً بفضل العمود الفقري والحوض والعضلات. مركز الثقل في الحوض. يسمح بالحركة الثنائية.</div> },
      { id: "4", titleAr: "الآن دورك", practice: true, content: <div>صف كيف يعمل العضل والعظم معاً لتحريك الذراع. ما دور المفصل؟</div> },
    ]
  },

  "phase12_chapitres_23_24": {
    titleAr: "البنية الدقيقة للعضلة وآلية التقبض",
    phases: [
      { id: "1", titleAr: "البنية الدقيقة", content: <div className="text-lg leading-relaxed">العضلة مكونة من ألياف. كل ليف من ليفات عضلية. الليفات تحتوي على أكتين وميوزين مرتبة في وحدات تسمى ساركوميرات.</div> },
      { id: "2", titleAr: "نظرية الخيوط المنزلقة", content: <div className="text-lg leading-relaxed">أثناء الانقباض: خيوط الميوزين تسحب خيوط الأكتين. تتقارب خطوط Z. الساركومير يقصر بدون تغير طول الخيوط.</div> },
      { id: "3", titleAr: "دور الكالسيوم وATP", content: <div className="text-lg leading-relaxed">الكالسيوم يكشف مواقع الارتباط. ATP يوفر الطاقة لفصل الرؤوس. بدون ATP تبقى العضلة متيبسة (تيبس الموت).</div> },
      { id: "4", titleAr: "تدرب", practice: true, content: <div>اشرح خطوة بخطوة آلية التقبض العضلي حسب نظرية الخيوط المنزلقة.</div> },
    ]
  },

  "phase13_chapitres_25_26": {
    titleAr: "الطاقة الكامنة وتحويل الطاقة في العضلة",
    phases: [
      { id: "1", titleAr: "مصادر الطاقة في العضلة", content: <div className="text-lg leading-relaxed">ATP المباشر. الكرياتين فوسفات. الغليكوجين (تحلل لا هوائي). التنفس الهوائي. كل مصدر له سرعة ومدة مختلفة.</div> },
      { id: "2", titleAr: "تحويل الطاقة", content: <div className="text-lg leading-relaxed">الطاقة الكيميائية في الغذاء → طاقة كيميائية في ATP → طاقة ميكانيكية في الانقباض. حرارة تنتج كمنتج ثانوي.</div> },
      { id: "3", titleAr: "الكفاءة", content: <div className="text-lg leading-relaxed">فقط 40% من الطاقة تصبح حركة. الباقي حرارة. الرياضيون يحسنون الكفاءة بالتدريب.</div> },
      { id: "4", titleAr: "يلا نجرب", practice: true, content: <div>كيف يتم تحويل الطاقة أثناء الركض السريع؟ قارن بين المصادر المختلفة.</div> },
    ]
  },

  "phase14_chapitres_27_28": {
    titleAr: "النشاط الإنزيمي للعضلة وتنظيم الفعل العضلي",
    phases: [
      { id: "1", titleAr: "الإنزيمات في العضلة", content: <div className="text-lg leading-relaxed">إنزيمات التحلل الغليكوجيني. إنزيمات دورة كريبس. إنزيم ATPase. كلها تعمل بتنسيق لإنتاج ATP.</div> },
      { id: "2", titleAr: "التنظيم العصبي", content: <div className="text-lg leading-relaxed">الخلايا العصبية الحركية ترسل إشارات. الصفيحة الحركية تطلق الأسيتيل كولين. يسبب تقلص الألياف.</div> },
      { id: "3", titleAr: "التنظيم الهرموني", content: <div className="text-lg leading-relaxed">الأدرينالين يزيد من سرعة التحلل. يرفع مستوى الطاقة. الكورتيزول يساعد في التعافي.</div> },
      { id: "4", titleAr: "الآن دورك", practice: true, content: <div>كيف يتحكم الجهاز العصبي والهرمونات في النشاط العضلي أثناء التمرين؟</div> },
    ]
  },

  "phase15_chapitres_29_30": {
    titleAr: "الخصائص العامة للظواهر التكتونية",
    phases: [
      { id: "1", titleAr: "شنو هي التكتونية؟", content: <div className="text-lg leading-relaxed">حركة الصفائح الصخرية على سطح الأرض. تسبب البراكين والزلازل والجبال. الصفائح تتحرك ببطء شديد بسبب الحرارة داخل الأرض.</div> },
      { id: "2", titleAr: "أنواع الحدود", content: <div className="text-lg leading-relaxed">تباعد: براكين وأخاديد. تصادم: جبال وبراكين. انزلاق: زلازل قوية. كل نوع له نتائج جيولوجية مختلفة.</div> },
      { id: "3", titleAr: "الأدلة على التكتونية", content: <div className="text-lg leading-relaxed">شكل القارات. الصخور المتشابهة. الحفريات. الزلازل على خطوط معينة. الحرارة في قاع المحيطات.</div> },
      { id: "4", titleAr: "دورك الحين", practice: true, content: <div>اشرح كيف تتكون البراكين والجبال من حركة الصفائح. أعط مثالين من العالم.</div> },
    ]
  },

  "phase16_chapitres_31_32": {
    titleAr: "بنية الغلاف الصخري وحركية الصفائح",
    phases: [
      { id: "1", titleAr: "الغلاف الصخري", content: <div className="text-lg leading-relaxed">الطبقة الخارجية الصلبة من الأرض. تتكون من القشرة والجزء العلوي من الوشاح. مقسمة إلى صفائح تكتونية كبيرة.</div> },
      { id: "2", titleAr: "حركة الصفائح", content: <div className="text-lg leading-relaxed">تتحرك بسبب التيارات الحرارية في الوشاح. 5-10 سم في السنة. مدفوعة بالحمل الحراري والجاذبية.</div> },
      { id: "3", titleAr: "الصفائح الرئيسية", content: <div className="text-lg leading-relaxed">صفيحة أوراسية، أفريقية، أمريكية، باسيفيكية، هندية. كل واحدة تتحرك باتجاه مختلف.</div> },
      { id: "4", titleAr: "تدرب", practice: true, content: <div>كيف تتحرك الصفائح؟ وما دور التيارات الحرارية في الوشاح؟</div> },
    ]
  },

  "phase17_chapitres_33_34": {
    titleAr: "الحدود المتقاربة والمتباعدة",
    phases: [
      { id: "1", titleAr: "الحدود المتباعدة", content: <div className="text-lg leading-relaxed">صفيحتان تبتعدان. يتكون قاع محيط جديد. براكين وأخاديد. مثال: وسط الأطلسي.</div> },
      { id: "2", titleAr: "الحدود المتقاربة", content: <div className="text-lg leading-relaxed">صفيحتان تتصادمان. واحدة تغوص تحت الأخرى. جبال، براكين، خنادق. مثال: جبال الهيمالايا وخندق الماريانا.</div> },
      { id: "3", titleAr: "النتائج", content: <div className="text-lg leading-relaxed">تباعد: توسع المحيطات. تقارب: تشكل السلاسل الجبلية والبراكين. كلاهما يسبب زلازل.</div> },
      { id: "4", titleAr: "دورك", practice: true, content: <div>قارن بين الحدود المتباعدة والمتقاربة مع أمثلة ونتائج كل نوع.</div> },
    ]
  },

  "phase18_chapitres_35_36": {
    titleAr: "التحولات الباطنية والبنية الداخلية للأرض",
    phases: [
      { id: "1", titleAr: "البنية الداخلية", content: <div className="text-lg leading-relaxed">القشرة: رقيقة. الوشاح: سميك ساخن. اللب الخارجي: سائل. اللب الداخلي: صلب. كل طبقة لها خصائص مختلفة.</div> },
      { id: "2", titleAr: "التحولات الباطنية", content: <div className="text-lg leading-relaxed">الصهارة تتكون في الوشاح. تتحرك للأعلى. تسبب البراكين. الضغط والحرارة يغيران الصخور.</div> },
      { id: "3", titleAr: "الدليل", content: <div className="text-lg leading-relaxed">الموجات الزلزالية تكشف الطبقات. سرعة الموجات تتغير حسب الكثافة. نعرف البنية بدون حفر عميق.</div> },
      { id: "4", titleAr: "الآن دورك", practice: true, content: <div>صف البنية الداخلية للأرض وكيف تسبب التحولات الباطنية البراكين.</div> },
    ]
  },

  "phase19_chapitres_37_38": {
    titleAr: "الزلازل والموجات الزلزالية",
    phases: [
      { id: "1", titleAr: "ما هي الزلازل؟", content: <div className="text-lg leading-relaxed">اهتزاز مفاجئ للأرض بسبب تحرر الطاقة عند حدود الصفائح. يحدث على طول الفوالق. مقياس ريختر يقيس القوة.</div> },
      { id: "2", titleAr: "الموجات الزلزالية", content: <div className="text-lg leading-relaxed">موجات P: سريعة، طولية. موجات S: أبطأ، عرضية. موجات سطحية: تسبب الدمار الأكبر. تنتقل عبر الأرض.</div> },
      { id: "3", titleAr: "التنبؤ والوقاية", content: <div className="text-lg leading-relaxed">لا يمكن التنبؤ بدقة. لكن نعرف المناطق الخطرة. المباني المقاومة للزلازل تنقذ الأرواح.</div> },
      { id: "4", titleAr: "يلا تدرب", practice: true, content: <div>اشرح أنواع الموجات الزلزالية وكيف تساعد في دراسة باطن الأرض.</div> },
    ]
  },

  "phase20_chapitres_39_40": {
    titleAr: "التشوهات التكتونية: الطيات والفوالق",
    phases: [
      { id: "1", titleAr: "الطيات", content: <div className="text-lg leading-relaxed">انحناء الصخور بسبب الضغط. أنواع: محدبة ومقعرة. تتشكل الجبال الكبيرة من الطيات الكبيرة.</div> },
      { id: "2", titleAr: "الفوالق", content: <div className="text-lg leading-relaxed">كسر في الصخور مع حركة. أنواع: عادية، معكوسة، انزلاقية. الزلازل تحدث على طول الفوالق النشطة.</div> },
      { id: "3", titleAr: "النتائج الجيولوجية", content: <div className="text-lg leading-relaxed">الطيات والفوالق تشكل السلاسل الجبلية والأودية. تؤثر على توزيع المعادن والمياه الجوفية.</div> },
      { id: "4", titleAr: "دورك الحين", practice: true, content: <div>قارن بين الطيات والفوالق مع رسم بسيط وأمثلة من الطبيعة.</div> },
    ]
  },

  "phase21_chapitres_41_42": {
    titleAr: "تشكل السلاسل الجبلية وظاهرة الحركات البانية",
    phases: [
      { id: "1", titleAr: "تشكل الجبال", content: <div className="text-lg leading-relaxed">نتيجة تصادم الصفائح. الصخور تطوى وترتفع. أمثلة: الألب، الهيمالايا، الأطلس في المغرب.</div> },
      { id: "2", titleAr: "الحركات البانية", content: <div className="text-lg leading-relaxed">حركات بطيئة ترفع القشرة. تستمر ملايين السنين. تسبب ارتفاع الجبال وتغير المناخ.</div> },
      { id: "3", titleAr: "التآكل والتشكيل", content: <div className="text-lg leading-relaxed">بعد التشكل، الرياح والمياه والجليد تآكل الجبال. يتشكل الوادي والسهول. عملية مستمرة.</div> },
      { id: "4", titleAr: "تدرب", practice: true, content: <div>اشرح كيف تتشكل السلاسل الجبلية وما دور الحركات البانية والتآكل.</div> },
    ]
  },

  "phase22_chapitres_43_44": {
    titleAr: "العلاقة بين التكتونية والرسوبيات والتطبيقات",
    phases: [
      { id: "1", titleAr: "الرسوبيات والتكتونية", content: <div className="text-lg leading-relaxed">التكتونية تؤثر على الترسيب. الحركات تخلق أحواض رسوبية. الصخور الرسوبية تحفظ تاريخ الحركات.</div> },
      { id: "2", titleAr: "التطبيقات الجيولوجية", content: <div className="text-lg leading-relaxed">البحث عن النفط والغاز في الطيات. المعادن في المناطق البركانية. الزلازل والبراكين للتنبؤ بالمخاطر.</div> },
      { id: "3", titleAr: "أهمية للجزائر", content: <div className="text-lg leading-relaxed">الجزائر في منطقة نشطة تكتونياً. جبال الأطلس. الزلازل في الشمال. دراسة التكتونية مهمة للسلامة والموارد.</div> },
      { id: "4", titleAr: "الخاتمة - دورك", practice: true, content: <div>لخص العلاقة بين التكتونية والرسوبيات وأعطِ تطبيقين عمليين في الجزائر.</div> },
    ]
  },

  default: {
    titleAr: "درس تفاعلي شامل",
    phases: [
      { id: "1", titleAr: "المقدمة", content: <div className="text-lg leading-relaxed">هذا الدرس يشرح المفهوم الأساسي في العلوم التجريبية. ركز على العلاقة بين البنية والوظيفة. كل شيء مترابط في الطبيعة.</div> },
      { id: "2", titleAr: "المفاهيم الرئيسية", content: <div className="text-lg leading-relaxed">تحليل الوثائق + استنتاج + تفسير. استخدم المصطلحات العلمية بدقة. البنية تحدد الوظيفة دائماً.</div> },
      { id: "3", titleAr: "أمثلة تطبيقية", content: <div className="text-lg leading-relaxed">من البروتينات إلى الصفائح التكتونية. كل درس يبني على السابق. التكرار يقوي الذاكرة.</div> },
      { id: "4", titleAr: "دورك الحين - تدرب", practice: true, content: <div>اكتب إجابة كاملة باستخدام كلمات: بنية، وظيفة، علاقة، تحليل. ركز واربح نقاط البكالوريا!</div> },
    ]
  }
}

const QCMS: Record<string, any[]> = {
  "phase1_chapitres_1_2": [
    { id: 1, question: "البروتينات تتكون أساساً من؟", options: ["الأحماض الأمينية", "السكريات", "الدهون", "الأملاح"], correct: 0 },
    { id: 2, question: "البنية الثالثية هي؟", options: ["الطي ثلاثي الأبعاد", "تسلسل فقط", "صفائح بيتا", "سلسلة خطية"], correct: 0 },
  ],
  "phase2_chapitres_3_4": [
    { id: 1, question: "الإنزيم هو", options: ["بروتين محفز", "سكر", "دهن", "ماء"], correct: 0 },
    { id: 2, question: "يؤثر على الإنزيم بشكل كبير", options: ["الحرارة و pH", "الضوء فقط", "الريح", "الصوت"], correct: 0 },
  ],
  "phase15_chapitres_29_30": [
    { id: 1, question: "سبب البراكين الرئيسي؟", options: ["حركة الصفائح", "الرياح", "الأمطار", "الشمس"], correct: 0 },
    { id: 2, question: "الحدود المتقاربة تشكل؟", options: ["جبال وبراكين", "براكين فقط", "سهول", "أنهار"], correct: 0 },
  ],
  default: [
    { id: 1, question: "المفهوم الأساسي في العلوم التجريبية؟", options: ["البنية والوظيفة", "الحفظ فقط", "الرسم", "الكتابة"], correct: 0 },
    { id: 2, question: "أفضل طريقة للإجابة في البكالوريا؟", options: ["استخدام المصطلحات بدقة", "الكتابة الطويلة", "الرسوم فقط", "الرأي الشخصي"], correct: 0 },
  ]
}

function getQCMForSlug(slug: string) {
  if (QCMS[slug]) return QCMS[slug]
  const lesson = GENZ_LESSONS[slug] || GENZ_LESSONS.default
  const title = lesson.titleAr
  return [
    { id: 1, question: `ما هو المفهوم الأساسي في "${title}"؟`, options: ["البنية والوظيفة", "الحفظ فقط", "الرسم", "الكتابة"], correct: 0 },
    { id: 2, question: "أفضل طريقة للإجابة في البكالوريا؟", options: ["استخدام المصطلحات بدقة", "الكتابة الطويلة", "الرسوم فقط", "الرأي الشخصي"], correct: 0 },
    { id: 3, question: "كيف يجب أن تكون الإجابة؟", options: ["دقيقة ومنظمة", "طويلة جداً", "بدون مصطلحات", "رأي شخصي"], correct: 0 },
  ]
}

export default function GenZPhaseLesson() {
  const params = useParams()
  const slug = (params?.slug as string) || "default"

  const lesson = GENZ_LESSONS[slug] || GENZ_LESSONS.default
  const qcms = getQCMForSlug(slug)

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto px-4 pt-5 pb-20" dir="rtl">
        <Link href="/lecons-sciences-experimentales" className="text-mint text-sm hover:underline inline-block mb-4">
          ← التجارب المقررة
        </Link>

        <div className="mb-6">
          <div className="inline px-3 py-1 text-xs font-black bg-mint/10 text-mint rounded-full">
            GEN Z • تفاعلي • 17 سنة • بكالوريا 2026
          </div>
          <h1 className="text-4xl font-black tracking-[-1px] mt-2">{lesson.titleAr}</h1>
          <p className="text-white/60 text-sm">درس تفاعلي ديناميكي — خطوة بخطوة مثل الأفعال الأدائية 🔥</p>
        </div>

        <GenZInteractiveLesson
          lessonTitleAr={lesson.titleAr}
          phases={lesson.phases}
          slug={slug}
        />

        <div className="mt-12">
          <div className="text-center mb-3">
            <span className="px-3 py-0.5 bg-orange-500/10 text-orange-400 text-xs font-black rounded-full">QCM سريع • اختبر نفسك</span>
          </div>
          <h3 className="text-center font-bold text-2xl mb-5">اختبر نفسك الآن يا خويا</h3>
          <GenZQCMFlow titleAr="اختبار الدرس" questions={qcms} />
        </div>

        <div className="text-center text-[10px] text-white/30 mt-16">
          البكالوريا 2026 • جيل زد • كل شيء بالعربية • بدون محتوى فارغ
        </div>
      </div>
    </AppShell>
  )
}
