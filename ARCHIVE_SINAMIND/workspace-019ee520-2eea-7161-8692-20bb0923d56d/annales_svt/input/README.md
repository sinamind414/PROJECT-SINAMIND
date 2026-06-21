# Dossier INPUT

Déposez ici les fichiers sources des annales SVT à traiter.

## Formats acceptés
- **Images** : `.jpg`, `.jpeg`, `.png`, `.webp` (scans de sujets) → je lis visuellement
- **PDF** : `.pdf` (jusqu'à 30 pages par document)
- **Texte** : `.txt`, `.md`, `.json` (texte brut, même corrompu/mojibake)

## Convention de nommage (recommandée)
`<source>_<annee>_<page>.<ext>` — exemples :
- `khelifa_2023_p47.jpg`
- `bac_officiel_2022_sujet.pdf`
- `rochdi_2021_p12.png`

## Après dépôt
1. Indiquez-moi simplement « fichiers déposés » (ou listez-les).
2. Je lis chaque source → EXTRACTION → TRANSCRIPTION (arabe corrigé) → TAGGING.
3. Résultat consolidé dans `../output/questions_taggees.json`.
4. Validation automatique via `../scripts/validate_tags.py`.

## Note sur l'arabe corrompu
N'hésitez pas à déposer le texte même s'il est mojibake (ex: "أ ذهص زالث").
La phase TRANSCRIPTION le corrigera en gardant le sens et les termes scientifiques.
