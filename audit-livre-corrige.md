# Audit — « الكتاب_المصحح_v1.0 (1).md » (Livre SVT 3AS corrigé)

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

| # | Action | Effort | Impact |
|---|---|---|---|
| 1 | Corriger C1 (« km للاستقطاب ») et C2 (« dالة الحلقة ») | 2 min | texte propre |
| 2 | Renommer le fichier (retirer « (1) », homogénéiser la hamza) | 1 min | hygiène |
| 3 | Aligner le domaine 1 sur « التخصص الوظيفي للبروتينات » (ou documenter le choix) | 2 min | conformité programme |
| 4 | Normaliser la hiérarchie H1/H2/H3 (S1) — préalable si ingestion RAG | 30-60 min | arbre exploitable |
| 5 | Corriger le mojibake de `fallback_programme_data.py` (cp1252→UTF-8) | 15 min | app : fallback lisible |
| 6 | Écrire `scripts/ingest_livre_corrige.py` sur le modèle de `ingest_livre_manhadjiya.py` | 1-2 h | le livre sert enfin le produit |
| 7 | Ajouter la vérification visuelle manquante de U1 (C4) | selon accès PDF | parité de confiance |

---

# 9. Limites de l'audit

- La conformité page-à-page au manuel officiel n'a pas pu être re-vérifiée (le PDF officiel n'est pas dans le dépôt) ; les « تحقق مرئي » cités par le livre lui-même sont pris comme déclarations.
- Spot-checks scientifiques limités à ~10 points clés du programme ; pas de relecture ligne à ligne par un spécialiste SVT.
- La comparaison des pages du TOC (10, 39, 57…) avec le manuel officiel repose sur la cohérence interne + l'alignement avec le fallback ONEC de l'app, pas sur le PDF lui-même.
