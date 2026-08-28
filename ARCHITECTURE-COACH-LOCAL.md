# Architecture cible — Coach local « comme le livre »

**Date :** 2026-08-26 · **révisé** 2026-08-27 (C1 clé cache, contrat sanity, politique lexique, table d’état)  
**Statut :** S0–S28 **implémentés** — `grade()` **1.1.6** + filet ATP ٣٦ / 38-annule-36 + FSRS pas sur cache hit. Flag `LOCAL_RUBRIC_GRADER` défaut `false` (**lu nulle part**).  
**S0 (T1–T3) :** **fait** (T1 UI PDF, T2 IDOR, T3 whitelist). Flag prod encore `false`. Voir table §14.1.  
**Public :** revue humaine / audit par IA  
**Produit :** Khawarizmi / IA Khawarizmi Pro — Bac SVT Algérie 3AS  

**Contrainte non négociable :** **0 LLM** sur le chemin de note. Aucun appel génératif (OpenAI, Groq, Gemini, LLM local). `ENABLE_EXTERNAL_LLM` est **ignoré**. Inférence déterministe uniquement.

**Promesse :** un seul moteur qui note **méthode (Manhadjiya) + science (manuel)**, **sans mentir sur le %**.

---

## Phrase d’architecture

> La machine ne génère rien. Elle **compile** le livre (étapes, lexique, chiffres du document) en règles, **coche** une trace, **nomme un diagnostic**, et **plafonne** si le contenu est faux ou hors sujet.  
> Le % est un résumé d’**entraînement** (« درجة التدريب »), jamais une note Bac.  
> Les grilles sont des fichiers git, relus par un humain. Un ajout au lexique profite à toutes les questions.

---

## 0. Contrat d’audit (comment juger ce document)

| # | Question | Verdict attendu |
|---|---|---|
| A1 | Aucun chemin d’évaluation n’appelle un LLM ? | OUI |
| A2 | Une seule fonction de notation pour DA / verbes / Bac blanc / (plus de) fallback front ? | OUI |
| A3 | Le barème est un objet versionné par **question**, pas un effet de bord de `VERB_RULES` ? | OUI |
| A4 | L’UI n’affiche jamais un seul % comme « note Bac /20 » ? | OUI |
| A5 | Savoir ne produit pas la note méthode ; il peut seulement **plafonner / flagger** le contenu ? | OUI |
| A6 | Les 3 réparations confiance sont listées avec fichiers et critères de done ? | OUI |
| A7 | Mapping explicite vers le code **existant** (réutiliser, pas réécrire) ? | OUI |
| A8 | Hors-sujet → `science_status=error`, pas `ok` ? | OUI |
| A9 | Sur un DA, un chiffre **quelconque** ne valide pas l’ancrage document ? | OUI |
| A10 | La normalisation arabe est une **liste fermée**, testée ? | OUI |

Toute proposition qui réintroduit `evaluate.py` / `ai_evaluate.py` / `_call_with_fallback` / un 2ᵉ cerveau JS sur le chemin de note = **rejet**.

---

## 1. Objectif / hors-objectif

### 1.1 Objectif

Remplacer les **5 moteurs actuels** par un pipeline déterministe :

```
copie + Rubric(question) + DocumentModel? + lexique
        →  NoteMéthode  +  AlerteScience  +  diagnostic  +  prochaine étape
```

Aligné sur :
- **Méthode :** `LIVRE-MANHADJIYA.md` (حلّل = 4 pas **ordonnés** ; فسّر = cause + لأن ; نص علمي = 3 blocs)
- **Science :** `الكتاب_المصحح_v1.0.md` + `savoir_corrector.py` (`_GRAVE_ERRORS`, 38 ATP, P/O, lexique FR/AR)

### 1.2 Hors-objectif (assumer, ne pas mentir)

| Non couvert en v1 | Pourquoi |
|---|---|
| Noter un **schéma dessiné** (pixels) | 0 vision ; `schematiser` = comparaison au modèle, **0 note auto** |
| « Beau style » d’un نص علمي | On coche intro / عرض / خاتمة + thème, pas le style |
| Barème ONEC officiel 0,25–1,25 d’un sujet scanné | Pas de pièce ONEC dans le git ; grilles **d’entraînement** |
| Embeddings ONNX / L2 TF-IDF comme juge | Trop flou + ONNX = pointeur LFS ; **hors chemin** |
| Génération de Rubric par LLM | Interdit |
| Fuzzy Levenshtein / mini-LLM « juste pour la phrase » | Faux oui (`نور`/`دور`) + casse P1 |

### 1.3 Promesse élève (texte canonique UI)

> « ملاحظة تدريبية — منهج + محتوى. ليست علامة بكالوريا رسمية. »

**Interdit :** « جاهز للبكالوريا » calé sur ce %, un cercle unique 78 %, un `/20` présenté comme سلم الدولة.  
*(Fait code actuel à tuer : `bac_blanc.py` si score ≥ 75 % → « أنت جاهز للبكالوريا ».)*

---

## 2. État actuel (fait — pour ancrer la cible)

```
Écran                    Moteur actuel                         Fichier
DA ScenarioRunner        grade() / 422 ungraded                local_grader + GradeResultCard
Bac blanc                grade() / 422 ungraded                bac_blanc.py + GradeResultCard
Action-verbs             grade() / 422 ungraded                action_verbs.py + GradeResultCard
Front si API down        evaluateMethodologyAnswer = ungraded  methodology-evaluator.ts (stub)
evaluate.py / ai_eval    GPT-4o → L2                           NON montés — NE PAS monter
```

**Runtime local aujourd’hui :** sanity → normalize → structure/ordre → ancrage document → match Rubric → veto Savoir + hors-sujet → stuffing → diagnostic. UI : `GradeResultCard` (2 axes).

`verb_database.json` : **حلّل ajouté** (id 11). Templates L0 dans `data/rubrics/templates/`.

---

