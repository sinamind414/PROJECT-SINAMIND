# Guide d'annotation expert SVT (à joindre au CSV)

**Fichier à remplir** : `data/golden_annotation_template.csv`
(125 copies Bac SVT — ONEC · ouverture : Excel / Google Sheets / LibreOffice,
l'encodage UTF-8 BOM est pris en charge automatiquement)

**Temps estimé** : 2-3 h (50 questions × 2-3 copies).

---

## 1. Ce que vous devez faire

Remplir **4 colonnes** pour chacune des **100 copies à noter** (les 25 copies
vides sont déjà remplies : score 0 + `empty` — rien à faire dessus).

| Colonne | À mettre | Exemple |
|---|---|---|
| `human_score` | note **entière** sur le barème (colonne `bareme`) | `3` |
| `human_dominant_error` | le code d'erreur dominant (liste §2) | `partial_correct` |
| `human_matched_criteria` | mots-clés **présents** dans la copie, séparés par `;` | `النواة; ADN` |
| `human_unmatched_criteria` | mots-clés **absents**, séparés par `;` | `نسخ` |

Les colonnes en **noir** (question, réponse modèle, mots-clés attendus…)
ne se modifient **jamais**.

## 2. Codes `human_dominant_error` (13 valides)

| Code | Quand |
|---|---|
| `all_correct` | copie parfaite (score = barème) |
| `partial_correct` | copie partielle correcte (défaut) |
| `scientific_error` | erreur scientifique (concept faux) |
| `methodology_error` | démarche/méthode non respectée |
| `off_topic` | hors sujet |
| `insufficient` | trop pauvre pour être notée > 0 |
| `empty` | copie vide (déjà pré-rempli) |
| `gibberish` / `too_short` / `not_arabic` / `repeated_chars` | copies invalides |
| `server_error` / `unknown` | à éviter (défauts techniques) |

## 3. Règles de notation

1. **Copie égale à la réponse modèle** → `human_score` = `bareme` (par
   définition) et `all_correct` — les colonnes matched/unmatched peuvent
   rester vides.
2. **Copie partielle** → proportion de critères satisfaits, arrondie à
   l'entier le plus proche. Ex. barème 4, 2 critères sur 3 → 3/4 ? Non :
   2 critères → 2×4/3 ≈ 3 (arrondi).
3. **Copie vide** → déjà remplie : score 0 + `empty`.
4. **matched + unmatched doivent couvrir TOUS les mots-clés attendus**
   (`mots_cles_attendus`), sauf copie parfaite (règle 1). Ex. mots-clés
   `[النواة; ADN; نسخ]` → matched `النواة; ADN`, unmatched `نسخ`.
5. **Cohérence** : une copie qui reçoit 0 → `insufficient` (ou `empty` si
   vide) ; une copie qui reçoit le barème → `all_correct`.

## 4. Après votre livraison (fait par l'équipe technique)

```bash
cd khawarizmi-backend
python scripts/import_golden_annotations.py --csv data/golden_annotation_template.csv
python scripts/golden_human_report.py     # MAE, exact, severe, κ + verdict
```

Le validateur rejette : score hors barème, code invalide, critères
incohérents avec la copie, ligne partiellement remplie sans score. Une
**livraison partielle est possible** (les lignes vides sont conservées).

## 5. Décision attendue

Le rapport compare vos notes aux moteurs locaux (L2, savoir). Le **κ savoir
≥ 0.65** décidera de réactiver la remédiation pédagogique de l'étage savoir
(actuellement désactivée). Vos annotations remplacent la baseline
synthétique (mots-clés automatiques).
