-- Migration 009 : Création de la table d'embeddings de référence et son index HNSW

CREATE TABLE IF NOT EXISTS reference_embeddings (
    id              BIGSERIAL PRIMARY KEY,
    question_id     VARCHAR(255) NOT NULL,
    variant_index   SMALLINT NOT NULL DEFAULT 0,
    reference_text  TEXT NOT NULL,
    embedding       vector(384) NOT NULL,
    source          VARCHAR(20) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE (question_id, variant_index)
);

-- Index HNSW (rapide pour la similarité cosinus avec un volume faible/moyen)
CREATE INDEX IF NOT EXISTS idx_ref_embeddings_hnsw 
ON reference_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Index classique B-Tree pour filtrer rapidement par question_id
CREATE INDEX IF NOT EXISTS idx_ref_embeddings_question_id 
ON reference_embeddings (question_id);
