# Pack d'intégration — S1 à S4
**Contrat de données** · pastille `reconstitue` · `valide: false` par défaut

| Champ | Valeur |
|---|---|
| Code | `INT-S1S4-CONTRACT-001` |
| Statut | **Proposition** — n'invente pas l'API runtime du site |
| Règle d'or | Aucun sujet n'entre en `valide: true` sans figures binaires + relecture humaine |
| Note auto | **Interdite** (`scoring: "corrigé_à_consulter"`) tant que L2 `reformulee < 6/8` |
| Cadre juridique annales | Loi **18-07** (données mineurs) ≠ RGPD. Ces 4 sujets = **reconstitués**, pas des épreuves officielles |

Ce pack **ne remplace pas** C. Il empêche C de casser la v3.

---

## 1. Décisions figées (ne plus rouvrir)

| Décision | Valeur |
|---|---|
| N exercices Bac exploitables *actuels dans le fichier* | **19** = 6 / 4 / 2 / 4 / 3 (D1-U1→U5), 0 D2, 0 D3 |
| S1–S4 | **rédigés**, **hors produit** jusqu'à C |
| ATP respiration | **38** = valeur programme / barème |
| O₂ photosynthèse | **eau**, jamais CO₂ |
| S (ondes) / noyau externe | **liquide** |
| Étiquette 2026 | interdite sur ces sujets |
| Correcteur | L2 vécu ≈ **4,6/10** ; 5,1 = mixte non déployé |

---

## 2. Pastilles (enum fermé)

```ts
type AuthenticiteSujet =
  | "officiel"       // PDF réel d'une session publiée, hash contrôlé
  | "reconstitue"    // S1–S4 : gabarit Bac, pas une session
  | "entrainement";  // drill / QCM, hors épreuve

type StatutValidation = "brouillon" | "relu_humain" | "publie";
type ScoringMode = "interdit" | "corrige_a_consulter" | "note_auto";
```

| Sujet | `authenticite` | `scoring` | `valide` à l'ingestion |
|---|---|---|---|
| S1–S4 | `"reconstitue"` | `"corrige_a_consulter"` | **`false`** |
| Annales 2008–année connue, PDF réel | `"officiel"` | selon correcteur | `false` jusqu'à relecture |
| Entrées **2026** | ne jamais `"officiel"` | — | rester hors catalogue ou `"reconstitue"` + pastille UI |

**UI obligatoire** (AR + FR) :

> تدريب مُعاد بناؤه — ليس موضوعاً رسمياً ولا موضوع دورة 2026.

---

## 3. Contrat `SujetBac` proposé

Champs **minimaux**. Renommer pour matcher le type réel au moment de C ; ne pas perdre la sémantique.

```ts
type SujetBacReconstitue = {
  id: string;                    // S1-D2-RESP-RECONST-001 …
  code: string;
  authenticite: "reconstitue";
  filiere: "SE";
  niveau: "3AS";
  domaines: Array<"D1" | "D2" | "D3">;
  unites: string[];              // ex. ["D2-U2"]
  titre_ar: string;
  titre_fr: string;
  duree_min: 120;
  bareme_total: 20;
  scoring: "corrige_a_consulter";
  valide: false;                 // défaut ingestion
  statut: "brouillon" | "relu_humain" | "publie";
  exercices: ExerciceBac[];
  documents: DocumentFigure[];   // JAMAIS un DocumentRef texte-seul
  interdits_redaction: string[]; // "38 ATP", "Wilson", …
  anti_f3: PairePolarite[];
  alerte_f2: true;
  sources_internes: string[];    // chemins md
};
```

### `DocumentFigure` — le point qui cassait le site

```ts
type DocumentFigure = {
  id: string;                    // "S3-D4"
  kind: "svg" | "png" | "csv_table";
  path: string;                  // public/figures/bac/s3/s3_d4_chaine.svg
  sha256: string;                // fichier réel, pas pointeur LFS
  bytes_min: 500;                // garde-fou : 132 octets = LFS → CI fail
  width: 1200;
  height: 800;
  rtl: true;
  nb_lisible: true;
  titre_ar: string;
  consigne_legende_ar: string;
  interdit_sur_dessin: string[];
};
```

**Règle CI :** si `bytes < 500` ou contenu commençant par `version https://git-lfs.github.com` → **build rouge**. Même dette que `public/pdfs/` et l'ONNX.

### `ExerciceBac`

```ts
type ExerciceBac = {
  id: string;                    // "S1-E1"
  type: "exploitation" | "raisonnement";
  points: number;                // 10 + 10
  questions: QuestionBac[];
};

type QuestionBac = {
  id: string;
  points: number;
  verbe: "عرّف" | "استخرج" | "حلّل" | "فسّر" | "علّل" | "استنتج" | "أظهر" | "أنجز_نصا";
  documents: string[];           // ids DocumentFigure
  corrigé_interne: string;       // équipe, pas lexique Savoir
  bareme_atomique: { critere: string; pts: number }[];
};
```

---

## 4. Catalogue S1–S4 (pour le mapping JSON)

