# Bilan des audits — correcteur local Khawarizmi

**Date :** 2026-08-27  
**Moteur mesuré :** `grade()` **1.1.2**, flag **`false`**, **pas** d’API `/api/grade`  
**Sources :** 4 passes d’audit (C1–C5, F1–F7, N1–N6, F-01–F-19) **contre le code**, pas contre la spec seule.

**Légende**

| Force | Sens |
|---|---|
| **FORT** | Vrai dans le code. Ment sur le %, ouvre une faille, ou casse un élève. À traiter. |
| **MOYEN** | Vrai, mais pas un mensonge live. S2 / auteur / hygiène. |
| **FAIBLE** | Surjoué, déjà fermé, ou **choix produit** (كتفي / دليل). Ne pas « réparer ». |

---

## 1. FORT — vrais, mesurés

| # | Bug | Preuve | Effet | Quand |
|---|---|---|---|---|
| **T2** | IDOR Bac blanc | **FERMÉ 1.1.3** : `_require_own_session` → 403 / 404 + `AND user_id` sur UPDATE | — | fait |
| **T3** | Points / XP client | **FERMÉ** : whitelist `action` → delta serveur. `?points=99999` → 400 | — | fait |
| **T1** | PDF LFS | **FERMÉ UI** : « الموضوع غير متاح (ملف ناقص) », plus de bouton فتح | — | fait |
| **N1** | Digits = chimie | **FERMÉ 1.1.3** dump → 0. G7 `ATP`/`P/O` encore defer | — | fait |
| **N1b** | `forbidden_abs` cadeau | dump **déjà 0** (N1) — silence plus noté | — | caduc |
| **N2** | Séparateur arabe `٫` | **FERMÉ 1.1.4** : `٫`→`.` `٬` supprimé `٪`→`%`. `٢٫٥` ancre 2,5 | — | fait |
| **S2-JS** | ScenarioRunner | **FERMÉ S2** : `/api/grade` only, 5xx → تعذر التصحيح, **0** `evaluateMethodologyAnswer`. diagnostic/global + bac encore anciens (S3) | — | ScenarioRunner fait |

**Pas FORT (souvent classé P0 à tort)**

- Clé de cache sans `rubric_id` : **spec S2**, **0 Redis** dans `grade()`. Corrigée dans la cible. Pas un mensonge live.
- `theme_min_hits=1` : **voulu** (حلّل courte).
- Caper **38 ATP** : **38 est juste.** 36/32 capent.

---

## 2. MOYEN — vrais, pas un mensonge aujourd’hui

| # | Bug | Preuve | Pourquoi pas FORT |
|---|---|---|---|
| **UI %** | `method=100 متقن` + `overall=40` si 36 ATP | **FERMÉ S9** : `GradeResultCard` sépare منهج / محتوى ; درجة التدريب = overall ; ungraded = — |
| **Validate narcissique** | `model_answer ≥ 85` seulement | **FERMÉ S18** : `validate_rubrics` refuse aussi hors-sujet / 36 ATP overall > 40, vide ≠ 0 |
| **N2 exposant** | `3.6e6` → errata **silence** | mesuré | `10^6` / `×10^6` **jaune OK**. Trou étroit |
| **Keypoint = n’importe quel chiffre du doc** | yeast : `4` (heures) ancre autant que `18` | JSON | Case L0 = « un vrai chiffre », pas l’association 18↔glucose |
| **`$lex:glucose` trop large** | contient `سكر`, `مادة عضوية` | lexique | `سكر` ⊄ `السكريات` (frontière OK). Risque auteur L1 |
| **Stuffing diluable** | ratio / tokens | formule | Garde-fou, pas un 100 % volé. Borne abs. = S2 |
| **Deux `normalize`** | arabic ≠ Savoir (possessifs) | dette écrite | Sur ADN/هيولى + tashkîl : **même chaîne**. Fusion **sans** golden Savoir = plus dangereux |
| **نص titres** | en-têtes + lexique | mesuré **50 % stuffing** | Pas 100 %. min tokens/section = L1 |
| **`tolerance=0`** | JSON L0 | — | Règle **auteur** sur une courbe (±0,5), pas un défaut moteur 5 % |
| **SoT multiples** | 4 docs d’audit + 2 archi | — | **Code** = juge. Docs = annexes |
| **Flags morts** | `SAVOIR_VETO` / `savoir_enabled_verbs` hors `grade()` | grep | Nettoyage S3. Ne pas les réactiver |

