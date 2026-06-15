"""Create lexique_termes table and import JSON data."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import get_settings
from sqlalchemy import create_engine, text

SETTINGS = get_settings()
ENGINE = create_engine(SETTINGS.DATABASE_URL)

JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                         "data", "lexique_svt_terminale_complet.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    lexique = json.load(f)

def create_table():
    with ENGINE.connect() as conn:
        res = conn.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables "
                 "WHERE table_name = 'lexique_termes')")
        )
        if res.scalar():
            print("Table lexique_termes already exists")
            return
        conn.execute(text("""
            CREATE TABLE lexique_termes (
                id VARCHAR(50) PRIMARY KEY,
                terme_fr VARCHAR(255) NOT NULL,
                terme_ar VARCHAR(255) NOT NULL,
                abreviation VARCHAR(50),
                type VARCHAR(50) NOT NULL,
                definition_fr TEXT NOT NULL,
                definition_ar TEXT NOT NULL,
                synonymes_fr TEXT[],
                synonymes_ar TEXT[],
                importance VARCHAR(20) NOT NULL DEFAULT 'moyenne',
                bac_frequent BOOLEAN NOT NULL DEFAULT false,
                chapitre_principal VARCHAR(100) NOT NULL,
                micro_concept_id VARCHAR(50),
                exemples_contexte TEXT[],
                termes_lies TEXT[],
                tags TEXT[],
                categorie_id VARCHAR(50),
                categorie_fr VARCHAR(255),
                categorie_ar VARCHAR(255),
                domaine_id VARCHAR(50),
                domaine_fr VARCHAR(255),
                domaine_ar VARCHAR(255),
                donnees_brutes JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        conn.execute(text("CREATE INDEX ix_lexique_terme_fr ON lexique_termes (terme_fr)"))
        conn.execute(text("CREATE INDEX ix_lexique_type ON lexique_termes (type)"))
        conn.execute(text("CREATE INDEX ix_lexique_chapitre ON lexique_termes (chapitre_principal)"))
        conn.execute(text("CREATE INDEX ix_lexique_micro_concept ON lexique_termes (micro_concept_id)"))
        conn.execute(text("CREATE INDEX ix_lexique_domaine ON lexique_termes (domaine_id)"))
        conn.execute(text("CREATE INDEX ix_lexique_search ON lexique_termes (importance, chapitre_principal, type)"))
        conn.commit()
        print("Table lexique_termes created successfully")

def import_data():
    rows = []
    for dom in lexique["domaines"]:
        for cat in dom["categories"]:
            for t in cat["termes"]:
                rows.append(dict(
                    id=t["id"],
                    terme_fr=t["terme_fr"],
                    terme_ar=t["terme_ar"],
                    abreviation=t.get("abreviation"),
                    type=t["type"],
                    definition_fr=t["definition_fr"],
                    definition_ar=t["definition_ar"],
                    synonymes_fr=t.get("synonymes_fr") or [],
                    synonymes_ar=t.get("synonymes_ar") or [],
                    importance=t["importance"],
                    bac_frequent=t["bac_frequent"],
                    chapitre_principal=t["chapitre_principal"],
                    micro_concept_id=t.get("micro_concept_id"),
                    exemples_contexte=t.get("exemples_contexte") or [],
                    termes_lies=t.get("termes_lies") or [],
                    tags=t.get("tags") or [],
                    categorie_id=cat["id"],
                    categorie_fr=cat["nom_fr"],
                    categorie_ar=cat["nom_ar"],
                    domaine_id=dom["id"],
                    domaine_fr=dom["nom_fr"],
                    domaine_ar=dom["nom_ar"],
                    donnees_brutes=json.dumps(t, ensure_ascii=False),
                ))

    with ENGINE.connect() as conn:
        total = len(rows)
        for i, row in enumerate(rows):
            conn.execute(text("""
                INSERT INTO lexique_termes (
                    id, terme_fr, terme_ar, abreviation, type,
                    definition_fr, definition_ar, synonymes_fr, synonymes_ar,
                    importance, bac_frequent, chapitre_principal, micro_concept_id,
                    exemples_contexte, termes_lies, tags,
                    categorie_id, categorie_fr, categorie_ar,
                    domaine_id, domaine_fr, domaine_ar, donnees_brutes
                ) VALUES (
                    :id, :terme_fr, :terme_ar, :abreviation, :type,
                    :definition_fr, :definition_ar, :synonymes_fr, :synonymes_ar,
                    :importance, :bac_frequent, :chapitre_principal, :micro_concept_id,
                    :exemples_contexte, :termes_lies, :tags,
                    :categorie_id, :categorie_fr, :categorie_ar,
                    :domaine_id, :domaine_fr, :domaine_ar, CAST(:donnees_brutes AS jsonb)
                ) ON CONFLICT (id) DO UPDATE SET
                    terme_fr = EXCLUDED.terme_fr,
                    terme_ar = EXCLUDED.terme_ar,
                    definition_fr = EXCLUDED.definition_fr,
                    definition_ar = EXCLUDED.definition_ar,
                    importance = EXCLUDED.importance,
                    bac_frequent = EXCLUDED.bac_frequent,
                    updated_at = NOW()
            """), row)
            if (i + 1) % 50 == 0:
                print(f"  Imported {i + 1}/{total}")
        conn.commit()
        print(f"  Imported {total}/{total}")

        # Verify
        result = conn.execute(text("SELECT COUNT(*) FROM lexique_termes"))
        count = result.scalar()
        print(f"\nTotal rows in DB: {count}")

if __name__ == "__main__":
    print("Creating table...")
    create_table()
    print("\nImporting data...")
    import_data()
    print("\nDone!")
