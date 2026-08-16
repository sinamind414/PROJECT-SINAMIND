# Audit du 4ᵉ niveau — inventaire clôturé, checklist nommée, durée tranchée

> **Date** : 2026-08-16 · **Branche** : `arena/01a0066d-project-sinamind`
> **Objet** : le 4ᵉ texte (audit de ma méta-méta), sans accès dépôt.
> **Méthode** : chaque affirmation vérifiée sur le repo + 1 fait extérieur (durée d'épreuve) tranché par sources web.
> **Ce document modifie** : mes 2 amendements sur `audit-meta-meta.md` (déjà appliqués §6), rien d'autre.

---

## 0. Verdict en une ligne

Le 4ᵉ texte **a raison sur le nœud** (n/6 = checklist auto-cochée + regex, pas une correction de Bac) et **se trompe sur 3 faits** (sims « anonymes », durée « 4 h », et il me prête un sprint « magique »). Il aura servi à fermer l'inventaire : après lui, **tout est mesuré** — reste à choisir.

---

## 1. Ce que je concède net (et j'amende mes docs)

| Grief du 4ᵉ texte | Vérifié sur repo | Réponse |
|---|---|---|
| « Seed 5 = P0 » = homme de paille | Le 3ᵉ texte disait « P0 **seulement si** runtime = seed » — c'est **ma méta** qui l'avait mis en P0. Je lui ai attribué une affirmation qu'il n'avait pas. | **Concession complète** — déjà rétrogradé P2 |
| n/6 = l'élève coche lui-même | **Vérifié** : Phase A = `checkbox onChange={() => toggleCase(i)}` — les 6 cases sont **cochées par l'élève** ; la regex ne tourne que sur le texte (crimes). C'est un **hybride (a)+(b)**. | **Concession — amendement 1 appliqué** : « corrigé sur le geste » remplacé par « checklist auto-cochée + détection de forme ; le sens et le سلم ne sont pas évalués » |
| Le 65 était « Règle d'audit » en tête de MON premier audit | Vérifié : `audit-nav-rubriques.md` porte « Règle d'audit : … 65/100 figé ». La consigne vient du porteur du fil, mais **je l'ai écrite en en-tête et en verdict**. | **Concession** : dans mes docs, le 65 n'est plus cité comme verrou de verdict ; il reste la consigne du porteur, non calculée par moi |
| Sprint : IAM en dernier = ordre inversé si élèves réels | Juste. | **Concession — amendement 4 appliqué** : IAM d'abord si JWT élève réel existe |
| Porte sans nom وضعية = 4ᵉ porte | Juste — 3 entrées méthodo existent déjà dans la nav. | **Concession — amendement 2 appliqué** : porte + nom fusionnés en une entrée « الوضعية الإدماجية », en remplaçant/reléguant une entrée existante, pas en ajout |
| Annales « sans corrigé » trop doux | Juste — et aggravé (voir §3.3). | **Concession — amendement 3 appliqué** : *باك* remontée en P0 produit |

---

## 2. Ses 3 erreurs factuelles — vérifiées contre le dépôt et les sources

### 2.1 « Les 5 simulations toujours anonymes » — **FAUX**

Ma méta §2.5 (écrite **avant** son texte) les nomme déjà : `action-potential` (كمون العمل) · `enzyme-activity` (ExAO) · `mitosis` (رسم) · `photosynthesis` (Hill) · `tectonics`. Le 4ᵉ texte les réclame à nouveau (§5.2) — l'inventaire existait.

### 2.2 « Corriger au passage : 4 heures » — **FAUX aussi, comme le 3 h 30**

Le repo ne contient aucune durée. Sources extérieures consultées :
- **Calendrier Bac 2026** : SVT شعبة العلوم التجريبية = **08h30 → 13h00 = 4 h 30** [4](https://bac-algerie.net/date-bac-algerie.html)
- **Coefficient** : SVT sciences exp = **6** [5](https://sujetbacdz.com/blog/mawad-wa-mouaamalat-chouab-bac)
- **Deux sujets au choix** : confirmé par l'en-tête d'une épreuve 2021 (« على المترشح أن يختار أحد الموضوعين ») [1](https://www.scribd.com/document/607227754/)

→ **Toute la chaîne s'est trompée** : 3 h 30 (2ᵉ texte) faux, 4 h (4ᵉ texte) faux. **4 h 30, coeff 6, 2 sujets** — confirmé ensuite par la pièce ONEC 2025 (cartouche). **Règle durable** : *SNV علوم تجريبية, Bac 2025 (pièce ONEC) : 04 h 30, deux sujets, 5+7+8. Autres sessions : lire le cartouche. 3 h 30 écarté. 4 h = historique fréquent, pas 2025.* La morale de la chaîne tient : sans cartouche ONEC, on invente.

### 2.3 « ~28 devrait être un entier » — fait : **24 exactement**

`ENRICHED_ACTION_VERBS` = **24** : ANALYSIS · INTERPRET · DEDUCE · JUSTIFY · HYPOTHESIS · VALIDATE · COMPARE · SCIENTIFIC_TEXT · DISCUSS · DEFINE · NAME · CITE · RELATIONSHIP · EXTRACT · DESCRIBE · CLASSIFY · DISTINGUISH · DETERMINE · EXPLAIN · SCHEMATIC_FUNCTIONAL · SCHEMATIC_EXPLANATORY · SUMMARIZE_DIAGRAM · COMMENT · CRITICIZE. (Mon « ~28 » venait d'un grep non refermé — son réflexe était le bon.)

---

## 3. Les mesures qu'il réclamait — livrées, avec deux faits neufs que personne n'avait

### 3.1 Les 10 verbes runtime (`methodology/verb_database.json`, v2.0, « Livre Manhajiya Bac SVT »)

| # | Verbe AR | FR | max_score | type |
|---|---|---|---|---|
| 1 | وضّح في نص علمي | Expliquer dans un texte scientifique | **20** | complex |
| 2 | صف | Décrire / Caractériser | 10 | simple |
| 3 | عرف | Définir | 10 | simple |
| 4 | أثبت | Prouver / Démontrer | 15 | complex |
| 5 | برّر | Justifier | 15 | complex |
| 6 | استنتج | Conclure / Déduire | 10 | simple |
| 7 | فسر | Expliquer / Interpréter | 15 | complex |
| 8 | اقترح فرضية | Proposer une hypothèse | 10 | complex |
| 9 | ناقش | Discuter | 15 | complex |
| 10 | أنجز رسما تخطيطيا | **Réaliser un schéma** | 10 | simple |

**Deux faits neufs** :
1. **حلّل (le J1 de la file) est ABSENT des 10 verbes runtime.** La file ouvre sur un verbe que le backend n'évalue pas. (Le front l'affiche — ANALYSIS — mais l'API d'évaluation ne le connaît pas.)
2. **Le schéma existe** — أنجز رسما تخطيطيا, max_score 10 — dans le barème runtime. Le « pan entier sans surface produit » du 2ᵉ texte est donc **couvert dans la base verbes, absent de toute page**. Troisième vérité : l'échelle runtime est **/20 par verbe** (10/15/20), la file est **n/6** — deux échelles coexistantes, ni réconciliées ni confrontées au سلم.

### 3.2 Runtime UI tranché (sa question « que voit l'élève ? »)

La page `action-verbs` affiche **ENRICHED (24)** et appelle l'API pour la **progression** (`getActionVerbs`, `getVerbProgress`). → **l'élève voit 24 verbes, l'API en évalue 10.** 14 verbes affichés sont **décoratifs au sens évaluation**. C'est le cas 2 de son tri-cas : **mensonge d'interface, P1**.

### 3.3 Annales : la matrice des 23 titres — pire que « dropbox muette »

```
23 items = 1×2019 (« 605 Questions de Révision ») + 3×2023 (« Sujet 1 - Protéines et pH »,
« Sujet 3 - ADN et Perméabilité ») + 19×2024 dont :
  · 10 « Méthodologie: …pdf » (منهجية-النص-العلمي, منهجية-الاجابة-على-اسئلة-التحليل…)
  · 7 « ملخص-الوحدةXX…pdf » (résumés eddirasa)
  · 2 recueils d'auteurs (Khelifa, Mohammedi, Brahimi…)
→ 27 exercices, 0 corrigé, 0 سلم, 0 épreuve ONEC complète.
```

**Conclusion aggravée** : la rubrique *باك* n'est pas une banque d'épreuves, c'est une **bibliothèque de résumés et de méthodo scrapés**. Le 4ᵉ texte pressentait « fausse banque » — la réalité est pire que son hypothèse. **P0 produit confirmé et détaillé.**

### 3.4 Le grain des 23 leçons — réglé

23 fichiers = **44 chapitres** (phase1_chapitres_1_2 → phase22_chapitres_43_44 + transcription), grain = **2 chapitres/fichier, séance 20–25 min** (45 mentions « المدة التقديرية للتعلم الذاتي »). Domaines : **11 / 5 / 7 fichiers** → المجال 2 ≈ **10 chapitres sur 44**. Son « zone rouge si leçon = unité » est réglée : ce ne sont pas des unités, ce sont des séances — mais le déséquilibre **5/23 fichiers** pour l'énergie reste un vrai signal de catalogue.

---

## 4. Le nœud pédagogique, tranché une fois pour toutes

La décomposition exacte de la « pastille » des 3 écrans :

| Composant | Qui le produit | Nature |
|---|---|---|
| `خطوات n/6` | **l'élève** (cases cochées à la main) | **checklist auto-déclarée** — posture (a) |
| pastille محترمة/غالطة | **regex** sur le texte tapé | détection de **forme** — posture (b) miniature |
| messages crimes/manques | regex | détection de forme |
| sens scientifique, سلم, barème | **personne** | non évalué |

→ Le vocabulaire honnête est : **« checklist guidée par grille + détection de forme »**. Ni « corrigé », ni « rien ». J'ai appliqué cette correction dans ma méta (amendement 1). Le 4ᵉ texte avait exactement raison de l'exiger — un 6/6 sur checklist ne vaut pas 8/8 au سلم, et personne ne doit croire le contraire dans un doc interne.

---

## 5. Reclassement consolidé v4

| Rang | Risque | Preuve |
|---|---|---|
| **P0 confiance/légal** | `students-at-risk` : prénoms + notes lisibles par tout élève JWT | SQL vérifié |
| **P0 produit** | *باك* = 19 résumés + 3 fragments, 0 épreuve, 0 corrigé, 0 سلم | 23 titres listés |
| **P0 produit** | File **invisible** (0 porte) + وضعية innommée + checklist non سلم | grep + code |
| **P0 usage** | Double progression : dashboard (localStorage) vs progress (serveur) | code |
| **P1** | UI 24 verbes vs évaluation 10 ; **حلّل absent du runtime** | matrice |
| **P1** | Deux échelles : /20 (verb_database) vs n/6 (file) ; grilles vs سلم officiel | matrice |
| **P1** | Domaine 2 = 5/23 fichiers (≈10 chapitres/44) | comptage |
| **P2** | Seed 5 mort · TP en dur · orphelins 15 routes · poids mobile | état |

---

## 6. Amendements appliqués sur mes documents (2 fichiers)

1. `audit-meta-meta.md` §7 : « corrigé sur le geste » → **« checklist n/6 auto-cochée + détection de forme ; le sens scientifique et le سلم ne sont pas évalués »**.
2. `audit-meta-meta.md` §4 : annales remontées en **P0 produit** (19 résumés, 0 épreuve) ; sprint réordonné : **IAM d'abord si élève réel → porte+وضعية fusionnées → annales labelées honnêtes**.
3. (Fait précédemment) orphelins 15 routes plates ; seed P2.

---

## 7. Notation du 4ᵉ texte

| Axe | Note |
|---|---|
| Justesse du nœud pédagogique (checklist vs correction) | **19/20** — c'est la bonne exigeance |
| Précision factuelle | 12/20 — sims anonymes (faux), 4 h (faux : 4 h 30), « sprint magique » (faux : mes items étaient des chantiers) |
| Lecture annales | 16/20 — « fausse banque » confirmé et dépassé |
| Demande d'amendements | 17/20 — les 4 sont justes, je les applique |
| Honnêteté métrique | 14/20 — grief de forme juste sur mon en-tête ; attribue toujours la consigne au mauvais auteur |

**En tant que critique de ma méta-méta : 15/20.**
**En tant que juge d'inventaire : 16/20** (il a forcé la fermeture de tout, au prix de 3 erreurs).

---

## 8. Où la chaîne atterrit — et ce qui reste à choisir

| Texte | A prouvé | A trop dit |
|---|---|---|
| Audit nav | 18 pages existent, file hors nav | « 0 rubrique vide », 65 en règle |
| Contre-expertise | la question est le barème | 3 h 30, « fidèlement » |
| Méta | 23/5/24/16 modules, JWT sans rôle | seed P0, hubs « pas vides » |
| Méta-méta | matrices file×grading, admin qualifié, 11/5/7 | « corrigé sur le geste » |
| **4ᵉ texte** | **checklist ≠ correction**, annales = fausse banque, IAM d'abord | sims anonymes, 4 h |

**Devant le سلم 2025 (pièce ONEC : 04 h 30, deux sujets, 5+7+8, نص علمي ×2, حلّل, مخطط, فرضيتان) :** l'élève plateforme n'entre pas dans la pièce, n'a pas cette copie, coche une checklist, et le verbe **حلّل** du premier document n'est pas dans le barème interne exposé. **On sait pourquoi on ne peut pas dire qu'il gagne des points. On ne l'a pas encore fait gagner.** La référence de comparaison est complète ; la réponse produit, elle, ne l'est pas — c'est une liste de travaux, pas un verdict.
il ne peut **pas entrer** (0 porte) ; s'il entre par deep link, il remplit une **checklist de forme** (pas un سلم) ; la rubrique *باك* contient des **résumés sans corrigé** ; le seul barème réel (/20 par verbe, 10 verbes) **exclut حلّل** et n'est exposé sur **aucune page**. Ce n'est plus une controverse d'audit : c'est une liste de travaux, chacun nommé, chacun avec son ordre.

**Ce que je retiens sans rien exécuter** : l'ordre honnête, si un mot est donné — (1) IAM `students-at-risk` si JWT élève réel, (2) une entrée nommée **الوضعية الإدماجية** qui mène à la file (en remplaçant une entrée méthodo existante, pas une 4ᵉ porte), (3) labeler *باك* « sujets partiels sans corrigé » avant toute promesse, (4) confronter les deux échelles (/20 et n/6) à un سلم officiel. Quatre travaux, zéro LLM, zéro écran de plus.
