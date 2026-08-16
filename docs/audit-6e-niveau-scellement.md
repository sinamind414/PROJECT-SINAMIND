# Acte 6 — Arrêté d'instruction : table des 10 dans le corps, file greppée, grain expliqué, question fermée au porteur

> **Date** : 2026-08-16 · **Branche** : `arena/01a0066d-project-sinamind`
> **Objet** : le 6ᵉ texte (audit de mon acte 5). Vérifications repo faites, 5 substitutions appliquées, table des 10 collée **dans ce corps** (pas en annexe).
> **Ce document** : fin de la controverse d'architecture — **pas** fin de l'audit (3 inspections courtes faites ici ; le git reste ouvert sur ce qui n'a pas été lu).


---

## 0. Verdict

Le 6ᵉ texte a raison sur ses deux griefs centraux : « 5/5 exact » était un **certificat** (la durée vient de la pièce ONEC, pas du repo), et « exactement la zone du sujet » était **rhétorique** (22 % = sous-poids, même part en fichiers comme en chapitres). **Ses 5 substitutions sont appliquées** (acte 5 modifié) et **les 4 trous repo qu'il réclamait sont comblés en annexe A de l'acte 5** : table des 10 verbes + appelants, 44→46 expliqué avec D1=22/D2=10/D3=14, grep de la file (0/3 noms), surfaces de score nuancées.

---

## 1. État consolidé — ce qui est ÉTABLI, recatégorisé (6 git + 1 pièce + 2 conditionnels)

**7 constats git (vérifiés dans les fichiers)** :
1. **0 porte** vers la file (0 lien) ; la file elle-même ne nomme **ni وضعية, ni نص علمي, ni مخطط** (0 occurrence ; seul فرضية apparaît, en voix de clôture J3).
2. ***باك*** = 23 items : **19 résumés PDF eddirasa + 3 fragments + 1 recueil 2019** — 0 épreuve ONEC, 0 corrigé, 0 سلم ; **23/23 titres en latin** (français) contre une copie 2025 **arabe**.
3. **n/6 file = checklist auto-cochée + regex de forme** ; le sens et le سلم ne sont pas évalués.
4. **Domaine 2 = 10 chapitres / 46 = 22 %** (D1 = 22 dont les 2 de `lecon_transcription` ∈ المجال الأول — phase-only D1 = 20 ; D2 = 10 ; D3 = 14), le plus maigre — et c'est celui que la pièce 2025 charge dans ses deux sujets.
5. **`students-at-risk` = prénoms + notes lisibles par tout JWT** (0 contrôle de rôle) ; `ingest-rag` protégé par secret.
6. **24 verbes UI / 10 évalués** ; seed 5 = données mortes (2 scripts).
7. **حلّل ABSENT des 10 verbes runtime** (table §2 ci-dessous — plus une citation : le constat est levé en git établi).
8. **Les 5 sims = SVG réels, aucun canvas** ; geste élève : ActionPotential = **règle** (slider) · Enzyme = **règle + points enregistrés → courbe** · Mitosis = **regarde** (2 boutons) · Photosynthesis = **règle** (sliders) ; **aucune ne fait tracer** un schéma libre → la production d'un مخطط reste non couverte.
9. **Langue des annales : titres FR (23/23) mais corps AR (26/27 exercices)** — le scénario doux : métadonnées en latin, contenu en arabe → P2 de propreté, **pas** P0 d'offre.

**1 constat pièce ONEC (pas le repo)** :
7. **Durée 2025 = 4 h 30** (cartouche) ; 3 h 30 et 4 h écartés comme dogmes ; coeff 6 ; 2 sujets ; 5+7+8.

**2 constats conditionnels (pas encore mesurés à l'instant) ** :
8. **حلّل absent des 10 verbes runtime** — sous condition de la table ci-dessous (§2, collée).
9. **Double progression** (dashboard localStorage vs progress FSRS serveur) — architecture vérifiée, **divergence chiffrée jamais exemplifiée** ; P0 d'architecture, pas constat mesuré.

---

## 2. La table des 10 — collée ici, croisée appelants × file

`methodology/verb_database.json` v2.0 (« Livre Manhajiya Bac SVT Algérie ») :

| # | Verbe (AR / FR) | max_score | evaluator.py | task_classifier.py | mindmap_methodology | **file (3 écrans)** |
|---|---|---|---|---|---|---|
| 1 | وضّح في نص علمي / Expliquer dans un texte scientifique | 20 | ✓ | | ✓ | **✗** |
| 2 | صف / Décrire · Caractériser | 10 | ✓ | ✓ | | ✗ |
| 3 | عرف / Définir | 10 | ✓ | ✓ | | ✗ |
| 4 | أثبت / Prouver · Démontrer | 15 | ✓ | ✓ | | ✗ |
| 5 | برّر / Justifier | 15 | ✓ | ✓ | | ✗ |
| 6 | استنتج / Conclure · Déduire | 10 | ✓ | ✓ | | **✗ (le J3 file n'appelle pas cette base)** |
| 7 | فسر / Expliquer · Interpréter | 15 | ✓ | ✓ | | ✗ |
| 8 | اقترح فرضية / Proposer une hypothèse | 10 | ✓ | ✓ | | ✗ |
| 9 | ناقش / Discuter | 15 | ✓ | ✓ | | ✗ |
| 10 | أنجز رسما تخطيطيا / Réaliser un schéma | 10 | ✓ | ✓ | | ✗ |

**حلّل : ABSENT de la table** (aucune ligne, aucun alias — vérifié sur la liste entière, plus une simple hypothèse grep).
**La file ne charge `verb_database` par aucun des 4 appelants connus** (`methodology/__init__.py` export, `evaluator.py`, `task_classifier.py`, `mindmap_methodology_service.py`).

→ **Le P0 pédagogique « حلّل hors runtime » est désormais opposable hors équipe : la table est dans cette page.**

**Échelles de score — réponse à « score_max vaut 20, 6, 100 ? »** :
- file : pastille + `خطوات n/6` (auto-cochée) ;
- monolithe L2 (`action-verbs/[slug]`) : `score/score_max` affiché — **score_max = somme des points des règles enrichies front** (`enrichedScoringRules.reduce(points)`), **pas** le `max_score` /20 de la base verbes ; échelle variable par verbe ;
- `verb_database.max_score` /20 : **donnée morte côté UI** (0 affichage).

---

## 3. Ce qui reste hors repo — et ce qui n'y était pas

**Vraiment hors repo** : droits des 19 PDF eddirasa (juridique) · **un JWT d'élève réel existe-t-il en prod ?** (ops/secret).

**Dans le repo, maintenant inspecté court** (ce n'est plus « intranchable ») :
- **Langue** : 23/23 titres d'annales en latin vs copie 2025 arabe — écart mesuré ; profondeur (corps des leçons bilingues) non chiffrée.
- **Dessin réel** : les 5 sims ont canvas/SVG (greppé) ; la **production** graphique par l'élève (upload/dessin) n'a pas été vérifiée — à vivre, pas à grepper.
- **`lecon_transcription`** : ∈ المجال الأول (breadcrumb vérifié) — D1 = 20 phase + 2 = 22 ; le 22/10/14 est juste tel quel.

---

## 4. Les 5 substitutions demandées — appliquées sur l'acte 5

1. ✅ « Tout … exact (5 vérifications) » → « cinq grep vont dans le même sens ; la durée vient de la pièce, pas du repo ; la table des 10 n'est pas dans cette page ».
2. ✅ « exactement la zone du sujet » → « sous-poids face à un exercice énergie dans les deux sujets 2025. 44 puis 46 expliqué. D1/D3 publiés ».
3. ✅ Grep de la file pour les mêmes trois noms — résultat publié (0/3).
4. ✅ Les 10 verbes collés (annexe A.1).
5. ✅ « Le travail n'a pas commencé » conservé ; « définitif » réservé à la seule phrase tenable : *l'offre actuelle ne peut pas être dite préparatoire à cette copie.*

---

## 5. La question fermée — et rien d'autre

Le 6ᵉ texte a raison : le prochain mot utile n'est pas un 7ᵉ md. C'est :

> **« Un JWT d'élève réel existe-t-il en production ou en préproduction partagée ? »**
> — **Oui** → premier travail : `students-at-risk` (rôle), avant tout `href`.
> — **Non** → premier travail : porte + entrée **الوضعية الإدماجية** (avec النص العلمي et المخطط comme noms d'ateliers sur des écrans existants), puis IAM avant le premier élève.

Toujours : zéro LLM, zéro 4ᵉ écran de concept, zéro scan ONEC dans le git sans filière juridique.
