"""Generate complete bilingual SVT lexique JSON (320+ terms).
Usage: python scripts/generate_lexique_complet.py
Output: data/lexique_svt_terminale_complet.json
"""
import json
import os

OUTPUT = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                      "data", "lexique_svt_terminale_complet.json")

terms = []
links = []
N = [0]


def nid():
    N[0] += 1
    return f"term-{N[0]:03d}"


def add(terme_fr, terme_ar, type, definition_fr, definition_ar,
        importance="moyenne", bac_frequent=False, abreviation=None,
        synonymes_fr=None, synonymes_ar=None,
        chapitre_principal="", micro_concept_id="",
        exemples_contexte=None, termes_lies=None, tags=None):
    tid = nid()
    terms.append(dict(
        id=tid,
        terme_fr=terme_fr,
        terme_ar=terme_ar,
        abreviation=abreviation,
        type=type,
        definition_fr=definition_fr,
        definition_ar=definition_ar,
        synonymes_fr=synonymes_fr or [],
        synonymes_ar=synonymes_ar or [],
        importance=importance,
        bac_frequent=bac_frequent,
        chapitre_principal=chapitre_principal,
        micro_concept_id=micro_concept_id,
        exemples_contexte=exemples_contexte or [],
        termes_lies=termes_lies or [],
        tags=tags or [],
    ))
    return tid


def link(source, target, relation, type="dependance"):
    links.append(dict(source=source, target=target,
                      relation=relation, type=type))


# ═══════════════════════════════════════════════════════════
# DOMAINE 1 — Protéines
# ═══════════════════════════════════════════════════════════
D1 = "domaine-1"
D1_FR = "Spécialisation fonctionnelle des protéines"
D1_AR = "التخصص الوظيفي للبروتينات"

C1_MC = "ch1_proteines"
C1_CH = "Synthèse des protéines"

# Cat 1.1 — Génétique moléculaire
ADN = add("ADN", "الحمض النووي ADN", "molecule",
    "Acide désoxyribonucléique, support de l'information génétique, constitué de deux chaînes complémentaires en double hélice",
    "الحمض النووي الريبي منقوص الأكسجين، حامل المعلومات الوراثية، يتكون من سلسلتين متكاملتين بشكل حلزوني مزدوج",
    "critique", True, "ADN", ["acide désoxyribonucléique"], ["الدنا"], C1_CH, C1_MC,
    ["L'ADN est une molécule en double hélice située dans le noyau", "La transcription utilise l'ADN comme matrice pour synthétiser l'ARNm"],
    tags=["molecule", "genetique", "structure", "noyau"])

ARNm = add("ARN messager", "الحمض النووي الريبي الرسول", "molecule",
    "Molécule d'ARN simple brin qui transmet l'information génétique de l'ADN du noyau aux ribosomes",
    "جزيء ARN أحادي السلسلة ينقل المعلومات الوراثية من ADN النواة إلى الريبوزومات في الهيولى",
    "critique", True, "ARNm", ["messager"], ["ARN الرسول"], C1_CH, C1_MC,
    ["L'ARNm est synthétisé lors de la transcription", "La séquence des codons de l'ARNm détermine la séquence des acides aminés"],
    tags=["molecule", "transcription", "traduction"])

ARNP = add("ARN polymérase", "ARN بوليميراز", "enzyme",
    "Enzyme responsable de la transcription de l'ADN en ARNm en catalysant la liaison des ribonucléotides",
    "إنزيم مسؤول عن استنساخ ADN إلى ARNm عن طريق تحفيز ارتباط الريبونوكليوتيدات",
    "haute", True, None, ["ARN polymérase ADN-dépendante"], ["إنزيم الاستنساخ"], C1_CH, C1_MC,
    ["L'ARN polymérase se fixe au promoteur du gène", "L'ARN polymérase se déplace le long du brin matrice d'ADN"],
    tags=["enzyme", "transcription", "proteine"])

CGEN = add("Code génétique", "الشفرة الوراثية", "concept",
    "Système de correspondance entre les codons de l'ARNm et les acides aminés lors de la traduction",
    "نظام تطابق بين الرامزات في ARNm والأحماض الأمينية أثناء الترجمة",
    "critique", True, None, ["code génétique standard"], ["الشفرة الوراثية القياسية"], C1_CH, C1_MC,
    ["Le codon AUG code pour la méthionine et sert de codon d'initiation", "Le code génétique est universel et redondant"],
    tags=["concept", "traduction", "codon"])

TRANSC = add("Transcription", "الاستنساخ", "processus",
    "Processus de synthèse d'une molécule d'ARNm à partir d'un gène d'ADN catalysé par l'ARN polymérase",
    "عملية تركيب جزيء ARNm انطلاقاً من مورثة ADN بتحفيز من ARN بوليميراز",
    "critique", True, None, ["transcription génique"], ["النسخ"], C1_CH, C1_MC,
    ["La transcription a lieu dans le noyau des cellules eucaryotes", "Seul un brin d'ADN sert de matrice pour la transcription"],
    tags=["processus", "expression", "genetique"])

TRAD = add("Traduction", "الترجمة", "processus",
    "Processus de synthèse d'une chaîne polypeptidique à partir de l'ARNm au niveau des ribosomes par lecture des codons",
    "عملية تركيب سلسلة بولي ببتيدية انطلاقاً من ARNm على مستوى الريبوزومات بقراءة الرامزات",
    "critique", True, None, [], ["الترجمة"], C1_CH, C1_MC,
    ["La traduction se déroule dans le cytoplasme au niveau des ribosomes", "L'initiation de la traduction commence au codon AUG"],
    tags=["processus", "proteine", "ribosome"])

RIBO = add("Ribosome", "الريبوزوم", "organite",
    "Complexe ribonucléoprotéique composé de deux sous-unités, site de la synthèse des protéines",
    "معقد ريبونوكليوتيدي بروتيني يتكون من تحت وحدتين، موقع تركيب البروتينات بترجمة ARNm",
    "haute", True, None, ["ribosome 80S"], ["الريبوسوم"], C1_CH, C1_MC,
    ["Les ribosomes libres synthétisent des protéines cytoplasmiques", "Les ribosomes fixés au RE synthétisent des protéines sécrétées"],
    tags=["organite", "traduction", "proteine"])

COD = add("Codon", "الرامزة", "concept",
    "Séquence de trois nucléotides de l'ARNm codant pour un acide aminé spécifique",
    "تسلسل من ثلاث نوكليوتيدات في ARNm يرمز لحمض أميني محدد",
    "haute", True, None, [], ["الرامزة", "الكودون"], C1_CH, C1_MC,
    ["Le codon AUG est le codon d'initiation", "Les codons stop UAA, UAG, UGA marquent la fin de la traduction"],
    tags=["concept", "genetique", "codon"])

PROM = add("Promoteur", "المحفز", "concept",
    "Séquence d'ADN située en amont d'un gène, permettant la fixation de l'ARN polymérase pour initier la transcription",
    "تسلسل ADN يقع قبل المورثة، يسمح بتثبيت ARN بوليميراز لبدء الاستنساخ",
    "haute", True, None, [], ["المحفز"], C1_CH, C1_MC,
    ["Le promoteur n'est pas transcrit", "La région promotrice contient la boîte TATA chez les eucaryotes"],
    tags=["concept", "regulation", "genetique"])

INT = add("Intron", "الإنترون", "concept",
    "Séquence non codante d'un gène eucaryote, transcrite mais excisée lors de l'épissage de l'ARN pré-messager",
    "تسلسل غير مشفر في مورثة الكائنات حقيقية النواة، يُنسخ ثم يُستأصل أثناء وصل ARN الأولي",
    "haute", True, None, [], ["الإنترون"], C1_CH, C1_MC,
    ["Les introns sont excisés lors de l'épissage", "Les introns séparent les exons dans l'ADN génomique"],
    tags=["concept", "genetique", "epissage"])

EXON = add("Exon", "الإكسون", "concept",
    "Séquence codante d'un gène eucaryote conservée dans l'ARNm mature après épissage",
    "تسلسل مشفر في مورثة الكائنات حقيقية النواة يُحفظ في ARNm الناضج بعد الوصل",
    "haute", True, None, [], ["الإكسون"], C1_CH, C1_MC,
    ["Les exons contiennent l'information pour la séquence protéique", "L'épissage assemble les exons entre eux"],
    tags=["concept", "genetique", "epissage"])

EPIS = add("Épissage", "الوصل", "processus",
    "Processus d'excision des introns et de ligature des exons dans l'ARN pré-messager pour former l'ARNm mature",
    "عملية استئصال الإنترونات وربط الإكسونات في ARN الأولي لتشكيل ARNm الناضج",
    "haute", True, None, ["splicing"], ["الوصل"], C1_CH, C1_MC,
    ["L'épissage se déroule dans le noyau", "L'épissage alternatif permet de produire plusieurs protéines à partir d'un même gène"],
    tags=["processus", "expression", "genetique"])

NUCL = add("Nucléotide", "النوكليوتيد", "molecule",
    "Unité de base des acides nucléiques composée d'un phosphate, d'un sucre (désoxyribose/ribose) et d'une base azotée",
    "وحدة أساسية للأحماض النووية مكونة من فوسفات وسكر (ريبوز منقوص الأكسجين/ريبوز) وقاعدة آزوتية",
    "haute", True, None, [], ["النوكليوتيد"], C1_CH, C1_MC,
    ["L'ADN contient les nucléotides A, T, G, C", "L'ARN contient les nucléotides A, U, G, C"],
    tags=["molecule", "genetique", "structure"])

BASEA = add("Base azotée", "القاعدة الآزوتية", "molecule",
    "Composé organique cyclique contenant de l'azote : adénine (A), guanine (G), cytosine (C), thymine (T) ou uracile (U)",
    "مركب عضوي حلقي يحتوي على النيتروجين: الأدينين (A) والغوانين (G) والسيتوزين (C) والثيمين (T) أو اليوراسيل (U)",
    "moyenne", True, None, [], ["القاعدة النيتروجينية"], C1_CH, C1_MC,
    ["Les bases puriques sont A et G", "Les bases pyrimidiques sont C, T et U"],
    tags=["molecule", "genetique", "structure"])

COMPL = add("Complémentarité des bases", "تتام القواعد", "concept",
    "Règle d'appariement spécifique A-T (ou A-U) et C-G par liaisons hydrogène entre les deux brins d'ADN ou ADN/ARN",
    "قاعدة الاقتران النوعي A-T (أو A-U) و C-G بواسطة روابط هيدروجينية بين سلسلتي ADN أو ADN/ARN",
    "critique", True, None, [], ["التتام"], C1_CH, C1_MC,
    ["A s'apparie avec T (2 liaisons H)", "C s'apparie avec G (3 liaisons H)"],
    tags=["concept", "genetique", "structure"])

MUT = add("Mutation", "الطفرة", "concept",
    "Modification de la séquence nucléotidique de l'ADN, pouvant être ponctuelle (substitution, insertion, délétion) ou chromosomique",
    "تعديل في تسلسل النوكليوتيدات في ADN، يمكن أن يكون نقطياً (استبدال، إدراج، حذف) أو صبغياً",
    "haute", True, None, [], ["الطفرة"], C1_CH, C1_MC,
    ["Les mutations ponctuelles peuvent être silencieuses, faux-sens ou non-sens", "Les agents mutagènes augmentent la fréquence des mutations"],
    tags=["concept", "genetique", "variation"])

