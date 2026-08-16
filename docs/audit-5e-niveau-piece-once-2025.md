# Acte 5 — La pièce ONEC 2025 : lecture expert vérifiée sur repo, corrections appliquées

> **Date** : 2026-08-16 · **Branche** : `arena/01a0066d-project-sinamind`
> **Objet** : la lecture expert du sujet officiel SNV Bac 2025 (document externe, non présent dans le repo — je n'audite **pas** le sujet, je vérifie ce que la lecture affirme du dépôt, et j'applique sa correction canonique).
> **Méthode** : repo pour tout ce qui est repo ; le cartouche (04 h 30, 5+7+8, نص علمي, حلّل, مخطط, فرضيتان) est pris comme **déclaration de lecture d'une pièce ONEC** que je ne peux pas revérifier ici.
> **Modifications** : 2 amendements sur `audit-4e-niveau.md` (déjà appliqués), rien d'autre.

---

## 0. Verdict en une ligne

La lecture expert est **la pièce qui manquait** : elle fournit la norme de comparaison (un vrai sujet + سلم) contre laquelle tout l'inventaire se relit. **Chaque affirmation vérifiable sur le repo est exacte.** La chaîne d'audits ne peut plus dire « la réponse est complète » — corrigé (elle dit désormais : *la référence de comparaison est complète, on ne l'a pas encore fait gagner*). La durée 2025 est actée : **4 h 30, ni 3 h 30, ni 4 h**.

---

## 1. Ce que la lecture affirme du dépôt — vérifié point par point

| Affirmation | Vérification repo | Verdict |
|---|---|---|
| نص علمي / وضعية / مخطط **innommés en surface** | grep dans `Sidebar.tsx` + `methodology` + `action-verbs` + `document-analysis` : **0 occurrence** | ✅ exact |
| Barème `/20` (max_score) **jamais exposé** | grep `max_score` dans tout le front : **0 affichage** | ✅ exact |
| حلّل **hors des 10 verbes runtime** | `verb_database.json` : 10 verbes listés, **حلّل absent** | ✅ exact (vérifié à l'acte 4) |
| Domaine 2 sous-doté → « 5/23 fichiers → ?/44 » | calcul exact : **5 fichiers = chapitres 21–30 = 10 chapitres / 46 = 22 %** — et c'est exactement la zone du sujet 2025 (photosynthèse ex.2 + glycolyse) | ✅ chiffré : **10/46** |
| *باك* = 19 résumés eddirasa + 3 fragments, 0 épreuve ONEC | 23 titres listés (acte 4) | ✅ exact |
| « Les 5 sims ne sont pas dans le texte que j'audite » | `audit-meta-meta.md` §2.5 (le texte audité par le 4ᵉ) **contient** les noms : كمون العمل · ExAO · رسم · Hill · tectonics | ⚠️ exact seulement si le 4ᵉ texte a lu un état antérieur du fichier ; dans le fichier committé, les noms y sont — point clos, sans importance |
| Durée : ni 3 h 30 (Bac FR) ni 4 h (dogme) — 2025 = 4 h 30 | calendrier 2026 (08h30→13h00) + lecture du cartouche ONEC 2025 | ✅ acté : **4 h 30 pour 2025**, autres sessions = cartouche |

**Sa phrase-clé, que j'adopte** : *« un créneau horaire n'est pas une durée » — cède devant le cartouche.* Les deux phrases coexistent, et c'est la règle durable écrite en §9 de sa lecture, reprise dans mes docs.

---

## 2. Ce que la pièce casse dans la chaîne (recension honnête)

| Texte | A dit | Face à la pièce ONEC 2025 |
|---|---|---|
| Contre-expertise | 3 h 30 | **Faux** |
| 4ᵉ texte | « corriger : 4 heures » | **Faux pour 2025** (historique possible d'autres sessions) |
| Mes actes 3–4 | « 4 h 30 via calendrier » | **Corroboré par le cartouche** — et ce n'était qu'un créneau, il a raison de l'avoir dit |
| Méta-méta | « l'élève est corrigé sur le geste » | **Déjà remplacé** (checklist) à l'acte 4 — la pièce rend le remplacement définitif : un 6/6 cochable perd le 1,25 RIP |
| Acte 4 | « la réponse est complète et vérifiée » | **Corrigé maintenant** : la **référence** est complète, la réponse produit est une liste de travaux |
| Chaîne entière | « deux exercices + وضعية » | **3 exercices, le 3ᵉ (8 pts) = l'intégration** — la وضعية n'est pas un 4ᵉ écran, c'est l'exercice 8 points |

---

## 3. Ce que la lecture apporte de neuf à l'inventaire produit

1. **Le سلم réel est une échelle 0,25 → 1,25 / 20** (intro au مشكل 0,5 · rôles ARNm/ARNt/ARNr 0,5 ×3 · RIP 1,25 · conclusion 0,5). Les 4 échelles coexistantes de la plateforme — n/6 (file) · /20 caché (verb_database) · grading/ hors file · سلم État — ne se « réconcilient » pas : **on choisit ce qui s'affiche et on borne le reste.**
2. **النص العلمي = 5 pts, exigé deux fois** — objet distinct de fassir/istintaj (intro qui pose le مشكل → corps notionnel → conclusion), **0 entrée nommée**.
3. **حلّل ouvre l'exercice documents des deux sujets** — l'absence du runtime n'est plus un détail de JSON : c'est **P0 pédagogique**.
4. **Le schéma est exigé** (« وضّح في مخطط », S1 ex.3) — le verbe `أنجز رسما تخطيطيا` (max_score 10) existe dans la base mais **aucune surface ne le sert**.
5. **« تًقبل الإجابات بكل طريقة تؤدي إلى نفس النتيجة »** (corrigé) = la borne honnête du 0-LLM : une regex de forme ne peut pas honorer cette phrase. Le miniature (a)+(b) mécanique vaut pour J-90, pas pour le 1,25 du mécanisme.

---

## 4. Reclassement v6 — adopté, avec deux précisions chiffrées

| Rang | Risque | Précision repo |
|---|---|---|
| **P0 offre** | *باك* n'ouvre pas une copie type 2025 + سلم | 23 items = 19 résumés + 3 fragments + 1 recueil ; 0 épreuve, 0 corrigé |
| **P0 trouvabilité** | 0 lien file · وضعية/نص علمي/مخطط innommés | grep = 0 en surface ; porte = 0 lien |
| **P0 légal** | `students-at-risk` (prénoms+notes, JWT sans rôle) · 19 PDF eddirasa (droits tiers) | SQL vérifié (acte 3) |
| **P0 pédagogique runtime** | حلّل absent du /20 · /20 jamais affiché · n/6 ≠ سلم | 10 verbes listés, 0 affichage max_score |
| **P1 catalogue** | Domaine 2 = **10 chapitres / 46 (22 %)** face à une session qui l'exige deux fois | calcul exact |
| **P1 doctrine note** | 4 échelles coexistantes — on borne, on n'additionne pas | état |
| **P1 confiance UI** | 24 verbes affichés / 10 évalués · نسقسي 0-LLM non inventorié | état |
| **P2** | seed 5 mort · TP en dur · orphelins 15 routes | état |

**Sprint (sur mot uniquement, si JWT élève réel existe)** — repris de sa lecture, ordre inchangé :
0. IAM `students-at-risk` → 1. **une** entrée **الوضعية الإدماجية** (+ نص علمي + مخطط comme noms d'atelier sur des écrans déjà là, zéro 4ᵉ concept) → 2. *باك* : retirer la promesse tant qu'une copie type + سلم n'existe pas ; reclasser eddirasa en fiches de cours ; **ne pas coller le sujet scanné sans filière juridique ONEC** → 3. Doctrine : pastille = auto-éval de forme ; publier les 10 verbes ; réintégrer حلّل dans le runtime ou cesser de parler de verbes d'épreuve ; ne pas afficher un /20 comme note Bac.

---

## 5. Corrections appliquées (2, sur mes documents)

1. `audit-4e-niveau.md` §8 : « la réponse est complète et vérifiée » → **« Devant le سلم 2025 … On sait pourquoi on ne peut pas dire qu'il gagne des points. On ne l'a pas encore fait gagner. »**
2. `audit-4e-niveau.md` §2.2 : règle durable des durées écrite : **4 h 30 pour 2025, cartouche pour les autres, 3 h 30 écarté, 4 h = historique.**

---

## 6. Notation de la lecture expert

| Axe | Note |
|---|---|
| Justesse sur le repo (5 vérifications) | **19/20** — tout ce qui était vérifiable est exact |
| Lecture du سلم (0,25–1,25, équivalence de sens) | **18/20** — la borne du 0-LLM est la bonne |
| Retrait discipliné de ses propres erreurs (4 h) | **18/20** — rare dans cette chaîne |
| Demande de correction | **17/20** — deux phrases remplacées, appliquées |

**En tant que lecture d'une pièce officielle : 18/20.**
**En tant que fin de chaîne : elle ne clôt rien — elle fournit la norme. Le travail, lui, n'a toujours pas commencé.**

---

## 7. Où la chaîne atterrit — sans opinion

Cinq tours, une leçon stable : **chaque niveau a gagné en précision en vérifiant, et s'est trompé chaque fois qu'il a affirmé sans pièce** (3 h 30, 4 h, seed=runtime, « corrigé », « complet »). La pièce ONEC 2025 est la seule norme qui restera vraie hors repo. Contre elle :

- l'élève **n'entre pas** (0 porte) ;
- s'il entre, il **coche** une checklist, ne compose pas un نص علمي ;
- *باك* lui montre des **résumés** sans corrigé ;
- le verbe qui ouvre l'exercice documents, **حلّل**, n'est pas dans le barème interne exposé ;
- les trois noms qui font les 13 points (نص علمي + وضعية + مخطط) n'existent **nulle part en surface**.

Ce n'est plus une controverse. C'est un plan de travaux, chaque item nommé, chaque item avec sa preuve. Le premier mot qui lancera le sprint devra dire si un JWT d'élève réel existe — c'est lui qui décide si on commence par l'éthique ou par la porte.
