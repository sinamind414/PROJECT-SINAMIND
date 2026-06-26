"""
scripts/ingest_chapter1.py - Ingestion des chunks du manuel scolaire pour le RAG.
"""

import asyncio
import json
import os
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import get_settings
from services.embedder import embedder

CHAPTER1_CHUNKS = [
    # ════ النشاط 2 : مقر تركيب البروتين ════
    {
        "id": "ch1_act2_autoradiographie",
        "branche": "مقر تركيب البروتين",
        "sous_branche": "تقنية التصوير الإشعاعي",
        "page": 12,
        "type": "experience",
        "priority": 2,
        "texte": """تقنية التصوير الإشعاعي الذاتي تسمح بتتبع مسار المركبات المشعة داخل الخلية. بعد تحضين خلايا البنكرياس مع أحماض أمينية مشعة لمدة 3 دقائق، تمركز الإشعاع في منطقة الشبكة الهيولية المحببة (الريبوزومات). الاستنتاج: مقر تركيب البروتين هو الريبوزوم.""",
        "concepts": ["autoradiographie_technique", "ribosome_maqar", "methode_onec"]
    },
    {
        "id": "ch1_act2_arnm_grenouille",
        "branche": "مقر تركيب البروتين",
        "sous_branche": "إثبات دور ARNm",
        "page": 13,
        "type": "experience",
        "priority": 1,
        "texte": """تجربة حقن ARNm الأرنب في الخلايا البيضية للضفدع: المجموعة الثالثة أنتجت بروتينات الضفدع + هيموغلوبين الأرنب. الاستنتاج: ARNm يحمل المعلومات الوراثية ويوجه تركيب البروتين بصرف النظر عن نوع الخلية (عالمية الشفرة الوراثية).""",
        "concepts": ["ARNm_messager", "ARNm_universalite", "information_genetique"]
    },
    {
        "id": "ch1_act2_uracile_radioactif",
        "branche": "مقر تركيب البروتين",
        "sous_branche": "انتقال ARNm",
        "page": 14,
        "type": "experience",
        "priority": 1,
        "texte": """تجربة اليوراسيل المشع: اليوراسيل قاعدة أزوتية خاصة بـ ARN (غير موجودة في ADN). بعد فترة قصيرة: الإشعاع في النواة. بعد فترة أطول: الإشعاع ينتقل إلى الهيولى. الاستنتاج: ARNm يُصنع في النواة ثم ينتقل إلى الهيولى.""",
        "concepts": ["uracile_ARN_only", "ARNm_migration", "ARNm_messager"]
    },

    # ════ النشاط 3 : الاستنساخ ════
    {
        "id": "ch1_act3_arn_polymerase",
        "branche": "عملية الاستنساخ",
        "sous_branche": "إنزيم ARN بوليمراز",
        "page": 16,
        "type": "experience",
        "priority": 1,
        "texte": """تثبيط إنزيم ARN بوليمراز بمادة α-أمانيتين (مستخرجة من فطر Amanita phalloides) أدى إلى توقف تشكل ARNm. الاستنتاج: ARN بوليمراز ضروري وأساسي لعملية الاستنساخ. الإنزيم يفتح سلسلتي ADN ويقرأ السلسلة المستنسخة ويربط النيوكليوتيدات في اتجاه 5' → 3'.""",
        "concepts": ["ARN_polymerase_role", "inhibition_alpha_amanitine", "transcription_direction"]
    },
    {
        "id": "ch1_act3_phases_transcription",
        "branche": "عملية الاستنساخ",
        "sous_branche": "المراحل الثلاث",
        "page": 18,
        "type": "hasila",
        "priority": 1,
        "texte": """مراحل الاستنساخ الثلاث: الانطلاق: ارتباط ARN بوليمراز بمنطقة البداية وانفتاح سلسلتي ADN. الاستطالة: تحرك الإنزيم وقراءة السلسلة المستنسخة (3'→5') وربط النيوكليوتيدات المتكاملة لتشكيل ARNm (5'→3'). النهاية: انتهاء تركيب ARNm وانفصال الإنزيم والـ ARNm والتحام سلسلتي ADN.""",
        "concepts": ["transcription_initiation", "transcription_elongation", "transcription_terminaison", "polarite_5_3"]
    },
    {
        "id": "ch1_act3_epissage",
        "branche": "عملية الاستنساخ",
        "sous_branche": "نضج ARNm",
        "page": 19,
        "type": "hasila",
        "priority": 1,
        "texte": """عند حقيقيات النواة: ARNm الأولي يخضع لعملية النضج (الإسبلايسينغ): حذف القطع غير الدالة (Introns/الإنترونات) وربط القطع الدالة (Exons/الإكسونات) ← ARNm ناضج أقل طولاً يغادر إلى الهيولى. هذه الظاهرة غائبة تماماً عند بدائيات النواة (البكتيريا).""",
        "concepts": ["epissage", "introns_suppression", "exons_jonction", "ARNm_mature", "eucaryotes_only"]
    },

    # ════ النشاط 4 : الشفرة الوراثية ════
    {
        "id": "ch1_act4_code_genetique_base",
        "branche": "الشفرة الوراثية",
        "sous_branche": "مفهوم الرامزة",
        "page": 20,
        "type": "hasila",
        "priority": 1,
        "texte": """الشفرة الوراثية: الرامزة = 3 نيوكليوتيدات تشفر لحمض أميني واحد. 64 رامزة إجمالاً (4³): 61 رامزة تشفر لـ 20 حمض أميني (الشفرة منحلة/متردّدة)، 3 رامزات توقف: UAA، UAG، UGA (لا تشفر لأي حمض أميني)، ورامزة الانطلاق: AUG (تشفر للميثيونين دائماً). الشفرة عالمية: نفس الشفرة لجميع الكائنات الحية.""",
        "concepts": ["codon_definition", "code_degenere", "AUG_methionine", "stop_codons_UAA_UAG_UGA", "code_universel"]
    },
    {
        "id": "ch1_act4_nirenberg",
        "branche": "الشفرة الوراثية",
        "sous_branche": "تجربة Nirenberg",
        "page": 21,
        "type": "experience",
        "priority": 2,
        "texte": """تجربة Nirenberg: ARNm اصطناعي من U فقط (UUU...) ← سلسلة من فينيل ألانين (Phe) فقط. النتيجة: رامزة UUU تشفر للفينيل ألانين. بالمثل: AAA→Lys, CCC→Pro, GGG→Gly. الاستنتاج: الرمز الوراثي يقرأ بثلاثيات متتالية غير متداخلة.""",
        "concepts": ["nirenberg_experience", "decodage_codon", "code_non_chevauchant"]
    },

    # ════ النشاط 5 : مراحل الترجمة ════
    {
        "id": "ch1_act5_polysome",
        "branche": "عملية الترجمة",
        "sous_branche": "متعدد الريبوزوم",
        "page": 24,
        "type": "hasila",
        "priority": 1,
        "texte": """متعدد الريبوزوم (البوليزوم/Polyribosome): عدة ريبوزومات تنزلق على نفس خيط ARNm في نفس الوقت. الفائدة: تضاعف كمية البروتين المصنع في نفس الوقت. إضافة ريبونيوكلياز (يفكك ARNm) ← اختفاء البوليزوم وتوقف تركيب البروتين (إثبات دور ARNm في تماسك البوليزوم).""",
        "concepts": ["polysome_definition", "polysome_role_quantite", "ARNm_polysome_liaison"]
    },
    {
        "id": "ch1_act5_ribosome_structure",
        "branche": "عملية الترجمة",
        "sous_branche": "بنية الريبوزوم",
        "page": 26,
        "type": "schema",
        "priority": 2,
        "texte": """الريبوزوم يتكون من وحدتين: الوحدة الكبرى (50S عند البكتيريا): تحتوي على الموقع P (موقع الببتيد) والموقع A (موقع الحمض الأميني) ونفق خروج السلسلة الببتيدية. الوحدة الصغرى (30S): موقع ارتباط ARNm. كلتا الوحدتين تتكونان من بروتينات و ARNr.""",
        "concepts": ["ribosome_structure", "site_P_peptidyl", "site_A_aminoacyl", "ARNr_composition"]
    },
    {
        "id": "ch1_act5_arnt_structure",
        "branche": "عملية الترجمة",
        "sous_branche": "بنية ARNt",
        "page": 27,
        "type": "schema",
        "priority": 1,
        "texte": """ARNt (الحمض الريبي الناقل) يتميز بموقعين أساسيين: 1. موقع تثبيت الحمض الأميني في النهاية 3' (CCA-3')، 2. موقع الرامزة المضادة (Anticodon): تتكامل مع رامزة ARNm بروابط هيدروجينية. البنية الثلاثية الأبعاد: شكل حرف L مقلوب.""",
        "concepts": ["ARNt_site_AA", "anticodon_site", "ARNt_3D_structure", "complementarite_codon_anticodon"]
    },
    {
        "id": "ch1_act5_activation_AA",
        "branche": "عملية الترجمة",
        "sous_branche": "تنشيط الأحماض الأمينية",
        "page": 28,
        "type": "hasila",
        "priority": 1,
        "texte": """تنشيط الأحماض الأمينية (خطوة ضرورية قبل الترجمة): الحمض الأميني + ARNt + ATP --[أمينو أسيل ARNt سينتيتار]-→ معقد (AA-ARNt) نشط + AMP + بيروفسفات. كل حمض أميني له إنزيم نوعي خاص به.""",
        "concepts": ["activation_AA", "aminoacyl_ARNt_synthetase", "ATP_energie_activation", "specificite_enzyme"]
    },
    {
        "id": "ch1_act5_phases_traduction",
        "branche": "عملية الترجمة",
        "sous_branche": "المراحل الثلاث",
        "page": 29,
        "type": "hasila",
        "priority": 1,
        "texte": """مراحل الترجمة الثلاث: الانطلاق: ARNm يرتبط بالوحدة الصغرى، ARNt-Met (رامزة مضادة UAC) يتوضع على AUG في الموقع P، التحام الوحدة الكبرى. الاستطالة: ARNt الثاني يتوضع في الموقع A، تشكل الرابطة الببتيدية بين الحمضين بتدخل إنزيمات وATP، انزلاق الريبوزوم رامزة واحدة نحو 3'، الموقع A يصبح شاغراً لاستقبال حمض جديد. النهاية: وصول رامزة توقف (UAA أو UAG أو UGA)، انفصال السلسلة الببتيدية + تحرير الميثيونين الأول، تفكك الريبوزوم إلى وحدتيه.""",
        "concepts": ["traduction_initiation", "traduction_elongation", "traduction_terminaison", "liaison_peptidique", "ribosome_glissement", "methionine_liberation"]
    },

    # ════ الحصيلة المعرفية (الأولوية القصوى) ════
    {
        "id": "ch1_hasila_complete",
        "branche": "الحصيلة المعرفية",
        "sous_branche": "الملخص الرسمي",
        "page": 32,
        "type": "hasila",
        "priority": 1,
        "is_bareme_source": True,
        "texte": """يتم تركيب البروتين في الهيولى، ويتطلب نقل نسخة من المعلومات الوراثية من النواة في صورة جزيء الـ ARNm. يتم تركيب جزيء ARNm بواسطة إنزيم نوعي يدعى ARN بوليمراز عبر ثلاث خطوات: الانطلاق (ارتباط الإنزيم ببداية المورثة وفتح السلسلتين)، الاستطالة (ربط النيوكليوتيدات المتكاملة)، النهاية (انفصال ARNm الأولي والإنزيم). عند حقيقيات النواة: حذف الإنترونات وربط الإكسونات ← ARNm ناضج. وحدة الشفرة الوراثية هي الرامزة (3 نيوكليوتيدات تشفر لحمض أميني واحد). 64 رامزة لـ 20 حمض أميني. 61 رامزة تشفر للأحماض الأمينية (منها AUG رامزة الانطلاق). 3 رامزات توقف (UAA, UAG, UGA). تتم الترجمة على مستوى متعدد الريبوزوم (البوليزوم). يتطلب تدخل الـ ARNt الذي يقوم بتنشيط الأحماض الأمينية بتدخل إنزيم نوعي (أمينو أسيل ARNt سينتيتار) وطاقة ATP. الريبوزومات تتكون من تحت وحدتين تحتوي الكبرى على الموقعين A و P. الانطلاق: تشكيل معقد الانطلاق وتوضع الميثيونين في الموقع P. الاستطالة: توالي توضع الأحماض وتشكل الروابط الببتيدية وانزلاق الريبوزوم من 5' إلى 3'. النهاية: الوصول لرامزة التوقف وانفصال السلسلة الببتيدية وتفكك العضيات. ينطوي البروتين ليأخذ بنيته الفراغية. إذا كان إفرازياً: ينتقل عبر الشبكة الهيولية الفعالة ← جهاز غولجي ← حويصلات إفرازية ← خارج الخلية. عند بدائيات النواة: الاستنساخ والترجمة في الهيولى معاً وفي نفس الوقت (لا يوجد غشاء نووي).""",
        "concepts": [
            "maqar_synthese_proteine", "ARNm_messager_role", "expression_genique_2etapes",
            "transcription_3phases", "epissage_eucaryotes", "code_genetique_64_codons",
            "traduction_polysome", "activation_AA_ATP", "traduction_3phases",
            "destin_proteine_secretion", "procaryotes_couplage_traduction"
        ]
    }
]


