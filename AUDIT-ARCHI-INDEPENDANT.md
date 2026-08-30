# Réponse à l’audit indépendant (A1–A10, C1–C5)

**Date :** 2026-08-27  
**Cible auditée :** `ARCHITECTURE-COACH-LOCAL.md` (contrat papier)  
**Code as-built :** `local_grader.py` 1.1.2 — flag **off**, **0 cache Redis**  
**Règle :** faits / hypothèses / jugement. 0 LLM sur le chemin de note.

---

## 0. Deux documents, deux verdicts

L’audit juge le **contrat cible** (ce que le papier promet).  
`AUDIT-GRADER-LOCAL.md` juge le **code**. Ils ne disent pas la même chose sur A2 et A6 — c’est normal.

| # | Papier (cible) | Code (as-built 1.1.2) |
|---|---|---|
| A1 0 LLM | OUI | OUI — G1 AST |
| A2 1 moteur | OUI *promesse* | **NON** — `grade()` existe, 5 cerveaux encore en prod |
| A3 Rubric git | OUI | OUI L0 ; prod = `VERB_RULES` |
| A4 pas /20 Bac | OUI | OUI dans `GradeResult` ; UI bac_blanc **pas** touchée |
| A5 Savoir = filet | OUI | OUI |
| A6 T1–T3 listés | OUI *listés* | **NON faits** |
| A7 mapping code | OUI | OUI (deux `normalize` encore) |
| A8 hors-sujet → error | OUI | OUI `theme_min_hits` |
| A9 chiffre bidon ≠ DA | OUI | OUI `cites_keypoint` |
| A10 N1–N10 fermé | OUI | OUI testé |

**Jugement :** l’auditeur a raison de dire que le **papier** tient A1–A10. Il a tort s’il en déduit que le **site** note déjà comme ça. Flag `false` = l’élève n’est pas noté par `grade()`.

---

## 1. C1 — clé de cache sans `rubric_id`

**Fait.** La clé papier était :

```
grade:{GRADER_VERSION}:{rubric.version}:{doc.version|none}:{verb}:{hash_answer}
```

Les 10 grilles L0 ont toutes `version=1.0.0`. Quatre questions partagent le verbe `analyse`.  
Le scénario « même copie générique collée sur Q1 puis Q2 → note de Q1 » est **réel pour cette spec**.

**Fait.** `grade()` est pur (P7) : **aucun Redis**. `GradeResult.cacheable` / `from_cache` existent ; `from_cache` reste toujours `False` aujourd’hui. G2 (3× même résultat) est vert **parce qu’il n’y a pas de cache**.

**Jugement.** Ce n’est **pas** un mensonge live. C’est un **piège S2**. Si on branche `/api/grade` avec l’ancienne clé, là oui on mentirait sur le %. L’auditeur sur-classe « défaut de justesse bloquant » : bloquant **avant S2**, pas avant de relire le moteur.

**Décision (faite dans la spec) :**

```
grade:{GRADER_VERSION}:{rubric_id}:{rubric.version}:{doc_id|none}:{doc.version|none}:{verb}:{hash_answer}
```

P6 reformulé : version ≠ identité. G17 ajouté. Option ceinture : `sha16` du JSON canonique.  
G2 compare **hors** `from_cache` (posé par la **route**, jamais par `grade()`).

**Pas de code cache aujourd’hui** — on n’implémente pas Redis dans le grader.

---

## 2. C2 — hash-only vs survie L1

**Fait.** P8 = copie jamais en clair sur le chemin grade. §15 parie L1 sur `$lex:` + templates + mixins **écrits à la main**, pas sur un mineur de copies prod.

**Hypothèse de l’auditeur :** sans variance réelle des copies, le lexique reste aveugle → faux 0.  
**Vrai à l’échelle.** **Faux** comme contradiction L0/L1 immédiat : L1 = index DA complet **ou** `ungraded` honnête + mixins S5. Ça ne *nécessite* pas de relire les copies.

**Décision (tranchée, §15) :**

1. Auteur humain + `$lex:` / `_SYNONYMS` + mixins — **plan L1**
2. Fréquence de **hash** (HMAC les plus fréquents parmi error / % < 40) — le prof reproduit en classe, 0 plaintext
3. Récolte enseignant **opt-in**, table séparée — produit à part, pas v1

On **refuse** de casser P8 « pour enrichir le lexique ». Ce n’est pas un problème de chemin de note.

---

## 3. C3 — sanity vs code-switching AR/FR

**Fait.** Le seuil **existe dans le code**, pas dans l’ancien papier :

