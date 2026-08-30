# L0 — 10 grilles d’entraînement (comme le livre)

**Lot :** 4 حلّل · 3 فسّر · 2 استنتج · 1 نص علمي  
**Moteur `grade()` :** `services/local_grader.py` (0 LLM, flag `LOCAL_RUBRIC_GRADER` défaut false). Tests : `pytest tests/test_local_grader.py tests/golden/test_rubric_l0.py --noconftest`.  
**Index machine :** `khawarizmi-backend/data/rubrics/index.json`

Spécimen détaillé (خميرة) : `BAREME-L0-KHAMIRA.md`.

---

## Carte

| # | `rubric_id` | Verbe | Document (chiffres qui comptent) | /pts |
|---|---|---|---|---|
| 1 | `manhadjiya-yeast-analyse` | حلّل | 9 → **18** / **6** | 4 |
| 2 | `greffe-ltc-analyse` | حلّل | **10** j vs **5** j · **2,5** vs **4,8** | 4 |
| 3 | `enzyme-temp-analyse` | حلّل | **37°م** → 100% · **80°م** → 0 | 4 |
| 4 | `photo-o2-analyse` | حلّل | O2 **0** puis hôte **6** مل | 4 |
| 5 | `greffe-ltc-interpret` | فسّر | mêmes 10/5 · 4,8/2,5 · **لأن ذاكرة/LTc** | 4 |
| 6 | `yeast-glucose-interpret` | فسّر | 18 vs 6 · **لأن** مادة أيض | 4 |
| 7 | `enzyme-temp-interpret` | فسّر | après 37° · **لأن تمسخ** | 4 |
| 8 | `greffe-ltc-deduce` | استنتج | **خلوية** + دليل LTc (pas un roman) | 3 |
| 9 | `synapse-curare-deduce` | استنتج | كورار على **مستقبلات Ach** (ت4/ت5) | 3 |
| 10 | `proteine-adn-scientific-text` | نص علمي | intro+مشكل / نسخ+ترجمة / خاتمة | 5 |

Même dossier طعم : **2 → 5 → 8** = jours 1–2–3 des ateliers (`ateliers/atelier-02` / `03`).  
خميرة : **1 → 6**. إنزيم : **3 → 7**.

---

## Ce que le prof change selon le verbe

| Verbe | Oui | Non |
|---|---|---|
| حلّل | الوثيقة + **vrai** chiffre + كلما | لأن / هذا يدل / le cours |
| فسّر | **لأن** + mécanisme du cours + le chiffre | refaire le tableau · استنتج le type |
| استنتج | **جملة** + دليل court | القصة · إعادة حلّل |
| نص علمي | 3 blocs + thème | liste à puces · ADN sort dans الهيولى |

**Science (filet) :** 36 ATP · CO2 « produit » en photosynthèse · ADN dans le cytoplasme.  
**Hors-sujet :** 0 mot du thème → محتوى خطأ.

---

## Fichiers

```
khawarizmi-backend/data/rubrics/templates/{analyse,interpret,deduce,scientific-text}.json
khawarizmi-backend/data/rubrics/questions/*.v1.json     (10)
khawarizmi-backend/data/documents/*.v1.json            (5)
```

Suite code : `local_grader.grade()` + `validate_rubrics.py` (copie modèle ≥ 85 %).
