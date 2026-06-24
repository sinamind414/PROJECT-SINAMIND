-- 006_fsrs_graph.sql
-- Table des micro-concepts avec état FSRS

-- 1. S'assurer que la table de base existe
CREATE TABLE IF NOT EXISTS mastery_micro_concepts (
    id              BIGSERIAL PRIMARY KEY,
    user_id         INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    concept_id      VARCHAR(100),
    chapter         VARCHAR(50),
    stability       FLOAT DEFAULT 0.0,
    difficulty      FLOAT DEFAULT 0.0,
    reps            INT DEFAULT 0,
    lapses          INT DEFAULT 0,
    state           SMALLINT DEFAULT 0,
    due_date        TIMESTAMPTZ DEFAULT NOW(),
    last_review     TIMESTAMPTZ,
    total_reviews   INT DEFAULT 0,
    avg_score       FLOAT DEFAULT 0.0,
    streak          INT DEFAULT 0,
    UNIQUE(user_id, concept_id)
);

-- 2. Ajouter les colonnes manquantes si la table a été créée par 003_create_mastery.sql
ALTER TABLE mastery_micro_concepts ADD COLUMN IF NOT EXISTS concept_id VARCHAR(100);
ALTER TABLE mastery_micro_concepts ADD COLUMN IF NOT EXISTS chapter VARCHAR(50);
ALTER TABLE mastery_micro_concepts ADD COLUMN IF NOT EXISTS reps INT DEFAULT 0;
ALTER TABLE mastery_micro_concepts ADD COLUMN IF NOT EXISTS lapses INT DEFAULT 0;
ALTER TABLE mastery_micro_concepts ADD COLUMN IF NOT EXISTS state SMALLINT DEFAULT 0;
ALTER TABLE mastery_micro_concepts ADD COLUMN IF NOT EXISTS due_date TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE mastery_micro_concepts ADD COLUMN IF NOT EXISTS last_review TIMESTAMPTZ;
ALTER TABLE mastery_micro_concepts ADD COLUMN IF NOT EXISTS total_reviews INT DEFAULT 0;
ALTER TABLE mastery_micro_concepts ADD COLUMN IF NOT EXISTS avg_score FLOAT DEFAULT 0.0;
ALTER TABLE mastery_micro_concepts ADD COLUMN IF NOT EXISTS streak INT DEFAULT 0;

-- 3. Synchronisation et compatibilité ascendante
-- Recopier micro_concept_id vers concept_id s'il est vide
UPDATE mastery_micro_concepts SET concept_id = micro_concept_id WHERE concept_id IS NULL AND micro_concept_id IS NOT NULL;
-- Recopier prochaine_revision vers due_date s'il est vide
UPDATE mastery_micro_concepts SET due_date = prochaine_revision WHERE due_date IS NULL AND prochaine_revision IS NOT NULL;

-- Tenter de renseigner le chapitre à partir de la table micro_concepts
UPDATE mastery_micro_concepts mmc
SET chapter = mc.chapitre_id
FROM micro_concepts mc
WHERE mmc.concept_id = mc.id AND mmc.chapter IS NULL;

-- S'assurer qu'il y a une contrainte unique sur (user_id, concept_id)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_mastery_micro_concepts_user_concept'
    ) THEN
        ALTER TABLE mastery_micro_concepts ADD CONSTRAINT uq_mastery_micro_concepts_user_concept UNIQUE (user_id, concept_id);
    END IF;
END $$;

-- 4. Index pour la requête "quels concepts réviser aujourd'hui"
CREATE INDEX IF NOT EXISTS idx_due_user ON mastery_micro_concepts (user_id, due_date);

-- Table du graphe de dépendances (statique, chargée au déploiement)
CREATE TABLE IF NOT EXISTS concept_prerequisites (
    concept_id      VARCHAR(100) NOT NULL,
    prerequisite_id VARCHAR(100) NOT NULL,
    strength        FLOAT DEFAULT 1.0,  -- Force de la dépendance (0.0 - 1.0)
    PRIMARY KEY (concept_id, prerequisite_id)
);

-- Table de mapping question → concepts
CREATE TABLE IF NOT EXISTS question_concept_mapping (
    question_id     VARCHAR(100) NOT NULL,
    concept_id      VARCHAR(100) NOT NULL,
    weight          FLOAT NOT NULL,  -- Poids du concept dans cette question (0.0 - 1.0)
    PRIMARY KEY (question_id, concept_id)
);

-- Vue matérialisée : état de maîtrise par chapitre
CREATE MATERIALIZED VIEW IF NOT EXISTS mastery_by_chapter AS
SELECT 
    user_id,
    chapter,
    COUNT(*) as total_concepts,
    COUNT(*) FILTER (WHERE stability > 10.0 AND streak >= 3) as mastered,
    COUNT(*) FILTER (WHERE state = 0) as not_started,
    AVG(stability) as avg_stability,
    MIN(due_date) as next_review_due
FROM mastery_micro_concepts
WHERE chapter IS NOT NULL
GROUP BY user_id, chapter;

-- Index unique requis pour pouvoir faire REFRESH MATERIALIZED VIEW CONCURRENTLY
CREATE UNIQUE INDEX IF NOT EXISTS idx_mastery_by_chapter_user_chap ON mastery_by_chapter (user_id, chapter);
