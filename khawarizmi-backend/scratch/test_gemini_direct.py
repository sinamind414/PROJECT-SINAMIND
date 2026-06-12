import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
    model = os.environ.get("OPENAI_MODEL", "gemini-2.5-flash")

    print(f"Testing Gemini API with model: {model}")
    print(f"Base URL: {base_url}")
    print(f"API Key: {api_key[:10]}...")

    client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    # Test 1: JSON mode WITH specific schema instructions
    print("\n--- Test 1: JSON mode with specific prompt instructions ---")
    system_prompt = """You are a helpful assistant. You must output a JSON object containing a 'reply' field.
Format:
{
  "reply": "<your response>"
}"""
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Say hello in French"}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        print("Response 1:")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Error 1: {e}")

    # Test 2: JSON mode WITHOUT specific schema instructions
    print("\n--- Test 2: JSON mode without specific schema instructions ---")
    system_prompt = "You are a helpful assistant. Answer the user's question."
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Say hello in French"}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        print("Response 2:")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Error 2: {e}")

if __name__ == "__main__":
    asyncio.run(main())
