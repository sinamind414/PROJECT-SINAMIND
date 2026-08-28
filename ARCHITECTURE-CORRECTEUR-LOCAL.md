# Architecture détaillée — Correcteur local Khawarizmi

**Version moteur :** `GRADER_VERSION = 1.1.4`  
**Statut :** **S0–S20.** `grade()` 0 LLM, `GRADER_VERSION=1.1.4`. Adaptateurs + G11 + hash + mixins/`$lex:` + v2/methodology/JS gelés. UI 2 axes + G12. Drill/exercices copies → grade()/ungraded. Schéma dessiné = 0 auto. Observabilité `/api/grade/metrics`. Colonnes 035. Cache C1 + sha16 hors `grade()`. Chatbot copies gelées. Quota sanity==ok. FSRS `may_write_fsrs`. `validate_rubrics` G5+négatifs. Sans grille → ungraded.  
**Promesse :** noter **méthode (Manhadjiya) + science (manuel / دليل)** sans mentir sur le %.  
**Bannière élève :** `ملاحظة تدريبية — منهج + محتوى. ليست علامة بكالوريا رسمية.`

---

## 0. Phrase d’architecture

> La machine **ne génère rien**. Elle **normalise** l’arabe (liste fermée N1–N10), **coche** des cases d’une grille git, **ancre** les chiffres du document, **filet** les erreurs graves (38 ATP, ADN hors noyau, coquille 10⁶→10⁴), **nomme un diagnostic**, et **plafonne** si le contenu est faux.  
> Sans grille → `ungraded`. Jamais de fallback `VERB_RULES` / L2 / LLM.

**Qui juge quoi**

| Source | Rôle |
|---|---|
| **كتفي / Manhadjiya** | **Comment** — حلّل / فسّر / استنتج / نص |
| **دليل الأستاذ ONPS** | **Quoi** chiffré — 10⁴ ARNr/ARNt, رابعة ≠ 4 |
| **الكتاب المصحح** | Lexique + graves Savoir |
| **إكرام** | **Pas** sur le chemin de note |

---

## 1. Deux mondes (ne pas confondre)

```
S3 (as-built)
  ScenarioRunner / diagnostic/global / verb / bac / DA v1 / evaluate-v2  → grade()
  Sans Rubric → 422 ungraded (jamais VERB_RULES / JS / L2 / LLM)
  evaluateMethodologyAnswer() mort sur les pages note (fichier encore là)

CORRECTEUR
  grade(copy, rubric, document)  ← SEUL JUGE
  CLI : scripts/grade_copy.py
  Tests : pytest --noconftest
```

Sans grille L0, l’élève voit **تعذر التصحيح**, pas un %. C’est honnête.

---

## 2. Fichiers

```
khawarizmi-backend/
  services/local_grader.py      # grade() — pur, sync, 0 I/O, 0 LLM
  services/rubric_store.py      # load(question_id) depuis git
  services/arabic.py            # normalize N1–N10
  services/answer_sanity.py     # filtre vide / charabia (fork defer dans grade)
  services/savoir_corrector.py  # _GRAVE_ERRORS, _NUMERIC_RULES, _SYNONYMS, detect_textbook_errata
  schemas/rubric.py             # Rubric, Criterion, GradeResult
  schemas/document_model.py     # keypoints du DA
  scripts/validate_rubrics.py   # sum(points) + modèle ≥ 85 % + $lex:
  scripts/grade_copy.py         # coller une copie
  data/rubrics/index.json
  data/rubrics/templates/{analyse,interpret,deduce,scientific-text}.json
  data/rubrics/questions/*.v1.json     # 10 L0
  data/rubrics/mixins/synthese-proteines.json  # doc auteur (10⁴)
  data/documents/*.v1.json             # 5 DocumentModel
  tests/test_local_grader.py
  tests/golden/test_rubric_l0.py
  tests/test_arabic_normalize_contract.py
```

**Interdit dans `local_grader.py` :** `openai`, `llm`, `pipeline`, FastAPI, Redis, SQL.

---

## 3. Contrat d’entrée / sortie

```python
def grade(*, student_answer: str, rubric: Rubric, document: DocumentModel | None) -> GradeResult

def grade_question(question_id: str, student_answer: str) -> GradeResult
# load() None → UngradedError  (cible HTTP : 422 ungraded)
```

**`GradeResult` (élève / tests)**

