-- 007_add_pending_real_evaluation.sql
-- Ajoute la colonne pending_real_evaluation pour la réconciliation L1/L2 asynchrone

ALTER TABLE mastery_micro_concepts
    ADD COLUMN IF NOT EXISTS pending_real_evaluation BOOLEAN DEFAULT FALSE;

COMMENT ON COLUMN mastery_micro_concepts.pending_real_evaluation IS
    'Indique si l''évaluation sémantique locale nécessite une réévaluation asynchrone par L1 (GPT)';
