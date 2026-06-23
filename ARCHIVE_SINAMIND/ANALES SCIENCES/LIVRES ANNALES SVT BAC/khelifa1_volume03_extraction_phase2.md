# Phase 2 — Extraction des questions candidates

Source : `KHELIFA1_VOLUME_03.pdf`  
OCR de référence : `input/KHELIFA1_VOLUME_03.ocr_prod_full.txt`  
Pipeline utilisé : `scripts/ocr_pipeline_production.py` v3  
Fichier JSON détaillé : `output/khelifa1_volume03_extraction_phase2.json`

## Résultat

- **28 blocs de questions/exercices candidats** extraits.
- Le volume 03 ressemble fortement à un **volume de corrigés / reprises d’exercices** autour de l’expression de l’information génétique.
- Domaine dominant : **synthèse des protéines, transcription, traduction, code génétique, mutations**.

## Qualité OCR

Rapport OCR production v3 :

```text
Pages traitées : 28 / 28
Méthode : OCR sur 28 pages
Erreurs OCR : 0
Total caractères OCR : 58,629
Confiance moyenne : 65.29
Quality warning : aucun
```

## Micro-concepts probables dominants

- `mc_prot_01` — Transcription de l'ADN
- `mc_prot_02` — Traduction de l'ARNm
- `mc_prot_03` — Code génétique
- `mc_prot_04` — ARNm
- `mc_prot_05` — ARNt
- `mc_prot_06` — Ribosome
- `mc_prot_07` — Initiation de la traduction
- `mc_prot_08` — Élongation et terminaison
- `mc_struc_01` — Structure primaire
- `mc_struc_05` — Relation structure-fonction

## Liste courte des blocs extraits

| ID | Pages | Thème | Qualité OCR |
|---|---:|---|---|
| khelifa1_vol03_c001 | 1 | Expression génétique : transcription/traduction | bonne |
| khelifa1_vol03_c002 | 2 | α-amanitine et ARN polymérase | bonne |
| khelifa1_vol03_c003 | 2-3 | Mucoviscidose / CFTR | bonne |
| khelifa1_vol03_c004 | 3-4 | Organites, ARNm et synthèse protéique | moyenne |
| khelifa1_vol03_c005 | 4-5 | Mécanismes de synthèse protéique chez eucaryotes | bonne |
| khelifa1_vol03_c006 | 5 | Initiation, élongation, terminaison | bonne |
| khelifa1_vol03_c007 | 6 | Albinisme, codon stop et mélanine | bonne |
| khelifa1_vol03_c008 | 7 | HbA/HbS et drépanocytose | bonne |
| khelifa1_vol03_c009 | 8-9 | RNase, puromycine, ARNt | moyenne |
| khelifa1_vol03_c010 | 10 | Procaryotes vs eucaryotes | bonne |
| khelifa1_vol03_c011 | 11 | ARNm, codons, polysomes | bonne |
| khelifa1_vol03_c012 | 11-12 | Insuline humain/rat | bonne |
| khelifa1_vol03_c013 | 12 | Mutation silencieuse / mutation changeante | bonne |
| khelifa1_vol03_c014 | 12 | ARNm mélanine et synthèse in vitro | bonne |
| khelifa1_vol03_c015 | 13 | CFTR : ARNm et protéine | moyenne |
| khelifa1_vol03_c016 | 14 | Mutations Hb et relation gène-protéine | moyenne |
| khelifa1_vol03_c017 | 14-15 | Cellule sécrétrice, noyau et cytoplasme | bonne |
| khelifa1_vol03_c018 | 15 | Calcul longueur gène / codons | bonne |
| khelifa1_vol03_c019 | 16 | Globules rouges sans noyau | moyenne |
| khelifa1_vol03_c020 | 17-18 | ADN / ARN / protéine | bonne |
| khelifa1_vol03_c021 | 19 | Voie sécrétoire : REG → Golgi → vésicules | bonne |
| khelifa1_vol03_c022 | 20 | Amibe : ARN du noyau vers cytoplasme | bonne |
| khelifa1_vol03_c023 | 21 | Nucléotide / nucléoside / ADN | moyenne |
| khelifa1_vol03_c024 | 22 | Courbes de sécrétion protéique | bonne |
| khelifa1_vol03_c025 | 23-24 | Noyau, ADN, ARN et synthèse protéique | bonne |
| khelifa1_vol03_c026 | 25 | Caséine et glandes mammaires | moyenne |
| khelifa1_vol03_c027 | 26-27 | Mutation Ser → Arg | moyenne |
| khelifa1_vol03_c028 | 28 | Noyau, ARN préexistant et effet des rayons | moyenne |

## Remarques

1. Plusieurs passages sont des **corrigés** ; les questions ont donc été reconstruites à partir des réponses et des thèmes visibles.
2. Les séquences nucléotidiques exactes restent à vérifier visuellement avant une correction scientifique ultra-fidèle.
3. Cette phase ne modifie pas encore `questions_taggees.json`.

## Prochaine phase

Phase 3 possible : transformer ces 28 blocs en entrées finales puis intégrer dans :

```text
output/questions_taggees.json
```

Validation ensuite avec :

```bash
python scripts/validate_tags.py output/questions_taggees.json
```
