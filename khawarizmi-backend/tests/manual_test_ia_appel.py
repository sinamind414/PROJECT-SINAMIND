"""
test_ia_appel.py — Test du pipeline complet Khawarizmi
Usage : python test_ia_appel.py
"""

import asyncio
import os
import json
import time
import logging
import pytest
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv
from services.khawarizmi_engine import KhawarizmiTutor

@pytest.fixture
def tutor():
    """Create a KhawarizmiTutor instance for tests."""
    # Determine data directory; default matches script's default
    data_dir = os.getenv(
        "DATA_DIR",
        str(Path(__file__).parent.parent / "LIVRES SCOLAIRES")
    )
    return KhawarizmiTutor(data_dir=data_dir)

# ═══ CONFIGURATION LOGGING ══════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger('test_ia_appel')

# ═══ CHARGEMENT ENV ══════════════════════════════════════
load_dotenv()

API_KEY  = os.environ.get("GEMINI_API_KEY", "AIzaSy...COLLE_TA_CLE_ICI")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
MODEL    = os.environ.get("OPENAI_MODEL", "gemini-2.5-flash")
COUT_PAR_TOKEN = 0.0  # Gratuit pour tester

client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)

# ═══ CHEMIN DONNÉES ═══════════════════════════════════════
DATA_DIR = os.environ.get(
    "DATA_DIR",
    str(Path(__file__).parent.parent / "LIVRES SCOLAIRES")
)

# ═══ SCÉNARIOS DE TEST ════════════════════════════════════
SCENARIOS = [
    {
        "nom":         "Récurrence — Erreur d'omission (TYPE_4)",
        "sujet_id":    "BAC_MATH_2024_SC_S1_EX1",
        "question_id": "Q1",
        "input":       "Pour n=0 on a U0=1 donc c'est vrai. Ensuite on suppose que Un est entre 0 et 1. La limite est 1 donc c'est bon.",
        "mode":        "ANNALES_COMPLEXES",
        "erreur_attendue": "TYPE_4"  # Oublie l'étape d'hérédité
    },
    {
        "nom":         "Probabilités — Somme != 1 (TYPE_3)",
        "sujet_id":    "BAC_MATH_2024_SC_S1_EX2",
        "question_id": "Q1_a",
        "input":       "P(A)=1/4, P(B)=2/4, P(C)=1/4",
        "mode":        "RAPPEL_ACTIF",
        "erreur_attendue": "TYPE_3"
    },
]


