#!/usr/bin/env python3
"""
Script de migration vers les données canoniques.
"""

import re
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
TARGET_FILES = [
    "services/khawarizmi_engine.py",
    "routes/chat.py",
    "routes/programme.py",
    "main.py",
]

LEGACY_PATTERNS = [
    r"programme_sciences_3as\.json",
    r"annales_sciences_3as\.json",
    r"tutor\.programme_sciences",
]


def main():
    print("=== Migration vers données canoniques ===")
    for rel in TARGET_FILES:
        p = BASE / rel
        if p.exists():
            content = p.read_text(encoding="utf-8")
            found = False
            for pattern in LEGACY_PATTERNS:
                if re.search(pattern, content):
                    found = True
                    print(f"[!] {rel} contient encore du legacy : {pattern}")
            if not found:
                print(f"[OK] {rel}")


if __name__ == "__main__":
    main()
