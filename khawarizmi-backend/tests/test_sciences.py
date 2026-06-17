import os
import sys
from services.khawarizmi_engine import KhawarizmiTutor

def safe_print(text):
    """Affiche le texte de manière sûre pour éviter les erreurs d'encodage sous Windows."""
    sys.stdout.buffer.write((text + '\n').encode('utf-8', errors='replace'))

def tester_sciences():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    tutor = KhawarizmiTutor(data_dir=data_dir)
    
    # Sujet et question issus de l'annale Sciences
    sujet_id = 'revision_605_questions'
    question_id = 'q_6'
    
    # Simuler une réponse d'élève pour l'Analyse (où il fait une erreur de méthode par ex)
    student_input = "نلاحظ خروج البروتين"
    
    safe_print("\n=== TEST DE L'ENGINE SUR UNE QUESTION DE SCIENCES ===")
    safe_print(f"Sujet ID: {sujet_id} | Question ID: {question_id}")
    safe_print(f"Réponse de l'élève: {student_input}")
    
    prompt = tutor.build_system_prompt(
        sujet_id=sujet_id,
        question_id=question_id,
        student_input=student_input
    )
    
    safe_print("\n=== PROMPT GÉNÉRÉ ===")
    safe_print(prompt)

if __name__ == "__main__":
    tester_sciences()
