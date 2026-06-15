import pytest
import os
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Force OPENAI_API_KEY environment variable to avoid config failure
os.environ["OPENAI_API_KEY"] = "sk-fake-key-for-testing"

from main import app
from services.questions import questions_db

client = TestClient(app)

from deps import get_current_user, get_db, get_scheduler, get_openai

def override_get_current_user():
    return {"id": 1, "email": "test@test.com", "prenom": "Amina", "plan": "pro"}

class MockAsyncResult:
    def fetchone(self):
        return ({"stability": 0, "difficulty": 0, "scheduled_days": 0, "reps": 0, "lapses": 0, "state": "0"},)
    def fetchall(self):
        return []

class MockAsyncSession:
    async def execute(self, *args, **kwargs):
        return MockAsyncResult()
    async def commit(self):
        pass

async def override_get_db():
    return MockAsyncSession()

class MockCard:
    stability = 0
    difficulty = 0
    scheduled_days = 0
    reps = 0
    lapses = 0
    state = "0"

class MockScheduler:
    def calculer_prochain_intervalle(self, card, score_percent):
        from datetime import datetime, timedelta, timezone
        mock_card = MockCard()
        return {
            "card": mock_card,
            "prochaine_revision": datetime.now(timezone.utc) + timedelta(days=2),
            "interval_jours": 2,
            "difficulty": 0,
            "stability": 0
        }

def override_get_scheduler():
    return MockScheduler()

def override_get_openai():
    return MagicMock()

app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_scheduler] = override_get_scheduler
app.dependency_overrides[get_openai] = override_get_openai

# On injecte manuellement quelques données dans questions_db pour être sûr
questions_db["q_test"] = {
    "question_id": "q_test",
    "texte": "Quel est le rôle de l'ARN polymérase ?",
    "reponse_attendue": "L'ARN polymérase catalyse la transcription de l'ADN en ARNm.",
    "concept_cle": "Transcription",
    "pattern_recherche": "ARN polymérase && transcription && ADN && ARNm"
}

def print_result(title, res_json):
    print(f"\n{'='*50}\n{title}\n{'='*50}")
    print(json.dumps(res_json, indent=2, ensure_ascii=True))

def run_tests():
    print("Démarrage des 3 tests de validation KHAWARIZMI-EVAL")
    
    # TEST 1: Cas Nominal (Réponse parfaite)
    print("\n--- TEST 1: Cas Nominal ---")
    # On mock l'appel LLM pour simuler un "CORRECT"
    with patch('services.llm.call_gpt4o_evaluator') as mock_llm:
        mock_llm.return_value = {
            "score": 10,
            "statut": "CORRECT",
            "feedback": "C'est exact. L'ARN polymérase a bien ce rôle.",
            "manquant": []
        }
        res1 = client.post("/api/evaluate", json={
            "question_id": "q_test",
            "reponse_eleve": "L'ARN polymérase s'occupe de la transcription de l'ADN en ARNm.",
            "tentative": 1
        })
        print_result("Test 1 - Résultat", res1.json())

    # TEST 2: Cas Faux (Erreur conceptuelle)
    print("\n--- TEST 2: Cas Faux (Erreur conceptuelle) ---")
    with patch('services.llm.call_gpt4o_evaluator') as mock_llm:
        mock_llm.return_value = {
            "score": 2,
            "statut": "FAUX",
            "feedback": "Les anticorps ne détruisent pas. Quelle est la bonne action ?",
            "manquant": ["neutralisation"]
        }
        res2 = client.post("/api/evaluate", json={
            "question_id": "q_test",
            "reponse_eleve": "les anticorps détruisent les antigènes",
            "tentative": 1
        })
        print_result("Test 2 - Résultat", res2.json())

    # TEST 3: Fallback Forcé (Simulation crash OpenAI)
    print("\n--- TEST 3: Fallback Forcé ---")
    with patch('services.llm.call_gpt4o_evaluator') as mock_llm:
        # On force une exception pour déclencher le fallback L2
        mock_llm.side_effect = Exception("Timeout API OpenAI")
        
        res3 = client.post("/api/evaluate", json={
            "question_id": "q_test",
            # On donne une réponse qui a un des mots clés mais pas tous, pour tester fallback L2
            "reponse_eleve": "C'est la transcription.",
            "tentative": 1
        })
        print_result("Test 3 - Résultat", res3.json())

