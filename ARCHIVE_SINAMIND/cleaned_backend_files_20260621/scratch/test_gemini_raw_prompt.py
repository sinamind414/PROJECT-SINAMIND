import os
import asyncio
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.khawarizmi_engine import KhawarizmiTutor

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def main():
    data_dir = os.environ.get(
        "DATA_DIR",
        str(Path(__file__).parent.parent / "LIVRES SCOLAIRES")
    )
    tutor = KhawarizmiTutor(data_dir=data_dir)

    scenario = {
        "sujet_id":    "BAC_MATH_2024_SC_S1_EX1",
        "question_id": "Q1",
        "input":       "Pour n=0 on a U0=1 donc c'est vrai. Ensuite on suppose que Un est entre 0 et 1. La limite est 1 donc c'est bon.",
        "mode":        "ANNALES_COMPLEXES",
    }

    # ── Étape 1 : Pré-analyse sans IA ──────────────────────
    pre_analyse = tutor.pre_analyser_sans_ia(
        scenario['sujet_id'],
        scenario['question_id'],
        scenario['input']
    )

    # ── Étape 2 : Construction du prompt ───────────────────
    system_prompt = tutor.build_system_prompt(
        sujet_id     = scenario['sujet_id'],
        question_id  = scenario['question_id'],
        student_input= scenario['input'],
        pre_analyse  = pre_analyse,
        mode_force   = scenario['mode']
    )

    print("=== SYSTEM PROMPT ===")
    print(system_prompt)
    print("=====================")

    api_key  = os.environ.get("GEMINI_API_KEY")
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
    model    = os.environ.get("OPENAI_MODEL", "gemini-2.5-flash")

    client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    print(f"\nCalling {model} with response_format = json_object...")
    try:
        response = await client.chat.completions.create(
            model           = model,
            messages        = [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": scenario['input']}
            ],
            temperature     = 0.3,
            timeout         = 30.0
        )
        content = response.choices[0].message.content
        print("\n=== FULL RESPONSE OBJECT ===")
        print(response)
        print("\n=== RAW CONTENT RESPONSE ===")
        print(repr(content))
        print("=============================")
    except Exception as e:
        print(f"Error during API call: {e}")

if __name__ == "__main__":
    asyncio.run(main())
