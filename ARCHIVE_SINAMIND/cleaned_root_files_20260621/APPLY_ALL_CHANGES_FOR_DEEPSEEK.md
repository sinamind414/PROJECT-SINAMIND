# APPLY ALL PROJECT MODIFICATIONS
## Fichier unique pour DeepSeek V4 Flash (Antigravity)

**Objectif** : Appliquer toutes les modifications structurelles et data foundation sur le projet SINAMIND (Khawarizmi Pro).

**Instructions pour DeepSeek** :
- Lis ce fichier dans l'ordre.
- Crée les fichiers avec le contenu exact.
- Modifie les fichiers existants comme indiqué.
- Respecte les chemins relatifs depuis la racine du projet.

---

## PHASE 1 : ARCHIVAGE & NOUVELLE FONDATION DONNÉES

### 1.1 Archiver les anciennes données (corrompues)

Crée le dossier et déplace les fichiers suivants :

```
khawarizmi-backend/data_archive/2026-06-20/
```

**Fichiers à archiver** :
- `annales_sciences_3as.json`
- `annales_maths_3as.json`
- `programme_sciences_3as.json`
- `lexique_svt_terminale_complet.json`
- `programme_sciences_3as.backup_20260608_181234.json`

### 1.2 Créer le Programme Canonique (42 micro-concepts)

**Fichier à créer** : `khawarizmi-backend/data/official/programme_svt_3as_canonical.json`

