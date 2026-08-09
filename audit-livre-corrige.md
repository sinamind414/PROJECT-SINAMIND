# Audit — « الكتاب_المصحح_v1.0 (1).md » (Livre SVT 3AS corrigé)

> **⚠️ MIS À JOUR (2026-08-06) — Corrections appliquées dans la foulée :**
> voir §10 « Corrections appliquées » en fin de rapport. C1, C2, C3, le renommage
> et la correction du mojibake de `fallback_programme_data.py` + 14 fichiers de
> l'app sont **faits** ; la normalisation H1/H2/H3 (S1) reste à faire avant
> ingestion RAG.

**Date :** 2026-08-06 — **Fichier :** `الكتاب_المصحح_v1.0 (1).md` (racine du dépôt)
**Méthode :** lecture intégrale structurée + vérifications automatiques (encodage, hiérarchie Markdown, tables, doublons, artefacts) + spot-checks scientifiques + croisement avec les données du programme officiel encodées dans l'app (`fallback_programme_data.py`) et les sources ONEC en ligne.

---

# 1. Identité du document

| Attribut | Valeur |
|---|---|
| Contenu | **كتاب علوم الطبيعة والحياة — النسخة المصحّحة** (SVT), 3ème année secondaire, **شعبة العلوم التجريبية** (Bac Sciences Expérimentales), Algérie |
| Nature | Reconstruction « corrigée » d'un transcript OCR/DeepSeek du **manuel officiel**, relue contre le **PDF officiel scanné** (vérifications visuelles de pages citées) |
| Taille | 2 586 lignes, ~280 Ko (163 274 caractères), UTF-8 valide |
| Historique | ajouté par le commit `5fb3fce` « Add files via upload » (2026-08-06) |
| Structure | 3 domaines, **11 unités**, ~60 activités, 414 titres, 226 lignes de tableaux |
| Intégration app | **aucune** — aucun script/route/service ne référence ce fichier |

**Couverture :** les 11 unités du programme officiel 3AS Sciences Expérimentales sont présentes :
- **Domaine 1 — التخصّص الحَياتي** (5 unités) : تركيب البروتين · العلاقة بين بنية ووظيفة البروتين · النشاط الإنزيمي · دور البروتينات في الدفاع عن الذات · دور البروتينات في الاتصال العصبي
- **Domaine 2 — التحوّلات الطاقوية** (3 unités) : آليات تحويل الطاقة الضوئية · آليات تحويل الطاقة الكيميائية الكامنة إلى ATP · تحويل الطاقة على المستوى ما فوق البنية الخلوية
- **Domaine 3 — التكتونية العامة** (3 unités) : النشاط التكتوني للصفائح · بنية الكرة الأرضية · النشاط التكتوني والبنيات الجيولوجية المرتبطة به

---

# 2. Verdict synthèse

| Axe | Note | Constat |
|---|---|---|
| Complétude (programme officiel) | 🟢 **11/11 unités**, toutes avec introduction, activités, réponses modèles, bilan, exercices corrigés | cohérent avec les pages du programme ONEC (unité 1 p. 10, etc.) |
| Exactitude scientifique (spot-checks) | 🟢 10/10 points vérifiés corrects | voir §4 |
| Qualité du texte | 🟠 2 corruptions réelles, quelques notations incohérentes | voir §5 |
| Conformité au programme officiel | 🟠 titre du domaine 1 **non officiel** | voir §5-C3 |
| Structure Markdown | 🟠 hiérarchie de titres plate (64 H1) | voir §6 |
| Rigueur du processus « correction » | 🟢 documenté (7 notes + 3 sections) | mais 1 unité sans vérification visuelle |
| Utilisation dans l'app | 🔴 **fichier dormant** — non ingéré | voir §7 |

**En une phrase :** un document de référence **excellent sur le fond** (complet, exact, bien documenté), avec des défauts de finition (2 corruptions, 1 nommage hors programme, hiérarchie Markdown plate) et — surtout — **aucune intégration dans l'application**, alors qu'il s'agit de la matière officielle la plus fidèle du dépôt.

---

# 3. Ce qui est bon (vérifié)