| id | Domaine | Unités | Fichier source | Docs | Interdits de rédaction |
|---|---|---|---|---|---|
| `S1-D2-RESP-RECONST-001` | D2 | D2-U2 (+ U3 léger) | `S1-sujet-type-bac-D2-respiration.md` | mito, QR, chaîne oxphos, aéro/ferment | photosynthèse développée |
| `S2-D3-TECTO-RECONST-001` | D3 | U1+U2+U3 | `S2-sujet-type-bac-D3-tectonique.md` | D1–D6 vitesses, coupe globe, gous, ophiolite, foyers | dorsale / paléomag (S4) |
| `S3-D2-PHOTO-RECONST-001` | D2 | D2-U1 | `S3-sujet-type-bac-D2-photosynthese.md` | chloro, Hill, spectres, chaîne, Calvin, pools | **38 ATP**, respiration |
| `S4-D3-DORSALE-RECONST-001` | D3 | U1+U3 | `S4-sujet-type-bac-D3-dorsale.md` | dorsale, âge, flux, anomalies, chrons, TRR | gous, Benioff, ophiolite, Wilson |

**Fichiers figures attendus (24)**
`public/figures/bac/{s1,s2,s3,s4}/` — noms déjà spécifiés dans chaque sujet (`s2_d1_…`, `s3_d4_…`, `s4_d4_…`).

**Fichier items (séparé, pas mélangé à l'OCR)**

```
data/sujets_reconstitues/s1.json
data/sujets_reconstitues/s2.json
data/sujets_reconstitues/s3.json
data/sujets_reconstitues/s4.json
```

Ne **pas** append dans `sciences_bac_exercices.json` tant que les 89 OCR `valide: true` n'ont pas été basculés à `false`.

---

## 5. Ingestion — machine à états

```
brouillon + valide:false + scoring:interdit
        ↓ figures présentes (CI sha256 + bytes)
        ↓ relecture enseignant SVT (checklist §6)
relu_humain + valide:false + scoring:corrige_a_consulter
        ↓ merge manuel
publie + valide:true + scoring:corrige_a_consulter
        ↓ seulement si L2 reformulee ≥ 6/8 ET F2 patché
publie + scoring:note_auto     ← aujourd'hui INTERDIT
```

`valide: true` **n'autorise pas** la note auto. Deux flags distincts.

---

## 6. Checklist relecture humaine (une page / sujet)

- [ ] Pastille AR visible avant l'énoncé
- [ ] 6 figures ouvrables, ≠ 132 o, légendes ≠ réponses
- [ ] Barème somme = 20
- [ ] Polarités anti-F3 cochées (O₂/eau, S/liquide, 38 ATP seulement S1, etc.)
- [ ] Aucune date de session, aucun « officiel », aucun 2026
- [ ] Routes : **pas** `/exercices/[chapitre]` factice
- [ ] `evaluate_l2` / Savoir **non appelés**
- [ ] Texte modèle **absent** du payload élève

---

## 7. Exemple d'enveloppe JSON (S3, tronqué)

```json
{
  "id": "S3-D2-PHOTO-RECONST-001",
  "authenticite": "reconstitue",
  "valide": false,
  "statut": "brouillon",
  "scoring": "corrige_a_consulter",
  "domaines": ["D2"],
  "unites": ["D2-U1"],
  "alerte_f2": true,
  "interdits_redaction": ["38 ATP", "respiration_developpee"],
  "anti_f3": [
    { "concept": "origine_O2", "juste": "H2O", "faux": "CO2", "zero": true }
  ],
  "documents": [
    {
      "id": "S3-D4",
      "kind": "svg",
      "path": "public/figures/bac/s3/s3_d4_chaine.svg",
      "bytes_min": 500,
      "interdit_sur_dessin": ["P680", "P700", "Calvin", "38 ATP"]
    }
  ]
}
```

`sha256` se calcule **après** le binaire réel, pas maintenant.

---

## 8. Ce que ce pack ne fait pas

- Pas de routes Next, pas de `page.tsx`.
- Pas de PDF officiels (toujours LFS).
- Pas de purge des 89 OCR (à faire **avant** ou **en même temps** que la pub S1–S4).
- Pas de patch F2.
- **13/20 inchangé.**

---

## 9. Ordre d'exécution recommandé (produit)

1. CI anti-LFS sur `public/pdfs/**` **et** `public/figures/bac/**` **et** ONNX.
2. `valide: false` par défaut sur toute ingestion (89 OCR compris).
3. Produire les 24 SVG (ou 4 sujets × figures réellement dessinées).
4. Mapper ce contrat → **vrai** `SujetBac` (**C**).
5. Publier en `corrige_a_consulter`.
6. **D** (F2) avant toute `note_auto`.

---

## Livrables à date

| Pièce | Statut |
|---|---|
| Audit site v3 (N = 19 = 6/4/2/4/3) | livrable |
| Correcteur v1.1 (L2 ≈ 4,6/10) | livrable |
| S1 · S2 · S3 · S4 | livrables rédaction |
| **Contrat d'intégration E** | **livrable** |

**Stop métier contenu.** Suite utile uniquement si tu colles quelque chose :

- **C** + extraits `SujetBac` / un sujet D1 → mapping réel
- **D** + `fallback_v2.py` → patch F2
- **Stop** → envoyer au propriétaire : v3 + v1.1 + S1–S4 + ce contrat

Rien d'autre à rédiger côté Bac tant que ce n'est pas dans le produit.
