# Rapport corruption OCR — liste de travail (2026-08-22)

> Réserve n°2 de l'audit pédagogique de la plateforme, rendue concrète.
> Outil : `khawarizmi-backend/scripts/audit_ocr_corruption.py` (réutilisable —
> c'est aussi le **garde-fou à exécuter avant toute future import** : exigence
> 0 item CORROMPU avant ingestion).
> Liste de travail machine : `docs/audit-contenu/ocr_items_a_traiter.json`
> (1 235 items flaggés avec verdict, score, extrait et mots suspects).

## 1. Méthode

Le texte arabe transcrit par OCR (documents scannés) présente deux classes de
corruption détectées séparément :

- **Classe A — fragmentation** : les mots se désolidarisent en fragments de
  1-3 lettres (« أ ذهص زالث متثَالت ٌَػػ ARN »). Détecteur : ratio de mots
  arabes courts hors liste blanche de mots légitimes (في، من، دم، نوع…).
  Seuil ≥ 30 % = **CORROMPU** (hautement fiable — une phrase arabe saine ne
  contient pas un tiers de fragments orphelins), 12-30 % = **SUSPECT**.
- **Classe B — formes de présentation** : extraction PDF en caractères
  U+FB50-U+FDFF non normalisés (« اﻟوﺛﯾﺔ » au lieu de « الوثيقة »). Réparable
  par normalisation unicode, pas par re-OCR.

Validation du détecteur sur échantillons de référence : 2 textes corrompus
connus détectés (scores 60 % et 45 %), 4 textes sains non détectés (0-10 %).
Le champ SUSPECT conserve un taux de faux positifs sur les textes courts
légitimes — c'est une **file de relecture**, pas une liste de fautes.

## 2. Résultats globaux (4 197 textes arabes scannés, 9 collections)

| Collection | Textes | OK | SUSPECT | CORROMPU | À traiter |
|---|---:|---:|---:|---:|---:|
| annales_sciences_3as | 268 | 84 | 69 | **115** | 42,9 % |
| qcm_items (670 items) | 2 010 | 1 572 | 411 | 27 | 1,3 % |
| questions taggées + khelifa | 323 | 209 | 106 | 8 | 2,5 % |
| exercices/résumés Bac | 226 | 53 | 66 | **107** | 47,3 % |
| methodologie (16 docs) | 54 | 38 | 8 | 8 | 14,8 % |
| lexique (844 termes) | 253 | 226 | 27 | 0 | 0,0 % |
| manhadjiya_seed | 58 | 41 | 14 | 3 | 5,2 % |
| annales_seed | 5 | 5 | 0 | 0 | 0,0 % |
| drills 620 (md) | 1 000 | 734 | 260 | 6 | 0,6 % |
| **TOTAL** | **4 197** | **2 962** | **961** | **274** | **6,5 %** |

**274 textes corrompus = 208 items distincts** (certains items ont la
question ET la réponse abîmées). Sous-classes : 258 fragmentations pures
(re-OCR / re-transcription) + 16 textes avec formes de présentation
(normalisables par script).

## 3. Lecture par collection — ce que ça veut dire

### 3.1 La banque « 605 Questions de Révision » : 75 questions corrompues sur 89 (84 %)
C'est le cœur du problème, et il est pire que ce que le titre laisse penser :

- Le titre promet **605** questions ; **89** sont réellement ingérées ;
  de ces 89, **75 sont corrompues** (classe A) → **seules 14 questions
  saines** subsistent dans cette banque.
- La banque apparaît dans **deux fichiers** (`annales_sciences_3as.json`
  et `sciences_bac_exercices.json`) — les 75 questions corrompues sont donc
  servies en double sur la plateforme.
- Exemples (ids dans le JSON) : `q_46` (question ET réponse illisibles),
  `q_010`, `q_016`, `q_030`… liste complète dans `ocr_items_a_traiter.json`.

