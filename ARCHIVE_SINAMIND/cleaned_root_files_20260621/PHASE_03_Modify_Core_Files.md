# PHASE 03 — Modifier les fichiers Core existants

## 3.1 Modifier `khawarizmi-backend/services/khawarizmi_engine.py`

Remplace la méthode `__init__` (la partie qui commence par `def __init__(self, data_dir: str):`) par le code suivant :

```python
def __init__(self, data_dir: str):
    self.data_dir = data_dir

    # === NEW: Single Source of Truth ===
    from services.data_loader import get_data_loader
    self.loader = get_data_loader(data_dir)

    self.programme_canonical = self.loader.load_canonical_programme()
    self.annales_clean = {}
    self.lexique = {}

    # Temporary compatibility layer
    self.programme_sciences = self.programme_canonical
    self.annales_sciences = self.annales_clean
    self.lexique_complet = self.lexique

    # Legacy subjects
    self.programme_maths    = self._charger_json(data_dir, 'programme_maths_3as.json', optional=True)
    self.annales_maths      = self._charger_json(data_dir, 'annales_maths_3as.json', optional=True)
    self.programme_physique = self._charger_json(data_dir, 'programme_physique_3as.json', optional=True)

    self._index_questions        = self._construire_index()
    self._index_micro_concepts   = self._construire_index_micro_concepts()
    self._index_lexique          = self._construire_index_lexique()

    report = self.loader.get_loading_report()
    logger.info("KhawarizmiTutor initialisé avec DataLoader (deep migration)")
    logger.info(f"  Programme: {report['loaded_from'].get('programme')}")
```

**Important** : Remplace aussi la méthode `_construire_index_micro_concepts` par celle qui priorise le canonique (si tu veux, je peux te donner la version complète dans un autre message).

---

## 3.2 Modifier `khawarizmi-backend/main.py`

Dans la fonction `lifespan`, juste après cette ligne :

```python
state.tutor = KhawarizmiTutor(data_dir=data_dir)
```

Ajoute ce bloc :

```python
# === DEEP DATA FOUNDATION REPORT ===
try:
    loader = state.tutor.loader
    report = loader.get_data_foundation_report()
    logger.warning("═══════════════════════════════════════════════")
    logger.warning("DATA FOUNDATION STATUS (DEEP MIGRATION)")
    logger.warning(f"  Programme source : {report['programme']['source']}")
    logger.warning(f"  Micro-concepts   : {report['programme']['total_micro_concepts']}")
    logger.warning("═══════════════════════════════════════════════")
except Exception as e:
    logger.error(f"Failed to report data foundation: {e}")
```

---

## 3.3 Modifier `khawarizmi-backend/routes/health.py`

Ajoute à la fin du fichier (avant le dernier `if __name__`) l'endpoint suivant :

```python
@router.get("/debug/data-foundation", tags=["Debug"])
async def data_foundation_debug():
    """Endpoint de debug pour voir l'état des données canoniques vs legacy."""
    s = _get_state()
    foundation = {"timestamp": "2026-06-20"}
    try:
        if s.tutor and hasattr(s.tutor, "loader"):
            foundation["data"] = s.tutor.loader.get_data_foundation_report()
            foundation["tutor"] = {
                "micro_concepts": len(getattr(s.tutor, "_index_micro_concepts", {})),
            }
    except Exception as e:
        foundation["error"] = str(e)
    return foundation
```

---

## 3.4 Modifier `khawarizmi-backend/routes/chat.py`

Dans la fonction `get_chapitres`, remplace le bloc :

```python
programme = {
    "maths":    tutor.programme_maths,
    "physique": tutor.programme_physique,
    "sciences": tutor.programme_sciences,
}.get(matiere)
```

Par :

```python
if hasattr(tutor, 'programme_canonical') and tutor.programme_canonical:
    programme = tutor.programme_canonical
else:
    programme = {
        "maths":    tutor.programme_maths,
        "physique": tutor.programme_physique,
        "sciences": tutor.programme_sciences,
    }.get(matiere)
```

**Fin de la Phase 3.** Confirme quand c'est fait.