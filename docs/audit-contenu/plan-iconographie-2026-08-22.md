# Plan iconographique — schémas du cours 3AS (2026-08-22)

> Réserve n°3 de l'audit pédagogique de la plateforme, rendue concrète.
> Outils : `khawarizmi-backend/scripts/audit_iconography_inventory.py`
> (ré-exécutable à chaque évolution du cours) · inventaire machine :
> `docs/audit-contenu/iconographie_inventaire.json`.

## 1. Situation initiale et état actuel

Le cours intégral (10 007 lignes, 11 unités) contenait pour chaque unité une
section « 🗺️ وصف الرسوم التوضيحية (لتوليدها بأدوات الذكاء الاصطناعية) » :
les schémas étaient décrits mais non produits. **Au 2026-08-22, 35/35
propositions techniques existent dans `docs/`, mais 0/35 est validée ou
publiable**. Exemple de spec (U1, figure 1 — transcription) :

> « Noyau d'une eucaryote, molécule d'ADN partiellement ouverte, ARN
> polymérase (ellipse bleue) avançant sur la chaîne codante de droite à
> gauche, ARNm en rouge qui s'élonge derrière ; bases nitrogenées écrites ;
> ARNm quittant la nucléaire par les pores vers le ribosome. »

La spec est prête — il manque la production.

## 2. Inventaire : 35 figures décrites sur 11 unités

| Unité | Fig. | Schémas décrits |
|---|---:|---|
| U1 — Synthèse des protéines | 3 | Transcription · Stades de la traduction · Polyribosome |
| U2 — Structure et fonction des protéines | 3 | 4 niveaux de structure · Hémoglobine normale vs drépanocytique · Collagène |
| U3 — Activité enzymatique | 4 | Cadenas-clé vs ajustement induit · Courbe pH · Courbe T° · Mécanisme (3 stades) |
| U4 — Immunologie | 3 | Schéma global de la réponse immunitaire · Cycle VIH dans le LTh · Mécanisme LTc |
| U5 — Transmission nerveuse | 3 | Courbe du potentiel d'action · Synapse · Intégration nerveuse |
| U6 — Photosynthèse | 3 | Ultrastructure du chloroplaste · Schéma Z · Cycle de Calvin |
| **U7 — Respiration cellulaire** | **4** | Ultrastructure de la mitochondrie · Glycolyse · Cycle de Krebs · Phosphorylation oxydative (restaurées — §3) |
| U8 — Bilan énergétique cellulaire | 3 | Schéma global des transformations · Cellule animale vs végétale · Pyramide énergétique |
| U9 — Activité tectonique des plaques | 3 | Carte des plaques · Coupes des 3 types de limites · Courants de convection |
| U10 — Structure interne du globe | 3 | Sismogramme et interprétation · Zones d'ombre sismiques · Coupe globale de la Terre |
| U11 — Structures géologiques | 3 | plaque océanique au niveau de la dorsale · Séquence ophiolithique · Cycle de Wilson |
| **TOTAL** | **35** | **35 specs prêtes · 35 propositions produites · 0 validée** |

## 3. Constat U7 (Respiration cellulaire) — **RESTAURÉ le 2026-08-22** ✅