## 3.1 Complétude — 11/11 unités
Chaque unité contient le schéma complet : **بطاقة تقنية** (carte technique) → **تقديم الوحدة / الوضعية الانطلاقية** → **إشكالية** → activités (وثائق + استغلال + أجوبة نموذجية) → **حصيلة معرفية** → **تمارين تطبيقية محلولة**.

| Unité | lignes | mots | intro/إشكالية | حصيلة | exercices |
|---|---|---|---|---|---|
| U1 تركيب البروتين | 507 | 5 441 | 4 | 1 | ✓ |
| U2 بنية/و fonction | 239 | 2 623 | 4 | 1 | ✓ |
| U3 enzyme | 222 | 2 547 | 5 | 1 | ✓ |
| U4 immunité | 271 | 2 571 | 1 | 1 | ✓ |
| U5 neuro | 232 | 2 335 | 1 | 1 | ✓ |
| U6 photosynthèse | 183 | 1 712 | 1 | 2 | ✓ |
| U7 respiration | 196 | 1 929 | 2 | 3 | ✓ |
| U8 supra-cellulaire | 129 | 1 185 | 1 | 2 | ✓ |
| U9 tectonique-1 | 159 | 1 599 | 6 | 3 | ✓ |
| U10 tectonique-2 | 174 | 1 611 | 6 | 3 | ✓ |
| U11 tectonique-3 | 165 | 1 715 | 6 | 3 | ✓ |

## 3.2 Exactitude scientifique — 10/10 spot-checks passés
- **Potentiel de repos :** −70 mV ✓ ; **potentiel d'action :** +30/+40 mV ✓ ; **pompe Na⁺/K⁺** 3:2 avec consommation d'ATP ✓ (l. 1439-1461)
- **Bilan énergétique respiration :** glycolyse 2 ATP nets (+2 NADH) → Krebs 2 ATP → phosphorylation oxydative ≈34 ATP → **38 ATP/glucose** ✓ (l. 1842-1938)
- **Fermentation :** éthanol + CO₂ + 2 ATP / lactate + 2 ATP ✓
- **Photosynthèse :** 6CO₂ + 12H₂O → C₆H₁₂O₆ + 6H₂O + 6O₂ (équation officielle algérienne) ✓
- **Cycle de Krebs :** acétyl-CoA (2C) → 2 CO₂, 3 NADH, 1 FADH₂, 1 ATP(GTP) par tour ✓
- **Dorsales océaniques :** 75 000 km, +3 km²/an, ≈20 km³ de magma/an ✓ (valeurs officielles)
- **Code génétique :** AUG = initiateur + Met, UAA/UAG/UGA = stop, tableau des codons présent ✓
- **Ondes sismiques :** P 6-13 km/s, S ne se propagent pas dans les liquides ✓

## 3.3 Processus de correction documenté (crédibilité)
- 7 unités portent la note `📝 ملاحظات تصحيح هذا الفصل مقارنة بنسخة DeepSeek المرفوعة` + `موارد التصحيح: تفريغ الكتاب + مستند البرنامج الوطني + المسح المرئي`.
- 8 unités citent les **pages du PDF officiel vérifiées visuellement** (39-46, 57, 61, 73-74, 128, 175, 206, 228).
- 3 unités (tectonique) ont une section `🔍 ملاحظات التصحيح (مقارنة بنص التفريغ الآلي)` détaillant les corrections terme à terme (ex. « الأفيوليت » → « الأوفيوليت », « الشيست الأزرق » → « الشست الأزرق HP/BT »).

