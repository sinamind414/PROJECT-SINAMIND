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

from main import get_current_user, get_db, get_scheduler, get_openai

def override_get_current_user():
    return {"id": 1, "email": "test@test.com", "prenom": "Amina", "plan": "pro"}

class MockAsyncResult:
    def fetchone(self):
        return ({"stability": 0, "difficulty": 0, "scheduled_days": 0, "reps": 0, "lapses": 0, "state": "0"},)

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
    print(json.dumps(res_json, indent=2, ensure_ascii=False))

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
