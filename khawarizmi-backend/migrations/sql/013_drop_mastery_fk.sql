-- 013_drop_mastery_fk.sql
-- Supprimer la FK qui bloque les inserts de drill (question_id ≠ micro_concept_id)
ALTER TABLE mastery_micro_concepts
    DROP CONSTRAINT IF EXISTS mastery_micro_concepts_micro_concept_id_fkey;
