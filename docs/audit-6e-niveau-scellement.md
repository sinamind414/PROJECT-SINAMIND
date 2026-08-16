# Acte 6 — Scellement : table des 10 collée, file greppée, grain expliqué, question fermée au porteur

> **Date** : 2026-08-16 · **Branche** : `arena/01a0066d-project-sinamind`
> **Objet** : le 6ᵉ texte (audit de mon acte 5). Vérifications repo faites, 5 substitutions appliquées, annexe A ajoutée à l'acte 5.
> **Ce document** : la fin de la boucle d'audits. Il ne contient **aucune nouvelle affirmation** — il liste ce qui est établi, ce qui ne l'est pas, et la seule question qui reste au porteur.

---

## 0. Verdict

Le 6ᵉ texte a raison sur ses deux griefs centraux : « 5/5 exact » était un **certificat** (la durée vient de la pièce ONEC, pas du repo), et « exactement la zone du sujet » était **rhétorique** (22 % = sous-poids, même part en fichiers comme en chapitres). **Ses 5 substitutions sont appliquées** (acte 5 modifié) et **les 4 trous repo qu'il réclamait sont comblés en annexe A de l'acte 5** : table des 10 verbes + appelants, 44→46 expliqué avec D1=22/D2=10/D3=14, grep de la file (0/3 noms), surfaces de score nuancées.

---

## 1. État consolidé — ce qui est ÉTABLI (tout vérifié sur repo, actes 1–6)

1. **0 porte** vers la file (0 lien nulle part) ; la file elle-même ne nomme **ni وضعية, ni نص علمي, ni مخطط** (0 occurrence ; seul فرضية apparaît, en voix de clôture J3).
2. **حلّل absent des 10 verbes runtime** (table collée en A.1) ; le barème `/20` de la base verbes n'est exposé nulle part (le monolithe L2, lui, affiche score/score_max sur `action-verbs/[slug]`).
3. ***باك*** = 23 items : **19 résumés PDF eddirasa + 3 fragments de sujets + 1 recueil 2019** — 0 épreuve ONEC, 0 corrigé, 0 سلم.
4. **n/6 file = checklist auto-cochée + regex de forme** ; le sens scientifique et le سلم ne sont pas évalués — la phrase « corrigé sur le geste » est rayée de la chaîne.
5. **Domaine 2 = 10 chapitres / 46 = 22 %** (D1=22, D2=10, D3=14), le plus maigre — et c'est celui que la pièce 2025 charge dans ses deux sujets.
6. **`students-at-risk` = prénoms + notes lisibles par tout JWT** (0 contrôle de rôle) ; `ingest-rag` protégé par secret.
7. **Durée 2025 = 4 h 30** (cartouche ONEC) ; 3 h 30 et 4 h écartés comme dogmes ; coeff 6 ; 2 sujets ; 5+7+8.
8. **Double progression** : dashboard (localStorage) vs progress (FSRS serveur).
9. **24 verbes UI / 10 évalués** ; seed 5 = données mortes (2 scripts).

---

## 2. Ce qui N'EST PAS établi (et où ça se décide)

| Inconnu | Pourquoi le repo ne peut pas le trancher | Qui le tranche |
|---|---|---|
| **Un JWT d'élève existe-t-il en prod / préprod partagée ?** | hors repo (déploiement) | **le porteur — question fermée ci-dessous** |
| Droits des 19 PDF eddirasa | hors repo (juridique) | porteur |
| Langue des contenus vs copie arabe 2025 | mesurable, non mesuré (chantier) | audit v2 si mot |
| رسم = production graphique réelle | mesurable (composants), non mesuré | audit v2 si mot |
| Interactivité réelle des 5 sims | mesurable, non mesuré | audit v2 si mot |
| Exemple chiffré de divergence dashboard vs FSRS | nécessite données de runtime | porteur / prod |
| Liste admin au-delà de `students-at-risk` | mesurable : 3 analytics + 1 ingest connus — reste le périmètre complet | audit v2 si mot |

---

## 3. Les 5 substitutions demandées — appliquées sur l'acte 5

1. ✅ « Tout … exact (5 vérifications) » → « cinq grep vont dans le même sens ; la durée vient de la pièce, pas du repo ; la table des 10 n'est pas dans cette page ».
2. ✅ « exactement la zone du sujet » → « sous-poids face à un exercice énergie dans les deux sujets 2025. 44 puis 46 expliqué. D1/D3 publiés ».
3. ✅ Grep de la file pour les mêmes trois noms — résultat publié (0/3).
4. ✅ Les 10 verbes collés (annexe A.1).
5. ✅ « Le travail n'a pas commencé » conservé ; « définitif » réservé à la seule phrase tenable : *l'offre actuelle ne peut pas être dite préparatoire à cette copie.*

---

## 4. La question fermée — et rien d'autre

Le 6ᵉ texte a raison : le prochain mot utile n'est pas un 7ᵉ md. C'est :

> **« Un JWT d'élève réel existe-t-il en production ou en préproduction partagée ? »**
> — **Oui** → premier travail : `students-at-risk` (rôle), avant tout `href`.
> — **Non** → premier travail : porte + entrée **الوضعية الإدماجية** (avec النص العلمي et المخطط comme noms d'ateliers sur des écrans existants), puis IAM avant le premier élève.

Toujours : zéro LLM, zéro 4ᵉ écran de concept, zéro scan ONEC dans le git sans filière juridique.
