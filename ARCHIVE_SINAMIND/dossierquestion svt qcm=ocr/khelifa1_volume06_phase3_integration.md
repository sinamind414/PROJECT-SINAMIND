# KHELIFA 1 Volume 06 — OCR production v3 + extraction/intégration

Source : `input/KHELIFA1_VOLUME_06.pdf`

## Téléchargement

PDF téléchargé depuis Dropbox :

```text
input/KHELIFA1_VOLUME_06.pdf
```

Taille : ~22 MB  
Pages : 28

## OCR production v3

Sortie :

```text
input/KHELIFA1_VOLUME_06.ocr_prod_full.txt
input/KHELIFA1_VOLUME_06.ocr_prod_full.txt.bundle/
```

Rapport OCR :

```text
Pages traitées : 28 / 28
Méthode : OCR sur 28 pages
Erreurs : 0
Total caractères OCR : 49,779
Taille fichier texte final : 78,476 bytes
Confiance moyenne : 62.88
Quality warning : aucun
Durée : ~13 min 19 s
```

## Phase 2 — Extraction

Fichier créé :

```text
output/khelifa1_volume06_extraction_phase2.json
```

Résultat : **20 blocs candidats** extraits.

## Phase 3 — Intégration

Sauvegarde avant intégration :

```text
output/questions_taggees.before_khelifa1_vol06.json
```

Questions ajoutées :

```text
q_khelifa1_vol06_001 → q_khelifa1_vol06_020
```

## Validation globale

```text
Total questions : 234
Concepts distincts utilisés : 35
Erreurs : 0
Avertissements : 0
```

## Distribution des 20 questions ajoutées

### Concepts principaux

| Micro-concept | Questions |
|---|---:|
| `mc_enz_01` — Site actif de l'enzyme | 2 |
| `mc_enz_02` — Spécificité enzymatique | 4 |
| `mc_enz_03` — Vitesse de réaction enzymatique | 2 |
| `mc_enz_05` — Inhibition enzymatique | 2 |
| `mc_struc_01` — Structure primaire | 5 |
| `mc_struc_03` — Structure tertiaire | 4 |
| `mc_struc_05` — Relation structure-fonction | 1 |

### Types

| Type | Questions |
|---|---:|
| `analyse_document` | 12 |
| `raisonnement` | 5 |
| `application` | 2 |
| `comparaison` | 1 |

### Difficulté

| Difficulté | Questions |
|---|---:|
| `facile` | 2 |
| `moyenne` | 14 |
| `difficile` | 4 |

## Thèmes principaux

- Hémoglobine HbA/HbS et relation structure-fonction
- Site actif de la carboxypeptidase
- Électrophorèse des protéines et pHi
- Hydrolyse protéique et liaison peptidique
- RNase, urée, β-mercaptoéthanol et ponts disulfure
- Maladie de Pompe et métabolisme du glycogène
- Glucokinase, glucose-6-phosphate et spécificité enzymatique
- Cinétique enzymatique ExAO
- Inhibition enzymatique : tacrine / autres inhibiteurs
- Structure tertiaire et spécialisation fonctionnelle des enzymes
