-- Migration 010 : Ajout de la configuration FSRS par défaut pour chaque utilisateur dans la table users

ALTER TABLE users ADD COLUMN IF NOT EXISTS fsrs_config JSONB DEFAULT '{
    "desired_retention": 0.85,
    "w": [0.4072, 1.1829, 3.1262, 15.4722, 7.2102, 0.5316, 1.0651, 0.0589,
          1.4654, 0.1544, 0.9956, 1.9867, 0.1254, 0.2870, 2.2700, 0.3010,
          2.9898, 0.5100, 0.3828],
    "maximum_interval": 36500,
    "enable_fuzzing": true
}'::jsonb;
