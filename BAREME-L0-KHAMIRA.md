# Barème L0 — حلّل منحنى الخميرة (comme le livre)

**Question :** `manhadjiya-yeast-analyse`  
**Verbe :** حلّل (pas فسّر)  
**Source :** Manhadjiya, exemple tableau / منحنى (خميرة + غلوكوز)  
**Note d’entraînement :** /4 — **pas** une note Bac officielle  
**Fichiers machine :**
- `khawarizmi-backend/data/rubrics/templates/analyse.json`
- `khawarizmi-backend/data/rubrics/questions/manhadjiya-yeast-analyse.v1.json`
- `khawarizmi-backend/data/documents/yeast-glucose-curve.v1.json`

---

## Document (ce que l’élève a sous les yeux)

Même quantité de الخميرة, deux milieux, temps en heures :

| الزمن (سا) | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| وسط (أ) + غلوكوز | 9 | 10 | 12 | 15 | **18** |
| وسط (ب) بدون غلوكوز | 9 | 8 | 7 | **6** | **6** |

**Chiffres qui comptent** (pas un « 1 » inventé) : **9**, **18**, **6**, **4 سا**.

**هدف السياق :** دور الغلوكوز في نمو / تكاثر الخميرة.

---

## Cases (le prof coche)

| # | Case livre | Points | Comment le prof voit « oui » |
|---|---|---|---|
| 1 | تقديم الوثيقة | 0,75 | الوثيقة / المنحنى / الجدول |
| 2 | تغير + **رقم du graphe** | 1,00 | 9 ou 18 ou 6 (ou 4 سا) |
| 3 | علاقة كلما | 0,75 | كلما … زاد/نقص … (أو علاقة طردية) |
| 4 | **Sans** لأن / هذا يدل | 0,50 | Si لأن → tu as changé de verbe (فسّر) |
| 5 | استنتاج = but du contexte | 1,00 | الغلوكوز ضروري لنمو/تكاثر الخميرة |
| | **Total** | **4,00** | |

**Ordre :** 1 → 2 → 3 → 5. Si tu as tout mais dans le désordre : points OK, label **pas** متقن.

**Science :**
- 0 mot du thème (خميرة / غلوكوز / تكاثر) → خارج الموضوع, contenu **erreur**.
- « 36 ATP » → filet manuel, plafond.
- التركيب الضوئي / صانعة recrachés → suspicion حشو.

---

## Copie modèle (livre, un peu resserrée)

> تمثل الوثيقة جدولا يوضح تغيرات عدد خلايا الخميرة بدلالة الزمن في الوسط (أ) الذي يحتوي على الغلوكوز والوسط (ب) الذي يخلو منه. في (أ) يزداد العدد من 9 إلى 18 خلية. في (ب) يتناقص من 9 إلى 6 ثم يثبت. فكلما تواجد الغلوكوز تزايد عدد الخلايا والعكس صحيح. نستنتج أن الغلوكوز عنصر ضروري لنمو وتكاثر فطر الخميرة.

Attendu entraînement : **متقن**, science OK.

---

## Ce que le prof dirait (3 copies)

**Bourrage cours :** « الخميرة تتنفس وتنتج 36 ATP والتركيب الضوئي 1 »  
→ pas de document, pas de 18, hors-sujet, 36 faux. *« الإجابة خارج الموضوع. 38 ATP وليس 36. »*

**Glissement de verbe :** bonne lecture + **لأن** الخميرة تتكاثر بالتنفس  
→ cases 1–2–5 vertes, case 4 rouge. *« حلّلت لكن فسّرت مبكراً (لأن). »* → مقبول.

**Comme le livre :** copie modèle → متقن + *« أحسنت: قدّمت الوثيقة وذكرت 18. »*

---

Le moteur `grade()` est dans `services/local_grader.py` (tests, flag prod encore off). Cette grille est le spécimen d’auteur : d’autres حلّل collent les mêmes 5 cases, autres chiffres.