---

## 3. FAIBLE — surjoué, fermé, ou choix produit

| Ils ont dit | Mesure / décision | Classe |
|---|---|---|
| Dump numérique = **50 % جزئي** | **38 % غير كاف** + خارج الموضوع | **Surjoué** |
| Correctif stuffing « keypoint **et** objet » ferme N1 | Ratio dump **déjà ~0** → stuffing ne part pas | **Mauvais diagnostic** |
| defer latin ATP → **80 %** | **12 %** hors-sujet | **Faux** |
| stuffing **écrase** le cap 40 | stuffing+36 ATP → overall **12** | **Faux** (ordre déjà bon) |
| `order_ok` → متقن avec 2 steps en désordre | L0 `required` manquant → **déjà مقبول**. G15 : 4 full désordre → pas متقن | **Pas L0** |
| `theme_min_hits ≥ 2` en CI | Faux hors-sujet sur حلّل courte | **Refusé** |
| Élargir jaune 10⁶ hors ARNr/ARNt | Faux positifs. Verrouillé دليل | **Refusé** |
| Caper **38 ATP** | 38 = ONEC **juste** ; 36/32 = grave | **Refusé** |
| Tolérer `لأن الوثيقة` dans حلّل | كتفي : لأن = فسّر. 88 % مقبول + `verb_slip` | **Refusé** |
| Proclitiques `لكن` → `كن` | On **ajoute** des préfixes, on n’efface **pas** la copie. `كن` ⊄ `لكن` | **Faux** |
| `ok` doit s’appeler `no_veto` | Filet, bannière déjà là | Sémantique, pas bug |
| `Observation` / `cites_relation` | Limite **0 LLM** assumée | **L1 auteur**, pas S1 |
| Clé cache collision live | Pas de cache dans `grade()` | **Spec S2**, déjà corrigée sur le papier |
| G1–G16 « absents » | `test_local_grader.py` + golden L0 | **Faux** (l’auditeur n’avait pas les tests) |
| praise/next = LLM caché | Templates **JSON** `advice_*` | **Faux** |
| A2 « un seul moteur » sur le **site** | **S0–S21** : `grade()` + cache C1+sha16 + chatbot gelé + quota + `counter_examples` + caps hors méthode | **Fermé** sur le chemin de note |

---

## 4. Compte

| Force | Nombre (cette synthèse) |
|---|---|
| **FORT** | **7** (T2, T3, T1, N1, N1b, N2 `٫`, S2-JS) |
| **MOYEN** | **11** |
| **FAIBLE / faux / refusé** | **15** |

Les 4 passes répètent souvent les **mêmes** 3 vrais (S0 prod, N1 digits, N2 `٫`) et gonflent le reste.

---

## 5. Que faire (si tu le dis)

| Mot | Action | Touche `grade()` ? |
|---|---|---|
| **`hotfix T2`** | `user_id` sur **toutes** les routes Bac blanc + test 403 | non |
| **`hotfix T3`** | supprimer `?points=` / `?xp=` | non |
| **`hotfix N1`** | digits ≠ chimie → dump **0** ; G7 inchangé | **oui** (2 lignes + golden) |
| **N8** | `٫`→`.` `٬` supprimer `٪`→`%` | oui, contrat N |
| **`S2`** | `/api/grade` + **tuer le JS le même jour** | adaptateur, pas le châssis |

**Ne pas faire :** fusion normalize à l’aveugle, `theme_min_hits=2` en CI, caper 38, Levenshtein, 2ᵉ cerveau, `/20`.

---

*S0–S29 : T1–T3, N1–N2, `/api/grade`, adaptateurs, G11, hash, mixins + `$lex:`, v2/methodology/JS gelés, UI 2 axes + caps, métriques, cache C1+sha16+filet_sha16, P/O NADH/FADH, filet ATP ٣٦ + 38-annule-36, FSRS pas sur cache hit, quota `ok`+`defer`, proclitique `كال` (`1.1.7`), `evaluate.py` hors registre.*
