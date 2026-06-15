"""Add ~200 more terms to the existing lexique JSON."""
import json, os, random

PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                    "data", "lexique_svt_terminale_complet.json")

with open(PATH, "r", encoding="utf-8") as f:
    lexique = json.load(f)

# Build flat index of existing term IDs and chapter->category mapping
existing_ids = set()
chapter_cat = {}  # chapitre -> category index in domain
for di, dom in enumerate(lexique["domaines"]):
    for ci, cat in enumerate(dom["categories"]):
        ch = None
        for t in cat["termes"]:
            existing_ids.add(t["id"])
            if ch is None:
                ch = t["chapitre_principal"]
        if ch:
            chapter_cat[ch] = (di, ci)

# Term counter - find next ID
max_n = 0
for tid in existing_ids:
    n = int(tid.split("-")[1])
    max_n = max(max_n, n)

N = [max_n]
def nid():
    N[0] += 1
    return f"term-{N[0]:03d}"

def get_cat(ch):
    if ch in chapter_cat:
        di, ci = chapter_cat[ch]
        return lexique["domaines"][di]["categories"][ci]
    # fallback: find by chapter_principal anywhere
    for dom in lexique["domaines"]:
        for cat in dom["categories"]:
            for t in cat["termes"]:
                if t["chapitre_principal"] == ch:
                    chapter_cat[ch] = (lexique["domaines"].index(dom),
                                       dom["categories"].index(cat))
                    return cat
    return None

def add(terme_fr, terme_ar, type, definition_fr, definition_ar,
        importance="moyenne", bac_frequent=False, abreviation=None,
        synonymes_fr=None, synonymes_ar=None,
        chapitre_principal="", micro_concept_id="",
        exemples_contexte=None, termes_lies=None, tags=None):
    tid = nid()
    term = dict(
        id=tid,
        terme_fr=terme_fr, terme_ar=terme_ar, abreviation=abreviation,
        type=type, definition_fr=definition_fr, definition_ar=definition_ar,
        synonymes_fr=synonymes_fr or [], synonymes_ar=synonymes_ar or [],
        importance=importance, bac_frequent=bac_frequent,
        chapitre_principal=chapitre_principal,
        micro_concept_id=micro_concept_id,
        exemples_contexte=exemples_contexte or [],
        termes_lies=termes_lies or [], tags=tags or [],
    )
    cat = get_cat(chapitre_principal)
    if cat:
        cat["termes"].append(term)
    return tid

# ═══════════════════════════════════════════════════════════
# Additional terms for Domain 1 — Génétique moléculaire
# ═══════════════════════════════════════════════════════════
CH1 = "Synthèse des protéines"
MC1 = "ch1_proteines"

add("Réplication","التضاعف","processus",
    "Processus de duplication de la molécule d'ADN avant la division cellulaire, produisant deux molécules identiques",
    "عملية مضاعفة جزيء ADN قبل الانقسام الخلوي، منتجة جزيئين متطابقين",
    "haute",True,None,[],[],CH1,MC1,
    ["La réplication est semi-conservative","L'ADN polymérase synthétise le nouveau brin"],
    tags=["processus","genetique","division"])

add("ADN polymérase","ADN بوليميراز","enzyme",
    "Enzyme catalysant la synthèse d'un nouveau brin d'ADN à partir d'un brin matrice lors de la réplication",
    "إنزيم يحفز تركيب سلسلة ADN جديدة انطلاقاً من سلسلة ماتريس أثناء التضاعف",
    "haute",True,None,[],[],CH1,MC1,
    ["L'ADN polymérase ajoute des nucléotides dans le sens 5'→3'","Elle nécessite une amorce ARN pour initier la synthèse"],
    tags=["enzyme","replication","genetique"])

add("Nucléosome","النوكليوزوم","structure",
    "Unité de base de la chromatine constituée d'ADN enroulé autour d'un octamère d'histones",
    "الوحدة الأساسية للكروماتين المكونة من ADN ملتف حول ثماني هيستونات",
    "moyenne",False,None,[],[],CH1,MC1,
    ["Les nucléosomes permettent la compaction de l'ADN","L'acétylation des histones décompacte la chromatine"],
    tags=["structure","genetique","chromatine"])

add("Histone","الهيستون","molecule",
    "Protéine basique autour de laquelle l'ADN s'enroule pour former le nucléosome, jouant un rôle dans la régulation de l'expression génique",
    "بروتين قاعدي يلتف حوله ADN لتشكيل النوكليوزوم، يلعب دوراً في تنظيم التعبير الجيني",
    "moyenne",False,None,[],[],CH1,MC1,
    ["Les histones H2A, H2B, H3 et H4 forment l'octamère","L'histone H1 lie l'ADN linker"],
    tags=["molecule","genetique","chromatine"])

add("Chromatine","الكروماتين","structure",
    "Complexe d'ADN et de protéines histones formant les chromosomes, existant sous forme condensée (hétérochromatine) ou décondensée (euchromatine)",
    "معقد ADN وبروتينات هيستون مشكلاً الصبغيات، موجود بشكل مكثف (كروماتين غير فعال) أو منحل (كروماتين فعال)",
    "moyenne",True,None,[],[],CH1,MC1,
    ["L'euchromatine est transcriptionnellement active","L'hétérochromatine est condensée et inactive"],
    tags=["structure","genetique","chromosome"])

add("ARN de transfert","الحمض النووي الريبي الناقل","molecule",
    "Molécule d'ARN en forme de trèfle transportant un acide aminé spécifique au ribosome lors de la traduction",
    "جزيء ARN على شكل نفل ينقل حمضاً أمينياً محدداً إلى الريبوزوم أثناء الترجمة",
    "haute",True,"ARNt",["ARNt","tRNA"],[],CH1,MC1,
    ["L'ARNt possède un anticodon complémentaire au codon de l'ARNm","Chaque ARNt est chargé par une aminoacyl-ARNt synthétase"],
    tags=["molecule","traduction","ribosome"])

add("Anticodon","الرامزة المضادة","concept",
    "Triplet de nucléotides de l'ARNt complémentaire au codon de l'ARNm, assurant la spécificité de l'appariement codon-anticodon",
    "ثلاثي نوكليوتيدات في ARNt متمم لرامزة ARNm، يضمن نوعية الاقتران رامزة-رامزة مضادة",
    "haute",True,None,[],[],CH1,MC1,
    ["L'appariement codon-anticodon suit la règle de complémentarité","La wobble (oscillation) permet un appariement partiel en 3ème position"],
    tags=["concept","traduction","genetique"])

add("Gène de structure","المورثة البنيوية","concept",
    "Gène codant pour une protéine structurale ou fonctionnelle (enzyme, hormone, anticorps...)",
    "مورثة ترمز لبروتين بنيوي أو وظيفي (إنزيم، هرمون، جسم مضاد...)",
    "moyenne",True,None,[],[],CH1,MC1,
    ["Les gènes de structure sont transcrits en ARNm","Ils s'opposent aux gènes de régulation"],
    tags=["concept","genetique","expression"])

add("Gène régulateur","المورثة المنظمة","concept",
    "Gène codant pour une protéine régulatrice contrôlant l'expression d'autres gènes",
    "مورثة ترمز لبروتين منظم يتحكم في تعبير مورثات أخرى",
    "moyenne",True,None,[],[],CH1,MC1,
    ["Les gènes régulateurs codent des facteurs de transcription","Le gène lacI code le répresseur de l'opéron lactose"],
    tags=["concept","regulation","genetique"])