BRIN = add("Brin matrice", "السلسلة الماتريس", "concept",
    "Brin d'ADN transcrit par l'ARN polymérase pour synthétiser l'ARNm complémentaire",
    "سلسلة ADN التي ينسخها ARN بوليميراز لتركيب ARNm المتمم",
    "haute", True, None, [], ["السلسلة الناسخة"], C1_CH, C1_MC,
    ["L'ARNm est complémentaire du brin matrice", "Le brin non transcrit est appelé brin codant"],
    tags=["concept", "transcription", "genetique"])

GENE = add("Gène", "المورثة", "concept",
    "Segment d'ADN portant l'information génétique nécessaire à la synthèse d'une protéine fonctionnelle ou d'un ARN",
    "قطعة من ADN تحمل المعلومات الوراثية اللازمة لتركيب بروتين وظيفي أو ARN",
    "critique", True, None, [], ["الجين"], C1_CH, C1_MC,
    ["Un gène est constitué de promoteur, d'exons et d'introns", "L'expression d'un gène aboutit à une protéine fonctionnelle"],
    tags=["concept", "genetique", "heredite"])

# Cat 1.2 — Structure des protéines
C2_MC = "ch_structure"
C2_CH = "Structure-fonction des protéines"

AA = add("Acide aminé", "حمض أميني", "molecule",
    "Molécule organique constituée d'une fonction amine, d'une fonction carboxyle et d'une chaîne latérale R variable liés à un carbone alpha",
    "جزيء عضوي يتكون من مجموعة أمين ومجموعة كربوكسيل وسلسلة جانبية R متغيرة مرتبطة بذرة كربون ألفا",
    "critique", True, "AA", ["acide α-aminé"], ["الحمض الأميني"], C2_CH, C2_MC,
    ["Il existe 20 acides aminés standards", "Les acides aminés sont liés par des liaisons peptidiques"],
    tags=["molecule", "proteine", "structure"])

LPEP = add("Liaison peptidique", "الرابطة الببتيدية", "concept",
    "Liaison covalente entre le groupement carboxyle d'un acide aminé et le groupement amine du suivant avec libération d'une molécule d'eau",
    "رابطة تساهمية بين مجموعة الكربوكسيل لحمض أميني ومجموعة الأمين للحمض الأميني التالي مع تحرير جزيء ماء",
    "haute", True, None, ["liaison amide"], ["الرابطة الببتيدية"], C2_CH, C2_MC,
    ["La liaison peptidique se forme par une réaction de déshydratation", "L'hydrolyse des liaisons peptidiques libère les acides aminés"],
    tags=["concept", "liaison", "proteine"])

STERT = add("Structure tertiaire", "البنية الثالثية", "concept",
    "Repliement tridimensionnel d'une chaîne polypeptidique stabilisé par des liaisons hydrogène, ioniques, hydrophobes et des ponts disulfure",
    "الطي ثلاثي الأبعاد لسلسلة بولي ببتيدية يثبت بواسطة روابط هيدروجينية وأيونية وكارهة للماء وجسور كبريتية",
    "haute", True, None, ["repliement tridimensionnel"], ["الطي الفراغي"], C2_CH, C2_MC,
    ["La structure tertiaire est essentielle à la fonction catalytique des enzymes", "La dénaturation détruit la structure tertiaire"],
    tags=["concept", "structure", "proteine"])

SACT = add("Site actif", "الموقع الفعال", "concept",
    "Région spécifique de l'enzyme constituée d'acides aminés précis responsable de la fixation du substrat et de la catalyse",
    "منطقة نوعية في الإنزيم تتكون من أحماض أمينية محددة مسؤولة عن تثبيت الركيزة وتحفيز التفاعل",
    "critique", True, None, ["site catalytique"], ["الموقع النشط"], C2_CH, C2_MC,
    ["Le site actif est complémentaire à la forme du substrat", "Une mutation dans le site actif peut inactiver l'enzyme"],
    tags=["concept", "enzyme", "catalyse", "proteine"])

STERP = add("Structure primaire", "البنية الأولية", "concept",
    "Séquence linéaire des acides aminés dans une chaîne polypeptidique, déterminée par la séquence nucléotidique du gène",
    "التسلسل الخطي للأحماض الأمينية في سلسلة بولي ببتيدية، يحدده التسلسل النوكليوتيدي للمورثة",
    "haute", True, None, [], ["البنية الأولية"], C2_CH, C2_MC,
    ["La structure primaire détermine les niveaux supérieurs d'organisation", "Une mutation peut modifier la structure primaire"],
    tags=["concept", "structure", "proteine"])

STERS = add("Structure secondaire", "البنية الثانية", "concept",
    "Repliement local de la chaîne polypeptidique en hélice alpha ou feuillet bêta stabilisé par des liaisons hydrogène",
    "طي موضعي للسلسلة البولي ببتيدية بشكل حلزون ألفا أو صفحة بيتا يثبت بروابط هيدروجينية",
    "haute", True, None, [], ["البنية الثانية"], C2_CH, C2_MC,
    ["L'hélice alpha est stabilisée par des liaisons H entre CO et NH", "Les feuillets bêta peuvent être parallèles ou antiparallèles"],
    tags=["concept", "structure", "proteine"])

PQ = add("Structure quaternaire", "البنية الرابعية", "concept",
    "Association de plusieurs chaînes polypeptidiques (sous-unités) en un complexe protéique fonctionnel",
    "ارتباط عدة سلاسل بولي ببتيدية (وحدات فرعية) في معقد بروتيني وظيفي",
    "moyenne", True, None, [], ["البنية الرابعية"], C2_CH, C2_MC,
    ["L'hémoglobine est un exemple de structure quaternaires", "Chaque sous-unité peut avoir un rôle spécifique"],
    tags=["concept", "structure", "proteine"])

DENAT = add("Dénaturation", "التشويه", "processus",
    "Perte de la structure tridimensionnelle native d'une protéine sous l'effet de la chaleur, du pH ou d'agents chimiques, entraînant une perte de fonction",
    "فقدان البنية الفراغية الطبيعية للبروتين تحت تأثير الحرارة أو الpH أو عوامل كيميائية مما يؤدي إلى فقدان الوظيفة",
    "haute", True, None, [], ["التشويه", "إفساد البروتين"], C2_CH, C2_MC,
    ["La dénaturation est souvent irréversible", "Un pH extrême ou une température élevée dénature les protéines"],
    tags=["processus", "proteine", "structure"])

AMPHO = add("Caractère amphotère", "السلوك الأمفوتيري", "concept",
    "Propriété d'un acide aminé de se comporter à la fois comme un acide (donneur de H+) et comme une base (accepteur de H+)",
    "خاصية الحمض الأميني في التصرف كحمض (مانح H+) وكقاعدة (مستقبل H+) في آن واحد",
    "haute", True, None, [], ["السلوك الأمفوتيري"], C2_CH, C2_MC,
    ["Le caractère amphotère est dû aux groupes NH2 et COOH", "Le pH isoélectrique est le pH où la charge nette est nulle"],
    tags=["concept", "chimie", "acideamine"])

PONTD = add("Pont disulfure", "الجسر الكبريتي", "concept",
    "Liaison covalente entre deux résidus cystéine formant un pont -S-S-, stabilisant la structure tertiaire des protéines",
    "رابطة تساهمية بين بقيتي سيستئين تشكل جسراً -S-S- تثبت البنية الثالثية للبروتينات",
    "moyenne", True, None, [], ["الجسر الكبريتي"], C2_CH, C2_MC,
    ["Les ponts disulfure sont importants dans les protéines sécrétées", "La réduction des ponts disulfure déstabilise la protéine"],
    tags=["concept", "liaison", "structure"])

POLYP = add("Chaîne polypeptidique", "السلسلة البولي ببتيدية", "molecule",
    "Enchaînement linéaire d'acides aminés reliés par des liaisons peptidiques, formant une protéine après repliement",
    "تسلسل خطي من الأحماض الأمينية مرتبطة بروابط ببتيدية، تشكل بروتيناً بعد الطي",
    "haute", True, None, [], ["السلاسل الببتيدية"], C2_CH, C2_MC,
    ["La chaîne polypeptidique est synthétisée lors de la traduction", "Le nombre d'acides aminés détermine la taille de la protéine"],
    tags=["molecule", "proteine", "structure"])

# Cat 1.3 — Enzymologie
C3_MC = "ch2_enzymes"
C3_CH = "Activité enzymatique"

ENZ = add("Enzyme", "إنزيم", "enzyme",
    "Protéine catalytique qui accélère une réaction biochimique spécifique sans être consommée en abaissant l'énergie d'activation",
    "بروتين محفز يسرع تفاعل كيميائي حيوي نوعي دون أن يُستهلك بخفض طاقة التنشيط",
    "critique", True, None, ["biocatalyseur", "catalyseur biologique"], ["الحفاز الحيوي"], C3_CH, C3_MC,
    ["Le maltase hydrolyse le maltose en deux molécules de glucose", "La catalase décompose le peroxyde d'hydrogène en eau et oxygène"],
    tags=["enzyme", "proteine", "catalyse"])

SUB = add("Substrat", "الركيزة", "concept",
    "Molécule sur laquelle agit une enzyme, se fixant au niveau du site actif pour être transformée en produit",
    "الجزيء الذي يؤثر عليه الإنزيم حيث يثبت في الموقع الفعال ليتحول إلى ناتج",
    "haute", True, "S", [], ["مادة التفاعل"], C3_CH, C3_MC,
    ["Le lactose est le substrat de la lactase", "Plus la concentration en substrat augmente, plus la vitesse initiale augmente"],
    tags=["concept", "enzyme", "catalyse"])

COMPE = add("Complexe enzyme-substrat", "معقد إنزيم-ركيزة", "concept",
    "Association temporaire entre l'enzyme et son substrat au niveau du site actif formant un complexe intermédiaire réactif",
    "ارتباط مؤقت بين الإنزيم وركيزته على مستوى الموقع الفعال يشكّل معقداً وسيطاً نشطاً",
    "haute", True, None, ["complexe ES"], ["معقد ES"], C3_CH, C3_MC,
    ["Le complexe ES est très instable", "La formation du complexe ES suit le modèle clé-serrure ou ajustement induit"],
    tags=["concept", "enzyme", "catalyse"])

VITI = add("Vitesse initiale", "السرعة الابتدائية", "concept",
    "Vitesse de réaction enzymatique mesurée au début de la réaction lorsque la concentration en substrat est encore saturante",
    "سرعة التفاعل الإنزيمي المقاسة في بداية التفاعل عندما يكون تركيز الركيزة لا يزال مشبعاً",
    "haute", True, "Vi", [], ["السرعة الابتدائية"], C3_CH, C3_MC,
    ["La vitesse initiale est proportionnelle à la concentration en enzyme", "La Vi est mesurée à partir de la pente de la courbe produit/temps"],
    tags=["concept", "enzyme", "cinetique"])

