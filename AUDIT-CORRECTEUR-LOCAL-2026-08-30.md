# Audit — correcteur local `grade()` (2026-08-30)

**Cible :** `khawarizmi-backend/services/local_grader.py` v**1.1.7** + montage routes + grilles git
**Branche :** `arena/01a053f2-project-sinamind` (HEAD `56200fb`)
**Méthode :** lecture du code, exécution du suite, probes adversariales reproductibles
(`scripts/probe_audit_correcteur_local.py`). Règle du repo : faits / écarts / jugement.

---

## 0. Verdict en une ligne

> Le moteur tient ses promesses structurelles (0 LLM, grille git, caps honnêtes,
> `ungraded` sans fallback). **1 vrai bug de rappel** (enclitiques لانه/لانها),
> **2 neutralisations jouables** (36 ATP + « 38 ATP » ; bourrage + 1 chiffre du doc),
> **3 tests rouges** (mur `NoLocalGradeWall` vs contrats S3/S9/S25 non tranchés),
> et le **suite grade n'est dans aucun gate** (CI ni pre-commit).

---

## 1. Exécution (faits mesurés)

| Contrôle | Résultat |
|---|---|
| `pytest tests/test_local_grader.py + test_grade_s2..s29 + bac2023` (`--noconftest`) | **179 ✓ / 3 ✗** |
| Échecs | `test_grade_s3::test_diagnostic_page_does_not_import_js_grader`, `test_grade_s9::test_surfaces_use_grade_result_card`, `test_grade_s25::test_adapters_forward_caps` |
| `scripts/validate_rubrics.py` | **13 grilles OK** (G5 modèle ≥ 85 %, hors-sujet, 36 ATP, vide, counter_examples) |
| Perf plafond (copie 20 000 car = limite route) | ~230–280 ms, 0 erreur |
| `.github/workflows/ci.yml` + `.pre-commit-config.yaml` | **ne lancent ni le suite grade, ni `validate_rubrics.py`** |

Montage vérifié : `routes/grade.py` (`/api/grade` + `/questions` + `/rubric` + `/metrics`)
et `grade_or_none` branché sur `bac_blanc`, `exercices`, `methodology`, `flashcards`,
`dual_coding`, `document_analysis` v1/v2 — sans fallback `VERB_RULES`/L2/LLM (tests S3 ✓ sur ces fichiers).

---

## 2. Findings

### F1 — BUG (haut) : enclitiques suffixaux non matchés → points perdus — **CORRIGÉ en 1.1.8 (S30)**

> **Fix appliqué :** liste fermée `_ENCLITICS = (ها هم هن هما كم نا ه ك ي)` symétrique
> de `_PROCLITICS`, implémentée comme une regex unique par needle
> (proclitique optionnel + base + enclitique optionnel) — les combos
> `ولأنها` matchent aussi, sans énumérer le produit cartésien. Garde ≥ 3 chars.
> Non-gérés volontairement : `ات` (pluriel ≠ pronom), ة→ت (`خميرتها`).
> `GRADER_VERSION=1.1.8` (clé cache auto-invalidée), 12 tests `tests/test_grade_s30.py`,
> pins s8/s15–s29 mis à jour. Effet mesuré : copie modèle avec «لأنها/لأنه» 75 % → **100 %**.
> Bonus perf : copie 20k chars ~280 ms → **~75 ms**.
`_unigram_forms` (`local_grader.py`) génère les formes **préfixées** (proclitiques
وال/فال/بال/لل/كال/ال/و/ف/ب/ك/ل) mais **aucune forme suffixée**. Or l'arabe écrit
colle les pronoms suffixés :

```
copie modèle avec «لأن»    → 100 %, diag all_correct
même copie avec «لأنها»    →  75 %, cause=absent, diag first_required_gap.cause
même copie avec «لأنه»     →  75 %, cause=absent
«بسببها»                   → cause=absent
```

«لأنه/لأنها» sont des formulations ultra-courantes au Bac. C'est une **perte de
rappel injuste** : l'élève écrit la bonne cause et perd 25 %. Toutes les grilles
avec critère cause-type (`yeast-glucose-interpret`, `enzyme-temp-interpret`,
`greffe-ltc-interpret`, …) sont exposées.
**Fix proposé (cohérent avec la philosophie « liste fermée »)** : ajouter une liste
fermée d'enclitiques (ها هم هن كم نا ه) symétrique de `_PROCLITICS` — ce n'est pas
du stemming, c'est le même contrat. Bump `GRADER_VERSION` → 1.1.8 + goldens.