add("Opéron","الأوبرون","concept",
    "Unité fonctionnelle d'ADN bactérien comprenant un promoteur, un opérateur et plusieurs gènes de structure contrôlés ensemble",
    "وحدة وظيفية من ADN بكتيري تشمل محفزاً ومشغلاً وعدة مورثات بنيوية مضبوطة معاً",
    "moyenne",True,None,[],[],CH1,MC1,
    ["L'opéron lactose est induit par le lactose","L'opéron tryptophane est réprimé par le tryptophane"],
    tags=["concept","regulation","procaryote"])

add("Facteur de transcription","عامل النسخ","molecule",
    "Protéine se fixant sur des séquences d'ADN pour activer ou inhiber la transcription d'un gène",
    "بروتين يثبت على تسلسلات ADN لتنشيط أو تثبيط استنساخ مورثة",
    "moyenne",True,None,[],[],CH1,MC1,
    ["Les facteurs de transcription sont spécifiques de séquence","Le TFIID se fixe à la boîte TATA"],
    tags=["molecule","regulation","transcription"])

# Cat 1.2 — Structure des protéines
CH2 = "Structure-fonction des protéines"
MC2 = "ch_structure"

add("Protéine","بروتين","molecule",
    "Macromolécule biologique constituée d'une ou plusieurs chaînes polypeptidiques repliées en structure tridimensionnelle fonctionnelle",
    "جزيء ضخم حيوي مكون من سلسلة أو عدة سلاسل بولي ببتيدية مطوية في بنية فراغية وظيفية",
    "critique",True,None,[],[],CH2,MC2,
    ["Les protéines assurent des fonctions variées : catalyse, transport, structure, signalisation","La séquence en AA détermine le repliement et la fonction"],
    tags=["molecule","proteine","biologie"])

add("Acide aminé essentiel","حمض أميني أساسي","concept",
    "Acide aminé que l'organisme ne peut pas synthétiser et doit être apporté par l'alimentation",
    "حمض أميني لا يستطيع الجسم تركيبه ويجب توفره في الغذاء",
    "moyenne",True,None,[],[],CH2,MC2,
    ["Les 8 acides aminés essentiels chez l'homme sont Val, Leu, Ile, Phe, Trp, Met, Lys, Thr","Les acides aminés essentiels varient selon les espèces"],
    tags=["concept","nutrition","proteine"])

add("Liaison hydrogène","الرابطة الهيدروجينية","concept",
    "Interaction électrostatique faible entre un atome d'hydrogène lié à un atome électronégatif (O, N) et un autre atome électronégatif",
    "تفاعل إلكتروستاتيكي ضعيف بين ذرة هيدروجين مرتبطة بذرة كهرسلبية (O, N) وذرة كهرسلبية أخرى",
    "moyenne",True,None,[],[],CH2,MC2,
    ["Les liaisons H stabilisent les structures secondaire et tertiaire","Les liaisons H sont réversibles et sensibles à la température"],
    tags=["concept","liaison","chimie"])

add("Interaction hydrophobe","التفاعل الكاره للماء","concept",
    "Tendance des chaînes latérales non polaires des acides aminés à se regrouper au cœur de la protéine pour éviter l'eau",
    "نزوع السلاسل الجانبية غير القطبية للأحماض الأمينية للتجمع في قلب البروتين لتجنب الماء",
    "moyenne",False,None,[],[],CH2,MC2,
    ["Les interactions hydrophobes sont essentielles au repliement","Elles stabilisent le noyau hydrophobe des protéines globulaires"],
    tags=["concept","liaison","structure"])

add("Protéine globulaire","البروتين الكروي","concept",
    "Protéine soluble de forme sphérique repliée en structure globulaire, souvent enzymatique ou de transport",
    "بروتين ذائب بشكل كروي مطوي في بنية كروية، غالباً إنزيمي أو ناقل",
    "moyenne",True,None,[],[],CH2,MC2,
    ["L'hémoglobine et les enzymes sont des protéines globulaires","Les protéines globulaires sont généralement hydrosolubles"],
    tags=["concept","proteine","structure"])

add("Protéine fibreuse","البروتين الليفي","concept",
    "Protéine allongée insoluble jouant un rôle structural dans les tissus (collagène, kératine, élastine)",
    "بروتين طويل غير ذائب يلعب دوراً بنيوياً في الأنسجة (كولاجين، كيراتين، إيلاستين)",
    "moyenne",True,None,[],[],CH2,MC2,
    ["Le collagène est la protéine la plus abondante chez les mammifères","Les protéines fibreuses sont résistantes à la traction"],
    tags=["concept","proteine","structure"])

add("Hélice alpha","حلزون ألفا","structure",
    "Structure secondaire régulière en hélice droite stabilisée par des liaisons hydrogène entre le CO du résidu n et le NH du résidu n+4",
    "بنية ثانوية منتظمة بشكل حلزون أيمن تثبت بروابط هيدروجينية بين CO للبقية n و NH للبقية n+4",
    "moyenne",True,None,[],[],CH2,MC2,
    ["L'hélice alpha est droite et compacte","La kératine est riche en hélices alpha"],
    tags=["structure","proteine","conformation"])

add("Feuillet bêta","صفحة بيتا","structure",
    "Structure secondaire en feuillet plissé où les chaînes polypeptidiques sont étirées et liées par des liaisons H latérales",
    "بنية ثانوية بشكل صفحة مطوية حيث السلاسل البولي ببتيدية ممدودة ومرتبطة بروابط H جانبية",
    "moyenne",True,None,[],[],CH2,MC2,
    ["Les feuillets bêta peuvent être parallèles ou antiparallèles","La fibroïne de soie est riche en feuillets bêta"],
    tags=["structure","proteine","conformation"])

add("pH isoélectrique","درجة الحموضة متساوية الشحنة","concept",
    "pH auquel la charge nette d'une protéine ou d'un acide aminé est nulle (forme zwitterion)",
    "pH الذي تكون عنده الشحنة الصافية للبروتين أو الحمض الأميني معدومة (شكل متأين مزدوج)",
    "moyenne",False,"pI",["point isoélectrique"],[],CH2,MC2,
    ["Au pI, la solubilité de la protéine est minimale","La mobilité électrophorétique est nulle au pI"],
    tags=["concept","chimie","acideamine"])

add("Peptide","الببتيد","molecule",
    "Courte chaîne d'acides aminés (2-50) reliés par des liaisons peptidiques, classé en dipeptide, tripeptide, oligopeptide ou polypeptide",
    "سلسلة قصيرة من الأحماض الأمينية (2-50) مرتبطة بروابط ببتيدية، يصنف إلى ثنائي وثلاثي وقليل وسلاسل",
    "moyenne",True,None,[],[],CH2,MC2,
    ["Les peptides ont des fonctions hormonales et de signalisation","Le glutathion est un tripeptide antioxydant"],
    tags=["molecule","proteine","structure"])

# Cat 1.3 — Enzymologie
CH3 = "Activité enzymatique"
MC3 = "ch2_enzymes"

add("Site de fixation","موقع الارتباط","concept",
    "Région de l'enzyme où se fixe le substrat, partie intégrante du site actif assurant la spécificité de reconnaissance",
    "منطقة الإنزيم حيث يثبت الركيزة، جزء من الموقع الفعال يضمن نوعية التعرف",
    "haute",True,None,[],[],CH3,MC3,
    ["Le site de fixation est complémentaire à la forme du substrat","La spécificité est due à la forme du site de fixation"],
    tags=["concept","enzyme","catalyse"])

