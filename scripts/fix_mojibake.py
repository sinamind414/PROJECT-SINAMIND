"""Correcteur de mojibake — répare l'arabe double-encodé (UTF-8 lu comme latin-1/cp1252).

Sûr car : seuls les tokens contenant des caractères latin-1 supplement (U+0080-U+00FF)
sont tentés en round-trip ; un round-trip réussi implique que la source était
double-encodée (un token français légitime comme "é" échoue au décodage UTF-8).
"""
import re
import sys

MOJI = re.compile(r"[\u0080-\u00ff]")
ARABIC = re.compile(r"[\u0600-\u06ff]")

# Table cp1252 : caractères Unicode spéciaux → octets (le reste = latin-1 direct).
CP_EXTRA = {
    0x20AC: 0x80, 0x201A: 0x82, 0x0192: 0x83, 0x201E: 0x84, 0x2026: 0x85,
    0x2020: 0x86, 0x2021: 0x87, 0x02C6: 0x88, 0x2030: 0x89, 0x0160: 0x8A,
    0x2039: 0x8B, 0x0152: 0x8C, 0x017D: 0x8E, 0x2018: 0x91, 0x2019: 0x92,
    0x201C: 0x93, 0x201D: 0x94, 0x2022: 0x95, 0x2013: 0x96, 0x2014: 0x97,
    0x02DC: 0x98, 0x2122: 0x99, 0x0161: 0x9A, 0x203A: 0x9B, 0x0153: 0x9C,
    0x017E: 0x9E, 0x0178: 0x9F,
}


def _to_bytes_cp1252(s: str):
    """Reconstruit le flux d'octets d'origine (avant décodage mojibake)."""
    out = bytearray()
    for c in s:
        o = ord(c)
        if o == 0xFE0F:  # sélecteur de variation (emoji) → EF B8 8F
            out += b"\xef\xb8\x8f"
        elif o <= 0xFF:
            out.append(o)  # y compris U+0081 (octet 0x81 non défini en cp1252)
        elif o in CP_EXTRA:
            out.append(CP_EXTRA[o])
        else:
            return None
    return bytes(out)


def fix_token(tok: str) -> str:
    """Round-trip du token s'il est double-encodé.

    Sûr car : un round-trip ne réussit que si TOUS les octets reconstruits
    forment un UTF-8 valide. Tout token contenant un accent latin réel
    (ex. "é" = 0xE9) échoue au décodage UTF-8 et reste intact.
    """
    if not MOJI.search(tok):
        return tok
    for enc in ("latin-1", "cp1252"):
        try:
            return tok.encode(enc).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    # Passage cp1252 manuel (gère les octets 0x81/0x8D/0x8F/0x90/0x9D non définis)
    raw = _to_bytes_cp1252(tok)
    if raw is not None:
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            pass
    return tok


def fix_text(text: str) -> tuple[str, int]:
    # NB: découpage sur espaces ASCII uniquement — U+00A0 (nbsp) peut faire
    # partie d'un émoji corrompu (ex. "ðŸ\x8f\xa0" → 🏠) et ne doit pas être
    # traité comme séparateur.
    parts = re.split(r"([ \t\r\n]+)", text)
    changed = 0
    out = []
    for p in parts:
        if p and not p.isspace():
            f = fix_token(p)
            if f != p:
                changed += 1
            p = f
        out.append(p)
    return "".join(out), changed


def main(paths: list[str]) -> None:
    total = 0
    for p in paths:
        src = open(p, encoding="utf-8").read()
        fixed, n = fix_text(src)
        open(p, "w", encoding="utf-8").write(fixed)
        total += n
        print(f"{n:>6} tokens corrigés  {p}")
    print(f"\nTotal: {total} tokens corrigés dans {len(paths)} fichiers")


if __name__ == "__main__":
    main(sys.argv[1:])
