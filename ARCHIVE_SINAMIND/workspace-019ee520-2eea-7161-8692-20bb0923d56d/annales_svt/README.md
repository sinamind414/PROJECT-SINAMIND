# Traitement Annales SVT — Bac Sciences Expérimentales (Algérie)

Pipeline d'EXTRACTION → TRANSCRIPTION → TAGGING des questions d'annales vers un JSON normalisé.

## Mission (3 phases par question)
1. **EXTRAIRE** — isoler le contenu brut de la question (scan/PDF/texte).
2. **TRANSCRIRE** — corriger l'arabe corrompu (mojibake), fautes, garder le sens + termes scientifiques (ADN, ARNm, ribosome…).
3. **TAGGER** — associer 1 micro-concept principal (+ 0 à 2 secondaires) parmi les **42 autorisés**.

## Paramètres validés (cette session)
| Paramètre | Valeur |
|---|---|
| Livraison des sources | Upload dans `input/` |
| Priorité de traitement | `LIVRES ANNALES SVT BAC` |
| Volume | Lot maximal (tout ce qui est fourni) |
| `texte_corrige` | Arabe corrigé uniquement (pas de traduction FR dans notes) |

## Structure
```
annales_svt/
├── input/                 # ← déposer ici les fichiers (PDF, images, txt)
├── output/                # JSON normalisé consolidé
│   └── questions_taggees.json
├── referentiel/
│   └── micro_concepts.json   # les 42 concepts (référence de validation)
└── scripts/
    └── validate_tags.py      # vérifie conformité des tags
```

## Format de sortie (JSON)
Voir `output/questions_taggees.json`. Champs :
- `id`, `texte_corrige`, `micro_concept_id`, `secondary_concepts`
- `source`, `type`, `difficulte`, `bac_frequent`, `notes`

## Règles de tagging (rappel)
- IDs **uniquement** parmi les 42 de `referentiel/micro_concepts.json`.
- Concept **le plus spécifique** possible.
- Prioriser les concepts `bac: true` (marqués BAC fréquent).
- Si doute → `mc_xxx_xx` + `a_verifier: true`.

## Procédure
1. Déposez les fichiers dans `annales_svt/input/`.
2. Je lis chaque source, extrait et corrige.
3. Je tagge et j'écris dans `output/questions_taggees.json`.
4. Je lance `validate_tags.py` pour contrôle final.