```json
{
  "metadata": {
    "version": "2026.2.0",
    "source": "ONEC - Programme officiel SVT Terminale Sciences Expérimentales Algérie",
    "matiere": "SVT",
    "niveau": "3AS",
    "filiere": "Sciences Expérimentales",
    "date": "2026-06-20",
    "status": "FOUNDATION"
  },
  "domaines": [
    {
      "id": "domaine_proteines",
      "nom_fr": "Spécialisation fonctionnelle des protéines",
      "nom_ar": "التخصص الوظيفي للبروتينات",
      "importance": "critique",
      "chapitres": [
        {
          "id": "ch1_proteines",
          "nom_fr": "Synthèse des protéines",
          "nom_ar": "تركيب البروتينات",
          "micro_concepts": [
            {"id": "mc_prot_01", "nom_fr": "Transcription de l'ADN", "nom_ar": "نسخ المعلومة الوراثية", "importance": "critique", "bac_frequent": true},
            {"id": "mc_prot_02", "nom_fr": "Traduction de l'ARNm", "nom_ar": "ترجمة الرنا الرسول", "importance": "critique", "bac_frequent": true},
            {"id": "mc_prot_03", "nom_fr": "Code génétique", "nom_ar": "الشفرة الوراثية", "importance": "critique", "bac_frequent": true},
            {"id": "mc_prot_04", "nom_fr": "ARN messager (ARNm)", "nom_ar": "الرنا الرسول", "importance": "critique", "bac_frequent": true},
            {"id": "mc_prot_05", "nom_fr": "ARN de transfert (ARNt)", "nom_ar": "الرنا الناقل", "importance": "haute", "bac_frequent": true},
            {"id": "mc_prot_06", "nom_fr": "Ribosome", "nom_ar": "الريبوزوم", "importance": "critique", "bac_frequent": true},
            {"id": "mc_prot_07", "nom_fr": "Initiation de la traduction", "nom_ar": "بدء الترجمة", "importance": "haute", "bac_frequent": true},
            {"id": "mc_prot_08", "nom_fr": "Élongation et terminaison", "nom_ar": "الاستطالة والإنهاء", "importance": "haute", "bac_frequent": false}
          ]
        },
        {
          "id": "ch_structure_proteines",
          "nom_fr": "Structure et fonction des protéines",
          "nom_ar": "بنية البروتين ووظيفته",
          "micro_concepts": [
            {"id": "mc_struc_01", "nom_fr": "Structure primaire", "nom_ar": "البنية الأولية", "importance": "haute", "bac_frequent": true},
            {"id": "mc_struc_02", "nom_fr": "Structure secondaire (α-hélice, feuillet β)", "nom_ar": "البنية الثانوية", "importance": "haute", "bac_frequent": true},
            {"id": "mc_struc_03", "nom_fr": "Structure tertiaire", "nom_ar": "البنية الثالثية", "importance": "critique", "bac_frequent": true},
            {"id": "mc_struc_04", "nom_fr": "Structure quaternaire", "nom_ar": "البنية الرباعية", "importance": "moyenne", "bac_frequent": false},
            {"id": "mc_struc_05", "nom_fr": "Relation structure-fonction", "nom_ar": "العلاقة بين البنية والوظيفة", "importance": "critique", "bac_frequent": true}
          ]
        },
        {
          "id": "ch2_enzymes",
          "nom_fr": "Activité enzymatique",
          "nom_ar": "النشاط الإنزيمي",
          "micro_concepts": [
            {"id": "mc_enz_01", "nom_fr": "Site actif de l'enzyme", "nom_ar": "الموقع الفعال للإنزيم", "importance": "critique", "bac_frequent": true},
            {"id": "mc_enz_02", "nom_fr": "Spécificité enzymatique", "nom_ar": "النوعية الإنزيمية", "importance": "critique", "bac_frequent": true},
            {"id": "mc_enz_03", "nom_fr": "Vitesse de réaction enzymatique", "nom_ar": "سرعة التفاعل الإنزيمي", "importance": "haute", "bac_frequent": true},
            {"id": "mc_enz_04", "nom_fr": "Facteurs influençant l'activité (température, pH)", "nom_ar": "العوامل المؤثرة على النشاط الإنزيمي", "importance": "critique", "bac_frequent": true},
            {"id": "mc_enz_05", "nom_fr": "Inhibition enzymatique", "nom_ar": "تثبيط الإنزيم", "importance": "haute", "bac_frequent": false}
          ]
        },
        {
          "id": "ch3_immunite",
          "nom_fr": "Immunologie",
          "nom_ar": "المناعة",
          "micro_concepts": [
            {"id": "mc_imm_01", "nom_fr": "Lymphocytes B", "nom_ar": "الخلايا الليمفاوية B", "importance": "critique", "bac_frequent": true},
            {"id": "mc_imm_02", "nom_fr": "Lymphocytes T", "nom_ar": "الخلايا الليمفاوية T", "importance": "critique", "bac_frequent": true},
            {"id": "mc_imm_03", "nom_fr": "Anticorps et antigènes", "nom_ar": "الأجسام المضادة والمستضدات", "importance": "critique", "bac_frequent": true},
            {"id": "mc_imm_04", "nom_fr": "Réponse immunitaire humorale", "nom_ar": "الاستجابة المناعية الخلطية", "importance": "haute", "bac_frequent": true},
            {"id": "mc_imm_05", "nom_fr": "Réponse immunitaire cellulaire", "nom_ar": "الاستجابة المناعية الخلوية", "importance": "haute", "bac_frequent": true},
            {"id": "mc_imm_06", "nom_fr": "Mémoire immunitaire", "nom_ar": "الذاكرة المناعية", "importance": "haute", "bac_frequent": true}
          ]
        },
        {
          "id": "ch4_nerveux",
          "nom_fr": "Transmission de l'information nerveuse",
          "nom_ar": "نقل المعلومة العصبية",
          "micro_concepts": [
            {"id": "mc_nerv_01", "nom_fr": "Potentiel de repos", "nom_ar": "كمون الراحة", "importance": "critique", "bac_frequent": true},
            {"id": "mc_nerv_02", "nom_fr": "Potentiel d'action", "nom_ar": "كمون العمل", "importance": "critique", "bac_frequent": true},
            {"id": "mc_nerv_03", "nom_fr": "Synapse chimique", "nom_ar": "المشبك الكيميائي", "importance": "critique", "bac_frequent": true},
            {"id": "mc_nerv_04", "nom_fr": "Neurotransmetteurs", "nom_ar": "النواقل العصبية", "importance": "haute", "bac_frequent": true}
          ]
        }
      ]
    },
    {
      "id": "domaine_energie",
      "nom_fr": "Transformations énergétiques",
      "nom_ar": "التحولات الطاقوية",
      "chapitres": [
        {
          "id": "ch_photosynthese",
          "nom_fr": "Photosynthèse",
          "nom_ar": "التركيب الضوئي",
          "micro_concepts": [
            {"id": "mc_photo_01", "nom_fr": "Chloroplaste et thylakoïdes", "nom_ar": "البلاستيدات الخضراء والثايلاكويدات", "importance": "critique", "bac_frequent": true},
            {"id": "mc_photo_02", "nom_fr": "Phase photochimique (lumineuse)", "nom_ar": "المرحلة الضوئية", "importance": "critique", "bac_frequent": true},
            {"id": "mc_photo_03", "nom_fr": "Cycle de Calvin (phase obscure)", "nom_ar": "دورة كالفن", "importance": "critique", "bac_frequent": true},
            {"id": "mc_photo_04", "nom_fr": "Facteurs influençant la photosynthèse", "nom_ar": "العوامل المؤثرة على التركيب الضوئي", "importance": "haute", "bac_frequent": true}
          ]
        },
        {
          "id": "ch_respiration",
          "nom_fr": "Respiration cellulaire",
          "nom_ar": "التنفس الخلوي",
          "micro_concepts": [
            {"id": "mc_resp_01", "nom_fr": "Mitochondrie", "nom_ar": "الميتوكوندريا", "importance": "critique", "bac_frequent": true},
            {"id": "mc_resp_02", "nom_fr": "Glycolyse", "nom_ar": "الجليكوليز", "importance": "haute", "bac_frequent": true},
            {"id": "mc_resp_03", "nom_fr": "Cycle de Krebs", "nom_ar": "دورة كربس", "importance": "critique", "bac_frequent": true},
            {"id": "mc_resp_04", "nom_fr": "Chaîne respiratoire et phosphorylation oxydative", "nom_ar": "سلسلة التنفس والفسفرة التأكسدية", "importance": "critique", "bac_frequent": true},
            {"id": "mc_resp_05", "nom_fr": "Fermentation (lactique et alcoolique)", "nom_ar": "التخمر", "importance": "haute", "bac_frequent": true}
          ]
        }
      ]
    },
    {
      "id": "domaine_tectonique",
      "nom_fr": "Tectonique globale",
      "nom_ar": "التكتونية العامة",
      "chapitres": [
        {
          "id": "ch_tectonique",
          "nom_fr": "Tectonique des plaques",
          "nom_ar": "تكتونية الصفائح",
          "micro_concepts": [
            {"id": "mc_tec_01", "nom_fr": "Structure interne de la Terre", "nom_ar": "البنية الداخلية للأرض", "importance": "haute", "bac_frequent": true},
            {"id": "mc_tec_02", "nom_fr": "Plaques tectoniques", "nom_ar": "الصفائح التكتونية", "importance": "critique", "bac_frequent": true},
            {"id": "mc_tec_03", "nom_fr": "Divergence et convergence des plaques", "nom_ar": "تباعد وتقارب الصفائح", "importance": "critique", "bac_frequent": true},
            {"id": "mc_tec_04", "nom_fr": "Subduction et dorsales océaniques", "nom_ar": "الاندساس والحواف المتباعدة", "importance": "haute", "bac_frequent": true},
            {"id": "mc_tec_05", "nom_fr": "Sismicité et volcanisme", "nom_ar": "الزلازل والبراكين", "importance": "haute", "bac_frequent": true}
          ]
        }
      ]
    }
  ]
}
```