KM = add("Constante de Michaelis", "ثابت ميكايليس", "concept",
    "Concentration en substrat pour laquelle la vitesse de réaction est égale à la moitié de la vitesse maximale (Vmax/2), reflétant l'affinité enzyme-substrat",
    "تركيز الركيزة الذي تكون عنده سرعة التفاعل نصف السرعة القصوى (Vmax/2), يعكس ألفة الإنزيم للركيزة",
    "haute", True, "Km", ["constante de Michaelis-Menten"], ["ثابت ميكايليس"], C3_CH, C3_MC,
    ["Un Km faible indique une forte affinité", "Le Km est caractéristique d'un couple enzyme-substrat"],
    tags=["concept", "enzyme", "cinetique", "constante"])

VMAX = add("Vitesse maximale", "السرعة القصوى", "concept",
    "Vitesse maximale atteinte par une réaction enzymatique lorsque tous les sites actifs sont saturés par le substrat",
    "السرعة القصوى التي يبلغها التفاعل الإنزيمي عندما تكون جميع المواقع الفعالة مشبعة بالركيزة",
    "haute", True, "Vmax", [], ["السرعة القصوى"], C3_CH, C3_MC,
    ["Vmax dépend de la concentration en enzyme", "Vmax est atteinte à saturation en substrat"],
    tags=["concept", "enzyme", "cinetique"])

EACT = add("Énergie d'activation", "طاقة التنشيط", "concept",
    "Énergie minimale nécessaire pour qu'une réaction chimique puisse se produire, abaissée par l'enzyme",
    "الطاقة الدنيا اللازمة لحدوث تفاعل كيميائي، يخفضها الإنزيم",
    "haute", True, None, [], ["طاقة التنشيط"], C3_CH, C3_MC,
    ["L'enzyme abaisse l'énergie d'activation sans modifier l'équilibre", "La barrière énergétique est plus facile à franchir grâce à l'enzyme"],
    tags=["concept", "energie", "catalyse"])

INHIB = add("Inhibition", "التثبيط", "concept",
    "Diminution de l'activité enzymatique par une molécule inhibitrice qui se fixe sur l'enzyme de façon compétitive, non compétitive ou incompétitive",
    "انخفاض النشاط الإنزيمي بجزيء مثبط يثبت على الإنزيم بطريقة تنافسية أو غير تنافسية أو لاتنافسية",
    "haute", True, None, [], ["التثبيط"], C3_CH, C3_MC,
    ["L'inhibiteur compétitif se fixe au site actif", "L'inhibiteur non compétitif se fixe en dehors du site actif"],
    tags=["concept", "regulation", "enzyme"])

INHCO = add("Inhibition compétitive", "التثبيط التنافسي", "concept",
    "Type d'inhibition où l'inhibiteur entre en compétition avec le substrat pour le site actif de l'enzyme",
    "نوع من التثبيط حيث يتنافس المثبط مع الركيزة على الموقع الفعال للإنزيم",
    "haute", True, None, [], ["التثبيط التنافسي"], C3_CH, C3_MC,
    ["L'inhibition compétitive peut être levée par augmentation de [S]", "Le Km augmente, Vmax reste inchangée"],
    tags=["concept", "regulation", "enzyme"])

PH = add("pH optimal", "الأس الهيدروجيني الأمثل", "concept",
    "Valeur de pH pour laquelle l'activité enzymatique est maximale, variant selon l'enzyme et son environnement physiologique",
    "قيمة pH التي يكون عندها النشاط الإنزيمي أقصاه، تختلف حسب الإنزيم ووسطه الفسيولوجي",
    "haute", True, None, [], ["درجة الحموضة المثلى"], C3_CH, C3_MC,
    ["Le pH optimal de la pepsine est 2 (estomac)", "Le pH optimal de la trypsine est 8 (intestin)"],
    tags=["concept", "enzyme", "physicochimie"])

TEMP = add("Température optimale", "درجة الحرارة المثلى", "concept",
    "Température à laquelle l'activité enzymatique est maximale, au-delà de laquelle la dénaturation thermique réduit l'activité",
    "درجة الحرارة التي يكون عندها النشاط الإنزيمي أقصاه، وبعدها يؤدي التشويه الحراري إلى انخفاض النشاط",
    "haute", True, None, [], ["درجة الحرارة المثلى"], C3_CH, C3_MC,
    ["La température optimale des enzymes humaines est ~37°C", "Au-delà de 45°C, la plupart des enzymes se dénaturent"],
    tags=["concept", "enzyme", "physicochimie"])

COENZ = add("Coenzyme", "المرافق الإنزيمي", "molecule",
    "Molécule organique non protéique nécessaire à l'activité de certaines enzymes, souvent dérivée de vitamines",
    "جزيء عضوي غير بروتيني ضروري لنشاط بعض الإنزيمات، مشتق غالباً من الفيتامينات",
    "moyenne", True, None, [], ["العامل المرافق"], C3_CH, C3_MC,
    ["Le NADH et FADH2 sont des coenzymes", "Les coenzymes sont régénérées après la réaction"],
    tags=["molecule", "enzyme", "cofacteur"])

ALLOS = add("Site allostérique", "الموقع الألستيري", "concept",
    "Site de fixation régulateur distinct du site actif, où la fixation d'un effecteur module l'activité enzymatique",
    "موقع تثبيت تنظيمي منفصل عن الموقع الفعال، حيث يعدل ارتباط مؤثر النشاط الإنزيمي",
    "moyenne", True, None, [], ["الموقع الألستيري"], C3_CH, C3_MC,
    ["Les enzymes allostériques ont une courbe sigmoïde", "L'effecteur allostérique peut être activateur ou inhibiteur"],
    tags=["concept", "regulation", "enzyme"])

SPECI = add("Spécificité enzymatique", "النوعية الإنزيمية", "concept",
    "Propriété d'une enzyme à reconnaître un substrat ou un groupe de substrats spécifiques et à catalyser une réaction particulière",
    "خاصية الإنزيم في التعرف على ركيزة أو مجموعة ركائز نوعية وتحفيز تفاعل معين",
    "haute", True, None, ["spécificité de substrat"], ["النوعية الإنزيمية"], C3_CH, C3_MC,
    ["La spécificité absolue : une enzyme = un substrat", "La spécificité de groupe : l'enzyme reconnaît un type de liaison"],
    tags=["concept", "enzyme", "specificite"])

# Cat 1.4 — Immunologie
C4_MC = "ch3_immunite"
C4_CH = "Immunologie"

AC = add("Anticorps", "جسم مضاد", "molecule",
    "Glycoprotéine de forme Y produite par les plasmocytes, capable de se lier spécifiquement à un antigène pour former un complexe immun",
    "بروتين سكري على شكل Y ينتجه البلازموسيت، قادر على الارتباط نوعياً بمستضد لتشكيل معقد مناعي",
    "critique", True, "Ac", ["immunoglobuline", "Ig"], ["الغلوبولين المناعي"], C4_CH, C4_MC,
    ["Les anticorps neutralisent les toxines et les virus", "Chaque anticorps possède deux sites de fixation pour l'antigène"],
    tags=["molecule", "immunite", "proteine"])

AG = add("Antigène", "مستضد", "concept",
    "Toute substance étrangère à l'organisme capable de déclencher une réponse immunitaire en se liant spécifiquement à un anticorps ou un récepteur lymphocytaire",
    "كل مادة غريبة عن الجسم قادرة على إثارة استجابة مناعية بالارتباط النوعي مع جسم مضاد أو مستقبل لمفاوي",
    "critique", True, "Ag", ["immunogène"], ["مولد الضد"], C4_CH, C4_MC,
    ["Un virus, une bactérie ou une toxine peuvent agir comme antigènes", "L'épitope est la partie reconnue par l'anticorps"],
    tags=["concept", "immunite"])

CMH = add("Complexe majeur d'histocompatibilité", "معقد التوافق النسيجي الرئيسي", "molecule",
    "Glycoprotéines membranaires présentant des peptides antigéniques aux lymphocytes T, permettant la distinction soi/non-soi",
    "بروتينات سكرية غشائية تعرض الببتيدات المستضدية للخلايا اللمفاوية T مما يسمح بالتمييز بين الذات واللاذات",
    "critique", True, "CMH", ["HLA (chez l'homme)"], ["HLA"], C4_CH, C4_MC,
    ["Le CMH I est présent sur toutes les cellules nucléées", "Le CMH II est présent sur les CPA"],
    tags=["molecule", "immunite", "membrane"])

LT8 = add("Lymphocyte T cytotoxique", "الخلية اللمفاوية التائية السامة", "cellule",
    "Lymphocyte T CD8+ responsable de la destruction des cellules infectées par un virus ou tumorales via la sécrétion de perforine",
    "خلية لمفاوية T تحمل CD8+ مسؤولة عن تدمير الخلايا المصابة بفيروس أو السرطانية عبر إفراز البرفورين",
    "critique", True, "LTc/CTL", ["LT8", "cellule T CD8+", "CTL"], ["لمفاوية تائية سامة"], C4_CH, C4_MC,
    ["Les LTc reconnaissent les peptides viraux présentés par le CMH I", "La perforine forme des pores dans la membrane de la cellule cible"],
    tags=["cellule", "immunite", "lymphocyte"])

CPA = add("Cellule présentatrice d'antigène", "خلية عارضة للمستضد", "cellule",
    "Cellule immunitaire (macrophage, cellule dendritique, LB) qui capture, dégrade et présente les antigènes via le CMH II aux LT CD4+",
    "خلية مناعية (بالعة كبيرة، خلية شجيرية، LB) تلتقط المستضد وتحلله وتعرضه عبر CMH II للخلايا اللمفاوية T CD4+",
    "haute", True, "CPA", ["cellule accessoire", "CPA professionnelle"], ["خلية عارضة"], C4_CH, C4_MC,
    ["Les macrophages présentent les antigènes aux LT auxiliaires", "Les CPA sécrètent l'interleukine 1 pour activer les LT4"],
    tags=["cellule", "immunite", "activation"])

IL2 = add("Interleukine 2", "إنترلوكين 2", "molecule",
    "Cytokine sécrétée par les LT4 activés stimulant la prolifération et la différenciation des lymphocytes T et B",
    "سيتوكين تفرزه الخلايا Th المنشطة يحفز تكاثر وتمايز الخلايا اللمفاوية T و B",
    "haute", False, "IL-2", ["facteur de croissance des lymphocytes T"], ["عامل نمو الخلايا T"], C4_CH, C4_MC,
    ["L'IL-2 active les LTc et LB après reconnaissance de l'antigène", "L'IL-2 est produite par les LT4 activés"],
    tags=["molecule", "cytokine", "immunite"])

LT4 = add("Lymphocyte T auxiliaire", "الخلية اللمفاوية التائية المساعدة", "cellule",
    "Lymphocyte T CD4+ qui orchestre la réponse immunitaire en sécrétant des cytokines activant les LTc, LB et macrophages",
    "خلية لمفاوية T تحمل CD4+ تنظم الاستجابة المناعية بإفراز سيتوكينات تنشط LTc و LB والبالعات",
    "critique", True, "LTh/Th", ["LTh", "cellule T CD4+", "helper"], ["لمفاوية تائية مساعدة"], C4_CH, C4_MC,
    ["Les LT4 reconnaissent les antigènes présentés par le CMH II", "Les LT4 activés sécrètent de l'IL-2"],
    tags=["cellule", "immunite", "lymphocyte"])

