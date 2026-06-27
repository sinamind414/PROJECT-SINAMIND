-- 013_drop_mastery_micro_concept_fk.sql
-- Supprime la FK héritée de 003 qui bloque la sauvegarde des résultats drill.

ALTER TABLE mastery_micro_concepts
    DROP CONSTRAINT IF EXISTS mastery_micro_concepts_micro_concept_id_fkey;

-- Index utile pour le drill
CREATE INDEX IF NOT EXISTS idx_mastery_user_micro_concept
    ON mastery_micro_concepts (user_id, micro_concept_id);
