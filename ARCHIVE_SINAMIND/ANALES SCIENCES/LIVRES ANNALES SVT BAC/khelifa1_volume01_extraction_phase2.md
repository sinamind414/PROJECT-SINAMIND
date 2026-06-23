# Phase 2 — Extraction des questions candidates

Source : `KHELIFA1_VOLUME_01.pdf`  
OCR de référence demandé : `KHELIFA1_VOLUME_01.ocr_prod_full.txt` + bundle production  
Fichier JSON détaillé : `output/khelifa1_volume01_extraction_phase2.json`

## Résultat

- **32 blocs de questions/exercices candidats** extraits.
- Domaine dominant : **synthèse des protéines / expression de l'information génétique**.
- Pages utiles principales : **9 à 28**.
- Pages 1 à 8 : couverture, préface, pages bruitées ou peu exploitables, sauf fragments.

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
| khelifa1_vol01_c001 | 9 | HbA/HbS et drépanocytose | moyenne |
| khelifa1_vol01_c002 | 9-10 | Locus de synthèse des protéines pancréatiques | moyenne |
| khelifa1_vol01_c003 | 10 | ARNm et formation des polysomes | moyenne |
| khelifa1_vol01_c004 | 10 | ADN viral et protéines virales | faible |
| khelifa1_vol01_c005 | 11 | Exons/introns par hybridation ARNm-ADN | bonne |
| khelifa1_vol01_c006 | 11 | Cinétique ADN/ARN/protéines chez la souris | moyenne |
| khelifa1_vol01_c007 | 12 | ADN viral + uridine radioactive | moyenne |
| khelifa1_vol01_c008 | 13 | Calcul du nombre de gènes chez E. coli | bonne |
| khelifa1_vol01_c009 | 13 | ARNm ajouté à un extrait cellulaire | bonne |
| khelifa1_vol01_c010 | 13 | Procaryotes vs eucaryotes | bonne |
| khelifa1_vol01_c011 | 14 | Traduction d'un ARNm donné | bonne |
| khelifa1_vol01_c012 | 14 | ARNm UGUG... et polysome | moyenne |
| khelifa1_vol01_c013 | 15 | Insuline humain/rat | bonne |
| khelifa1_vol01_c014 | 15 | ADN → ARNm → protéine + mutation | bonne |
| khelifa1_vol01_c015 | 15-16 | ARNm de la mélanine injecté dans une cellule œuf | moyenne |
| khelifa1_vol01_c016 | 16 | Mucoviscidose et CFTR | bonne |
| khelifa1_vol01_c017 | 18-19 | ARNt et étapes de la traduction | moyenne |
| khelifa1_vol01_c018 | 19-20 | Système ABO et allèles | bonne |
| khelifa1_vol01_c019 | 20 | Codon stop / Hb anormal | bonne |
| khelifa1_vol01_c020 | 21 | ADN, ARNm, protéine et code génétique | bonne |
| khelifa1_vol01_c021 | 21-22 | ARNm des globules rouges injecté dans ovocytes | bonne |
| khelifa1_vol01_c022 | 22-23 | Chromatine active et transcription | moyenne |
| khelifa1_vol01_c023 | 23 | Trajet des protéines sécrétées au leucine marqué | bonne |
| khelifa1_vol01_c024 | 24 | Protéine LamB et résistance aux virus | bonne |
| khelifa1_vol01_c025 | 25 | Expériences noyau/ADN/ARNm | bonne |
| khelifa1_vol01_c026 | 25 | Caséine : traduction d'ARNm | bonne |
| khelifa1_vol01_c027 | 26-27 | Cellule sécrétrice et liaison peptidique | moyenne |
| khelifa1_vol01_c028 | 27 | Amibe : noyau, RNAase, uridine | bonne |
| khelifa1_vol01_c029 | 27 | Myopathie et dystrophine | bonne |
| khelifa1_vol01_c030 | 28 | Acétabulaire : rôle du noyau | moyenne |
| khelifa1_vol01_c031 | 28 | Synthèse in vitro avec ARNm | bonne |
| khelifa1_vol01_c032 | 28 | Caséine et glandes mammaires | moyenne |

## Remarques qualité

1. L'OCR production est complet et traçable, mais certaines pages contiennent beaucoup de bruit typographique.
2. Pour l'extraction sémantique, j'ai recoupé les sorties OCR disponibles, surtout quand le fichier production était trop bruité.
3. Les séquences nucléotidiques doivent être **vérifiées visuellement** avant insertion finale, car une seule base fausse change le tag ou la correction attendue.
4. Ces 32 blocs ne sont pas encore injectés dans `questions_taggees.json` : ils constituent la **phase extraction**.

## Prochaine phase proposée

Phase 3 : transformer ces blocs en entrées normalisées finales :

- `id`
- `texte_corrige`
- `micro_concept_id`
- `secondary_concepts`
- `source`
- `type`
- `difficulte`
- `bac_frequent`
- `notes`

Puis validation avec :

```bash
python scripts/validate_tags.py output/questions_taggees.json
```
