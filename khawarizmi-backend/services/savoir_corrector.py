"""services/savoir_corrector.py — Correcteur SAVOIR 100% déterministe (0 LLM).

Corrige le CONTENU SCIENTIFIQUE d'une réponse d'élève pour SVT Bac Algérie 3AS
en s'appuyant sur :
  • Les mots-clés obligatoires de la question (barème) ;
  • Un lexique de synonymes FR/AR pour chaque concept ;
  • Des règles biologiques officielles DZ (38 ATP, P/O 3 NADH / 2 FADH2, etc.) ;
  • La détection des contre-sens / erreurs conceptuelles graves.

Retourne un score sur max_points + points forts, erreurs, réponse modèle
synthétique. Utilisé par correction_service.correct_student_answer() en
fallback quand l'IA externe est coupée (mode local).
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

# ──────────────────────────────────────────────────────────────────────
# Lexique de synonymes scientifiques FR/AR/arabe dialectal
# ──────────────────────────────────────────────────────────────────────
_SYNONYMS: dict[str, list[str]] = {
    # ── Biologie moléculaire / Synthèse protéines ──
    "noyau":          ["noyau", "nucléus", "النواة", "نواة"],
    "adn":            ["adn", "dna", "الدنا", "الـadn", "جزيئة adn", "المادة الوراثية"],
    "arn":            ["arn", "rna", "الرنا", "الرن"],
    "desoxyribose":   ["désoxyribose", "ديوكسي ريبوز", "سكر ديوكسي ريبوز", "الديوكسي ريبوز", "ديوكسيريبوز", "سكر خماسي منقوص الأكسجين"],
    "ribose":         ["ribose", "سكر ريبوز", "الريبوز", "ريبوز"],
    "thymine":        ["thymine", "الثايمين", "ثايمين", "القاعدة الثايمين", "t"],
    "uracile":        ["uracile", "اليوراسيل", "يوراسيل", "قاعدة يوراسيل", "u"],
    "adn_double_brin": ["double brin", "double hélice", "ثنائي السلاسل", "ثنايي السلسله", "مزدوج", "سلسلتان", "حلزون مزدوج"],
    "arn_simple_brin": ["simple brin", "brin simple", "أحادي السلسلة", "احادي السلسله", "سلسلة واحدة"],
    "bases_azotees":  ["bases azotées", "القواعد الآزوتية", "قواعد آزوتية", "القواعد النيتروجينية", "تسلسل القواعد", "تسلسل القواعد الآزوتية", "تسلسل القواعد الازوتيه"],
    "arm":            ["arnm", "mrna", "arn messager", "الرنا الرسول", "الرنا الرسول", "رنا رسول"],
    "trn":            ["arnt", "trna", "arn de transfert", "arn transférable", "الرنا الناقل", "رنا ناقل", "arn الناقل", "الرنا الناقل", "ينقل arnt", "arn ناقل"],
    "arnt_role":      ["ينقل الأحماض الأمينية", "ينقل الاحماض الامينيه", "حامل الأحماض الأمينية", "يحمل الأحماض الأمينية", "حاملا الأحماض الأمينية", "ينقل الحمض الأميني"],
    "rarn":           ["arnr", "rrna", "arn ribosomique", "الرنا الريبوزومي"],
    "ribosome":       ["ribosome", "الريبوزوم", "ريبوزوم", "جسيم ريبوزومي", "جسم ريبوزومي"],
    "hyaloplasme":    ["hyaloplasme", "cytoplasme", "الهيولى", "هيولى", "السايتوبلازم", "سايتوبلازم", "سيتوبلازم", "السيتوبلازم", "السايتوبلاسما"],
    "transcription":  ["transcription", "نسخ", "النسخ", "استنساخ", "الاستنساخ"],
    "traduction":     ["traduction", "ترجمة", "الترجمة"],
    "codon":          ["codon", "triplet", "كودون", "الكودون", "الكودونات", "قواعد ثلاثية", "ثلاثية القواعد", "رامزة"],
    "acide_amine":    ["acide aminé", "acides amines", "aminoacide", "حمض أميني", "أحماض أمينية", "احماض امينيه"],
    "anticodon":      ["anticodon", "مضاد الكودون", "مضاد كودون", "الكودون المضاد", "كودون مضاد", "الرامزة المضادة"],
    "replica":        ["réplication", "تضاعف", "التضاعف"],
    "polymerase":     ["arn polymérase", "arn polymerase", "adn polymérase", "بوليميراز", "البوليميراز"],

    # ── Structure des protéines ──
    "prot_primaire":  ["structure primaire", "البنية الأولية", "البنية الاوليه", "التركيب الأولي", "التركيب الاولي", "تسلسل الأحماض الأمينية", "تسلسل الاحماض الامينيه", "sequence des acides amines", "سلسلة ببتيدية ببتيدية", "تتابع الأحماض الأمينية"],
    "prot_secondaire": ["structure secondaire", "بنية ثانوية", "البنية الثانوية", "التركيب الثانوي", "حلزون ألفا", "حلزون الفا", "hélice alpha", "helice α", "الصحيفة بيتا", "الصفيحة بيتا", "صحيفة مطوية", "الوريقات المطوية", "الورقة المطوية", "وريقات مطوية", "feuillet bêta", "feuillet beta", "رابطة هيدروجينية", "روابط هيدروجينية", "liaisons hydrogène", "لولبي", "حلزوني", "الشكل الحلزوني", "البنية الحلزونية", "بنية حلزونية", "شكل حلزوني", "أشكال حلزونية", "التفاف السلسلة الببتيدية", "انطواء السلسلة", "الانطواء"],
    "prot_tertiaire": ["structure tertiaire", "بنية ثالثية", "بنية ثلاثية", "البنية الثالثية", "البنيه الثالثيه", "التركيب الثالثي", "التركيب الثالثى", "التفاف", "التلاف", "الانطواء", "انطواء", "انطواء السلسلة", "تلتف", "شكل كروي", "شكلا كرويا", "كروي", "كروية", "repliement", "repliement tridimensionnel", "بنية ثلاثية الأبعاد", "الشكل ثلاثي الأبعاد", "بنيات ثانوية حلزونية ووريقات"],
    "prot_quaternaire": ["structure quaternaire", "بنية رباعية", "البنية الرباعية", "التركيب الرباعي", "عدة سلاسل ببتيدية", "plusieurs chaînes peptidiques", "وحدات فرعية", "تحت الوحدات", "تحت الوحدة", "تحت وحدات", "لسلسلتين ببتيديتين أو أكثر", "تجمع تحت وحدات"],
    "pont_disulfure": ["pont disulfure", "ponts disulfures", "جسور ثنائية الكبريت", "جسور كبريتية", "الجسور الكبريتية", "رابطة ثنائية الكبريت", "liaison disulfure", "جسر كبريتي"],
    "liaison_h":      ["liaison hydrogène", "liaisons hydrogène", "رابطة هيدروجينية", "روابط هيدروجينية"],
    "liaison_ionique": ["liaison ionique", "pont salin", "ponts salins", "رابطة أيونية", "روابط أيونية", "روابط شاردية", "رابطة شاردية", "الروابط الملحية", "رابطة ملحية", "تفاعلات كهربائية", "تفاعلات الشحنات"],
    "liaison_hydrophobe": ["interaction hydrophobe", "interactions hydrophobes", "تفاعلات كارهة للماء", "تداخل الجذور الكارهة للماء", "تجاذب كاره للماء", "تداخل كاره للماء", "تأثير كاره للماء"],
    "groupe_r":       ["groupes latéraux", "groupe r", "المجموعات الجانبية", "مجموعات جانبية", "السلاسل الجانبية r", "chaînes latérales", "chaîne latérale", "مجموعات R", "مجموعات الجانب", "المجموعات الجانبيه", "المجموعة الجانبية", "الجذور r", "جذر r", "جذور الأحماض الأمينية", "الجذور الكيميائية"],
    "chaine_peptidique": ["chaîne peptidique", "سلسلة ببتيدية", "السلسلة الببتيدية", "سلسلة بيبتيدية", "السلسلة البيبتيدية", "سلسل بيبتيدي"],
    "liaison_peptidique": ["liaison peptidique", "روابط ببتيدية", "رابطة ببتيدية", "الرابطة الببتيدية", "الروابط الببتيدية"],
    "sequence_aa":    ["séquence des acides aminés", "تسلسل الأحماض الأمينية", "ترتيب الأحماض الأمينية", "تسلسل", "متسلسل", "الترتيب المتسلسل"],
    "ordre_aa":       ["ترتيب", "الترتيب", "ترتيب الأحماض", "ترتيب متسلسل"],
    "feuillet_beta_nom": ["صفائح", "الصفائح", "الصفائحية", "الشكل الصفائحي", "بنية صفائحية", "مناطق صفائحية"],
    "helice_alpha_nom": ["لولبي", "لولبية", "حلزوني", "حلزونية", "الشكل الحلزوني", "بنية لولبية", "الشكل اللولبي"],
    "liaison_generique": ["روابط", "رابطة", "روابط كيميائية"],
    "structure_generique": ["بنية", "البنية", "البناء", "البنية الفراغية"],
    "fonction":       ["وظيفة", "الوظيفة", "وظيفة البروتين", "الدور"],
    "complementarite_nom": ["تمامة", "التمامة", "متمم", "متممة", "تكامل", "التكامل"],
    "globules_rouges": ["كرات الدم الحمراء", "كريات حمراء"],
    "codon_stop":     ["codon stop", "codon de terminaison", "كودون التوقف", "كودون توقف", "توقف الترجمة"],

    # ── Enzymologie ──
    "enzyme":         ["enzyme", "إنزيم", "أنزيم", "إنظيم", "الإنزيم", "الانزيم", "الإنزميم", "الانزيمات"],
    "substrat":       ["substrat", "الركيزة", "ركيزة", "مادة التفاعل", "ماده التفاعل", "المادة المتفاعلة"],
    "site_actif":     ["site actif", "site catalytique", "الموقع الفعال", "الموقع النشط", "موقع فعال", "موقع فعّال", "موقع الفعال", "موقع النشاط", "موقع نشط", "site actif de l'enzyme", "site de fixation", "المنطقة الفعالة"],
    "complexe_es":    ["complexe enzyme-substrat", "complexe es", "معقد إنزيم ركيزة", "معقد انزيم ركيزه", "معقد انزيم ركيزة", "ارتباط الانزيم بالركيزة", "يرتبط بالركيزة", "يرتبط بالموقع الفعال", "ارتباط الركيزة", "تشكل معقد es", "معقد es انتقالي", "روابط ضعيفة انتقالية"],
    "inhibiteur":     ["inhibiteur", "مثبط", "المثبط", "تثبيط", "تثبيط تنافسي", "مثبطات تنافسية", "inhibiteur compétitif", "inhibiteur allostérique", "مثبطات غير تنافسية", "مادة مثبطة"],
    "energie_activation": ["énergie d'activation", "طاقة التنشيط", "طاقة التشغيل", "تقليل طاقة التنشيط", "تخفيض طاقة التنشيط"],
    "ph":             ["ph", "الحموضة", "الأس الهيدروجيني", "درجة الحموضة", "ph المثلى", "حموضة الوسط"],
    "temperature":    ["température", "درجة الحرارة", "درجه الحراره", "الحرارة", "الدرجة المثلى", "حرارة الوسط"],
    "competition":    ["compétitif", "تنافسي", "تثبيط تنافسي", "inhibition compétitive", "تثبيط تنافسى"],
    "non_compet":     ["inhibition non compétitive", "non compétitif", "غير تنافسي", "تثبيط غير تنافسي"],
    "allosterique":   ["allostérique", "تثبيط ألوستيري", "مختلف التموقع", "ألوستيري", "الوستيري", "التفارغي"],
    "v_max":          ["vmax", "vitesse maximale", "السرعة القصوى", "سرعه قصوي", "السرعة الابتدائية القصوى", "سرعة ابتدائية قصوى"],
    "km":             ["km", "constante de michaëlis", "constante de michaelis", "ثابتة ميكايليس", "ثابت ميكايليس"],
    "denaturation":   ["dénaturation", "تمسخ", "التمسخ", "تغير بنيته", "تغير البنية الفراغية", "تغير بنية الإنزيم", "تفكك البنية", "denaturation", "ينمسخ", "تمسخ الإنزيم", "الإنزيم يتمسخ", "إلغاء طبيعة البروتين", "إلغاء الطبيعة البروتينية", "إلغاء طبيعة الإنزيم", "التشويه", "تدمير البنية الفراغية", "التغريب", "تغرب", "تغرب البنية", "يفقد بنيته الفراغية", "انفصام الروابط", "تكسر الروابط"],
    "coenzyme":       ["coenzyme", "أنزيم مساعد", "إنزيم مساعد", "مرافق إنزيمي", "العامل المرافق"],
    "t_opt":          ["température optimale", "درجة الحرارة المثلى", "الدرجة المثلى", "حرارة مثلى", "درجه الحراره المثلي", "الحراره المثلي", "37 درجة", "37°م", "37°", "حرارة الجسم"],
    "ph_opt":         ["ph optimal", "ph optimum", "الأس الهيدروجيني الأمثل", "الحموضة المثلى", "ph مثلى"],
    "vitesse":        ["vitesse de réaction", "سرعة التفاعل", "سرعه التفاعل", "سرعة التفاعل الإنزيمي", "السرعة الابتدائية", "vi", "السرعة الابتدائية للتفاعل"],
    "specificite":    ["spécificité de substrat", "spécificité", "نوعية الركيزة", "تخصص الركيزة", "النوعية", "التخصص", "تأثير نوعي", "نوعية التفاعل"],
    "saturation":     ["saturation", "تشبع", "إشباع المواقع الفعالة", "تشبع المواقع الفعالة"],
    "cofacteur":      ["cofacteur", "عامل مساعد", "العوامل المساعدة", "عوامل مساعدة"],
    "holoenzyme":     ["holoenzyme", "إنزيم كامل", "الإنزيم الكامل", "هولوانزيم"],
    "apoenzyme":      ["apoenzyme", "الإنزيم البروتيني", "أبوانزيم", "جزء بروتيني"],
    "concentration":  ["concentration", "تركيز", "التركيز", "تركيز الركيزة", "زيادة تركيز", "تغير تركيز"],
    "cinetique":      ["cinétique enzymatique", "حركية الإنزيم", "الحركية الإنزيمية", "سرعة التفاعل"],
    "activateur":     ["activateur", "منشط", "منشطات"],
    "complementarite_forme": ["التكامل المحفز", "تكامل محفز", "التكامل الشكلي المحفز", "adaptation induite", "التواؤم المستحث", "تكامل الشكل", "التكامل البنيوي المحفز", "المكمل الشكلي"],
    # ── Conformation / structure-fonction ──
    "conformation":   ["conformation", "بنية مكانية", "البنية المكانية", "بنيه مكانيه", "البنية ثلاثية الأبعاد", "الشكل ثلاثي الأبعاد", "البنية الفراغية", "التخصص البنيوي", "البنية ثلاثية الابعاد"],
    "relation_struct_fonction": ["relation structure-fonction", "علاقة بين البنية والوظيفة", "البنية تحدد الوظيفة", "تغير البنية", "تغير البنية يؤدي", "تغير الوظيفة", "تفقد الانزيم وظيفته", "فقدان الوظيفة", "perte de fonction"],
    "complementarite": ["complémentarité", "تكامل", "التكامل", "التكامل البنيوي", "تمام", "التمامة", "متمم", "متممة", "تتطابق", "تطابق", "تطابق شكلي", "التكامل الشكلي", "complémentarité de forme", "التعرف النوعي", "يتعرف"],
    "globuline":      ["globuline", "الغلوبولينات", "غلوبولينات", "الغلوبولين", "غلوبولين", "الجلوبيولينات", "بروتينات الدم"],
    "reconnaissance": ["reconnaissance", "التعرف", "يتعرف على", "تتعرف على", "التعرف النوعي", "التعرف على المستضد"],
    # ── Traduction/transcription plus ──
    "export_arm":     ["الرنا يخرج", "الرنا ينتقل", "ينقل المعلومة", "نقل المعلومة الوراثية", "نسخة من المعلومة", "نسخة من المعلومة الوراثية"],

    # ── Respiration / Photosynthèse / ATP ──
    "mitochondrie":   ["mitochondrie", "الميتوكوندريا", "متقدرة", "الميتوكوندري", "ميتوكوندري", "الميتوكندري", "ميتوكندريا"],
    "atp":            ["atp", "adénosine triphosphate", "ثلاثي فوسفات الأدينوزين", "أتب", "أدينوزين ثلاثي الفوسفات"],
    "adp":            ["adp", "ثنائي فوسفات الأدينوزين"],
    "pi":             ["pi", "phosphate inorganique", "فوسفات غير عضوي"],
    "nadh":           ["nadh", "ناد مختزل", "ناد هـ", "ناد h", "أن أده+h", "ناد+h", "nad h", "nad+h"],
    "fadh2":          ["fadh2", "فاد2", "فاد هـ2", "فاد مختزل", "فاد هـ2 المختزل"],
    "glycolyse":      ["glycolyse", "التحلل السكري", "تحلل سكري", "انحلال الجلوكوز", "غليكوليز", "الجليكوليز"],
    "cycle_krebs":    ["cycle de krebs", "cycle de l'acide citrique", "حلقة كريبس", "دورة كريبس", "حلقة كربس", "دورة كربس"],
    "chaine_resp":    ["chaîne respiratoire", "chaîne de transport d'électrons", "السلسلة التنفسية", "سلسلة التنفس"],
    "phosphorylation_oxydative": ["phosphorylation oxydative", "الفسفرة التأكسدية", "الفسفرة المؤكسدة", "فسفرة تأكسدية"],
    "oxygene":        ["o2", "dioxygène", "oxygène", "الأكسجين", "أكسجين", "الاوكسجين", "اكسجين"],
    "38_atp":         ["38 atp", "38atp", "38 جزيئة atp", "38 جزيء atp", "38atp", "38 أتب", "38 جزيء atp"],
    "pyruvate":       ["pyruvate", "acide pyruvique", "البيروفات", "بيروفات", "حمض البيروفيك", "الحمض البيروفي", "البيروفيك", "مركب ثلاثي الكربون"],
    "acetyl_coa":     ["acétyl-coa", "acetyl-coa", "acétyl coenzyme a", "أستيل كوآ", "أستيل مرافق أ", "أسيتيل كوآ", "الأسيتيل كوآ", "أستيل كو إنزيم أ", "استيل كو"],
    "chloroplaste":   ["chloroplaste", "البلاستيدات الخضراء", "بلاستيدات خضراء", "الكلوروبلاست", "الصانعات الخضراء", "الصانعة الخضراء", "صانعات يخضورية", "صانعة خضراء"],
    "thylakoid":      ["thylakoïde", "thylakoids", "الثايلاكويد", "أقراص ثايلاكويد", "الثايلاكويدات", "ثايلاكويد", "التيلاكويد", "الأعراف"],
    "stroma":         ["stroma", "السترومة", "السدى", "الحشوة"],
    "lumieres":       ["phase claire", "réactions lumineuses", "المرحلة الضوئية", "تفاعلات ضوئية", "الطور الضوئي", "المرحلة الكيموضوئية"],
    "obscures":       ["phase obscure", "cycle de calvin", "المرحلة الكيموحيوية", "المرحلة المظلمة", "دورة كالفين", "دورة كالفن", "الطور المظلم"],
    "chlorophylle":   ["chlorophylle", "الكلوروفيل", "يخضور", "اليخضور"],
    "co2":            ["co2", "dioxyde de carbone", "ثنائي أكسيد الكربون", "ثنائي اكسيد الكربون", "غاز الكربون", "ثنائي أكسيد الكاربون"],
    "glucose":        ["glucose", "جلوكوز", "الغلوكوز", "الغلوكوز", "مادة عضوية", "المادة العضوية", "ماده عضويه", "مواد عضوية", "سكر", "الجلوكوز"],
    "o2_degage":      ["dégagement d'o2", "libération d'oxygène", "انطلاق الأكسجين", "إطلاق الأكسجين", "ينطلق الأكسجين"],
    "eau":            ["eau", "الماء", "ماء", "h2o"],
    "energie_lumineuse": ["énergie lumineuse", "طاقة ضوئية", "الطاقة الضوئية", "طاقه ضوييه", "الطاقه الضوييه", "طاقة الشمس", "ضوء", "lumière"],
    "mat_organique":  ["matière organique", "المادة العضوية", "ماده عضويه", "مواد عضوية", "matieres organiques", "glucides", "sucres"],
    "mat_minerale":   ["matière minérale", "المادة المعدنية", "ماده معدنيه", "مواد معدنية", "sels minéraux", "املاح معدنية", "co2 et eau"],

    # ── Immunologie ──
    "immunite":       ["immunité", "مناعة", "المناعة", "الجهاز المناعي", "استجابة مناعية", "الاستجابة المناعية", "استجابه مناعيه", "استجابه مناعيه", "المناعه"],
    "lympho_b":       ["lymphocyte b", "lb", "الخلية اللمفاوية b", "اللمفاويات ب", "اللمفاوية ب", "اللمفاويه b", "اللمفاوية b", "lymphocytes b", "الخلايا اللمفاوية b", "الخلايا اللمفاويه البائيه", "الخليه اللمفاويه البائيه", "خلية لمفاوية ب", "lb", " b", "الخلايا الليمفاوية", "اللمفاوية b", "الليمفاوية b", "الليمفاوية ب", "اللمفاوية b", "lb الخلايا", "الخلايا البائية", "بائية"],
    "lympho_t4":      ["lymphocyte t4", "lt4", "t helper", "cd4", "الخلية اللمفاوية التائية المساعدة", "اللمفاوية التائية المساعدة", "اللمفاويه المساعده", "لت4", "ت4", "الخلايا التائية المساعدة", "lt4", "t4", "lth", "lt helper", "اللمفاوية المساعدة", "الخلايا التائية المساعده", "المساعدة", "lth"],
    "lympho_t8":      ["lymphocyte t8", "lt8", "t cytotoxique", "cd8", "الخلية اللمفاوية التائية السامة", "اللمفاوية التائية السامة", "الخلايا التائية السامة", "الخلايا القاتلة", "لت8", "ت8", "ltc", "lt8", "ltc السامة", "السامة للخلايا المصابة", "ltc القاتلة", "القاتلة", "ltc"],
    "lympho_t":       ["lymphocyte t", "lt", "الخلية اللمفاوية t", "اللمفاويات ت", "اللمفاوية ت", "اللمفاويه t", "اللمفاوية t", "lymphocytes t", "الخلايا اللمفاوية t", "خلية لمفاوية t", " t", "اللمفاوية التائية", "الليمفاوية ت", "lt ", "التائية"],
    "rep_humorale":   ["réponse humorale", "الاستجابة المناعية الخلطية", "استجابة خلطية", "الاستجابه المناعيه الخلطيه", "المناعة الخلطية", "خلطية", "استجابه خلطيه", "المناعة الخلطية (السائلة)", "مناعية خلطية"],
    "rep_cellulaire": ["réponse cellulaire", "الاستجابة المناعية الخلوية", "استجابة خلوية", "الاستجابه المناعيه الخلويه", "المناعة الخلوية", "خلوية", "استجابه خلويه", "مناعية خلوية"],
    "hla1":           ["cmh i", "hla i", "hla-i", "معقد التوافق النسيجي النوع الأول", "hla من النوع الأول", "hla i", "hla1", "النمط الأول", "hla i معقد"],
    "hla2":           ["cmh ii", "hla ii", "hla-ii", "معقد التوافق النسيجي النوع الثاني", "hla من النوع الثاني", "hla ii", "hla2", "النمط الثاني", "hla ii معقد"],
    "ag_mhcii":       ["cmh ii", "complexe majeur d'histocompatibilité", "معقد التوافق النسيجي", "hla ii"],
    "interleukine":   ["interleukine", "الإنترلوكين", "أنترلوكين", "الإنترلوكينات", "انترلوكين", "الأنترلوكين", "الانترلوكين", "il2", "il1", "il ", "الأنترلوكينات", "المبلغ الكيميائي", "مبلغ كيميائي"],
    "plasmocyte":     ["plasmocyte", "plasmocytes", "خلية بلازمية", "البلازموسيت", "البلازمية", "خلايا بلازمية", "بلاسموسيت", "البلاسموسيت", "الخلية البلازمية", "البلعموسيت"],
    "anticorps":      ["anticorps", "immunoglobuline", "جسم مضاد", "الأجسام المضادة", "أجسام مضادة", "الاجسام المضاده", "الأجسام المضاده", "الجسم المضاد", "اجسام مضاده", "الإغلوبولينات المناعية", "اغلوبولين مناعي", "الغلوبيلينات المناعية", "الأجسام المضادة النوعية", "الأجسام المضادة لل", "الجلوبيولينات المناعية", "الغلوبولين المناعي"],
    "antigene":       ["antigène", "مستضد", "مولد الضد", "المستضدات", "جسم غريب", "أجسام غريبة", "محدد المستضد", "محددات المستضد", "مولد الضد الببتيدي", "مستضد بيبتيدي", "مستضد ببتيدي", "محدد المستضد الببتيدي", "محددات مولد الضد"],
    "phagocyte":      ["phagocyte", "بلعمية", "الخلايا البلعمية", "البالعة", "البالعة الكبيرة", "البلعم الكبير", "البلعميات", "بالعات", "بالعة", "البلاعم"],
    "macrophage":     ["macrophage", "البلعم الكبير", "البالعة الكبيرة", "البلاعم الكبيرة", "الخلايا العارضة", "ماكروفاج", "البلعميات الكبيرة", "البلاعم", "الخلايا البالعة", "البالعات الكبيرة"],
    "cpa":            ["cellule présentatrice", "cpa", "الخلية العارضة للمستضد", "خلايا عارضة", "عرض المستضد", "الخلايا العارضة للمستضد", "خلية عارضة للمستضد", "تقديم المستضد", "عرض مولد الضد", "العارضة"],
    "perforine":      ["perforine", "البيرفورين", "بيرفورين", "مادة تثقيب الغشاء", "البرفورين", "برفورين"],
    "granzyme":       ["granzyme", "الغرانزيم", "غرانزيم", "الغرانزيمات", "غرانزيمات"],
    "memoire":        ["mémoire immunitaire", "cellule mémoire", "cellules mémoires", "ذاكرة مناعية", "خلايا الذاكرة", "خلايا ذاكره", "خلية ذاكرة", "الذاكرة المناعية", "الخلية الذاكرة", "الخلايا الذاكره", "الخلايا الذاكرة"],
    "lymphocyte":     ["lymphocyte", "lymphocytes", "الخلية اللمفاوية", "الخلايا اللمفاوية", "اللمفاويات", "اللمفاوية", "اللمفاويات", "الليمفاوية", "اللمفاوية", "الخلايا اللمفاوية", "اللمفاويات"],
    "etapes_reconnaissance": ["التعرف", "تتعرف", "التعرف على المستضد", "مرحلة التعرف", "تعرف", "مرحلة التعرف على", "التعرف على"],
    "etapes_activation": ["التنشيط", "تنشيط", "تنشط", "تتكاثر", "التكاثر", "مرحلة التنشيط"],
    "etapes_differenciation": ["التمايز", "تتمايز", "تمايز", "مرحلة التمايز"],
    "proliferation":  ["تكاثر", "تتكاثر", "انقسام", "تكاثر اللـ", "تكاثر الخلايا اللمفاوية", "تكاثر اللمفاويات", "prolifération"],
    "thymus":         ["thymus", "الغدة التيموسية", "التيموس", "غدة التوتة", "الغدة الصعترية"],
    "vaccin":         ["vaccin", "لقاح", "اللقاح", "التلقيح"],
    "serum":          ["sérum", "مصل", "المصل"],
    "inflammation":   ["inflammation", "التهاب", "الإلتهاب", "تفاعل ملتهب"],
    "sida_vih":       ["vih", "sida", "فيروس فقدان المناعة", "السيدا", "فيروس العوز", "فيروس نقص المناعة المكتسب"],

    # ── Neurophysiologie ──
    "neurone":        ["neurone", "عصبون", "خلية عصبية", "العصبون", "الليف العصبي", "العصبونات", "الليف العضلي"],
    "synapse":        ["synapse", "مشبك", "المشبك", "المشبك العصبي", "الوصل العصبي", "الوصل المشبكي", "المشابك", "النقل المشبكي", "الإتصال العصبي", "الاتصال المشبكي"],
    "neurotransmetteur": ["neurotransmetteur", "ناقل عصبي", "نواقل عصبية", "الناقل العصبي", "المرسلات العصبية", "الوسيط الكيميائي", "وسيط كيميائي", "الناقلات العصبية", "ناقلات عصبية", "المبلغ الكيميائي", "مبلغ كيميائي", "مبلغات كيميائية", "المبلغات الكيميائية", "المرسل الكيميائي", "مرسل كيميائي"],
    "pr":             ["potentiel de repos", "pr", "كمون الراحة", "جهد الراحة", "كمون راحة", "الكمون الغشائي", "كمون غشائي", "راحة الغشاء"],
    "pa":             ["potentiel d'action", "pa", "جهد فعل", "كمون العمل", "كمون فعل", "السيال العصبي", "السيالة العصبية", "النبضة العصبية"],
    "ppse":           ["ppse", "potentiel postsynaptique excitateur", "كمون بعد مشبكي منبه", "كمون بعد مشبكي تنبيهي", "كمون بعد مشبكي منبه", "epsb", "كمون تنبيهي"],
    "ppsi":           ["ppsi", "potentiel postsynaptique inhibiteur", "كمون بعد مشبكي مثبط", "كمون بعد مشبكي تثبيطي", "كمون بعد مشبكي مثبط", "ipsb", "كمون تثبيطي"],
    "ach":            ["acétylcholine", "ach", "الأستيل كولين", "أستيل كولين", "استيل كولين", "أسيتيل كولين", "الاستيل كولين", "الأستيل كولين", "الاستل كولين", "الأستيلكولين"],
    "canal_na":       ["canaux na+", "canaux sodium", "قنوات الصوديوم", "قنوات صوديوم", "قنوات na+", "قنوات شوارد الصوديوم"],
    "canal_k":        ["canaux k+", "canaux potassium", "قنوات البوتاسيوم", "قنوات بوتاسيوم", "قنوات k+"],
    "canaux_ioniques": ["canaux ioniques", "قنوات أيونية", "قنوات شاردية", "القنوات الغشائية", "قنوات الغشاء"],
    "canaux_voltage": ["canaux voltage-dépendants", "قنوات فولطية", "قنوات الفولطية", "القنوات الفولطية", "canaux tensiodépendants"],
    "pompe_na_k":     ["pompe na/k", "pompe sodium potassium", "مضخة الصوديوم والبوتاسيوم", "مضخة na+ k", "مضخة صوديوم بوتاسيوم", "atpase", "مضخة na k", "مضخة na/k atpase"],
    "myeline":        ["myéline", "غمد المايلين", "النخاعين", "غمد نخاعيني", "غمد الميالين", "غمد النخاعين"],
    "ppm":            ["ppm", "plaque motrice", "الصفيحة المحركة", "المشبك العصبي العضلي", "اللوحة المحركة", "الصفيحة المحركة العضلية"],
    "contraction":    ["contraction musculaire", "تقلص عضلي", "انقباض عضلي", "التقلص العضلي"],
    "ca":             ["ca2+", "calcium", "أيونات الكالسيوم", "الكالسيوم", "شوارد الكالسيوم", "كالسيوم", "ايونات الكالسيوم", "ca2+", "شوارد ca"],
    "synapse_chimique": ["synapse chimique", "المشبك الكيميائي", "مشبك كيميائي", "مشبك كيميايي", "الناقل الكيميائي", "ناقل كيميائي", "المشابك الكيميائية", "وسيط كيميائي", "بواسطة مادة كيميائية", "المرسل الكيميائي", "مبلغ كيميائي"],
    "fente_synaptique": ["fente synaptique", "الشق المشبكي", "شق مشبكي", "الفراغ المشبكي", "الفراغ بين المشبكي"],
    "terminaison":    ["terminaison présynaptique", "الطرف قبل المشبكي", "نهاية قبل مشبكية", "الطرف المشبكي", "الحويصلات المشبكية", "النهاية قبل المشبكية", "النهاية العصبية", "النهاية قبل المشبكية"],
    "postsynaptique": ["postsynaptique", "بعد المشبكي", "الغشاء بعد المشبكي", "الخلية بعد المشبكية", "البعد مشبكي", "الخلية البعد مشبكية"],
    "presynaptique":  ["présynaptique", "قبل المشبكي", "قبل مشبكي", "الطرف قبل المشبكي", "القبل مشبكي", "الخلية قبل المشبكية"],
    "recepteur":      ["récepteur", "recepteurs", "مستقبلات", "المستقبلات", "مستقبل", "المستقبلات الغشائية", "المستقبلات على الغشاء", "المستقبلات النوعية", "مستقبلات غشائية"],
    "vesicule":       ["vésicule", "vésicules synaptiques", "حويصلات", "حويصلات مشبكية", "الحويصلات", "حويصلات المبلغ", "حويصلات الأستيل كولين"],
    "depolarisation": ["dépolarisation", "زوال الاستقطاب", "إزالة الاستقطاب", "زوال استقطاب", "اندفاع الصوديوم", "دخول الصوديوم", "انفتاح قنوات الصوديوم", "انعكاس قطبية الغشاء", "انعكاس قطبية", "انقلاب الاستقطاب", "انعكاس سريع لقطبية", "يصبح داخل الليف موجبا"],
    "polarisation":   ["قطبية الغشاء", "الاستقطاب الغشائي", "قطبية", "استقطاب الغشاء", "الشحنة السالبة", "داخل سالب خارج موجب", "سالبة داخل"],
    "potentiel_actif": ["تنبيه فعال", "التنبيه الفعال", "المنبه الفعال", "تنبيه كاف"],
    "repolarisation": ["repolarisation", "عودة الاستقطاب", "إعادة استقطاب", "عودة استقطاب", "خروج البوتاسيوم", "انفتاح قنوات البوتاسيوم", "العودة لكمون الراحة", "يعود لكمون الراحة"],
    "seuil":          ["seuil", "العتبة", "عتبة", "عتبة كمون العمل", "-50mv", "عتبة التنبيه"],
    "conduction_saltatoire": ["conduction saltatoire", "التوصيل القفزي", "النقل القفزي", "التوصيل القفزي على طول ليف النخاعين", "انتشار قفزي"],
    "integration":    ["intégration", "الإدماج العصبي", "الادماج العصبي", "آلية الإدماج", "دمج الكمونات", "محصلة الكمونات", "تجميع الكمونات", "الدمج العصبي"],
    "sommation":      ["sommation", "تجميع", "التجميع", "تجميع زمني", "تجميع فضائي", "التجميع الزمني", "التجميع الفضائي"],
    "gaba":           ["gaba", "غابا", "مثبط gaba"],
    "ache":           ["acétylcholinestérase", "ache", "الأستيل كولين إستراز", "أنزيم الأستيل كولين إستراز", "استيل كولين استراز", "إستراز الأستيل كولين"],
    "codage":         ["codage", "تشفير", "الترميز", "تشفير الرسالة العصبية", "تواترات كمون العمل"],
    "champs_membrane": ["شحنات الغشاء", "الشحنات الموجبة والسالبة", "فرق الكمون", "فرق الجهد", "الكمون الغشائي"],

    # ── Génétique ──
    "chromosome":     ["chromosome", "صبغي", "الصبغيات", "كروموزوم", "الكروموزومات", "الصبغيات"],
    "gene":           ["gène", "مورثة", "المورثة", "المورثات"],
    "allele":         ["allèle", "الأليل", "حليل", "الأليلات"],
    "genotype":       ["génotype", "طراز وراثي", "النمط الوراثي"],
    "phenotype":      ["phénotype", "مظهر خارجي", "النمط الظاهري", "المظهر الخارجي"],
    "dominant":       ["dominant", "سائد", "المورثة السائدة", "السائد", "سيادة تامة"],
    "recessif":       ["récessif", "متنحي", "المورثة المتنحية", "صفة متنحية"],
    "codominance":    ["codominance", "سيادة مشتركة", "هيمنة مشتركة", "السيادة المشتركة"],
    "crossing_over":  ["crossing-over", "enjambement", "العبور", "التصالب", "تبادل قطع", "عبور"],
    "meiose":         ["méiose", "انتصاف", "الانقسام المنصف", "الانقسام الاختزالي", "المنصف"],
    "mitose":         ["mitose", "انقسام خيطي", "الانقسام الخيطي", "الانقسام غير المباشر", "انقسام غير مباشر"],
    "mutation":       ["mutation", "طفرة", "الطفرة", "طفرات"],
    "brassage":       ["brassage", "اختلاط", "الاختلاط"],
    "karyotype":      ["caryotype", "karyotype", "النمط النووي", "الصيغة الصبغية"],
    "haploide":       ["haploïde", "n", "أحادي الصيغة", "أحادي الصيغة الصبغية", "فرداني"],
    "diploide":       ["diploïde", "2n", "ثنائي الصيغة", "ثنائي الصيغة الصبغية"],

    # ── Géologie ──
    "plaque":         ["plaque lithosphérique", "plaque tectonique", "الصفيحة التكتونية", "الصفائح التكتونية", "لوح", "لوحة تكتونية", "الألواح", "الصفائح", "صفائح", "صفيحه", "اللوح التكتوني", "ألواح تكتونية"],
    "dorsale":        ["dorsale", "dorsale océanique", "الأعراف المحيطية", "العرف المحيطي", "الظهرة المحيطية", "الحيود المحيطية", "الظهر المحيطي", "الظهرة", "ظهرات محيطية", "الرفت", "توسع قاع المحيط", "قاع المحيط", "تجدد قاع", "الظهرات وسط محيطية"],
    "fosse":          ["fosse océanique", "الخندق المحيطي", "الخنادق المحيطية", "خندق", "خندق محيطي", "خنادق", "خندق الانهيار", "خنادق محيطية"],
    "subduction":     ["subduction", "الاندساس", "الطرح", "غوص", "الغوص", "انغمار", "تغوص", "يغوص", "غوص اللوح"],
    "lithosphere":    ["lithosphère", "ليتوسفير", "الغلاف الصخري", "الليتوسفير"],
    "asthénosphère":  ["asthénosphère", "الغلاف المائع", "الأستينوسفير", "الغلاف الموري", "الاستينوسفير", "استينوسفير", "الأستينوسفير", "الاستينوسفير"],
    "point_chaud":    ["point chaud", "البقع الساخنة", "نقطة ساخنة", "بقعة ساخنة"],
    "derive_continents": ["dérive des continents", "الانزياح القاري", "زحزحة القارات", "انزياح القارات", "انجراف القارات", "زحزحه القارات", "انجراف القارات", "زحزحة القارة", "الانجراف القاري"],
    "expansion_fond_oceanique": ["expansion des fonds océaniques", "توسع قيعان المحيطات", "توسع قاع المحيط", "اتساع قاع المحيط", "تمدد قاع المحيط"],
    "inversions_mag":  ["inversions magnétiques", "الانعكاسات المغناطيسية", "انعكاسات المغناطيسية", "الانعكاس المغناطيسي", "تعاكس المغناطيسية", "الشذوذ المغناطيسي المتماثل"],
    "anomalie_mag":   ["anomalie magnétique", "الشذوذ المغناطيسي", "الانعكاسات المغناطيسية", "السجل المغناطيسي", "الشذوذ المغناطيسي المتماثل", "الانعكاس المغناطيسي"],
    "ophiolite":      ["ophiolite", "أوفيوليت", "الأوفيوليت", "الانيوليت", "أفيوليت", "الافيوليت", "الأفيوليت"],
    "magma":          ["magma", "صهارة", "الصهارة", "ماغما", "الماغما", "مغماتية", "الصهارة الصاعدة", "ماغما بازلتية", "الحمم البركانية"],
    "volcan":         ["volcan", "بركان", "البركان", "بركانية", "براكين"],
    "seisme":         ["séisme", "زلزال", "زلازل"],
    "epicentre":      ["épicentre", "المركز السطحي", "مركز سطحي", "المركز الظاهري"],
    "foyer":          ["foyer", "hypocentre", "المركز العميق", "البؤرة", "بؤرة الزلزال", "نقطة الانطلاق"],
    "intensite":      ["intensité", "شدة", "شد", "شدة الزلزال", "الشدة القصوى"],
    "wilson":         ["cycle de wilson", "دورة ويلسون"],
    "pangée":         ["pangée", "بانجيا", "القارة الأم"],
    "croute":         ["croûte", "القشرة", "قشرة", "القشرة الأرضية", "القشره"],
    "manteau":        ["manteau", "البرنس", "المعطف", "الوشاح", "الستار"],
    "noyau_terre":    ["noyau (terre)", "نواة الأرض", "النواة الداخلية", "النواة الخارجية", "لب الأرض", "اللب", "نواة الكرة الأرضية"],
    "limites_convergentes": ["limites convergentes", "حدود متقاربة", "حدود تصادمية", "الحدود المتقاربة", "متقاربة", "تصادمية", "حدود تقارب"],
    "limites_divergentes": ["limites divergentes", "حدود متباعدة", "حدود انفصالية", "الحدود المتباعدة", "متباعدة", "انفصالية", "تباعد", "حدود تباعد"],
    "limites_transformantes": ["failles transformantes", "limites transformantes", "حدود متحولة", "حدود متزاحة", "تحويلية", "متزاحة", "الفوالق التحويلية"],
    "convection":     ["courants de convection", "تيارات الحمل", "تيارات الحمل الحراري", "الحمل الحراري", "تيارات حمل", "تيارات الحمل في الوشاح", "تيارات الحمل في الأستينوسفير"],
    "structure_interne": ["structure interne de la terre", "البنية الداخلية للأرض", "التركيب الداخلي للأرض", "طبقات الأرض", "بنية الأرض الداخلية", "الطبقات الثلاث", "ثلاث طبقات", "ثلاثة أغلفة"],
}

# Erreurs conceptuelles GRAVES → pénalité automatique.
# Les patterns sont écrits pour matcher APRÈS _normalize() :
#  - les diacritiques ont été supprimés ;
#  - أ/إ/آ → ا ; ى → ي ; ئ → ي ; ة → ه ;
#  - les suffixes possessifs ont été retirés ;
#  - on ne dépend donc pas de l'orthographe exacte (ثنائي/ثنايي, جزيء/جزيي, ...).
_GRAVE_ERRORS = [
    # (pattern, message_ar, points_penalty)
    # ── ATP bilan erroné ──
    (r"36\s+\w+\s+atp|36\s+atp",
     "عدد جزيئات ATP هو 38 وليس 36 (البرنامج الرسمي ONEC)", 1.0),
    (r"32\s+\w*\s*atp|32\s+atp",
     "عدد جزيئات ATP هو 38 وليس 32", 1.0),
    (r"(?:2\s+atp.*(?:التنفس|تنفس|respir)|38\s+atp.*(?:تخم|ferment|تخمر))",
     "التنفس الهوائي ينتج 38 ATP والتخمر ينتج 2 ATP — خلط بينهما", 1.0),
    # ── Localisation erronée de la traduction / ADN ──
    (r"الترجم?ه\s+في\s+النوا|ribosome[^.]*noyau",
     "تتم الترجمة في الريبوزومات (الهيولى) وليس في النواة", 1.0),
    (r"الريبوزوم\s+في\s+النوا",
     "الريبوزوم يوجد في الهيولى وليس في النواة", 1.0),
    # ADN localisé explicitement DANS le hyaloplasme/cytoplasme (ERREUR).
    # Règle stricte : "ADN ... في hyaloplasme" SANS mention de النواة/noyau entre les deux.
    (r"adn\b(?!(?:(?!adn\b)[^.]){0,80}(?:النواة|النواه|noyau))(?:(?!adn\b)[^.]){0,30}(?:في|est|se trouve|se situe|localis|present|يوجد|يتواجد|موجود|يحتوي)(?:(?!adn\b)[^.]){0,20}(?:الهيول|هيول|hyaloplasme|cytoplasme|السايتوبلازم|السيتوبلازم)",
     "الـ ADN يبقى في النواة (حقيقيات النوى) ولا يخرج إلى الهيولى", 0.8),
    # Variante : "le cytoplasme contient de l'ADN"
    (r"(?:الهيول|هيول|hyaloplasme|cytoplasme|السايتوبلازم|السيتوبلازم)[^.]{0,20}(?:يحتوي|contient|يوجد به adn|فيه adn)",
     "الـ ADN يبقى في النواة (حقيقيات النوى) ولا يخرج إلى الهيولى", 0.8),
    # ERREUR GRAVE : "l'ADN sort/va vers le cytoplasme" (c'est l'ARNm qui sort)
    (r"adn\b(?:(?!adn\b)[^.]){0,40}(?:يخرج|ينتقل|يعبر|يغادر|sort|va vers|traverse|ينتقل الي|يخرج الي|يخرج الى)(?:(?!adn\b)[^.]){0,20}(?:الهيول|هيول|hyaloplasme|cytoplasme|السايتوبلازم|السيتوبلازم|الريبوزوم|الريبوزومات|الغشاء)",
     "الـ ADN لا يخرج من النواة — فقط ARNm يخرج إلى الهيولى للترجمة", 1.0),
    # ── Photosynthèse vs respiration (sens inversé) ──
    (r"بلاستيدات[^.]{0,30}جذر|chloroplaste[^.]*racine",
     "الصانعات الخضراء توجد في الأجزاء الخضراء (الأوراق) لا الجذور", 0.6),
    # Le CO2 est PRODUIT ou DÉGAGÉ → erreur (doit être CONSOMMÉ)
    (r"(?:ينتج|ينطلق|يطرح|يتحرر|يخرج|ينبعث|degage|produit|libere)[^.]{0,50}(?:co2|co\s*2|اكسيد\s+الكربون|ثنا?ي?ي?\s+اكسيد)",
     "عملية التركيب الضوئي تستهلك CO2 وتُنتج الأكسجين (لا العكس)", 1.0),
    # L'O2 est CONSOMMÉ (تمتص/يستهلك) → erreur dans la photosynthèse
    (r"(?:تمتص|تستهلك|يتم\s*امتصاص|يستهلك|absorbe|consomme)[^.]{0,50}(?:o2|اكسجين|الاكسجين|اوكسجين|الاوكسجين|oxygene|dioxygene)",
     "التركيب الضوئي يُنتج الأكسجين ولا يستهلكه (يستهلكه التنفس)", 1.0),
]

# Règles numériques DZ à vérifier dans les réponses quantitatives
_NUMERIC_RULES = {
    "atp_resp":  {"patterns": [r"bilan.{0,20}atp", r"atp.{0,20}respir", r"atp.{0,20}تنفس"], "expected": 38},
    "atp_ferm":  {"patterns": [r"atp.{0,20}ferment", r"atp.{0,20}تخم"], "expected": 2},
    "po_nadh":   {"patterns": [r"p/o.{0,15}nadh", r"nadh.{0,20}atp", r"p/o"], "expected": 3},
    "po_fadh":   {"patterns": [r"p/o.{0,15}fadh", r"fadh.{0,20}atp"], "expected": 2},
}


# ──────────────────────────────────────────────────────────────────────
# Utilitaires de normalisation
# ──────────────────────────────────────────────────────────────────────
def _normalize(text: str) -> str:
    if not text:
        return ""
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower().strip()
    # Supprimer ponctuation et diacritiques
    for ch in [".", ",", ";", ":", "!", "?", "،", "؛", "؟", "ـ", "(", ")", "[", "]", "{", "}", "…", "«", "»", "—", "-", "_", "\n", "\r", "\t", "'", '"', "’", "•"]:
        t = t.replace(ch, " ")
    # Normaliser caractères arabes (avant retrait possessifs)
    t = t.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    t = t.replace("ى", "ي")
    # ── Retirer les suffixes possessifs PRONOMINAUX arabes ──
    # Attention : ne PAS retirer le ة final (marqueur féminin), qui est écrit ه
    # après normalisation. On ne retire donc que les possessifs qui sont
    # précédés d'une consonne pleine (pas du ة lui-même).
    # Stratégie : on détecte les possessifs AVANT la conversion ة→h,
    # c'est-à-dire quand c'est réellement un ه pronominal.
    # Formes : ـه (son/masculin), ـها (son/elle), ـهم (leur/masc pluriel),
    # ـك (ton/masculin), ـكم (votre).
    # On les retire seulement si le mot d'origine contient au moins 3
    # caractères arabes avant le suffixe.

    def _strip_possessive(m: re.Match) -> str:
        prefix = m.group(1)
        # Conserver ة de féminin (devient ه en dernier ressort) : si le
        # préfixe se termine par un ة (avant conversion), c'est un féminin.
        # Ici on est avant conversion, donc ة reste ة.
        return prefix

    # ── Conversion ة → h APRÈS retrait possessifs (voir plus bas) ──
    # Retirer d'abord les pronoms possessifs qui se terminent par ه/ها/هم/ك/كم
    # mais qui NE SONT PAS précédés de ة (féminin). On utilise la propriété :
    #  - la ة (U+0629) se trouve au milieu d'un mot avant le pronom possessif rarement
    #  - sauf "له" (pour lui), "بها" (avec elle), "فيه" (en lui/elle) → mots de 2 lettres
    #    qu'on conserve dans une whitelist.
    _ARABIC_ALLOW_SHORT = {"له", "بها", "فيه", "منه", "عنه", "لها", "فيها", "منها", "عنها", "لك", "بك", "فيك"}

    def _poss_replacer(m: re.Match) -> str:
        word = m.group(0)
        if word in _ARABIC_ALLOW_SHORT:
            return word  # conserver ces petits mots-outils intacts
        # Si la partie avant le suffixe est de longueur < 2 (mots outils), on conserve
        prefix = m.group(1)
        # Retirer le suffixe possessif
        return prefix

    # Retrait des suffixes possessifs (avant ة→h)
    t = re.sub(r"(\S{2,})ها\b", _poss_replacer, t)
    t = re.sub(r"(\S{2,})هم\b", _poss_replacer, t)
    t = re.sub(r"(\S{2,})كم\b", _poss_replacer, t)
    t = re.sub(r"(\S{2,})ك\b", _poss_replacer, t)
    # Pour ه final : retirer seulement si ce n'est pas une ة/ت précédente,
    # ni un mot se terminant par ئ/ي/ى long (adjectifs : هوائي, ثنائي, عالي…),
    # et si le mot est suffisamment long pour être un nom+possessif.
    # Après normalisation ة est toujours U+0629 à ce stade, et ئ a été
    # décomposé par NFKD → ي + Hamza suscrite (puis le combining est enlevé)
    # → ئ devient ي. Donc il suffit de protéger le ي final aussi.

    def _h_final(m: re.Match) -> str:
        prefix = m.group(1)
        last = prefix[-1] if prefix else ""
        # Ne pas toucher si c'est un ة/ت féminin ou un ي/ئ long final (adjectifs)
        if last in ("ة", "ت", "ي"):
            return prefix + "ه"
        # Sinon retirer le possessif
        return prefix
    t = re.sub(r"(\S{2,})ه\b", _h_final, t)

    # Maintenant on peut convertir ة → h (pour normaliser le reste des recherches)
    t = t.replace("ة", "ه")
    # Normaliser les espaces
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _contains_any(text: str, variants: list[str]) -> bool:
    """Retourne True si l'une des variantes est présente dans le texte.

    On utilise des frontières de mots pour éviter les faux positifs sur
    les tokens courts (ex: "b" qui matche dans "اللمفاويه b" mais aussi dans
    "bien" ou dans d'autres mots). Pour les variantes >= 3 caractères on
    accepte aussi le match en sous-chaîne (tolérant aux pluriels agglutinés).

    ⚠️ Variantes BRUTES : re-normalisées à chaque appel (utilisé seulement
    pour des listes dynamiques) — voir _contains_any_norm pour le chemin
    chaud (lexique pré-normalisé, ~100× plus rapide).
    """
    return _contains_any_norm(text, [n for v in variants if (n := _normalize(v))])


def _contains_any_norm(text: str, variants_norm: list[str]) -> bool:
    """Comme _contains_any, mais variantes DÉJÀ normalisées (chemin chaud).

    Le lexique (_SYNONYMS) est statique : ses variantes sont normalisées UNE
    FOIS au chargement (_SYNONYMS_NORM). Avant ce fix, chaque correction
    re-normalisait ~1500 variantes (NFKD + 25 replace + 6 regex chacune) →
    ~30-60 ms CPU par copie, bloquant la boucle asyncio (GIL). Mesuré :
    30.7 ms/appel → < 0.5 ms/appel.
    """
    for vn in variants_norm:
        if not vn:
            continue
        # Variantes très courtes (1-2 caractères : B, T, pH, km, O2, CO2)
        # → nécessitent une frontière de mot stricte.
        if len(vn) <= 2:
            if re.search(r"(?<![a-z0-9\u0600-\u06ff])" + re.escape(vn) + r"(?![a-z0-9\u0600-\u06ff])", text):
                return True
            continue
        # Match en sous-chaîne (tolérant)
        if vn in text:
            return True
        # Pluriel FR
        if vn + "s" in text:
            return True
    return False


# Variantes du lexique pré-normalisées UNE FOIS au chargement (chemin chaud).
# Le lexique est statique : re-normaliser ~1500 variantes (NFKD + 25 replace
# + 6 regex chacune) à chaque correction coûtait ~30-60 ms CPU par copie et
# bloquait la boucle asyncio (GIL) — voir _contains_any_norm.
_SYNONYMS_NORM: dict[str, list[str]] = {
    kw: [n for v in syns if (n := _normalize(v))]
    for kw, syns in _SYNONYMS.items()
}


def _count_keyword_hits(text: str, keywords: list[str]) -> tuple[int, list[str]]:
    hits = 0
    hit_list: list[str] = []
    for kw in keywords:
        # Essayer le synonyme le plus long qui correspond
        syns = _SYNONYMS_NORM.get(kw, [kw])
        if _contains_any_norm(text, syns):
            hits += 1
            hit_list.append(kw)
    return hits, hit_list


def _detect_lexicon_concepts(question: str, model_answer: str) -> list[str]:
    """Concepts du lexique présents dans (question + réponse modèle).

    Même logique que la déduction automatique des mots-clés de
    deterministic_correct : pour chaque entrée du lexique, on regarde si
    l'un de ses synonymes apparaît dans l'énoncé ou la réponse modèle.
    """
    q_norm = _normalize(question or "")
    m_norm = _normalize(model_answer or "")
    found: list[str] = []
    for kw_id, syns in _SYNONYMS_NORM.items():
        if _contains_any_norm(q_norm, syns) or _contains_any_norm(m_norm, syns):
            found.append(kw_id)
    return found


def can_handle(question: str, model_answer: str = "") -> bool:
    """Le moteur SAVOIR couvre-t-il cette question ?

    Filtre d'applicabilité (audit — le moteur ne doit JAMAIS être utilisé
    comme correcteur généraliste) : au moins 2 concepts du lexique détectés
    dans (énoncé + réponse modèle). En dessous, le moteur tomberait dans son
    fallback générique bienveillant (0.3-0.5×barème) — inacceptable.
    """
    return len(_detect_lexicon_concepts(question, model_answer)) >= 2


def confidence_for(question: str, model_answer: str = "") -> float:
    """Confiance = couverture du lexique sur la question (0..1).

    min(1.0, concepts_détectés / 3) : ≥ 0.92 ⟺ ≥ 3 concepts couverts par le
    lexique — seuil de promotion « local_savoir » (étage haute confiance).
    """
    return min(1.0, len(_detect_lexicon_concepts(question, model_answer)) / 3.0)


# ── Seuil de promotion (audit A1) ────────────────────────────────────
# Un item est "haute confiance" ssi ≥ 3 concepts détectés DANS LA COPIE.
# 0.92 est un seuil DÉRIVÉ (3/3) — informatif, à NE PAS ajuster
# dynamiquement : c'est la formule confidence_for qui devrait évoluer.
SAVOIR_HIGH_CONFIDENCE_MIN_CONCEPTS = 3
SAVOIR_HIGH_CONFIDENCE_THRESHOLD = 0.92  # dérivé = 3 / 3 — informatif


def is_high_confidence(n_concepts_matched: int) -> bool:
    """Un résultat savoir est promu ssi ≥ MIN_CONCEPTS concepts trouvés
    dans la copie de l'élève (périmètre validé par le golden set :
    MAE=0.308, severe=0.0 sur ce sous-groupe)."""
    return n_concepts_matched >= SAVOIR_HIGH_CONFIDENCE_MIN_CONCEPTS


def is_savoir_enabled(verb_slug: str) -> bool:
    """Feature flag PAR VERBE (activation progressive en prod).

    Défaut vide = savoir jamais activé. La liste contient les verb_slug de
    la route (ex. 'analyse', 'extract', 'interpret' — la route reçoit des
    slugs, pas les noms arabes).
    """
    from config import get_settings
    return verb_slug in (get_settings().savoir_enabled_verbs or [])


# ── Highlights sur la copie élève (offsets BRUTS) ────────────────────

def find_keyword_occurrences(text: str, keyword_id: str) -> list[tuple[int, int]]:
    """Occurrences d'un concept dans le texte BRUT (start, end).

    Cherche chaque variante du lexique dans le texte non normalisé
    (case-insensitive) — le texte normalisé (_normalize) retire ponctuation
    et diacritiques : les positions y seraient fausses vs la copie affichée.
    Variantes < 3 caractères ignorées (faux positifs : 'b', 't'...).
    """
    occs: list[tuple[int, int]] = []
    text_lower = text.lower()
    for variant in _SYNONYMS.get(keyword_id, [keyword_id]):
        v = variant.strip().lower()
        if len(v) < 3:
            continue
        start = 0
        while True:
            idx = text_lower.find(v, start)
            if idx == -1:
                break
            occs.append((idx, idx + len(v)))
            start = idx + max(1, len(v))
    # Trier par position puis dédupliquer les occurrences IMBRIQUÉES
    # (ex. 'نواة' ⊂ 'النواة' — deux spans pour le même mot) : garder le
    # premier span (le plus long à la position de début), ignorer ceux qui
    # chevauchent un span déjà retenu.
    occs.sort()
    dedup: list[tuple[int, int]] = []
    for occ in occs:
        if dedup and occ[0] < dedup[-1][1]:
            continue  # chevauche le span précédent → imbriqué
        dedup.append(occ)
    return dedup


def build_savoir_highlights(
    student_answer: str,
    matched_keywords: list[str],
) -> list[dict]:
    """Surligne (good_element) les concepts trouvés DANS la copie.

    Uniquement les matches — on ne surligne jamais ce qui est absent
    (les `missing` sont un champ missing[], pas un highlight[]). Les offsets
    pointent dans le texte brut de l'élève, pas dans la réponse modèle.
    """
    highlights: list[dict] = []
    for kw in matched_keywords:
        for start, end in find_keyword_occurrences(student_answer, kw):
            if start >= end:
                continue
            highlights.append({
                "start": start,
                "end": end,
                "type": "good_element",
                "message_ar": f"جيد: {kw}",
            })
    return highlights


def _savoir_dominant_error(raw: dict, score: int, score_max: int) -> str:
    """Code d'erreur dominant pour un résultat savoir.

    κ modéré (0.449) : le code est une heuristique, la remédiation est
    désactivée (remediation=None) tant que κ < 0.65 sur golden humain.
    """
    if any("خطأ مفاهيمي" in e for e in raw.get("erreurs", [])):
        return "scientific_error"
    if score >= score_max:
        return "all_correct"
    if score > 0:
        return "partial_correct"
    return "insufficient"


def deterministic_correct_v2(
    *,
    question: str,
    student_answer: str,
    score_max: int,
    language: str = "ar",
    expected_keywords: list[str] | None = None,
    mandatory_keywords: list[str] | None = None,
    expected_numeric: dict[str, float] | None = None,
    model_answer: str = "",
) -> dict:
    """Version de deterministic_correct compatible contrat v2 (CACHEABLE).

    Retourne un dict au format du contrat v2 (score, score_max, percentage,
    confidence, matched_criteria, missing, success, errors, highlights,
    feedback_ar, advice_ar, dominant_error_code, sanity_code, provider,
    model) + métadonnées internes _savoir_* (retirées avant mise en cache).

    ⚠️ Concepts attendus : déduits de la RÉPONSE MODÈLE UNIQUEMENT (pas de
    l'énoncé). Déduire depuis la question piégerait la copie parfaite : un
    concept présent dans l'énoncé mais absent du modèle (ex. gs_022
    'immunite'/'rep_humorale') deviendrait un manquant inévitable → la copie
    modèle n'obtiendrait pas le barème. Mesuré sur le golden : MAE copies
    parfaites 0.104 → 0.000 ; MAE globale 0.361 → 0.279.
    """
    if expected_keywords is None:
        expected_keywords = _detect_lexicon_concepts("", model_answer)

    raw = deterministic_correct(
        question=question,
        student_answer=student_answer,
        points=score_max,
        language=language,
        expected_keywords=expected_keywords,
        mandatory_keywords=mandatory_keywords,
        expected_numeric=expected_numeric,
        model_answer=model_answer,
    )

    matched = list(raw.get("mots_cles_trouves", []) or [])
    missing = list(raw.get("mots_cles_manquants", []) or [])
    n_concepts = len(matched)
    confidence = min(1.0, n_concepts / SAVOIR_HIGH_CONFIDENCE_MIN_CONCEPTS)

    score = int(round(float(raw.get("score", 0.0))))
    score = max(0, min(score_max, score))
    percentage = round(100 * score / max(score_max, 1))

    return {
        "source": "local_savoir",
        "score": score,
        "score_max": score_max,
        "percentage": percentage,
        "confidence": confidence,
        "highlights": build_savoir_highlights(student_answer, matched),
        "matched_criteria": matched,
        "unmatched_criteria": [],
        "missing": [
            {"expected": k, "why_ar": f"مطلوب: {k}", "from_model_answer": ""}
            for k in missing
        ],
        "success": [f"تم اكتشاف: {k}" for k in matched],
        "errors": [f"مفقود: {k}" for k in missing],
        "feedback_ar": raw.get("explication", ""),
        "advice_ar": " ".join(raw.get("conseils", "").split()),
        "dominant_error_code": _savoir_dominant_error(raw, score, score_max),
        "sanity_code": "ok",
        "provider": "local",
        "model": "savoir_v1",
        # Métadonnées internes (observabilité, retirées avant cache)
        "_savoir_can_handle": can_handle(question, model_answer),
        "_savoir_confidence": confidence,
        "_savoir_n_concepts": n_concepts,
    }


# ──────────────────────────────────────────────────────────────────────
# Correcteur public
# ──────────────────────────────────────────────────────────────────────
def deterministic_correct(
    question: str,
    student_answer: str,
    points: float = 4.0,
    language: str = "ar",
    expected_keywords: list[str] | None = None,
    mandatory_keywords: list[str] | None = None,
    expected_numeric: dict[str, float] | None = None,
    model_answer: str = "",
) -> dict[str, Any]:
    """Corrige une réponse d'élève SANS LLM (moteur savoir déterministe).

    Args:
        question: énoncé de la question.
        student_answer: réponse de l'élève.
        points: barème (note max).
        language: 'ar' ou 'fr'.
        expected_keywords: mots-clés scientifiques attendus (chacun apporte
            des points). Si None, on déduit automatiquement de la question.
        mandatory_keywords: mots-clés OBLIGATOIRES sous peine de -50%.
        expected_numeric: {nom_règle: valeur_attendue} pour vérifier des
            chiffres (ex: {'atp_resp': 38}).
        model_answer: réponse modèle (utilisée pour extraire des mots-clés
            si expected_keywords est None).
    """
    ans_norm = _normalize(student_answer or "")
    q_norm = _normalize(question or "")
    model_norm = _normalize(model_answer or "")
    points = float(points or 4)

    points_forts: list[str] = []
    erreurs: list[str] = []
    conseils: list[str] = []
    penalites: float = 0.0

    # ── Cas 0 : réponse vide / trop courte ──────────────
    if not ans_norm or len(ans_norm) < 5:
        return {
            "score": 0.0,
            "max_score": points,
            "points_forts": [],
            "erreurs": ["إجابة فارغة أو قصيرة جدا — Réponse vide ou trop courte."],
            "reponse_correcte": model_answer or "راجع الدرس — consultez votre cours.",
            "explication": "اكتب على الأقل كلمتين أو جملة كاملة. — Écrivez au moins une phrase complète.",
            "conseils": "أعد قراءة السؤال وأجب بجملة علمية كاملة.",
            "source": "deterministic-savoir",
            "deterministic": True,
            "tokens_utilises": 0,
            "mots_cles_trouves": [],
            "mots_cles_manquants": (expected_keywords or []) + (mandatory_keywords or []),
        }

    # ── Cas 0b : copier-coller de la question ───────────
    if q_norm and len(q_norm) > 10:
        overlap = sum(1 for w in ans_norm.split() if w in q_norm and len(w) > 2)
        overlap_ratio = overlap / max(1, len(ans_norm.split()))
        if overlap_ratio > 0.85:
            erreurs.append("الإجابة منقولة من السؤال — Réponse copiée depuis la question.")
            penalites += points * 0.7
            language = language or "ar"

    # ── Déduction automatique des mots-clés si non fournis ──
    if not expected_keywords:
        expected_keywords = []
        # Chercher dans le modèle réponse (variantes pré-normalisées — chemin chaud)
        for kw_id, syns in _SYNONYMS_NORM.items():
            if _contains_any_norm(model_norm, syns) or _contains_any_norm(q_norm, syns):
                expected_keywords.append(kw_id)
        # Limiter à 6 mots-clés maximum pour éviter sur-pondération
        expected_keywords = expected_keywords[:6]

    # Toujours vérifier les erreurs graves et les règles numériques (même si
    # on n'a pas de mots-clés explicites à matcher). Si on détecte une erreur
    # grave, on court-circuite vers 0.
    for pattern, msg_ar, penalty in _GRAVE_ERRORS:
        if re.search(pattern, ans_norm, re.IGNORECASE):
            erreurs.append(f"❌ خطأ مفاهيمي: {msg_ar}")
            penalites += points * (0.75 * penalty)

    # Auto-détection des règles numériques DZ
    for rule_id, rule in _NUMERIC_RULES.items():
        if any(re.search(p, ans_norm, re.IGNORECASE) for p in rule["patterns"]):
            for pat in rule["patterns"]:
                m = re.search(rf"({pat}).{{0,30}}?(\d+)", ans_norm, re.IGNORECASE)
                if m:
                    try:
                        val = int(m.group(2))
                        if val != rule["expected"]:
                            erreurs.append(
                                f"❌ قيمة عددية خاطئة: قيمة {rule_id} الصحيحة هي {rule['expected']} وليس {val} حسب البرنامج الرسمي."
                            )
                            penalites += points * 0.25
                    except ValueError:
                        pass
                    break

    # Si vraiment rien à matcher, on évalue sur critères génériques
    if not expected_keywords and not mandatory_keywords:
        # Pénalité de longueur si trop courte
        if len(ans_norm) < 20:
            erreurs.append("الإجابة قصيرة — Réponse trop courte pour un exercice noté.")
            penalites += 0.3
        # Base générique (bienveillance)
        base = points * 0.5 if len(ans_norm) > 50 else points * 0.3
        score = max(0.0, min(points, base - penalites))
        if penalites > points * 0.5:
            score = 0.0
        return {
            "score": round(score, 2),
            "max_score": points,
            "points_forts": points_forts,
            "erreurs": erreurs[:5],
            "reponse_correcte": model_answer,
            "explication": ("راجع الدرس — Consultez le cours, erreur conceptuelle grave."
                            if penalites > points * 0.5 else
                            "تم التقييم بواسطة المصحح المحلي (كلمات دلالية غير محددة لهذا السؤال)."),
            "conseils": "استعمل مصطلحات علمية دقيقة." + (" راجع الدرس لتصحيح الأخطاء المفاهيمية." if penalites > 0 else ""),
            "source": "deterministic-savoir",
            "deterministic": True,
            "tokens_utilises": 0,
            "mots_cles_trouves": [],
            "mots_cles_manquants": [],
            "penalites": round(penalites, 2),
            "mots_cles_coverage": 0.0,
        }

    # ── Calcul du score sur les mots-clés attendus ──────
    hits, hit_list = _count_keyword_hits(ans_norm, expected_keywords or [])
    manquants = [kw for kw in (expected_keywords or []) if kw not in hit_list]
    total_kw = max(1, len(expected_keywords or []))
    base_score = (hits / total_kw) * points

    # Points forts pour chaque mot-clé trouvé
    for kw in hit_list:
        if language == "fr":
            points_forts.append(f"✅ Le concept '{kw}' est mentionné correctement.")
        else:
            points_forts.append(f"✅ ذكرت المفهوم العلمي : {kw}")

    # ── Mots-clés obligatoires ──────────────────────────
    if mandatory_keywords:
        hits_mandatory, _ = _count_keyword_hits(ans_norm, mandatory_keywords)
        if hits_mandatory < len(mandatory_keywords):
            miss = [m for m in mandatory_keywords if not _contains_any_norm(ans_norm, _SYNONYMS_NORM.get(m, [m]))]
            msg_miss = " ، ".join(miss) if language == "ar" else ", ".join(miss)
            if language == "fr":
                erreurs.append(f"Concept(s) obligatoire(s) manquant(s): {msg_miss}.")
            else:
                erreurs.append(f"مفهوم أساسي غائب: {msg_miss}")
            # Pénalité : jusqu'à -50% si aucun obligatoire, proportionnel sinon
            penalites += points * 0.5 * (1 - hits_mandatory / max(1, len(mandatory_keywords)))

    # ── Erreurs graves et règles numériques DZ ──────────
    # Elles ont déjà été exécutées au-dessus (avant le fallback), mais on
    # s'assure qu'elles tournent aussi lorsque expected_keywords est fourni.
    # Pour éviter les doublons on ne les ré-exécute que si aucune erreur n'a
    # encore été remplie par le code ci-dessus (le fallback sort prématurément).
    if not any("خطأ مفاهيمي" in e for e in erreurs):
        for pattern, msg_ar, penalty in _GRAVE_ERRORS:
            if re.search(pattern, ans_norm, re.IGNORECASE):
                erreurs.append(f"❌ خطأ مفاهيمي: {msg_ar}")
                penalites += points * (0.75 * penalty)
    if not any("قيمة عددية" in e for e in erreurs):
        rules_to_check = dict(expected_numeric or {})
        for rule_id, rule in _NUMERIC_RULES.items():
            if any(re.search(p, ans_norm, re.IGNORECASE) for p in rule["patterns"]):
                rules_to_check.setdefault(rule_id, rule["expected"])
        for rule_id, expected in rules_to_check.items():
            for pat in _NUMERIC_RULES.get(rule_id, {}).get("patterns", [r"\d+"]):
                m = re.search(rf"({pat}).{{0,30}}?(\d+)", ans_norm, re.IGNORECASE)
                if m:
                    try:
                        val = int(m.group(2))
                        if val != expected:
                            erreurs.append(
                                f"❌ قيمة عددية خاطئة: قيمة {rule_id} الصحيحة هي {expected} وليس {val} حسب البرنامج الرسمي."
                            )
                            penalites += points * 0.25
                    except ValueError:
                        pass
                    break

    # ── Calcul final ────────────────────────────────────
    score = max(0.0, min(points, base_score - penalites))

    # Si tous mots-clés trouvés et pas de pénalité : note pleine avec bonus
    if hits == total_kw and penalites < 0.1 and len(ans_norm) > 30:
        score = points
        points_forts.append("🌟 إجابة كاملة ودقيقة علميا — Excellente réponse" if language != "fr"
                            else "🌟 Réponse complète et scientifiquement exacte.")

    # Conseils automatiques
    if manquants:
        if language == "fr":
            conseils.append(f"Ajoutez les concepts manquants : {', '.join(manquants[:3])}.")
        else:
            conseils.append(f"أدرج المفاهيم المفقودة: {' ، '.join(manquants[:3])}.")
    if penalites > 0:
        if language == "fr":
            conseils.append("Relisez votre cours pour corriger les erreurs conceptuelles.")
        else:
            conseils.append("راجع الدرس لتصحيح الأخطاء المفاهيمية.")
    if not conseils:
        if language == "fr":
            conseils.append("Continuez — votre réponse est dans la bonne direction.")
        else:
            conseils.append("أحسنت — واصل الإجابة بهذه الدقة.")

    # Feedback final
    pct = score / points if points else 0
    if pct >= 0.8:
        explication = "إجابة ممتازة وشاملة." if language != "fr" else "Réponse excellente et complète."
    elif pct >= 0.5:
        explication = "إجابة جزئية، بُنيت على فهم جيد لكن تنقصك بعض التفاصيل." if language != "fr" \
                      else "Réponse partielle — bonne compréhension mais quelques détails manquent."
    elif pct > 0:
        explication = "بداية إجابة، تحتاج إلى استعمال مصطلحات علمية أكثر." if language != "fr" \
                      else "Début de réponse — utilisez davantage de termes scientifiques."
    else:
        explication = "راجع الدرس — Consultez le cours, la réponse est hors sujet ou insuffisante."

    return {
        "score": round(score, 2),
        "max_score": points,
        "points_forts": points_forts[:5],
        "erreurs": erreurs[:5],
        "reponse_correcte": model_answer,
        "explication": explication,
        "conseils": " ".join(conseils),
        "source": "deterministic-savoir",
        "deterministic": True,
        "tokens_utilises": 0,
        "mots_cles_trouves": hit_list,
        "mots_cles_manquants": manquants,
        "penalites": round(penalites, 2),
        "mots_cles_coverage": round(hits / total_kw, 2) if total_kw else 0.0,
    }