add("Site catalytique","الموقع المحفز","concept",
    "Partie du site actif où se déroule la réaction chimique, contenant les acides aminés catalytiques",
    "جزء من الموقع الفعال حيث يحدث التفاعل الكيميائي، يحتوي على الأحماض الأمينية المحفزة",
    "haute",True,None,[],[],CH3,MC3,
    ["Le site catalytique abaisse l'énergie d'activation","Les acides aminés du site catalytique participent directement à la réaction"],
    tags=["concept","enzyme","catalyse"])

add("Modèle clé-serrure","نموذج المفتاح والقفل","concept",
    "Modèle de spécificité enzymatique où la forme du site actif est rigide et parfaitement complémentaire du substrat",
    "نموذج النوعية الإنزيمية حيث شكل الموقع الفعال جامد ومتمم تماماً للركيزة",
    "moyenne",True,None,["modèle de Fischer"],[],CH3,MC3,
    ["Proposé par Emil Fischer en 1894","Ce modèle ne rend pas compte de la flexibilité enzymatique"],
    tags=["concept","enzyme","specificite"])

add("Ajustement induit","التكيف المستحث","concept",
    "Modèle de flexibilité enzymatique où la fixation du substrat induit un changement de conformation du site actif",
    "نموذج المرونة الإنزيمية حيث تثبيت الركيزة يحرض تغيراً في شكل الموقع الفعال",
    "moyenne",True,None,["modèle de Koshland"],[],CH3,MC3,
    ["Proposé par Koshland en 1958","Le site actif s'adapte à la forme du substrat après fixation"],
    tags=["concept","enzyme","specificite"])

add("Activateur enzymatique","المنشط الإنزيمي","concept",
    "Molécule qui augmente l'activité d'une enzyme en se fixant sur un site régulateur",
    "جزيء يزيد النشاط الإنزيمي بالارتباط بموقع تنظيمي",
    "moyenne",False,None,[],[],CH3,MC3,
    ["Les activateurs allostériques stabilisent la forme active de l'enzyme","Les ions Mg2+ activent de nombreuses enzymes"],
    tags=["concept","regulation","enzyme"])

add("Cinétique enzymatique","الحركية الإنزيمية","concept",
    "Étude de la vitesse des réactions enzymatiques en fonction des concentrations en substrat, enzyme, inhibiteurs et conditions physicochimiques",
    "دراسة سرعة التفاعلات الإنزيمية بدلالة تراكيز الركيزة والإنزيم والمثبطات والظروف الفيزيوكيميائية",
    "moyenne",True,None,[],[],CH3,MC3,
    ["La loi de Michaelis-Menten décrit la cinétique simple","La courbe Vi = f([S]) est une hyperbole"],
    tags=["concept","enzyme","cinetique"])

# Cat 1.4 — Immunologie
CH4 = "Immunologie"
MC4 = "ch3_immunite"

add("Immunité innée","المناعة الفطرية","concept",
    "Première ligne de défense non spécifique comprenant barrières physiques, phagocytes, complément et réaction inflammatoire",
    "خط الدفاع الأول غير النوعي يشمل حواجز فيزيائية وبالعات ومتممة والتفاعل الالتهابي",
    "haute",True,None,["immunité naturelle","immunité non spécifique"],[],CH4,MC4,
    ["L'immunité innée est rapide (minutes-heures)","Elle ne nécessite pas de reconnaissance préalable"],
    tags=["concept","immunite","inné"])

add("Immunité adaptative","المناعة التكيفية","concept",
    "Réponse immunitaire spécifique et mémoire faisant intervenir les lymphocytes T et B, avec reconnaissance d'antigènes spécifiques",
    "استجابة مناعية نوعية وذاكرة تشمل الخلايا اللمفاوية T و B مع تعرف على مستضدات محددة",
    "haute",True,None,["immunité acquise","immunité spécifique"],[],CH4,MC4,
    ["L'immunité adaptative est lente (jours) mais très spécifique","Elle génère une mémoire immunitaire durable"],
    tags=["concept","immunite","adaptatif"])

add("Immunité humorale","المناعة الخلطية","concept",
    "Composante de l'immunité adaptative médiée par les anticorps produits par les plasmocytes (lymphocytes B), agissant dans les liquides biologiques",
    "مكون المناعة التكيفية بوساطة الأجسام المضادة المنتجة من البلازموسيت، تعمل في السوائل البيولوجية",
    "haute",True,None,[],[],CH4,MC4,
    ["L'immunité humorale cible les pathogènes extracellulaires","Les LB se différencient en plasmocytes sécréteurs d'Ac"],
    tags=["concept","immunite","humoral"])

add("Immunité cellulaire","المناعة الخلوية","concept",
    "Composante de l'immunité adaptative médiée par les lymphocytes T cytotoxiques détruisant les cellules infectées ou tumorales",
    "مكون المناعة التكيفية بوساطة الخلايا اللمفاوية T السامة التي تدمر الخلايا المصابة أو السرطانية",
    "haute",True,None,[],[],CH4,MC4,
    ["L'immunité cellulaire cible les pathogènes intracellulaires","Les LTc reconnaissent les peptides présentés par le CMH I"],
    tags=["concept","immunite","cellulaire"])

add("Réaction inflammatoire","التفاعل الالتهابي","processus",
    "Réponse vasculaire et cellulaire à une lésion tissulaire ou infection caractérisée par rougeur, chaleur, gonflement et douleur",
    "استجابة وعائية وخلوية لإصابة نسيجية أو عدوى تتميز بالاحمرار والحرارة والتورم والألم",
    "haute",True,None,[],[],CH4,MC4,
    ["L'inflammation est une réponse de l'immunité innée","Les mastocytes libèrent de l'histamine dilatant les vaisseaux"],
    tags=["processus","immunite","inflammation"])

add("Complément","المتممة","molecule",
    "Système de protéines plasmatiques s'activant en cascade pour opsoniser, lyser les microbes et recruter les phagocytes",
    "نظام من بروتينات البلازما ينشط بالتسلسل ليوسم ويحلل الميكروبات ويجند البالعات",
    "moyenne",True,None,[],[],CH4,MC4,
    ["Le complément peut être activé par 3 voies : classique, alterne, lectine","Le complexe d'attaque membranaire (MAC) lyse les bactéries"],
    tags=["molecule","immunite","humoral"])

add("Opsonisation","التوسيم","processus",
    "Processus de marquage d'un pathogène par des opsonines (Ac, complément) facilitant sa reconnaissance et phagocytose",
    "عملية وسم الممرض بالأوبسونينات (Ac، متممة) لتسهيل التعرف عليه والبلعمة",
    "moyenne",True,None,[],[],CH4,MC4,
    ["Les anticorps IgG sont de puissantes opsonines","L'opsonisation augmente l'efficacité de la phagocytose"],
    tags=["processus","immunite","phagocytose"])

add("Granzyme","الغرانزيم","molecule",
    "Protéase cytotoxique libérée par les LTc et cellules NK, pénétrant dans la cellule cible via les pores de perforine pour induire l'apoptose",
    "بروتياز سام للخلايا تفرزه LTc والخلايا NK، يدخل الخلية الهدف عبر مسام البرفورين ليحث الاستماتة",
    "moyenne",False,None,[],[],CH4,MC4,
    ["Les granzymes activent les caspases de la cellule cible","Les granzymes sont stockés dans les granules cytotoxiques"],
    tags=["molecule","cytotoxique","apoptose"])

