# Réponse audit S1 (F1–F7 + 2ᵉ verdict)

**Date :** 2026-08-27  
**L’auditeur n’avait pas le code.** On a le code. `GRADER_VERSION = 1.1.2`, flag **off**.  
**Règle :** faits / hypothèses / jugement. **0 code** dans ce tour.

---

## Verdict (le nôtre, pas le leur)

S1 est un **prof local testable** pour **10 grilles**. Ce n’est **pas** le correcteur du site.

- Flag `LOCAL_RUBRIC_GRADER=false` : **déjà**. Rien à « garder off ».
- **S2** = brancher `POST /api/grade` sur ScenarioRunner **et** tuer le JS. Pas une mise en ligne Bac.
- **Publication du site** = S0 (T2/T3/T1). Ça **n’a rien à voir** avec `grade()`. L’IDOR Bac blanc est **déjà** en prod, flag ou pas.

Le 2ᵉ verdict (« pas prêt pour S2 ni pour un élève ») **mélange** trois choses :

| Chose | Statut |
|---|---|
| Sécurité site (IDOR, XP) | **Vrai**, prod, indépendant du grader |
| Limite 0 LLM (sac de mots ≠ compréhension) | **Assumée** depuis le jour 1 — hors-objectif |
| Trous L0 (association chiffres, dilution stuffing, tests faibles) | **Vrais**, hygiène / S2, **pas** un capotage du châssis |

On **ne** crée **pas** `Observation` / `cites_relation` / `theme_min_hits=2` aujourd’hui.

---

## F1 / P0 — S0 ouvert (IDOR, XP, PDF)

**Fait — vérifié dans le code.**

`bac_blanc.py` : `SELECT … FROM bac_sessions WHERE id = :sid` **sans** `user_id` sur choose / save / submit / GET correction. Un JWT peut lire/écrire **une autre** session si il a l’UUID.

`POST /api/gamification/points/add?points=` et `POST /api/avatar/add-xp?xp=` : entier **client**. Fraude triviale.

PDF LFS ~131 o : déjà documenté.

**Jugement.** Gravité **prod**, pas grader. Le gate cible « S0 avant S1 » a été **contourné volontairement** (moteur testable, flag off). L’auditeur a raison : ça n’efface pas l’IDOR.

**Décision.** Pas de hotfix dans ce tour (tu n’as pas dit « hotfix T2 »). Si tu dis **hotfix T2** : `WHERE id=:sid AND user_id=:uid` + test 403 croisé, **sans** toucher `grade()`.

---

## F2 — `theme_min_hits=1`

**Fait.** Les 10 grilles = 1. G13 géologie sur yeast → `off_topic` (la copie n’a **aucun** variant yeast).

**Hypothèse auditeur.** « البناء الضوئي » une fois dans une copie respiration → passe.  
Sur L0 yeast, le thème c’est خميرة/غلوكوز, pas البناء الضوئي. Une mention incidente d’un **autre** chapitre **ne** sauve **pas** le filet.

**Jugement.** ≥ 2 hits distincts **en CI** sur analyse/interpret = faux hors-sujet sur une حلّل courte (`الخميرة` + `18` + `كلما`). Mentir.

**Décision.** Défaut **1 conservé**. Règle **auteur** L1 si un variant est trop générique. **Refusé** comme bloqueur S2.

---

## F3 — errata 10⁶ silencieux hors ARNr/ARNt

**Fait.** C’est **verrouillé** (دليل p.25 + tests) :

- 10⁶ **à côté** ARNr 5S/S5 ou ARNt → jaune, status **ok**, **pas de cap**
- 10⁶ **sans** ces mots → **silence**
- 10⁴ correct → silence

**Jugement.** Élargir à « 10⁶ + n’importe quel mot synthèse protéine → jaune générique » = faux positifs (n’importe quelle notation scientifique). Le livre se trompe sur **deux** masses, pas sur tout 10⁶.

Le « ok sans cap si contexte mal détecté » : le contexte **est** ARNr/ARNt, pas un classifieur flou. Goldens **déjà là** (présent / absent / ARNt).

**Décision.** **Ne pas** changer le filet 10⁴.

Le diagnostic unique vs flags : **déjà corrigé en 1.1.2** — `تصويب الدليل` s’ajoute à `next_step` même si le code n’est pas `science.erratum`. `science_flags` reste une liste.

---

## F4 / §8 — stuffing par dilution

**Fait.** Formule : tokens ≥ 20 **et** ratio > 0.60 **et** pas de keypoint/objet, **ou** distractor.

Ajouter 40 mots vides **peut** faire tomber le ratio. C’est un **garde-fou contournable**, pas un mensonge sur une copie honnête.

**Décision.** Borne absolue (ex. ≥ 10 hits lexique, 0 ancrage) = **S2**, pas S1. On n’y touche pas maintenant.

---

## F5 / §10 — les tests existent ; ils ne font pas 80×8

**Fait.** L’auditeur n’a pas vu les fichiers. On les a.

Golden L0 (`test_rubric_l0.py`) :

| Scénario | Couverture |
|---|---|
| vide | 10/10 |
| modèle ≥ 85 | 10/10 |
| partielle (coupe 1/3 — **faible**) | 10/10 |
| 36 ATP → cap | 10/10 |
| hors-sujet géologie | 10/10 |
| stuffing thème (assert **OU** %≤50 **OU** error — **poreux**) | 10/10 |
| verb_slip | **2** grilles (yeast analyse + interpret) |
| désordre | **1** grille (yeast) |