async def ingest_chapter1():
    # Charger la configuration
    cfg = get_settings()
    db_url = cfg.DATABASE_URL
    if not db_url:
        db_url = os.getenv("DATABASE_URL")

    if not db_url:
        print("Error: DATABASE_URL not set in environment or settings.")
        return

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    print("Connecting to database...")
    engine = create_async_engine(db_url, echo=False)

    print(f"Ingestion de {len(CHAPTER1_CHUNKS)} chunks — Chapitre 1")
    print("=" * 60)

    async with engine.begin() as conn:
        for chunk in CHAPTER1_CHUNKS:
            # Calcul de l'embedding
            embedding = embedder.encode([chunk["texte"]])[0]

            # Insertion idempotente
            await conn.execute(
                text("""
                    INSERT INTO reference_embeddings
                        (question_id, variant_index, reference_text,
                         embedding, source, metadata)
                    VALUES (:qid, 0, :text, CAST(:emb AS vector), 'livre_scolaire_ch1', :meta)
                    ON CONFLICT (question_id, variant_index)
                    DO UPDATE SET
                        reference_text = EXCLUDED.reference_text,
                        embedding      = EXCLUDED.embedding,
                        metadata       = EXCLUDED.metadata,
                        updated_at     = NOW()
                """),
                {
                    "qid": chunk["id"],
                    "text": chunk["texte"],
                    "emb": str(embedding.tolist()),
                    "meta": json.dumps({
                        "branche":      chunk["branche"],
                        "sous_branche": chunk.get("sous_branche"),
                        "page":         chunk["page"],
                        "type":         chunk["type"],
                        "priority":     chunk["priority"],
                        "concepts":     chunk["concepts"],
                        "is_bareme":    chunk.get("is_bareme_source", False)
                    }, ensure_ascii=False)
                }
            )

            symbol = "⭐" if chunk.get("is_bareme_source") else "✅"
            print(f"  {symbol} {chunk['id']} (page {chunk['page']})")

    # Vérification finale
    async with engine.connect() as conn:
        res = await conn.execute(
            text("SELECT COUNT(*) FROM reference_embeddings WHERE source = 'livre_scolaire_ch1'")
        )
        count = res.scalar()
        print(f"\n{'=' * 60}")
        print(f"  Résultat : {count} chunks ingérés pour le chapitre 1")
        print("  Priorité 1 (bareme) : الحصيلة المعرفية ⭐")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(ingest_chapter1())