## 3. Principes (invariants)

| | |
|---|---|
| P1 | **0 LLM.** `grade()` n’importe ni n’appelle aucun client génératif. |
| P2 | **1 moteur.** `services/local_grader.py` :: `grade(copy, rubric, document=None) -> GradeResult`. |
| P3 | **Barème = donnée.** `Rubric` JSON versionné par `question_id`. Pas `sum(VERB_RULES.points)`. |
| P4 | **Deux axes.** `method_score` ≠ `science_status`. Jamais un seul % « officiel ». |
| P5 | **Savoir = filet.** Grave + numérique + hors-sujet. **Pas** de note méthode par couverture lexicale. |
| P6 | **Déterministe.** Même copie + même `rubric_id` + mêmes versions (rubric, document, grader) → même `GradeResult` **hors** `from_cache` (posé par la route, jamais par `grade()`). Version ≠ identité. |
| P7 | **Pas de FastAPI / Redis / SQL dans le grader** (même règle que `grading/`). |
| P8 | **Copie jamais en clair** sur ce chemin (`hash_answer` = HMAC-SHA256 `SECRET_KEY`, hex **sans** troncature). |
| P9 | **Équivalence de formulation** via **lexique + variants**, pas un mot unique, **pas** Levenshtein. |
| P10 | **Honnêteté de couverture.** Sans Rubric → `ungraded` (422), **pas** de fallback `VERB_RULES`. |
| P11 | **Le document DA est un objet**, pas « au moins un chiffre ». |
| P12 | **L’ordre Manhadjiya change le label**, pas le barème-points (sauf stuffing / cap science). Surface de gaming **assumée** : un élève peut permuter les phrases et garder les points (label ≠ متقن). |

---

## 4. Vue d’ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│  ÉCRANS — adaptateurs uniquement (0 logique de note)            │
│  ScenarioRunner · action-verbs/[slug] · BacBlanc                │
│  Fallback 5xx = « تعذر التصحيح »  (JAMAIS un 2ᵉ cerveau JS)     │
└──────────────────────────────┬──────────────────────────────────┘
                               │ POST /api/grade  (JWT)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  routes/grade.py                                                │