### F2 — Neutralisation (moyen) : « 36 ATP » lavé par un « 38 ATP » placé n'importe où
Le filet saute si `38 atp` apparaît **où que ce soit** dans la copie :

```
modèle + «وتنتج 36 ATP»                  → science=error, overall=40  ✓
modèle + «36 ATP لكن 38 ATP صحيح»        → science=ok,    overall=100 ✗ aucun flag
```

Le commentaire du code dit « pas un parseur de نفي » — légitime pour
« 36 غير صحيحة بل 38 », mais l'exemption actuelle est **aveugle à la position** :
l'élève qui *affirme* 36 puis ajoute « 38 ATP » en bout de phrase est noté 100 %.
**Fix proposé** : borner l'exemption à une fenêtre ~80 caractères autour du « 36 »
(réutiliser `_near` de `savoir_corrector`), ou la supprimer si aucun golden ne le justifie.

### F3 — Neutralisation (moyen) : bourrage + 1 chiffre du doc = exemption totale de stuffing
`_stuffing` retourne False dès qu'un `cites_keypoint` est full (`kp_full or obj_full`) :

```
bourrage lexical pur (30 tokens répétés)      → stuffing ✓, cap 50 ✓
même bourrage + « العدد يصل 18 »              → stuff=False, 75 %, aucun cap ✗
```

Le chiffre magique du document désactive tout le garde-fou. **Fix proposé** :
l'exemption devrait exiger kp_full **et** un signal syntaxique minimal
(ex. ≥ 1 marqueur de cause/structure), ou ne porter que sur le critère concerné.

### F4 — Diagnostic faussé (bas-moyen) : hors-sujet maquillé par 1 mot de thème
`theme_min_hits=1` sur la grille levure : une copie 100 % tectonique qui glisse
« الخميرة » une fois passe le filet hors-sujet. La **note reste 0** (aucun critère
touché) mais l'élève reçoit `verb_slip.analyse` (« فسّر بـ لأن ») au lieu de
`off_topic` — feedback pédagogiquement faux. **Fix proposé** : `theme_min_hits ≥ 2`
sur les grilles à lexique riche, ou test de densité (hits thème / tokens).