---

## PHASE 2 : CRÉATION DU DATA LOADER (Single Source of Truth)

**Fichier à créer** : `khawarizmi-backend/services/data_loader.py`

```python
"""
services/data_loader.py
SINGLE SOURCE OF TRUTH for all educational data.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("khawarizmi.data_loader")

DATA_ROOT = Path(__file__).parent.parent / "data"
OFFICIAL_DIR = DATA_ROOT / "official"

class DataLoader:
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else DATA_ROOT
        self._programme_canonical: Dict = {}
        self._loaded_from = {}

    def load_canonical_programme(self) -> Dict[str, Any]:
        candidates = [
            OFFICIAL_DIR / "programme_svt_3as_canonical.json",
            self.data_dir / "official" / "programme_svt_3as_canonical.json",
        ]
        
        for path in candidates:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._programme_canonical = data
                self._loaded_from["programme"] = str(path)
                logger.info(f"✅ Loaded CANONICAL programme from {path}")
                return data
        
        # Fallback
        old_path = self.data_dir / "programme_sciences_3as.json"
        if old_path.exists():
            logger.warning("⚠️ FALLBACK: Using OLD programme_sciences_3as.json")
            with open(old_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._programme_canonical = data
            self._loaded_from["programme"] = str(old_path) + " (DEPRECATED)"
            return data
        
        raise FileNotFoundError("No programme found")

    def get_programme(self) -> Dict:
        if not self._programme_canonical:
            self.load_canonical_programme()
        return self._programme_canonical

    def get_data_foundation_report(self) -> Dict:
        prog = self.get_programme()
        total_mc = 0
        chapters = 0
        if prog and "domaines" in prog:
            for d in prog.get("domaines", []):
                for ch in d.get("chapitres", []):
                    chapters += 1
                    total_mc += len(ch.get("micro_concepts", []))

        return {
            "programme": {
                "source": self._loaded_from.get("programme"),
                "version": prog.get("metadata", {}).get("version") if prog else None,
                "total_micro_concepts": total_mc,
                "total_chapters": chapters,
                "status": "CANONICAL"
            },
            "migration": {
                "phase": "deep_foundation"
            }
        }

# Singleton
_loader_instance = None

def get_data_loader(data_dir: Optional[str] = None) -> DataLoader:
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = DataLoader(data_dir)
    return _loader_instance
```