│  load Rubric + DocumentModel · grade() · persist hash · FSRS    │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  services/local_grader.py          ← SEUL MOTEUR                │
│  [0] sanity     answer_sanity (verbe-aware + defer chimie)      │
│  [1] normalize  arabic.normalize — CONTRAT FERMÉ §5.1           │
│  [2] structure  method_graph (ordre) + connecteurs verbe        │
│  [3] document   cites_keypoint / cites_trend / cites_object     │
│  [4] method     chaque Criterion (any_of, all_of, …)            │
│  [5] science    grave + numérique + theme_min_hits              │
│  [6] stuffing   seuils chiffrés                                 │
│  [7] diagnosis  UN code nommé + praise + next_step              │
└───────────┬──────────────────────────┬──────────────────────────┘
            ▼                          ▼
   data/rubrics/*.json        savoir_corrector (_GRAVE_ERRORS,
   data/documents/*.json      _NUMERIC_RULES, _SYNONYMS via $lex:)
```

**Cache** (équité : **pas** de `user_id`) — **S2, pas dans `grade()`** (P7 : 0 Redis dans le grader) :

```
grade:{GRADER_VERSION}:{rubric_id}:{rubric.version}:{doc_id|none}:{doc.version|none}:{verb}:{sha16}:{filet_sha16}:{hash_answer(lstrip+rstrip)}
```

**Pourquoi `rubric_id` + `doc_id` :** les semver ne sont pas uniques. Dix grilles L0 partagent `version=1.0.0` et plusieurs partagent le verbe `analyse`. Sans identité, la même copie générique collée sur Q1 puis Q2 servirait le `GradeResult` de Q1 — mensonge silencieux sur le %. Test **G17**.

Ceinture S19 : suffixe `:{sha16(json canonique Rubric+Document)}` si l’auteur oublie le bump de version. `model_answer` hors hash (n’affecte pas `grade(copy)`).  
Ceinture S23 / B2 : `:{filet_sha16}` = graves + numériques + `$lex` fichier + `_SYNONYMS` + regex errata. Éditer Savoir sans bump `GRADER_VERSION` → nouvelle clé. Hors `grade()`.

TTL 7 j. Cachable seulement si `sanity_code=ok` (pas `empty`, pas `defer`).  
`hash_answer` = HMAC-SHA256 pepper `SECRET_KEY`, hex 64 chars — **déjà** `services/hashing.py`.  
`from_cache` : la route le pose après lecture Redis ; `grade()` le laisse `False`. G2 compare **hors** ce champ.

---

## 5. Données

### 5.1 Contrat de normalisation (bloquant — avant toute Rubric)

**Une** fonction publique : `services/arabic.normalize_arabic`.  
Aujourd’hui elle fait déjà : diacritiques + kashida `ـ` + أإآٱ→ا + ى→ي + ة→ه + espaces + `.lower()`.  
**Il faut y fusionner** le meilleur de `savoir_corrector._normalize` (NFKD, `ئ`, possessifs) et **ajouter** ce qui manque.

Liste **fermée** (toute transformation hors liste = bug) :

| # | Transformation | Exemple |
|---|---|---|
| N1 | Unicode NFKC | formes compatibles |
| N2 | Strip ZWJ / ZWNJ / kashida `ـ` | `\u200d` `\u200c` |
| N3 | Suppression diacritiques (tashkîl + alef suscrit `\u0670`) | تَحْلِيل → تحليل |
| N4 | أ إ آ ٱ → ا | إنزيم → انزيم |
| N5 | ى → ي | على → علي |
| N6 | ئ → ي ; ؤ → و | ضوئي → **ضويي** (pas de collapse `يي`) |
| N7 | ة → ه | الطاقة → الطاقه |
| N8 | Chiffres indiens → occidentaux | ٣٨ → 38 |
| N9 | Formules chimie | CO₂ / co₂ / CO2 → co2 |
| N10 | Espaces multiples + strip + lower latin | ATP → atp |

**Interdit :** Levenshtein, stemming scientifique, racine trop agressive.  
**Option plus tard :** `stem_any_of` **uniquement** sur 10–20 mots outils de méthode (`حلل/تحليل/نحلل`, `استنتج/استنتاج`). Pas en v1.

Tests : un golden **par ligne du tableau**, plus fautes scolaires (hamza, tāʾ marbūṭa, mixte AR/FR).

Après fusion, `savoir_corrector._normalize` **délègue** à `arabic.normalize_arabic` (plus deux normaliseurs).

### 5.2 Lexique partagé (`$lex:`)

Ne pas recopier 40 synonymes par grille.

- Source v1 : **réutiliser** `savoir_corrector._SYNONYMS` / `_SYNONYMS_NORM` (ATP, تركيب ضوئي, enzyme, FR+AR déjà là).
- Fichier git plus tard : `data/lexicons/svt_terms.v1.json` (extrait du lexique, versionné).
- Dans une Rubric : `"variants": ["$lex:photosynthesis", "يحدث التركيب الضوئي"]`.
- **Guide auteur :** chaque terme scientifique = ar + fr + 1–2 fautes courantes **dans le lexique**, pas dans chaque question.

Un ajout `ارتفع` dans le slot « increase » profite à **toutes** les grilles `analyse`.

### 5.3 Schéma `Rubric`

```python
VerbSlug = Literal[
    "analyse", "interpret", "deduce", "justify", "hypothesis",
    "scientific-text", "compare", "relationship", "define",
    "describe", "cite", "schematiser",  # schematiser: 0 note auto
]

CheckKind = Literal[
    "any_of",           # ≥1 variante — binaire (full | absent)
    "all_of",           # full si tous ; partial si ≥1 ; absent si 0
    "forbidden_abs",    # full si 0 hit (ex. لأن dans analyse)
    "number_present",   # cite / define seulement — INTERDIT comme ancrage DA
    "cites_keypoint",   # ≥1 valeur du DocumentModel
    "cites_trend",
    "cites_object",     # الوثيقة / المنحنى / الجدول
    "min_length",
    "section_markers",  # intro / عرض / خاتمة
    "cooccurrence",     # token = split(r'\s+') — convention unique
]

class Criterion(BaseModel):
    id: str
    label_ar: str
    points: float
    check: CheckKind
    variants: list[str] = []          # littéraux et/ou $lex:id
    window_tokens: int | None = None  # cooccurrence ; token = whitespace
    min_chars: int | None = None
    required: bool = True             # absent → label ne peut pas être متقن

class MethodGraph(BaseModel):
    steps: list[str]                  # criterion.id dans l'ordre livre
    require_order: bool = True
    # Désordre → order_ok=False, label متقن interdit. Points inchangés.

class Rubric(BaseModel):
    rubric_id: str                    # = question_id
    version: str                      # semver — bump = invalide cache
    verb_slug: VerbSlug
    chapter_slug: str
    language: Literal["ar"] = "ar"
    total_points: float
    criteria: list[Criterion]         # 4–8
    method_graph: MethodGraph | None = None
    document_id: str | None = None    # → DocumentModel
    theme_variants: list[str] = []    # + $lex:
    theme_min_hits: int = 1           # 0 hit → science error « خارج الموضوع »
    # Défaut 1 CONSERVÉ. ≥2 distincts n'est PAS un invariant validate_rubrics L0 :
    # une حلّل courte honnête (الخميرة + 18 + كلما) peut n'avoir qu'un hit de thème.
    # Porosité assumée : un mot incident peut laisser science=ok — sur un DA le
    # trou est fermé par cites_keypoint + stuffing. Règle AUTEUR L1 : si un
    # variant est générique (طاقة، نمو، نشاط), le retirer ou monter le min
    # SUR CETTE grille.
    grave: list[GraveRef] = []
    distractors: list[Distractor] = []
    advice_by_gap: dict[str, str] = {}
    advice_praise: dict[str, str] = {}
    model_answer: str = ""            # TESTS / auteurs — JAMAIS exposé par GET rubric
    source: Literal["teacher_authored"] = "teacher_authored"
    grader_min_version: str = "1.0.0"
```

**Invariants :**
- `abs(sum(criteria.points) - total_points) < 1e-6` au load. Sinon **503**, pas de fallback `VERB_RULES`.
- `any_of` **jamais** `partial` (binaire). « Variation **et** nombre » = **deux** critères (règle auteur).
- `number_present` **interdit** sur un DA qui a un `document_id`.
- `model_answer` sert à G5 / `validate_rubrics.py` uniquement.

`GraveRef` / `Distractor` : inchangés vs v1 (`cap_science` défaut cap 40 %).

### 5.4 `DocumentModel` (à côté de la Rubric, pas dedans)

Mappe `da_documents.data` déjà en base.

```python
class Keypoint(BaseModel):
    id: str
    value: float
    unit: str | None = None
    tolerance: float = 0.0            # 12 ± 0.5
    aliases: list[str] = []           # "الذروة", "أقصى قيمة"
    label_ar: str

class DocumentModel(BaseModel):
    doc_id: str
    version: str = "1.0.0"
    kind: Literal["curve", "table", "schema_text", "text"]
    keypoints: list[Keypoint] = []
    trend: Literal[
        "increase", "decrease", "increase_then_plateau",
        "bell", "constant", "inverse", "unknown"
    ] = "unknown"
    trend_variants: list[str] = []
    objects: list[str] = []           # "المنحنى", "الجدول 1", "الوثيقة"
```

v1 **obligatoire** pour les questions L0 `analyse`. Les autres verbes : `document_id` optionnel.

### 5.5 Templates de verbe (Manhadjiya → cases)

Fichiers **écrits à la main** depuis le livre — **pas** un parseur markdown du `LIVRE-MANHADJIYA.md` (trop sale, templates pourris).

`data/rubrics/templates/{verb_slug}.json`  
Une question = template + mixin chapitre + keypoints.

| verb_slug | Cases (ordre livre) | Interdits |
|---|---|---|
| `analyse` | object · **cites_keypoint** · relation كلما sans cause · conclusion+thème | لأن، بسبب، يفسر، هذا يدل |
| `interpret` | rappel · lien causal (لأن/راجع) · savoir cours · conclusion | — |
| `deduce` | connecteur استنتاج · contenu lié au but | — |
| `scientific-text` | intro+مشكل · عرض (theme ≥ k) · خاتمة | liste à puces seule |
| `hypothesis` | marqueur فرضية · mécanisme · testable | constatation seule |
| `schematiser` | **refus poli**, 0 note auto | — |

`حلل` / `analyse` **doit** exister (absent aujourd’hui de `verb_database.json`).

**Mixins chapitre** (L1, pas L0) : `data/rubrics/mixins/{chapter}.json` = `theme_variants` + distractors + grave locaux. Une question DA photosynthèse ≈ 20 lignes, pas 120.

### 5.6 Stockage

```
data/rubrics/
  templates/{verb}.json
  mixins/{chapter}.json          # L1
  questions/da-…v1.json
  index.json                     # question_id → path  (chargé en mémoire au boot)
data/documents/{doc_id}.vN.json
```

`services/rubric_store.py` :: `load(question_id) -> Rubric | None`  
Pas de SQL obligatoire en v1 (git = revue possible).

### 5.7 Couverture

| Lot | Quantité | Done |
|---|---|---|
| L0 | 10 questions : 4 analyse (**avec DocumentModel**), 3 interpret, 2 deduce, 1 scientific-text | JSON valides + golden + `validate_rubrics.py` vert |
| L1 | questions DA en base | index complet **ou** `ungraded` honnête |
| L2 | action-verbs + bac_blanc | adaptateurs branchés |

Tant que L0 n’est pas vert : **ne pas** `LOCAL_RUBRIC_GRADER=true` en prod.

---

## 6. Moteur — `local_grader.grade`

### 6.1 Signature

```python
def grade(
    *,
    student_answer: str,
    rubric: Rubric,
    document: DocumentModel | None = None,
) -> GradeResult:
    """Pur, sync, 0 I/O, 0 LLM. Testable sans FastAPI."""
```

`GRADER_VERSION = "1.1.0"` dès que ordre / keypoints / theme_min_hits changent un label.

### 6.2 Pipeline

```
[0] SANITY  (fork verbe-aware de answer_sanity.py — NE PAS forker un 2ᵉ normaliseur)
    Contrat chiffré (liste fermée, comme N1–N10). Modifier = bump GRADER_VERSION + golden.

    | Constante            | Valeur | Code              |
    |----------------------|--------|-------------------|
    | MIN_LENGTH           | 8      | too_short         |
    | MIN_ARABIC_RATIO     | 0.30   | not_arabic        |
    | MAX_REPEAT_RATIO     | 0.60   | gibberish         |
    | MIN_UNIQUE_CHARS     | 4      | repeated_chars    |
    | chemistry_signal     | ≥ 2    | defer (continue)  |

    empty / gibberish / repeated_chars     → method=0, science=n/a, STOP
    too_short                              → method=0 sauf cite/define + ≥3 glyphes utiles
    not_arabic / gibberish :
        si _chemistry_signal_count ≥ 2     → defer : ON CONTINUE, cacheable=False
        sinon                              → method=0, STOP
    Caractères utiles = arabe + digits + latin + CO2/ATP/°/+/-/→
    defer = GradeResult COMPLET + sanity_code=defer (monitoring), method calculée.
    Quota : compter sanity==ok **et** defer (S22/B4). Vide / cache / 422 / stop sanity = 0.
    G7 reste defer ≠ 0. FSRS **pas** écrit sur defer (`may_write_fsrs` exige sanity==ok).

    Français / code-switching :
      les tokens FR du $lex (ATP, enzyme, glucose) NE baissent PAS le seuil 0.30.
      Copie Bac mixte (phrases arabes + ATP/enzyme) → l'arabe domine → ok.
      Essai 100 % FR sans ≥2 signaux chimie → not_arabic (voulu : Bac public = arabe).
      Essai 100 % FR avec 38 ATP / P/O → defer (G7).
      Golden G18 : copie arabe + ATP + enzyme + glucose FR → sanity ok, matching FR.

[1] NORMALIZE  arabic.normalize_arabic — contrat §5.1

[2] STRUCTURE
    method_graph : première occurrence de chaque step dans l'ordre ?
        oui → order_ok=True
        non (tous présents, désordre) → order_ok=False ; label متقن INTERDIT
        step required absent → déjà géré en [4]
    Connecteurs verbe (signals, pas encore diagnosis) :
        analyse + لأن/بسبب/يفسر → verb_slip.interpret
        interpret + كلما sans cause → verb_slip.analyse

[3] DOCUMENT  si rubric.document_id
    cites_object / cites_keypoint / cites_trend selon Criterion.check
    Keypoint : nombre dans [value ± tolerance] après N8.
    PAS number_present ici.

[4] METHOD MATCH
    any_of         → full si ≥1 variant (après $lex: + normalize) ; sinon absent
    all_of         → full / partial / absent
    forbidden_abs  → full si 0 ; absent si ≥1
    cites_*        → voir [3]
    min_length, section_markers, cooccurrence (split espaces)
    method_points = sum(earned)

[5] SCIENCE VETO  (savoir : grave + numériques SEULEMENT — ignorer le score lexique)
    grave / numeric mismatch → science_status=error, cap overall
    theme_min_hits : si hits(theme_variants|$lex) < min → science_status=error
                     message « الإجابة خارج الموضوع »
    sinon science_status=ok
    context_any sur GraveRef : un « 36 » ne saute que si ATP/respiration dans la copie.

[6] STUFFING  (chiffres, plus de « élevé »)
    tokens = split(r'\s+')
    SI tokens < 20 : stuffing_suspected = False (les courtes sont protégées par min_length)
    SINON :
      ratio = (# theme hits + # criterion-variant hits) / tokens
      stuffing si (ratio > 0.60) ET (pas de cites_keypoint si DA) ET (pas de cites_object)
      OU distractors hit
    Si stuffing : stuffing_suspected=True ; overall = min(overall, 50) ; caps_applied+=stuffing.
    method_percent RESTE pur (S21). متقن interdit si stuffing.
    Un « 1 » bidon NE désarme PAS le garde-fou (on ne teste plus number_present ici).

[7] DIAGNOSIS  — UN seul code, priorité :
    sanity > science.grave > verb_slip > off_topic > unanchored > stuffing > first_required_gap
    praise_ar  = templates advice_praise des criteria full (1–2)
    next_step_ar = advice_by_gap du diagnostic
```

### 6.3 `GradeResult`

```python
class GradeResult(BaseModel):
    grader_version: str
    rubric_id: str
    rubric_version: str
    verb_slug: str

    method_points: float
    method_points_max: float
    method_percent: int
    method_label_ar: str          # غير كاف / جزئي / مقبول / متقن
    order_ok: bool | None = None  # None si pas de method_graph

    science_status: Literal["ok", "error", "not_applicable"]
    science_flags: list[str]
    science_capped: bool

    sanity_code: str              # ok | empty | too_short | not_arabic | gibberish | defer
    stuffing_suspected: bool

    diagnosis: Diagnosis | None
    praise_ar: str
    next_step_ar: str
    phrase_ar: str                # praise + next (2 phrases max)
    criteria: list[CriterionHit]
    overall_training_percent: int
    source: Literal["local_rubric"] = "local_rubric"
    from_cache: bool = False
```

**Interdit dans le contrat élève :** `source=llm*`, `bac_ready`, un `/20` unique, `model_answer`.

### 6.4 Seuils d’affichage

| method_percent | method_label_ar | Exception |
|---|---|---|
| 0–39 | غير كاف | |
| 40–69 | جزئي | |
| 70–84 | مقبول | |
| 85–100 | متقن | **interdit** si `order_ok is False` **ou** stuffing → rétrogradé `مقبول` |

`overall_training_percent` (S21) :
- part de `method_percent` **pur**
- stuffing → `min(overall, 50)` + `caps_applied`
- science error → `min(overall, 40)` + `caps_applied`

Libellé UI : **« درجة التدريب »**.

### 6.5 Ce qu’on ne réutilise **pas** comme juge

| Module | Rôle cible |
|---|---|
| `fallback_v2.evaluate_l2` | **Hors chemin** |
| `VERB_RULES` / `evaluate_answer` | **Mort** après migration |
| `grading/pipeline.py` LLM | **Hors chemin** |
| `methodology-evaluator.ts` | **Supprimé** du chemin note (2ᵉ cerveau) |
| `savoir_corrector.deterministic_correct` score lexique | **Pas** la note méthode |

On **réutilise** : `arabic.py` (étendu), `_GRAVE_ERRORS`, `_NUMERIC_RULES`, `_SYNONYMS`, `hashing.py`, `answer_sanity.py` (fork defer), `fsrs_unified.py`.

---

## 7. Adaptateurs & API

```
POST /api/grade
  body: { question_id, answer, surface: da|verb|bac }
  auth: get_current_user
  quota evaluate_limit : compter si sanity==ok **ou** defer (S22)
        (vide / cache / 422 / stop sanity ne consomment pas)

GET  /api/grade/rubric/{question_id}
  → verb, criteria[].id + label_ar, total_points, method_graph.steps
  → JAMAIS variants, JAMAIS model_answer, JAMAIS keypoints.values
```

**Feature flag :** `LOCAL_RUBRIC_GRADER` défaut `false`.  
Quand on : `/api/grade` seul ; v2 LLM/L2 **gelé**.  
`SAVOIR_VETO` true dès LOCAL on.  
`ENABLE_EXTERNAL_LLM` ignoré par `grade()`.

Adaptateurs minces : `document_analysis_v2`, `document_analysis`, `bac_blanc`, `action_verbs` → `grade()`.  
Question sans Rubric → **422 `ungraded`**.  
Bac : `question_id` = `bac:{annale}:{ex}:{q}` **doit** exister dans `index.json`.

**Front :** `apiClient.grade()`. Si 5xx → « تعذر التصحيح ».  
**INTERDIT :** embarquer les Rubrics / `evaluateMethodologyAnswer()`.

Live saisie (option L1, **0 score**) : longueur, présence d’un chiffre, `لأن` interdit, marqueurs نص. **Aucun** mot attendu révélé.

### 7.1 Observabilité S2 (colonnes 035)

Compteurs (pas de copie en clair) :

- taux `422 ungraded` par `question_id`
- taux `sanity=defer` / `not_arabic` / `too_short`
- taux `stuffing_suspected`
- distribution `caps_applied` (`stuffing` / `science`) — S24
- taux `science_status=error` et `diagnosis_code` par grille
- hit-rate cache (après C1)
- latence `grade()` (doit rester cheap : regex)

Sans dashboard, on ne saura pas si une grille est sourde en prod.

---

## 8. UI — ne pas mentir

```
┌─────────────────────────────────────────┐
│ درجة التدريب (ليست علامة بكالوريا)     │
│ منهج:  3/4  ·  مقبول   (ordre: لا)      │
│ محتوى: خطأ علمي — 38 ATP وليس 36        │
│                                         │
│ أحسنت: قدّمت الوثيقة وذكرت رقمين.        │
│ الخطوة التالية: اربط بـ «كلما» دون «لأن».│
│                                         │
│ □ تقديم الوثيقة          ✓              │
│ □ قيمة من المنحنى        ✓              │
│ □ علاقة دون سببية        ✗              │
│ □ استنتاج مرتبط بالهدف   ✓              │
└─────────────────────────────────────────┘
```

`model_answer` **seulement après** une soumission persistée (`da_answers` pour cette question + user).  
`GET .../scenarios/{slug}/correction` actuel (JWT → toutes les model_answer) → **403/404 sans preuve d’eval** (G11).

G12 : pas de chaîne « بكالوريا » **à côté du %**. Le mot « بكالوريا » ailleurs dans le site (nav, leçons) n’est pas interdit.

---

## 9. Trois réparations de confiance (bloquantes publication)

### T1 — PDF annales
| Fait | `public/pdfs/**/*.pdf` = pointeurs LFS ~131 o |
| Done | fichiers > 100 Ko **ou** UI « الموضوع غير متاح (ملف ناقص) » + pas de bouton ouvrir |

### T2 — IDOR Bac blanc
| Fait | `bac_blanc.py` choose/save/submit/correction filtrent `id` **sans** `user_id` |
| Done | `WHERE id=:sid AND user_id=:uid` sur **toutes** les routes scopées session (list / delete inclus, pas seulement choose/save/submit/correction) + test 403 croisé |

### T3 — Économie client-trusted
| Fait | `POST /points/add?points=` et `/add-xp?xp=` acceptent n’importe quel int |
| Done | supprimer les query params libres **ou** whitelist serveur `{action → delta}` |

Sans T1–T3, le coach local n’est **pas** publiable.

---

## 10. Persistance & FSRS

```
da_answers (chemin grade)
  answer_text     = hash_answer(copy)     # plus de plaintext (fermer le v1 DA)
  score           = method_points
  score_max       = total_points
  percentage      = overall_training_percent
  success/errors  = ids de criteria (pas la copie)
  colonnes 035    : rubric_version, grader_version, grading_engine='local_rubric',
                    science_status, stuffing_suspected, method_percent, order_ok,
                    diagnosis_code

