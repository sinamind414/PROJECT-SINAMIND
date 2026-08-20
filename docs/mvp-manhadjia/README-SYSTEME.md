# Système Manhadjia — Documentation de livraison

> Dernière mise à jour : 2026-08-20 · Branche : `arena/01a01f52-project-sinamind`
> Série de commits : `836556e` → `9779af1`

## 1. Doctrine (invariants de conception)

| Règle | Valeur |
|---|---|
| Appels API | **0** — toutes les données sont dans les JSON frontend |
| LLM | **0** — détection locale par regex listes fermées |
| Note /20 | **0** — jamais de score officiel affiché à l'élève |
| Verbes | 1 verbe = 1 atelier, rituel → carte → atelier (phases أ/ب/ج) |
| Couleurs | 7 couleurs réservées au bootcamp ; satellites = **فضي** unifié |
| Erreur | jamais « فشل » — toujours « مهنة غالطة » + voix إيجابية |

## 2. Routes (23)

### Bootcamp J1→J7 (7 jours, 7 couleurs)

| Route | Jour | Verbe | Couleur | verb_ref |
|---|---|---|---|---|
| `/manhadjia` | 1 | حلّل | أصفر (jaune) | — |
| `/manhadjia/fassir` | 2 | فسّر | برتقالي (orange) | 7 |
| `/manhadjia/istintaj` | 3 | استنتج | أخضر (vert) | 6 |
| `/manhadjia/allil` | 4 | علّل | أزرق (bleu) | 5 |
| `/manhadjia/quarin` | 5 | قارن | بنفسجي (violet) | — |
| `/manhadjia/nas-ilmi` | 6 | نص علمي | وردي (rose) | 1 |
| `/manhadjia/moukhattat` | 7 | مخطط | سماوي (cyan) | 10 |

Chaîne `lien_suivant` bouclée : J1→J2→…→J7→J1.

### Hub + Satellites (15 أقمار صناعية)

| Route | قمر | Verbe | verb_ref | Doc |
|---|---|---|---|---|
| `/manhadjia/atwal` | — | **Hub des 15 satellites** | — | — |
| `/manhadjia/saf` | 1 | صف | 2 | greffe LTc |
| `/manhadjia/arif` | 2 | عرّف | 3 | greffe LTc |
| `/manhadjia/atbat` | 3 | أثبت | 4 | greffe LTc + exemple diwan |
| `/manhadjia/fardiya` | 4 | اقترح فرضية | 8 | greffe LTc |
| `/manhadjia/naqich` | 5 | ناقش | 9 | greffe LTc |
| `/manhadjia/synapse` | 6 | استنتج — وثيقة المشبك | 6 | **مشبك (5 تجارب + رسم)** + exemple |
| `/manhadjia/taaraf` | 7 | تعرّف / سمّ | من الكتاب §1 | مشبك |
| `/manhadjia/oudkur` | 8 | اذكر | §4 | greffe LTc |
| `/manhadjia/addid` | 9 | عدّد | §5 | greffe LTc |
| `/manhadjia/sannif` | 10 | صنّف | §6 | greffe LTc |
| `/manhadjia/mayyiz` | 11 | ميّز | §7 | greffe LTc |
| `/manhadjia/istakhrij` | 12 | استخرج | §19 | مشبك + exemple |
| `/manhadjia/alliq` | 13 | علّق | §18 | greffe LTc |
| `/manhadjia/anqid` | 14 | انقد | §21 | greffe LTc |
| `/manhadjia/mochkil` | 15 | صياغة مشكل علمي | §22 | greffe LTc |

Chaîne satellites bouclée : 1→2→…→15→bootcamp J1.

## 3. Données — `khawarizmi-frontend/data/ateliers/` (22 JSON)

- `manhadjia_0X_*_taam.json` (7) : bootcamp. Ne **jamais** toucher sans demande explicite.
- `manhadjia_s01..s15_*_taam.json` (15) : satellites. Schéma `AtelierSatelliteData` :
  - `detection.obligatoires[]` / `interdits[]` : regex testées sur texte normalisé (أ→ا, diacritiques ôtés). **Pièges connus** : écrire les patterns en forme normalisée (أما→اما, خطأ→خطا), protéger لان imbriqué `(^|[\s،.؛:])لان(?=[\s،.؛:]|$)`, جين `راجع` dans les variantes de يرجع.
  - `docs` : `tableau` obligatoire ; `courbe`+`phrase_sous_graphe` (greffe LTc) **ou** `schema` (مشبك).
  - `unites[]` / `exemples[]` : données officielles injectées statiquement.
  - `verb_ref` : jamais de `max_score` (doctrine).

## 4. Scripts de régénération

| Script | Rôle | Idempotent |
|---|---|---|
| `khawarizmi-frontend/scripts/wire-verb-refs.mjs` | injecte `verb_ref` officiels (1·2·3·4·5·6·7·8·9·10) | ⚠️ reformate les JSON bootcamp → reverter le diff cosmétique après exécution |
| `khawarizmi-backend/scripts/wire_satellite_official_data.py` | injecte `unites` (VERB_UNIT_MAP + ALL_UNITS) et `exemples` (PRACTICAL_EXAMPLES) dans les 15 satellites | ✅ vérifié (0 diff à la 2e exécution) |

## 5. Navigation

```
Bandeau bootcamp (7 pastilles colorées, jour actif)
   └─ lien « أقمار صناعية (15) » → /manhadjia/atwal (15 cartes)
SatelliteHeader : → البوتكامب · كل الأقمار (15) · القمر الجاي ←
Phase ج (miroir) : lien_suivant = قمر N+1 (boucle → bootcamp)
```

## 6. Tests

- `khawarizmi-frontend/src/lib/manhadjia-lib.test.ts` : **142 tests** — registres
  (7+15), cohérence JSON↔registre, accepteurs rituel fermés, détection
  modèle/pièges par verbe, chaînes bouclées, données officielles,
  scope-fence bootcamp, invariant de couverture verb_ref 1→10.
- Suite complète frontend : **787 tests verts** (`npx vitest run`).
- Environnement vitest = `node` (pas de jsdom/RTL — les composants ne sont
  pas testés en rendu ; la vérification se fait sur le HTML servi + build).

## 7. Vérification livrée

- `npm run build` : OK — 23 routes manhadjia prerendered.
- Serveur (`npm start`) : **23/23 routes HTTP 200**, bandeau/header/hub
  vérifiés dans le HTML servi (aria-current du jour actif, badges verb_ref,
  « من الكتاب », 15 cartes hub).

## 8. Reste possible (non fait — à valider)

- Branchement **runtime** des APIs `/api/manhadjiya/*` (casserait la doctrine 0 API).
- Rendu tests (jsdom + @testing-library/react) : changement d'infra test.
- Capture d'écran automatisée : navigateur headless indisponible dans le sandbox.
