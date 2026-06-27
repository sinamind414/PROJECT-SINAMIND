-- 014_normalize_mastery_conventions.sql
-- Normalise la table mastery_micro_concepts :
--   - micro_concept_id : identifiant métier FK vers micro_concepts(id)
--   - concept_id       : identifiant FSRS/drill (peut être ≠ micro_concept_id)
--   - Garantit que concept_id est renseigné (fallback sur micro_concept_id)

-- 1. S'assurer que concept_id est toujours rempli
UPDATE mastery_micro_concepts
SET concept_id = micro_concept_id
WHERE concept_id IS NULL OR concept_id = '';

-- 2. Index sur concept_id (utilisé par drill, session, scheduler)
CREATE INDEX IF NOT EXISTS idx_mastery_user_concept
    ON mastery_micro_concepts (user_id, concept_id);

-- 3. Index composite pour la requête FSRS critique
CREATE INDEX IF NOT EXISTS idx_mastery_user_due
    ON mastery_micro_concepts (user_id, due_date)
    WHERE pending_real_evaluation = FALSE OR pending_real_evaluation IS NULL;

-- 4. Contrainte CHECK : concept_id ne doit jamais être vide
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'chk_mastery_concept_id_not_empty'
    ) THEN
        ALTER TABLE mastery_micro_concepts
            ADD CONSTRAINT chk_mastery_concept_id_not_empty
            CHECK (concept_id IS NOT NULL AND concept_id != '');
    END IF;
END $$;

-- 5. Commentaire de documentation
COMMENT ON COLUMN mastery_micro_concepts.micro_concept_id IS
    'Identifiant métier FK vers micro_concepts(id). Utilisé par flashcards CRUD.';
COMMENT ON COLUMN mastery_micro_concepts.concept_id IS
    'Identifiant FSRS/drill. Utilisé par session queue, scheduler, reconciliation. Doit toujours être renseigné.';