## 3.4 Hygiène Markdown — très propre
- **0** ligne de tableau cassée, **0** caractère de contrôle, **0** U+FFFD, **0** espace de fin de ligne, **0** placeholder/TODO.
- 1 318 paires `**` équilibrées ; 2 fences `` ``` `` équilibrées ; pas de doublons de paragraphes significatifs (11 doublons, tous des titres récurrents légitimes).

---

# 4. Corruptions et erreurs de contenu (à corriger)

## C1 — ligne 1439 : fragment illisible
> `الغشاء العصبي في حالة الراحة **مستقطب (km للاستقطاب)**: كمون الراحة = **-70 mV**…`

« **(km للاستقطاب)** » est du texte mort (probablement « **حالة الاستقطاب** »). Une seule occurrence — mais elle tombe sur une définition clé du Bac.

## C2 — ligne 1845 : lettre latine dans un mot arabe
> `…تنتج: 2CO₂ (هرب الكربونين عبر **dالة الحلقة**)…`

« **dالة الحلقة** » → probablement « **دورة الحلقة** » (cycle de Krebs). Même nature que C1 : résidu de saisie/OCR.

## C3 — le titre du domaine 1 n'est pas le nom officiel
Le livre intitule le domaine 1 « **التخصّص الحَياتي** », mais :
- le programme officiel (et les références ONEC : ency-education, education-onec-dz) le nomme « **التخصص الوظيفي للبروتينات** » (La spécialisation fonctionnelle des protéines) — vérifié en ligne [1](https://3as.ency-education.com/sciences-lessons1.html), [2](http://education-onec-dz.blogspot.com/2019/09/blog-post_953.html), [3](https://www.bac-feljib.com/2023/09/sciences-bac-2024-programme-3as.html) ;
- le fallback ONEC de l'app (`fallback_programme_data.py`) utilise aussi « التخصص الوظيفي للبروتينات ».

Cela contredit la revendication du TOC « *مطابق للبنية الرسمية* » et, si le livre est ingéré dans le RAG, créera une **incohérence de nommage** avec le reste de l'app (même domaine, deux noms → retrieval perturbé). Les noms des domaines 2 et 3 (« التحوّلات الطاقوية », « التكتونية générale ») sont, eux, conformes.

## C4 — U1 (تركيب البروتين) : seule unité sans vérification visuelle
Les unités U2-U8 citent les pages du PDF vérifiées (« تحقق مرئي ») ; U1 repose uniquement sur le transcript — alors que c'est l'unité la plus longue (507 lignes) et la plus chargée en Bac.

## C5 — notations incohérentes (mineures)
- « **ARNم** » (l. 283, 2×) vs « **ARNm** » partout ailleurs.
- « **متعدد U** » vs « متعدد الأدنين » (corrigé en C0 dans le texte, mais le TOC des corrections l. 609 dit « الأدنين »).
- Deux systèmes de numérotation des unités : chiffres romains I–V (TOC) vs « الوحدة الأولى/الثانية… » (corps), **renumérotés par domaine** → « الوحدة الأولى » existe 2 fois (domaine 1 et domaine 2).

---

# 5. Problèmes structurels Markdown

## S1 — Hiérarchie de titres plate : 64 H1
Le niveau H1 est utilisé pour tout : le domaine (répété **5×** pour le domaine 1, 3× pour le domaine 2), les unités du domaine 3, **et chaque « النشاط »**. Résultat : un parseur qui découpe par titres (cas typique d'une ingestion RAG) produira des chunks « activité » étiquetés au niveau domaine, et l'arbre sémantique du document est perdu.

**Recommandé :** H1 = domaine (1 seule fois), H2 = unité, H3 = activité, H4 = questions/réponses. (La cohérence H2/H3/H4 à l'intérieur des blocs est déjà bonne.)

## S2 — Conventions différentes entre domaines
- Domaines 1-2 : `# المجال …` + `## الوحدة X` + `# النشاط X`.
- Domaine 3 : `# الوحدة الأولى/الثانية/الثالثة ✅` + `# 🟦/🟥/🟩 أولاً/ثانياً…` (éléments 1-8).
- Le « ✅ » dans les titres (et `🟦🟥🟩`) est un **marqueur d'état**, pas un intitulé — il pollue l'indexation.

## S3 — Nom de fichier
`الكتاب_المصحح_v1.0 (1).md` : le suffixe « (1) » est un artefact de téléchargement dupliqué, et la hamza du nom (« المصحح ») diffère de celle du titre interne (« المصحّحة »). Renommage suggéré : `كتاب-SVT-3AS-المصحح-v1.0.md`.

---

# 6. Découverte connexe — mojibake dans le fallback programme de l'app

