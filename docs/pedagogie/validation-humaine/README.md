# Lot 7 — Dossier de validation humaine et garde de publication

**État au 2026-08-22 : NO-GO.** Ce dossier prépare le travail humain ; il ne
contient ni visa ministériel, ni annotation experte, ni signature. Les fichiers
de `templates/` sont volontairement vides et ne comptent jamais comme preuve.

## Ce qu’un agent logiciel peut vérifier

- présence et SHA-256 de la pièce primaire archivée ;
- couverture 125/125 des deux annotations indépendantes ;
- identités pseudonymisées distinctes A/B et références de déclarations
  conservées dans un stockage externe autorisé ;
- liste exacte des désaccords et couverture de leur arbitrage ;
- cohérence du consensus et du rapport MAE/κ ;
- décisions 55 contenus, 110 barèmes et 35 figures ;
- présence d’un GO final faisant référence à deux signatures externes.

Le logiciel **ne peut pas** vérifier qu’une personne est réellement enseignant
ou inspecteur, ni signer à sa place. Cette authenticité reste une responsabilité
humaine et organisationnelle.

## Templates fournis

| Fichier | Lignes attendues | Rôle |
|---|---:|---|
| `golden-grader-a.csv` | 125 | annotation aveugle A |
| `golden-grader-b.csv` | 125 | annotation aveugle B |
| `golden-arbitration.csv` | désaccords seulement | décision d’un troisième humain |
| `content-review.csv` | 55 | validation scientifique chapitre par chapitre |
| `rubric-review.csv` | 110 | validation des barèmes formatifs |
| `figure-review.csv` | 35 | science, overlay AR/FR, mobile et impression A4 |
| `primary-source-manifest-template.json` | 1 | référence administrative + hash de la pièce primaire |
| `reviewers-template.json` | 2 + arbitre | rôles et références de déclarations externes |
| `human-metrics-template.json` | 1 | MAE, κ et taux d’écarts graves recalculés |
| `publication-signoff-template.json` | 1 | décision finale et références de signatures |

Les templates golden ne contiennent pas le texte des copies, uniquement un
`answer_sha256`. L’annotation se fait avec un paquet sécurisé séparé ; aucune
copie d’élève réelle ne doit être ajoutée au dépôt.

## Workflow double aveugle

1. Archiver la pièce ministérielle primaire autorisée et créer
   `evidence/primary-source.json` depuis le template avec son hash réel.
2. Désigner deux correcteurs A/B ne voyant ni l’identité ni les notes de
   l’autre. Conserver leurs attestations hors dépôt et référencer celles-ci
   dans `evidence/reviewers.json`.
3. Remplir séparément `evidence/golden-grader-a.csv` et
   `evidence/golden-grader-b.csv`. Aucun score n’est prérempli, y compris pour
   les copies vides.
4. Générer la liste des divergences ; un troisième humain remplit uniquement
   ces lignes dans `evidence/golden-arbitration.csv`.
5. Construire le consensus puis recalculer les métriques liées à son hash :

   ```bash
   python scripts/build_double_blind_consensus.py
   cd khawarizmi-backend
   python scripts/golden_human_report.py \
     --input ../docs/pedagogie/validation-humaine/evidence/golden-human-annotated.json \
     --consensus ../docs/pedagogie/validation-humaine/evidence/golden-consensus.json \
     --metrics-output ../docs/pedagogie/validation-humaine/evidence/human-metrics.json
   ```

6. Relire 55 contenus, 110 barèmes et 35 figures. Une figure exige en plus
   labels AR/FR effectivement appliqués et tests écran mobile + impression A4.
7. Deux responsables humains déposent les références de leurs signatures dans
   `evidence/publication-signoff.json` et fixent le commit autorisé.
8. Exécuter la garde sans tolérance :

```bash
python scripts/check_publication_gate.py --write
```

Le code de sortie reste non nul tant qu’une preuve manque. Pour seulement
régénérer le constat NO-GO courant :

```bash
python scripts/check_publication_gate.py --write --allow-no-go
```

## Interdictions

- Ne jamais recopier `templates/` dans `evidence/` pour forcer un GO.
- Ne jamais changer `annotator` ou une métadonnée synthétique en « expert ».
- Ne jamais considérer l’ancien workflow mono-correcteur
  `export_golden_template.py` / `import_golden_annotations.py` comme une preuve
  double aveugle.
- Ne jamais intégrer les figures de `docs/` avant décision humaine.
- Ne jamais présenter les scores automatiques comme certificatifs avant GO.
