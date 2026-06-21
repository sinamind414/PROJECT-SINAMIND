# PHASE 04 — Créer les scripts Data Pipeline

## 4.1 Créer le script Auto Tagger

**Fichier** : `khawarizmi-backend/scripts/data_pipeline/auto_tagger.py`

Crée le fichier avec le contenu du script d'auto-tagging que nous avons déjà (celui qui utilise les 42 concepts + KEYWORD_MAP).  
Si tu n'as pas la version complète, dis-le-moi et je te la donne dans un message séparé.

Contenu minimal à inclure :
- Chargement de `micro_concepts_reference.json`
- Fonction `suggest_micro_concepts(text)`
- Support `--batch`

## 4.2 Créer le script de Migration

**Fichier** : `khawarizmi-backend/scripts/data_pipeline/migrate_to_canonical.py`

Contenu :

```python
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
```

## 4.3 Créer le README du pipeline

**Fichier** : `khawarizmi-backend/scripts/data_pipeline/README.md`

Contenu simple :

```markdown
# Data Pipeline

Ce dossier contient les scripts pour construire les données propres.

Règle : Ne plus utiliser directement les anciens JSON dans `data/`.
```

**Fin de la Phase 4.**