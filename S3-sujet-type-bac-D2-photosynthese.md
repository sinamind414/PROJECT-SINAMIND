# S3 — Sujet type Bac, Domaine 2-U1 · Photosynthèse — phases photochimique et chimiochimique

> **Étiquette :** *entraînement reconstitué* — **ce n'est PAS une épreuve officielle publiée**, et **pas un sujet « 2026 »**. Produit pour le 2ᵉ sujet D2 de l'épreuve (objectif v3 « ≥ 2 par domaine »), **sans recycler le bilan 38 ATP** (déjà S1).
>
> **Règle de mise en ligne (décision v1.1 du correcteur) :** **ne pas brancher de score automatique (L2) tant que `reformulee ≥ 6/8` n'est pas tenu** (F2 non patché). ⇒ **Mode « corrigé à consulter »** : barème et corrigé affichés, **pas de note chiffrée**.
>
> **Ancrage programme :** `programme_svt_3as_canonical.json` → **D2-U1 Photosynthèse** : chloroplaste, phase photochimique (chemiephotochimique), phase chimiochimique / Calvin–Rubisco, **origine de l'O₂**.
>
> **Calage 2025 (rétroactif, voir `ANALYSE-bac-svt-2025-officiel.md`) :** ce sujet est un **socle classique** (Hill, spectres, O₂/eau, Calvin). L'officiel 2025 S1-Ex. 2 pousse plus loin — **mécanisme de concentration du carbone (CCM) / pyrénoïde** : HCO₃⁻ → CO₂ par CA, membrane **imperméable au CO₂**, accumulation autour de Rubisco, mutant sans pyrénoïde. **S3 ne couvre pas ce niveau** : un élève dressé sur S3 comprend le cours mais pas entièrement 2025. Le trou fin = **un S5-type 2025 (CCM / pyrénoïde)**, pas une refonte de S3.
>
> **Hors sujet volontaire :** bilan **38 ATP** de la respiration (déjà S1). Ici, ATP/NADPH **thylakoïdiens** servent de *carburant* du Calvin, pas un second bilan mitochondrial.

---

## 0. Fiche sujet