Plus G1–G8, G12–G15, errata 10⁴, N1–N10. ~108 pytest `--noconftest`.

**Manque (vrai) :** relation **inversée**, chiffres **permutés** (9 vs 18), dilution stuffing, G17 (2 rubrics), G18 mixte AR/FR, unités.

`--noconftest` : le conftest charge FastAPI. `grade()` **n’importe pas** FastAPI. Isolation moteur **OK**. Bruit de repo, pas un 2ᵉ cerveau.

**Décision.** Goldens négatifs **par grille** = S2 (déjà écrit dans la cible). Pas un capotage S1.

---

## F6 / §9 — deux normaliseurs

**Fait.** `arabic.normalize_arabic` (méthode) ≠ `savoir_corrector._normalize` (graves, possessifs). Documenté. Fusion **interdite** sans rejouer le golden Savoir.

**Décision.** Pas S2 obligatoire. Test de cohérence croisée = hygiène **quand** on fusionne (S3+).

---

## F7 — FSRS / observabilité absents du doc S1

**Fait.** Persistance = S4. Observabilité = ajoutée dans la **cible** §7.1, pas dans le moteur (0 I/O, P7).

**Décision.** Rien à coder dans `grade()`.

---

## §4 — « la méthode n’est pas la présence de mots »

**Fait.** 0 LLM ⇒ on coche des **indices** de grille, pas une compréhension. C’est **hors-objectif** depuis le papier.

Manhadjiya حلّل L0 : objet + **un** chiffre du doc + كلما + conclusion, **sans** لأن.  
Une relation **inversée** avec كلما passe aujourd’hui. **Vrai trou.**

**Jugement.** `Observation` / `cites_relation` = **L1**, écrit **à la main** par grille (condition → valeur), **pas** un nouveau moteur. Sans ça, on **annonce** : « indices formels + chiffres du document », déjà la promesse.

**Décision.** Pas de nouveau schéma maintenant.

---

## §5 — chiffres sans unité / mauvais objet

**Fait.** `cites_keypoint` = **n’importe quel** nombre ∈ `{9, 18, 6, 4}` (yeast) ± tolérance. L’unité du JSON **n’est pas** exigée. Un `4` (heures) ancre autant qu’un `18`.

Les 4 analyse L0 **n’utilisent pas** `cites_trend` (donc `يتناقص` dans les variants yeast est du **bruit de fichier**, pas un juge).

**Jugement.** Pour L0, une case « valeur du document » = ≥1 vrai chiffre, **pas** l’association 18↔glucose. L’association est le métier de فسّر (cause) / de critères `all_of` **si l’auteur les écrit**.

**Décision.** Pas de classe `Observation` en S1. Hygiène auteur : ne pas mettre `4` (durée) comme keypoint d’ancrage si on veut seulement 18/6 — **dette JSON**, pas moteur.

---

## §6 — un diagnostic vs plusieurs flags

**Fait.** `diagnosis.code` = un. `science_flags` = liste. v1.1.2 : le jaune 10⁴ n’est **plus** masqué.

**Décision.** Pas de champ `display_messages`. L’UI cible montre déjà منهج + محتوى + 2 phrases.

---

## §7 — cap 40 %

**Fait.** Choix **écrit** : science error → overall ≤ 40. L’UI cible **sépare** منهج et محتوى. Bannière : ليست علامة بكالوريا.

**Décision.** On **garde** le cap. On **n’affiche pas** le 40 comme seul cercle. Pas de « overall non calculable ».

`schematiser` : déjà un message poli, 0 auto. Pas un 0 silencieux.

---

## §11 `cacheable` dans `GradeResult`

Hygiène S2 : la **route** décide. Champ = indice. G2 hors `from_cache`. **Pas bloquant.** Pas de Redis dans `grade()`.

---

## §12 `source_ref` sur les grilles

Utile **L1** (دليل p.25 vs livre). Pas exposé élève. **Pas S1.**

---

## Table d’actions (la nôtre)

| # | Action | Quand | Code maintenant ? |
|---|---|---|---|
| T2 IDOR | `user_id` sur **toutes** les routes session | dès que tu dis hotfix | **non** |
| T3 XP | supprimer query libre | idem | **non** |
| T1 PDF | UI « غير متاح » | publication | **non** |
| C1 clé cache | `rubric_id` + `doc_id` | **dans** S2 | spec **déjà** corrigée |
| Goldens négatifs | relation inversée, 9≠18, dilution | S2 | **non** |
| Stuffing borne abs. | ≥10 hits, 0 ancrage | S2 | **non** |
| `theme_min_hits≥2` | — | **jamais** en CI L0 | **non** |
| Filet 10⁶ élargi | — | **non** | **non** |
| `Observation` | — | L1 auteur | **non** |
| Fusion normalize | replay Savoir | S3+ | **non** |

---

*S1 tient son contrat : 0 LLM, 10 grilles, pas de % Bac. L’IDOR est un trou **du site**, pas du correcteur. Le 2ᵉ audit décrit bien les limites d’un juge lexical — c’est le produit, pas un bug à « réparer » par un 2ᵉ cerveau.*
