# Brouillons de grilles — générés, **non validés**

Dossier produit par `scripts/gen_rubric_skeletons.py`. Rien ici n'est publié :
`services/rubric_store.py` ne lit que `data/rubrics/index.json`, donc ces paires
(`questions/*.draft.json` + `documents/*.draft.json`) ne corrigent aucune copie d'élève.

## Pourquoi ce dossier existe

L'audit des surfaces de correction (`AUDIT-SURFACES-CORRECTION-SITE-2026-08-30.md`) a mesuré
55 questions de rubriques sans grille, atteignables par les élèves depuis
`/document-analysis/chapters/...` et `/diagnostic/chapters/...` (mur `NoLocalGradeWall`).
Les brouillons accélèrent la saisie — ils ne remplacent pas le jugement pédagogique.

## Ce qui est mécanique et ce qui ne l'est pas

* mécanique : `verb_slug`, `criteria` (structure), `model_answer` = l'exemple déjà affiché à
  l'élève dans `methodology-documents.ts`, keypoint = nombre **à la fois** cité par cet exemple
  et présent dans le document, `trend` déduit des points de la courbe ;
* à écrire par l'auteur : exiger d'autres valeurs, `trend_variants`, `counter_examples`,
  le barème (`points`), et la relecture de `title_ar`.

Mesure : sur 55 squelettes, 55 se chargent, **3 seulement** s'auto-valident à 100 % avec leur
propre copie modèle (`--check`). Ailleurs, les nombres de l'exemple viennent du cours et non du
document : c'est précisément ce qui empêche la publication automatique.

## Publier une grille

1. vérifier/corriger le `.draft.json` (rubric + document), supprimer les clés `_draft_notice` ;
2. renommer en `<id>.v1.json`, déplacer sous `data/rubrics/questions/` et `data/documents/` ;
3. ajouter l'entrée dans `data/rubrics/index.json` ;
4. brancher `gradeQuestionId: "<id>"` sur la question dans
   `khawarizmi-frontend/src/lib/methodology-documents.ts` ;
5. `python scripts/validate_rubrics.py` puis `python -m pytest tests/test_grade_s40.py` :
   la garde exige que l'exemple montré à l'élève obtienne 100 % sous la grille branchée —
   un branchement sur le mauvais document est rejeté en rouge.
