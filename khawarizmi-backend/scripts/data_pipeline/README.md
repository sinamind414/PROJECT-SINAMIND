# Data Pipeline

Ce dossier contient les scripts pour construire les données propres.

Règle : Ne plus utiliser directement les anciens JSON dans `data/`.

## OCR Production (Pipeline Modulaire)

Nouveau backend professionnel :

```bash
python scripts/ocr/ocr_pipeline_production.py \
  data/ANNALES_SVT_BAC_ALGERIE/KHELIFA_1/VOLUMES_KHELIFA1/KHELIFA1_VOLUME_05.pdf \
  --dpi 140
```

Puis intégrer dans le canonique :

```bash
python scripts/data_pipeline/integrate_ocr_bilan.py \
  --bilan-json data/annales_clean/questions_taggees.json
```