FSRS  update_memory(verb_chapter)  si sanity==ok
      NE PAS écrire si science_status=error ET method_percent ≥ 85
      NE PAS écrire si method_percent < 10   (grille sourde / faux 0)
```

Plus tard (pas v1) : carte FSRS par `criterion.id` / diagnostic — « aujourd’hui : كلما sans لأن ».

Ancien moteur : `grading_engine='v2_legacy'`. **Ne pas** recalculer l’historique.

---

## 11. Carte fichiers

```
# NOUVEAU
khawarizmi-backend/schemas/rubric.py
khawarizmi-backend/schemas/document_model.py
khawarizmi-backend/services/local_grader.py
khawarizmi-backend/services/rubric_store.py
khawarizmi-backend/routes/grade.py
khawarizmi-backend/data/rubrics/…
khawarizmi-backend/data/documents/…
khawarizmi-backend/scripts/validate_rubrics.py
khawarizmi-backend/tests/test_local_grader.py
khawarizmi-backend/tests/golden/test_rubric_l0.py
khawarizmi-backend/tests/test_arabic_normalize_contract.py
khawarizmi-backend/migrations/versions/035_grade_columns.py

# RÉUTILISER
services/arabic.py                 # CONTRAT §5.1 — fusionner savoir._normalize
services/savoir_corrector.py       # grave + numeric + _SYNONYMS ($lex)
services/answer_sanity.py          # + defer
services/hashing.py                # HMAC-SHA256 déjà correct
services/fsrs_unified.py
methodology/verb_database.json     # AJOUTER حلّل