| Champ | Sens |
|---|---|
| `method_points` / `method_points_max` | cases cochées |
| `method_percent` | 0–100, **degré التدريب** |
| `method_label_ar` | غير كاف / جزئي / مقبول / متقن |
| `order_ok` | `False` → **متقن interdit** (points inchangés) |
| `science_status` | `ok` \| `error` \| `not_applicable` |
| `science_flags` | messages filet (grave, hors-sujet, تصويب 10⁴) |
| `science_capped` | `error` → overall ≤ cap (défaut **40**) |
| `sanity_code` | ok \| empty \| too_short \| not_arabic \| gibberish \| defer |
| `stuffing_suspected` | ratio > 0.60, copies ≥ 20 tokens |
| `diagnosis.code` | **un** code |
| `praise_ar` + `next_step_ar` | 2 phrases max |
| `source` | toujours `local_rubric` |
| `cacheable` | seulement `sanity_code==ok` (pas defer) |

**Interdit dans le contrat :** `source=llm*`, `bac_ready`, `/20` officiel, `model_answer`.

**Labels**

| % méthode | Label | Exception |
|---|---|---|
| 0–39 | غير كاف | |
| 40–69 | جزئي | |
| 70–84 | مقبول | |
| 85–100 | متقن | interdit si `order_ok is False` **ou** case `required` absente → **مقبول** |

`overall_training_percent` = `min(method_percent, 40)` si science error ; sinon `method_percent` (déjà plafonné stuffing 50).

---

## 4. Pipeline (8 étages)

```
[0] SANITY
[1] NORMALIZE
[2] STRUCTURE (ordre + verb_slip signal)
[3] DOCUMENT (keypoints / objet / tendance)
[4] METHOD MATCH (chaque Criterion)
[5] SCIENCE VETO (grave + num + thème + errata)
[6] STUFFING
[7] DIAGNOSIS
```

### [0] Sanity (fork verbe-aware)

Appelle `check_answer_sanity`, puis :

| Code | Stop ? |
|---|---|
| empty / too_short / repeated_chars | **oui** → method=0, science n/a |
| too_short + verbe `cite`/`define` + ≥3 glyphes utiles | continue |
| not_arabic / gibberish + ≥2 tokens chimie (`ATP`, `P/O`, digits…) | **`defer`** : on **continue**, `cacheable=False` |
| sinon not_arabic / gibberish | stop |

`schematiser` : **court-circuit** — 0 point, `schematiser_manual` (pas de vision).

### [1] Normalize — contrat fermé

`services.arabic.normalize_arabic` :

| # | Transformation |
|---|---|
| N1 | Unicode NFKC |
| N2 | Strip ZWJ / ZWNJ / kashida `ـ` |
| N3 | Tashkîl + alef suscrit |
| N4 | أ إ آ ٱ → ا |
| N5 | ى → ي |
| N6 | ئ → ي ؛ ؤ → و |
| N7 | ة → ه |
| N8 | chiffres indiens + indices → ASCII |
| N9 | CO₂ → co2 (via N8+lower) |
| N10 | espaces + `.lower()` |

**Pas** Levenshtein, **pas** stemming scientifique.  
Proclitiques **fermés** au match seulement : `و ف ب ك ل ال وال فال بال لل` (فكلما، النمو).

**Dette :** `savoir_corrector._normalize` est **un autre** normaliseur (graves Savoir). Ne pas fusionner sans rejouer le golden Savoir.

### [2] Structure

`method_graph.steps` = ids de critères dans l’ordre livre.  
Désordre **seulement si toutes** les steps sont `full` mais positions non croissantes → `order_ok=False`.

Signaux (pas encore diagnosis) :

- `analyse` + لأن/بسبب/يفسر/تفسير/هذا يدل → `verb_slip.interpret`
- `interpret` + كلما **sans** cause → `verb_slip.analyse`

### [3] Document

`DocumentModel.keypoints[]` : un nombre de la copie ∈ `[value ± tolerance]` (virgule ou point).  
**Un « 1 » inventé ne compte pas.**  
`cites_object` : الوثيقة / الجدول / المنحنى.  
`cites_trend` : variants du document.  
`number_present` **interdit** si `document_id` (validé au load).

### [4] Method match

| `check` | Full | Partial |
|---|---|---|
| `any_of` | ≥1 variant (`$lex:` expansé) | **jamais** |
| `all_of` | tous | ≥1 → points proportionnels |
| `forbidden_abs` | **0** hit (لأن dans حلّل) | — |
| `cites_keypoint` / `_object` / `_trend` | voir [3] | — |
| `min_length` | `len ≥ min_chars` | — |
| `section_markers` | comme any_of | — |
| `cooccurrence` | tous les variants dans une fenêtre de tokens | — |