LB = add("Lymphocyte B", "الخلية اللمفاوية البائية", "cellule",
    "Lymphocyte responsable de l'immunité humorale, se différenciant en plasmocytes sécréteurs d'anticorps après activation",
    "خلية لمفاوية مسؤولة عن المناعة الخلطية، تتمايز إلى بلازموسيت مفرز للأجسام المضادة بعد التنشيط",
    "critique", True, "LB", [], ["لمفاوية بائية"], C4_CH, C4_MC,
    ["Les LB reconnaissent l'antigène natif directement", "Les LB se différencient en plasmocytes et cellules mémoire"],
    tags=["cellule", "immunite", "humoral"])

PLASM = add("Plasmocyte", "البلازموسيت", "cellule",
    "Cellule effectrice dérivée du lymphocyte B activé, spécialisée dans la sécrétion massive d'anticorps spécifiques",
    "خلية فعالة مشتقة من الخلية اللمفاوية B المنشطة، متخصصة في الإفراز الكثيف للأجسام المضادة النوعية",
    "haute", True, None, [], ["البلازما"], C4_CH, C4_MC,
    ["Les plasmocytes ont une durée de vie de quelques jours", "Chaque plasmocyte sécrète un seul type d'anticorps"],
    tags=["cellule", "immunite", "humoral"])

MEM = add("Cellule mémoire", "الخلية الذاكرة", "cellule",
    "Lymphocyte T ou B à longue durée de vie issu de l'activation immunitaire, permettant une réponse plus rapide et plus intense lors d'une seconde rencontre avec le même antigène",
    "خلية لمفاوية T أو B طويلة العمر ناتجة عن التنشيط المناعي، تسمح باستجابة أسرع وأقوى عند اللقاء الثاني مع نفس المستضد",
    "haute", True, None, [], ["الخلية الذاكرة"], C4_CH, C4_MC,
    ["Les cellules mémoire sont à la base de la vaccination", "La mémoire immunitaire peut durer des années voire toute la vie"],
    tags=["cellule", "immunite", "memoire"])

VACC = add("Vaccination", "التلقيح", "concept",
    "Procédé d'immunisation active consistant à administrer un antigène atténué ou inactivé pour induire une mémoire immunitaire protectrice",
    "إجراء المناعة النشطة يتمثل في إعطاء مستضد موهن أو معطل لإحداث ذاكرة مناعية واقية",
    "critique", True, None, [], ["التطعيم"], C4_CH, C4_MC,
    ["La vaccination induit une réponse primaire puis une mémoire", "Les vaccins peuvent être vivants atténués, inactivés ou sous-unitaires"],
    tags=["concept", "immunite", "prevention"])

COMPI = add("Complexe immun", "المعقد المناعي", "concept",
    "Association spécifique entre un anticorps et son antigène, neutralisant l'antigène et facilitant son élimination par les phagocytes",
    "ارتباط نوعي بين جسم مضاد ومستضده، يعطل المستضد ويسهل التخلص منه بالبلعمة",
    "haute", True, None, [], ["المعقد المناعي"], C4_CH, C4_MC,
    ["Le complexe immun active le complément", "Les complexes immuns sont éliminés par les macrophages"],
    tags=["concept", "immunite", "humoral"])

PERF = add("Perforine", "البرفورين", "molecule",
    "Protéine cytotoxique sécrétée par les LTc formant des pores dans la membrane de la cellule cible, entraînant sa lyse",
    "بروتين سام للخلايا تفرزه LTc يشكل مساماً في غشاء الخلية الهدف مما يؤدي إلى تحللها",
    "haute", True, None, [], ["البرفورين"], C4_CH, C4_MC,
    ["La perforine forme des canaux transmembranaires", "Les granules cytotoxiques contiennent perforine et granzymes"],
    tags=["molecule", "cytotoxique", "immunite"])

CYT = add("Cytokine", "السيتوكين", "molecule",
    "Protéine de signalisation sécrétée par les cellules immunitaires, régulant l'activation, la prolifération et la différenciation des cellules du système immunitaire",
    "بروتين إشارة تفرزه الخلايا المناعية، ينظم تنشيط وتكاثر وتمايز خلايا الجهاز المناعي",
    "haute", True, None, ["interleukine", "interféron"], ["السيتوكين"], C4_CH, C4_MC,
    ["Les cytokines agissent localement (paracrine) ou à distance", "L'IL-2, l'IFN-γ et le TNF-α sont des cytokines importantes"],
    tags=["molecule", "signalisation", "immunite"])

PHAGO = add("Phagocyte", "البالعة", "cellule",
    "Cellule immunitaire capable d'englober et de digérer des particules étrangères, des débris cellulaires ou des micro-organismes par phagocytose",
    "خلية مناعية قادرة على ابتلاع وهضم جسيمات غريبة أو حطام خلوي أو كائنات دقيقة بالبلعمة",
    "haute", True, None, ["macrophage", "granulocyte"], ["البالعة"], C4_CH, C4_MC,
    ["Les macrophages sont des phagocytes professionnels", "La phagocytose est une immunité innée"],
    tags=["cellule", "immunite", "inné"])

MACRO = add("Macrophage", "البالعة الكبيرة", "cellule",
    "Phagocyte dérivé du monocyte, jouant un rôle clé dans l'immunité innée par phagocytose et la présentation antigénique aux LT",
    "بالعة مشتقة من الوحيدة، تلعب دوراً رئيسياً في المناعة الفطرية بالبلعمة وعرض المستضد للخلايا T",
    "haute", True, None, [], ["البالعة الكبيرة"], C4_CH, C4_MC,
    ["Les macrophages sont des CPA", "Les macrophages sécrètent des cytokines pro-inflammatoires"],
    tags=["cellule", "immunite", "phagocytose"])

DEND = add("Cellule dendritique", "الخلية الشجيرية", "cellule",
    "CPA la plus efficace, capturant les antigènes dans les tissus périphériques pour les présenter aux LT naïfs dans les ganglions lymphatiques",
    "أكثر CPA فعالية، تلتقط المستضدات في الأنسجة المحيطية لتقدمها للخلايا T البكر في العقد اللمفاوية",
    "moyenne", False, None, [], ["الخلية الشجيرية"], C4_CH, C4_MC,
    ["Les cellules dendritiques sont des sentinelles du système immunitaire", "Elles activent les LT naïfs"],
    tags=["cellule", "immunite", "presentation"])

# Cat 1.5 — Neurobiologie
C5_MC = "ch_nerveux"
C5_CH = "Communication nerveuse"

PA = add("Potentiel d'action", "كمون العمل", "concept",
    "Dépolarisation rapide et brève de la membrane neuronale due à l'entrée massive de Na+ suivie de la sortie de K+, permettant la propagation du message nerveux",
    "زوال استقطاب سريع وقصير للغشاء العصبي ناتج عن دخول جماعي لـ Na+ يتبعه خروج K+، مما يسمح بانتشار الرسالة العصبية",
    "critique", True, "PA", ["influx nerveux", "spike"], ["السيالة العصبية"], C5_CH, C5_MC,
    ["Le potentiel d'action naît au niveau du cône d'émergence", "La propagation est saltatoire dans les fibres myélinisées"],
    tags=["concept", "nerveux", "membrane"])

NT = add("Neurotransmetteur", "الناقل العصبي", "molecule",
    "Molécule chimique libérée dans la fente synaptique par le neurone présynaptique se fixant sur des récepteurs postsynaptiques pour transmettre le signal",
    "جزيء كيميائي يُحرر في الشق المشبكي من العصبون قبل المشبكي يثبت على مستقبلات بعد مشبكية لنقل الإشارة العصبية",
    "critique", True, "NT", ["neuromédiateur", "messager chimique"], ["المرسل الكيميائي"], C5_CH, C5_MC,
    ["L'acétylcholine est le NT de la jonction neuromusculaire", "Le GABA est un neurotransmetteur inhibiteur"],
    tags=["molecule", "synapse", "nerveux"])

SYN = add("Synapse", "المشبك", "concept",
    "Zone de jonction fonctionnelle entre deux neurones ou entre un neurone et une cellule effectrice, permettant la transmission du message nerveux",
    "منطقة التماس الوظيفي بين عصبونين أو بين عصبون وخلية منفذة تسمح بنقل الرسالة العصبية",
    "critique", True, None, ["jonction synaptique"], ["التشابك العصبي"], C5_CH, C5_MC,
    ["La synapse chimique utilise des neurotransmetteurs", "La fente synaptique mesure environ 20 nm"],
    tags=["concept", "nerveux", "synapse"])

PR = add("Potentiel de repos", "كمون الراحة", "concept",
    "Différence de potentiel de membrane d'environ -70 mV d'un neurone non stimulé, maintenue par les pompes Na+/K+ et les canaux ioniques",
    "فرق كمون الغشاء حوالي -70 ملڤولت لعصبون غير منبه، يثبت بمضخات Na+/K+ والقنوات الأيونية",
    "critique", True, "PR", [], ["كمون الراحة"], C5_CH, C5_MC,
    ["Le potentiel de repos est négatif à l'intérieur", "Les ions K+ sont plus concentrés à l'intérieur, Na+ à l'extérieur"],
    tags=["concept", "membrane", "nerveux"])

PPSE = add("PPSE", "كمون ما بعد المشبكي الاستثاري", "concept",
    "Dépolarisation locale de la membrane postsynaptique due à l'ouverture de canaux Na+ sous l'effet d'un neurotransmetteur excitateur",
    "زوال استقطاب موضعي للغشاء بعد المشبكي ناتج عن فتح قنوات Na+ بتأثير ناقل عصبي استثاري",
    "haute", True, "PPSE", ["potentiel postsynaptique excitateur"], ["EPSP"], C5_CH, C5_MC,
    ["Le PPSE est une dépolarisation graduée", "La sommation des PPSE peut déclencher un PA"],
    tags=["concept", "synapse", "nerveux"])

PPSI = add("PPSI", "كمون ما بعد المشبكي المثبط", "concept",
    "Hyperpolarisation de la membrane postsynaptique due à l'ouverture de canaux Cl- ou K+ sous l'effet d'un NT inhibiteur",
    "فرط استقطاب للغشاء بعد المشبكي ناتج عن فتح قنوات Cl- أو K+ بتأثير ناقل عصبي مثبط",
    "haute", True, "PPSI", ["potentiel postsynaptique inhibiteur"], ["IPSP"], C5_CH, C5_MC,
    ["Le PPSI rend la membrane moins excitable", "Le GABA est un NT inhibiteur produisant des PPSI"],
    tags=["concept", "synapse", "nerveux"])