# ADAPTATEURS minces
routes/document_analysis_v2.py · document_analysis.py · bac_blanc.py · action_verbs.py
frontend ScenarioRunner + action-verbs/[slug]  — tuer evaluateMethodologyAnswer

# GELÉ / NE PAS MONTER
routes/evaluate.py · routes/ai_evaluate.py
grading/pipeline.py · services/fallback_v2.py   # hors chemin grade
```

`correction_v2.py` reste façade morte. **Ne pas** y ajouter de logique.

---

## 12. Flags

| Variable | Défaut | Effet |
|---|---|---|
| `LOCAL_RUBRIC_GRADER` | `false` | `/api/grade` + adaptateurs |
| `SAVOIR_VETO` | `true` dès LOCAL on | filet science |
| `ENABLE_EXTERNAL_LLM` | ignoré par `grade()` | même à 1, **aucun** appel |

Le flag **n’est lu par aucune route**. `false` **ne** remonte **pas** `evaluate.py` / L2 (`evaluate.py` hors registre). Ne pas l’activer comme « rollback LLM ».

---

## 13. Tests (avant flag prod)

| ID | Test | Attendu |
|---|---|---|
| G1 | `local_grader` n’importe pas `openai`, `llm`, `pipeline` | grep CI |
| G2 | Même copie DA / verb / bac (même `rubric_id`) | 3× même `GradeResult` **hors** `from_cache` |
| G17 | Même copie, deux `rubric_id` distincts (même verb + même semver 1.0.0) | résultats distincts (`rubric_id` différent ; pas de collision de clé cache) |
| G18 | Copie arabe + ATP + enzyme + glucose (FR) | `sanity_code=ok` (ratio ≥ 0.30) ; variants FR matchent |
| G3 | Analyse avec لأن | `forbidden_abs` absent + diagnosis `verb_slip.interpret` |
| G4 | « 36 ATP » + bonne méthode | `science_status=error`, overall capped |
| G5 | Copie = `model_answer` | method ≥ 85 **sinon corriger la Rubric** |
| G6 | Bourrage lexique, 0 keypoint, 0 doc | stuffing, **overall ≤ 50**, method pur, `caps_applied` |
| G6b | Réponse courte correcte (< 20 tokens, vrais keypoints) | **pas** stuffing |
| G7 | `38 ATP · P/O=3` sans arabe | `defer`, **pas** 0 `not_arabic` |
| G8 | `question_id` sans rubric | HTTP 422 `ungraded` |
| G9 | Bac blanc user B lit session user A | 403 |
| G10 | `points/add?points=99999` | 400 ou endpoint absent |
| G11 | GET `/correction` sans soumission | 403 ou 404 |
| G12 | Pas de « بكالوريا » collé au % d’entraînement | lint |
| G13 | Hors-sujet (bonne forme, autre chapitre) | `science_status=error` |
| G14 | Analyse : chiffre 1 bidon, pas la valeur du graphe | `cites_keypoint` absent |
| G15 | 4 étapes présentes **dans le désordre** | points OK, `order_ok=False`, label ≠ متقن |
| G16 | Table de normalisation N1–N10 | chaque ligne du contrat |

Golden L0 : 10 rubrics × (vide, modèle, partielle, science-fausse, hors-sujet, stuffing, verb_slip, désordre) ≥ 80 cas.  
`validate_rubrics.py` : `sum(points)` + `grade(model_answer) ≥ 85` — **bloque le merge**.  
S2 : goldens **négatifs** par grille (hors-sujet, distracteur, fausse valeur) avec un **plafond** de score — aujourd’hui G5 n’attrape que les grilles sourdes aux bonnes réponses, pas celles qui sur-notent le faux. G6/G13/G14 existent déjà en pytest (pas dans le validateur JSON).

---

## 14. Migration (pas de big-bang)

```
S0  T2 IDOR + T3 points + T1 UI PDF
S1  contrat normalize + schemas + local_grader + 10 rubrics
    + 4 DocumentModel analyse + tests G1–G8, G12–G16