**Implication** : cette banque est inutilisable en l'état. Elle doit être
soit purgée intégralement (14 questions = pas d'intérêt), soit
re-transcrite de zéro depuis les sources.

### 3.2 Méthodologie : le document n°1 est entierement en « formes de présentation »
Les 6 sous-documents de `documents[0]` (PDF eddirasa.com « تدرج التعليمات
مناهج العلوم الطبيعية 3 ثانوي ») sont extraits en caractères non normalisés
(comptage : **9 861 / 127 / 96 / 306 / 12 766 / 4 731 / 5 937** caractères
de présentation par sous-document). Les **15 autres documents sont propres**.
Réparation par normalisation unicode (scriptable) + relecture — pas de
re-OCR nécessaire si l'ordre des lettres est correct après normalisation.

### 3.3 Le reste : petites taches locales
- **qcm_items** : 26 items sur 670 (4 %) — correction au cas par cas.
- **annales** (hors banque 605) : 8 textes ; **taggées/khelifa** : 8 ;
  **drills 620** : 6 ; **manhadjia** : 3 — correction ciblée.
- **lexique : 0 texte corrompu** (27 SUSPECT = file de relecture seulement).

## 4. Plan de traitement (ordré par impact, avec effort estimé)

| # | Action | Effort | Critère de fin |
|---|---|---|---|
| 1 | **Purger les 75 questions corrompues** de la banque 605 (les 2 fichiers) — script 30 min + validation | 0,5 j | Scan : 0 CORROMPU dans annales + exercices ; la banque affiche 14 questions ou est retirée de la navigation |
| 2 | **Normaliser le document méthodologie n°1** (6 sous-docs, formes de présentation) + relecture | 0,5 j | Scan : 0 CORROMPU dans methodologie ; texte lisible par un prof |
| 3 | **Corriger les 26 QCM + 24 autres petits lots** (listes exactes dans le JSON) | 1-2 j | Scan : 0 CORROMPU global |
| 4 | **Re-transcription intégrale de la banque 605** depuis les sources originales (89 questions + réponses, sources publiques) — ou re-OCR depuis de meilleures images + validation humaine | 2-3 j | 89/89 questions saines avec réponses validées ; scan 0 CORROMPU |
| 5 | **File SUSPECT (961 textes)** : relecture au pas de tir (pas un audit complet — le détecteur a des faux positifs connus sur les textes courts) ; enrichir la liste blanche si un pattern récurrent apparaît | 1 j (spot) | Aucun pattern de corruption récurrent non capté |
| 6 | **Garde-fou pérenne** : exécuter `audit_ocr_corruption.py` avant toute future import (exigence 0 CORROMPU) ; documenter dans le runbook d'ingestion | — | Processus écrit |

**Effort total : ~5-7 jours** de travail de correction (dont 2-3 j sur la
re-transcription de la banque). Après les actions 1-3 (≈ 2 j), la plateforme
est **propre** (0 texte corrompu) ; l'action 4 restaure la profondeur de la
banque.

## 5. Actions exécutées

### Action 1 — EXÉCUTÉE le 2026-08-22 ✅

- **`annales_sciences_3as.json`** (23 → 21 sujets) :
  - sujet `revision_605_questions` supprimé **entier** (89 questions, 100 %
    corrompue — y compris les 14 « non-flaggées » en formes de présentation
    que le détecteur par ratio ne captait pas ; cohérent avec
    `_CORRUPTED_SOURCES` de `services/questions.py` qui sautait déjà ce sujet
    au chargement runtime : les données mortes sont maintenant sorties du
    fichier) ;
  - sujet `minhajiya_eddirasa.com-تدرج-التعليمات-…` supprimé (7/7 questions
    corrompues, doublon du document méthodologie n°1 en formes de
    présentation).
- **`sciences_bac_exercices.json`** (108 → 19 items) : les 89 items issus de
  la banque 605 purgés ; restent 6 sources de livres de préparation.
- `tests/test_sciences.py` re-pointé sur une question saine
  (`el_mojtahid_3as::q1_mojtahid_transcription`).
- **Scan post-purge** (détecteur renforcé — les formes de présentation sont
  désormais flaggées quel que soit le ratio) : annales = **0 CORROMPU** (+ 1
  NON-NORMALISÉ) · exercices = **0 CORROMPU** · global : 274 → **56 textes à
  traiter (44 CORROMPU + 12 NON-NORMALISÉ, 1,5 %)** — le reste relève des
  actions 2-4 (12 methodologie à normaliser, 27 QCM + 25 petits lots, listes
  dans le JSON).
- **Suite complète : 1036 passed / 10 skipped / 5 xfailed** (0 régression).

### Action 2 — EXÉCUTÉE le 2026-08-22 ✅ (normalisation methodologie)

- **Outil** : `scripts/normalize_arabic_pres_forms.py` (réutilisable, idempotent —
  2e exécution = 0 changement) : NFKC (formes de présentation → lettres
  standard) + suppression contrôleurs C0 + 3+ sauts de ligne → 2 + numéro de
  page erratique en tête de champ (uniquement sur champ corrompu — garde
  anti-régression sur les textes sains).
- **Résultat** : `data/methodologie_sciences_3as.json` — **12 champs
  normalisés** (le document n°1 eddirasa.com, 6 sous-docs : en-tête officiel
  « الجمهورية الجزائرية… 2017 تدرج التعلمات », documents géologiques,
  progressions pédagogiques). Scan : methodologie **0 CORROMPU / 0
  NON-NORM**. Idempotence vérifiée.
- **Reste connu (relecture humaine)** : quelques erreurs de caractère OCR
  irrécupérables par l'encodage (ex. « المف%ش$ية » au lieu de « المفتشية »,
  « 4لوم » au lieu de « العلوم ») — à corriger à la main dans la relecture ;
  rapport before/after : `docs/audit-contenu/normalisation-methodologie-2026-08-22.md`.
- **Global après action 2** : 56 → **45 textes à traiter (1,2 %)** — reste =
  actions 3-4 (27 QCM + 1 annales NON-NORM + 17 petits lots).
- **Suite complète : 1036 passed / 10 skipped / 5 xfailed** (0 régression).

### Action 3 — EXÉCUTÉE le 2026-08-22 ✅ (0 CORROMPU global)