En croisant le livre avec la référence ONEC de l'app, j'ai constaté que **`khawarizmi-backend/fallback_programme_data.py` contient de l'arabe mal encodé** :

- 159 occurrences du motif mojibake « Ø§Ù„ » (= « ال » double-encodée) sur **69 titres `titre_ar`** ;
- le décodage inverse cp1252 → UTF-8 **restaure l'arabe correct** (vérifié : « ØªØ±ÙƒÙŠØ¨ Ø§Ù„Ø¨Ø±ÙˆØªÙŠÙ† » → « تركيب البروتين ») ; 1 titre a un caractère perdu (\x81) ;
- le fichier est servi tel quel par `routes/programme.py` (fallback) → **titres illisibles pour l'élève en mode fallback**.

C'est un bug app (hors périmètre « audit du livre ») — signalé ici car c'est la même source de vérité ONEC que le livre prétend refléter, et il documente la divergence C3.

---

# 7. Intégration dans l'application : aucune

- `grep` sur tout le backend : **0 référence** à ce fichier (ni ingestion, ni route, ni prompt).
- `LIVRE-MANHADJIYA.md` (autre livre : « منهجية علوم الطبيعة والحياة » — الأستاذة كتفي شريف زينة) est, lui, ingéré par `scripts/ingest_livre_manhadjiya.py`.
- **Opportunité :** ce livre est le contenu officiel le plus fidèle du dépôt — parfait pour le RAG (chunks par unité/activité), les QCM, et l'alignement avec le programme ONEC. À condition de corriger d'abord C1-C3 et S1.

---

# 8. Plan d'action priorisé

| # | Action | Effort | Impact | Statut |
|---|---|---|---|---|
| 1 | Corriger C1 (« km للاستقطاب ») et C2 (« dالة الحلقة ») | 2 min | texte propre | ✅ fait |
| 2 | Renommer le fichier (retirer « (1) », homogénéiser la hamza) | 1 min | hygiène | ✅ fait |
| 3 | Aligner le domaine 1 sur « التخصص الوظيفي للبروتينات » | 2 min | conformité programme | ✅ fait |
| 4 | Normaliser la hiérarchie H1/H2/H3 (S1) — préalable si ingestion RAG | 30-60 min | arbre exploitable | ⏳ à faire |
| 5 | Corriger le mojibake de `fallback_programme_data.py` + 14 fichiers app | 15 min | app : fallback lisible | ✅ fait |
| 6 | Écrire `scripts/ingest_livre_corrige.py` sur le modèle de `ingest_livre_manhadjiya.py` | 1-2 h | le livre sert enfin le produit | ⏳ à faire |
| 7 | Ajouter la vérification visuelle manquante de U1 (C4) | selon accès PDF | parité de confiance | ⏳ à faire |

---

# 9. Limites de l'audit


- La conformité page-à-page au manuel officiel n'a pas pu être re-vérifiée (le PDF officiel n'est pas dans le dépôt) ; les « تحقق مرئي » cités par le livre lui-même sont pris comme déclarations.
- Spot-checks scientifiques limités à ~10 points clés du programme ; pas de relecture ligne à ligne par un spécialiste SVT.
- La comparaison des pages du TOC (10, 39, 57…) avec le manuel officiel repose sur la cohérence interne + l'alignement avec le fallback ONEC de l'app, pas sur le PDF lui-même.

---

# 10. Corrections appliquées (session du 2026-08-06)

Suite à cet audit, les corrections suivantes ont été **appliquées et vérifiées** :