---

## PHASE 3 : MODIFICATIONS DES FICHIERS EXISTANTS

### 3.1 Modifier `khawarizmi-backend/services/khawarizmi_engine.py`

**Remplacer la méthode `__init__`** par ceci :

```python
def __init__(self, data_dir: str):
    self.data_dir = data_dir

    from services.data_loader import get_data_loader
    self.loader = get_data_loader(data_dir)

    self.programme_canonical = self.loader.load_canonical_programme()
    self.annales_clean = {}
    self.lexique = {}

    # Compatibility layer
    self.programme_sciences = self.programme_canonical
    self.annales_sciences = self.annales_clean
    self.lexique_complet = self.lexique

    # Legacy subjects
    self.programme_maths = self._charger_json(data_dir, 'programme_maths_3as.json', optional=True)
    self.annales_maths = self._charger_json(data_dir, 'annales_maths_3as.json', optional=True)
    self.programme_physique = self._charger_json(data_dir, 'programme_physique_3as.json', optional=True)

    self._index_questions = self._construire_index()
    self._index_micro_concepts = self._construire_index_micro_concepts()
    self._index_lexique = self._construire_index_lexique()

    report = self.loader.get_loading_report()
    logger.info("KhawarizmiTutor initialisé avec DataLoader (deep migration)")
    logger.info(f"  Programme: {report['loaded_from'].get('programme')}")
```

**Remplacer aussi** la méthode `_construire_index_micro_concepts` par la version qui priorise le canonique.

---

### 3.2 Modifier `khawarizmi-backend/main.py`

Dans la fonction `lifespan`, ajouter après la création du tutor :

```python
# === DEEP DATA FOUNDATION MIGRATION ===
try:
    loader = state.tutor.loader
    report = loader.get_data_foundation_report()
    logger.warning("═══════════════════════════════════════════════")
    logger.warning("DATA FOUNDATION STATUS (DEEP MIGRATION)")
    logger.warning(f"  Programme: {report['programme']['source']}")
    logger.warning(f"  Micro-concepts: {report['programme']['total_micro_concepts']}")
    logger.warning("═══════════════════════════════════════════════")
except Exception as e:
    logger.error(f"Failed to report data foundation: {e}")
```

---

### 3.3 Modifier `khawarizmi-backend/routes/health.py`

Ajouter à la fin du fichier l'endpoint suivant :

```python
@router.get("/debug/data-foundation", tags=["Debug"])
async def data_foundation_debug():
    s = _get_state()
    foundation = {"timestamp": "2026-06-20"}
    try:
        if s.tutor and hasattr(s.tutor, "loader"):
            foundation["data"] = s.tutor.loader.get_data_foundation_report()
    except Exception as e:
        foundation["error"] = str(e)
    return foundation
```

---

### 3.4 Modifier `khawarizmi-backend/routes/chat.py`

Dans la route `/api/chapitres/{matiere}`, remplacer par :

```python
if hasattr(tutor, 'programme_canonical') and tutor.programme_canonical:
    programme = tutor.programme_canonical
else:
    programme = {
        "maths": tutor.programme_maths,
        "physique": tutor.programme_physique,
        "sciences": tutor.programme_sciences,
    }.get(matiere)
```

---

## PHASE 4 : CRÉER LES SCRIPTS DATA PIPELINE

### 4.1 `khawarizmi-backend/scripts/data_pipeline/auto_tagger.py`

Crée le fichier avec le contenu complet du script d'auto-tagging (utilise les 42 concepts).

### 4.2 `khawarizmi-backend/scripts/data_pipeline/migrate_to_canonical.py`

Crée le script de migration.

---

## PHASE 5 : CRÉER LES TEMPLATES

### 5.1 `khawarizmi-backend/templates/questions_batch_template.csv`

Crée avec l'en-tête et quelques lignes d'exemple.

### 5.2 `khawarizmi-backend/templates/question_template.json`

Crée le template JSON.

---

## PHASE 6 : CRÉER LES FICHIERS DE DOCUMENTATION

- `DATA_FOUNDATION_AUDIT.md`
- `DATA_REBUILD_PLAN.md`
- `BATCH_PLAN_DATA_FOUNDATION.md`

---

**FIN DES INSTRUCTIONS**

DeepSeek : Commence par créer le dossier `data/official/`, puis le fichier `programme_svt_3as_canonical.json`, puis `services/data_loader.py`, puis applique les modifications sur les fichiers existants.

Exécute les étapes dans l'ordre.