ACH = add("Acétylcholine", "الأستيل كولين", "molecule",
    "Neurotransmetteur excitateur de la jonction neuromusculaire et du système nerveux parasympathique, libéré par les motoneurones",
    "ناقل عصبي استثاري في الوصلة العصبية العضلية والجهاز العصبي اللاودي، يحرره العصبون الحركي",
    "haute", True, "ACh", [], ["الأستيل كولين"], C5_CH, C5_MC,
    ["L'ACh est dégradée par l'acétylcholinestérase", "L'ACh active les récepteurs nicotiniques et muscariniques"],
    tags=["molecule", "synapse", "nerveux"])

MYEL = add("Gaine de myéline", "غمد الميالين", "structure",
    "Gaine lipidique isolante formée par les cellules de Schwann (SNP) ou oligodendrocytes (SNC) autour des axones, accélérant la propagation saltatoire",
    "غلاف دهني عازل تشكله خلايا شوان (الجهاز العصبي المحيطي) أو الخلايا الدبقية قليلة التغصن (المركزي) حول المحاور، يسرع الانتشار القفزي",
    "haute", True, None, ["myéline"], ["الميالين"], C5_CH, C5_MC,
    ["La myéline permet la conduction saltatoire", "La sclérose en plaques détruit la myéline"],
    tags=["structure", "nerveux", "propagation"])

CAN = add("Canal ionique", "القناة الأيونية", "structure",
    "Protéine membranaire formant un pore permettant le passage sélectif d'ions spécifiques (Na+, K+, Ca2+, Cl-) à travers la membrane",
    "بروتين غشائي يشكل مساماً يسمح بالمرور الانتقائي لأيونات محددة (Na+, K+, Ca2+, Cl-) عبر الغشاء",
    "haute", True, None, ["canal voltage-dépendant"], ["القناة الأيونية"], C5_CH, C5_MC,
    ["Les canaux Na+ voltage-dépendants s'ouvrent lors de la dépolarisation", "Les canaux K+ voltage-dépendants s'ouvrent plus lentement"],
    tags=["structure", "membrane", "ion"])

POMP = add("Pompe Na+/K+", "مضخة Na+/K+", "mecanisme",
    "Protéine membranaire transportant activement 3 Na+ hors de la cellule et 2 K+ dans la cellule en hydrolysant de l'ATP, maintenant le potentiel de repos",
    "بروتين غشائي ينقل بنشاط 3 Na+ خارج الخلية و 2 K+ داخل الخلية بتحليل ATP، محافظاً على كمون الراحة",
    "haute", True, None, ["Na+/K+ ATPase"], ["مضخة الصوديوم/البوتاسيوم"], C5_CH, C5_MC,
    ["La pompe Na+/K+ utilise 1/3 de l'énergie cellulaire", "La pompe maintient le gradient électrochimique"],
    tags=["mecanisme", "transport", "membrane", "energie"])

NM = add("Jonction neuromusculaire", "الوصلة العصبية العضلية", "structure",
    "Synapse spécialisée entre un motoneurone et une fibre musculaire squelettique utilisant l'acétylcholine comme neurotransmetteur",
    "مشبك متخصص بين عصبون حركي وليفة عضلية هيكلية يستخدم الأستيل كولين كناقل عصبي",
    "haute", True, None, ["plaque motrice"], ["الوصلة العصبية العضلية", "اللويحة المحركة"], C5_CH, C5_MC,
    ["La libération d'ACh dans la JNM déclenche la contraction musculaire", "Le curare bloque les récepteurs à l'ACh de la JNM"],
    tags=["structure", "nerveux", "muscle", "synapse"])

SOM = add("Sommation", "الجمع", "concept",
    "Intégration des potentiels postsynaptiques excitateurs et inhibiteurs au niveau du cône d'émergence, déterminant si un potentiel d'action est déclenché",
    "دمج كمونات ما بعد المشبك الاستثارية والمثبطة على مستوى مخروط الانبثاق، يحدد إطلاق كمون العمل",
    "haute", True, None, ["intégration neuronale"], ["الجمع الزماني والمكاني"], C5_CH, C5_MC,
    ["La sommation temporelle : PPSE rapprochés dans le temps", "La sommation spatiale : PPSE de plusieurs synapses"],
    tags=["concept", "nerveux", "integration"])

PERIO = add("Période réfractaire", "فترة المقاومة", "concept",
    "Période suivant un potentiel d'action pendant laquelle la membrane neuronale est inexcitable (absolue) ou moins excitable (relative)",
    "الفترة التي تلي كمون العمل والتي يكون خلالها الغشاء العصبي غير قابل للإثارة (المطلقة) أو أقل إثارة (النسبية)",
    "haute", True, None, [], ["فترة المقاومة"], C5_CH, C5_MC,
    ["La période réfractaire absolue limite la fréquence des PA", "La période réfractaire relative nécessite un stimulus plus fort"],
    tags=["concept", "nerveux", "membrane"])

# ═══════════════════════════════════════════════════════════
# DOMAINE 2 — Transformations énergétiques
# ═══════════════════════════════════════════════════════════
D2 = "domaine-2"
D2_FR = "Transformations énergétiques"
D2_AR = "التحولات الطاقوية"

# Cat 2.1 — Photosynthèse
C21_CH = "Photosynthèse"
C21_MC = "ch_photosynthese"

CHLO = add("Chloroplaste", "الصانعة الخضراء", "organite",
    "Organite cellulaire végétal contenant la chlorophylle, siège de la photosynthèse, constitué de thylakoïdes et d'un stroma",
    "عضية خلوية نباتية تحتوي على اليخضور، مقر التركيب الضوئي، تتكون من تيلاكويدات وحشوة",
    "critique", True, None, ["plaste vert"], ["البلاستيدة الخضراء"], C21_CH, C21_MC,
    ["Le chloroplaste contient des thylakoïdes empilés en granum", "La phase claire se déroule dans la membrane des thylakoïdes"],
    tags=["organite", "photosynthese", "vegetal"])

CALV = add("Cycle de Calvin", "دورة كالفن", "processus",
    "Réactions biochimiques du stroma fixant le CO2 sur le RuBP pour synthétiser des glucides, utilisant l'ATP et le NADPH de la phase claire",
    "تفاعلات كيميائية حيوية في حشوة الصانعة الخضراء تثبت CO2 على RuBP لتخليق سكريات، تستخدم ATP و NADPH من الطور الضوئي",
    "haute", True, None, ["cycle de Calvin-Benson", "phase sombre", "phase chimio-biotique"], ["حلقة كالفن-بنسون"], C21_CH, C21_MC,
    ["Le cycle de Calvin utilise l'ATP et le NADPH", "L'enzyme Rubisco catalyse la fixation du CO2 sur le RuBP"],
    tags=["processus", "photosynthese", "metabolisme"])

ATPS = add("ATP synthase", "ATP سنتاز", "enzyme",
    "Complexe enzymatique membranaire catalysant la synthèse d'ATP à partir d'ADP et Pi grâce à un flux de protons (chimiosmose)",
    "معقد إنزيمي غشائي يحفز تركيب ATP انطلاقاً من ADP و Pi بفضل تدفق البروتونات (التناضح الكيميائي)",
    "haute", True, None, ["ATPase", "complexe ATP-synthétique", "tête globulaire"], ["الكرات المذنبة"], C21_CH, C21_MC,
    ["L'ATP synthase utilise l'énergie du gradient de protons", "L'ATP synthase fonctionne comme une turbine moléculaire"],
    tags=["enzyme", "energie", "membrane"])

CHLOR = add("Chlorophylle", "اليخضور", "molecule",
    "Pigment photosynthétique vert présent dans les thylakoïdes, absorbant l'énergie lumineuse pour la photosynthèse",
    "صبغة خضراء ممتصة للضوء موجودة في التيلاكويدات، تمتص الطاقة الضوئية للتركيب الضوئي",
    "critique", True, None, ["pigment vert"], ["الكلوروفيل"], C21_CH, C21_MC,
    ["La chlorophylle absorbe la lumière bleue et rouge", "La chlorophylle reflète la lumière verte"],
    tags=["molecule", "pigment", "photosynthese"])

PHOCL = add("Phase claire", "الطور الضوئي", "processus",
    "Première phase de la photosynthèse se déroulant dans les thylakoïdes où l'énergie lumineuse est convertie en ATP et NADPH avec libération d'O2",
    "الطور الأول للتركيب الضوئي يحدث في التيلاكويدات حيث تحول الطاقة الضوئية إلى ATP و NADPH مع تحرير O2",
    "haute", True, None, ["phase lumineuse", "photochimique"], ["الطور الضوئي"], C21_CH, C21_MC,
    ["La phase claire produit O2, ATP et NADPH", "La photolyse de l'eau libère les électrons pour la chaîne photosynthétique"],
    tags=["processus", "photosynthese", "energie"])

PHOSC = add("Photophosphorylation", "الفسفرة الضوئية", "processus",
    "Synthèse d'ATP couplée au transport d'électrons dans la membrane des thylakoïdes lors de la phase claire",
    "تركيب ATP المرتبط بنقل الإلكترونات في غشاء التيلاكويدات أثناء الطور الضوئي",
    "haute", True, None, [], ["الفسفرة الضوئية"], C21_CH, C21_MC,
    ["La photophosphorylation est cyclique ou non cyclique", "Elle produit l'ATP nécessaire au cycle de Calvin"],
    tags=["processus", "photosynthese", "energie", "membrane"])

RUBIS = add("Rubisco", "روبيسكو", "enzyme",
    "Enzyme clé du cycle de Calvin catalysant la fixation du CO2 sur le ribulose bisphosphate (RuBP), première étape de la carboxylation",
    "إنزيم رئيسي في دورة كالفن يحفز تثبيت CO2 على الريبولوز ثنائي الفوسفات (RuBP)، الخطوة الأولى للكربوكسلة",
    "haute", True, None, ["RuBisCO", "ribulose bisphosphate carboxylase/oxygénase"], ["روبيسكو"], C21_CH, C21_MC,
    ["La Rubisco est l'enzyme la plus abondante sur Terre", "La Rubisco peut aussi catalyser la photorespiration"],
    tags=["enzyme", "photosynthese", "carbone"])

THYL = add("Thylakoïde", "التيلاكويد", "organite",
    "Sac membranaire aplati dans le chloroplaste contenant les pigments photosynthétiques et les chaînes de transport d'électrons",
    "كيس غشائي مسطح في الصانعة الخضراء يحتوي على الأصبغة الضوئية وسلاسل نقل الإلكترونات",
    "haute", True, None, [], ["التيلاكويد"], C21_CH, C21_MC,
    ["Les thylakoïdes sont empilés en granums", "La membrane du thylakoïde est le site de la phase claire"],
    tags=["organite", "photosynthese", "membrane"])

STRO = add("Stroma", "الحشوة", "concept",
    "Substance aqueuse du chloroplaste entourant les thylakoïdes, contenant les enzymes du cycle de Calvin",
    "مادة مائية في الصانعة الخضراء حول التيلاكويدات، تحتوي على إنزيمات دورة كالفن",
    "haute", True, None, [], ["الحشوة"], C21_CH, C21_MC,
    ["Le stroma est le site du cycle de Calvin", "Le stroma contient l'ADN chloroplastique et les ribosomes"],
    tags=["concept", "photosynthese", "chloroplaste"])

