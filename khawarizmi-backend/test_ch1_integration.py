import sys
import os
import asyncio

# Configurer sys.path pour importer depuis le bon dossier
sys.path.append(os.path.dirname(__file__))

from services.questions import get_question
from services.fallback_v2 import evaluate_l2

def safe_print(text: str):
    """Affichage UTF-8 robuste (Windows + Arabic/Emojis)."""
    try:
        sys.stdout.buffer.write(text.encode('utf-8') + b'\n')
        sys.stdout.buffer.flush()
    except Exception:
        print(text.encode('ascii', errors='replace').decode('ascii'))

async def test_fallback_ch1():
    safe_print("=== TESTING FALLBACK L2 FOR CHAPITRE 1 CONCEPTS ===")
    
    # Charger les questions
    questions_to_test = [
        "ch1_bac_pattern_01", "ch1_bac_pattern_02", "ch1_bac_pattern_03", 
        "ch1_bac_pattern_04", "ch1_bac_pattern_05",
        "bac_ch1_exp_uracile", "bac_ch1_exp_grenouille", "bac_ch1_phases_traduction_complet"
    ]
    for q_id in questions_to_test:
        q = get_question(q_id)
        if q:
            safe_print(f"[OK] Loaded question {q_id}: {q.get('texte', '')[:50]}...")
        else:
            safe_print(f"[ERR] Failed to load question {q_id}")
            continue
            
    # Cas de tests
    test_cases = [
        {
            "q_id": "ch1_bac_pattern_01",
            "ans": "يظهر التصوير الإشعاعي الذاتي إشعاعا في النواة ثم يهاجر إلى الهيولى",
            "expected_concepts": ["autoradiographie", "miqr_synthesis", "ARNm_migration"]
        },
        {
            "q_id": "ch1_bac_pattern_03",
            "ans": "تتشكل الرابطة الببتيدية بفقدان جزيء ماء ويحدث انزلاق للريبوزوم",
            "expected_concepts": ["liaison_peptidique", "H2O", "translocation"]
        },
        {
            "q_id": "ch1_bac_pattern_04",
            "ans": "الاستنساخ يحدث في النواة عند حقيقيات النوى مع إقصاء الإنترونات والقطع غير الدالة",
            "expected_concepts": ["epissage_eucaryotes", "enveloppe_nucleaire"]
        },
        {
            "q_id": "ch1_bac_pattern_05",
            "ans": "الشفرة الوراثية تتميز بأنها عالمية ومتدهورة أو منحلة ولها رامزة انطلاق وتوقف",
            "expected_concepts": ["universel", "degenere", "stop_codons", "AUG_start"]
        },
        {
            "q_id": "bac_ch1_exp_uracile",
            "ans": "تم اختيار اليوراسيل لأنه قاعدة أزوتية مميزة للـ ARN ولا توجد في الـ ADN",
            "expected_concepts": ["uracile_radioactif"]
        },
        {
            "q_id": "bac_ch1_exp_grenouille",
            "ans": "نلاحظ تركيب هيموغلوبين الأرنب في الخلايا البيضية للضفدع مما يدل على أن ARNm ينقل المعلومات الوراثية وتتميز الشفرة بالعالمية بصرف النظر عن نوع الخلية",
            "expected_concepts": ["hemo_rabbit", "arnm_transmission", "universalite"]
        },
        {
            "q_id": "bac_ch1_phases_traduction_complet",
            "ans": "مرحلة الانطلاق: يتوضع حمض الميثيونين الأول. مرحلة الاستطالة: تتشكل الرابطة الببتيدية وانزلاق الريبوزوم. مرحلة النهاية: الوصول لرامزة التوقف وتفكك معقد الترجمة.",
            "expected_concepts": ["initiation", "elongation", "terminaison", "liaison_peptidique"]
        }
    ]
    
    for tc in test_cases:
        q_data = get_question(tc["q_id"])
        if not q_data:
            continue
        res = await evaluate_l2(tc["ans"], q_data)
        safe_print(f"\nQuestion: {q_data['texte']}")
        safe_print(f"Student Answer: {tc['ans']}")
        safe_print(f"Score: {res.score_final} | Verdict: {res.verdict}")
        safe_print(f"Found: {res.concepts_trouves}")
        safe_print(f"Missing: {res.concepts_manquants}")
        for c in tc["expected_concepts"]:
            if c in res.concepts_trouves:
                safe_print(f"  [OK] Concept '{c}' matched correctly.")
            else:
                safe_print(f"  [ERR] Concept '{c}' MISSED.")

if __name__ == "__main__":
    asyncio.run(test_fallback_ch1())
