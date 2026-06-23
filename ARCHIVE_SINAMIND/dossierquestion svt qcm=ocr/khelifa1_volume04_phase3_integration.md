# KHELIFA 1 Volume 04 — OCR production v3 + extraction/intégration

Source : `input/KHELIFA1_VOLUME_04.pdf`

## OCR production v3

Sortie :

```text
input/KHELIFA1_VOLUME_04.ocr_prod_full.txt
input/KHELIFA1_VOLUME_04.ocr_prod_full.txt.bundle/
```

Rapport OCR :

```text
Pages traitées : 28 / 28
Méthode : OCR sur 28 pages
Erreurs : 0
Total caractères OCR : 61,362
Taille fichier texte final : 98,082 bytes
Confiance moyenne : 65.05
Quality warning : aucun
Durée : ~13 min 51 s
```

## Phase 2 — Extraction

Fichier créé :

```text
output/khelifa1_volume04_extraction_phase2.json
```

Résultat : **23 blocs candidats** extraits.

## Phase 3 — Intégration

Sauvegarde avant intégration :

```text
output/questions_taggees.before_khelifa1_vol04.json
```

Questions ajoutées :

```text
q_khelifa1_vol04_001 → q_khelifa1_vol04_023
```

## Validation globale

```text
Total questions : 192
Concepts distincts utilisés : 35
Erreurs : 0
Avertissements : 0
```

## Distribution des 23 questions ajoutées

### Concepts principaux

| Micro-concept | Questions |
|---|---:|
| `mc_prot_01` — Transcription de l'ADN | 9 |
| `mc_prot_02` — Traduction de l'ARNm | 1 |
| `mc_prot_03` — Code génétique | 3 |
| `mc_prot_04` — ARNm | 2 |
| `mc_prot_05` — ARNt | 2 |
| `mc_prot_06` — Ribosome | 3 |
| `mc_prot_08` — Élongation et terminaison | 2 |
| `mc_struc_01` — Structure primaire | 1 |

### Types

| Type | Questions |
|---|---:|
| `analyse_document` | 6 |
| `raisonnement` | 6 |
| `application` | 5 |
| `schema_a_completer` | 3 |
| `definition` | 3 |

### Difficulté

| Difficulté | Questions |
|---|---:|
| `facile` | 5 |
| `moyenne` | 17 |
| `difficile` | 1 |

## Thèmes principaux

- Polysomes et traduction simultanée chez les bactéries
- Transcription par ARN polymérase
- ARNm comme intermédiaire noyau → cytoplasme
- ARNt et activation des acides aminés
- Ribosomes et nécessité de leur présence pour la synthèse protéique
- Codons, anticodons, codons stop
- Mutations : substitution, insertion, délétion
- Structure primaire/tertiaire de l'insuline