## Livre (renommé → `الكتاب_المصحح_v1.0.md`)
| # | Correction | Preuve |
|---|---|---|
| C1 | « مستقطب (km للاستقطاب) » → « مستقطب (في حالة استقطاب) » (l. 1439) | diff confirmé |
| C2 | « عبر dالة الحلقة » → « عبر دورة الحلقة » (l. 1845) | diff confirmé |
| C3 | « التخصّص الحَياتي » → « التخصص الوظيفي للبروتينات » (13 occurrences, dont TOC, en-têtes H1 et cartes techniques) | `grep -c` = 13 |
| Renommage | `الكتاب_المصحح_v1.0 (1).md` → `الكتاب_المصحح_v1.0.md` (retrait de l'artefact « (1) ») | `git mv` |
| Préservé | les journaux de correction du texte citent toujours les formes fautives d'origine (« الأفيوليت », « الشيست الأزرق ») — la correction s'applique au contenu, pas aux citations des erreurs corrigées | 2 occurrences volontaires |

## Mojibake de l'app (découverte §6) — **corrigé partout**
- `khawarizmi-backend/fallback_programme_data.py` : 69 titres `titre_ar` réparés (240 tokens en round-trip cp1252→UTF-8 + 14 titres mixtes reconstruits manuellement à partir des titres français). **Preuve :** `import fallback_programme_data` → `['التخصص الوظيفي للبروتينات', 'التحولات الطاقوية', 'التكتونية العامة']`.
- **14 fichiers frontend + backend** (SuggestionChips, VerbLessonFlow, mindmap, drill, leaderboard, ActiveLesson, SocialLivePanel, OnboardingOverlay, MethodPracticeGate, annales/read, VideosWidget, ProgrammeView, auth-context, mindmap_prompt_v2=FP) : **1 252 tokens** réparés au total (arabe corrompu + français « Ã© » + émojis tronqués « ðŸ… »).
- **Scan final : 0 marqueur mojibake résiduel** dans tout le repo (hors actifs modèle `tokenizer.json` et OCR bruts, exclus par nature).
- Outil conservé : `scripts/fix_mojibake.py` (round-trip latin-1/cp1252 + table cp1252 + gestion des octets 0x81/0x8F et du sélecteur de variation emoji U+FE0F).

## Terminologie scientifique alignée sur le livre (leçons + données du site)
| Terme (livre) | Avant | Fichiers corrigés | Nb |
|---|---|---|---|
| **الشست الأزرق** | الشيست الأزرق | `programme_national_svt_claude_opus.md`, `drills_svt_arabe_500_QCM…md`, `qcm_items.json`, `scientific_knowledge.py` | 39 |
| **الأوفيوليت** | الأفيوليت | `scientific_knowledge.py`, `methodology-chapters.ts`, `experimental-lessons-data.ts`, `experimental_lessons.json` | 7 |
| **الفنيل ألانين** | فينيل ألانين | `programme_national_svt_claude_opus.md`, `methodology-v2.ts` | 4 |
| Variante fautive ajoutée au correcteur | « الأفيوليت » → accepté comme équivalent d'« الأوفيوليت » | `services/savoir_corrector.py` | 1 |

## Vérifications après correction
- Backend : `pytest tests/` → **624 passed, 4 failed** (les 4 échecs sont **pré-existants** — dérive de mocks `pulse_service` et attente `llm_recovered`, non liés).
- Frontend : `vitest` → **592/592 passed** ; `eslint` → **1 erreur + 21 warnings** (identique à avant, aucune régression).
- JSON modifiés (`qcm_items.json`, `experimental_lessons.json`) : parse OK.

**Reste à faire (hors périmètre de cette session) :** S1 normalisation H1/H2/H3, C4 vérification visuelle de l'unité 1, et l'ingestion RAG du livre (§7).

# 11. Vague 2 — Alignement terminologique et structurel des leçons et données du site sur le livre

Suite à la demande « ma base de données, leçons et autres rubriques doit respecter le livre »,
toutes les **données actives** du site (cours, QCM, lexique, méthodologie, annales, prompts,
simulations, leçons expérimentales, planificateur) ont été alignées sur la terminologie du livre
`الكتاب_المصحح_v1.0.md` (termes standards extraits du livre lui-même et de ses journaux de correction).

## 11.1 Terminologie scientifique corrigée (22 fichiers, ~290 remplacements)

| Terme avant (site) | Terme selon le livre | Fichiers corrigés | Nb |
|---|---|---|---|
| أدينين (adénine) | **الأدنين** | lexique, programme_national, leçons expérimentales | 8 |
| الكودون / كودون / كودونات | **الرامزة / الرامزات** (+ « الرامزة المضادة ») | scientific_knowledge, lexique, regex fallback_v2 | 18 |
| الكلوروفيل | **اليخضور** | programme_national, lexique | 14 |
| الاندساس / اندساس | **الغوص / غوص** | methodology-documents, scientific_knowledge, methodology-chapters, lexique | 27 |
| البولي ريبوزوم | **متعدد الريبوزوم** | drills, qcm_items, programme_national | 39 |
| الجلوكوز | **الغلوكوز** | scientific_knowledge, simulations, 3 JSON, methodology-chapters | 28 |
| الميتوكوندري / الميتوكوندريا / الميتوكندرون | **الميتوكندري / الميتوكندريا** | 3 JSON, scientific_knowledge, lexique, programme_national, methodology-v2, free_chat_prompt, aujourdhui, simulations, leçons expérimentales | 125+ |
| الستار (manteau, lexique) | **البرنس** | lexique_svt_terminale_complet | 13 |
| الوشاح (manteau) | **البرنس** | scientific_knowledge, chapitres-traduction, methodology-documents, TectonicsSimulation, keyword units.py | 9 |
| accord « الرامزة البادئ/الختامي » | **البادئة / الختامية** | scientific_knowledge | 2 |

**Exclusions volontaires (documentées) :**
- `savoir_corrector.py` : dictionnaire de reconnaissance orthographique — les variantes
  (« الكودون », « الجلوكوز », « الوشاح »…) y restent pour **accepter** les écritures élèves,
  la forme du livre étant déjà la forme principale reconnue.
- `fallback_v2.py` : la regex accepte encore « كودون » (écriture élève), « رامزه » → « رامزة » corrigé.
- `experimental-lessons-data.ts` : « الستار (البرنس) » / « البرنس (الستار) » — formes d'équivalence
  identiques à l'usage du livre (« البرنس (الستار/المعطف) »), conservées.
- Archives OCR (`data/annales_workspace/`, `data/ocr_output/`) : données sources brutes, non servies
  par l'app (vérifié : aucune route ne les lit) — hors périmètre.

## 11.2 Structure alignée sur le livre

| Élément | Avant | Après (livre) |
|---|---|---|
| `services/units.py` u6 | التركيب الضوئي | **آليات تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة** |
| `services/units.py` u7 | التنفس الخلوي والتخمر | **آليات تحويل الطاقة الكيميائية الكامنة في الجزيئات العضوية إلى ATP** |
| `services/units.py` u8 | الحصيلة الطاقوية على المستوى الخلوي | **تحويل الطاقة على المستوى ما فوق البنية الخلوية** |
| `services/units.py` u11 | البنيات الجيولوجية المرتبطة بالنشاط التكتوني | **النشاط التكتوني والبنيات الجيولوجية المرتبطة به** |
| keywords u6-u11 | — | élargis aux termes du livre (المرحلة الكيموضوئية/الكيموحيوية, التحلل السكري, الفسفرة التأكسدية, الأوفيوليت, الموجات الزلزالية…) |
| `WeekSchedule.tsx` (unité 6) | « التركيب الضوئي » | « آليات تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة » |

**Preuve de non-régression :** `normalize_unit()` matche toujours les anciens libellés de QCM
(« التركيب الضوئي » → u6, « التنفس الخلوي والتخمر » → u7, « الحصيلة الطاقوية » → u8,
« البنيات الجيولوجية » → u11) et retourne désormais les noms officiels.

## 11.3 Vérifications

- Backend : `pytest` → **624 passed / 4 failed** (les 4 échecs sont pré-existants, non liés).
- Frontend : `vitest` → **592/592 passed** ; `eslint` → 1 erreur + 21 warnings (inchangé).
- JSON modifiés : tous valides (`json.load` OK sur les 6 gros fichiers de données).
- Scan final : 0 occurrence fautive résiduelle dans les données actives (hors exclusions ci-dessus).

**Reste (déjà signalé) :** S1 normalisation H1/H2/H3 du livre (préalable ingestion RAG) et
`scripts/ingest_livre_corrige.py`.


# 12. Vague 3 — Leçons et rubriques alignées sur le livre (structure + labels)

Vérification approfondie des **leçons** : le contenu pédagogique (23 leçons interactives
dans `experimental-lessons-data.ts`) était **déjà aligné sur le livre** — les 11 unités y sont
couvertes dans l'ordre du programme. En revanche, la **page liste** (`/lecons-sciences-experimentales`)
affichait des labels d'un ancien programme et un **mapping phases→unités décalé** (dès l'unité 2).
Corrections appliquées :