| Champ | Valeur |
|---|---|
| Code | `S3-D2-PHOTO-RECONST-001` |
| Pastille | **Entraînement reconstitué** — ni épreuve officielle, ni sujet 2026 |
| Filière | 3AS Sciences Expérimentales |
| Unité | **D2-U1 Photosynthèse** (chloroplaste, phase الكيميوضوئية, phase الكيميوحيوية / Calvin–Rubisco, origine de l'O₂) |
| Hors sujet volontaire | Bilan **38 ATP** (déjà S1) — ici ATP/NADPH thylakoïdiens comme *carburant* du Calvin |
| Durée indicative | 2 h · /20 · 2 exercices |
| Note auto | **Interdite** tant que `reformulee < 6/8` (L2). Corrigé à consulter |
| Langue d'épreuve | arabe |

**Piège Bac n°1 (jeu doré `photo_1`) :** « الأكسجين يأتي من CO₂ » = **0**. Origine programme : **التحلل الضوئي للماء**.

---

## Page de garde élève (arabe)

```
تدريب على نمط البكالوريا — علوم الطبيعة والحياة
شعبة العلوم التجريبية — السنة الثالثة ثانوي

المجال 2 : التحولات الطاقوية — الوحدة 1 : التركيب الضوئي
الموضوع : الصانعة الخضراء · المرحلة الكيميوضوئية · حلقة كالفن / روبيسكو

⚠ تدريب مُعاد بناؤه لأغراض التعلّم.
ليس موضوعاً رسمياً، وليس موضوع دورة 2026.

المدة الإرشادية : ساعتان
العلامة : 20 / 20
يُنجَز التمرينان.

يُسلَّم التصحيح للمعاينة. لا تُحتسب علامة آلية.
```

---

## Énoncé (arabe)

### التمرين الأول (10 نقاط) — استغلال وثائق
**مصدر O₂ والآلية الكيميوضوئية**

**الوثيقة 1 — مقطع فوق-بنيوي لصانعة خضراء**
*(spécification : chloroplaste ovale ; double membrane ; **grana** = piles de thylakoïdes ; thylakoïdes inter-grana ; **stroma** avec quelques grains d'amidon. Légender **uniquement** : غشاء خارجي، غشاء داخلي. **Interdit sur le dessin :** thylakoïde, stroma, grana, emplacement de formation ATP/NADPH/O₂.)*

**الوثيقة 2 — جدول تجربة هيل (مبسّط)**
معلق كلوروبلاستات + مستقبل اصطناعي للإلكترونات (أكسيدان أ) في الضوء / الظلام.

| الوسط | ضوء | أكسيدان أ | انطلاق O₂ | اختزال أ |
|---|:---:|:---:|:---:|:---:|
| 1 | + | + | نعم | نعم |
| 2 | − | + | لا | لا |
| 3 | + | − | لا | — |
| 4 | كلوروبلاستات مغليّة + ضوء + أ | + | لا | لا |

**الوثيقة 3 — طيف امتصاص اليخضور / طيف عمل التركيب الضوئي**
*(spécification : X = λ 400–700 nm ; Y = intensité relative 0–100. Courbe 1 (absorption) : pics **bleu ~430** et **rouge ~680**, creux vert. Courbe 2 (action : dégagement O₂) : **même allure**, légèrement décalée. **Interdit :** écrire « chlorophylles a/b » ou « l'O₂ vient de… ».)*

**الوثيقة 4 — مخطط السلسلة الكيميوضوئية (non légendé)**
*(spécification, gauche → droite, membrane thylakoïde vue en coupe :*
- *PSII (P680) côté lumen ; flèche H₂O → ½ O₂ + 2 H⁺ + 2 e⁻ **sans** écrire « photolyse »*
- *e⁻ vers chaîne (PQ, cyt b₆f, PC)*
- *PSI (P700)*
- *NADP⁺ → NADPH côté **stroma***
- *ATP synthase, H⁺ lumen → stroma, ATP côté stroma*
***Interdit :** P680, P700, Rubisco, Calvin, « 38 ATP ».)*

**التعليمة**

1. **عرّف** الوثيقة 1 ثم **عيّن** (برقم أو وصف) المقصورتين اللتين يحدث فيهما التفاعل الكيميوضوئي والتفاعل الكيميوحيوي. (01,5)
2. **حلّل** الوثيقة 2 ثم **استنتج** الشرطين الضروريين لانطلاق O₂. (02)
3. **أظهر**، باستغلال الوثيقتين 3 و 4، أن اليخضور هو المُلتقِط وأن **مصدر الأكسجين هو الماء وليس CO₂**. (03)
4. **أنجز نصاً علمياً** (8–12 سطراً) تشرح فيه المرحلة الكيميوضوئية : موقعها، نواتجها الثلاثة، ودور تدرج H⁺ — **دون** ذكر حلقة كالفن. (03,5)

---

### التمرين الثاني (10 نقاط) — استدلال
**حلقة كالفن وربط المرحلتين**

**الوثيقة 5 — حلقة كالفن (مخطط صامت)**
*(spécification, cycle :*
- *entrée **CO₂***
- *sucres en C₅ (RuBP) → C₃ (APG) → C₃ réduit (PCAL) → régénération C₅*
- *flèches **ATP → ADP** et **NADPH → NADP⁺** sur la réduction, **sans** les placer sur la carboxylation seule*
- *une enzyme au carrefour CO₂ + C₅ : case vide*
***Interdit :** Rubisco, « المرحلة المظلمة », glucose écrit comme produit *direct* unique, 38 ATP.)*

**الوثيقة 6 — جدول كمّيات (نسبية) حسب الإضاءة**

| الشرط | NADPH في الستروما | ATP في الستروما | APG | سكر ثلاثي (PCAL) | نشا |
|---|:---:|:---:|:---:|:---:|:---:|
| ضوء مستمر + CO₂ | مرتفع | مرتفع | متوسط | مرتفع | + |
| ضوء ثم ظلام مفاجئ (ثوان) | ينهار | ينهار | يرتفع لحظياً | ينخفض | ثابت قصيرًا |
| ضوء + غياب CO₂ | مرتفع | مرتفع | منخفض | منخفض | − |

**التعليمة**

1. **حدّد** التفاعل الذي تحدثه الخانة الفارغة في الوثيقة 5، **سمّ** الإنزيم (روبيسكو) و**علّل** أهميته. (02)
2. **فسّر** سطر « ضوء ثم ظلام مفاجئ » في الوثيقة 6 (ارتفاع APG / انخفاض PCAL). (02,5)
3. **أظهر** أن المرحلة الكيميوحيوية **تعتمد** على نواتج المرحلة الكيميوضوئية دون أن تحتاج إلى الضوء *مباشرة*. (02,5)
4. **أنجز فقرة** (6–8 أسطر) تربط المرحلتين في الصانعة الخضراء، وتُبيّن مصير O₂ وNADPH وATP وCO₂. **يُمنع** ذكر التنفس الخلوي أو « 38 ATP ». (03)

---

## Specs figures

| ID | Fichier | Type | Doit montrer | Interdit sur le dessin |
|---|---|---|---|---|
| D1 | `s3_d1_chloroplaste.svg` | coupe | double membrane, grana, stroma | noms thylakoïde/stroma/ATP |
| D2 | `s3_d2_hill.csv` | tableau | 4 milieux de Hill | la conclusion « O₂ du H₂O » |
| D3 | `s3_d3_spectres.svg` | 2 courbes | pics bleu+rouge, creux vert, action ≈ absorption | « chlorophylles » écrit |
| D4 | `s3_d4_chaine.svg` | schéma membrane | PSII→PSI, H₂O, NADP⁺, ATP synthase, polarité H⁺ | P680/P700/Calvin/38 ATP |
| D5 | `s3_d5_calvin.svg` | cycle muet | CO₂, C₅, C₃, ATP, NADPH, case enzyme vide | Rubisco, « phase sombre », glucose-seul |
| D6 | `s3_d6_pool.csv` | tableau | lumière / coupure / −CO₂ | interprétation rédigée |

Format : SVG 1200×800, texte arabe RTL, fond blanc, lisible N&B (Bac papier). Poids cible &lt; 80 Ko / fichier. **Pas de pointeur LFS.**

---

## Corrigé + barème (équipe)

### Exercice 1 /10

**1. (01,5)**
- 0,5 définition : مقطع فوق-بنيوي لصانعة خضراء (عضية التركيب الضوئي).
- 0,5 كيميوضوئية : **غشاء الثايلاكويد / الغرانا**.
- 0,5 كيميوحيوية : **الستروما**.
*0 si* « الكل في الستروما » ou « الميتوكندري ».

**2. (02)**
- 0,5 milieu 1 vs 2 : **la lumière est nécessaire**.
- 0,5 milieu 1 vs 3 : **un accepteur d'électrons** (ou chaîne oxydante) nécessaire.
- 0,5 milieu 4 : la **structure / les enzymes du chloroplaste** doivent être intactes (l'ébullition arrête).
- 0,5 conclusion : dégagement d'O₂ lié à une **oxydation photique** dans le chloroplaste fonctionnel, pas à la simple présence d'un pigment.

**3. (03)** — **cœur anti-`photo_1`**
- 1,0 doc. 3 : le spectre d'action **coïncide** avec l'absorption de la chlorophylle ⇒ la chlorophylle capte les photons efficaces.
- 1,0 doc. 2 + 4 : l'O₂ se dégage à la lumière avec une chaîne d'électrons **en l'absence de CO₂** (expérience de Hill) ⇒ CO₂ n'est **pas** la source de l'O₂.
- 1,0 doc. 4 : H₂O → ½ O₂ + 2 H⁺ + 2 e⁻ (**photolyse de l'eau** au PSII).
*Zéro sur cet item si* « l'oxygène vient de CO₂ », même avec un vocabulaire riche (F3).

**4. Texte scientifique (03,5)**

| Critère | pts | Attendus |
|---|---:|---|
| Lieu | 0,5 | غشاء الثايلاكويد |
| Photolyse + e⁻ | 1,0 | الماء = مصدر e⁻ و O₂ |
| NADPH + ATP + lieu | 1,0 | NADPH و ATP نحو الستروما ؛ تدرج H⁺ / ATP synthase |
| Pas de Calvin / pas de 38 | 0,5 | hors sujet = −0,5 à −1 selon gravité |
| Forme Bac | 0,5 | ربط، دون نسخ الجدول |

**Texte modèle (~10 lignes) — pour le corrigé, pas pour le lexique Savoir.**

> تحدث المرحلة الكيميوضوئية على أغشية الثايلاكويد. يلتقط اليخضور الفوتونات (تطابق طيفي الوثيقة 3). يتأكسد الماء عند النظام الضوئي الثاني فينطلق O₂ وتتوافر إلكترونات وبروتونات. تنتقل الإلكترونات عبر سلسلة غشائية إلى NADP⁺ الذي يُختزل إلى NADPH في جهة الستروما. في الوقت نفسه تُضخّ H⁺ نحو تجويف الثايلاكويد فيتكون تدرج كيميائي-كهربائي تُستغله ATP-سينثاز لتشكيل ATP. النواتج الثلاثة المتاحة للمرحلة التالية هي : O₂ و ATP و NADPH. مصدر الأكسجين هو الماء وليس CO₂.

---

### Exercice 2 /10

**1. (02)**
- 0,5 : **carboxylation** du CO₂ sur le RuBP (C₅) → composés C₃ (APG).
- 0,75 : l'enzyme **روبيسكو (Rubisco)**.
- 0,75 : entrée du carbone minéral dans la matière organique / réaction limitante de la boucle.

**2. (02,5)**
- 1,0 : coupure de la lumière ⇒ arrêt de la production d'**ATP et NADPH** (phase photochimique stoppée).
- 1,0 : la réduction APG → PCAL s'arrête ⇒ **APG s'accumule**, **PCAL chute**.
- 0,5 : l'amidon ne bouge pas en quelques secondes (réserve).
*Piège :* « le noir active Calvin » = confusion « phase sombre ». **0 sur l'item** si l'élève écrit que la boucle de Calvin *exige* l'obscurité.

**3. (02,5)**
- 1,0 : Calvin, dans le **stroma**, consomme l'**ATP + NADPH** venus du thylakoïde.
- 0,75 : la lumière n'est **pas** requise *directement* sur Rubisco, mais sa coupure vide le carburant (doc. 6).
- 0,75 : l'absence de CO₂ arrête la boucle malgré la disponibilité en NADPH/ATP ⇒ les deux phases sont couplées mais chacune a son facteur limitant.

**4. Paragraphe (03)** — **interdiction respiration / 38 ATP**

| Critère | pts |
|---|---:|
| O₂ من الماء، يُطرح (أو يُستعمل لاحقاً — sans développer la mito) | 0,75 |
| ATP + NADPH → ستروما → اختزال APG / كالفن | 0,75 |
| CO₂ → مادة عضوية (سكر ثلاثي / نشا) عبر روبيسكو | 0,75 |
| Couplage des deux phases, lexique programme | 0,5 |
| Forme ; **−1 si 38 ATP ou respiration développée** | 0,25 |

**Texte modèle**

> في الصانعة الخضراء تُحوَّل الطاقة الضوئية على الثايلاكويد إلى ATP و NADPH مع انطلاق O₂ من الماء. في الستروما يثبّت روبيسكو CO₂ على RuBP فتتكون مركبات ثلاثية تُختزل بفضل ATP و NADPH إلى سكاكر تُؤدّي إلى النشا. لا تعمل حلقة كالفن في الظلام لأنها « مرحلة مظلمة » بل لأنها **مستقلة عن الفوتون مباشرة** وتابعة لنواتج المرحلة الكيميوضوئية. إذا انقطع الضوء توقف الوقود فتوقف الاختزال.

---

## Grille anti-F3 (sens, pas lexique)

| Concept | Polarité juste (programme) | Polarité fausse → 0 |
|---|---|---|
| Origine O₂ | **ماء** (تحلل ضوئي / هيل) | **CO₂** |
| Lieu photochimique | غشاء ثايلاكويد | ستروما / ميتوكندري |
| Lieu Calvin | ستروما | ثايلاكويد |
| Rubisco | كربكسلة CO₂ + RuBP | « تصنع ATP » / « تشق الماء » |
| « Phase sombre » | indép. *directe* de la lumière, dépend ATP/NADPH | « تحتاج الظلام » / « تتوقف في الضوء » |
| ATP ici | فسفرة ضوئية، وقود كالفن | **38 ATP** / bilan de Krebs |
| NADPH | مختزِل كالفن، جهة الستروما | « يُطرح كـ O₂ » |

**Alerte F2.** Les réponses/corrigés contiennent `ليس من CO₂`, `لا تحتاج إلى الضوء مباشرة`, `دون ذكر`. **Ne pas** appeler `evaluate_l2` : même bug que `photo_1` / `enz_1`.

---

## Recoupement audits v3 + correcteur v1.1

| Trou v3 | Après S1–S3 |
|---|---|
| Exos / sujets D2 épreuve | 0 → **S1 respiration + S3 photosynthèse** = **objectif « ≥ 2 D2 » tenu** (rédaction) |
| D2-U3 bilan ultrastructural | **volontairement non** (évite un 3ᵉ sujet ATP). Reste un *drill* QCM, pas une épreuve |
| D3 épreuve | **S2 × 1 / objectif 2** — il manque un 2ᵉ D3 |
| 13/20 plateforme | **inchangé** (fichiers hors site, L2 non branché, PDF/ONNX LFS intacts) |
| Note élève | toujours **corrigé à consulter** |

---

## Livrables à date

| Fichier | Statut |
|---|---|
| Audit site v3 (N = 19 = 6/4/2/4/3) | livrable |
| `audit-correcteur` v1.1 | L2 vécu ≈ 4,6/10 ; 5,1 mixte non déployé |
| S1 D2 respiration | livrable |
| S2 D3 tectonique | livrable |
| **S3 D2 photosynthèse** | **livrable** |

---

## Suite — un seul track à la fois

| Option | Quand | Pourquoi |
|---|---|---|
| **F. S5-type 2025 (photosynthèse CCM / pyrénoïde)** | non prioritaire contenu | seul manque réel face à 2025 S1-Ex.2 (voir analyse officielle) — **recadrer au gabarit 5+7+8** |
| **C. Intégrer S1–S4 dans les JSON** | avec le typage `SujetBac` + figures binaires | sinon documents vides (risque pointé) |
| **D. Patch F2** | avec `concept_present_without_negation` | 2 h dev ; **bloque** toute note élève |

**Reste réellement (ordre) :** 1. **S4 D3** pour tenir « ≥ 2 D3 » → 2. **C** (intégration JSON, avec le type `SujetBac`) → 3. **D** (patch F2).

**Suite proposée : B = S4 D3.** Même gabarit. Je le rédige dès confirmation — ou envoie le typage pour **C**.