add("Sérotonine","السيروتونين","molecule",
    "Molécule de signalisation impliquée dans la régulation de l'humeur, libérée par les plaquettes lors de l'inflammation",
    "جزيء إشارة يشارك في تنظيم المزاج، تفرزه الصفائح الدموية أثناء الالتهاب",
    "moyenne",False,None,[],[],CH4,MC4,
    ["La sérotonine est un neurotransmetteur et une molécule inflammatoire","Les mastocytes libèrent aussi de la sérotonine"],
    tags=["molecule","inflammation","signalisation"])

add("Histamine","الهيستامين","molecule",
    "Molécule libérée par les mastocytes et basophiles lors de la réaction inflammatoire provoquant vasodilatation et augmentation de la perméabilité vasculaire",
    "جزيء تفرزه الخلايا البدينة والقعدات أثناء التفاعل الالتهابي يسبب تمدد الأوعية وزيادة نفاذيتها",
    "haute",True,None,[],[],CH4,MC4,
    ["L'histamine est responsable des symptômes allergiques","Les antihistaminiques bloquent les récepteurs à l'histamine"],
    tags=["molecule","inflammation","allergie"])

add("Lymphocyte","الخلية اللمفاوية","cellule",
    "Type de leucocyte incluant les lymphocytes T, B et NK, jouant un rôle central dans l'immunité adaptative et innée",
    "نوع من الكريات البيض يشمل الخلايا اللمفاوية T و B و NK، تلعب دوراً مركزياً في المناعة التكيفية والفطرية",
    "haute",True,None,[],[],CH4,MC4,
    ["Les lymphocytes représentent 20-40% des leucocytes","Ils sont produits dans la moelle osseuse"],
    tags=["cellule","immunite","leucocyte"])

add("Sérothérapie","المصل العلاجي","concept",
    "Traitement passif par injection d'anticorps spécifiques (sérum) provenant d'un animal immunisé, utilisé en urgence contre les toxines",
    "علاج سلبي بحقن أجسام مضادة نوعية (مصل) من حيوان ممنع، يستخدم في حالات الطوارئ ضد السموم",
    "moyenne",True,None,[],[],CH4,MC4,
    ["La sérothérapie antivenimeuse neutralise les venins","Elle confère une immunité immédiate mais temporaire"],
    tags=["concept","therapie","immunite"])

add("Allergie","الحساسية","concept",
    "Réaction immunitaire excessive et inappropriée contre un antigène normalement inoffensif (allergène)",
    "استجابة مناعية مفرطة وغير ملائمة لمستضد غير ضار عادة (مسبب الحساسية)",
    "moyenne",True,None,[],[],CH4,MC4,
    ["Les IgE sont impliquées dans les allergies","Les mastocytes libèrent de l'histamine lors d'une réaction allergique"],
    tags=["concept","immunite","pathologie"])

add("Auto-immunité","المناعة الذاتية","concept",
    "Réaction du système immunitaire contre les constituants du soi, causant des maladies auto-immunes",
    "تفاعل الجهاز المناعي ضد مكونات الذات، مسبباً أمراضاً مناعية ذاتية",
    "moyenne",True,None,[],[],CH4,MC4,
    ["La sélection négative élimine les lymphocytes auto-réactifs","Le diabète de type 1 est une maladie auto-immune"],
    tags=["concept","immunite","pathologie"])

add("Vaccin","اللقاح","concept",
    "Préparation antigénique administrée pour induire une immunité active protectrice contre un agent pathogène spécifique",
    "مستحضر مستضدي يعطى لإحداث مناعة نشطة واقية ضد عامل ممرض معين",
    "critique",True,None,[],[],CH4,MC4,
    ["Les vaccins contiennent des antigènes atténués, inactivés ou sous-unitaires","La vaccination a permis d'éradiquer la variole"],
    tags=["concept","immunite","prevention"])

# Cat 1.5 — Neurobiologie
CH5 = "Communication nerveuse"
MC5 = "ch_nerveux"

add("Potentiel postsynaptique","كمون ما بعد المشبكي","concept",
    "Variation locale du potentiel de membrane de la cellule postsynaptique suite à la libération de neurotransmetteurs, excitateur (PPSE) ou inhibiteur (PPSI)",
    "تغير موضعي في كمون غشاء الخلية بعد المشبكية إثر تحرير النواقل العصبية، استثاري (PPSE) أو مثبط (PPSI)",
    "haute",True,"PPS",[],[],CH5,MC5,
    ["Les PPS sont gradués et se propagent passivement","La sommation des PPS détermine le déclenchement du PA"],
    tags=["concept","synapse","nerveux"])

add("Potentiel gradué","كمون متدرج","concept",
    "Variation locale du potentiel de membrane dont l'amplitude est proportionnelle à l'intensité du stimulus, pouvant être dépolarisante ou hyperpolarisante",
    "تغير موضعي في كمون الغشاء سعته متناسبة مع شدة المنبه، يمكن أن يكون مزيلاً أو مفرطاً للاستقطاب",
    "haute",True,None,[],[],CH5,MC5,
    ["Les potentiels gradués se propagent par décrément","Ips sont générés au niveau des dendrites et du corps cellulaire"],
    tags=["concept","membrane","nerveux"])

add("Codage en fréquence","الترميز الترددي","concept",
    "Principe de codage de l'intensité du stimulus par la fréquence des potentiels d'action générés par le neurone",
    "مبدأ ترميز شدة المنبه بتردد كمونات العمل المولدة من العصبون",
    "moyenne",True,None,[],[],CH5,MC5,
    ["Plus le stimulus est fort, plus la fréquence des PA est élevée","La période réfractaire limite la fréquence maximale des PA"],
    tags=["concept","nerveux","signal"])

add("Loi du tout ou rien","قانون الكل أو لا شيء","concept",
    "Principe selon lequel un potentiel d'action est soit déclenché avec une amplitude maximale fixe, soit pas déclenché du tout",
    "مبدأ ينص على أن كمون العمل إما ينطلق بسعة قصوى ثابتة أو لا ينطلق أبداً",
    "haute",True,None,[],[],CH5,MC5,
    ["Le seuil de déclenchement doit être atteint","L'amplitude du PA ne dépend pas de l'intensité du stimulus"],
    tags=["concept","nerveux","membrane"])

add("Dépolarisation","زوال الاستقطاب","processus",
    "Diminution du potentiel de membrane vers des valeurs moins négatives due à l'entrée de Na+ dans la cellule",
    "انخفاض كمون الغشاء نحو قيم أقل سلبية بسبب دخول Na+ إلى الخلية",
    "haute",True,None,[],[],CH5,MC5,
    ["La dépolarisation ouvre les canaux Na+ voltage-dépendants","Une dépolarisation atteignant le seuil déclenche un PA"],
    tags=["processus","membrane","ion"])

add("Repolarisation","عودة الاستقطاب","processus",
    "Retour du potentiel de membrane vers le potentiel de repos après un PA, dû à la sortie de K+ et à la fermeture des canaux Na+",
    "عودة كمون الغشاء نحو كمون الراحة بعد PA، بسبب خروج K+ وإغلاق قنوات Na+",
    "haute",True,None,[],[],CH5,MC5,
    ["La repolarisation suit la phase descendante du PA","Les canaux K+ voltage-dépendants s'ouvrent plus lentement que les canaux Na+"],
    tags=["processus","membrane","ion"])