## 12.1 Page « التجارب المقررة » (`lecons-sciences-experimentales/page.tsx`)
- **Domaines** → noms officiels du livre : « المواد العضوية والبروتينات » → **التخصص الوظيفي للبروتينات**,
  « تحويل الطاقة » → **التحولات الطاقوية**, « الظواهر التكتونية » → **التكتونية العامة**.
- **Unités** → noms officiels : « العلاقة بين بنية البروتين ووظيفته » → **العلاقة بين بنية ووظيفة البروتين**,
  « آليات تحويل الطاقة الكيميائية الكامنة إلى ATP » → **…في الجزيئات العضوية إلى ATP**,
  « تحويل الطاقة على المستوى ما فوق البنيوي الخلوي » → **ما فوق البنية الخلوية**.
- **Labels des 22 phases** → renommés selon le contenu réel de chaque leçon et le vocabulaire du livre
  (ex. « التنظيم الهرموني · دور الهرمونات » → « النقل المشبكي: عبور السيالة العصبية »,
  « الهضم · النقل الدموي » → « المرحلة الكيميوحيوية: تثبيت CO₂ (حلقة كالفن) », etc.).
- **Mapping phases→unités corrigé** : le découpage `PHASES.slice(...)` était décalé d'une phase à
  partir de l'unité 2 (l'unité « الاتصال العصبي » pointait vers des leçons de respiration/muscle).
  Désormais : u1→2 leçons, u2→1, u3→1, u4→3, u5→3, u6→2, u7→2, u8→1, u9→3, u10→2, u11→2 (22 phases).