NADP = add("NADPH", "NADPH", "molecule",
    "Nicotinamide adénine dinucléotide phosphate réduit, transporteur d'électrons produit lors de la phase claire et utilisé dans le cycle de Calvin",
    "فوسفات نيكوتيناميد أدينين ثنائي النوكليوتيد المرجع، ناقل إلكترونات ينتج في الطور الضوئي ويستخدم في دورة كالفن",
    "moyenne", True, None, [], ["NADPH"], C21_CH, C21_MC,
    ["Le NADPH est un pouvoir réducteur", "Le NADPH est oxydé en NADP+ dans le cycle de Calvin"],
    tags=["molecule", "coenzyme", "photosynthese"])

PHOTR = add("Photorespiration", "التنفس الضوئي", "processus",
    "Processus où la Rubisco fixe O2 au lieu de CO2, consommant de l'ATP et libérant du CO2, réduisant l'efficacité photosynthétique",
    "عملية حيث يثبت روبيسكو O2 بدلاً من CO2، مستهلكاً ATP ومحرراً CO2، مما يقلل كفاءة التركيب الضوئي",
    "moyenne", False, None, [], ["التنفس الضوئي"], C21_CH, C21_MC,
    ["La photorespiration augmente à haute température", "Les plantes C4 évitent la photorespiration"],
    tags=["processus", "photosynthese", "metabolisme"])

# Cat 2.2 — Respiration cellulaire
C22_CH = "Respiration cellulaire"
C22_MC = "ch_respiration"

MITO = add("Mitochondrie", "الميتوكوندري", "organite",
    "Organite à double membrane, siège de la respiration cellulaire où se déroulent le cycle de Krebs et la phosphorylation oxydative",
    "عضية ذات غشاء مزدوج، مقر التنفس الخلوي حيث تحدث دورة كريبس والفسفرة التأكسدية",
    "critique", True, None, ["chondriosome", "centrale énergétique"], ["متقدرة", "ميتوكوندريون"], C22_CH, C22_MC,
    ["La mitochondrie possède une membrane interne repliée en crêtes", "La matrice contient les enzymes du cycle de Krebs"],
    tags=["organite", "respiration", "energie"])

KREBS = add("Cycle de Krebs", "دورة كريبس", "processus",
    "Série de réactions enzymatiques dans la matrice mitochondriale oxydant l'acétyl-CoA en CO2, produisant NADH, FADH2 et GTP",
    "سلسلة من التفاعلات الإنزيمية في المادة الأساسية للميتوكوندري تؤكسد أسيتيل CoA إلى CO2، منتجة NADH و FADH2 و GTP",
    "haute", True, None, ["cycle de l'acide citrique", "cycle tricarboxylique"], ["حلقة حمض الليمون"], C22_CH, C22_MC,
    ["Le cycle de Krebs produit 2 CO2, 3 NADH, 1 FADH2 et 1 GTP par tour", "C'est une étape clé du métabolisme aérobie"],
    tags=["processus", "respiration", "metabolisme"])

POX = add("Phosphorylation oxydative", "الفسفرة التأكسدية", "processus",
    "Synthèse d'ATP couplée à la chaîne respiratoire où l'oxydation du NADH et FADH2 génère un gradient de protons pour l'ATP synthase",
    "تركيب ATP المقترن بالسلسلة التنفسية حيث تؤكسدة NADH و FADH2 تولد تدرجاً بروتونياً يستخدمه ATP سنتاز",
    "haute", True, None, ["chaîne respiratoire", "oxydation phosphorylante"], ["السلسلة التنفسية"], C22_CH, C22_MC,
    ["La phosphorylation oxydative produit 36 ATP/glucose", "L'oxygène est l'accepteur final d'électrons"],
    tags=["processus", "respiration", "energie", "membrane"])

CRE = add("Chaîne respiratoire", "السلسلة التنفسية", "processus",
    "Série de complexes protéiques membranaires (I, II, III, IV) dans la membrane interne mitochondriale transférant des électrons du NADH/FADH2 à O2",
    "سلسلة من معقدات بروتينية غشائية (I, II, III, IV) في الغشاء الداخلي للميتوكوندري تنقل الإلكترونات من NADH/FADH2 إلى O2",
    "haute", True, None, ["chaîne de transport d'électrons"], ["السلسلة التنفسية"], C22_CH, C22_MC,
    ["Les complexes I, III et IV pompent des protons", "L'O2 est réduit en H2O au niveau du complexe IV"],
    tags=["processus", "respiration", "energie", "membrane"])

PYR = add("Pyruvate", "البيروفات", "molecule",
    "Molécule à 3 carbones produite par la glycolyse, transformée en acétyl-CoA pour entrer dans le cycle de Krebs en conditions aérobies",
    "جزيء ثلاثي الكربون ينتج عن التحلل السكري، يتحول إلى أسيتيل CoA لدخول دورة كريبس في الظروف الهوائية",
    "haute", True, None, ["acide pyruvique"], ["البيروفات"], C22_CH, C22_MC,
    ["Le pyruvate est transporté dans la matrice mitochondriale", "La décarboxylation du pyruvate produit acétyl-CoA et CO2"],
    tags=["molecule", "metabolisme", "respiration"])

ACCOA = add("Acétyl-CoA", "أسيتيل CoA", "molecule",
    "Molécule à 2 carbones liée au coenzyme A, issue de la dégradation du pyruvate, des acides gras ou des acides aminés, entrant dans le cycle de Krebs",
    "جزيء ثنائي الكربون مرتبط بالمرافق A، ناتج عن هدم البيروفات والأحماض الدهنية أو الأمينية، يدخل دورة كريبس",
    "haute", True, None, [], ["أسيتيل CoA"], C22_CH, C22_MC,
    ["L'acétyl-CoA est le carrefour métabolique", "La formation d'acétyl-CoA produit du NADH"],
    tags=["molecule", "metabolisme", "respiration"])

NADH = add("NADH", "NADH", "molecule",
    "Nicotinamide adénine dinucléotide réduit, coenzyme transporteur d'électrons produit lors de la glycolyse, décarboxylation et cycle de Krebs",
    "نيكوتيناميد أدينين ثنائي النوكليوتيد المرجع، مرافق ناقل للإلكترونات ينتج في التحلل السكري ونزع الكربوكسيل ودورة كريبس",
    "moyenne", True, None, [], ["NADH"], C22_CH, C22_MC,
    ["Le NADH donne ses électrons au complexe I de la chaîne respiratoire", "Chaque NADH produit ~2.5 ATP"],
    tags=["molecule", "coenzyme", "respiration", "energie"])

FADH = add("FADH2", "FADH2", "molecule",
    "Flavine adénine dinucléotide réduit, coenzyme transporteur d'électrons produit dans le cycle de Krebs, donnant ses électrons au complexe II",
    "فلافين أدينين ثنائي النوكليوتيد المرجع، مرافق ناقل للإلكترونات ينتج في دورة كريبس، يعطي إلكتروناته للمعقد II",
    "moyenne", True, None, [], ["FADH2"], C22_CH, C22_MC,
    ["Le FADH2 produit ~1.5 ATP", "Le FADH2 est oxydé au niveau du complexe II"],
    tags=["molecule", "coenzyme", "respiration", "energie"])

# Cat 2.3 — Fermentation
C23_CH = "Énergie cellulaire"
C23_MC = "ch_fermentation"

FERMA = add("Fermentation alcoolique", "التخمر الكحولي", "processus",
    "Processus anaérobie de dégradation partielle du glucose par les levures produisant éthanol, CO2 et 2 ATP par glucose",
    "عملية لاهوائية للهدم الجزئي للغلوكوز بواسطة الخمائر تنتج الإيثانول و CO2 و 2 ATP لكل غلوكوز",
    "moyenne", False, None, ["fermentation éthanolique"], ["التخمر الكحولي"], C23_CH, C23_MC,
    ["Utilisée dans la fabrication du pain et du vin", "Le NADH est réoxydé lors de la réduction de l'acétaldéhyde en éthanol"],
    tags=["processus", "fermentation", "anaerobie"])

GLYC = add("Glycolyse", "التحلل السكري", "processus",
    "Voie métabolique cytoplasmique dégradant le glucose en deux pyruvates, produisant 2 ATP et 2 NADH",
    "مسار أيضي هيولي يهدم جزيء غلوكوز إلى جزيئي بيروفات، منتجاً 2 ATP و 2 NADH",
    "haute", True, None, ["voie d'Embden-Meyerhof-Parnas"], ["الغلكزة", "تحلل السكر"], C23_CH, C23_MC,
    ["La glycolyse est la première étape de la respiration et fermentation", "La glycolyse ne consomme pas d'O2"],
    tags=["processus", "metabolisme", "energie"])

FERML = add("Fermentation lactique", "التخمر اللبني", "processus",
    "Processus anaérobie transformant le pyruvate en lactate pour réoxyder le NADH en NAD+, permettant la poursuite de la glycolyse",
    "عملية لاهوائية تحول البيروفات إلى لاكتات لأكسدة NADH إلى NAD+، مما يسمح باستمرار التحلل السكري",
    "moyenne", False, None, [], ["التخمر اللبني"], C23_CH, C23_MC,
    ["La fermentation lactique se produit dans les muscles lors d'effort intense", "Les bactéries lactiques sont utilisées dans la fabrication du yaourt"],
    tags=["processus", "fermentation", "anaerobie"])

ATP = add("ATP", "ATP", "molecule",
    "Adénosine triphosphate, molécule énergétique universelle des êtres vivants, libérant de l'énergie par hydrolyse en ADP + Pi",
    "أدينوزين ثلاثي الفوسفات، جزيء الطاقة العام للكائنات الحية، يحرر الطاقة بالتحلل المائي إلى ADP + Pi",
    "critique", True, "ATP", ["adénosine triphosphate"], ["أدينوزين ثلاثي الفوسفات"], C23_CH, C23_MC,
    ["L'ATP est la monnaie énergétique de la cellule", "L'hydrolyse de l'ATP libère ~30.5 kJ/mol"],
    tags=["molecule", "energie", "metabolisme"])

GLUC = add("Glucose", "الغلوكوز", "molecule",
    "Hexose (C6H12O6), principale source d'énergie cellulaire, dégradé par la glycolyse puis respiration ou fermentation",
    "سكر سداسي (C6H12O6)، المصدر الرئيسي للطاقة الخلوية، يُهدم بالتحلل السكري ثم التنفس أو التخمر",
    "critique", True, None, ["dextrose", "sucre simple"], ["الغلوكوز", "سكر العنب"], C23_CH, C23_MC,
    ["Le glucose est stocké sous forme de glycogène (animal) ou amidon (végétal)", "La dégradation complète du glucose produit 36-38 ATP"],
    tags=["molecule", "glucide", "energie", "metabolisme"])

BILAN = add("Bilan énergétique", "الحصيلة الطاقوية", "concept",
    "Quantité totale d'ATP produite par la dégradation complète d'une molécule de glucose, variant selon la voie métabolique",
    "الكمية الإجمالية لـ ATP المنتجة من الهدم الكامل لجزيء غلوكوز، تختلف حسب المسار الأيضي",
    "haute", True, None, [], ["الحصيلة الطاقوية"], C23_CH, C23_MC,
    ["Respiration : 36-38 ATP par glucose", "Fermentation : 2 ATP par glucose"],
    tags=["concept", "energie", "metabolisme"])

