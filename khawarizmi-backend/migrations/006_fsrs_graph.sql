-- 006_fsrs_graph.sql
-- Table des micro-concepts avec état FSRS
CREATE TABLE IF NOT EXISTS mastery_micro_concepts (
    id              BIGSERIAL PRIMARY KEY,
    user_id         INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    concept_id      VARCHAR(100) NOT NULL,
    chapter         VARCHAR(50) NOT NULL,  -- 'ch1_proteines', 'ch3_enzymes'...
    
    -- État FSRS v4
    stability       FLOAT DEFAULT 0.0,
    difficulty      FLOAT DEFAULT 0.0,
    reps            INT DEFAULT 0,
    lapses          INT DEFAULT 0,
    state           SMALLINT DEFAULT 0,  -- 0=new, 1=learning, 2=review, 3=relearning
    due_date        TIMESTAMPTZ DEFAULT NOW(),
    last_review     TIMESTAMPTZ,
    
    -- Métadonnées d'analyse
    total_reviews   INT DEFAULT 0,
    avg_score       FLOAT DEFAULT 0.0,
    streak          INT DEFAULT 0,       -- Séquence de réussites consécutives
    
    UNIQUE(user_id, concept_id)
);

-- Index pour la requête "quels concepts réviser aujourd'hui"
CREATE INDEX IF NOT EXISTS idx_due_user ON mastery_micro_concepts (user_id, due_date) WHERE state IN (1, 2, 3);

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
-- On utilise CREATE MATERIALIZED VIEW IF NOT EXISTS
-- Note: Les vues matérialisées nécessitent d'être rafraîchies périodiquement (REFRESH MATERIALIZED VIEW)
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
GROUP BY user_id, chapter;

-- Index unique requis pour pouvoir faire REFRESH MATERIALIZED VIEW CONCURRENTLY
CREATE UNIQUE INDEX IF NOT EXISTS idx_mastery_by_chapter_user_chap ON mastery_by_chapter (user_id, chapter);
