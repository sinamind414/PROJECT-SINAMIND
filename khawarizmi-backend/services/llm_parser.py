import json
import logging
import re

logger = logging.getLogger("khawarizmi.llm_parser")


def parse_llm_json(raw: str) -> dict:
    if not raw or not raw.strip():
        raise ValueError("Réponse IA vide")
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    brace_start = text.find("{")
    if brace_start != -1:
        depth = 0
        for i, char in enumerate(text[brace_start:], start=brace_start):
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[brace_start : i + 1])
                    except json.JSONDecodeError:
                        break
    open_braces = text.count("{") - text.count("}")
    open_brackets = text.count("[") - text.count("]")
    repaired = text + ("]" * max(0, open_brackets)) + ("}" * max(0, open_braces))
    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass
    raise ValueError(f"Réponse IA non-JSON après tous les essais : {raw[:200]}")
