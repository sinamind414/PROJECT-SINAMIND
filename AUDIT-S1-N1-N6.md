# Réponse 3ᵉ passe (N1–N6) — mesurée sur `grade()` 1.1.2

**Date :** 2026-08-27  
**Méthode :** copie collée dans `grade_question()`, pas un raisonnement sur la spec.  
**Flag :** toujours `false`. **Pas de code** dans ce tour.

L’auditeur n’a **pas** relancé le moteur. Plusieurs chiffres de sa narrative sont **faux**. Un trou **réel** existe, ailleurs que là où il le met.

---

## N1 — dump numérique : mesuré, pas 50 % جزئي

Copie exacte de l’audit, 4 grilles `analyse` :

```
1 2 3 4 5 6 7 8 9 10 20 37 80 100 0 2,5 4,8 18 6 10 5
```

| Grille | sanity | method | label | overall | science | stuffing | cases full |
|---|---|---|---|---|---|---|---|
| enzyme-temp-analyse | `defer` | **1,5 / 4 → 38 %** | **غير كاف** | 38 | `error` خارج الموضوع | false | keypoint + **no_cause** |
| yeast-analyse | idem | 38 % | غير كاف | 38 | hors-sujet | false | idem |
| greffe-ltc-analyse | idem | 38 % | غير كاف | 38 | hors-sujet | false | idem |
| photo-o2-analyse | idem | 38 % | غير كاف | 38 | hors-sujet | false | idem |

`37 80 100` (court) → **`too_short`, 0 %**. Pas l’exploit.

`الوثيقة 37 80 100` → sanity **ok**, **2,25 / 4 = 56 %** جزئي (objet + keypoint + no_cause). Ça, un prof peut le donner en partiel (الوثيقة + chiffres, sans كلما).

### Ce que l’auditeur a **faux**

1. **« 2/4 = 50 %, جزئي »** — mesuré **38 %, غير كاف**, diagnostic **hors-sujet**.
2. **Le correctif (a)** « stuffing seulement si keypoint **et** objet » **ne ferme pas** ce dump : le ratio lexique d’une liste de nombres est **déjà ~0**, donc `< 0.60`. L’exemption keypoint est **hors-jeu** ici. Stuffing n’est pas le chemin.

### Ce qui est **vrai**

Le dump **passe** l’étage [0] au lieu d’être `not_arabic` → 0.

**Cause code, une ligne :**

```python
# local_grader._chemistry_signal_count
return len(_CHEM_TOKEN_RE.findall(text)) + min(3, len(_DIGIT_RE.findall(text)))
```

`min(3, nb_chiffres)` : **2 chiffres suffisent** à `defer` (on continue).  
G7 (`38 ATP · P/O=3`) n’a **pas besoin** de ça : `ATP` et `P/O` sont déjà dans `_CHEM_TOKEN_RE`.

Les **1,5 pts** viennent de :

| Case | pts | Pourquoi |
|---|---|---|
| `cites_keypoint` | 1,0 | 37/80/100 **sont** les chiffres du doc — la case fait ce qu’on lui a dit |
| `forbidden_abs` (no_cause) | 0,5 | pas de لأن → **cadeau** à toute copie muette |

Le « mensonge » n’est pas 50 % جزئي. C’est : **une copie sans arabe n’est pas à 0**, à cause des **digits = chimie** + le cadeau `forbidden_abs`.

### Décision (pas codée)

Hotfix N1 **propre** (2 lignes, golden) :

1. **Digits seuls ≠ chimie.** `defer` seulement si ≥ 1 vrai token de la liste fermée (`ATP`, `ADP`, `NADH`, `CO2`, `O2`, `P/O`, `pH`, `°`, flèches…). Dump `1 2 3 37 80` → `not_arabic` → **0**. G7 inchangé.
2. Golden : dump ci-dessus → `sanity=not_arabic`, method **0**, jamais ≥ 1 pt.
3. Option plus tard : `forbidden_abs` ne paie que si **une** case positive est `full` (sinon le silence rapporte 0,5). Pas obligatoire pour fermer N1.

Correctifs (a) stuffing+objet, (b) plafonner tout `defer` à 25, (c) arabe obligatoire dans `cites_keypoint` : **trop large** (cassent G7 / copies mixtes ATP).

**Si tu dis `hotfix N1` : on fait (1)+(2), rien d’autre.**

---

## N2 — séparateurs / exposants : **oui, partiel**

Mesuré `normalize_arabic` :

