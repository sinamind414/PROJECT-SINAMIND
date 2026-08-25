# Note d'envoi — SINAMIND / Khawarizmi
**Audit SVT Bac 3AS SE + correcteur + 4 sujets reconstitués + contrat d'intégration**

## Verdict en une phrase
Le **cours** est solide ; l'**épreuve** dans le produit ne l'est pas ; le **correcteur local** sait refuser et mal récompense ; le trou D2/D3 est **écrit** (S1–S4), **pas shippé**.

| Objet | Note | Réserve |
|---|---|---|
| Plateforme (contenu + parcours) | **13/20** | Correcteur non inclus |
| Correcteur **vécu** (L2, no-clé, ONNX LFS) | **≈ 4,6/10** | LLM non testé ; 5,1 = mixte Savoir+L2 **non déployé** |
| Potentiel documenté | **16/20** | Après PDF réels, figures, purge OCR, 404, S1–S4 *dans* le site, F2 patché. Pas après plus de badges |

## Ce qui est vrai dans les fichiers (ne plus rediscuter)
- **19** exercices Bac exploitables = **6 / 4 / 2 / 4 / 3** (D1 seulement). **0** D2, **0** D3.
- 89/108 items OCR encore `valide: true`.
- PDF annales + modèle ONNX = pointeurs **Git LFS 132 octets** (même dette).
- Routes `/exercises/by-chapter`, `/exercices/sciences` → 404 ; QCM chapitre souvent factice ; docs d'épreuve sans figure.
- Savoir **éteint** ; s'il s'allume sans contrôle de **sens** : 100 % possible sur une contre-vérité.
- L2 : 16/16 reformulations justes < 60 % ; 3/8 copies **exactes** sous-notées (bug négation `لا` / `دون` / `وليس`).
- Cadre données mineurs : **loi 18-07**, pas le RGPD.
- Sujets **2026** ≠ officiels.

## Pièces jointes (ordre de lecture)

1. `audit-svt-sinamind-v3-livable.md` — grille, 13/20, matrice, plan site
2. `audit-correcteur-svt-sinamind-v1.1.md` — L2 vs Savoir vs LLM
3. `S1-sujet-type-bac-D2-respiration.md`
4. `S2-sujet-type-bac-D3-tectonique.md`
5. `S3-sujet-type-bac-D2-photosynthese.md`
6. `S4-sujet-type-bac-D3-dorsale.md`
7. `INT-contrat-integration-S1-S4.md` — comment les entrer **sans** recréer des `DocumentRef` vides
8. `ANALYSE-bac-svt-2025-officiel.md` — structure réelle 2025 (5+7+8, domaines, figures, barème atomique), pour recaler l'audit et S3

S1–S4 = **entraînement reconstitué**, gabarit Bac, /20, figures spécifiées, barème, anti-F3. **Pas** des annales. **Pas** de note auto.

Objectif court terme v3 « ≥ 2 D2 + ≥ 2 D3 » : **tenu sur le papier** (S1+S3, S2+S4). **Non tenu dans le produit.**

**Calage 2025 (voir `ANALYSE-bac-svt-2025-officiel.md`).** La session officielle 2025 (Sujet 1 : 13 D1 / 7 D2 / 0 D3 ; Sujet 2 : 15 D1 / 5 D2 / 0 D3) **confirme et aggrave** le trou D2 — désormais prouvé par une épreuve réelle — et montre que même le D1 du site, sans figures ni hypothèse-validation, n'est pas l'épreuve. **Le 13/20 n'est pas relevé par 2025.** Gabarit épreuve = **5 + 7 + 8** (texte imposé intro/problème/développement/conclusion en Ex. 1) ; nos S1–S4 sont en 10+10, donc des **entraînements de domaine**, pas des clones 2025. D3 = 0 en 2025 (loterie de session) : S2/S4 restent le 2ᵉ pilier de couverture pluriannuelle. **Écart fin mis au jour :** S3 (photosynthèse classique) ne couvre pas le **CCM / pyrénoïde** (S1-Ex.2 2025).

## Cinq actions produit (ordre)

1. CI anti-LFS (`public/pdfs/**`, figures, ONNX) ; vrais PDF ou liens retirés.
2. `valide: false` par défaut ; sortir les 89 OCR du circuit élève.
3. Réparer les 404 ; tuer le QCM factice par chapitre.
4. Intégrer S1–S4 **selon le contrat E** (24 figures réelles, pastille AR, `corrige_à_consulter`).
5. Patch F2 (négation) **avant** toute note chiffrée. P2 paraphrase ensuite.

Parallèle possible : 1–4 d'un côté, 5 de l'autre. **Ne pas** afficher de score L2 sur S1–S4 tant que `reformulee < 6/8`.

## Hors ce pli
Runtime, mobile, arabe systématique, accessibilité, droits d'annales, grader LLM.

---

**Fin de mission contenu.**
C ou D seulement si tu colles les extraits ou `fallback_v2.py`. Sinon le dossier s'arrête là.