if __name__ == "__main__":
    run_tests()
    
    # Exécuter les nouveaux tests unitaires de régression
    print("\n" + "="*50)
    print("Démarrage des tests de régression unitaires")
    print("="*50)
    
    import numpy as np
    from datetime import date
    from unittest.mock import patch, MagicMock
    from services.fallback_v2 import L2Evaluator
    from services.fsrs_config import get_fsrs_scheduler
    from services.embedder import KhawarizmiEmbedder
    from sentence_transformers import SentenceTransformer

    MOCK_CONCEPT_DB = {
        "q_enzyme_structure_01": {
            "question_id": "q_enzyme_structure_01",
            "texte": "Expliquez la structure de l'enzyme.",
            "reponse_attendue": "L'enzyme a une structure tertiaire avec un site actif.",
            "concepts_requis": ["structure_tertiaire", "site_actif"]
        },
        "q_ph_enzyme_01": {
            "question_id": "q_ph_enzyme_01",
            "texte": "Quel est l'effet du pH sur l'enzyme ?",
            "reponse_attendue": "Le pH modifie l'état d'ionisation des acides aminés du site actif.",
            "concepts_requis": ["ph", "site_actif"]
        }
    }

    class TestL2Evaluator:
        """Tests de régression pour le fallback L2"""
        
        def test_arabic_synonym_normalization(self):
            """
            La réponse en arabe avec tashkeel doit matcher 
            le terme de référence sans tashkeel.
            """
            evaluator = L2Evaluator(concept_db=MOCK_CONCEPT_DB)
            result = evaluator.evaluate(
                student_answer="الإنزيمُ بروتينٌ ذو بنيةٍ ثلاثيةٍ",  # Avec tashkeel
                question_id="q_enzyme_structure_01"
            )
            # Le terme "بنية ثلاثية" (sans tashkeel) doit être matché
            assert "structure_tertiaire" in result["concepts_trouves"]
            assert "structure_tertiaire" not in result["missing_concepts"]
        
        def test_ambiguous_score_enqueues_l1_review(self):
            """Un score entre 0.35 et 0.70 doit déclencher l'enfilage L1."""
            evaluator = L2Evaluator(concept_db=MOCK_CONCEPT_DB)
            result = evaluator.evaluate(
                student_answer="L'enzyme a une structure tertiaire mais sans site actif.",
                question_id="q_enzyme_structure_01"
            )
            assert result["needs_l1_review"] is True
            assert 0.35 <= (result["score"] / 10.0) < 0.70

        def test_embedding_quality_vs_sentence_transformers(self):
            """
            L'embedding ONNX INT8 doit rester à > 97% de corrélation
            avec l'embedding sentence-transformers de référence.
            """
            st_embedder = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            onnx_embedder = KhawarizmiEmbedder()
            
            test_phrases = [
                "La dénaturation d'une enzyme modifie son site actif",
                "تغير درجة الحموضة يؤثر على التركيب الثلاثي للإنزيم"
            ]
            st_embs = st_embedder.encode(test_phrases, normalize_embeddings=True)
            onnx_embs = onnx_embedder.encode(test_phrases)
            
            correlations = [
                float(np.dot(st_embs[i], onnx_embs[i])) 
                for i in range(len(test_phrases))
            ]
            assert all(c > 0.97 for c in correlations), \
                f"Dégradation trop importante : {correlations}"

    class TestFSRSConfig:
        def test_phase_transitions(self):
            """Vérifier les seuils de changement de phase."""
            # Phase 1 : Septembre - Mars (ex: 2026-02-15) -> desired_retention = 0.82
            with patch('services.fsrs_config.date') as mock_date:
                mock_date.today.return_value = date(2026, 2, 15)
                # S'assurer que les appels à date(...) fonctionnent normalement
                mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
                scheduler = get_fsrs_scheduler()
                assert scheduler.desired_retention == 0.82
            
            # Phase 2 : Avril - Mai (ex: 2026-04-15) -> desired_retention = 0.87
            with patch('services.fsrs_config.date') as mock_date:
                mock_date.today.return_value = date(2026, 4, 15)
                mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
                scheduler = get_fsrs_scheduler()
                assert scheduler.desired_retention == 0.87
            
            # Phase 3 : Juin (ex: 2026-06-01) -> desired_retention = 0.90
            with patch('services.fsrs_config.date') as mock_date:
                mock_date.today.return_value = date(2026, 6, 1)
                mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
                scheduler = get_fsrs_scheduler()
                assert scheduler.desired_retention == 0.90

    # Exécution
    try:
        t1 = TestL2Evaluator()
        t1.test_arabic_synonym_normalization()
        t1.test_ambiguous_score_enqueues_l1_review()
        t1.test_embedding_quality_vs_sentence_transformers()
        print("[OK] TestL2Evaluator passes avec succes !")
        
        t2 = TestFSRSConfig()
        t2.test_phase_transitions()
        print("[OK] TestFSRSConfig passes avec succes !")
    except AssertionError as e:
        print(f"[FAIL] Echec d'un test d'assertion: {e}")
        import traceback
        traceback.print_exc()
        raise e
    except Exception as e:
        print(f"[FAIL] Erreur lors de l'execution des tests: {e}")
        raise e