add("Conduction saltatoire","التوصيل القفزي","processus",
    "Propagation rapide du PA d'un nœud de Ranvier au suivant dans les fibres myélinisées, par bonds saltatoires",
    "انتشار سريع لـ PA من عقدة رانفييه إلى التالية في الألياف الميالينية، بقفزات",
    "haute",True,None,[],[],CH5,MC5,
    ["La conduction saltatoire est plus rapide et économique","Les nœuds de Ranvier sont les seules zones dépourvues de myéline"],
    tags=["processus","nerveux","propagation"])

# ═══════════════════════════════════════════════════════════
# Additional terms for Domain 2 — Transformations énergétiques
# ═══════════════════════════════════════════════════════════

# Cat 2.1 — Photosynthèse
CH21 = "Photosynthèse"
MC21 = "ch_photosynthese"

add("Pigment photosynthétique","الصبغة الضوئية","molecule",
    "Molécule absorbant l'énergie lumineuse pour la photosynthèse, incluant chlorophylles et caroténoïdes",
    "جزيء ممتص للطاقة الضوئية من أجل التركيب الضوئي، يشمل اليخضور والكاروتينات",
    "haute",True,None,[],[],CH21,MC21,
    ["Les pigments sont organisés en photosystèmes dans les thylakoïdes","Chaque pigment absorbe des longueurs d'onde spécifiques"],
    tags=["molecule","pigment","photosynthese"])

add("Photosystème","النظام الضوئي","concept",
    "Complexe protéique membranaire contenant des pigments photosynthétiques et un centre réactionnel, réalisant la photoconversion",
    "معقد بروتيني غشائي يحوي أصبغة ضوئية ومركز تفاعل، يقوم بالتحويل الضوئي",
    "haute",True,None,[],[],CH21,MC21,
    ["Le photosystème II (PSII) fonctionne avant le PSI","Le centre réactionnel contient une paire spéciale de chlorophylles"],
    tags=["concept","photosynthese","membrane"])

add("Photolyse de l'eau","التحلل الضوئي للماء","processus",
    "Réaction de fragmentation de la molécule d'eau en protons, électrons et dioxygène sous l'effet de l'énergie lumineuse au niveau du PSII",
    "تفاعل تفكك جزيء الماء إلى بروتونات وإلكترونات وأكسجين تحت تأثير الطاقة الضوئية على مستوى PSII",
    "haute",True,None,[],[],CH21,MC21,
    ["La photolyse de l'eau libère l'O2 atmosphérique","Les électrons de l'eau remplacent ceux perdus par la chlorophylle du PSII"],
    tags=["processus","photosynthese","energie"])

add("Chaîne photosynthétique","السلسلة الضوئية","processus",
    "Série de transporteurs d'électrons dans la membrane du thylakoïde reliant le PSII au PSI, générant un gradient de protons pour la synthèse d'ATP",
    "سلسلة من ناقلات الإلكترونات في غشاء التيلاكويد تربط PSII مع PSI، تولد تدرجاً بروتونياً لتركيب ATP",
    "haute",True,None,[],[],CH21,MC21,
    ["Le transport d'électrons est non cyclique dans le schéma classique","Le plastoquinone transporte les électrons du PSII au complexe cytochrome b6f"],
    tags=["processus","photosynthese","energie","membrane"])

add("NADP réductase","NADP مختزلة","enzyme",
    "Enzyme du côté stromal du thylakoïde catalysant la réduction du NADP+ en NADPH en utilisant les électrons du PSI",
    "إنزيم في جهة الحشوة للتيلاكويد يحفز اختزال NADP+ إلى NADPH باستخدام إلكترونات PSI",
    "moyenne",False,None,[],[],CH21,MC21,
    ["La NADP réductase est la dernière enzyme de la chaîne photosynthétique","Le NADPH est utilisé dans le cycle de Calvin"],
    tags=["enzyme","photosynthese","NADPH"])

add("Photophosphorylation cyclique","الفسفرة الضوئية الحلقية","processus",
    "Voie alternative où les électrons du PSI retournent au complexe cytochrome b6f, produisant uniquement de l'ATP sans NADPH ni O2",
    "مسار بديل حيث تعود إلكترونات PSI إلى معقد السيتوكروم b6f، منتجة ATP فقط دون NADPH أو O2",
    "moyenne",False,None,[],[],CH21,MC21,
    ["La photophosphorylation cyclique compense le déficit en ATP","Elle implique uniquement le PSI"],
    tags=["processus","photosynthese","energie"])

add("Caroténoïde","الكاروتين","molecule",
    "Pigment photosynthétique auxiliaire orange/jaune protégeant la chlorophylle de la photo-oxydation et étendant le spectre d'absorption",
    "صبغة ضوئية مساعدة برتقالية/صفراء تحمي اليخضور من الأكسدة الضوئية وتوسع طيف الامتصاص",
    "moyenne",False,None,[],[],CH21,MC21,
    ["Les caroténoïdes absorbent la lumière bleue-verte","Le bêta-carotène est un caroténoïde important"],
    tags=["molecule","pigment","photosynthese"])

add("Cycle de Calvin phase 1 : Carboxylation","دورة كالفن المرحلة 1 : الكربوكسلة","processus",
    "Première phase du cycle de Calvin où la Rubisco fixe le CO2 sur le ribulose bisphosphate (RuBP) formant un composé instable à 6C",
    "المرحلة الأولى من دورة كالفن حيث يثبت روبيسكو CO2 على RuBP مشكلاً مركباً غير مستقر بـ 6C",
    "haute",True,None,[],[],CH21,MC21,
    ["La carboxylation est la fixation du CO2","Le composé à 6C se scinde immédiatement en deux molécules de 3-phosphoglycérate (3-PGA)"],
    tags=["processus","photosynthese","carbone"])

add("Cycle de Calvin phase 2 : Réduction","دورة كالفن المرحلة 2 : الاختزال","processus",
    "Deuxième phase utilisant l'ATP et le NADPH pour réduire le 3-phosphoglycérate (3-PGA) en glycéraldéhyde-3-phosphate (G3P)",
    "المرحلة الثانية تستخدم ATP و NADPH لاختزال 3-فوسفوغليسيرات (3-PGA) إلى غليسيرالديهايد-3-فوسفات (G3P)",
    "haute",True,None,[],[],CH21,MC21,
    ["La réduction consomme ATP et NADPH","Le G3P est un sucre à 3 carbones"],
    tags=["processus","photosynthese","carbone"])

add("Cycle de Calvin phase 3 : Régénération","دورة كالفن المرحلة 3 : التجديد","processus",
    "Troisième phase où le RuBP est régénéré à partir de G3P utilisant de l'ATP, permettant au cycle de continuer",
    "المرحلة الثالثة حيث يتجدد RuBP من G3P باستخدام ATP، مما يسمح باستمرار الدورة",
    "moyenne",True,None,[],[],CH21,MC21,
    ["La régénération de RuBP consomme de l'ATP","5 molécules de G3P sur 6 sont utilisées pour régénérer 3 RuBP"],
    tags=["processus","photosynthese","carbone"])

# Cat 2.2 — Respiration cellulaire
CH22 = "Respiration cellulaire"
MC22 = "ch_respiration"

add("Membrane interne mitochondriale","الغشاء الداخلي للميتوكوندري","structure",
    "Membrane sélectivement perméable repliée en crêtes où sont localisés les complexes de la chaîne respiratoire et l'ATP synthase",
    "غشاء انتقائي النفاذية مطوي في أعراف حيث توجد معقدات السلسلة التنفسية و ATP سنتاز",
    "haute",True,None,[],[],CH22,MC22,
    ["Les crêtes augmentent la surface de la membrane interne","La membrane interne est imperméable aux ions H+"],
    tags=["structure","mitochondrie","membrane"])