| Entrée | Sortie | Parse keypoint |
|---|---|---|
| `2,5` / `2.5` | inchangé | **2,5 OK** |
| `٢٫٥` (U+066B) | `2٫5` | **2 et 5**, pas 2,5 — **faux négatif** |
| `10⁶` | `106` (NFKC) | collision 106 |
| `٣٦٪` | `36٪` | 36 lu (٪ ignoré) |

Errata دليل (sur le **brut**, pas N1–N10) :

- `ARNr 5S 3.6×10^6` → jaune **OK**
- `ARNr 3.6·10^6` → jaune **OK**
- `ARNr 3.6e6` → **silence** (trou)
- `3.6×106` sans ARNr → silence (**voulu**)

**Décision.** Étendre N8 (`٫`→`.` , `٬` supprimer, `٪`→`%`) = **juste**, avant S2 si on note des copies manuscrites OCR. Parser `3.6e6` dans l’errata = hygiène. **Pas** un parseur scientifique général (hors contrat fermé). Collision NFKC `10⁶`→`106` : l’errata ne passe **pas** par `normalize_arabic` — déjà isolé.

---

## N3 — en-têtes نص علمي

La grille **n’utilise pas** `section_markers`. C’est du `any_of` (مشكل، نسخ، ترجمة، خاتمة) + `min_length` 80.

Copie « en-têtes + lexique » mesurée : **toutes** les cases `full`, puis **stuffing → 50 % جزئي**. Pas 100 %. Pas متقن.

**Décision.** Pas un P0. Minimum de tokens **par** section = L1 auteur, pas un nouvel étage.

---

## N4 — proclitiques : **l’auditeur se trompe**

On **n’efface pas** la copie. On **ajoute** des préfixes au *needle* (`فكلما`, `النمو`).

Mesuré : `كن` **ne** matche **pas** `لكن`. `لكن` matche `لكن`. Pas de « لكن → كن ».

**Décision.** Rien à changer. Le contrat peut dire : « expansion du needle, pas strip du texte ».

---

## N5 — `tolerance=0`

**Fait.** Les JSON L0 mettent `0`. Le `model_answer` a les valeurs exactes. Un élève qui lit `6,2` sur un graphe « 6 ml » perd le point.

**Jugement.** Règle **auteur** (`tolerance: 0.5` sur une courbe), pas un défaut moteur à 5 %. On n’invente pas ±0,5 global.

`cites_observation` = **L1**, déjà refusé en S1.

---

## N6 — contrat

| Champ | Déjà dans le code | Manquait au papier S1 |
|---|---|---|
| `too_short` | `MIN_LENGTH=8` glyphes hors espaces | oui — **déjà** dans la cible §6.2 depuis C3 |
| `not_applicable` | stop sanity + `schematiser` | oui, à une ligne |
| tokens chimie | `_CHEM_TOKEN_RE` + **digits** | liste **pas** fermée — c’est **N1** |

Matrice G1–G16 : elle est dans `ARCHITECTURE-COACH-LOCAL.md` §13 + `tests/test_local_grader.py`. L’auditeur n’a pas ouvert les tests. `AUDIT-GRADER-LOCAL.md` existe.

Clé cache : **déjà** corrigée dans la cible (C1). Pas « à spécifier ».

`theme_min_hits≥2` : **toujours refusé** (passe 2).

---

## Bloqueurs « encore ouverts » — statut vrai

| Ils disent encore ouvert | Statut réel |
|---|---|
| S0 IDOR/XP/PDF | **Vrai**, prod, pas le grader |
| Goldens négatifs absents | **Partiel** — G6/G13/G14 existent ; dump/relation inversée **non** |
| `theme_min_hits=1` | **Voulu** |
| Clé cache sans identité | **Faux** — corrigée dans la cible, cache **inexistant** dans `grade()` |
| G1–G16 invérifiable | **Faux** — fichiers tests + AUDIT-GRADER-LOCAL |

---

## Priorités (les nôtres)

| P | Action | Code maintenant |
|---|---|---|
| P0 site | T2/T3 si tu dis **hotfix T2** | non |
| **P0 moteur** | **hotfix N1** : digits ≠ chimie + golden dump → 0 | **si tu le dis** |
| P1 | N8 `٫٬٪` | si copies OCR |
| — | (a) stuffing+objet, (b) cap defer, `theme_min_hits=2`, `Observation` | **non** |

---

*Le dump n’affiche pas 50 % جزئي. Il affiche 38 % غير كاف hors-sujet — encore trop pour une copie sans arabe. Le trou c’est `digits → defer`, pas le stuffing.*
