# Phase 3 — Tagging + intégration JSON

Source : `KHELIFA1_VOLUME_01.pdf`  
Extraction source : `output/khelifa1_volume01_extraction_phase2.json`  
Sortie consolidée : `output/questions_taggees.json`

## Actions réalisées

1. Sauvegarde du JSON précédent :

```text
output/questions_taggees.before_khelifa1_vol01.json
```

2. Transformation des 32 blocs candidats en entrées normalisées.

3. Ajout dans :

```text
output/questions_taggees.json
```

4. Validation automatique avec :

```bash
python scripts/validate_tags.py output/questions_taggees.json
```

## Résultat validation

```text
Total questions : 112
Concepts distincts utilisés : 32
Erreurs : 0
Avertissements : 0
```

## Ajout KHELIFA1 Vol 01

- Questions ajoutées : **32**
- IDs : `q_khelifa1_vol01_001` à `q_khelifa1_vol01_032`

### Distribution des concepts principaux ajoutés

| Micro-concept | Questions |
|---|---:|
| `mc_prot_01` — Transcription de l'ADN | 16 |
| `mc_prot_02` — Traduction de l'ARNm | 7 |
| `mc_prot_03` — Code génétique | 4 |
| `mc_prot_04` — ARNm | 4 |
| `mc_prot_05` — ARNt | 1 |

### Distribution des types

| Type | Questions |
|---|---:|
| `analyse_document` | 15 |
| `raisonnement` | 7 |
| `application` | 5 |
| `schema_a_completer` | 3 |
| `comparaison` | 2 |

### Distribution des difficultés

| Difficulté | Questions |
|---|---:|
| `facile` | 2 |
| `moyenne` | 20 |
| `difficile` | 10 |

## Remarques

- Les entrées sont validées structurellement et utilisent uniquement les 42 micro-concepts autorisés.
- Plusieurs notes indiquent que les **séquences nucléotidiques exactes** doivent être vérifiées visuellement si une correction scientifique ultra-fidèle est requise.
- Les tags sont centrés sur le domaine `prot`, ce qui correspond au contenu du volume.
