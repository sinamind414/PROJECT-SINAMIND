"""Génère le Golden Set ONEC — 50 questions/réponses corrigées SVT 3AS.

Couvre les 8 chapitres principaux du programme officiel.
Structure: id, chapitre, niveau (L1/L2/L3), question (AR), reponse_attendue (AR),
mots_cles_attendus, bareme, type (restitution/application/type_bac).
"""

import json
import pathlib

QUESTIONS = []

# ── Chapitre 1: Synthèse des protéines (8 questions) ──
QUESTIONS.extend(
    [
        {
            "id": "gs_001",
            "chapitre": "Synthèse des protéines",
            "chapitre_id": "ch1_proteines",
            "niveau": "L1",
            "question": "أين يحدث نسخ المعلومة الوراثية في الخلية حقيقية النواة؟",
            "reponse_attendue": "يحدث نسخ المعلومة الوراثية في النواة حيث تتواجد جزيئة ADN",
            "mots_cles_attendus": ["النواة", "ADN", "نسخ"],
            "bareme": 2,
            "type": "restitution",
        },
        {
            "id": "gs_002",
            "chapitre": "Synthèse des protéines",
            "chapitre_id": "ch1_proteines",
            "niveau": "L1",
            "question": "ما هو دور الرنا الرسول (ARNm) في تركيب البروتينات؟",
            "reponse_attendue": "ينقل الرنا الرسول نسخة من المعلومة الوراثية من ADN الموجود في النواة إلى الريبوزوم في الهيولى حيث تتم ترجمة هذه المعلومة لتركيب البروتين",
            "mots_cles_attendus": ["نقل", "معلومة", "الريبوزوم", "الهيولى"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_003",
            "chapitre": "Synthèse des protéines",
            "chapitre_id": "ch1_proteines",
            "niveau": "L1",
            "question": "ما هي الشفرة الوراثية؟",
            "reponse_attendue": "الشفرة الوراثية هي مجموعة القواعد الثلاثية المتتالية (الكودونات) في جزيئة ARNm التي تحدد نوع الأحماض الأمينية في البروتين المراد تركيبه",
            "mots_cles_attendus": ["كودونات", "قواعد", "ثلاثية", "أحماض أمينية"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_004",
            "chapitre": "Synthèse des protéines",
            "chapitre_id": "ch1_proteines",
            "niveau": "L2",
            "question": "اشرح مراحل ترجمة ARNm إلى بروتين",
            "reponse_attendue": "ترجمة ARNm تمر بثلاث مراحل: 1- بدء الترجمة: ارتباط الوحدة الصغيرة للريبوزوم مع ARNm ثم ارتباط ARNt البادئ، 2- الاستطالة: إضافة الأحماض الأمينية المتتالية بواسطة ARNt حسب كودونات ARNm، 3- الإنهاء: عند الوصول لكودون التوقف ينفصل البروتين المركب",
            "mots_cles_attendus": ["بدء", "استطالة", "إنهاء", "ريبوزوم", "ARNt", "كودون"],
            "bareme": 5,
            "type": "application",
        },
        {
            "id": "gs_005",
            "chapitre": "Synthèse des protéines",
            "chapitre_id": "ch1_proteines",
            "niveau": "L1",
            "question": "ما هو دور ARN الناقل (ARNt)؟",
            "reponse_attendue": "ينقل ARNt الأحماض الأمينية المناسبة إلى الريبوزوم حسب الترميز الذي يحمله كل كودون في ARNm، وكل ARNt يحمل كودونا مضادا (anticodon) يطابق الكودون",
            "mots_cles_attendus": ["نقل", "أحماض أمينية", "كودون مضاد", "anticodon"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_006",
            "chapitre": "Synthèse des protéines",
            "chapitre_id": "ch1_proteines",
            "niveau": "L2",
            "question": "حدد الشروط الضرورية لترجمة ARNm",
            "reponse_attendue": "الشروط الضرورية لترجمة ARNm هي: 1- وجود ARNm، 2- وجود الأحماض الأمينية، 3- وجود إنزيم خاص بكل حمض أميني، 4- وجود الطاقة (ATP)، 5- وجود ARNt، 6- وجود الريبوزومات",
            "mots_cles_attendus": ["ARNm", "أحماض أمينية", "إنزيم", "ATP", "ARNt", "ريبوزوم"],
            "bareme": 4,
            "type": "application",
        },
        {
            "id": "gs_007",
            "chapitre": "Synthèse des protéines",
            "chapitre_id": "ch1_proteines",
            "niveau": "L3",
            "question": "صف مراحل تركيب البروتين انطلاقا من نسخ ADN إلى ترجمة ARNm",
            "reponse_attendue": "1- النسخ: في النواة، تنفتح جزيئة ADN وتنسخ إحدى سلسلتيها إلى ARNm بواسطة إنزيم ARN بوليميراز، 2- خروج ARNm من النواة إلى الهيولى، 3- الترجمة: يرتبط ARNm بالريبوزوم، يأتي ARNt حاملا الأحماض الأمينية حسب الكودونات، تتشكل الروابط الببتيدية، 4- ينفصل البروتين المركب عند كودون التوقف",
            "mots_cles_attendus": ["نسخ", "ADN", "ARNm", "ريبوزوم", "ARNt", "روابط ببتيدية", "كودون توقف"],
            "bareme": 6,
            "type": "type_bac",
        },
        {
            "id": "gs_008",
            "chapitre": "Synthèse des protéines",
            "chapitre_id": "ch1_proteines",
            "niveau": "L1",
            "question": "ما هو دور الريبوزوم في تركيب البروتين؟",
            "reponse_attendue": "الريبوزوم هو عضية تتوضع في الهيولى، دوره هو قراءة ARNm وربط الأحماض الأمينية فيما بينها بروابط ببتيدية لتشكيل البروتين، يتكون من وحدتين صغيرة وكبيرة",
            "mots_cles_attendus": ["الهيولى", "قراءة", "ARNm", "روابط ببتيدية", "وحدتين"],
            "bareme": 3,
            "type": "restitution",
        },
    ]
)

# ── Chapitre 2: Structure des protéines (5 questions) ──
QUESTIONS.extend(
    [
        {
            "id": "gs_009",
            "chapitre": "Structure des protéines",
            "chapitre_id": "ch_structure_proteines",
            "niveau": "L1",
            "question": "ما هي البنية الأولية للبروتين؟",
            "reponse_attendue": "البنية الأولية للبروتين هي الترتيب المتسلسل للأحماض الأمينية المرتبطة فيما بينها بروابط ببتيدية لتشكيل سلسلة ببتيدية",
            "mots_cles_attendus": ["ترتيب", "أحماض أمينية", "روابط ببتيدية", "سلسلة"],
            "bareme": 2,
            "type": "restitution",
        },
        {
            "id": "gs_010",
            "chapitre": "Structure des protéines",
            "chapitre_id": "ch_structure_proteines",
            "niveau": "L1",
            "question": "كيف تتشكل البنية الثالثية للبروتين؟",
            "reponse_attendue": "تتشكل البنية الثالثية للبروتين نتيجة التفاف السلسلة الببتيدية ذات البنية الثانوية في الفضاء لتأخذ شكلا كرويا، وتنتج عن روابط بين المجموعات الجانبية (R) للأحماض الأمينية",
            "mots_cles_attendus": ["التلاف", "كروي", "مجموعات جانبية", "روابط"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_011",
            "chapitre": "Structure des protéines",
            "chapitre_id": "ch_structure_proteines",
            "niveau": "L2",
            "question": "اشرح العلاقة بين بنية البروتين ووظيفته",
            "reponse_attendue": "هناك علاقة طردية بين بنية البروتين ووظيفته: فالبنية المكانية للبروتين تحدد موقعه الفعال الذي يرتبط بالركيزة، وأي تغير في البنية يؤدي إلى تغير الوظيفة. مثال: إنزيم الأميلاز له بنية تسمح له بالارتباط بالنشا وتفكيكه",
            "mots_cles_attendus": ["بنية", "وظيفة", "موقع فعال", "ركيزة"],
            "bareme": 4,
            "type": "application",
        },
        {
            "id": "gs_012",
            "chapitre": "Structure des protéines",
            "chapitre_id": "ch_structure_proteines",
            "niveau": "L1",
            "question": "ما الفرق بين البنية الثانوية الحلزونية والصفائحية؟",
            "reponse_attendue": "البنية الثانوية الحلزونية تأخذ شكل لولبي نتيجة الروابط الهيدروجينية بين مجموعات CO و NH المتجاورة، بينما الصفائحية تأخذ شكل صفائح مطوية نتيجة الروابط الهيدروجينية بين سلاسل ببتيدية متجاورة",
            "mots_cles_attendus": ["لولبي", "صفائح", "روابط هيدروجينية"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_013",
            "chapitre": "Structure des protéines",
            "chapitre_id": "ch_structure_proteines",
            "niveau": "L3",
            "question": "بين انطلاقا من دراسة بروتينات الدم (الغلوبولينات) العلاقة بين البنية والوظيفة",
            "reponse_attendue": "الغلوبولينات (الأجسام المضادة) بروتينات ذات بنية ثالثية ورباعية تسمح لها بالتعرف النوعي على المستضدات، فالموقع الفعال لكل غلوبولين متمم لبنية مستضد محدد، مما يثبت أن البنية المكانية تحدد الوظيفة",
            "mots_cles_attendus": ["غلوبولينات", "بنية", "موقع فعال", "مستضد", "تمامة", "وظيفة"],
            "bareme": 5,
            "type": "type_bac",
        },
    ]
)

# ── Chapitre 3: Activité enzymatique (5 questions) ──
QUESTIONS.extend(
    [
        {
            "id": "gs_014",
            "chapitre": "Activité enzymatique",
            "chapitre_id": "ch2_enzymes",
            "niveau": "L1",
            "question": "ما هو الموقع الفعال للإنزيم؟",
            "reponse_attendue": "الموقع الفعال للإنزيم هو المنطقة التي يرتبط فيها الركيزة ويتفاعل معها، وهو ذو بنية مكانية متممة لبنية الركيزة",
            "mots_cles_attendus": ["موقع", "ركيزة", "متممة", "بنية"],
            "bareme": 2,
            "type": "restitution",
        },
        {
            "id": "gs_015",
            "chapitre": "Activité enzymatique",
            "chapitre_id": "ch2_enzymes",
            "niveau": "L1",
            "question": "ماذا نقصد بالنوعية الإنزيمية؟",
            "reponse_attendue": "النوعية الإنزيمية هي خاصية الإنزيم التي تجعله يتعرف على ركيزة محددة فقط ويفككها أو يركبها، وذلك بسبب التمامة بين الموقع الفعال والركيزة",
            "mots_cles_attendus": ["نوعية", "ركيزة", "موقع فعال", "تمامة"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_016",
            "chapitre": "Activité enzymatique",
            "chapitre_id": "ch2_enzymes",
            "niveau": "L2",
            "question": "كيف تؤثر درجة الحرارة على نشاط الإنزيم؟",
            "reponse_attendue": "تزداد سرعة التفاعل الإنزيمي مع ارتفاع درجة الحرارة حتى تصل إلى درجة الحرارة المثلى (حوالي 37 درجة في الإنسان) حيث تكون السرعة قصوى، ثم تنخفض السرعة عند درجات حرارة أعلى بسبب تمسخ الإنزيم وتغير بنيته المكانية",
            "mots_cles_attendus": ["حرارة مثلى", "تمسخ", "بنية", "سرعة"],
            "bareme": 4,
            "type": "application",
        },
        {
            "id": "gs_017",
            "chapitre": "Activité enzymatique",
            "chapitre_id": "ch2_enzymes",
            "niveau": "L2",
            "question": "اشرح آلية تثبيط الإنزيم التنافسي",
            "reponse_attendue": "التثبيط التنافسي يحدث عندما يشبه المثبط بنية الركيزة فيرتبط بالموقع الفعال للإنزيم بدلا من الركيزة، مما يمنع الركيزة من الارتباط. يمكن التغلب على هذا التثبيط بزيادة تركيز الركيزة",
            "mots_cles_attendus": ["مثبط", "موقع فعال", "ركيزة", "تركيز"],
            "bareme": 4,
            "type": "application",
        },
        {
            "id": "gs_018",
            "chapitre": "Activité enzymatique",
            "chapitre_id": "ch2_enzymes",
            "niveau": "L3",
            "question": "بين انطلاقا من تجربة أن نشاط الإنزيم يتأثر بدرجة الـ pH",
            "reponse_attendue": "نأخذ عدة أنابيب اختبار نضع في كل منها نفس كمية الإنزيم ونفس كمية الركيزة ولكن نغير درجة الـ pH من 2 إلى 10، نقيس سرعة التفاعل في كل أنبوب. النتائج: تكون السرعة قصوى عند pH محدد (الـ pH الأمثل) وتنخفض عند باقي قيم الـ pH. الاستنتاج: نشاط الإنزيم يتأثر بدرجة الـ pH وكل إنزيم له pH أمثل",
            "mots_cles_attendus": ["تجربة", "pH", "سرعة", "pH أمثل", "استنتاج"],
            "bareme": 5,
            "type": "type_bac",
        },
    ]
)

# ── Chapitre 4: Immunologie (6 questions) ──
QUESTIONS.extend(
    [
        {
            "id": "gs_019",
            "chapitre": "Immunologie",
            "chapitre_id": "ch3_immunite",
            "niveau": "L1",
            "question": "ما الفرق بين الخلايا الليمفاوية B و T؟",
            "reponse_attendue": "الخلايا الليمفاوية B مسؤولة عن الاستجابة المناعية الخلطية (إنتاج الأجسام المضادة)، بينما الخلايا الليمفاوية T مسؤولة عن الاستجابة المناعية الخلوية (التدمير المباشر للخلايا المصابة)",
            "mots_cles_attendus": ["B", "T", "خلطية", "خلوية", "أجسام مضادة"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_020",
            "chapitre": "Immunologie",
            "chapitre_id": "ch3_immunite",
            "niveau": "L1",
            "question": "ما هو المستضد؟",
            "reponse_attendue": "المستضد هو كل جسم غريب يدخل الجسم ويثير استجابة مناعية، فيتعرف عليه الجهاز المناعي ويحفز إنتاج الأجسام المضادة النوعية ضده",
            "mots_cles_attendus": ["جسم غريب", "استجابة", "أجسام مضادة"],
            "bareme": 2,
            "type": "restitution",
        },
        {
            "id": "gs_021",
            "chapitre": "Immunologie",
            "chapitre_id": "ch3_immunite",
            "niveau": "L1",
            "question": "ما هي الأجسام المضادة؟",
            "reponse_attendue": "الأجسام المضادة هي بروتينات (غلوبولينات مناعية) تنتجها الخلايا الليمفاوية B المتمايزة إلى خلايا بلازمية، ترتبط نوعيا مع المستضد لتحيده وتمنع تأثيره",
            "mots_cles_attendus": ["بروتينات", "غلوبولينات", "B", "خلايا بلازمية", "نوعيا"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_022",
            "chapitre": "Immunologie",
            "chapitre_id": "ch3_immunite",
            "niveau": "L2",
            "question": "اشرح مراحل الاستجابة المناعية الخلطية",
            "reponse_attendue": "1- التعرف: تتعرف الخلايا الليمفاوية B على المستضد، 2- التنشيط: تنشط الخلايا B وتتكاثر، 3- التمايز: تتمايز إلى خلايا بلازمية (تنتج الأجسام المضادة) وخلايا ذاكرة، 4- الإنتاج: تنتج الخلايا البلازمية الأجسام المضادة النوعية التي ترتبط بالمستضد وحيده",
            "mots_cles_attendus": ["تعرف", "تنشيط", "تمايز", "خلايا بلازمية", "أجسام مضادة", "ذاكرة"],
            "bareme": 5,
            "type": "application",
        },
        {
            "id": "gs_023",
            "chapitre": "Immunologie",
            "chapitre_id": "ch3_immunite",
            "niveau": "L2",
            "question": "ما المقصود بالذاكرة المناعية؟",
            "reponse_attendue": "الذاكرة المناعية هي قدرة الجهاز المناعي على الاحتفاظ بخلايا ذاكرة بعد الاستجابة المناعية الأولى، فعند دخول نفس المستضد مرة ثانية تكون الاستجابة أسرع وأقوى لأن خلايا الذاكرة تتذكر المستضد",
            "mots_cles_attendus": ["خلايا ذاكرة", "أسرع", "أقوى", "نفس المستضد"],
            "bareme": 3,
            "type": "application",
        },
        {
            "id": "gs_024",
            "chapitre": "Immunologie",
            "chapitre_id": "ch3_immunite",
            "niveau": "L3",
            "question": "حلل تجربة تثبت دور الخلايا الليمفاوية T في الاستجابة المناعية الخلوية",
            "reponse_attendue": "نأخذ فأرين: الفأر الأول سليم والفأر الثاني مستأصل منه الغدة التيموسية. نحقن كلاهما بنفس المستضد. النتائج: الفأر السليم يظهر استجابة خلوية طبيعية، الفأر المستأصل التيموس لا يظهر استجابة خلوية. الاستنتاج: الخلايا الليمفاوية T مسؤولة عن الاستجابة المناعية الخلوية وتتطور في الغدة التيموسية",
            "mots_cles_attendus": ["تيموس", "T", "خلوية", "استجابة", "استنتاج"],
            "bareme": 5,
            "type": "type_bac",
        },
    ]
)

# ── Chapitre 5: Transmission nerveuse (6 questions) ──
QUESTIONS.extend(
    [
        {
            "id": "gs_025",
            "chapitre": "Transmission nerveuse",
            "chapitre_id": "ch4_nerveux",
            "niveau": "L1",
            "question": "ما هو كمون الراحة؟",
            "reponse_attendue": "كمون الراحة هو الفرق في الشحنات الكهربائية بين وجهي الغشاء الخلوي في حالة الراحة، يكون داخل الخلية سالبا بالنسبة للخارج (حوالي -70 ميليفولت)",
            "mots_cles_attendus": ["الراحة", "الغشاء", "سالبا", "-70", "فرق"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_026",
            "chapitre": "Transmission nerveuse",
            "chapitre_id": "ch4_nerveux",
            "niveau": "L1",
            "question": "ما هو كمون العمل؟",
            "reponse_attendue": "كمون العمل هو انعكاس سريع ومؤقت في قطبية الغشاء العصبي عند التنبيه الفعال، يصبح داخل الليف موجبا بالنسبة للخارج ثم يعود لكمون الراحة",
            "mots_cles_attendus": ["انعكاس", "قطبية", "موجبا", "تنبيه", "فعال"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_027",
            "chapitre": "Transmission nerveuse",
            "chapitre_id": "ch4_nerveux",
            "niveau": "L1",
            "question": "ما هو المشبك الكيميائي؟",
            "reponse_attendue": "المشبك الكيميائي هو منطقة الاتصال بين عصبونين أو بين عصبون وخلية مستجيبة، يتم فيه نقل الرسالة العصبية بواسطة نواقل كيميائية تنتشر من الطرف قبل المشبكي إلى الطرف بعد المشبكي",
            "mots_cles_attendus": ["اتصال", "نواقل كيميائية", "قبل مشبكي", "بعد مشبكي"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_028",
            "chapitre": "Transmission nerveuse",
            "chapitre_id": "ch4_nerveux",
            "niveau": "L2",
            "question": "اشرح آلية انتقال الرسالة العصبية عبر المشبك الكيميائي",
            "reponse_attendue": "1- وصول كمون العمل للطرف قبل المشبكي، 2- دخول شوارد الكالسيوم، 3- إفراز الحويصلات للنواقل العصبية في الشق المشبكي، 4- ارتباط النواقل بالمستقبلات على الغشاء بعد المشبكي، 5- توليد كمون عمل جديد في الخلية بعد المشبكية",
            "mots_cles_attendus": ["كمون عمل", "كالسيوم", "حويصلات", "نواقل", "مستقبلات", "شق مشبكي"],
            "bareme": 5,
            "type": "application",
        },
        {
            "id": "gs_029",
            "chapitre": "Transmission nerveuse",
            "chapitre_id": "ch4_nerveux",
            "niveau": "L2",
            "question": "ما هي النواقل العصبية؟ أعط أمثلة",
            "reponse_attendue": "النواقل العصبية هي جزيئات كيميائية تنتقل من العصبون قبل المشبكي إلى العصبون بعد المشبكي لنقل الرسالة العصبية. أمثلة: الأستيل كولين، الدوبامين، السيروتونين، GABA",
            "mots_cles_attendus": ["جزيئات", "كيميائية", "أستيل كولين", "دوبامين", "GABA"],
            "bareme": 3,
            "type": "application",
        },
        {
            "id": "gs_030",
            "chapitre": "Transmission nerveuse",
            "chapitre_id": "ch4_nerveux",
            "niveau": "L3",
            "question": "حلل تجربة تثبت أن الناقل العصبي الأستيل كولين مسؤول عن نقل الرسالة في المشبك",
            "reponse_attendue": "نضع إلكترودين قبل وبعد المشبكي، ننبه العصبون قبل المشبكي فنسجل كمون عمل في الجهتين. ثم نحقن مادة تثبط إنزيم أستيل كولين إستراز (الذي يفكك الأستيل كولين) فنلاحظ استمرار الاستجابة بعد المشبكية. نستنتج أن الأستيل كولين هو الناقل العصبي وأن إنزيم أستيل كولين إستراز يوقف تأثيره",
            "mots_cles_attendus": ["أستيل كولين", "إلكترود", "إنزيم", "أستيل كولين إستراز", "استنتاج"],
            "bareme": 6,
            "type": "type_bac",
        },
    ]
)

# ── Chapitre 6: Photosynthèse (5 questions) ──
QUESTIONS.extend(
    [
        {
            "id": "gs_031",
            "chapitre": "Photosynthèse",
            "chapitre_id": "ch5_photosynthese",
            "niveau": "L1",
            "question": "ما هي Photosynthèse (البناء الضوئي)؟",
            "reponse_attendue": "البناء الضوئي هو عملية حيوية تحدث في البلاستيدات الخضراء حيث تصنع المادة العضوية (الغلوكوز) انطلاقا من المادة المعدنية (CO2 والماء) باستخدام الطاقة الضوئية",
            "mots_cles_attendus": ["بلاستيدات خضراء", "مادة عضوية", "CO2", "ماء", "طاقة ضوئية"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_032",
            "chapitre": "Photosynthèse",
            "chapitre_id": "ch5_photosynthese",
            "niveau": "L1",
            "question": "أين تحدث عملية البناء الضوئي؟",
            "reponse_attendue": "تحدث عملية البناء الضوئي في البلاستيدات الخضراء الموجودة في خلايا الأوراق، وتحديدا في الثايلاكويدات التي تحتوي على صبغة الكلوروفيل",
            "mots_cles_attendus": ["بلاستيدات خضراء", "الأوراق", "ثايلاكويدات", "كلوروفيل"],
            "bareme": 2,
            "type": "restitution",
        },
        {
            "id": "gs_033",
            "chapitre": "Photosynthèse",
            "chapitre_id": "ch5_photosynthese",
            "niveau": "L2",
            "question": "ما هي مراحل البناء الضوئي؟",
            "reponse_attendue": "البناء الضوئي يمر بمرحلتين: 1- المرحلة الضوئية: تحدث في الثايلاكويدات، يتم امتصاص الطاقة الضوئية وتفكك الماء وإنتاج ATP و NADPH وتحرر الأكسجين، 2- المرحلة الكيميائية (دورة كالفن): تحدث في الستروما، يتم تثبيت CO2 وتركيب الغلوكوز باستخدام ATP و NADPH",
            "mots_cles_attendus": ["ضوئية", "كيميائية", "ثايلاكويدات", "ستروما", "ATP", "كالفن"],
            "bareme": 5,
            "type": "application",
        },
        {
            "id": "gs_034",
            "chapitre": "Photosynthèse",
            "chapitre_id": "ch5_photosynthese",
            "niveau": "L2",
            "question": "ما هو دور الكلوروفيل في البناء الضوئي؟",
            "reponse_attendue": "الكلوروفيل صبغة خضراء موجودة في الثايلاكويدات، دوره هو امتصاص الطاقة الضوئية وتحويلها إلى طاقة كيميائية (ATP) تستخدم في تفاعلات البناء الضوئي",
            "mots_cles_attendus": ["صبغة", "خضراء", "امتصاص", "طاقة ضوئية", "ATP"],
            "bareme": 3,
            "type": "application",
        },
        {
            "id": "gs_035",
            "chapitre": "Photosynthèse",
            "chapitre_id": "ch5_photosynthese",
            "niveau": "L3",
            "question": "صمم تجربة تثبت أن البناء الضوئي ينتج الأكسجين",
            "reponse_attendue": "نأخذ نبتة مائية (إلوديا) ونضعها في قمع مقلوب في أنبوب اختبار مملوء بالماء. نضع الجهاز في الضوء. النتائج: نلاحظ تصاعد فقاعات الغاز نحو الأنبوب. نجمع الغاز وندخل شعلة مشتعلة فتزداد توهجا. الاستنتاج: الغاز المتصاعد هو الأكسجين الناتج عن البناء الضوئي",
            "mots_cles_attendus": ["إلوديا", "قمع", "ضوء", "فقاعات", "أكسجين", "شعلة", "استنتاج"],
            "bareme": 5,
            "type": "type_bac",
        },
    ]
)

# ── Chapitre 7: Génétique (7 questions) ──
QUESTIONS.extend(
    [
        {
            "id": "gs_036",
            "chapitre": "Génétique",
            "chapitre_id": "ch6_genetique",
            "niveau": "L1",
            "question": "ما هو ADN؟",
            "reponse_attendue": "ADN (الحمض النووي الريبي منقوص الأكسجين) هو جزيئة تحمل المعلومة الوراثية، يتكون من سلسلتين ملتفين على شكل لولب مزدوج، ويتكون من وحدات تسمى النيوكليوتيدات",
            "mots_cles_attendus": ["معلومة وراثية", "لولب مزدوج", "نيوكليوتيدات", "سلسلتين"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_037",
            "chapitre": "Génétique",
            "chapitre_id": "ch6_genetique",
            "niveau": "L1",
            "question": "ما هي مكونات النيوكليوتيد؟",
            "reponse_attendue": "النيوكليوتيد يتكون من ثلاثة مكونات: 1- حمض فوسفوري، 2- سكر خماسي (ديوكسي ريبوز)، 3- قاعدة آزوتية (أدنين، غوانين، سيتوزين، ثايمين)",
            "mots_cles_attendus": ["حمض فوسفوري", "سكر خماسي", "ديوكسي ريبوز", "قاعدة آزوتية"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_038",
            "chapitre": "Génétique",
            "chapitre_id": "ch6_genetique",
            "niveau": "L1",
            "question": "ما هي القواعد الآزوتية في ADN وكيف تترابط؟",
            "reponse_attendue": "القواعد الآزوتية أربعة: أدنين (A)، غوانين (G)، سيتوزين (C)، ثايمين (T). تترابط بشكل نوعي: A مع T بروابط هيدروجينية مزدوجة، G مع C بروابط هيدروجينية ثلاثية",
            "mots_cles_attendus": ["أدنين", "غوانين", "سيتوزين", "ثايمين", "روابط هيدروجينية", "نوعي"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_039",
            "chapitre": "Génétique",
            "chapitre_id": "ch6_genetique",
            "niveau": "L2",
            "question": "اشرح آلية تضاعف ADN",
            "reponse_attendue": "تضاعف ADN شبه محافظ: 1- تنفتح السلسلتان بواسطة إنزيم، 2- كل سلسلة تعمل كقالب، 3- ترتبط النيوكليوتيدات الحرة حسب الترابط النوعي (A-T, G-C)، 4- تتشكل سلسلتان جديدتان متطابقتان، كل واحدة تحتوي على سلسلة قديمة وأخرى جديدة",
            "mots_cles_attendus": ["شبه محافظ", "قالب", "ترابط نوعي", "نيوكليوتيدات", "إنزيم"],
            "bareme": 5,
            "type": "application",
        },
        {
            "id": "gs_040",
            "chapitre": "Génétique",
            "chapitre_id": "ch6_genetique",
            "niveau": "L2",
            "question": "ما الفرق بين ADN و ARN؟",
            "reponse_attendue": "ADN يحتوي على سكر ديوكسي ريبوز وقاعدة ثايمين وهو ثنائي السلسلة، بينما ARN يحتوي على سكر ريبوز وقاعدة يوراسيل بدل ثايمين وهو أحادي السلسلة",
            "mots_cles_attendus": ["ديوكسي ريبوز", "ريبوز", "ثايمين", "يوراسيل", "ثنائي", "أحادي"],
            "bareme": 3,
            "type": "application",
        },
        {
            "id": "gs_041",
            "chapitre": "Génétique",
            "chapitre_id": "ch6_genetique",
            "niveau": "L3",
            "question": "حلل تجربة تثبت أن ADN هو المادة الوراثية",
            "reponse_attendue": "تجربة أفري: نأخذ سلالتين من البكتيريا، سلالة ممرضة (S) وسلالة غير ممرضة (R). نقتل السلالة S بالحرارة ونستخلص ADN منها، نحقنه في السلالة R. النتائج: تتحول السلالة R إلى سلالة ممرضة S. الاستنتاج: ADN هو المادة الوراثية المسؤولة عن نقل الصفات الوراثية",
            "mots_cles_attendus": ["أفري", "بكتيريا", "ممرضة", "S", "R", "تحول", "استنتاج"],
            "bareme": 6,
            "type": "type_bac",
        },
        {
            "id": "gs_042",
            "chapitre": "Génétique",
            "chapitre_id": "ch6_genetique",
            "niveau": "L3",
            "question": "اشرح كيف يحدد ADN الصفات الوراثية",
            "reponse_attendue": "ADN يحمل المعلومة الوراثية على شكل تسلسل القواعد الآزوتية، هذه المعلومة تُنسخ إلى ARNm ثم تُترجم إلى بروتين في الريبوزوم. البروتينات هي التي تحدد الصفات الوراثية. العلاقة: تسلسل القواعد في ADN يحدد تسلسل الأحماض الأمينية في البروتين",
            "mots_cles_attendus": ["تسلسل", "قواعد", "نسخ", "ARNm", "ترجمة", "بروتين", "صفات"],
            "bareme": 5,
            "type": "type_bac",
        },
    ]
)

# ── Chapitre 8: Géologie / Tectonique (8 questions) ──
QUESTIONS.extend(
    [
        {
            "id": "gs_043",
            "chapitre": "Géologie",
            "chapitre_id": "ch7_geologie",
            "niveau": "L1",
            "question": "ما هي البنية الداخلية للأرض؟",
            "reponse_attendue": "تتكون الأرض من ثلاث طبقات: 1- القشرة الأرضية (الصلبة الخارجية)، 2- الوشاح (الطبقة الوسطى)، 3- النواة (اللب الداخلي والخارجي)",
            "mots_cles_attendus": ["قشرة", "وشاح", "نواة", "ثلاث"],
            "bareme": 2,
            "type": "restitution",
        },
        {
            "id": "gs_044",
            "chapitre": "Géologie",
            "chapitre_id": "ch7_geologie",
            "niveau": "L1",
            "question": "ما هي الصفائح التكتونية؟",
            "reponse_attendue": "الصفائح التكتونية هي أجزاء صلبة من القشرة الأرضية والوشاح العلوي (الليثوسفير) تتحرك فوق الطبقة اللدنة (الأسثينوسفير)",
            "mots_cles_attendus": ["قشرة", "ليثوسفير", "أسثينوسفير", "تحرك", "صلبة"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_045",
            "chapitre": "Géologie",
            "chapitre_id": "ch7_geologie",
            "niveau": "L2",
            "question": "ما هي أنواع حدود الصفائح التكتونية؟",
            "reponse_attendue": "ثلاثة أنواع: 1- حدود متقاربة (تصادمية): تنتج جبال وخنادق، 2- حدود متباعدة (انفصالية): تنتج قيعان محيطات جديدة، 3- حدود متزاحة (تحويلية): تنتج زلازل",
            "mots_cles_attendus": ["متقاربة", "متباعدة", "متزاحة", "تصادم", "انفصال"],
            "bareme": 4,
            "type": "application",
        },
        {
            "id": "gs_046",
            "chapitre": "Géologie",
            "chapitre_id": "ch7_geologie",
            "niveau": "L2",
            "question": "اشرح آلية تحرك الصفائح التكتونية",
            "reponse_attendue": "تتحرك الصفائح بسبب تيارات الحمل الحراري في الوشاح: المادة الساخنة ترتفع وتبرد ثم تغوص، مما يسبب حركة الصفائح فوقها. أيضا دفع القشرة عند الحدود المتباعدة وسحبها عند الحدود المتقاربة",
            "mots_cles_attendus": ["تيارات الحمل", "حراري", "وشاح", "ترتفع", "تغوص"],
            "bareme": 4,
            "type": "application",
        },
        {
            "id": "gs_047",
            "chapitre": "Géologie",
            "chapitre_id": "ch7_geologie",
            "niveau": "L3",
            "question": "حلل وثائق تثبت ظاهرة الانجراف القاري",
            "reponse_attendue": "أدلة الانجراف القاري: 1- التطابق الجيولوجي بين سواحل إفريقيا وأمريكا الجنوبية، 2- وجود نفس المستحثات (الميزوصور) في قارتين منفصلتين، 3- تطابق الصخور والأعمار الجيولوجية. الاستنتاج: القارات كانت متصلة (بانجيا) ثم انجرفت",
            "mots_cles_attendus": ["إفريقيا", "أمريكا", "مستحثات", "ميزوصور", "بانجيا", "انجراف"],
            "bareme": 5,
            "type": "type_bac",
        },
        {
            "id": "gs_048",
            "chapitre": "Géologie",
            "chapitre_id": "ch7_geologie",
            "niveau": "L1",
            "question": "ما هي الزلازل وكيف تحدث؟",
            "reponse_attendue": "الزلازل هي اهتزازات أرضية تحدث عند تحرك الصفائح التكتونية فجأة عند الحدود، تتراكم الطاقة ثم تتحرر على شكل أمواج زلزالية",
            "mots_cles_attendus": ["اهتزازات", "صفائح", "طاقة", "أمواج", "تحرر"],
            "bareme": 3,
            "type": "restitution",
        },
        {
            "id": "gs_049",
            "chapitre": "Géologie",
            "chapitre_id": "ch7_geologie",
            "niveau": "L2",
            "question": "ما الفرق بين المركز السطحي والمركز العميق للزلزال؟",
            "reponse_attendue": "المركز العميق (البؤرة) هو نقطة انطلاق الزلزال في الأعماق، بينما المركز السطحي (المركز الظاهري) هو النقطة على سطح الأرض فوق المركز العميق مباشرة، حيث تكون شدة الزلزال قصوى",
            "mots_cles_attendus": ["سطحي", "عميق", "بؤرة", "شد", "قصوى"],
            "bareme": 3,
            "type": "application",
        },
        {
            "id": "gs_050",
            "chapitre": "Géologie",
            "chapitre_id": "ch7_geologie",
            "niveau": "L3",
            "question": "حلل وثائق تثبت ظاهرة توسع قاع المحيط",
            "reponse_attendue": "أدلة توسع قاع المحيط: 1- وجود سلسلة جبال وسط المحيط (ظهر المحيط)، 2- تزداد عمر الصخور كلما ابتعدنا عن الظهر، 3- الانعكاسات المغناطيسية المتناظرة على جانبي الظهر. الاستنتاج: قاع المحيط يتوسع بانفصال الصفائح عند الحدود المتباعدة وتكوين قشرة محيطية جديدة",
            "mots_cles_attendus": ["ظهر المحيط", "عمر الصخور", "انعكاسات مغناطيسية", "توسع", "انفصال", "استنتاج"],
            "bareme": 6,
            "type": "type_bac",
        },
    ]
)


# ── Génération du fichier JSON ──────────────────────────────────────────────


def main():
    output = {
        "metadata": {
            "version": "1.0",
            "source": "ONEC — Bac Sciences Expérimentales SVT",
            "description": "Golden Set pour benchmark qualité RAG + Eval Engine",
            "usage": "scripts/benchmark_golden_set.py",
            "total_questions": len(QUESTIONS),
            "created": "2026-06-22",
            "chapitres_couverts": list({q["chapitre"] for q in QUESTIONS}),
            "niveaux": {"L1": "restitution", "L2": "application", "L3": "type_bac"},
        },
        "questions": QUESTIONS,
    }

    output_path = pathlib.Path(__file__).parent.parent / "data" / "golden_set_onec.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Golden Set généré: {len(QUESTIONS)} questions")
    print(f"Fichier: {output_path}")
    print(f"Chapitres: {len({q['chapitre'] for q in QUESTIONS})}")
    print(
        f"Niveaux: L1={sum(1 for q in QUESTIONS if q['niveau'] == 'L1')}, "
        f"L2={sum(1 for q in QUESTIONS if q['niveau'] == 'L2')}, "
        f"L3={sum(1 for q in QUESTIONS if q['niveau'] == 'L3')}"
    )


if __name__ == "__main__":
    main()