- **Stats** : « 44 تجربة مقررة » (chiffre de l'ancien programme) → « 23 تجربة تفاعلية · 11 وحدات دراسية · 3 مجالات ».

## 12.2 Catalogue des cours (`lib/cours-data.ts`)
- Domaines d2/d3 : « تحويل الطاقة » → **التحولات الطاقوية**, « ديناميكية الكرة الأرضية » → **التكتونية العامة**.
- **Bug `UNIT_SLUGS` corrigé** : les unités françaises des domaines 2 et 3 renvoyaient **u1/u2/u3**
  au lieu de **u6/u7/u8** et **u9/u10/u11** → les slugs d'unités des cours étaient faux.

## 12.3 Méthodologie (`lib/methodology-chapters.ts`) et simulations
- 18 chapitres de méthodologie du domaine 2 → « التحولات الطاقوية », 18 du domaine 3 → « التكتونية العامة »
  (le nom de l'unité 8 « تحويل الطاقة على المستوى ما فوق البنية الخلوية » reste intact — remplacement ciblé sur le champ domaine).
- Simulation photosynthesis : `chapter: "تحويل الطاقة"` → « التحولات الطاقوية ».

## 12.4 Vérifications
- `tsc --noEmit` : **aucune erreur dans les 4 fichiers modifiés** (8 erreurs pré-existantes dans les pages
  des routes mortes `/aujourdhui`, `/dix-minutes`, `/fiche-j1`, `/progress` — déjà documentées §P0-2 de l'audit global).
- `vitest` : **592/592 passed** ; `eslint` : 1 erreur + 21 warnings (inchangé).
- Scan : plus aucun ancien label de domaine (« المواد العضوية والبروتينات », « الظواهر التكتونية »,
  « ديناميكية الكرة الأرضية », « ما فوق البنيوي ») dans le frontend.

**Couverture finale livre ↔ site :** unités (units.py), chapitres (chapitres-traduction.ts, fallback),
leçons interactives (23), cours (cours-data.ts), méthodologie (methodology-chapters.ts), planificateur
(WeekSchedule), simulations — tous alignés sur les 11 unités et la terminologie de `الكتاب_المصحح_v1.0.md`.
