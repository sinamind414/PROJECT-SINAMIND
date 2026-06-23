# KHELIFA 1 Volume 05 — OCR production v3 + extraction/intégration

Source : `input/KHELIFA1_VOLUME_05.pdf`

## Téléchargement

PDF téléchargé depuis Dropbox :

```text
input/KHELIFA1_VOLUME_05.pdf
```

Taille : ~22 MB  
Pages : 28

## OCR production v3

Sortie :

```text
input/KHELIFA1_VOLUME_05.ocr_prod_full.txt
input/KHELIFA1_VOLUME_05.ocr_prod_full.txt.bundle/
```

Rapport OCR :

```text
Pages traitées : 28 / 28
Méthode : OCR sur 28 pages
Erreurs : 0
Total caractères OCR : 52,817
Taille fichier texte final : 83,883 bytes
Confiance moyenne : 63.35
Quality warning : aucun
Durée : ~15 min 50 s
```

## Phase 2 — Extraction

Fichier créé :

```text
output/khelifa1_volume05_extraction_phase2.json
```

Résultat : **22 blocs candidats** extraits.

## Phase 3 — Intégration

Sauvegarde avant intégration :

```text
output/questions_taggees.before_khelifa1_vol05.json
```

Questions ajoutées :

```text
q_khelifa1_vol05_001 → q_khelifa1_vol05_022
```

## Validation globale

```text
Total questions : 214
Concepts distincts utilisés : 35
Erreurs : 0
Avertissements : 0
```

## Distribution des 22 questions ajoutées

### Concepts principaux

| Micro-concept | Questions |
|---|---:|
| `mc_enz_01` — Site actif de l'enzyme | 2 |
| `mc_enz_02` — Spécificité enzymatique | 5 |
| `mc_enz_03` — Vitesse de réaction enzymatique | 2 |
| `mc_enz_04` — Facteurs influençant l'activité | 1 |
| `mc_enz_05` — Inhibition enzymatique | 2 |
| `mc_prot_01` — Transcription de l'ADN | 1 |
| `mc_prot_03` — Code génétique | 3 |
| `mc_prot_04` — ARNm | 1 |
| `mc_prot_06` — Ribosome | 1 |
| `mc_struc_01` — Structure primaire | 3 |
| `mc_struc_05` — Relation structure-fonction | 1 |

### Types

| Type | Questions |
|---|---:|
| `analyse_document` | 13 |
| `raisonnement` | 4 |
| `application` | 4 |
| `schema_a_completer` | 1 |

### Difficulté

| Difficulté | Questions |
|---|---:|
| `moyenne` | 19 |
| `difficile` | 3 |

## Thèmes principaux

- Mutations et enzymes non fonctionnelles
- Code génétique et expérience poly-U
- Conditions de synthèse protéique in vitro
- Protéases : trypsine, chymotrypsine
- Structure des peptides et acides aminés
- pHi et électrophorèse
- Cinétique enzymatique
- Température, pH et activité enzymatique
- Spécificité enzymatique
- Inhibition : arabinose / glucose oxydase
- Enzymes de mobilisation des réserves d'amidon pendant la germination