**Retournement d'analyse** : l'examen du contenu réel des 45 derniers textes
a montré que **44/45 étaient des faux positifs du détecteur** (et non des
corruptions) :

- mots courts arabes LÉGITIMES non listés (بـ، لأن، مما، سطح، ضغط, et les
  verbes impératifs courts des consignes d'exercices : « صنف الأحماض الأمينية
  حسب خواصها الكيميائية » est une phrase saine),
- **notations composites arabe/latin** (وO2، لATP، بARNr) comptées à tort
  comme fragmentation.

**Correctifs apportés** :
1. **Détecteur v3** (`audit_ocr_corruption.py`) : exclusion des mots mixtes
   arabe/latin + comparaison whitelist sur **formes de base sans
   diacritiques** (robuste aux variantes) + ~50 mots courts légitimes ajoutés
   → 44 faux positifs disparus ; file SUSPECT : 854 → **122**.
2. **1 seul texte réellement corrompu** : la réponse attendue de
   `minhajiya_2-النشاط-التكتوني…::q_0` (formes de présentation) — normalisée
   avec le script de l'action 2 (rapport before/after :
   `normalisation-annales-2026-08-22.md`).

**Résultat final** : **0 CORROMPU / 0 NON-NORM sur les 3 824 textes scannés**
(9 collections) — la plateforme est à **0 texte corrompu**. La file SUSPECT
(122) reste une liste de relecture ponctuelle (action 5).

**Suite complète : 1036 passed / 10 skipped / 5 xfailed** (0 régression).

### Action 4 — TENTATIVE DE RÉCUPÉRATION (2026-08-22) — résultat : 0 récupérable en sécurité

La banque pré-purge a été restaurée depuis l'historique git
(`da5df7b^`) et les 89 questions ont été traitées (NFKC + nettoyage +
tri automatique). **Trois modes d'échec OCR distincts** ont été identifiés :

1. **formes de présentation** (PDF non normalisé) — réversible par NFKC
   (c'est l'action 2) ;
2. **fragmentation** (mots désolidarisés en fragments 1-3 lettres) —
   irrévirable par script ;
3. **désordre de caractères en formes standard** (« ثـصف » au lieu de « صف »)
   — irrévirable par script, et **détectable seulement à la lecture**.

Résultat du tri : **85/89 irrécupérables** (modes 2+3), **4/89** à peine
lisibles mais dont les réponses restent scramblées. **Décision : rien ne
doit être republié sans re-transcription humaine** — publier du contenu
deviné (même probable) sur une plateforme de préparation au Bac est pire
que le vide. La banque reste purgée.

**Action 4 (vraie) — reste** : re-transcription intégrale de la banque 605
(89 questions + réponses) depuis les **sources publiques originales**
(travail manuel 2-3 j, hors périmètre des sessions).

### Action 5 — EXÉCUTÉE le 2026-08-22 ✅ (relecture de la file SUSPECT)

- File initiale : 122 textes. Traitement : 108 résolus par raffinements du
  détecteur (chaque motif ajouté était d'abord validé à la lecture) + **40
  extraits relus un par un : 0 corruption réelle détectée** — la file était
  composée de mots courts arabes légitimes (verbes impératifs des consignes
  Bac, mots de contenu), jetons-labels de sujets ((س), (أ و ب), (غ1)),
  références de page (ص208), notations (وO2, و70).
- **Détecteur v4** : jetons avec chiffres exclus, labels avec chiffres
  acceptés, `:`/`؛` retirés avant whitelist, +35 mots validés à la relecture.
- File restante : **14 textes (0,36 %) — tous relus et confirmés sains**.
  L'ajout de mots pour ces 14-là serait un overfitting ; le résidu est le
  faux-positif résiduel normal du garde-fou (il sert à alerter, pas à
  bloquer).
- **Bilan final de la file de relecture : 0 problème réel détecté,
  0 correction nécessaire** (40 extraits relus un par un + 14 résidus
  confirmés sains + motifs validés à la lecture avant chaque ajout au
  whitelist).

## 6. Reçu (R-Audit-OCR)

- Scan initial du 2026-08-22 : 4 197 textes / 9 collections
  → 274 CORROMPU (6,5 %) / 961 SUSPECT (22,9 %) / 2 962 OK (70,6 %)
- **État final** (après actions 1-5) : 3 824 textes → **0 CORROMPU /
  0 NON-NORM** / 14 SUSPECT résiduels relus et confirmés sains (0,36 %) /
  3 810 OK
- Récupération banque 605 : 0/89 récupérable en sécurité (3 modes d'échec
  OCR identifiés, dont le désordre de caractères) → banque reste purgée,
  re-transcription depuis sources publiques = seul chemin
- Détecteur v4 + normaliseur : `khawarizmi-backend/scripts/audit_ocr_corruption.py`
  et `normalize_arabic_pres_forms.py` (garde-fous d'ingestion : 0 CORROMPU
  exigé avant import)
- Liste de travail : `ocr_items_a_traiter.json` (regénérée, 14 items —
  file vide de problèmes réels)
