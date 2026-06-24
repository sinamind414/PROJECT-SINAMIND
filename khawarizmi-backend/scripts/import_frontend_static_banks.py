"""
Script d'import des banques statiques TypeScript du frontend
vers les tables PostgreSQL du backend.

Lit :
  - ../../khawarizmi-frontend/src/lib/annales-bac.ts  → table annales
  - ../../khawarizmi-frontend/src/lib/methodology-documents.ts → da_scenarios, da_documents, da_questions

Usage :
  cd khawarizmi-backend && python scripts/import_frontend_static_banks.py
"""

import json
import os
import re
import sys
from datetime import UTC, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from sqlalchemy import create_engine, text
except ImportError:
    print("Installe sqlalchemy : pip install sqlalchemy psycopg2-binary")
    sys.exit(1)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_LIB = os.path.join(PROJECT_ROOT, "..", "khawarizmi-frontend", "src", "lib")
DATABASE_URL = os.environ.get("DATABASE_URL", "")


def extract_ts_array(filepath: str, var_name: str) -> list:
    """Extrait un tableau TypeScript const var_name: Type = [...] depuis un fichier."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        rf"const\s+{re.escape(var_name)}\s*:\s*\w+\s*=\s*(\[.*?\]);\s*\n",
        re.DOTALL,
    )
    match = pattern.search(content)
    if not match:
        raise ValueError(f"{var_name} non trouvé dans {filepath}")

    raw = match.group(1)
    raw = re.sub(r"//.*", "", raw)
    raw = re.sub(r"/\*.*?\*/", "", raw, flags=re.DOTALL)
    raw = re.sub(r"(?<!\w)(readonly\s+)", "", raw)
    raw = re.sub(r",\s*([}\]])", r"\1", raw)
    raw = raw.replace(r"'", '"')
    raw = re.sub(r'"(\w+)"\s*:', r"'\1':", raw)
    raw = raw.replace("'", '"')

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Erreur JSON après nettoyage : {e}")
        print(f"Extrait : {raw[:2000]}")
        raise


def import_annales(engine):
    """Importe les sujets du BAC depuis annales-bac.ts vers la table annales."""
    filepath = os.path.join(FRONTEND_LIB, "annales-bac.ts")
    if not os.path.exists(filepath):
        print(f"Fichier introuvable : {filepath}")
        return

    sujets = extract_ts_array(filepath, "SUJETS")
    print(f"Import de {len(sujets)} sujets BAC...")

    with engine.begin() as conn:
        for sujet in sujets:
            slug = sujet.get("slug", "")
            if conn.execute(
                text("SELECT 1 FROM annales WHERE slug = :slug"),
                {"slug": slug},
            ).fetchone():
                print(f"  SKIP (existe) : {slug}")
                continue

            conn.execute(
                text("""
                    INSERT INTO annales
                        (slug, annee, session, matiere, filiere, titre, titre_ar,
                         difficulte, duree, total_pages, chapitres, url_pdf, url_corrige,
                         created_at)
                    VALUES
                        (:slug, :annee, :session, :matiere, :filiere, :titre, :titre_ar,
                         :difficulte, :duree, :total_pages, :chapitres, :url_pdf, :url_corrige,
                         :created_at)
                """),
                {
                    "slug": slug,
                    "annee": sujet.get("annee"),
                    "session": sujet.get("session"),
                    "matiere": sujet.get("matiere", "SVT"),
                    "filiere": sujet.get("filiere", "Sciences Naturelles"),
                    "titre": sujet.get("titre", ""),
                    "titre_ar": sujet.get("titreAr", ""),
                    "difficulte": sujet.get("difficulte", "moyen"),
                    "duree": sujet.get("duree", 0),
                    "total_pages": sujet.get("totalPages", 0),
                    "chapitres": json.dumps(sujet.get("chapitres", [])),
                    "url_pdf": sujet.get("url_pdf", ""),
                    "url_corrige": sujet.get("url_corrige", ""),
                    "created_at": datetime.now(UTC),
                },
            )
            print(f"  IMPORTE : {slug} ({sujet.get('annee')})")

    print(f"Import annales terminé : {len(sujets)} sujets.")


def import_methodology_documents(engine):
    """Importe les scénarios depuis methodology-documents.ts."""
    filepath = os.path.join(FRONTEND_LIB, "methodology-documents.ts")
    if not os.path.exists(filepath):
        print(f"Fichier introuvable : {filepath}")
        return

    scenarios = extract_ts_array(filepath, "methodologyScenarios")
    print(f"Import de {len(scenarios)} scénarios méthodologie...")

    with engine.begin() as conn:
        for scenario in scenarios:
            sid = scenario.get("id", "")
            if conn.execute(text("SELECT 1 FROM da_scenarios WHERE id = :sid"), {"sid": sid}).fetchone():
                print(f"  SKIP (existe) : {sid}")
                continue

            conn.execute(
                text("""
                    INSERT INTO da_scenarios
                        (id, unit_key, title_ar, subtitle_ar, context_ar,
                         dominant_skills, created_at)
                    VALUES
                        (:id, :unit_key, :title_ar, :subtitle_ar, :context_ar,
                         :dominant_skills, :created_at)
                """),
                {
                    "id": sid,
                    "unit_key": scenario.get("unitKey", ""),
                    "title_ar": scenario.get("title", ""),
                    "subtitle_ar": scenario.get("subtitle", ""),
                    "context_ar": scenario.get("contextAr", ""),
                    "dominant_skills": json.dumps(scenario.get("dominantSkills", [])),
                    "created_at": datetime.now(UTC),
                },
            )

            for doc in scenario.get("documents", []):
                conn.execute(
                    text("""
                        INSERT INTO da_documents
                            (id, scenario_id, type, title, caption, content, created_at)
                        VALUES
                            (:id, :scenario_id, :type, :title, :caption, :content, :created_at)
                    """),
                    {
                        "id": doc.get("id", ""),
                        "scenario_id": sid,
                        "type": doc.get("type", ""),
                        "title": doc.get("title", ""),
                        "caption": doc.get("caption", ""),
                        "content": json.dumps(doc),
                        "created_at": datetime.now(UTC),
                    },
                )

            for q in scenario.get("questions", []):
                conn.execute(
                    text("""
                        INSERT INTO da_questions
                            (id, scenario_id, verb_slug, number, title, skill,
                             doc_ref, prompt, placeholder, model_answer, learning_focus,
                             created_at)
                        VALUES
                            (:id, :scenario_id, :verb_slug, :number, :title, :skill,
                             :doc_ref, :prompt, :placeholder, :model_answer, :learning_focus,
                             :created_at)
                    """),
                    {
                        "id": q.get("id", ""),
                        "scenario_id": sid,
                        "verb_slug": q.get("verbSlug", ""),
                        "number": q.get("n", 0),
                        "title": q.get("title", ""),
                        "skill": q.get("skill", ""),
                        "doc_ref": q.get("docRef", ""),
                        "prompt": q.get("prompt", ""),
                        "placeholder": q.get("placeholder", ""),
                        "model_answer": q.get("modelAnswer", ""),
                        "learning_focus": q.get("learningFocus", ""),
                        "created_at": datetime.now(UTC),
                    },
                )

            print(f"  IMPORTE : {sid} ({len(scenario.get('questions', []))} questions)")

    print(f"Import méthodologie terminé : {len(scenarios)} scénarios.")


def main():
    if not DATABASE_URL:
        print("Variable DATABASE_URL non définie. Utilise un .env ou exporte-la.")
        print("Mode dry-run : affiche la structure sans importer.")
        test_parsing()
        return

    engine = create_engine(DATABASE_URL)
    import_annales(engine)
    import_methodology_documents(engine)
    engine.dispose()


def test_parsing():
    """Teste l'extraction sans connexion DB."""
    filepath_annales = os.path.join(FRONTEND_LIB, "annales-bac.ts")
    filepath_methodo = os.path.join(FRONTEND_LIB, "methodology-documents.ts")

    if os.path.exists(filepath_annales):
        try:
            sujets = extract_ts_array(filepath_annales, "SUJETS")
            print(f"annales-bac.ts : {len(sujets)} sujets extraits")
            for s in sujets[:2]:
                print(f"  - {s.get('slug')} ({s.get('annee')})")
        except Exception as e:
            print(f"Erreur annales : {e}")

    if os.path.exists(filepath_methodo):
        try:
            scenarios = extract_ts_array(filepath_methodo, "methodologyScenarios")
            print(f"\nmethodology-documents.ts : {len(scenarios)} scénarios extraits")
            for s in scenarios[:2]:
                print(f"  - {s.get('id')} ({len(s.get('questions', []))} questions)")
        except Exception as e:
            print(f"Erreur méthodologie : {e}")


if __name__ == "__main__":
    main()