DECARB = add("Décarboxylation", "نزع الكربوكسيل", "processus",
    "Réaction enzymatique libérant du CO2 à partir d'un substrat carboné, étape entre la glycolyse et le cycle de Krebs",
    "تفاعل إنزيمي يحرر CO2 من ركيزة كربونية، مرحلة بين التحلل السكري ودورة كريبس",
    "moyenne", False, None, [], ["نزع الكربوكسيل"], C23_CH, C23_MC,
    ["La décarboxylation du pyruvate est irréversible", "Elle produit acétyl-CoA et NADH"],
    tags=["processus", "metabolisme", "respiration"])

# ═══════════════════════════════════════════════════════════
# DOMAINE 3 — Tectonique globale
# ═══════════════════════════════════════════════════════════
D3 = "domaine-3"
D3_FR = "Tectonique globale"
D3_AR = "التكتونية العامة"

# Cat 3.1 — Plaques tectoniques
C31_CH = "Tectonique des plaques"
C31_MC = "ch_tectonique"

LITHO = add("Lithosphère", "الغلاف الصخري", "concept",
    "Enveloppe rigide externe de la Terre composée de la croûte et du manteau supérieur, fragmentée en plaques tectoniques",
    "الغلاف الصلب الخارجي للأرض المكون من القشرة والستار العلوي، مقسم إلى صفائح تكتونية",
    "critique", True, None, ["croûte lithosphérique"], ["الليتوسفير"], C31_CH, C31_MC,
    ["La lithosphère est découpée en une douzaine de plaques", "La lithosphère océanique est plus dense que la continentale"],
    tags=["concept", "tectonique", "geologie"])

DOR = add("Dorsale océanique", "الظهرة المحيطية", "concept",
    "Chaîne de montagnes sous-marine résultant de la divergence de plaques, siège de l'accrétion océanique",
    "سلسلة جبلية تحت مائية ناتجة عن تباعد الصفائح، مقر النمو المحيطي",
    "haute", True, None, ["dorsale médio-océanique", "rift océanique"], ["الظهرة وسط محيطية"], C31_CH, C31_MC,
    ["L'Islande est émergée au niveau de la dorsale médio-atlantique", "Les dorsales sont des zones de sismicité superficielle"],
    tags=["concept", "tectonique", "geologie"])

SUB = add("Subduction", "الغوص", "processus",
    "Processus par lequel une plaque océanique plonge sous une autre dans une zone de convergence, créant une fosse océanique",
    "عملية تغوص بموجبها صفيحة محيطية تحت صفيحة أخرى في منطقة تقارب، مكونة خندقاً محيطياً",
    "critique", True, None, ["zone de subduction"], ["الاندساس", "منطقة الغوص"], C31_CH, C31_MC,
    ["La subduction crée une fosse océanique et un volcanisme explosif", "Elle génère des séismes profonds jusqu'à 700 km"],
    tags=["processus", "tectonique", "geologie"])

RIFT = add("Rift", "الخسف", "concept",
    "Structure géologique d'extension où la lithosphère continentale s'amincit et se fragmente, prélude à l'ouverture océanique",
    "بنية جيولوجية تمددية حيث يترقق الغلاف الصخري القاري ويتفتت، تمهيداً للفتح المحيطي",
    "haute", True, None, ["vallée de rift"], ["الخسف"], C31_CH, C31_MC,
    ["Le rift est-asiatique est un exemple de rift actif", "Le rift évolue en dorsale océanique"],
    tags=["concept", "tectonique", "extension"])

FOS = add("Fosse océanique", "الخندق المحيطي", "concept",
    "Dépression sous-marine profonde et étroite formée à la frontière de plaques convergentes, marquant la zone de subduction",
    "منخفض بحري عميق وضيق يتشكل على حدود الصفائح المتقاربة، مميزاً منطقة الغوص",
    "haute", True, None, [], ["الخندق المحيطي"], C31_CH, C31_MC,
    ["La fosse des Mariannes est la plus profonde (~11 km)", "Les fosses sont associées aux arcs volcaniques"],
    tags=["concept", "tectonique", "convergence"])

PAL = add("Paléomagnétisme", "علم المغناطيسية القديمة", "concept",
    "Étude de l'aimantation fossile des roches permettant de reconstituer les déplacements des plaques tectoniques",
    "دراسة التمغنط الأحفوري للصخور مما يسمح بإعادة بناء حركات الصفائح التكتونية",
    "haute", True, None, [], ["المغناطيسية القديمة"], C31_CH, C31_MC,
    ["Les anomalies magnétiques symétriques des dorsales prouvent l'expansion océanique", "L'inversion du champ magnétique est enregistrée dans les roches"],
    tags=["concept", "tectonique", "magnetisme"])

ACCR = add("Accrétion", "النمو المحيطي", "processus",
    "Processus de formation de nouvelle croûte océanique au niveau des dorsales par remontée de magma mantellique",
    "عملية تشكل قشرة محيطية جديدة على مستوى الأظهرة بصعود الماغما الستارية",
    "haute", True, None, ["expansion océanique"], ["النمو المحيطي", "الانتشار المحيطي"], C31_CH, C31_MC,
    ["L'accrétion produit 2-10 cm de croûte par an", "L'âge de la croûte océanique augmente avec la distance à la dorsale"],
    tags=["processus", "tectonique", "divergence"])

CONV = add("Convergence", "التقارب", "concept",
    "Mouvement de rapprochement de deux plaques tectoniques, pouvant aboutir à une subduction ou une collision continentale",
    "حركة تقارب صفيحتين تكتونيتين، يمكن أن تؤدي إلى غوص أو تصادم قاري",
    "haute", True, None, [], ["التقارب"], C31_CH, C31_MC,
    ["La convergence océan-continent produit subduction et volcanisme", "La convergence continent-continent produit des chaînes de montagnes"],
    tags=["concept", "tectonique", "convergence"])

COL = add("Collision", "التصادم", "processus",
    "Rencontre de deux lithosphères continentales après subduction de la lithosphère océanique, formant une chaîne de montagnes",
    "لقاء غلافين صخريين قاريين بعد غوص الغلاف الصخري المحيطي، مشكلاً سلسلة جبلية",
    "haute", True, None, ["collision continentale"], ["التصادم القاري"], C31_CH, C31_MC,
    ["La collision himalayenne résulte de la convergence Inde-Eurasie", "La collision produit un épaississement crustal"],
    tags=["processus", "tectonique", "convergence"])

CBORD = add("Frontière de plaque", "حدود الصفائح", "concept",
    "Zone de contact entre deux plaques tectoniques, classée en divergente, convergence ou transformante",
    "منطقة التماس بين صفيحتين تكتونيتين، تصنف إلى متباعدة أو متقاربة أو متحولة",
    "haute", True, None, ["limite de plaque"], ["حدود الصفائح التكتونية"], C31_CH, C31_MC,
    ["Les frontières divergentes créent la lithosphère", "Les frontières convergentes la détruisent"],
    tags=["concept", "tectonique", "limite"])

# Cat 3.2 — Structure interne de la Terre
C32_CH = "Structure du globe"
C32_MC = "ch_globe"

NOYAU = add("Noyau terrestre", "النواة الأرضية", "concept",
    "Partie centrale de la Terre constituée principalement de fer et de nickel, divisée en noyau interne solide et externe liquide",
    "الجزء المركزي للأرض المكون أساساً من الحديد والنيكل، مقسم إلى نواة داخلية صلبة وخارجية سائلة",
    "moyenne", False, None, ["centre de la Terre", "endogée"], ["لب الأرض"], C32_CH, C32_MC,
    ["Le noyau externe liquide génère le champ magnétique", "Le noyau interne solide a un rayon de ~1220 km"],
    tags=["concept", "geologie", "structure"])

DISMO = add("Discontinuité de Mohorovičić", "انقطاع موهو", "concept",
    "Surface de séparation entre la croûte et le manteau où la vitesse des ondes sismiques augmente brusquement, située à 5-70 km de profondeur",
    "سطح فاصل بين القشرة والستار حيث تزداد سرعة الموجات الزلزالية فجأة، يوجد على عمق 5-70 كم",
    "moyenne", True, "Moho", ["Moho"], ["انقطاع موهو"], C32_CH, C32_MC,
    ["Le Moho est plus profond sous les continents (~35 km) que sous les océans (~7 km)", "Il a été découvert par Andrija Mohorovičić en 1909"],
    tags=["concept", "geologie", "sismologie"])

DISC = add("Discontinuité sismique", "الانقطاع الزلزالي", "concept",
    "Surface de séparation entre deux couches terrestres où la vitesse des ondes sismiques change brusquement",
    "سطح فاصل بين طبقتين أرضيتين حيث تتغير سرعة الموجات الزلزالية فجأة",
    "moyenne", False, None, ["frontière sismique"], ["عدم الاستمرارية الزلزالية"], C32_CH, C32_MC,
    ["La discontinuité de Gutenberg sépare manteau et noyau", "La discontinuité de Lehmann sépare noyau externe et interne"],
    tags=["concept", "geologie", "sismologie"])

MANT = add("Manteau terrestre", "الستار الأرضي", "concept",
    "Couche terrestre entre la croûte et le noyau, représentant 84% du volume terrestre, constituée de péridotite riche en olivine",
    "الطبقة الأرضية بين القشرة والنواة، تمثل 84% من حجم الأرض، مكونة من البيريدوتيت الغني بالأوليفين",
    "haute", True, None, [], ["الستار"], C32_CH, C32_MC,
    ["Le manteau est solide mais ductile", "Les mouvements de convection dans le manteau entraînent les plaques"],
    tags=["concept", "geologie", "structure"])

CROUTE = add("Croûte terrestre", "القشرة الأرضية", "concept",
    "Enveloppe externe solide de la Terre, fine (5-70 km), divisée en croûte continentale (granitique) et océanique (basaltique)",
    "الغلاف الخارجي الصلب للأرض، رقيق (5-70 كم)، مقسم إلى قشرة قارية (غرانيتية) ومحيطية (بازلتية)",
    "haute", True, None, [], ["القشرة الأرضية"], C32_CH, C32_MC,
    ["La croûte continentale est plus épaisse et moins dense que la croûte océanique", "La croûte océanique est plus jeune (<200 Ma) que la croûte continentale"],
    tags=["concept", "geologie", "structure"])

ASTH = add("Asthénosphère", "الغلاف الموري", "concept",
    "Couche du manteau supérieur située sous la lithosphère (100-700 km), moins rigide et partiellement fondue, permettant les mouvements des plaques",
    "طبقة من الستار العلوي تحت الغلاف الصخري (100-700 كم)، أقل صلابة ومنصهرة جزئياً، تسمح بحركة الصفائح",
    "haute", True, None, ["zone à faible vitesse"], ["الغلاف الموري"], C32_CH, C32_MC,
    ["L'asthénosphère est ductile et partiellement fondue (~1%)", "Les ondes S ralentissent dans l'asthénosphère"],
    tags=["concept", "geologie", "structure"])

