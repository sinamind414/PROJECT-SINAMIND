# -*- coding: utf-8 -*-
"""
scripts/precompute_embeddings.py - Pré-calcule et stocke les embeddings dans PostgreSQL.
"""

import os
import sys
import json
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importations des composants du backend
from main import get_settings
from services.questions import questions_db
from services.embedder import embedder

async def precompute_and_store():
    # Charger la configuration
    cfg = get_settings()
    db_url = cfg.database_url
    if not db_url:
        db_url = os.getenv("DATABASE_URL")
        
    if not db_url:
        print("Error: DATABASE_URL not set in environment or settings.")
        return
        
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
    print(f"Connecting to database...")
    engine = create_async_engine(db_url, echo=False)
    
    # Calculer le nombre attendu d'embeddings dans la source
    num_annales_ref = 0
    for q_id, q_data in questions_db.items():
        reponses_ref = q_data.get("reponses_reference", [])
        if not reponses_ref and "reponse_attendue" in q_data:
            reponses_ref = [q_data["reponse_attendue"]]
        num_annales_ref += len(reponses_ref)
        
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    exercises_path = os.path.join(base_dir, "corpus", "sciences_bac_exercices.json")
    num_exercises = 0
    if os.path.exists(exercises_path):
        try:
            with open(exercises_path, "r", encoding="utf-8") as f:
                exercices = json.load(f)
                for ex in exercices:
                    if ex.get("reponse_attendue") and ex.get("id"):
                        num_exercises += 1
        except Exception as e:
            print(f"Warning: Could not read exercises to count them: {e}")
            
    expected_minimum = int((num_annales_ref + num_exercises) * 0.90)
    
    # Vérification si les embeddings sont déjà précalculés
    async with engine.connect() as conn:
        try:
            res = await conn.execute(text("SELECT COUNT(*) FROM reference_embeddings"))
            count = res.scalar()
            if count is not None and count >= expected_minimum:
                print(f"Embeddings are already precomputed ({count} rows found in DB, expected minimum: {expected_minimum}). Skipping computation.")
                await engine.dispose()
                return
            else:
                print(f"Precomputation required: only {count} rows in DB, expected at least {expected_minimum}.")
        except Exception as e:
            print(f"Table reference_embeddings not checkable (it may be created during automatic migration): {e}")
            
    async with engine.begin() as conn:
        # 1. Traitement des annales (réponses de référence)
        print("Processing annales questions from database...")
        annales_count = 0
        for q_id, q_data in questions_db.items():
            reponses_ref = q_data.get("reponses_reference", [])
            if not reponses_ref and "reponse_attendue" in q_data:
                reponses_ref = [q_data["reponse_attendue"]]
                
            if not reponses_ref:
                continue
                
            # Calcul des embeddings (batch pour cette question)
            embeddings = embedder.encode(reponses_ref)
            
            for i, (text_val, emb) in enumerate(zip(reponses_ref, embeddings)):
                await conn.execute(
                    text("""
                        INSERT INTO reference_embeddings 
                            (question_id, variant_index, reference_text, embedding, source)
                        VALUES (:qid, :vidx, :text, :emb::vector, 'annales')
                        ON CONFLICT (question_id, variant_index) 
                        DO UPDATE SET 
                            reference_text = EXCLUDED.reference_text,
                            embedding = EXCLUDED.embedding,
                            updated_at = NOW()
                    """),
                    {
                        "qid": q_id,
                        "vidx": i,
                        "text": text_val,
                        "emb": str(emb.tolist())
                    }
                )
            annales_count += 1
            
        print(f"Successfully processed {annales_count} questions from annales.")
        
        # 2. Traitement des exercices (réponses attendues)
        print("Processing exercises...")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        exercises_path = os.path.join(base_dir, "corpus", "sciences_bac_exercices.json")
        
        if os.path.exists(exercises_path):
            with open(exercises_path, "r", encoding="utf-8") as f:
                exercices = json.load(f)
                
            batch_size = 32
            exercice_texts = []
            exercice_ids = []
            
            for ex in exercices:
                if ex.get("reponse_attendue") and ex.get("id"):
                    exercice_texts.append(ex["reponse_attendue"])
                    exercice_ids.append(ex["id"])
                    
            print(f"Encoding {len(exercice_texts)} exercises in batches of {batch_size}...")
            
            for i in range(0, len(exercice_texts), batch_size):
                batch_ids = exercice_ids[i:i+batch_size]
                batch_texts = exercice_texts[i:i+batch_size]
                batch_embeddings = embedder.encode(batch_texts)
                
                for eid, text_val, emb in zip(batch_ids, batch_texts, batch_embeddings):
                    await conn.execute(
                        text("""
                            INSERT INTO reference_embeddings 
                                (question_id, variant_index, reference_text, embedding, source)
                            VALUES (:qid, 0, :text, :emb::vector, 'exercices')
                            ON CONFLICT (question_id, variant_index)
                            DO UPDATE SET 
                                reference_text = EXCLUDED.reference_text,
                                embedding = EXCLUDED.embedding,
                                updated_at = NOW()
                        """),
                        {
                            "qid": eid,
                            "text": text_val,
                            "emb": str(emb.tolist())
                        }
                    )
            print(f"Successfully processed {len(exercice_texts)} exercises.")
        else:
            print(f"Warning: Exercises file not found at {exercises_path}")

    await engine.dispose()
    print("Database connection closed. Precomputation completed.")

if __name__ == "__main__":
    asyncio.run(precompute_and_store())