add("Espace intermembranaire","الحيز بين الغشائي","structure",
    "Compartiment entre les membranes externe et interne de la mitochondrie où les protons sont pompés pour créer le gradient électrochimique",
    "حيز بين الغشاءين الخارجي والداخلي للميتوكوندري حيث تضخ البروتونات لإحداث التدرج الكهروكيميائي",
    "moyenne",True,None,[],[],CH22,MC22,
    ["La concentration en H+ est maximale dans l'espace intermembranaire","Le gradient de protons est la force proton-motrice"],
    tags=["structure","mitochondrie","energie"])

add("Matrice mitochondriale","المادة الأساسية للميتوكوندري","structure",
    "Compartiment interne de la mitochondrie contenant les enzymes du cycle de Krebs, l'ADN mitochondrial et les ribosomes",
    "الحيز الداخلي للميتوكوندري يحتوي على إنزيمات دورة كريبس و ADN الميتوكوندري والريبوزومات",
    "moyenne",True,None,[],[],CH22,MC22,
    ["Le cycle de Krebs se déroule dans la matrice","La matrice est riche en enzymes métaboliques"],
    tags=["structure","mitochondrie","metabolisme"])

add("Complexe I (NADH déshydrogénase)","المعقد I (نازعة NADH)","enzyme",
    "Premier complexe de la chaîne respiratoire oxydant le NADH et pompant des protons vers l'espace intermembranaire",
    "أول معقد في السلسلة التنفسية يؤكسد NADH ويضخ بروتونات نحو الحيز بين الغشائي",
    "haute",True,None,[],[],CH22,MC22,
    ["Le complexe I transfère les électrons du NADH à l'ubiquinone","Il pompe 4 H+ par NADH oxydé"],
    tags=["enzyme","respiration","membrane"])

add("Complexe IV (Cytochrome c oxydase)","المعقد IV (سيتوكروم c أكسيداز)","enzyme",
    "Dernier complexe de la chaîne respiratoire réduisant O2 en H2O et pompant des protons",
    "آخر معقد في السلسلة التنفسية يختزل O2 إلى H2O ويضخ بروتونات",
    "haute",True,None,[],[],CH22,MC22,
    ["Le complexe IV contient les centres cuivre-hème","Il pompe 2 H+ par paire d'électrons"],
    tags=["enzyme","respiration","membrane"])

add("Cytochrome c","السيتوكروم c","molecule",
    "Petite protéine mobile de transport d'électrons située dans l'espace intermembranaire, transférant les électrons du complexe III au complexe IV",
    "بروتين صغير متحرك ناقل للإلكترونات في الحيز بين الغشائي، ينقل الإلكترونات من المعقد III إلى المعقد IV",
    "moyenne",True,None,[],[],CH22,MC22,
    ["Le cytochrome c contient un groupe hème","Le cytochrome c est aussi impliqué dans l'apoptose"],
    tags=["molecule","respiration","transport"])

add("Force proton-motrice","القوة المحركة للبروتونات","concept",
    "Énergie potentielle électrochimique du gradient de protons à travers la membrane interne mitochondriale utilisée par l'ATP synthase",
    "الطاقة الكامنة الكهروكيميائية لتدرج البروتونات عبر الغشاء الداخلي للميتوكوندري يستخدمها ATP سنتاز",
    "haute",True,None,[],[],CH22,MC22,
    ["La force proton-motrice a un gradient chimique et électrique","L'ATP synthase convertit cette énergie en ATP"],
    tags=["concept","energie","membrane"])

add("Couple redox","الزوج المرتجع/مؤكسد","concept",
    "Paire d'une forme réduite et oxydée d'une molécule participant aux réactions d'oxydo-réduction (NAD+/NADH, FAD/FADH2)",
    "زوج من شكل مرجع ومؤكسد لجزيء يشارك في تفاعلات الأكسدة-الاختزال (NAD+/NADH, FAD/FADH2)",
    "moyenne",True,None,[],[],CH22,MC22,
    ["Le potentiel redox standard détermine le sens du transfert d'électrons","NADH a un potentiel plus négatif que FADH2"],
    tags=["concept","chimie","energie"])

# Cat 2.3 — Fermentation
CH23 = "Énergie cellulaire"
MC23 = "ch_fermentation"

add("Métabolisme","الأيض","concept",
    "Ensemble des réactions biochimiques cellulaires comprenant le catabolisme (dégradation) et l'anabolisme (synthèse)",
    "مجموع التفاعلات الكيميائية الحيوية الخلوية يشمل التقويض (الهدم) والبناء",
    "critique",True,None,[],[],CH23,MC23,
    ["Le catabolisme libère de l'énergie","L'anabolisme consomme de l'énergie"],
    tags=["concept","biologie","cellule"])

add("Catabolisme","التقويض","processus",
    "Voie métabolique de dégradation des molécules complexes en molécules simples avec libération d'énergie chimique (ATP)",
    "مسار أيضي لهدم الجزيئات المعقدة إلى جزيئات بسيطة مع تحرير طاقة كيميائية (ATP)",
    "haute",True,None,[],[],CH23,MC23,
    ["Le catabolisme du glucose produit de l'énergie","La respiration et la fermentation sont des voies cataboliques"],
    tags=["processus","metabolisme","energie"])

add("Anabolisme","البناء","processus",
    "Voie métabolique de synthèse de molécules complexes à partir de molécules simples avec consommation d'énergie",
    "مسار أيضي لتركيب جزيئات معقدة من جزيئات بسيطة مع استهلاك طاقة",
    "haute",True,None,[],[],CH23,MC23,
    ["La photosynthèse est un processus anabolique","La synthèse des protéines consomme de l'ATP"],
    tags=["processus","metabolisme","synthese"])

add("Respiration cellulaire","التنفس الخلوي","processus",
    "Processus aérobie de dégradation complète du glucose en CO2 et H2O produisant 36-38 ATP par glucose",
    "عملية هوائية للهدم الكامل للغلوكوز إلى CO2 و H2O تنتج 36-38 ATP لكل غلوكوز",
    "critique",True,None,[],[],CH23,MC23,
    ["La respiration utilise O2 comme accepteur final d'électrons","Elle comprend glycolyse, cycle de Krebs et phosphorylation oxydative"],
    tags=["processus","metabolisme","energie"])

add("Fermentation","التخمر","processus",
    "Processus anaérobie de dégradation partielle du glucose produisant seulement 2 ATP par glucose, avec régénération du NAD+",
    "عملية لاهوائية للهدم الجزئي للغلوكوز تنتج فقط 2 ATP لكل غلوكوز، مع تجديد NAD+",
    "haute",True,None,[],[],CH23,MC23,
    ["La fermentation permet la poursuite de la glycolyse en absence d'O2","Le NAD+ régénéré permet à la glycolyse de continuer"],
    tags=["processus","fermentation","anaerobie"])

add("Régénération du NAD+","تجديد NAD+","processus",
    "Processus clé des fermentations où le NADH est réoxydé en NAD+ pour permettre la poursuite de la glycolyse",
    "عملية رئيسية في التخمرات حيث يُعاد أكسدة NADH إلى NAD+ للسماح باستمرار التحلل السكري",
    "haute",True,None,[],[],CH23,MC23,
    ["Dans la fermentation alcoolique, le NADH réduit l'acétaldéhyde en éthanol","Dans la fermentation lactique, le NADH réduit le pyruvate en lactate"],
    tags=["processus","fermentation","metabolisme"])

