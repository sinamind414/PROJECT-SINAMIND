# KHELIFA 1 Volume 02 — OCR production + Phase 2/3

Source : `input/KHELIFA1_VOLUME_02.pdf`

## OCR production

Commande utilisée :

```bash
python scripts/ocr_pipeline_production.py input/KHELIFA1_VOLUME_02.pdf \
  --start 1 --end 28 \
  --dpi 140 \
  --workers 1 \
  --timeout 180 \
  --psm 3 \
  --oem 1 \
  --pdf-mode ocr \
  --retries 2 \
  --suffix .ocr_prod_full.txt
```

Sortie :

```text
input/KHELIFA1_VOLUME_02.ocr_prod_full.txt
input/KHELIFA1_VOLUME_02.ocr_prod_full.txt.bundle/
```

Rapport OCR :

```text
Pages traitées : 28 / 28
Méthode : OCR sur 28 pages
Erreurs : 0
Total caractères OCR : 53,838
Taille fichier texte final : 84,842 bytes
Confiance moyenne OCR : 60.45
Durée : ~9 min 26 s
```

## Phase 2 — Extraction

Fichier créé :

```text
output/khelifa1_volume02_extraction_phase2.json
```

Résultat : **29 blocs candidats** extraits.

## Phase 3 — Intégration

Sauvegarde avant intégration :

```text
output/questions_taggees.before_khelifa1_vol02.json
```

Questions ajoutées :

```text
q_khelifa1_vol02_001 → q_khelifa1_vol02_029
```

## Validation globale

Commande :

```bash
python scripts/validate_tags.py output/questions_taggees.json
```

Résultat :

```text
Total questions : 141
Concepts distincts utilisés : 33
Erreurs : 0
Avertissements : 0
```

## Distribution des 29 questions ajoutées

### Concepts principaux

| Micro-concept | Questions |
|---|---:|
| `mc_prot_01` — Transcription de l'ADN | 8 |
| `mc_prot_02` — Traduction de l'ARNm | 4 |
| `mc_prot_03` — Code génétique | 6 |
| `mc_prot_04` — ARNm | 4 |
| `mc_prot_05` — ARNt | 4 |
| `mc_prot_06` — Ribosome | 2 |
| `mc_struc_01` — Structure primaire | 1 |

### Types

| Type | Questions |
|---|---:|
| `analyse_document` | 15 |
| `application` | 6 |
| `raisonnement` | 4 |
| `schema_a_completer` | 2 |
| `comparaison` | 2 |

### Difficulté

| Difficulté | Questions |
|---|---:|
| `moyenne` | 17 |
| `difficile` | 12 |

## Thèmes principaux

- Régulation/expression de la lactase chez les bactéries
- ARNm, ARNt, ARNr et ribosomes
- Traduction et code génétique
- Mutations et maladies génétiques : thalassémie, hypercholestérolémie familiale, xeroderma pigmentosum, phénylcétonurie
- Structure-fonction des protéines : insuline, récepteurs membranaires
- Virus à ARN : VMT