ONDES = add("Onde sismique", "الموجة الزلزالية", "concept",
    "Vibration se propageant à travers la Terre suite à un séisme, classée en ondes P (longitudinales) et S (transversales)",
    "اهتزاز ينتشر عبر الأرض إثر زلزال، تصنف إلى موجات P (طولية) و S (مستعرضة)",
    "haute", True, None, [], ["الموجة الزلزالية"], C32_CH, C32_MC,
    ["Les ondes P traversent solides et liquides", "Les ondes S ne traversent pas les liquides"],
    tags=["concept", "geologie", "sismologie"])

# Cat 3.3 — Magmatisme
C33_CH = "Magmatisme"
C33_MC = "ch_magmatisme"

MAGMA = add("Magma", "الماغما", "concept",
    "Roche en fusion d'origine mantellique ou crustale contenant liquide, cristaux et gaz dissous, dont le refroidissement donne des roches magmatiques",
    "صخر منصهر من أصل ستاري أو قشري يحتوي على سائل وبلورات وغازات مذابة، يبرد ليعطي صخوراً مغماتية",
    "haute", True, None, ["roche fondue", "lave (en surface)"], ["الصهارة"], C33_CH, C33_MC,
    ["Le magma basaltique provient de la fusion partielle de la péridotite du manteau", "La chambre magmatique alimente les volcans"],
    tags=["concept", "magmatisme", "roche"])

RMET = add("Roche métamorphique", "صخر متحول", "concept",
    "Roche issue de la transformation à l'état solide d'une roche préexistante sous l'effet de changements de pression et/ou température",
    "صخر ناتج عن تحول صخر سابق في الحالة الصلبة تحت تأثير تغيرات في الضغط و/أو الحرارة",
    "moyenne", False, None, ["roche métamorphique régionale"], ["الصخور المتحولة"], C33_CH, C33_MC,
    ["Le basalte se transforme en schiste vert puis amphibolite", "Le gabbro en subduction devient schiste bleu puis éclogite"],
    tags=["concept", "geologie", "roche"])

ROCMA = add("Roche magmatique", "صخر ناري", "concept",
    "Roche issue du refroidissement et de la solidification d'un magma, classée en plutonique (refroidissement lent) ou volcanique (rapide)",
    "صخر ناتج عن تبريد وتصلب الماغما، يصنف إلى بلوتوني (تبريد بطيء) أو بركاني (سريع)",
    "haute", True, None, ["roche ignée"], ["الصخر الناري"], C33_CH, C33_MC,
    ["Le granite est une roche plutonique", "Le basalte est une roche volcanique"],
    tags=["concept", "magmatisme", "roche"])

VOLC = add("Volcanisme", "النشاط البركاني", "concept",
    "Ensemble des phénomènes liés à la remontée de magma en surface, incluant éruptions effusives et explosives",
    "مجموعة الظواهر المرتبطة بصعود الماغما إلى السطح، شامل ثورانات إنبجاسية وانفجارية",
    "haute", True, None, [], ["البركانية"], C33_CH, C33_MC,
    ["Le volcanisme effusif produit des coulées de lave fluide", "Le volcanisme explosif produit des nuées ardentes et cendres"],
    tags=["concept", "magmatisme", "volcan"])

METAM = add("Métamorphisme", "التحول", "processus",
    "Transformation à l'état solide d'une roche sous l'effet de changements de température, pression et/ou fluides, modifiant sa minéralogie et sa texture",
    "تحول صخر في الحالة الصلبة تحت تأثير تغيرات الحرارة والضغط و/أو الموائع، يغير تركيبه المعدني وملمسه",
    "haute", True, None, [], ["التحول"], C33_CH, C33_MC,
    ["Le métamorphisme de contact est dû à la chaleur d'un magma", "Le métamorphisme régional est lié à la subduction/collision"],
    tags=["processus", "magmatisme", "roche", "geologie"])

FUSION = add("Fusion partielle", "الانصهار الجزئي", "processus",
    "Fusion incomplète d'une roche mantellique (péridotite) produisant un magma basaltique par départ des éléments les plus fusibles",
    "انصهار غير كامل لصخر ستاري (بيريدوتيت) ينتج ماغما بازلتية بخروج العناصر الأكثر انصهاراً",
    "haute", True, None, [], ["الانصهار الجزئي"], C33_CH, C33_MC,
    ["La fusion partielle de la péridotite donne un magma basaltique", "Les conditions de fusion sont réunies au niveau des dorsales et zones de subduction"],
    tags=["processus", "magmatisme", "geologie"])

GRAN = add("Granite", "الغرانيت", "concept",
    "Roche magmatique plutonique acide composée de quartz, feldspath et mica, formée par refroidissement lent en profondeur",
    "صخر ناري بلوتوني حمضي مكون من الكوارتز والفلسبار والميكا، يتشكل بالتبريد البطيء في العمق",
    "moyenne", True, None, [], ["الغرانيت", "الجرانيت"], C33_CH, C33_MC,
    ["Le granite est la roche caractéristique de la croûte continentale", "Sa faible densité empêche la subduction"],
    tags=["concept", "magmatisme", "roche"])

BASAL = add("Basalte", "البازلت", "concept",
    "Roche magmatique volcanique basique sombre, riche en fer et magnésium, constituant principal de la croûte océanique",
    "صخر ناري بركاني قاعدي غامق، غني بالحديد والمغنيزيوم، المكون الرئيسي للقشرة المحيطية",
    "moyenne", True, None, [], ["البازلت"], C33_CH, C33_MC,
    ["Le basalte provient du refroidissement rapide du magma basaltique", "Le basalte forme les planchers océaniques"],
    tags=["concept", "magmatisme", "roche"])

# ═══════════════════════════════════════════════════════════
# LIENS TRANSVERSAUX
# ═══════════════════════════════════════════════════════════

link(ENZ, SACT, "structure-fonction", "dependance")
link(AC, AG, "reconnaissance-spécifique", "causal")
link(CMH, LT8, "présentation-antigénique", "causal")
link(PA, NT, "propagation-synaptique", "causal")
link(ATPS, POX, "synthèse-ATP-commune", "dependance")
link(KREBS, POX, "fourniture-substrats", "dependance")
link(SUB, MAGMA, "fusion-crustale", "causal")
link(SUB, RMET, "métamorphisme-subduction", "causal")
link(GLYC, KREBS, "glycolyse-alimente-Krebs", "dependance")
link(GLYC, FERMA, "glycolyse-alimente-fermentation", "dependance")
link(PYR, ACCOA, "décarboxylation-pyruvate", "dependance")
link(GLYC, FERML, "glycolyse-alimente-lactique", "dependance")
link(ATPS, CHLO, "ATP-synthase-chloroplaste", "inclusion")
link(ATPS, MITO, "ATP-synthase-mitochondrie", "inclusion")
link(TRANSC, TRAD, "dogme-central", "dependance")
link(COD, CGEN, "codon-code-génétique", "inclusion")
link(ARNP, PROM, "fixation-polymérase", "dependance")
link(SACT, SUB, "fixation-substrat", "causal")
link(PPSE, PPSI, "PPSE-PPSI", "opposition")
link(RIFT, DOR, "rift-évolution-dorsale", "causal")
link(LITHO, ASTH, "lithosphère-asthénosphère", "opposition")
link(CROUTE, LITHO, "croûte-composant-lithosphère", "inclusion")
link(MANT, CONV, "convection-mantellique", "causal")
link(FOS, SUB, "fosse-marque-subduction", "causal")
link(COL, METAM, "collision-métamorphisme", "causal")
link(FUSION, MAGMA, "fusion-partielle-produit-magma", "causal")
link(MAGMA, ROCMA, "magma-refroidissement-roche", "causal")
link(ACCOA, KREBS, "acétyl-CoA-alimente-Krebs", "dependance")
link(ADN, TRANSC, "ADN-matrice-transcription", "causal")
link(ARNm, TRAD, "ARNm-matrice-traduction", "causal")
link(INT, EPIS, "intron-épissage", "dependance")
link(MUT, CGEN, "mutation-modifie-code", "causal")

# ── Domain mapping ──
DOMAINE_CATS = [
    (D1, D1_FR, D1_AR, [
        ("cat-1-1", "Génétique moléculaire", "الوراثة الجزيئية", [
            t for t in terms if t["chapitre_principal"] == C1_CH
        ]),
        ("cat-1-2", "Structure des protéines", "بنية البروتينات", [
            t for t in terms if t["chapitre_principal"] == C2_CH
        ]),
        ("cat-1-3", "Enzymologie", "علم الإنزيمات", [
            t for t in terms if t["chapitre_principal"] == C3_CH
        ]),
        ("cat-1-4", "Immunologie", "علم المناعة", [
            t for t in terms if t["chapitre_principal"] == C4_CH
        ]),
        ("cat-1-5", "Neurobiologie", "علم الأعصاب", [
            t for t in terms if t["chapitre_principal"] == C5_CH
        ]),
    ]),
    (D2, D2_FR, D2_AR, [
        ("cat-2-1", "Photosynthèse", "التركيب الضوئي", [
            t for t in terms if t["chapitre_principal"] == C21_CH
        ]),
        ("cat-2-2", "Respiration cellulaire", "التنفس الخلوي", [
            t for t in terms if t["chapitre_principal"] == C22_CH
        ]),
        ("cat-2-3", "Fermentation", "التخمر", [
            t for t in terms if t["chapitre_principal"] == C23_CH
        ]),
    ]),
    (D3, D3_FR, D3_AR, [
        ("cat-3-1", "Plaques tectoniques", "الصفائح التكتونية", [
            t for t in terms if t["chapitre_principal"] == C31_CH
        ]),
        ("cat-3-2", "Structure interne de la Terre", "البنية الداخلية للأرض", [
            t for t in terms if t["chapitre_principal"] == C32_CH
        ]),
        ("cat-3-3", "Magmatisme", "المغماتية", [
            t for t in terms if t["chapitre_principal"] == C33_CH
        ]),
    ]),
]

# ── Build final JSON ──
domain_json = []
for did, dfr, dar, cats in DOMAINE_CATS:
    domain_json.append(dict(
        id=did, nom_fr=dfr, nom_ar=dar,
        categories=[
            dict(id=cid, nom_fr=cnfr, nom_ar=cnar, termes=cterms)
            for cid, cnfr, cnar, cterms in cats
        ]
    ))

lexique = dict(
    metadata=dict(
        matiere="SVT", niveau="Terminale",
        filiere="Sciences Expérimentales",
        source="Programme officiel ONEC Algérie + Lexique de référence",
        version="1.0",
        date_creation="2026-06-15",
        langue_source="français",
        langues_cibles=["arabe"],
        total_entrees=len(terms)
    ),
    domaines=domain_json,
    liens_transversaux=links,
)

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(lexique, f, ensure_ascii=False, indent=2)

print(f"[OK] Generated {OUTPUT}")
print(f"  Total terms: {len(terms)}")
print(f"  Cross-links: {len(links)}")
for d in lexique["domaines"]:
    c_total = sum(len(c["termes"]) for c in d["categories"])
    print(f"  {d['nom_fr']}: {c_total} terms ({len(d['categories'])} categories)")