add("Lactate","اللاكتات","molecule",
    "Produit de la fermentation lactique formé par réduction du pyruvate par le NADH en conditions anaérobies",
    "ناتج التخمر اللبني المتشكل باختزال البيروفات بواسطة NADH في الظروف اللاهوائية",
    "moyenne",True,None,["acide lactique"],[],CH23,MC23,
    ["L'accumulation de lactate cause la crampe musculaire","Le lactate est recyclé en glucose dans le foie (cycle de Cori)"],
    tags=["molecule","fermentation","muscle"])

add("Éthanol","الإيثانول","molecule",
    "Produit de la fermentation alcoolique formé par réduction de l'acétaldéhyde par le NADH sous l'action de l'alcool déshydrogénase",
    "ناتج التخمر الكحولي المتشكل باختزال الأسيتالديهايد بواسطة NADH بفعل نازعة هيدروجين الكحول",
    "moyenne",False,None,[],[],CH23,MC23,
    ["L'éthanol est produit par les levures en anaérobiose","La fermentation alcoolique est utilisée en brasserie et boulangerie"],
    tags=["molecule","fermentation","levure"])

# ═══════════════════════════════════════════════════════════
# Additional terms for Domain 3 — Tectonique globale
# ═══════════════════════════════════════════════════════════

# Cat 3.1 — Plaques tectoniques
CH31 = "Tectonique des plaques"
MC31 = "ch_tectonique"

add("Plaque tectonique","الصفيحة التكتونية","concept",
    "Fragment rigide de la lithosphère se déplaçant sur l'asthénosphère, limité par des frontières divergentes, convergentes ou transformantes",
    "قطعة صلبة من الغلاف الصخري تتحرك فوق الغلاف الموري، محددة بحدود متباعدة أو متقاربة أو متحولة",
    "critique",True,None,["plaque lithosphérique"],[],CH31,MC31,
    ["Il existe 7 plaques principales et plusieurs plaques secondaires","Les plaques se déplacent de quelques cm/an"],
    tags=["concept","tectonique","geologie"])

add("Divergence","التباعد","processus",
    "Mouvement d'écartement de deux plaques tectoniques au niveau des dorsales océaniques ou des rifts continentaux",
    "حركة ابتعاد صفيحتين تكتونيتين على مستوى الأظهرة المحيطية أو الخسوف القارية",
    "haute",True,None,[],[],CH31,MC31,
    ["La divergence crée une nouvelle lithosphère océanique","La divergence est à l'origine de l'expansion océanique"],
    tags=["processus","tectonique","extension"])

add("Anomalie magnétique","الشذوذ المغناطيسي","concept",
    "Variation du champ magnétique terrestre enregistrée dans les roches, symétrique de part et d'autre des dorsales océaniques",
    "تغير في المجال المغناطيسي الأرضي المسجل في الصخور، متماثل على جانبي الأظهرة المحيطية",
    "haute",True,None,[],[],CH31,MC31,
    ["Les anomalies magnétiques symétriques prouvent l'expansion océanique","Les inversions magnétiques sont enregistrées dans la croûte océanique"],
    tags=["concept","tectonique","magnetisme"])

add("Âge de la croûte océanique","عمر القشرة المحيطية","concept",
    "Âge des roches de la croûte océanique augmentant avec la distance à la dorsale, la plus jeune étant au niveau de l'axe de la dorsale",
    "عمر صخور القشرة المحيطية يزداد مع البعد عن الظهرة، الأصغر على محور الظهرة",
    "haute",True,None,[],[],CH31,MC31,
    ["La croûte océanique la plus vieille a ~200 Ma","La croûte océanique est recyclée par subduction"],
    tags=["concept","tectonique","geologie"])

add("Sismologie","علم الزلازل","concept",
    "Science étudiant les séismes et la propagation des ondes sismiques pour comprendre la structure interne de la Terre",
    "علم يدرس الزلازل وانتشار الموجات الزلزالية لفهم البنية الداخلية للأرض",
    "moyenne",True,None,[],[],CH31,MC31,
    ["La sismologie a permis de découvrir la structure en couches de la Terre","Les ondes sismiques sont des ondes P et S"],
    tags=["concept","geologie","sismologie"])

add("Séisme","الزلزال","concept",
    "Tremblement de terre résultant de la libération brusque d'énergie accumulée le long des failles, principalement aux frontières des plaques",
    "اهتزاز أرضي ناتج عن تحرر مفاجئ للطاقة المتراكمة على طول الصدوع، خاصة عند حدود الصفائح",
    "haute",True,None,[],[],CH31,MC31,
    ["Les séismes sont fréquents aux limites de plaques","Le foyer (hypocentre) est le point de rupture initial"],
    tags=["concept","geologie","seisme"])

add("Faille","الصدع","structure",
    "Cassure de la lithosphère avec déplacement des blocs rocheux, classée en faille normale (extension), inverse (compression) ou décrochante (cisaillement)",
    "كسر في الغلاف الصخري مع إزاحة الكتل الصخرية، يصنف إلى عادي (تمددي) أو معكوس (انضغاطي) أو مضرب (قصي)",
    "moyenne",True,None,[],[],CH31,MC31,
    ["Les failles normales sont associées aux rifts","Les failles inverses sont associées aux zones de subduction"],
    tags=["structure","tectonique","geologie"])

add("Expansion océanique","الانتشار المحيطي","processus",
    "Processus de création de nouvelle croûte océanique au niveau des dorsales, éloignant progressivement les continents",
    "عملية تكوين قشرة محيطية جديدة على مستوى الأظهرة، تبعد القارات تدريجياً",
    "haute",True,None,["accrétion océanique"],[],CH31,MC31,
    ["L'expansion océanique a été proposée par Hess en 1962","Les taux d'expansion varient de 1 à 10 cm/an"],
    tags=["processus","tectonique","divergence"])

add("Dérive des continents","الانجراف القاري","concept",
    "Théorie de Wegener (1912) proposant que les continents se déplacent à la surface de la Terre, précurseur de la tectonique des plaques",
    "نظرية فيجنر (1912) تقترح أن القارات تتحرك على سطح الأرض، سابقة للنظرية التكتونية",
    "haute",True,None,[],[],CH31,MC31,
    ["Wegener s'est basé sur l'emboîtement des continents et la continuité des fossiles","La théorie a été rejetée faute de mécanisme"],
    tags=["concept","tectonique","histoire"])

# Cat 3.2 — Structure interne
CH32 = "Structure du globe"
MC32 = "ch_globe"

add("Croûte continentale","القشرة القارية","concept",
    "Partie de la croûte terrestre formant les continents, épaisse (30-70 km), de composition granitique (sial), moins dense que la croûte océanique",
    "جزء القشرة الأرضية المكون للقارات، سميكة (30-70 كم)، غرانيتية التركيب (سيال)، أقل كثافة من القشرة المحيطية",
    "haute",True,None,[],[],CH32,MC32,
    ["La croûte continentale est riche en silice et aluminium","Les roches les plus vieilles de la croûte continentale ont 4 Ga"],
    tags=["concept","geologie","structure"])

add("Croûte océanique","القشرة المحيطية","concept",
    "Partie de la croûte terrestre formant le plancher océanique, fine (5-10 km), de composition basaltique (sima), dense",
    "جزء القشرة الأرضية المكون لقاع المحيط، رقيقة (5-10 كم)، بازلتية التركيب (سيما)، كثيفة",
    "haute",True,None,[],[],CH32,MC32,
    ["La croûte océanique est composée de basalte et de gabbro","Elle est recyclée par subduction tous les ~200 Ma"],
    tags=["concept","geologie","structure"])