S2  POST /api/grade + flag + ScenarioRunner seulement
    + clé cache C1 (rubric_id+doc_id) + G17 + observabilité §7.1
    + tuer evaluateMethodologyAnswer (sinon deux notes)
S3  adaptateurs verb + bac ; tuer evaluate_answer regex
S4  fermer GET correction ; persist hash ; FSRS règles science / <10
S5  mixins chapitre + $lex: extrait fichier  (condition de survie L1)
```

### 14.1 Table d’état (2026-08-27) — C5

| Étape | Statut | Bloque quoi |
|---|---|---|
| S0 T1 PDF LFS | **OUI** | UI « غير متاح », pas de bouton فتح |
| S0 T2 IDOR `bac_blanc` | **OUI** | `_require_own_session` 403/404 |
| S0 T3 `points`/`xp` query | **OUI** | whitelist `action` |
| S1 `grade()` + 10 L0 + G1–G8, G12–G16 | **OUI** | flag `false` |
| S2 `POST /api/grade` + ScenarioRunner | **OUI** | 422 ungraded, 0 JS |
| S3 verb + bac → `grade()` | **OUI** | 422 ungraded si pas de grille. VERB_RULES hors routes. diagnostic/global → `/api/grade`. « جاهز للبكالوريا » tué. |
| S4 hash persist + GET `/correction` | **OUI** | G11 : 404 sans da_answers de CET élève. DA v1 + bac submit = `hash_answer`. GET bac `student_answer=""`. FSRS via `may_write_fsrs`. |
| S5 mixins + `$lex:` fichier | **OUI** | `data/lexicons/svt_terms.v1.json` (clés L0). Mixin `{chapter_slug}.json` union au `load()`. Pas de lactose inventé. |
| S6 evaluate-v2 → `grade()` | **OUI** | 0 L2 / 0 LLM |
| S7 `/api/evaluate/methodology` | **OUI** | 422 ungraded si pas L0 |
| S8 JS stub + `evaluate.py` hors registre | **OUI** | `GRADER_VERSION=1.1.4` |
| S9 UI 2 axes + G12 | **OUI** | `GradeResultCard` : درجة التدريب, منهج ≠ محتوى, ungraded = —, pas de بكالوريا collé au % |
| S10 drill + exercices copies | **OUI** | `/api/drill/submit` et `/api/exercices/{id}/correct` → `grade()` / 422. QCM local intact. 0 GPT-4o. |
| S11 schéma + evaluation_mode | **OUI** | Dual-coding evaluate = 0 (pas Vision). `evaluation_mode` → `grade()` / ungraded. |
| S12 observabilité §7.1 | **OUI** | `GET /api/grade/metrics` : ungraded par qid, sanity, stuffing, science, diagnosis, latence. Cache = 0 (pas dans `grade()`). |
| S13 colonnes 035 | **OUI** | `da_answers` : `grading_engine`, `method_percent`, `science_status`, `diagnosis_code`, hash. Pas de copie. |
| S14 cache C1 | **OUI** | clé `grade:{version}:{rubric_id}:{rubric.ver}:{doc}:{doc.ver}:{verb}:{hash}` — 0 `user_id`. Hors `grade()`. |
| S15 chatbot explain-back / boss-fight | **OUI** | Plus de % overlap / longueur. `ungraded`, 0 copie, 0 `model_answer`. Pas d’alias L0. `GRADER_VERSION` reste `1.1.4`. |
| S16 cache Redis optionnel | **OUI** | `grade_cache` SETEX 7 j via `state.redis` si dispo ; mémoire sinon. 0 Redis dans `grade()`. 0 `user_id`. 0 copie. |
| S17 quota + FSRS sur `/api/grade` | **OUI** | S17 : `evaluate_limit` si `sanity==ok`. **S22** : defer aussi. Vide/cache/422/stop = 0. FSRS `may_write_fsrs`, 0 copie, 0 `da_answers` sur cette route. |
| S18 goldens négatifs `validate_rubrics` | **OUI** | Merge bloqué si hors-sujet ou 36 ATP overall > 40, ou vide ≠ 0. Mêmes copies que golden L0. `GRADER_VERSION` 1.1.4. |
| S19 cache sha16 | **OUI** | clé C1 + `sha16` Rubric+Document. Éditer un critère sans bump de version → nouvelle clé. 0 `user_id`. Hors `grade()`. |
| S20 `counter_examples` L0 | **OUI** | ≥2 par grille dont `off_topic`, `axis` overall/method, `use` fermé `model+atp36`. Hors GET rubric. |
| S21 caps hors méthode | **OUI** | stuffing/science → `overall` + `caps_applied`. `method_percent` pur. متقن interdit si stuffing. `GRADER_VERSION=1.1.5`. |
| S22 defer consomme le quota (B4) | **OUI** | `should_count_quota` : `ok` **ou** `defer`. G7 reste `defer` ≠ 0. FSRS non. Cache non. Pas de compteur 50/jour. `GRADER_VERSION` inchangé `1.1.5`. |
| S23 filet_sha16 cache (B2) | **OUI** | clé + `filet_sha16` (graves, numériques, `$lex`, `_SYNONYMS`, errata). `model_answer` hors. 0 `user_id`. Hors `grade()`. `1.1.5` inchangé. |
| S24 métriques `caps_applied` | **OUI** | `GET /api/grade/metrics` : compteurs `stuffing` / `science`. 0 copie. Hors `grade()`. `1.1.5` inchangé. |
| S25 UI caps | **OUI** | `GradeResultCard` : سقف 50 · حشو / سقف 40. Écart منهج vs درجة expliqué. Hors `grade()`. `1.1.5` inchangé. |
| S26 P/O contextualisé | **OUI** | plus de `p/o` nu ni `nadh…atp`. FADH2=2 n’est pas capé. 38 ATP juste, 36 cap. `filet_sha16` invalide le cache. `1.1.5` inchangé. |
| S27 filet ATP clavier DZ | **OUI** | ٣٦ ATP cap 40. `ليس 36 بل 38` pas capé. 36 seul cap. `GRADER_VERSION=1.1.6`. Pas de fusion normalize. |
| S28 FSRS idempotent | **OUI** | cache hit → 0 quota (déjà) **et** 0 `update_memory`. `may_write_fsrs` refuse `from_cache`. Hors `grade()`. `1.1.6`. |

**Gates :**
- S0 → S1 : G9, G10 verts (même sans grader) — **contourné volontairement** le 2026-08-27 : S1 = moteur **testable hors prod**, pas une mise en ligne. Le gate redevient bloquant le jour où `LOCAL_RUBRIC_GRADER=true`.
- S1 → S2 : L0 golden + `validate_rubrics` verts, G1, **clé cache avec `rubric_id` (C1)**, G17
- S2 → S3 : ScenarioRunner seul, 0 incident « note inventée », flag on ≥ quelques jours
- S3 → S4 : G2 (parité 3 surfaces)
- S4 → S5 : G11 + plus de plaintext `answer_text` sur le chemin grade

---

## 15. Chemin optimiste (L1 sans usine à LLM)

L0 tient avec **10 grilles à la main**. L1 ne tient **pas** si chaque question recopie 40 synonymes.

Ce qui rend L1 réaliste **sans** LLM :

1. `$lex:` branché sur `_SYNONYMS` (déjà ~centaines de termes FR/AR)
2. Templates verbe (4–8 cases) écrits **une fois**
3. Mixins chapitre (thème + distractors + grave)
4. Question = 20 lignes (keypoints + ids lexique)
5. `validate_rubrics.py` empêche les grilles sourdes

**Politique d’enrichissement du lexique (tranchée — C2) :** P8 reste. On **ne** stocke **pas** les copies en clair « pour enrichir `$lex:` ». Trois leviers, dans l’ordre :

1. Auteur humain + `$lex:` / `_SYNONYMS` + mixins (plan L1)
2. Analytique **fréquence de hash** : HMAC les plus fréquents parmi `science_status=error` ou `method_percent<40` — le prof **reproduit** la formulation en classe, 0 plaintext lu
3. Sessions de récolte enseignant **opt-in** (table séparée, rétention courte) — **produit à part**, pas v1

Sans (1), L1 ne scale pas. (2) et (3) sont de la gouvernance, pas du chemin de note.

**Plus tard seulement :** FSRS par trou, live structurel client, stemming outils, schéma-texte (légendes), mineur contrastif **interne** (le prof coche des n-grammes — jamais d’écriture auto en prod).

**Jamais :** parseur auto du livre, Aho-Corasick avant que le lexique soit énorme, Bloom filter JS, 3 soumissions / 4 h type examen, `/20` « pour faire plaisir ».

---

## 16. Risques

| Risque | Mitigation |
|---|---|
| 10 grilles ≠ produit | flag + `ungraded` |
| Rubric mal écrite | G5 + `validate_rubrics.py` |
| Deux `normalize` qui divergent | fusion §5.1, Savoir délègue |
| Tentation « un petit LLM » | G1 grep + P1 |
| Fuite grille | pas de variants front ; GET rubric = labels |
| Cache 7 j fige une grille corrigée | `rubric_id` + versions + `doc_id` (+ sha16 optionnel) |
| Collision cache 2 questions même semver | **C1** : identités dans la clé ; G17 |
| Historique mixte v2 / local | `grading_engine`, pas de recalcul du passé |
| Collision N6/N7 (ئ→ي, ة→ه) | golden anti-collision : 2 clés `$lex:` distinctes ≠ même chaîne normalisée |

---

## 17. Interdits (rappel)

- `evaluate.py` / `ai_evaluate.py` / température LLM / `user_id` dans la clé cache  
- Recréer SM-2 (FSRS existe)  
- L2 / ONNX comme juge v1  
- `VERB_RULES` en fallback silencieux  
- Variants dans le bundle JS  
- Levenshtein  
- Recalculer les anciennes notes  

---

**Fin.** Architecture hybride « LLM si flag » = **autre** proposition, hors périmètre.

*Signé comme châssis + durcissements audits (normalize, hors-sujet, stuffing chiffré, keypoints DA, ordre=label, 0 2ᵉ cerveau).*
