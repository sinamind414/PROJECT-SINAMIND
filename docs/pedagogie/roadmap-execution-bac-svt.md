# Roadmap d’exécution — SINAMIND Bac SVT Algérie

**Date de référence : 2026-08-22**  
**Cap produit :** savoir scientifique → Manhadjiya automatisée → pratique Bac → correction ciblée → coaching → nouvelle tentative → FSRS.

## Invariants

1. Référentiel interne : **3 domaines, 11 unités, 55 chapitres** ; aucune revendication ministérielle sans pièce primaire et visa humain.
2. Une note automatisée reste **formative** tant que le golden set n’est pas annoté par deux correcteurs humains.
3. Le fond scientifique est contrôlé avant la forme méthodologique.
4. L’élève produit une réponse avant de voir le modèle.
5. Le coach donne au maximum deux priorités et une route réelle par action.
6. L’arabe est la langue pédagogique ; les termes scientifiques français sont conservés.
7. Aucun contenu d’élève n’est journalisé en clair.

## Lot 1 — Contrat d’apprentissage des 55 chapitres

**But :** chaque chapitre possède le même parcours minimal vérifiable.

- fiche de révision ;
- objectif de chapitre ;
- checklist Bac en six réflexes ;
- verbes recommandés ;
- lien vers entraînement documentaire ;
- exercices et nouvelle tentative.

**Acceptation :**
- 55 contrats uniques, même ensemble de slugs que le référentiel ;
- exactement six étapes par checklist ;
- aucune route ou fiche manquante ;
- test automatique bloquant et build frontend vert.

**État : EN COURS — première tranche appliquée dans ce lot.**

## Lot 2 — Boucle active dans la page de chapitre

**But :** transformer la consultation passive en séance de travail.

1. lire la fiche ;
2. cocher les six réflexes ;
3. répondre sans modèle ;
4. soumettre ;
5. lire la correction ;
6. refaire immédiatement la question faible.

**Acceptation :** la réponse modèle n’est jamais visible avant une tentative ; chaque CTA mène à une route existante.

## Lot 3 — Banque d’exercices alignée

**But :** au moins une activité documentaire et une activité de restitution par chapitre.

**Acceptation :**
- couverture 55/55 ;
- question, documents, réponse de référence, critères et barème présents ;
- contenus hors programme marqués « enrichissement » ;
- aucune annale présentée comme ONEC sans preuve primaire.

## Lot 4 — Correcteur et coach en boucle fermée

**But :** une erreur produit une réparation concrète puis une nouvelle tentative.

**Acceptation :**
- classification science/méthode/hors-sujet ;
- deux priorités maximum ;
- erreur scientifique → chapitre précis ;
- erreur méthodologique → atelier du verbe ;
- absence de référence → note plafonnée et avertissement ;
- tests adversariaux et score toujours borné au barème.

## Lot 5 — Mémoire et boussole

**But :** FSRS choisit quoi revoir, le coach explique pourquoi.

**Acceptation :**
- 11 unités dans l’ordre du référentiel ;
- tous les liens de la boussole valides ;
- une seule source de vérité mémoire ;
- aucune « prédiction Bac » non calibrée présentée comme certaine.

## Lot 6 — Iconographie et accessibilité

**But :** schémas utilisables dans une copie Bac et interface mobile accessible.

**Acceptation :** 35/35 figures relues, labels AR/FR, provenance, lisibilité mobile/A4, texte alternatif et validation enseignant.

## Lot 7 — Validation humaine et publication

**But :** passer du formatif au publiable.

**Acceptation :**
- pièce ministérielle primaire archivée avec hash ;
- golden set annoté en double aveugle par deux enseignants/inspecteurs ;
- désaccords arbitrés ;
- seuils MAE/κ recalculés sur annotations humaines ;
- GO signé pour contenus, figures et barèmes.

## Hors périmètre automatique

Un agent logiciel ne signe pas une validation scientifique, ne fabrique pas une provenance ONEC et ne transforme pas une baseline synthétique en annotation humaine.