add("Manteau supérieur","الستار العلوي","concept",
    "Partie supérieure du manteau terrestre (jusqu'à 670 km) incluant la zone de faible vitesse (asthénosphère) et la lithosphère mantellique",
    "الجزء العلوي من الستار الأرضي (حتى 670 كم) يشمل منطقة السرعة المنخفضة (الغلاف الموري) والغلاف الصخري الستاري",
    "moyenne",True,None,[],[],CH32,MC32,
    ["Le manteau supérieur est constitué de péridotite","La fusion partielle du manteau supérieur produit le magma basaltique"],
    tags=["concept","geologie","structure"])

add("Manteau inférieur","الستار السفلي","concept",
    "Partie inférieure du manteau entre 670 km et 2900 km, solide mais soumise à de très hautes pressions et températures",
    "الجزء السفلي من الستار بين 670 كم و 2900 كم، صلب لكن تحت ضغوط وحرارة عالية جداً",
    "moyenne",False,None,[],[],CH32,MC32,
    ["La pression dans le manteau inférieur dépasse 1 million d'atmosphères","Les minéraux y adoptent des structures cristallines plus denses"],
    tags=["concept","geologie","structure"])

add("Noyau externe","النواة الخارجية","concept",
    "Partie liquide du noyau terrestre entre 2900 et 5100 km de profondeur, composée principalement de fer et de nickel en fusion, générant le champ magnétique",
    "الجزء السائل من النواة الأرضية بين 2900 و 5100 كم عمقاً، مكون أساساً من حديد ونيكل منصهرين، يولد المجال المغناطيسي",
    "haute",True,None,[],[],CH32,MC32,
    ["Le noyau externe est liquide car les ondes S ne le traversent pas","Les mouvements de convection dans le noyau externe génèrent la géodynamo"],
    tags=["concept","geologie","structure"])

add("Noyau interne","النواة الداخلية","concept",
    "Partie solide centrale de la Terre (rayon ~1220 km) composée de fer et nickel solides, à ~5500°C sous très haute pression",
    "الجزء الصلب المركزي للأرض (نصف قطر ~1220 كم) مكون من حديد ونيكل صلبين، في ~5500°C تحت ضغط عال جداً",
    "moyenne",False,None,["graine"],[],CH32,MC32,
    ["Le noyau interne est solide malgré sa température élevée","Les ondes P augmentent de vitesse en traversant le noyau interne"],
    tags=["concept","geologie","structure"])

add("Champ magnétique terrestre","المجال المغناطيسي الأرضي","concept",
    "Champ magnétique dipolaire généré par les mouvements du fer liquide dans le noyau externe, protégeant la Terre des particules solaires",
    "مجال مغناطيسي ثنائي القطب يولده حركة الحديد السائل في النواة الخارجية، يحمي الأرض من الجسيمات الشمسية",
    "moyenne",True,None,[],[],CH32,MC32,
    ["Le champ magnétique s'inverse périodiquement (toutes les ~250 000 ans)","Il dévie les particules du vent solaire"],
    tags=["concept","geologie","magnetisme"])

# Cat 3.3 — Magmatisme
CH33 = "Magmatisme"
MC33 = "ch_magmatisme"

add("Roche plutonique","صخر بلوتوني","concept",
    "Roche magmatique formée par refroidissement lent du magma en profondeur (intrusion), à cristaux visibles à l'œil nu (grenue)",
    "صخر ناري يتشكل بتبريد بطيء للماغما في العمق (تداخلي)، ببلورات مرئية بالعين المجردة (حبيبي)",
    "haute",True,None,["roche intrusive"],[],CH33,MC33,
    ["Le granite est une roche plutonique typique","Le refroidissement lent permet la croissance de grands cristaux"],
    tags=["concept","magmatisme","roche"])

add("Roche volcanique","صخر بركاني","concept",
    "Roche magmatique formée par refroidissement rapide du magma en surface (effusion), à cristaux microscopiques (microlitique)",
    "صخر ناري يتشكل بتبريد سريع للماغما على السطح (انبجاسي)، ببلورات مجهرية (ميكروليتي)",
    "haute",True,None,["roche effusive"],[],CH33,MC33,
    ["Le basalte est une roche volcanique typique","Le refroidissement rapide donne une texture microlitique"],
    tags=["concept","magmatisme","roche"])

add("Chambre magmatique","الحجرة الماغماتية","concept",
    "Réservoir de magma situé dans la croûte terrestre alimentant les éruptions volcaniques",
    "خزان للماغما يقع في القشرة الأرضية يغذي الثورانات البركانية",
    "haute",True,None,[],[],CH33,MC33,
    ["La différenciation magmatique se produit dans la chambre","Le toit de la chambre peut s'effondrer formant une caldeira"],
    tags=["concept","magmatisme","volcan"])

add("Fusion mantellique","الانصهار الستاري","processus",
    "Fusion partielle des roches du manteau (péridotite) produisant un magma basaltique, déclenchée par décompression (dorsales) ou hydratation (subduction)",
    "انصهار جزئي لصخور الستار (بيريدوتيت) ينتج ماغما بازلتية، يحدث بفعل خفض الضغط (أظهرة) أو الإماهة (غوص)",
    "haute",True,None,[],[],CH33,MC33,
    ["La fusion par décompression se produit sous les dorsales","L'apport d'eau abaisse le point de fusion dans les zones de subduction"],
    tags=["processus","magmatisme","geologie"])

add("Dyke (filon)","القاطع (السد)","structure",
    "Intrusion magmatique tabulaire recoupant les structures de la roche encaissante, souvent verticale ou inclinée",
    "تداخل ماغماتي طبقي يقطع بنى الصخر المحيط، غالباً عمودي أو مائل",
    "moyenne",False,None,[],[],CH33,MC33,
    ["Les dykes sont souvent associés au volcanisme","Ils peuvent servir de conduits pour le magma"],
    tags=["structure","magmatisme","intrusion"])

add("Sill (filon-couche)","الطبقة المتداخلة","structure",
    "Intrusion magmatique tabulaire parallèle aux structures de la rocheencaissante, souvent horizontale",
    "تداخل ماغماتي طبقي موازٍ لبنى الصخر المحيط، غالباً أفقي",
    "moyenne",False,None,[],[],CH33,MC33,
    ["Les sills s'injectent entre les couches sédimentaires","Le refroidissement lent dans un sill donne des cristaux moyens"],
    tags=["structure","magmatisme","intrusion"])

# ── Update metadata ──
all_terms = [t for dom in lexique["domaines"] for c in dom["categories"] for t in c["termes"]]
lexique["metadata"]["total_entrees"] = len(all_terms)
lexique["metadata"]["date_creation"] = "2026-06-15"
lexique["metadata"]["version"] = "1.0"

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(lexique, f, ensure_ascii=False, indent=2)

print(f"[OK] Enriched lexique")
print(f"  Total terms: {len(all_terms)}")
for d in lexique["domaines"]:
    c_total = sum(len(c["termes"]) for c in d["categories"])
    cat_detail = [f"{c['nom_fr']}:{len(c['termes'])}" for c in d["categories"]]
    print(f"  {d['nom_fr']}: {c_total} terms ({', '.join(cat_detail)})")
print(f"  Critiques: {sum(1 for t in all_terms if t['importance']=='critique')}")
print(f"  Types: {sorted(set(t['type'] for t in all_terms))}")
