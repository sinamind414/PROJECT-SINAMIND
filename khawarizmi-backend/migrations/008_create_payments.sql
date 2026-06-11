-- 008_create_payments.sql
-- Table des paiements pour Chargily Pay

CREATE TABLE IF NOT EXISTS payments (
    id              BIGSERIAL PRIMARY KEY,
    checkout_id     VARCHAR(100) UNIQUE NOT NULL,
    user_id         INTEGER REFERENCES users(id) ON DELETE CASCADE,
    amount          FLOAT NOT NULL,
    status          VARCHAR(20) DEFAULT 'pending', -- 'pending', 'paid', 'failed'
    raw_webhook     JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    paid_at         TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour accélérer la recherche par checkout_id lors du webhook
CREATE INDEX IF NOT EXISTS idx_payments_checkout ON payments (checkout_id);
