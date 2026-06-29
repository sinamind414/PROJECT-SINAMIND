"""
scripts/extract_concepts_from_programme.py — Extrait les concepts du programme officiel.

Lit programme_national_svt_claude_opus.md, détecte les headers de concept
(### X.Y — concept), filtre les sections non-conceptuelles (exercices/réponses/
résumés), et extrait pour chaque concept :
  - label (titre sans numéro/emoji/parenthèses)
  - unité / domaine
  - définition (priorité : bloc > تعريف explicite, sinon premier paragraphe
    en ignorant tableaux/séparateurs/callouts/code)

Sortie : data/micro_concepts.json — liste de :
  {
    "id": "mc_<n>",
    "label": "الجين (Gène)",
    "definition": "الجين هو قطعة من الـ ADN ...",
    "unit": "الوحدة 1: ...",
    "domain": "المجال الأول: ...",
    "unit_slug": "u_1",
    "source": "programme_officiel_svt"
  }
"""

import json
import re
import unicodedata
from pathlib import Path

PROGRAMME_PATH = Path(__file__).resolve().parent.parent / "data" / "courses" / "programme_national_svt_claude_opus.md"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "micro_concepts.json"

RE_DOMAIN = re.compile(r"^# 📗 (المجال[^:]*):?\s*(.*)$")
RE_UNIT = re.compile(r"^# (?:🧬|🌿|⚡|🌍|🌋|🧪|🔬|🧠|💪|🩸) (الوحدة[^:]*):\s*(.*?)\s*(?:\([^)]*\))?\s*$")
RE_CONCEPT = re.compile(r"^### (\d+\.\d+)\s*[—–-]\s*(.+)$")
# Sections non-conceptuelles à exclure ( exercices, réponses, résumés, etc. )
_NON_CONCEPT_EMOJIS = ("🔵", "🟡", "🔴", "✅", "📖", "📝", "💡", "📋", "🔧", "🎯")


def slugify(value: str) -> str:
    nf = unicodedata.normalize("NFKD", value)
    s = "".join(c for c in nf if not unicodedata.combining(c))
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()
    return s or "unit"


def _clean_label(raw: str) -> str:
    """Nettoie le label : supprime emoji, parenthèses vides, espaces."""
    s = raw.strip()
    # Supprimer les emojis au début
    for emoji in _NON_CONCEPT_EMOJIS:
        s = s.replace(emoji, "")
    # Supprimer les parenthèses vides restantes
    s = re.sub(r"\(\s*\)", "", s)
    return s.strip()


def _extract_definition(lines: list[str], start_idx: int) -> str:
    """Extrait la définition d'un concept.

    Priorité 1 : bloc > ... تعريف ... ( explicit definition )
    Priorité 2 : premier paragraphe de texte ( ignorant tableaux/code/séparateurs )
    """
    i = start_idx
    n = len(lines)

    # ── Priorité 1 : chercher un bloc > تعريف ──
    for j in range(i, min(i + 20, n)):
        s = lines[j].strip()
        if s.startswith("### ") or s.startswith("# ") or s == "---":
            break
        if s.startswith(">") and "تعريف" in s:
            # Extraire le texte après > et **تعريف**:
            text = s.lstrip("> ").strip()
            text = re.sub(r"^\*\*تعريف\*\*\s*:?\s*", "", text)
            text = text.strip("*").strip()
            if len(text) >= 25:
                return text

    # ── Priorité 2 : premier paragraphe de texte propre ──
    in_code = False
    for j in range(i, min(i + 30, n)):
        raw = lines[j].strip()
        if raw.startswith("### ") or raw.startswith("# ") or raw == "---":
            break
        # Ignorer les blocs de code
        if raw.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        # Ignorer les tableaux
        if raw.startswith("|") or raw.startswith("╔") or raw.startswith("╠") or raw.startswith("╚") or raw.startswith("┌") or raw.startswith("├") or raw.startswith("└") or raw.startswith("│") or raw.startswith("║"):
            continue
        # Ignorer les séparateurs
        if raw.startswith("---") or raw.startswith("===") or raw.startswith("═══"):
            continue
        # Ignorer les callouts/lignes vides
        if not raw or raw.startswith(">") or raw.startswith("!["):
            continue
        # Ignorer les listes qui ne sont pas des définitions
        if raw.startswith("- ") or raw.startswith("* "):
            continue
        # C'est un paragraphe de texte
        text = raw.strip("*").strip()
        if len(text) >= 25:
            return text

    return ""


def extract_concepts():
    if not PROGRAMME_PATH.exists():
        raise FileNotFoundError(f"Programme introuvable : {PROGRAMME_PATH}")

    raw = PROGRAMME_PATH.read_text(encoding="utf-8")
    lines = raw.split("\n")

    items = []
    current_domain = ""
    current_unit = ""
    current_unit_slug = "unit"
    global_counter = 0

    i = 0
    n = len(lines)
    while i < n:
        stripped = lines[i].strip()

        m_dom = RE_DOMAIN.match(stripped)
        if m_dom:
            current_domain = stripped.lstrip("# ").strip()
            i += 1
            continue
        m_unit = RE_UNIT.match(stripped)
        if m_unit:
            current_unit = stripped.lstrip("# ").strip()
            slug_src = re.sub(r"^[^\u0600-\u06ff]+", "", current_unit)
            slug_src = re.sub(r"\([^)]*\)", "", slug_src).strip()
            current_unit_slug = "u_" + slugify(slug_src)
            i += 1
            continue

        m_concept = RE_CONCEPT.match(stripped)
        if m_concept:
            # Filtrer les sections non-conceptuelles
            if any(emoji in stripped for emoji in _NON_CONCEPT_EMOJIS):
                i += 1
                continue

            label = _clean_label(m_concept.group(2))
            if not label:
                i += 1
                continue

            definition = _extract_definition(lines, i + 1)

            global_counter += 1
            items.append({
                "id": f"mc_{global_counter:03d}",
                "label": label,
                "definition": definition,
                "unit": current_unit,
                "domain": current_domain,
                "unit_slug": current_unit_slug,
                "source": "programme_officiel_svt",
            })
            i += 1
            continue

        i += 1

    return items


def main():
    items = extract_concepts()
    with_def = sum(1 for item in items if len(item["definition"]) >= 25)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[OK] {len(items)} concepts extraits, {with_def} avec definition exploitable -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
