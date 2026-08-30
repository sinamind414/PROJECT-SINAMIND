# Audit live — correcteur local `grade()` (0 LLM)

**Date :** 2026-08-27  
**Cible :** `ARCHITECTURE-COACH-LOCAL.md` vs code  
**HEAD session :** branche `arena/01a03f4f-project-sinamind`  
**Règle :** faits / écarts / jugement. Pas de LLM sur le chemin de note.

---

## 0. Carte réelle (fait)

```
copie
  → sanity (fork answer_sanity + defer chimie)
  → normalize_arabic N1–N10
  → method_graph (ordre = label, pas les points)
  → Criterion.any_of / forbidden / cites_keypoint / …
  → Savoir grave + numériques + hors-sujet + errata 10⁴ (jaune)
  → stuffing
  → UN diagnosis + praise + next_step
```

**Un moteur** : `services/local_grader.py :: grade()`.  
**Pas** FastAPI / Redis / SQL / openai dans ce fichier.  
**Pas** monté : aucun `routes/grade.py`. Flag `local_rubric_grader=false`.  
Les **5 cerveaux** (v2 L2, regex DA, action-verbs, JS front, evaluate.py) **tournent encore** en prod.

---

## 1. Contrat A1–A10

| # | Question | Code |
|---|---|---|
| A1 | 0 LLM sur `grade()` | **OUI** — G1 AST : pas d’import openai/llm/pipeline |
| A2 | Un seul moteur DA/verb/bac | **NON** — `grade()` existe, adaptateurs **non** branchés |
| A3 | Barème = Rubric git | **OUI** L0 (10 JSON). Prod encore `VERB_RULES` |
| A4 | Pas un /20 Bac | **OUI** dans `GradeResult` (training %). UI Bac blanc **pas** touchée |
| A5 | Savoir = filet pas note méthode | **OUI** — grave + num + errata ; score lexique ignoré |
| A6 | T1–T3 (PDF, IDOR, points) | **NON** — hors S1 |
| A7 | Réutiliser arabic / Savoir / sanity | **OUI** (deux `normalize` encore) |
| A8 | Hors-sujet → science error | **OUI** `theme_min_hits` |
| A9 | Chiffre bidon ≠ keypoint | **OUI** `cites_keypoint` vs DocumentModel |
| A10 | Normalize liste fermée | **OUI** N1–N10 testés |

---

## 2. Bugs corrigés dans cet audit (v 1.1.2)

| Bug | Avant | Après |
|---|---|---|
| Stuffing comptait `لان` ⊂ `الانزيم` | `_occurrence_count` = `.find` brut | mêmes frontières + proclitiques que `_hit_pos` |
| Regex recompilée à chaque hit | lent / bruit | `@lru_cache` `_word_re` |
| `$lex:` inconnu silencieux | grille sourde | `validate_rubrics.py` **FAIL** |
| Message 10⁴ masqué si autre diag | next_step vide | append `تصويب الدليل` |

---

## 3. Écarts **volontaires** (pas des bugs)

| Spec | Code | Verdict |
|---|---|---|
| Mixin chargé au runtime | `synthese-proteines.json` = **doc auteur** ; filet 10⁴ = `detect_textbook_errata()` | L1, pas L0 |
| `savoir._normalize` délègue à arabic | **deux** normaliseurs | ne pas fusionner sans golden Savoir |
| S2 `POST /api/grade` | absent | flag off **voulu** |
| G8 = HTTP 422 | `UngradedError` Python | pas d’HTTP tant que S2 |
| Diagnosis : verb_slip **avant** off_topic | off_topic d’abord si theme miss | **mieux** : hors-sujet > glissement |
| 10⁶ ARNr = science error cap 40 | **warn**, status ok, pas de cap | **voulu** (coquille livre) |

---

## 4. Dettes (ne pas « réparer » en silence)

1. **5 moteurs encore en prod** — brancher `grade()` = S2 + tuer le front evaluator.  
2. **T2 IDOR Bac blanc / T3 points / T1 PDF LFS** — bloquants publication, pas le moteur.  
3. **`_NUMERIC_RULES["po_nadh"]` pattern `p/o` trop large** — héritage Savoir ; ne pas l’élargir ici.  
4. **Mixins non fusionnés** dans `rubric_store.load`.  
5. **Bac 2023/2025** : pas de Rubric → `ungraded`.  
6. **إكرام** : pas dans le chemin note (Manhadjiya = verbes).

---

## 5. Tests

`pytest tests/test_local_grader.py tests/golden/test_rubric_l0.py tests/test_arabic_normalize_contract.py --noconftest`  
`scripts/validate_rubrics.py` : 10/10 modèles ≥ 85 %.

---

## 6. Jugement

Le châssis **tient** : 0 LLM, Rubric git, deux axes, keypoints, filet 10⁴ jaune.  
Ce n’est **pas** encore « le correcteur du site ». C’est un **prof local testable**. Brancher sans tuer L2/JS = **deux notes**. Interdit.