| Constante | Valeur | Fichier |
|---|---|---|
| `MIN_LENGTH` | 8 | `answer_sanity.py` |
| `MIN_ARABIC_RATIO` | **0,30** | idem |
| `MAX_REPEAT_RATIO` | 0,60 | idem |
| chimie ≥ 2 | `defer`, on continue | `_sanity_fork` dans `local_grader.py` |
| G7 | `38 ATP · P/O=3` → `defer`, pas 0 | test vert |

**Hypothèse.** Une copie « honnête truffée de FR » prend `method=0` avant le matching.  
**Mesure :** une phrase arabe + ATP/enzyme/glucose → l’arabe **domine** la longueur → ratio ≫ 0,30.  
Un essai **100 % français** sans signaux chimie → `not_arabic`. **Voulu** : Bac SVT public = arabe.  
Un essai 100 % FR *avec* 38 ATP / P/O → `defer` (on note quand même, pas de cache).

**Jugement.** L’asymétrie « le lexique connaît le FR, le portail le refuse » est **surjouée**. Le portail refuse le **français comme langue de copie**, pas les **termes** FR dans une phrase arabe.

**Décision :** documenter le contrat chiffré (comme N1–N10). **Ne pas** baisser 0,30 pour les tokens `$lex` FR. Golden **G18** : copie arabe + ATP + enzyme + glucose.

Le « fork » sanity : **volontaire**. `answer_sanity.py` sert encore le chemin v2/LLM. On paramètre le fork dans `grade()` ; on ne fusionne pas tant que L2 vit.

---

## 4. C4 — `theme_min_hits=1`

**Fait.** Défaut 1, **les 10 grilles L0 = 1**. Overlap de variants = **même chapitre** (yeast analyse ↔ interpret), pas digestion ↔ photosynthèse.

**Fait.** G13 : copie géologie sur yeast → `off_topic`. Sur un DA, `cites_keypoint` refuse le chiffre bidon ; stuffing cap 50.

**Jugement.** Imposer ≥ 2 hits **distincts** dans `validate_rubrics` L0 est trop brutal : une حلّل courte honnête (`الخميرة` + `18` + `كلما`) peut n’avoir **qu’un** hit de thème. Faux hors-sujet = mentir.

Exemple auditeur « الطاقة dans une copie digestion » : **aucune** grille L0 n’a `طاقة` seul comme thème.

**Décision :** défaut **1 conservé**. Porosité **assumée**. Règle **auteur** L1 : variant générique (طاقة، نمو، نشاط) → le retirer ou monter le min **sur cette grille**. Pas d’invariant CI.

---

## 5. C5 — S1 implémenté, S0 pas fait

**Fait.** Header cible disait « S1 implémenté » sans dire que le gate S0→S1 (G9/G10) n’était pas vert.  
As-built (`ARCHITECTURE-CORRECTEUR-LOCAL.md` §9) disait déjà « S0 ← pas fait ».

**Jugement.** Ce n’est pas un contour **caché** du moteur. C’est un trou de **doc cible**. S1 = fichier testable, flag off, **pas une publication**. Le gate redevient bloquant le jour du flag `true`.

**Décision :** table d’état §14.1. S0 T1/T2/T3 = **NON**. T2 : filtrer **toutes** les routes session (list/delete), pas seulement 4.

---

## 6. Secondaires — acceptés comme hygiène, pas bloquants

| Point | Verdict |
|---|---|
| `from_cache` vs G2 | **Oui** — G2 hors ce champ ; `grade()` le laisse False |
| Fork sanity vs 2 normaliseurs | **Pas la même maladie.** Fork = ne pas casser le v2 encore live. Les 2 `normalize` (arabic vs Savoir) restent une dette **volontaire** |
| `defer` = compute gratuit | **Oui, mineur.** `grade()` = regex. Assumé |
| P12 gaming (ordre) | **Oui, assumé** — documenté dans P12 |
| `validate_rubrics` sans négatifs | **Oui S2.** G6/G13/G14 existent déjà en pytest |
| Observabilité | **Oui S2** — §7.1 (ungraded, defer, stuffing, science error, hit-rate) |
| Golden anti-collision N6/N7 | **Oui hygiène** — exemple papier `ضوئي→ضوي` était **faux** (`ضويي`, pas de collapse `يي`) |

---

## 7. Ce qu’on ne code pas maintenant

- Pas de Redis dans `grade()`
- Pas de `POST /api/grade`
- Pas de `theme_min_hits=2` sur les JSON L0
- Pas de table copies en clair
- Pas de fusion des deux `normalize` sans golden Savoir

S2, quand tu diras S2 : clé C1 + tuer le JS front **le même jour**.

---

*L’honnêteté est déjà une propriété du moteur. Le seul endroit où le papier allait mentir, c’était la clé de cache — corrigée avant d’exister.*