`$lex:glucose` → `savoir_corrector._SYNONYMS["glucose"]`. Clé inconnue → **FAIL** `validate_rubrics`.

Match unigramme = **frontières de mot** (sinon `لان` ⊂ `الانزيم` / `لانطلاق`).

### [5] Science veto (Savoir = filet, pas la note)

1. **Hors-sujet** : hits(`theme_variants`) < `theme_min_hits` (défaut 1) → `error`, « خارج الموضوع »
2. **`_GRAVE_ERRORS`** sur texte Savoir-normalisé (36 ATP, ADN في الهيولى, CO₂ « produit » en photosynthèse **si** contexte photosynthèse)
3. **`rubric.grave[]`** + `context_any`
4. **`_NUMERIC_RULES`** : 38 ATP, P/O 3/2, fermentation 2
5. **Errata دليل p.25** `detect_textbook_errata` :
   - ARNr 5S/S5 **3,6×10⁶** (livre) → message **10⁴**, status **ok**, **pas de cap** (jaune)
   - ARNt **2,5×10⁶** → idem
   - 10⁶ **sans** ARNr/ARNt → silence

Graves photosynthèse **ignorées** hors thème (évite « الخميرة تنتج CO2 »).

### [6] Stuffing

Si tokens < 20 : **jamais**.  
Sinon : ratio (hits thème + variants) / tokens > **0.60** et **pas** de keypoint/objet  
**ou** distractor hit.  
→ `stuffing_suspected`, `method_percent = min(%, 50)`.

### [7] Diagnosis (un seul code, priorité code actuel)

```
sanity.*  >  off_topic  >  science.grave  >  verb_slip.*
  >  unanchored  >  stuffing  >  first_required_gap.{id}
  >  science.erratum  >  all_correct
```

`schematiser_manual` hors liste (court-circuit).

---

## 5. Données L0 (10 grilles)

| `question_id` | Verbe | Doc | /pts |
|---|---|---|---|
| `manhadjiya-yeast-analyse` | حلّل | 9 → 18 / 6 | 4 |
| `greffe-ltc-analyse` | حلّل | 10 j / 5 j · 2,5 / 4,8 | 4 |
| `enzyme-temp-analyse` | حلّل | 37° → 100 % · 80° → 0 | 4 |
| `photo-o2-analyse` | حلّل | O2 plateau 6 ml | 4 |
| `greffe-ltc-interpret` | فسّر | لأن ذاكرة / LTc | 4 |
| `yeast-glucose-interpret` | فسّر | 18 vs 6 لأن أيض | 4 |
| `enzyme-temp-interpret` | فسّر | لأن تمسخ | 4 |
| `greffe-ltc-deduce` | استنتج | خلوية + LTc | 3 |
| `synapse-curare-deduce` | استنتج | كورار / Ach | 3 |
| `proteine-adn-scientific-text` | نص | intro / نسخ / ترجمة / خاتمة | 5 |

Invariant load : `sum(criteria.points) == total_points`.  
`validate_rubrics.py` : `model_answer` ≥ 85 % **et** hors-sujet / 36 ATP overall ≤ 40, vide = 0, **et** ≥2 `counter_examples` (dont `off_topic`) — sinon merge refusé. Jamais exposés par GET.

---

## 6. Flags

| Variable | Défaut | Effet |
|---|---|---|
| `LOCAL_RUBRIC_GRADER` | **false** | S2 : `/api/grade` + adaptateurs — **pas encore** |
| `SAVOIR_VETO` | true | filet science (code actuel : toujours on dans `grade()`) |
| `ENABLE_EXTERNAL_LLM` | ignoré par `grade()` | même à 1, **aucun** appel |
| `savoir_enabled_verbs` | `[]` | ancien étage Savoir **score** — **hors** `grade()` |

---

## 7. Lancer

```bash
cd khawarizmi-backend
PYTHONPATH=. python scripts/validate_rubrics.py
PYTHONPATH=. python -m pytest tests/test_local_grader.py tests/golden/test_rubric_l0.py --noconftest -q
PYTHONPATH=. python scripts/grade_copy.py --list
PYTHONPATH=. python scripts/grade_copy.py manhadjiya-yeast-analyse   # stdin = copie
```

---

## 8. Hors périmètre (assumer)

- Schéma **dessiné** (pixels)  
- Note Bac **officielle /20** (2023/2025 = pas de Rubric → ungraded)  
- L2 / ONNX / MiniLM comme juge  
- CMS prof / Mongo / GPU  
- Parser auto Manhadjiya ou إكرام  