Le défaut (unité sans en-tête dans l'index du cours) est corrigé :

- **Les 4 specs de figures EXISTAIENT déjà** (ultrastructure mitochondrie,
  glycolyse, cycle de Krebs, phosphorylation oxydative) — en format ligne
  plate, ce que l'inventaire initial ne captait pas. Reformatées au format
  blockquote standard des autres unités.
- En-tête d'unité `# ⚡ الوحدة 2` + sous-titre FR rétablis au format standard.
- Les 15 marqueurs de section plats (`📖 القسم`, `🔑 الإجابات`…) re-préfixés
  `## ` (contenu jamais altéré — opérations de formatage uniquement,
  vérifié : 63 sections, dernière ligne inchangée, domaine 3 intact).
- **Inventaire re-exécuté : 11 unités indexées / 35 figures** (le total
  production reste 35 — pas de spec supplémentaire à rédiger).
- Suite de tests : 1036 passed / 10 skipped / 5 xfailed (0 régression).

## 4. Plan de production priorisé

Raisonnement : les figures P1 sont celles qui reviennent telles quelles dans
les tâches du Bac (« tracez… », « interprétez le document ») — courbes
enzymatiques, synapse, potentiel d'action, cycle VIH, schéma Z, Calvin,
subduction/ophiolite. P2 = le reste du programme.

| Vague | Unités | Figures | Contenu |
|---|---|---:|---|
| **P1** (avant les examens blancs) | U3, U4, U5, U6, **U7**, U11 | **20** | Courbes pH/T° · Mécanisme enzymatique · Cycle VIH · Réponse immunitaire · LTc · Potentiel d'action · Synapse · Intégration · Chloroplaste · Schéma Z · Calvin · **4 figures U7 (specs déjà présentes)** · Dorsale · Ophiolithe · Wilson |
| **P2** (complétion) | U1, U2, U8, U9, U10 | **15** | Transcription · Traduction · Polyribosome · 4 structures · Hémoglobine drépanocytique · Collagène · Bilan énergétique · Cellule a/v · Pyramide · Carte des plaques · 3 limites · Convection · Sismogramme · Zones d'ombre · Coupe de la Terre |

## 5. Pipeline de production (par figure)

1. **Spec** : existante (les 31) ou à rédiger (les 4 de U7) — déjà au format
   « contenu + couleurs + étiquettes ».
2. **Production** :
   - **Courbes et schémas mécanistiques → vectoriel** (Illustrator, draw.io,
     Manim ou équivalent) — précision scientifique exigeante ; la génération
     d'images IA est inadaptée aux courbes chiffrées (pH, mV, min).
   - **Schémas d'ultrastructure / cycles → génération IA assistée** possible
     (les specs sont écrites pour ça), sous relecture stricte.
3. **Relecture scientifique** (1 enseignant SVT par figure) — critères
   d'acceptation : exactitude des étiquettes ; nomenclature FR/AR confrontée
   au manuel 3AS validé lorsque la pièce source sera archivée ; lisibilité A4
   et légende type Bac (« document 1 : … »).
4. **Intégration** : dans le cours (remplacement de la section « à générer »
   par la figure + légende) et dans les blocs de leçon si pertinent ;
   traçabilité (qui a relu, quand).

## 6. Effort estimé et critères de fin

| Poste | Estimation |
|---|---|
| Production P1 (20 figures) | 20–40 h (1-2 h/figure selon complexité) |
| Relecture scientifique P1 | 10 h (30 min/figure) |
| Intégration P1 | 4 h |
| **Sous-total P1** | **~4-6 semaines à 1, ou 2-3 semaines à 2** |
| P2 (15 figures) | idem × 0,75 |
| **Total (35 figures, specs 100 % prêtes)** | **~50-80 h de travail structuré** |

**Critère de fin (mesurable)** : 35/35 figures publiées ET relues (trace) ·
inventaire re-exécuté → 11 unités / 35 figures · chaque figure a sa
relecture signée dans le repo. *(U7 restaurée le 2026-08-22 — critère
structurel acquis.)*

## 7. Production P1 — TERMINÉE (20/20 propositions, 2026-08-22)

**Tranche 1 (4)** : synapse U5 · clé-serrure U3 · Calvin U6 · dorsale U11.
**Tranche 2 (10)** : courbes pH/T° + 3 stades enzymatiques U3 · réponse
immunitaire + cycle VIH + LTc U4 · potentiel d'action + intégration U5 ·
chloroplaste + schéma Z U6.
**Tranche 3 (6)** : mitochondrie + glycolyse + Krebs + phosphorylation
oxydative U7 · ophiolithe + cycle de Wilson U11.

- **20/20 figures P1 générées** et vérifiées par échantillonnage (statut
  **PROPOSITION — sous relecture**, `figures-pilote-p1/` — NE PAS PUBLIER
  avant relecture enseignant).
- Note de méthode : le modèle ajoute parfois des étiquettes EN — remplacées
  par l'arabe officiel en relecture (point 2 de la checklist).
- **P2 produite : 15/15 propositions** dans `figures-pilote-p2/`.
- **Reste bloquant :** relecture scientifique humaine 35/35, overlay AR/FR
  35/35 et tests mobile/A4 consignés ; aucune publication avant ces étapes.

## 8. Reçu (R-Audit-ICÔNO)

- Extraction initiale du 2026-08-22 : 31 figures décrites sur 10 unités
  indexables + U7 absente de l'index (en-tête manquant — contenu et 4 specs
  présents en format non capté)
- **U7 RESTAURÉE le 2026-08-22** : en-tête + 15 marqueurs `## ` + 4 specs
  reformatées (contenu non altéré, vérifications de cohérence passées)
- **État de production : 11 unités / 35 specs / 35 propositions** — inventaire
  re-exécutable : `audit_iconography_inventory.py` + JSON
  `iconographie_inventaire.json` ; contrôle publication/accessibilité :
  `iconography-manifest.json` (**0 validation humaine, 0 publiable**).
