# Evidence — répertoire réservé aux preuves humaines réelles

Ce répertoire est vide par conception. Les templates voisins ne sont pas des
preuves. Ajouter uniquement des manifestes, CSV et références effectivement
produits par les personnes responsables, sans secret ni donnée élève en clair.

Fichiers attendus par `scripts/check_publication_gate.py` :

- `primary-source.json` + document primaire autorisé placé dans `primary/`, dont le hash correspond ;
- `reviewers.json` ;
- `golden-grader-a.csv` et `golden-grader-b.csv` ;
- `golden-arbitration.csv` ;
- `human-metrics.json` ;
- `content-review.csv`, `rubric-review.csv`, `figure-review.csv` ;
- `publication-signoff.json`.

Les signatures restent dans un stockage externe sécurisé ; le dépôt contient
uniquement leur référence vérifiable.