---

## 9. Migration (rappel)

```
S0  T2 IDOR ← FAIT · T3 whitelist action ← FAIT · T1 PDF « غير متاح » ← FAIT
S1  grade() + 10 L0 + tests                           ← FAIT
S2  POST /api/grade + ScenarioRunner only + tuer JS   ← FAIT (1.1.4). 422 ungraded. Pas de fallback methodology-evaluator.ts
S3  verb + bac_blanc + DA v1 → grade() ; mort VERB_RULES / جاهز / JS diagnostic  ← FAIT
S4  GET /correction G11 + hash persist + FSRS science/<10                       ← FAIT
S5  mixins chapitre au load + $lex: fichier git                                 ← FAIT
S6  evaluate-v2 gelé → grade() (0 L2 / 0 LLM)                                   ← FAIT
S7  POST /api/evaluate/methodology gelé → grade()/ungraded                      ← FAIT
S8  JS evaluateMethodologyAnswer = ungraded ; evaluate.py hors registre ; 1.1.4 ← FAIT
S9  UI 2 axes (منهج / محتوى) + درجة التدريب + G12 ; ungraded = — pas 0 %     ← FAIT
S10 drill/submit + exercices/correct → grade()/ungraded (QCM local intact)   ← FAIT
S11 schéma Vision gelé (0 auto) ; evaluation_mode → grade()/ungraded         ← FAIT
S12 observabilité §7.1 GET /api/grade/metrics (0 copie, cache_hits=0)        ← FAIT
S13 colonnes 035 da_answers (engine/science/method_percent/diagnosis)        ← FAIT
S14 cache C1 hors grade() (rubric_id+doc_id, 0 user_id, TTL 7 j, sanity=ok) ← FAIT
S15 chatbot explain-back + boss-fight → ungraded (0 overlap, 0 model_answer) ← FAIT
S16 Redis optionnel SETEX 7 j sur cache C1 (mémoire si pas Redis ; 0 Redis dans grade()) ← FAIT
S17 quota evaluate_limit (sanity==ok only) + FSRS may_write_fsrs sur POST /api/grade     ← FAIT
S18 validate_rubrics goldens négatifs (hors-sujet / 36 ATP / vide → plafond)            ← FAIT
S19 cache sha16 (Rubric+Document) si bump oublié — 0 user_id, hors grade()               ← FAIT
S20 counter_examples L0 (≥2 dont off_topic, axis overall, hors GET)                     ← FAIT
```

**Brancher S2 sans tuer le fallback front = deux notes. Interdit.**

---

## 10. Réponse audit indépendant (C1–C5) — 2026-08-27

| # | Auditeur | Notre verdict | Action |
|---|---|---|---|
| C1 clé cache sans `rubric_id` | bloquant S2 | **Accepté** — spec fausse, **pas** un bug live (`grade()` n’a pas de Redis) | Clé corrigée dans `ARCHITECTURE-COACH-LOCAL.md` §4 + G17 |
| C2 hash-only vs lexique L1 | stratégique | **Tranché** : P8 reste. Enrichir = auteur + fréquence de hash + récolte opt-in. Pas de plaintext | §15 cible |
| C3 sanity / FR | bloquant S2 | **Doc** : seuil **0,30** déjà dans `answer_sanity.py`. FR `$lex` ne baisse pas le seuil. Mixte AR+ATP = ok | contrat §6.2 + G18 |
| C4 `theme_min_hits=1` | avant S2 | **Refusé** comme invariant : ≥2 → faux hors-sujet sur حلّل courte. Règle **auteur** L1 | défaut 1 conservé |
| C5 S0 vs S1 | immédiat | **Accepté** comme doc : S0 **pas fait**, gate contourné **volontairement** (flag off) | table §14.1 |

Détail C1–C5 : `AUDIT-ARCHI-INDEPENDANT.md`.  
2ᵉ passe (F1–F7, « pas prêt S2 ») : `AUDIT-S1-F1-F7.md` — **on refuse** `theme_min_hits≥2` en CI, **on refuse** d’élargir le filet 10⁶, **on refuse** `Observation` en S1. T2/T3 = prod, pas le grader. Flag **déjà** `false`.

---

*SoT code : `local_grader.py` 1.1.2. SoT cible produit : `ARCHITECTURE-COACH-LOCAL.md`. Audit écarts : `AUDIT-GRADER-LOCAL.md`.*
