# SINAMIND — Intégration locale des sujets Bac dans Annales

Ce fichier sert à intégrer les **vrais sujets PDF directement dans le site**, et non plus seulement via des liens externes.

---

## Problème à corriger

Actuellement, la rubrique Annales peut donner l’impression qu’il n’y a que des liens vers le site source.

Je veux que les sujets soient **insérés dans le site** :
- stockés localement dans `public/annales/`
- affichés directement dans le mode lecture
- utilisés aussi par les modes `bac blanc` et `guidé`

---

# 1. Package prêt

Une archive a été préparée :

```txt
sinamind-annales-with-subjects-package.tar.gz
```

Elle contient :

```txt
khawarizmi-frontend/public/annales/*.pdf
khawarizmi-frontend/src/lib/annales-bac.ts
khawarizmi-frontend/src/app/annales/page.tsx
khawarizmi-frontend/src/app/annales/[slug]/page.tsx
khawarizmi-frontend/src/app/annales/[slug]/read/page.tsx
khawarizmi-frontend/src/app/annales/[slug]/exam/page.tsx
khawarizmi-frontend/src/app/annales/[slug]/guided/page.tsx
```

---

# 2. Ce que contient le package

## Sujets PDF locaux
Les 10 sujets suivants sont inclus localement :

```txt
bac_svt_se_2025.pdf
bac_svt_se_2024.pdf
bac_svt_se_2023.pdf
bac_svt_se_2022.pdf
bac_svt_se_2021.pdf
bac_svt_se_2020.pdf
bac_svt_se_2019.pdf
bac_svt_se_2018.pdf
bac_svt_se_2017.pdf
bac_svt_se_2016.pdf
```

Ils doivent être copiés ici dans le vrai projet :

```txt
khawarizmi-frontend/public/annales/
```

Ainsi, les URLs du frontend deviennent par exemple :

```txt
/annales/bac_svt_se_2025.pdf
/annales/bac_svt_se_2024.pdf
```

---

## Mode lecture corrigé
Le fichier :

```txt
src/app/annales/[slug]/read/page.tsx
```

utilise maintenant un **iframe** pour afficher réellement le sujet dans la page.

Donc l’élève ne verra plus seulement un bouton “télécharger”.

---

# 3. Prompt OpenCode prêt à coller

```txt
Lis le fichier sinamind-opencode-annales-local-subjects.md et intègre exactement le package annales avec sujets locaux dans khawarizmi-frontend.

Objectif :
- intégrer les vrais sujets PDF dans le site
- ne plus dépendre seulement de liens externes
- stocker les sujets dans public/annales/
- afficher réellement les sujets dans le mode lecture
- garder les 3 modes : archive / exam / guided

Tâches obligatoires :
1. copier les PDF dans public/annales/
2. intégrer src/lib/annales-bac.ts mis à jour vers URLs locales
3. intégrer les routes /annales et sous-routes
4. vérifier que /annales/[slug]/read affiche bien le sujet via iframe
5. ne pas toucher au backend
6. lancer npm install si nécessaire
7. lancer npm run build
8. corriger jusqu’au succès

Critères d’acceptation :
- les sujets sont présents localement dans public/annales/
- /annales fonctionne
- /annales/[slug]/read affiche réellement le sujet
- il n’y a plus seulement des liens externes
- build Next.js OK
```

---

# 4. Résultat attendu

Après intégration, on doit pouvoir dire :

```txt
les sujets sont insérés dans le site
et pas seulement liés depuis DzExams.
```