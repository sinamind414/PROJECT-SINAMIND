# Procédure d'annotation humaine du golden set (approche A)

**Objectif** : remplacer les annotations SYNTHÉTIQUES (`synthetic_keyword_v1`)
par des annotations d'un expert SVT — les métriques MAE/κ deviennent alors
des mesures de justesse absolue, pas de non-régression.

**Durée estimée** : 2-3 h pour 50 questions × 2-3 copies (125 items).

---

## 1. Fichiers concernés

| Fichier | Rôle |
|---|---|
| `khawarizmi-backend/data/golden_set_onec.json` | questions sources (50) — NE PAS MODIFIER |
| `khawarizmi-backend/tests/golden/golden_annotated.json` | annotations — LE fichier à remplacer |
| `khawarizmi-backend/tests/golden/metrics.py` | calcul MAE/κ/severe (inchangé) |
| `khawarizmi-backend/tests/golden/test_golden_local.py` | tests CI avec seuils (inchangé) |

## 2. Format d'un item annoté

```json
{
  "question_id": "gs_001",
  "verb_slug": "restitution",
  "chapitre": "Synthèse des protéines",
  "question": "أين يحدث نسخ المعلومة الوراثية...؟",
  "student_answer": "يحدث نسخ المعلومة الوراثية في النواة...",
  "bareme": 2,
  "reponse_attendue": "يحدث نسخ المعلومة الوراثية...",
  "mots_cles_attendus": ["النواة", "ADN", "نسخ"],
  "human_score": 2,
  "human_score_max": 2,
  "human_dominant_error": "all_correct",
  "human_matched_criteria": ["النواة", "ADN", "نسخ"],
  "human_unmatched_criteria": [],
  "annotator": "expert_svt",
  "annotation_date": "2026-08-15"
}
```

## 3. Règles d'annotation

1. **human_score** : note sur `bareme` (entier). Une copie ÉGALE à la réponse
   modèle = `bareme` (par définition). Une copie partielle = proportion de
   critères satisfaits, arrondie à l'entier le plus proche.
2. **human_dominant_error** : un des codes valides (cf. §4). Une copie vide →
   `empty`. Une copie parfaite → `all_correct`. Une copie partielle →
   `partial_correct` (sauf erreur scientifique détectée → `scientific_error`).
3. **human_matched_criteria / human_unmatched_criteria** : listes de
   mots-clés SATISFAITS / NON satisfaits (d'après `mots_cles_attendus`).
4. **Ne PAS modifier** : question_id, verb_slug, chapitre, question,
   student_answer, bareme, reponse_attendue, mots_cles_attendus — ces champs
   viennent du golden source.
5. **annotator** : `"expert_svt"` + `annotation_date` au format ISO.

## 4. Codes `human_dominant_error` valides

`scientific_error`, `methodology_error`, `off_topic`, `partial_correct`,
`all_correct`, `insufficient`, `gibberish`, `too_short`, `empty`,
`not_arabic`, `repeated_chars`, `server_error`, `unknown`

## 5. Cohérence (vérifiée automatiquement)

Lancer avant livraison :

```bash
cd khawarizmi-backend
python scripts/validate_golden_annotations.py
```

Vérifie :
- chaque item a tous les champs requis ;
- `human_score` ∈ [0, bareme] (entier) ;
- `human_dominant_error` est un code valide ;
- `human_matched_criteria` + `human_unmatched_criteria` partitionnent
  `mots_cles_attendus` (tolérance aux formes fléchies ال) ;
- une copie vide → code `empty` + score 0 ;
- une copie égale à `reponse_attendue` → score = bareme.

## 6. Après livraison

1. Remplacer le contenu de `golden_annotated.json` (garder la structure
   `{"metadata": {...}, "items": [...]}`).
2. Lancer `python tests/golden/build_golden_annotated.py` ? NON — ce script
   régénère les annotations SYNTHÉTIQUES. Les annotations humaines sont
   livrées directement dans `golden_annotated.json`.
3. Lancer les tests :
   ```bash
   python -m pytest tests/golden/test_golden_local.py -v --tb=short
   ```
4. Les seuils CI (L2 MAE ≤ 0.85, savoir MAE ≤ 0.35, κ ≥ 0.45) deviennent
   des mesures absolues. Le κ savoir ≥ 0.65 permettra de réactiver la
   remédiation de l'étage savoir (actuellement désactivée — κ synthétique
   0.449).

## 7. Stratégie de livraison progressive

- Annoter d'abord 30/50 questions (copie parfaite + partielle) → livrer.
- Compléter les 20 restantes + les copies vides (25 items) ensuite.
- Les métriques sur 30 questions annotées valent plus que sur 50
  synthétiques.