async def tester_scenario(tutor: KhawarizmiTutor, scenario: dict) -> dict:
    """Exécute un scénario de test et retourne les métriques."""

    print(f"\n{'='*60}")
    print(f"🧪 SCÉNARIO : {scenario['nom']}")
    print(f"{'='*60}")

    # ── Étape 1 : Pré-analyse sans IA ──────────────────────
    print("\n🔍 1. PRÉ-ANALYSE (SANS IA)...")
    pre_analyse = tutor.pre_analyser_sans_ia(
        scenario['sujet_id'],
        scenario['question_id'],
        scenario['input']
    )
    if pre_analyse:
        print(f"   ✅ Erreur détectée : {pre_analyse.get('diagnostic')}")
        print(f"   💰 Économie tokens : {pre_analyse.get('economie_tokens', 0)}")
    else:
        print("   ℹ️  Aucune erreur détectée par pré-analyse")

    # ── Étape 2 : Construction du prompt ───────────────────
    print("\n🧠 2. CONSTRUCTION DU PROMPT SOCRATIQUE...")
    try:
        system_prompt = tutor.build_system_prompt(
            sujet_id     = scenario['sujet_id'],
            question_id  = scenario['question_id'],
            student_input= scenario['input'],
            pre_analyse  = pre_analyse,
            mode_force   = scenario['mode']
        )
        print(f"   ✅ Prompt construit : {len(system_prompt)} caractères")
        print(f"\n   --- APERÇU PROMPT (300 chars) ---")
        print(f"   {system_prompt[:300]}...")
    except ValueError as e:
        print(f"   ❌ Erreur construction prompt : {e}")
        return {"succes": False, "erreur": str(e)}

    # ── Étape 3 : Appel IA ─────────────────────────────────
    print(f"\n🌐 3. APPEL {MODEL} EN COURS...")
    start = time.perf_counter()

    try:
        response = await client.chat.completions.create(
            model           = MODEL,
            messages        = [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": scenario['input']}
            ],
            temperature     = 0.3,
            max_tokens      = 500,
            timeout         = 30.0
        )

        elapsed = time.perf_counter() - start
        content = response.choices[0].message.content

        content = content.strip()
        if content.startswith("```"):
            lines = content.splitlines()
            if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].startswith("```"):
                content = "\n".join(lines[1:-1]).strip()

        # ── Étape 4 : Validation JSON ──────────────────────
        try:
            result = json.loads(content)
            json_valide = True
        except json.JSONDecodeError as jde:
            print(f"   [JSONDecodeError] raw content: {repr(content)}")
            print(f"   [JSONDecodeError] error message: {jde}")
            result      = {}
            json_valide = False

        # ── Étape 5 : Métriques ────────────────────────────
        tokens_in  = response.usage.prompt_tokens
        tokens_out = response.usage.completion_tokens
        tokens_tot = response.usage.total_tokens
        cout_estime= tokens_tot * COUT_PAR_TOKEN

        print(f"\n✅ RÉPONSE KHAWARIZMI :")
        print(f"{'─'*50}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"{'─'*50}")

        print(f"\n📊 MÉTRIQUES :")
        print(f"   ⏱️  Temps réponse  : {elapsed:.2f}s")
        print(f"   📥 Tokens entrée  : {tokens_in}")
        print(f"   📤 Tokens sortie  : {tokens_out}")
        print(f"   💰 Coût estimé    : ${cout_estime:.6f}")
        print(f"   📋 JSON valide    : {'✅' if json_valide else '❌'}")

        # ── Validation pédagogique ─────────────────────────
        type_recu    = result.get('type_erreur', 'INCONNU')
        type_attendu = scenario.get('erreur_attendue', '')
        if type_attendu:
            match = type_recu == type_attendu
            print(f"   🎯 Type erreur    : {type_recu} "
                  f"({'✅ correct' if match else f'❌ attendu {type_attendu}'})")

        return {
            "succes":       True,
            "temps":        elapsed,
            "tokens":       tokens_tot,
            "cout":         cout_estime,
            "json_valide":  json_valide,
            "type_erreur":  type_recu,
        }

    except Exception as e:
        elapsed = time.perf_counter() - start
        print(f"\n❌ ERREUR API ({elapsed:.2f}s) : {e}")
        return {"succes": False, "erreur": str(e), "temps": elapsed}


async def main():
    print("🚀 KHAWARIZMI — TEST PIPELINE COMPLET")
    print(f"   Modèle    : {MODEL}")
    print(f"   Data dir  : {DATA_DIR}")

    # ── Init tuteur ────────────────────────────────────────
    print("\n📚 CHARGEMENT DU CORPUS BAC...")
    try:
        tutor = KhawarizmiTutor(data_dir=DATA_DIR)
    except FileNotFoundError as e:
        print(f"❌ Corpus introuvable : {e}")
        print(f"   Vérifie que DATA_DIR={DATA_DIR} contient les JSON")
        return

    # ── Run scénarios ──────────────────────────────────────
    resultats = []
    for scenario in SCENARIOS:
        res = await tester_scenario(tutor, scenario)
        resultats.append(res)
        await asyncio.sleep(1)  # Respecte le rate limit API

    # ── Rapport final ──────────────────────────────────────
    print(f"\n{'='*60}")
    print("📈 RAPPORT FINAL")
    print(f"{'='*60}")

    succes     = sum(1 for r in resultats if r.get('succes'))
    cout_total = sum(r.get('cout', 0) for r in resultats)
    temps_moy  = (
        sum(r.get('temps', 0) for r in resultats if r.get('succes'))
        / max(succes, 1)
    )

    print(f"   ✅ Tests réussis   : {succes}/{len(SCENARIOS)}")
    print(f"   ⏱️  Temps moyen    : {temps_moy:.2f}s")
    print(f"   💰 Coût total     : ${cout_total:.6f}")
    print(f"   💰 Coût 1000 req  : ${cout_total/len(SCENARIOS)*1000:.4f}")

    if succes == len(SCENARIOS):
        print("\n🏆 PIPELINE OPÉRATIONNEL — Prêt pour intégration FastAPI")
    else:
        print("\n⚠️  Des erreurs subsistent — Voir détails ci-dessus")


if __name__ == "__main__":
    asyncio.run(main())