### F5 — Contrat non tranché (à décider) : mur `NoLocalGradeWall` vs tests S3/S9/S25
`khawarizmi-frontend/src/app/diagnostic/global/page.tsx` (et `action-verbs/[slug]`)
affichent désormais un mur honnête « لا شبكة تقييم محلية » — **mais** 3 tests
backend exigent encore `apiClient.grade` + `GradeResultCard` + `capsApplied` sur
cette page → suite rouge. Le mur n'est couvert par **aucun** test ni doc
(`ARCHITECTURE-COACH-LOCAL.md` n'en parle pas). Deux sorties possibles :
1. le mur est la décision finale → mettre à jour S3/S9/S25 + ajouter un test qui
   verrouille le mur ;
2. c'est une régression → restaurer la carte.
**À trancher par le propriétaire ; en l'état le suite ne peut pas être mis vert.**

### F6 — Gate manquant (moyen) : le suite grade n'est nulle part
`ci.yml` ne lance que `test_methodology*` + quelques fichiers ; pre-commit ne lance
pas `validate_rubrics.py`. Une grille sourde ou une régression moteur peut être
mergeée sans rien voir. **Fix proposé** : job CI `grader` =
`pytest tests/test_local_grader.py tests/test_grade_s*.py --noconftest` +
`python scripts/validate_rubrics.py`.

### F7 — Piège dormant (bas) : `cites_trend` inutilisé + variantes contradictoires
Aucune grille n'utilise `cites_trend`, mais `documents/yeast-glucose-curve.v1.json`
déclare `trend=increase_then_plateau` avec des `trend_variants` contenant
**«يتناقص»** (décroît). Le premier auteur qui branche `cites_trend` validera une
tendance inverse. Nettoyer les variantes ou les typer par direction.

### F8 — Surface non authentifiée (bas) : `POST /api/evaluate/methodology`
Pas de `Depends(get_current_user)` (contrairement à `/api/grade`, `exercices`,
`flashcards`) : gradable sans compte, et **bypass du quota 15/h** (qui n'existe que
sur `/api/grade`). Moteur déterministe = coût faible, mais incohérent avec le
contrat quota. Ajouter l'auth + le quota, ou assumer et documenter.

### F9 — Fallback silencieux (info) : digest cache non pepperé si `SECRET_KEY` absent
`grade_cache._digest` retombe en silence sur SHA-256 brut (dictionnalisable) si
`hash_answer` lève (pepper absent). Faire échouer bruyamment ou logger une fois.

### F10 — Messages (info)
- Bourrage sans chiffre → diag affiché `unanchored` (« لا رقم من الوثيقة ») alors que
  le cap appliqué est `stuffing` (priorité `_diagnosis` : unanchored avant stuffing).
- Réponse anglaise à tokens chimie → `sanity=defer` mais diag `off_topic`
  (problème de langue traité comme hors-sujet).

---

## 3. Invariants confirmés (ce qui tient)

- **0 LLM / 0 I/O** dans `grade()` (test G1 AST ✓, relecture ✓) ; imports
  génératifs absents.
- **Normalisation N1–N10 fermée et idempotente** ; frontières tenues
  (`لان` ⊄ `الانزيم`, `نمو` ⊄ `النموذج`, `كن` ≠ `لكن`), séparateur décimal `٫`,
  chiffres orientaux, `18.0` = 18, année `2018` ≠ keypoint 18.
- **Anchoring DA** : `cites_keypoint` sur valeur±tolérance du DocumentModel, pas
  « un chiffre quelconque » ; `number_present` interdit sur DA (validateur schéma ✓).
- **Caps deux axes** : science 40 / stuffing 50, `caps_applied` propagé jusqu'à
  l'UI (`GradeResultCard` ✓ S25 pour SCENARIO/VERB_FLOW/API), méthode ≠ global,
  bannière « ليست علامة بكالوريا رسمية » partout.
- **Filet Savoir** : 36/32 ATP, P/O NADH=3/FADH=2, erreurs graves localisation ADN,
  errata 10⁶→10⁴ en **jaune sans cap** (P11/P12 ✓), hors-sujet golden (GEOLOGY) ✓.
- **Honnêteté** : sans Rubric → `UngradedError` / 422 `ungraded` (jamais 0, jamais
  VERB_RULES/JS/L2) ; verbe `schematiser` → manuel assumé ; FSRS pas écrit sur
  cache hit ni sur sanity ≠ ok (S28 ✓) ; quota ignoré vide/cache/422, compté sur
  `defer`.
- **Vie privée** : clé cache = `GRADER_VERSION + rubric canonique (sha16) +
  filet_sha16 + HMAC-SHA256(pepper, copie)` — pas de copie en clair, pas de
  user_id (équité), `model_answer`/variants jamais exposés par les routes
  publiques ; métriques = compteurs seuls.
- **Robustesse** : regex des grilles échappées pour les formes (`re.escape`) ;
  patterns Savoir bornés (≤ 80 car) ; pas de ReDoS injectable par la copie élève
  (la copie n'est jamais traitée comme regex). Perf 20k car < 300 ms.

---

## 4. Jugement et ordre de frappe

| # | Action | Coût | Effet |
|---|---|---|---|
| 1 | F1 enclitiques fermés + bump 1.1.8 + goldens — **CORRIGÉ (S30, v1.1.8, commit du 2026-08-30)** | faible | rend 25 % à des copies correctes |
| 2 | F6 gate CI (`grade suite` + `validate_rubrics`) | faible | protège tout le reste |
| 3 | F5 trancher mur vs carte, puis verdir S3/S9/S25 | décision | suite vert, contrat clair |
| 4 | F2 fenêtre _near sur l'exemption 38 ATP | faible | ferme l'exploit notation |
| 5 | F3 conditionner l'exemption stuffing | faible | bourrage re-détecté |
| 6 | F4 theme_min_hits ≥ 2 (grilles concernées) | grille | diagnostics justes |
| 7 | F7/F8/F9/F10 nettoyages | faible | hygiene |

Le moteur est **sain dans sa structure et ses limites** ; les écarts sont des
réglages de rappel et de garde-fous, pas des mensonges de note — sauf F1 qui
**sous-note** des copies correctes et doit passer en premier.

**Reproduction :** `cd khawarizmi-backend && python scripts/probe_audit_correcteur_local.py`
