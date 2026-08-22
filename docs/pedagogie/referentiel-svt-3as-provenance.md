# Référentiel SVT 3AS — provenance et règle de publication

**État au 2026-08-22 : alignement interne, validation externe en attente.**

## Source utilisée par l'application

- Référentiel de navigation backend :
  `khawarizmi-backend/data/programmes/svt_sciences_experimentales.json`.
- Copie frontend contrôlée :
  `khawarizmi-frontend/data/referentiel-interne-svt-3as.json`.
- Empreinte SHA-256 commune à cette version :
  `0f5ff7e6128af10705bf611beea9d19bfc7cb745e3c072d6e82d7dce846635ec`.
- Structure : **3 domaines, 11 unités, 55 chapitres/activités**.
- Matériau de recoupement présent dans le dépôt : transcription OCR d'une
  progression ministérielle de juillet 2017 dans
  `khawarizmi-backend/data/methodologie_sciences_3as.json`.

## Pièce encore requise

Le PDF ministériel primaire, sa référence administrative et son empreinte ne
sont pas archivés dans le dépôt. Tant que cette pièce et la signature d'un
enseignant/inspecteur ne sont pas présentes :

1. l'interface parle de « référentiel interne 3AS » et non de « contenu
   officiel validé par le ministère » ;
2. aucun modèle d'entraînement n'est présenté comme une annale ONEC ;
3. les enrichissements sont masqués du parcours Bac ou explicitement marqués
   « non requis » ;
4. les figures restent dans `docs/` et ne sont pas publiées avant relecture.

## Critère de clôture pédagogique

Ajouter la pièce primaire dans le stockage documentaire autorisé, renseigner
sa date/version/hash, puis faire signer une matrice reliant chaque chapitre à
la compétence, aux ressources, à l'activité et à l'évaluation correspondantes.
La signature ne doit jamais être simulée par un agent logiciel.
