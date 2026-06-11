-- migrations/011_create_concept_graph.sql
-- Dépendances : migrations/001_create_users.sql, migrations/002_create_micro_concepts.sql, migrations/006_fsrs_graph.sql

-- 1. S'assurer que les colonnes additionnelles de micro_concepts existent
ALTER TABLE micro_concepts ADD COLUMN IF NOT EXISTS code VARCHAR(64);
ALTER TABLE micro_concepts ADD COLUMN IF NOT EXISTS chapter VARCHAR(32);
ALTER TABLE micro_concepts ADD COLUMN IF NOT EXISTS label_fr TEXT;
ALTER TABLE micro_concepts ADD COLUMN IF NOT EXISTS label_ar TEXT;

-- Remplir temporairement code avec id si vide
UPDATE micro_concepts SET code = id WHERE code IS NULL;

-- Ajouter une contrainte unique sur code pour permettre des clés étrangères (uniquement si elle n'existe pas)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_micro_concepts_code'
    ) THEN
        ALTER TABLE micro_concepts ADD CONSTRAINT uq_micro_concepts_code UNIQUE (code);
    END IF;
END $$;

-- 2. Création de la table pivot question_concept_map
CREATE TABLE IF NOT EXISTS question_concept_map (
    question_id   VARCHAR(100) NOT NULL,
    micro_concept VARCHAR(64) REFERENCES micro_concepts(code) ON DELETE CASCADE,
    weight        FLOAT NOT NULL DEFAULT 1.0
        CONSTRAINT weight_range CHECK (weight > 0 AND weight <= 1),
    PRIMARY KEY (question_id, micro_concept)
);

-- 3. Ajout de penalty_factor à concept_prerequisites
ALTER TABLE concept_prerequisites ADD COLUMN IF NOT EXISTS penalty_factor FLOAT DEFAULT 0.15;

-- 4. Recopie des données existantes pour compatibilité ascendante
INSERT INTO question_concept_map (question_id, micro_concept, weight)
SELECT question_id, concept_id, weight 
FROM question_concept_mapping
ON CONFLICT DO NOTHING;
